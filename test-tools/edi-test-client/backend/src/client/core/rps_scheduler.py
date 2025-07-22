import threading
import time
from typing import Callable
from concurrent.futures import ThreadPoolExecutor


class RPSScheduler:
    """Manages request scheduling to maintain target requests per second."""

    def __init__(
        self,
        thread_pool: ThreadPoolExecutor,
        request_func: Callable,
        response_callback: Callable,
    ):
        self.thread_pool = thread_pool
        self.request_func = request_func
        self.response_callback = response_callback

        self._rps = 1.0
        self._rps_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._scheduler_thread = None

    def start_scheduling(self) -> None:
        """Start the background scheduler thread."""
        if self._scheduler_thread is not None:
            return

        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop, daemon=True
        )
        self._scheduler_thread.start()

    def stop_scheduling(self) -> None:
        """Stop the scheduler and wait for completion."""
        if self._scheduler_thread is None:
            return

        self._stop_event.set()
        self._scheduler_thread.join()
        self._scheduler_thread = None

    def update_rps(self, new_rps: float) -> None:
        """Update requests per second rate (thread-safe)."""
        with self._rps_lock:
            self._rps = new_rps

    @property
    def rps(self) -> float:
        """Get current requests per second rate (thread-safe)."""
        with self._rps_lock:
            return self._rps

    def _scheduler_loop(self) -> None:
        """Background scheduler that maintains target RPS."""
        last_time = time.perf_counter()
        requests_sent = 0

        while not self._stop_event.is_set():
            current_time = time.perf_counter()
            elapsed = current_time - last_time

            current_rps = self.rps
            target_requests = int(elapsed * current_rps)

            requests_to_send = max(0, target_requests - requests_sent)

            for _ in range(requests_to_send):
                if self._stop_event.is_set():
                    break

                # Submit request to thread pool
                future = self.thread_pool.submit(self.request_func)
                future.add_done_callback(self.response_callback)
                requests_sent += 1

            if elapsed >= 1.0:
                last_time = current_time
                requests_sent = 0

            time.sleep(0.001)
