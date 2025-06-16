import random

import config
from config import get_logger

logger = get_logger(__name__)


class ErrorCheck:
    def __init__(self, error_rate=config.TOTAL_ERROR_RATE):
        self.error_rate = error_rate
        self.used = False

    def should_insert(self):
        val = random.random()
        logger.debug(f"The value of the random number is {val}")
        return not self.used and val < self.error_rate

    def insert(self, value, kind):
        if self.used:
            return value
        self.used = True
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
