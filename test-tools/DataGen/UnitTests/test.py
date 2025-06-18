import unittest
import os
import config
import random
from TestSuite import run_test_suite

from Repository.Local_Database_Functions import LocalDBFunctions


class TestDuplicateSSNs(unittest.TestCase):
    def test_duplicate_ssns(self):
        db = LocalDBFunctions()
        ssns = []

        for sponsor in db.data:
            ssns.append(sponsor["ssn"])
            for b in sponsor.get("beneficiaries", []):
                ssns.append(b["ssn"])

        unique_ssns = set(ssns)
        self.assertEqual(len(ssns), len(unique_ssns), "Duplicate SSNs found")


class TestErrorRate(unittest.TestCase):
    def test_error_rates(self):
        messages = 100000
        expected_error_rate = config.TOTAL_ERROR_RATE
        error_check = ErrorCheck(max_messages=messages)

        actual_inserts = 0
        for _ in range(messages):
            if error_check.should_insert():
                error_check.insert("test", "missing")
                actual_inserts += 1

        # check if error_count and inserts are same
        self.assertEqual(error_check.error_count, actual_inserts)

        expected_errors = (expected_error_rate * messages)
        # 10% margin
        margin = int(0.1 * expected_errors)

        # Checks if the error count is within the margin
        self.assertTrue(abs(actual_inserts - expected_errors) <= margin,
                        f"Actual errors: {actual_inserts}, Expected: {expected_errors} {u"\u00B1"} {margin}")


# Make message, test if contents are valid, make sure it's not the same every time
class singleEDIMessage(unittest.TestCase):
    def test_make_one(self):
        run_test_suite(n=1000)
        path = os.path.join(config.EDI_OUTPUT_DIRECTORY, config.TEST_FILE_NAME)
        self.assertTrue(os.path.isfile(path), f"file not found at: {path}")

    # def test_check_message_validity(self):

