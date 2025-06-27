from dataclasses import dataclass
import tomllib
from pathlib import Path

DEFAULT_CONF = Path(__file__).parent / 'conf' / 'default.toml'

@dataclass
class Setting:
    """
    Class representing configuration settings for test client.
    """
    endpoint: str
    rps: float
    threads: int
    def __init__(self, endpoint : str, rps : float, threads : int):
        self.endpoint = endpoint
        self.rps = rps
        self.threads = threads

def load_settings():
    with open(DEFAULT_CONF, 'rb') as f:
        data = tomllib.load(f)
        return Setting(data['endpoint'], data['rps'], data['threads'])