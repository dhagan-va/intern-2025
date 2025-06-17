import logging
import os
from datetime import datetime

from BellShapes import BellShapes, fit_range_to_half_bel

# Time and File Info
DATE = datetime.now()
CCYYMMDD = DATE.strftime("%Y%m%d")

TEST_FILE_NAME = f'834.VFMP.{DATE.year}.{DATE.strftime("%y%m%d")}.{DATE.strftime("%H%M")}.{DATE.strftime("%Y%m%d1")}.edi'
LOCAL_DATABASE = f"localdb.jsonl"

# Paths

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
LOCAL_DATABASE_DIRECTORY = os.path.join(ROOT_PATH, "Output", "Local_DB")
EDI_OUTPUT_DIRECTORY = os.path.join(ROOT_PATH, "Output", "Test_Files_834")
LOG_DIRECTORY = os.path.join(ROOT_PATH, "Output")
os.makedirs(LOG_DIRECTORY, exist_ok=True)


# Creates directory if nonexistent
def get_edi_path():
    os.makedirs(EDI_OUTPUT_DIRECTORY, exist_ok=True)
    logger.info(f"Directory exists: {EDI_OUTPUT_DIRECTORY}")
    return os.path.join(EDI_OUTPUT_DIRECTORY, TEST_FILE_NAME)


def get_local_db_path():
    os.makedirs(LOCAL_DATABASE_DIRECTORY, exist_ok=True)
    logger.info(f"Directory exists: {LOCAL_DATABASE_DIRECTORY}")
    return os.path.join(LOCAL_DATABASE_DIRECTORY, LOCAL_DATABASE)


# Logging
def get_logger(name):
    log_path = os.path.join(LOG_DIRECTORY, f'TestSuite_{CCYYMMDD}.log')
    logging.basicConfig(
        level=0,
        filename=log_path,
        filemode='a'
    )
    return logging.getLogger(name)


logger = get_logger(__name__)

# Constants and config
FAKER_SEED = 49245
RANDOM_SEED = 52

# 834 Constants
SENDER_ID = "83-1002022"
RECEIVER_ID = "841439824"

# Message Error Rate
TOTAL_ERROR_RATE = 0.0005

# Database user limit
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

# Test size generator
NUMBER_OF_TESTS = fit_range_to_half_bel(avg=10627, std=13948, min_val=1, max_val=246778, shape=BellShapes.NORMAL)


def number_of_tests(n=None):
    return NUMBER_OF_TESTS if n is None else n
