import requests
import time
from samples import payloads


def send_edi_request(transaction, endpoint):
    start = time.perf_counter()
    try:
        resp = requests.post(url=endpoint, data=payloads[transaction])
        elapsed = (time.perf_counter() - start) * 1000
        return resp.status_code, elapsed, resp.content
    except Exception:
        return -1, (time.perf_counter() - start) * 1000, ""
