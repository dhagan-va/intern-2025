import requests
import time
import sys
from pathlib import Path
import random
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from client.samples import payloads


def extract_st_control_number(edi_content):
    """Extract ST control number from EDI content for header mapping."""
    try:
        match = re.search(r'ST\*270\*(\d+)', edi_content)
        return match.group(1) if match else None
    except Exception:
        return None


def send_edi_request(transaction, endpoint, metadata_manager=None):
    start = time.perf_counter()
    try:
        payload = random.choice(payloads[transaction])
        headers = {"Content-Type": "application/x-edi"}
        
        if metadata_manager:
            st_control = extract_st_control_number(payload)
            if st_control:
                error_info = metadata_manager.get_error_info(st_control)
                if error_info:
                    headers.update(error_info)
        
        resp = requests.post(url=endpoint, data=payload, headers=headers)
        elapsed = (time.perf_counter() - start) * 1000
        return resp.status_code, elapsed, resp.content
    except Exception:
        return -1, (time.perf_counter() - start) * 1000, ""