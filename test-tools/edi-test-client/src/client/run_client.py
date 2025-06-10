import requests
import sys
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import load_settings
import time



SAMPLE_270 = (
"ISA*00*          *00*          *ZZ*1234567        *ZZ*11111          *170508*1141*^*00501*000000101*1*P*:~\n"
"GS*HC*XXXXXXX*XXXXX*20170617*1741*101*X*005010X279A1~\n"
"ST*270*1234*005010X279A1~\n"
"BHT*0022*13*10001234*20060501*1319~\n"
"HL*1**20*1~\n"
"NM1*PR*2*ABC COMPANY*****PI*842610001~\n"
"HL*2*1*21*1~\n"
"NM1*1P*2*BONE AND JOINT CLINIC*****SV*2000035~\n"
"HL*3*2*22*0~\n"
"TRN*1*93175-012547*9877281234~\n"
"NM1*IL*1*SMITH*ROBERT****MI*11122333301~\n"
"DMG*D8*19430519~\n"
"DTP*291*D8*20060501~\n"
"EQ*30~\n"
"SE*13*1234~\n"
"GE*1*101~\n"
"IEA*1*000000101~\n"
)


def send_270_request(endpoint):
    start = time.perf_counter()
    try:
        resp = requests.post(url=endpoint, data=SAMPLE_270)
        elapsed = (time.perf_counter() - start)*1000
        return resp.status_code, elapsed
    except Exception:
        return -1, (time.perf_counter() - start)*1000

def main():
    cfg = load_settings()
    logger = logging.getLogger("edi_client")
    logging.basicConfig(filename='test.log', level=logging.INFO)
    logger.info("Client started with %d RPS", cfg.rps)
    reqs_sent = 0
    with ThreadPoolExecutor() as pool:
        futures = []
        try:
            while True:
                futures.append(pool.submit(send_270_request, cfg.endpoint))
                reqs_sent += 1
                time.sleep(max(1/cfg.rps - time.perf_counter(), 0))
        except KeyboardInterrupt:
            logger.info("Stopped by user")
    ok = 0
    err = 0
    for f in futures:
        status, _ = f.result()
        if status == 200:
            ok += 1
        else:
            err += 1
        logger.info("Completed %d requests with 200 OK: %d, ERROR: %d", reqs_sent, ok, err)


if __name__ == "__main__":
    main()
