from dataclasses import dataclass
import tomllib
from pathlib import Path

DEFAULT_CONF = Path('conf/default.toml')

@dataclass
class Setting:
    """
    eee
    """
    endpoint: str
    rps: int

    def __init__(self, endpoint : str, rps : int):
        self.endpoint = endpoint
        self.rps = rps

def load_settings():
    with open(DEFAULT_CONF, 'rb') as f:
        data = tomllib.load(f)
        return Setting(data['endpoint'], data['rps'])


