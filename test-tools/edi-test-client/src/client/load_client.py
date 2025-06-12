from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import threading
import logging
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Setting
import reqs


class LoadClient:
    def __init__(self, cfg: Setting):
        self.endpoint = cfg.endpoint
        self._rps = cfg.rps
        self._rps_lock = threading.Lock()
        self.threads = cfg.threads

        self._running = False
        self._pool = None
        self._sched_thread = None
        self._stop_event = threading.Event()

        self._log = logging.getLogger("edi_load_client")
        logging.basicConfig(filename="test.log", level=logging.INFO)

    def start(self):
        if self._running:
            return

        self._running = True
        self._stop_event.clear()

        self._sched_thread = threading.Thread(target=self._scheduler, daemon=True)
        self._pool = ThreadPoolExecutor(max_workers=self.threads)
        self._sched_thread.start()
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.info(
            "Client started at %s → %s, %.1f rps, %d threads.",
            curr_time,
            self.endpoint,
            self.rps,
            self.threads,
        )

    def stop(self):
        if not self._running:
            return
        self._stop_event.set()
        self._running = False
        self._log.info("Stopping client")

        if self._sched_thread:
            self._sched_thread.join()

        if self._pool:
            self._pool.shutdown(wait=True)

        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.info("Client stopped at %s", curr_time)

    def _scheduler(self):
        next_run = time.perf_counter()
        while not self._stop_event.is_set():
            interval = 1.0 / self.rps
            fut = self._pool.submit(reqs.send_270_request, self.endpoint)
            fut.add_done_callback(self._handle_response)
            next_run += interval
            time.sleep(max(0, next_run - time.perf_counter()))
        return

    def _handle_response(self, future):
        try:
            status, elapsed = future.result()
            if status == 200:
                self._log.info("200 OK in %.3f ms", elapsed)
            else:
                self._log.error("ERR %d in %.3f ms", status, elapsed)
        except Exception as e:
            self._log.error("Error handling response: %s", e)

    @property
    def rps(self) -> float:
        with self._rps_lock:
            return self._rps

    def update_rps(self, new_rps: float):
        with self._rps_lock:
            self._rps = new_rps

        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.info("RPS updated at %s to %.1f", curr_time, new_rps)
