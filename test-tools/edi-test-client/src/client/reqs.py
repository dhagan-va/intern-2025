import requests
import time
import samples

def send_270_request(endpoint):
    start = time.perf_counter()
    try:
        resp = requests.post(url=endpoint, data=samples.SAMPLE_270)
        elapsed = (time.perf_counter() - start) * 1000
        return resp.status_code, elapsed
    except Exception:
        return -1, (time.perf_counter() - start) * 1000
