import random

from Config import Config
from Config.Config import logger


class ErrorInjector:
    def __init__(self, num_messages, error_rate):
        self.random_seed = Config.RANDOM_SEED
        self.error_rate = Config.get_error_rate(error_rate)
        self.max_errors = num_messages * self.error_rate
        self.error_count = 0
        self.error_inserted = False
        random.seed(self.random_seed)

    def reset_error_inserted(self):
        self.error_inserted = False

    def should_insert(self):
        if self.error_count >= self.max_errors or self.error_inserted:
            return False
        val = random.random()
        logger.debug(f"The value of the random number is {val}")
        return val < self.error_rate

    def insert(self, value, kind):
        if self.error_count >= self.max_errors or self.error_inserted:
            return value
        logger.debug(f"The value of the error is {value}, it is an {kind} error")
        self.error_inserted = True
        self.error_count += 1
        return insert_error(value, kind)


def insert_error(value, kind):
    match kind:
        case "missing":
            return " "
        case "format":
            return f"~{value}??"
        case "invalid":
            return "!@#INVALID321"
        case "negative":
            return f"-{value}"
    return value
