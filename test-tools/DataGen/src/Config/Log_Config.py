import logging
import os
from datetime import datetime

DATE = datetime.now()
CCYYMMDD = DATE.strftime("%Y%m%d")
LOG_DIRECTORY = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "Output", "Logs")
LOG_FILE = f'TestSuite_{CCYYMMDD}.log'

os.makedirs(LOG_DIRECTORY, exist_ok=True)


def get_logger(name):
    log_path = os.path.join(LOG_DIRECTORY, LOG_FILE)
    logging.basicConfig(
        level=logging.INFO,
        filename=log_path,
        filemode='a',
        format = '%(asctime)s - %(levelname)s - %(name)s.%(funcName)s - %(message)s'
    )
    return logging.getLogger(name)
