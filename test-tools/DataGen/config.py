import logging
from BellShapes import BellShapes, fit_range_to_half_bel

FAKER_SEED = 49245
RANDOM_SEED = 52

NUMBER_OF_TESTS = fit_range_to_half_bel(avg=10627, std=13948, min_val=1, max_val=246778, shape=BellShapes.NORMAL)
DIRECTORY_NAME = 'Test_Files_834'
USER_LIMIT = 500_000

logging.basicConfig(
    level=logging.INFO,
    filename='TestSuite.log',
    filemode='a'
)


def get_logger(name):
    return logging.getLogger(name)
