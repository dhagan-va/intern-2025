import unittest
import os
import config
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


# class TestErrorRate(unittest.Testcase):
#     def test_error_rates(self):
#         self.assertTrue()


# Make message, test if contents are valid, make sure it's not the same every time
class singleEDIMessage(unittest.TestCase):
    def test_make_one(self):
        run_test_suite(n=2)
        path = os.path.join(config.EDI_OUTPUT_DIRECTORY, config.TEST_FILE_NAME)
        self.assertTrue(os.path.isfile(path), f"file not found at: {path}")
