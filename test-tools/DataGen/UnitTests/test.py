import unittest

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
