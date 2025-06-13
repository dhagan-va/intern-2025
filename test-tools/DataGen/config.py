import logging
from datetime import datetime

from BellShapes import BellShapes, fit_range_to_half_bel

FAKER_SEED = 49245
RANDOM_SEED = 52

DATE = datetime.now()
CCYYMMDD = DATE.strftime("%Y%m%d")

SENDER_ID = "83-1002022"
RECEIVER_ID = "841439824"

LOCAL_DATABASE = "localdb.jsonl"

NUMBER_OF_TESTS = fit_range_to_half_bel(avg=10627, std=13948, min_val=1, max_val=246778, shape=BellShapes.NORMAL)
OUTPUT_DIRECTORY_NAME = 'Test_Files_834'
USER_LIMIT = 500_000

RELATIONSHIP_MAP = {
    'Spouse': '01',
    'Child': '19',
    'Caregiver': '26',
    'Ex-Spouse': '25'
}


def get_logger(name):
    logging.basicConfig(
        level=logging.INFO,
        filename=f'TestSuite_{CCYYMMDD}.log',
        filemode='a'
    )
    return logging.getLogger(name)
