import csv
from dataclasses import dataclass
from pathlib import Path
import pandas as pd


class AbstractSink:
    def write(self):
        raise NotImplementedError


class CsvSink(AbstractSink):
    def __init__(self, path):
        self._path = Path(path)
        self.result_df = pd.DataFrame(
            columns=["timestamp", "latency", "http", "rps", "payload"]
        )

    def append(self, stamp, lat, status, rps, payload):
        self.result_df.loc[len(self.result_df)] = [stamp, lat, status, rps, payload]

    def write(self):
        self.result_df.to_csv(self._path)
