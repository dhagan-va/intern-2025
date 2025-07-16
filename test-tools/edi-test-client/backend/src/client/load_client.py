from config import Setting
from client.network import send_edi_request
from client.data import CsvSink, MetadataManager
from client.processing import ResponseProcessor
from client.core import RPSScheduler
from client.statistics import StatsCollector
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import threading
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class LoadClient:
    """
    Load testing client for EDI transactions (270, 276, 278).

    Now uses composition with specialized components for better separation of concerns.
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
        self.threads = cfg.threads
        self._configured_rps = cfg.rps
        self._trans_lock = threading.Lock()

        # Runtime state
        self._running = False
        self._pool = None

        # Initialize logging first
        self._log = logging.getLogger("edi_load_client")
        logging.basicConfig(filename="test.log", level=logging.INFO)

        self._sink = CsvSink("test.csv")
        self._stats_collector = StatsCollector()
        self._stats = self._stats_collector.live_stats

        # Response processing component
        self._response_processor = ResponseProcessor(
            self._stats_collector,
            self._sink,
            self._log,
        )

        self._scheduler = None
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

        # Initialize thread pool
        self._pool = ThreadPoolExecutor(max_workers=self.threads)

        def make_request():
            return send_edi_request(
                self.transaction,
                self.endpoints[self.transaction],
                self._metadata_manager,
                self._stats_collector,
            )

        def handle_response(future):
            self._response_processor.process_response(future, self.rps)

        self._scheduler = RPSScheduler(self._pool, make_request, handle_response)
        # Set the configured RPS value on the scheduler
        self._scheduler.update_rps(self._configured_rps)
        self._scheduler.start_scheduling()

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

        self._running = False
        self._log.info("Stopping client")

        if self._scheduler:
            self._scheduler.stop_scheduling()

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

    @property
    def rps(self) -> float:
        """Get current requests per second rate (thread-safe)."""
        if self._scheduler:
            return self._scheduler.rps
        return 1.0

    def update_rps(self, new_rps: float):
        """Update request rate during runtime."""
        if self._scheduler:
            self._scheduler.update_rps(new_rps)

        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.info("RPS updated at %s to %.1f", curr_time, new_rps)

    def update_transaction(self, new_transaction):
        """Update EDI transaction type during runtime."""
        with self._trans_lock:
            self.transaction = new_transaction
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.info("Transaction updated at %s to %d", curr_time, new_transaction)
