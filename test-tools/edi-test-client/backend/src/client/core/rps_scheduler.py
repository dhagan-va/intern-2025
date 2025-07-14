import threading
import time
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor


class RPSScheduler:
    """Manages request scheduling to maintain target requests per second."""
    
    def __init__(self, thread_pool: ThreadPoolExecutor, request_func: Callable, response_callback: Callable):
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
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
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
        next_run = time.perf_counter()
        
        while not self._stop_event.is_set():
            interval = 1.0 / self.rps
            
            # Submit request to thread pool
            future = self.thread_pool.submit(self.request_func)
            future.add_done_callback(self.response_callback)
            
            # Maintain timing
            next_run += interval
            time.sleep(max(0, next_run - time.perf_counter()))