import unittest

import config
from FileCreation.ErrorInjector import ErrorInjector
from Repository.Local_Database_Functions import LocalDBFunctions
from RunGenerator import RunGenerator


# Make message, test if contents are valid, make sure it's not the same every time
class Test834Message(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.messages = 10
        cls.error_rate = 0
        RunGenerator(max_messages=cls.messages, error_rate=cls.error_rate)
        cls.path = config.get_edi_path()
        with open(cls.path) as f:
            cls.lines = [line.strip() for line in f if line.strip()]

    def test_duplicate_ssns(self):
        db = LocalDBFunctions()
        ssns = []

        for sponsor in db.data:
            ssns.append(sponsor["ssn"])
            for b in sponsor.get("beneficiaries", []):
                ssns.append(b["ssn"])

        unique_ssns = set(ssns)
        self.assertEqual(len(ssns), len(unique_ssns), "Duplicate SSNs found")

    def test_834_message_validity(self):
        for line in self.lines:
            line = line.rstrip("~").strip()
            parts = line.split("*")

            if line.startswith("N1"):
                self.assertTrue(parts[4].strip(), f"N1 ID is empty: {line}")

            elif line.startswith("NM1"):
                self.assertFalse(any(c in parts[9] for c in ("~", ":")), f"Invalid char in SSN: {parts[9]}")

            elif line.startswith("PER"):
                self.assertTrue(parts[4].strip(), f"PER phone is empty: {line}")

            elif line.startswith("N3"):
                self.assertTrue("!@#" not in parts[1], f"Invalid street: {line}")

            elif line.startswith("N4"):
                self.assertTrue("!@#" not in parts[1], f"Invalid city: {line}")

            elif line.startswith("AMT"):
                amount_str = parts[2].replace("~", "")
                self.assertGreaterEqual(float(amount_str), 0, f"Invalid AMT: {line}")

    def test_error_rates(self):
        injector = ErrorInjector(max_messages=self.messages, error_rate=self.error_rate)

        actual_inserts = 0
        for _ in range(self.messages):
            if injector.should_insert():
                injector.insert("test", "missing")
                actual_inserts += 1

        # check if error_count and inserts are same, do we need a margin of failures?
        self.assertEqual(injector.error_count, actual_inserts,
                         f"Actual errors: {actual_inserts}, Expected: {injector.error_count}")
