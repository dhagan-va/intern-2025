import csv
from dataclasses import dataclass


@dataclass
class Result:
    timestamp: float
    latency: float
    http: int


class AbstractSink:
    def write(self, result: Result):
        raise NotImplementedError


class CsvSink(AbstractSink):
    def __init__(self, path):
        self._path = 

    def write(self, result: Result):
        return
