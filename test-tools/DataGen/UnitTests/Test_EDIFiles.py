import logging
import math
import os.path
import shutil
import unittest

import log_config
import config
from FileCreation.ErrorInjector import ErrorInjector
from Repository.Local_Database_Functions import LocalDBFunctions
from Repository.NPI_Functions import NPIFunctions, download_weekly_npi_data
from RunGenerator import Run834Generator, Run270Generator


class Test834Message(unittest.TestCase):
    def setUp(self):
        logging.shutdown()

        output_dir = os.path.join(config.ROOT_PATH, "Output")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        os.makedirs(log_config.LOG_DIRECTORY, exist_ok=True)
        config.get_edi_path(config.EDI834_PATH, config.EDI834_FILE_NAME)
        config.get_local_db_path()
        self.logger = config.get_logger(__name__)
        self.messages = 7
        self.error_rate = 0
        Run834Generator(max_messages=self.messages, error_rate=self.error_rate)
        self.path = config.get_edi_path(config.EDI834_PATH, config.EDI834_FILE_NAME)
        with open(self.path) as f:
            self.lines = [line.strip() for line in f if line.strip()]

    def test_duplicate_ssns(self):
        db = LocalDBFunctions()
        ssns = []

        for sponsor in db.data:
            ssns.append(sponsor.ssn)
            for b in sponsor.beneficiaries:
                ssns.append(b.ssn)

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

    def test_834_error_rates(self):
        injector = ErrorInjector(max_messages=self.messages, error_rate=self.error_rate)
        expected = self.messages * self.error_rate

        actual_inserts = 0
        for _ in range(self.messages):
            if injector.should_insert():
                injector.insert("test", "missing")
                actual_inserts += 1

        # check if error_count and inserts are same, do we need a margin of failures?
        self.assertTrue(math.isclose(actual_inserts, expected, abs_tol=1),
                        f"Actual errors {actual_inserts}, expected {expected}")


class Test270Message(unittest.TestCase):
    def setUp(self):
        logging.shutdown()

        output_dir = os.path.join(config.ROOT_PATH, "Output")
        download_dir = os.path.join(config.ROOT_PATH, "Downloads")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)

        os.makedirs(log_config.LOG_DIRECTORY, exist_ok=True)
        os.makedirs(config.DOWNLOAD_DIRECTORY, exist_ok=True)

        npi_csv_path = download_weekly_npi_data(config.DOWNLOAD_DIRECTORY)
        self.npi_funcs = NPIFunctions(npi_csv_path)

        self.messages_834 = 5
        self.error_rate_834 = 0
        Run834Generator(max_messages=self.messages_834, error_rate=self.error_rate_834)

        self.messages_270 = 100
        self.error_rate_270 = 0
        Run270Generator(max_messages=self.messages_270, error_rate=self.error_rate_270)
        self.path = config.get_edi_path(config.EDI270_PATH, config.EDI270_FILE_NAME)
        self.logger = config.get_logger(__name__)

        with open(self.path) as f:
            self.lines = [line.strip() for line in f if line.strip()]

    def test_valid_NPI(self):
        provider_npis = []
        for line in self.lines:
            line = line.rstrip("~").strip()
            parts = line.split("*")
            if parts[0] == "NM1" and parts[1] == "1P":
                provider_npis.append(parts[9])

        df = self.npi_funcs.load_csv()
        valid_npis = set(df["NPI"])
        
        for npi in provider_npis:
            self.assertTrue(npi.isdigit() and len(npi) == 10, f"Invalid NPI format: {npi}")
            self.assertIn(npi, valid_npis, f"NPI {npi} not found in CSV")
        
    def test_270_message_validity(self):
        for line in self.lines:
            line = line.rstrip("~").strip()
            parts = line.split("*")
            if line.startswith("HL"):
                self.assertTrue(parts[3].strip(), f"HL code is empty: {line}")
            elif line.startswith("NM1"):
                self.assertFalse(any(c in parts[9] for c in ("~", ":")), f"Invalid char in SSN: {parts[9]}")

    def test_270_error_rates(self):
        injector = ErrorInjector(max_messages=self.messages_270, error_rate=self.error_rate_270)
        expected = self.messages_270 * self.error_rate_270

        actual_inserts = 0
        for _ in range(self.messages_270):
            injector.reset_error_inserted()
            if injector.should_insert():
                injector.insert("test", "missing")
                actual_inserts += 1

        self.assertTrue(math.isclose(actual_inserts, expected, abs_tol=1),
                        f"Actual errors {actual_inserts}, expected {expected}")

if __name__ == "__main__":
    runner = unittest.TextTestRunner()