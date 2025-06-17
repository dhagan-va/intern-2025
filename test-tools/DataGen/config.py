import logging
import os
from datetime import datetime

from BellShapes import BellShapes, fit_range_to_half_bel

FAKER_SEED = 49245
RANDOM_SEED = 52

DATE = datetime.now()
CCYYMMDD = DATE.strftime("%Y%m%d")

SENDER_ID = "83-1002022"
RECEIVER_ID = "841439824"

TOTAL_ERROR_RATE = 0.0005

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
LOCAL_DATABASE_DIRECTORY = os.path.join(ROOT_PATH, "Local_DB")
LOCAL_DATABASE = f"localdb.jsonl"

TEST_FILE_NAME = f'834.VFMP.{DATE.year}.{DATE.strftime("%y%m%d")}.{DATE.strftime("%H%M")}.{DATE.strftime("%Y%m%d1")}.edi'

NUMBER_OF_TESTS = fit_range_to_half_bel(avg=10627, std=13948, min_val=1, max_val=246778, shape=BellShapes.NORMAL)
OUTPUT_DIRECTORY_NAME = 'Test_Files_834'
USER_LIMIT = 500_000

RELATIONSHIP_MAP = {
    'Spouse': '01',
    'Child': '19',
    'Caregiver': '26',
    'Ex-Spouse': '25'
}

MAX_BENEFICIARIES = 4
MIN_BENEFICIARIES = 1
MAX_DEDUCTIBLES = 100_000
MIN_DEDUCTIBLES = 0
MAX_VISITS = 15
MIN_VISITS = 0

def get_local_db_path():
    os.makedirs(LOCAL_DATABASE_DIRECTORY, exist_ok=True)
    return os.path.join(LOCAL_DATABASE_DIRECTORY, LOCAL_DATABASE)


def get_logger(name):
    logging.basicConfig(
        level=logging.INFO,
        filename=f'TestSuite_{CCYYMMDD}.log',
        filemode='a'
    )
    return logging.getLogger(name)
