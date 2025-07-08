import threading, collections


class LiveStats:
    def __init__(self):
        self.codes = collections.Counter()
        self.lock = threading.Lock()
        self.latencies = []

    def update(self, latency, http):
        with self.lock:
            self.codes[http] += 1
            self.latencies.append(latency)

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
            }
