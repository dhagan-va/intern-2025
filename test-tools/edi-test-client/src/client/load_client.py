from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import threading
import logging


class LoadClient:
    def __init__(self, endpoint: str, rps: float, threads: int):
        self.endpoint = endpoint
        self.rps = rps
        self.threads = threads

        self._pool = ThreadPoolExecutor
        self._sched_thread = threading.Thread

        self._log = logging.Logger("edi_load_client")

    def start(self):
        if self._scheduler:
            return
        self._sched_thread = threading.Thread(target=self._scheduler, daemon=True)
        self._pool = ThreadPoolExecutor(max_workers=self.threads)
        self._sched_thread.start()
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.info("EDI client started at %s, %.1f rps, %d threads.")

    def _scheduler(self):
        return
