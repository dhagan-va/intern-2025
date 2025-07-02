import sqlite3

from Config.Config import get_local_db_path, TRANSACTIONS_DATABASE_DIRECTORY, TRANSACTIONS_DATABASE


class TransactionFunctions:
    def __init__(self, file=get_local_db_path(TRANSACTIONS_DATABASE_DIRECTORY, TRANSACTIONS_DATABASE)):
        self.file = file
        self.connect = sqlite3.connect(self.file)
        self.cursor = self.connect.cursor()
        self.init_tables()

    def init_tables(self):
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sponsors (
                    sponsor_id TEXT PRIMARY KEY,
                    ssn TEXT,
                    dob TEXT,
                    first_name TEXT,
                    middle_name TEXT,
                    last_name TEXT,
                    gender TEXT,
                    phone TEXT,
                    insurance_company TEXT,
                    insurance_FID TEXT,
                    building_number TEXT,
                    street TEXT,
                    apartment TEXT,
                    city TEXT,
                    state TEXT,
                    zipcode TEXT
                )
            """)
