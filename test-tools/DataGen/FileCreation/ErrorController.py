import random

import config
from config import get_logger

logger = get_logger(__name__)


class ErrorCheck:
    def __init__(self, max_messages):
        self.error_rate = config.TOTAL_ERROR_RATE
        self.random_seed = config.RANDOM_SEED
        self.max_errors = max_messages * self.error_rate
        self.error_count = 0

    def should_insert(self):
        if self.error_count >= self.max_errors:
            return False
        val = random.random()
        logger.debug(f"The value of the random number is {val}")
        return val < self.error_rate

    def insert(self, value, kind):
        if self.error_count >= self.max_errors:
            return False
        logger.debug(f"The value of the error is {value}, it is an {kind} error")
        self.error_count += 1
        return insert_error(value, kind)


def insert_error(value, kind):
    match kind:
        case "missing":
            return ""
        case "format":
            return f"~{value}~"
        case "invalid":
            return "!@#INVALID321"
        case "negative":
            return f"-{value}"
    return value
