import logging
import random

FAKER_SEED = 49245
RANDOM_SEED = 52

NUMBER_OF_TESTS = random.gauss(10_627, 13_948)  # Binom dist for number of tests so that it generates the typical production rate, need to make it redo if it is negative
DIRECTORY_NAME = 'Test_Files_834'
USER_LIMIT = 500_000

logging.basicConfig(
    level=logging.INFO,
    filename='TestSuite.log',
    filemode='a'
)


def get_logger(name):
    return logging.getLogger(name)
