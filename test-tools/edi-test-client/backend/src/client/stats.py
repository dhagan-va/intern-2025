import threading, collections


class LiveStats:
    def __init__(self):
        self.codes = collections.Counter()
        self.edi_errors = collections.Counter()
        self.lock = threading.Lock()
        self.latencies = []

    def update(self, latency, http_status, edi_error_type=None):
        with self.lock:
            self.codes[http_status] += 1
            self.latencies.append(latency)

            if edi_error_type:
                self.edi_errors[edi_error_type] += 1

    def snapshot(self):
        with self.lock:
            return {
                "count": len(self.latencies),
                "avg_latency": (
                    sum(self.latencies) / len(self.latencies)
                    if len(self.latencies) != 0
                    else 0
                ),
                "codes": dict(self.codes),
                "edi_errors": dict(self.edi_errors),
                "edi_success_count": self.codes.get(200, 0) - sum(self.edi_errors.values()),
                "edi_error_count": sum(self.edi_errors.values()),
                "http_error_count": sum(v for k, v in self.codes.items() if k != 200),
            }
