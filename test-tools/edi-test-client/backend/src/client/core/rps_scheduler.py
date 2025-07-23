import threading
import time
import logging
from typing import Callable, Optional
from concurrent.futures import ThreadPoolExecutor


class RPSScheduler:
    """Manages request scheduling to maintain target requests per second with connection throttling."""

    def __init__(
        self,
        thread_pool: ThreadPoolExecutor,
        request_func: Callable,
        response_callback: Callable,
        max_concurrent_connections: int = 150,
        stats_collector: Optional[object] = None,
    ):
        self.thread_pool = thread_pool
        self.request_func = request_func
        self.response_callback = response_callback
        self.max_concurrent_connections = max_concurrent_connections
        self.stats_collector = stats_collector

        self._rps = 1.0
        self._rps_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._scheduler_thread = None

        self._throttled_requests = 0
        self._throttle_lock = threading.Lock()

        self._logger = logging.getLogger(__name__)

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

    def update_max_connections(self, max_connections: int) -> None:
        """Update maximum concurrent connections limit (thread-safe)."""
        self.max_concurrent_connections = max_connections
        self._logger.info(f"Updated max concurrent connections to {max_connections}")

    @property
    def rps(self) -> float:
        """Get current requests per second rate (thread-safe)."""
        with self._rps_lock:
            return self._rps

    def get_throttle_stats(self) -> dict:
        """Get throttling statistics."""
        with self._throttle_lock:
            return {
                "throttled_requests": self._throttled_requests,
                "max_concurrent_connections": self.max_concurrent_connections,
            }

    def _get_current_connections(self) -> int:
        """Get current number of active connections."""
        if self.stats_collector and hasattr(self.stats_collector, "get_concurrent_connections"):
            return self.stats_collector.get_concurrent_connections()
        return 0

    def _should_throttle(self) -> bool:
        """Check if we should throttle based on current connections."""
        current_connections = self._get_current_connections()
        return current_connections >= self.max_concurrent_connections

    def _scheduler_loop(self) -> None:
        """Background scheduler that maintains target RPS with connection throttling."""
        last_time = time.perf_counter()
        requests_sent = 0
        last_throttle_log = 0
        throttle_log_interval = 5.0  

        while not self._stop_event.is_set():
            current_time = time.perf_counter()
            elapsed = current_time - last_time

            current_rps = self.rps
            target_requests = int(elapsed * current_rps)

            requests_to_send = max(0, target_requests - requests_sent)

            if self._should_throttle():
                if current_time - last_throttle_log > throttle_log_interval:
                    current_connections = self._get_current_connections()
                    self._logger.warning(
                        f"Throttling requests: {current_connections}/{self.max_concurrent_connections} "
                        f"concurrent connections (limit reached)"
                    )
                    last_throttle_log = current_time

                with self._throttle_lock:
                    self._throttled_requests += requests_to_send

                time.sleep(0.1)  
            else:
                for _ in range(requests_to_send):
                    if self._stop_event.is_set():
                        break

                    if self._should_throttle():
                        with self._throttle_lock:
                            self._throttled_requests += 1
                        break

                    future = self.thread_pool.submit(self.request_func)
                    future.add_done_callback(self.response_callback)
                    requests_sent += 1

            if elapsed >= 1.0:
                last_time = current_time
                requests_sent = 0

            time.sleep(0.01)  
