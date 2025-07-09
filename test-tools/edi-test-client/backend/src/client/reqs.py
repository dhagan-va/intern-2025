import requests
import time
import sys
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from client.samples import payloads


def send_edi_request(transaction, endpoint):
    start = time.perf_counter()
    try:
        payload = random.choice(payloads[transaction])
        resp = requests.post(url=endpoint, data=payload)
        elapsed = (time.perf_counter() - start) * 1000
        return resp.status_code, elapsed, resp.content
    except Exception:
        return -1, (time.perf_counter() - start) * 1000, ""