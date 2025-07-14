from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import threading
import logging
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Setting
from client import reqs
from client.stats import LiveStats
from client import results
from client.metadata_manager import MetadataManager


class LoadClient:
    """
    Load testing client for EDI transactions (270, 276, 278).

    Manages concurrent HTTP requests with configurable RPS and thread pools.
    Supports runtime adjustment of request rates and transaction types.
    """

    def __init__(self, cfg: Setting):
        """Initialize load client with configuration settings."""
        # EDI transaction endpoints
        self.endpoints = {
            270: "http://127.0.0.1:5000/270/",  # Healthcare Eligibility/Benefit Inquiry
            276: "http://127.0.0.1:5000/276/",  # Healthcare Claim Status Request
            278: "http://127.0.0.1:5000/278/",  # Healthcare Services Review
        }

        self.transaction = cfg.transaction
        self._rps = cfg.rps
        self._rps_lock = threading.Lock()
        self.threads = cfg.threads
        self._trans_lock = threading.Lock()

        # Runtime state
        self._running = False
        self._pool = None
        self._sched_thread = None
        self._stop_event = threading.Event()

        # Data collection
        self._sink = results.CsvSink("test.csv")
        self._stats = LiveStats()
        self._log = logging.getLogger("edi_load_client")
        logging.basicConfig(filename="test.log", level=logging.INFO)

        self._metadata_manager = None

    def set_metadata_manager(self, metadata_manager: MetadataManager):
        """Set metadata manager for header-based error information."""
        self._metadata_manager = metadata_manager
        if metadata_manager:
            summary = metadata_manager.get_error_summary()
            self._log.info(
                f"Metadata loaded: {summary.get('total_transactions', 0)} transactions, "
                f"{summary.get('total_errors', 0)} errors ({summary.get('error_rate', 0):.1%} rate)"
            )

    def start(self):
        """Start the load testing client."""
        if self._running:
            return

        self._running = True
        self._stop_event.clear()

        # Initialize components
        self._sched_thread = threading.Thread(target=self._scheduler, daemon=True)
        self._pool = ThreadPoolExecutor(max_workers=self.threads)
        self._sched_thread.start()

        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.info(
            "Client started at %s → %s, %.1f rps, %d threads.",
            curr_time,
            self.endpoints[self.transaction],
            self.rps,
            self.threads,
        )

    def stop(self):
        """Stop the client and write final results."""
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
        result = self._stats.snapshot()
        self._sink.write()
        self._log.info(
            "%d requests sent, %.2f ms avg latency, %d 200 OK",
            result["count"],
            result["avg_latency"],
            result["codes"].get(200, 0),
        )

    def _scheduler(self):
        """Background scheduler that maintains target RPS."""
        next_run = time.perf_counter()
        while not self._stop_event.is_set():
            interval = 1.0 / self.rps

            fut = self._pool.submit(
                reqs.send_edi_request,
                self.transaction,
                self.endpoints[self.transaction],
                self._metadata_manager,
            )
            fut.add_done_callback(self._handle_response)

            # Maintain timing
            next_run += interval
            time.sleep(max(0, next_run - time.perf_counter()))
        return

    def _handle_response(self, future):
        """Process completed HTTP requests and update statistics."""
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            status, elapsed, body = future.result()

            # Analyze response to determine if it's an EDI error vs success
            edi_error_type = None
            if status == 200 and body:
                # Check if 200 OK response contains EDI error (AAA segment)
                body_str = (
                    body.decode("utf-8") if isinstance(body, bytes) else str(body)
                )
                if "AAA*N*" in body_str:
                    edi_error_type = self._categorize_edi_error(body_str)
                    self._log.info(
                        "200 OK with EDI error (%s) in %.3f ms", edi_error_type, elapsed
                    )
                else:
                    self._log.info("200 OK (EDI success) in %.3f ms", elapsed)
            elif status == 200:
                self._log.info("200 OK in %.3f ms", elapsed)
            else:
                self._log.error("HTTP ERR %d in %.3f ms", status, elapsed)

            self._stats.update(elapsed, status, edi_error_type)
            self._sink.append(curr_time, elapsed, status, self.rps, body)

        except Exception as e:
            self._log.error("Error handling response: %s", e)

    def _categorize_edi_error(self, response_body):
        """Categorize EDI error based on AAA segment error codes."""
        if "AAA*N**79*" in response_body:
            return "edi_format_error"
        elif "AAA*N**72*" in response_body:
            return "edi_member_error"
        elif "AAA*N**83*" in response_body:
            return "edi_amt_error"
        elif "AAA*N**85*" in response_body:
            return "edi_validation_error"
        elif "AAA*N*" in response_body:
            return "edi_other_error"
        return None

    @property
    def rps(self) -> float:
        """Get current requests per second rate (thread-safe)."""
        with self._rps_lock:
            return self._rps

    def update_rps(self, new_rps: float):
        """Update request rate during runtime."""
        with self._rps_lock:
            self._rps = new_rps

        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.info("RPS updated at %s to %.1f", curr_time, new_rps)

    def update_transaction(self, new_transaction):
        """Update EDI transaction type during runtime."""
        with self._trans_lock:
            self.transaction = new_transaction
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.info("Transaction updated at %s to %d", curr_time, new_transaction)
