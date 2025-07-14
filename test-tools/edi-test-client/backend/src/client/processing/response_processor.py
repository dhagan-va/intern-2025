from datetime import datetime
import logging
from typing import Optional, Callable, Any


class EdiResponseAnalyzer:
    """Analyzes EDI response content to categorize errors."""
    
    @staticmethod
    def categorize_edi_error(response_body: str) -> Optional[str]:
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
    
    @staticmethod
    def has_edi_error(response_body: str) -> bool:
        """Check if response contains EDI error (AAA segment)."""
        return "AAA*N*" in response_body


class ResponseProcessor:
    """Processes HTTP responses and delegates to appropriate handlers."""
    
    def __init__(self, stats_collector, result_sink, logger: logging.Logger):
        self.stats_collector = stats_collector
        self.result_sink = result_sink
        self.logger = logger
        self.edi_analyzer = EdiResponseAnalyzer()
    
    def process_response(self, future, current_rps: float) -> None:
        """Process completed HTTP requests and update statistics."""
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            status, elapsed, body = future.result()
            edi_error_type = self._analyze_response(status, elapsed, body)
            
            self.stats_collector.update(elapsed, status, edi_error_type)
            self.result_sink.append(curr_time, elapsed, status, current_rps, body)
            
        except Exception as e:
            self.logger.error("Error handling response: %s", e)
    
    def _analyze_response(self, status: int, elapsed: float, body: Any) -> Optional[str]:
        """Analyze response to determine EDI error type and log appropriately."""
        edi_error_type = None
        
        if status == 200 and body:
            body_str = body.decode("utf-8") if isinstance(body, bytes) else str(body)
            
            if self.edi_analyzer.has_edi_error(body_str):
                edi_error_type = self.edi_analyzer.categorize_edi_error(body_str)
                self.logger.info(
                    "200 OK with EDI error (%s) in %.3f ms", edi_error_type, elapsed
                )
            else:
                self.logger.info("200 OK (EDI success) in %.3f ms", elapsed)
        elif status == 200:
            self.logger.info("200 OK in %.3f ms", elapsed)
        else:
            self.logger.error("HTTP ERR %d in %.3f ms", status, elapsed)
        
        return edi_error_type