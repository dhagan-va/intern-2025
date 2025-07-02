import json
import sqlite3

from Config.Config import get_local_db_path, FAMILY_DATABASE_DIRECTORY, FAMILY_DATABASE_SQLITE
from DataLayer.Interfaces import DataAccess


class SQLiteDBFunctions(DataAccess):
    def __init__(self, file=get_local_db_path(FAMILY_DATABASE_DIRECTORY, FAMILY_DATABASE_SQLITE)):
        self.file = file
        self.connect = sqlite3.connect(self.file)
        self.cursor = self.connect.cursor()
        self.init_tables()

    def init_tables(self):
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sponsors (
                    sponsor_id TEXT PRIMARY KEY,
                    ssn TEXT,
                    data TEXT
                )
            """)
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS beneficiaries (
                    sponsor_id TEXT,
                    beneficiary_id TEXT,
                    ssn TEXT,
                    data TEXT,
                    PRIMARY KEY (sponsor_id, beneficiary_id),
                    FOREIGN KEY (sponsor_id) REFERENCES sponsors(sponsor_id)
                )
            """)
        self.connect.commit()

    def save_sponsor(self, sponsor):
        sponsor_data = sponsor.to_dict()
        sponsor_json = json.dumps(sponsor_data)
        self.cursor.execute("""
            INSERT OR REPLACE INTO sponsors (sponsor_id, ssn, data) VALUES (?, ?, ?) 
        """, (sponsor.sponsor_id, sponsor.ssn, sponsor_json))

        for bene in sponsor.beneficiaries:
            bene_data = bene.to_dict()
            bene_json = json.dumps(bene_data)
            self.cursor.execute("""
            INSERT OR REPLACE INTO beneficiaries (sponsor_id, beneficiary_id, ssn, data)
            VALUES (?, ?, ?, ?)
        """, (bene.sponsor_id, bene.beneficiary_id, bene.ssn, bene_json))

        self.connect.commit()

    def ssn_exists(self, ssn):
        pass

    def get_sponsor_by_id(self, sponsor_id):
        pass

    def get_sponsor_field(self, sponsor_id, field):
        pass

    def update_sponsor_field(self, sponsor_id, field, value):
        pass

    def get_beneficiary(self, sponsor_id, beneficiary_id):
        pass

    def get_beneficiary_field(self, sponsor_id, beneficiary_id, field):
        pass

    def update_beneficiary_field(self, sponsor_id, beneficiary_id, field, value):
        pass

    def get_bene_visit(self, sponsor_id, beneficiary_id, code):
        pass

    def get_bene_deductible(self, sponsor_id, beneficiary_id, code):
        pass

    def update_bene_deductible(self, sponsor_id, beneficiary_id, code, value):
        pass

    def update_bene_visit(self, sponsor_id, beneficiary_id, code, value):
        pass

