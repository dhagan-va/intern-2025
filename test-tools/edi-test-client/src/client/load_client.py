from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import threading
import logging


class LoadClient:
    def __init__(self, endpoint: str, rps: float, threads: int):
        self.endpoint = endpoint
        self.rps = rps
        self.threads = threads

        self._running = False
        self._pool = ThreadPoolExecutor
        self._sched_thread = threading.Thread
        self._stop_event = threading.Event

        self._log = logging.Logger("edi_load_client")

    def start(self):
        if self._running:
            return
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
        self._log("Stopping client")

        if self._sched_thread:
            self._sched_thread.join()

        if self._pool:
            self._pool.shutdown()

        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.info("Client stopped at %s", curr_time)

    def _scheduler(self):
        
        return
