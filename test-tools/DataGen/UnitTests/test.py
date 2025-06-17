import unittest
import os
import config

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

class TestErrorRate(unittest.Testcase):
    def test_error_rates(self):
        self.assertTrue()

# Make message, test if contents are valid, make sure its not the same every time
class singleEDIMessage(unittest.TestCase):
    def make_one(self):
        
            
        self.assertTrue(os.exists(config.TEST_FILE_NAME))