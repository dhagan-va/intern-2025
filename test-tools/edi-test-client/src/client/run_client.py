import requests
import sys
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import load_settings
import reqs
import time


def log_result(fut, logger):
    status, elapsed = fut.result()
    if status == 200:
        logger.info("200 OK in %.2f ms", elapsed)
    else:
        logger.error("ERR %d in %.2f ms", status, elapsed)

def main():
    cfg = load_settings()
    logger = logging.getLogger("edi_client")
    logging.basicConfig(filename='test.log', level=logging.INFO)
    logger.info("Client started with %d RPS", cfg.rps)
    reqs_sent = 0
    with ThreadPoolExecutor(max_workers=cfg.rps) as pool:
        next_run = time.perf_counter()
        try:
            while True:
                fut = pool.submit(reqs.send_270_request, cfg.endpoint)
                fut.add_done_callback(lambda f: log_result(f, logger))
                reqs_sent += 1
                next_run += 1.0 / cfg.rps
                time.sleep(max(0, next_run - time.perf_counter()))
        except KeyboardInterrupt:
            logger.info("Stopped by user")

if __name__ == "__main__":
    main()
