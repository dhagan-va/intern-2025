import threading
import collections
import time
from typing import Optional, Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from stats import LiveStats


class ConnectionTracker:
    """Tracks concurrent connections for monitoring connection behavior."""
    
    def __init__(self):
        self.active_connections = set()
        self.connection_counter = 0
        self.max_concurrent = 0
        self.total_connections = 0
        self.lock = threading.Lock()
        
    def connection_started(self) -> str:
        """Mark a new connection as started. Returns connection ID."""
        with self.lock:
            self.connection_counter += 1
            conn_id = f"conn_{self.connection_counter}_{int(time.time() * 1000)}"
            self.active_connections.add(conn_id)
            self.total_connections += 1
            
            current_count = len(self.active_connections)
            if current_count > self.max_concurrent:
                self.max_concurrent = current_count
                # DEBUG
                print(f"[DEBUG] New peak concurrent connections: {current_count}")
                
            return conn_id
    
    def connection_finished(self, conn_id: str) -> None:
        """Mark a connection as finished."""
        with self.lock:
            self.active_connections.discard(conn_id)
    
    def get_current_count(self) -> int:
        """Get current number of active connections."""
        with self.lock:
            return len(self.active_connections)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        with self.lock:
            return {
                "current_connections": len(self.active_connections),
                "max_concurrent_connections": self.max_concurrent,
                "total_connections_created": self.total_connections
            }


class StatsCollector:
    """Enhanced statistics collector with better separation of HTTP and EDI concerns."""
    
    def __init__(self):
        self.live_stats = LiveStats()
        self.edi_stats = EdiStatsTracker()
        self.connection_tracker = ConnectionTracker()
        
    def record_response(self, elapsed: float, status: int, edi_error_type: Optional[str] = None) -> None:
        """Record a response with both HTTP and EDI-specific tracking."""
        self.live_stats.update(elapsed, status, edi_error_type)
        
        if status == 200:
            if edi_error_type:
                self.edi_stats.record_edi_error(edi_error_type)
            else:
                self.edi_stats.record_edi_success()
    
    def start_connection(self) -> str:
        """Mark the start of a new HTTP connection. Returns connection ID."""
        return self.connection_tracker.connection_started()
    
    def end_connection(self, conn_id: str) -> None:
        """Mark the end of an HTTP connection."""
        self.connection_tracker.connection_finished(conn_id)
    
    def get_concurrent_connections(self) -> int:
        """Get current number of concurrent connections."""
        return self.connection_tracker.get_current_count()
    
    def snapshot(self) -> Dict[str, Any]:
        """Get combined snapshot with enhanced EDI-aware statistics."""
        base_stats = self.live_stats.snapshot()
        edi_stats = self.edi_stats.get_summary()
        connection_stats = self.connection_tracker.get_stats()
        
        return {
            **base_stats,
            **connection_stats,
            "edi_statistics": edi_stats,
            "total_edi_transactions": edi_stats["total_transactions"],
            "edi_success_rate": edi_stats["success_rate"],
            "edi_error_rate": edi_stats["error_rate"]
        }


class EdiStatsTracker:
    """Specialized tracker for EDI-specific statistics."""
    
    def __init__(self):
        self.error_counts = collections.Counter()
        self.success_count = 0
        self.lock = threading.Lock()
    
    def record_edi_error(self, error_type: str) -> None:
        """Record an EDI-specific error."""
        with self.lock:
            self.error_counts[error_type] += 1
    
    def record_edi_success(self) -> None:
        """Record a successful EDI transaction."""
        with self.lock:
            self.success_count += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of EDI statistics."""
        with self.lock:
            total_errors = sum(self.error_counts.values())
            total_transactions = self.success_count + total_errors
            
            return {
                "total_transactions": total_transactions,
                "success_count": self.success_count,
                "error_count": total_errors,
                "error_breakdown": dict(self.error_counts),
                "success_rate": (
                    self.success_count / total_transactions 
                    if total_transactions > 0 else 0.0
                ),
                "error_rate": (
                    total_errors / total_transactions 
                    if total_transactions > 0 else 0.0
                )
            }