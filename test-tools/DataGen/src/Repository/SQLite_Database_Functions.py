import sqlite3

from datetime import date
from DataLayer.Datatypes import Address, Beneficiary, Sponsor
from Config.Config import get_local_db_path, FAMILY_DATABASE_DIRECTORY, FAMILY_DATABASE_SQLITE
from Config.Config import logger
from DataLayer.Interfaces import DataAccess


class SQLiteDBFunctions(DataAccess):
    def __init__(self, file=get_local_db_path(FAMILY_DATABASE_DIRECTORY, FAMILY_DATABASE_SQLITE)):
        self.file = file
        self.connect = sqlite3.connect(self.file)
        self.connect.row_factory = sqlite3.Row
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
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS beneficiaries (
                    sponsor_id TEXT,
                    beneficiary_id TEXT,
                    ssn TEXT,
                    dob TEXT,
                    first_name TEXT,
                    middle_name TEXT,
                    last_name TEXT,
                    gender TEXT,
                    phone TEXT,
                    insurance_company TEXT,
                    insurance_FID TEXT,
                    relationship TEXT,
                    building_number TEXT,
                    street TEXT,
                    apartment TEXT,
                    city TEXT,
                    state TEXT,
                    zipcode TEXT,
                    PRIMARY KEY (sponsor_id, beneficiary_id),
                    FOREIGN KEY (sponsor_id) REFERENCES sponsors(sponsor_id)
                )
            """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS deductibles (
                sponsor_id TEXT,
                beneficiary_id TEXT,  -- NULL if it's a sponsor-level deductible
                code TEXT,
                amount REAL,
                PRIMARY KEY (sponsor_id, beneficiary_id, code),
                FOREIGN KEY (sponsor_id, beneficiary_id) REFERENCES beneficiaries(sponsor_id, beneficiary_id)
            )
        """)
        self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS visit_counts (
                    sponsor_id TEXT,
                    beneficiary_id TEXT,  -- NULL if it's a sponsor-level visit count
                    code TEXT,
                    count INTEGER,
                    PRIMARY KEY (sponsor_id, beneficiary_id, code),
                    FOREIGN KEY (sponsor_id, beneficiary_id) REFERENCES beneficiaries(sponsor_id, beneficiary_id)
                )
            """)
        self.connect.commit()

    def save_sponsor(self, sponsor, commit=True):
        self.cursor.execute("""
                INSERT OR REPLACE INTO sponsors (
                    sponsor_id, ssn, dob, first_name, middle_name, last_name, gender,
                    phone, insurance_company, insurance_FID, building_number, street,
                    apartment, city, state, zipcode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
            sponsor.sponsor_id,
            sponsor.ssn,
            sponsor.dob.isoformat(),
            sponsor.first_name,
            sponsor.middle_name,
            sponsor.last_name,
            sponsor.gender,
            sponsor.phone,
            sponsor.insurance_company,
            sponsor.insurance_FID,
            sponsor.address.building_number,
            sponsor.address.street,
            sponsor.address.apartment,
            sponsor.address.city,
            sponsor.address.state,
            sponsor.address.zipcode
        ))

        for code, amount in sponsor.deductibles.items():
            self.cursor.execute("""
                    INSERT OR REPLACE INTO deductibles (sponsor_id, beneficiary_id, code, amount)
                    VALUES (?, NULL, ?, ?)
                """, (sponsor.sponsor_id, code, amount))

        for code, count in sponsor.visit_counts.items():
            self.cursor.execute("""
                    INSERT OR REPLACE INTO visit_counts (sponsor_id, beneficiary_id, code, count)
                    VALUES (?, NULL, ?, ?)
                """, (sponsor.sponsor_id, code, count))

        for bene in sponsor.beneficiaries:
            self.cursor.execute("""
                    INSERT OR REPLACE INTO beneficiaries (
                        sponsor_id, beneficiary_id, ssn, dob, first_name, middle_name, last_name,
                        gender, phone, insurance_company, insurance_FID, relationship,
                        building_number, street, apartment, city, state, zipcode
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                bene.sponsor_id,
                bene.beneficiary_id,
                bene.ssn,
                bene.dob.isoformat(),
                bene.first_name,
                bene.middle_name,
                bene.last_name,
                bene.gender,
                bene.phone,
                bene.insurance_company,
                bene.insurance_FID,
                bene.relationship,
                bene.address.building_number,
                bene.address.street,
                bene.address.apartment,
                bene.address.city,
                bene.address.state,
                bene.address.zipcode
            ))

            for code, amount in bene.deductibles.items():
                self.cursor.execute("""
                        INSERT OR REPLACE INTO deductibles (sponsor_id, beneficiary_id, code, amount)
                        VALUES (?, ?, ?, ?)
                    """, (sponsor.sponsor_id, bene.beneficiary_id, code, amount))

            for code, count in bene.visit_counts.items():
                self.cursor.execute("""
                        INSERT OR REPLACE INTO visit_counts (sponsor_id, beneficiary_id, code, count)
                        VALUES (?, ?, ?, ?)
                    """, (sponsor.sponsor_id, bene.beneficiary_id, code, count))
        if commit:
            self.connect.commit()

    def save_many_sponsors(self, sponsors):
        try:
            logger.info(f"Saving {len(sponsors)} sponsors to the database")
            self.connect.execute("BEGIN TRANSACTION")
            for sponsor in sponsors:
                self.save_sponsor(sponsor, commit=False)
            self.connect.commit()
        except Exception as e:
            self.connect.rollback()
            logger.error(f"No sponsors were saved due to an error: {e}")
            raise e

    def get_random_beneficiary(self, count):
        self.cursor.execute("""
            SELECT *
            FROM beneficiaries
            ORDER BY RANDOM()
            LIMIT ?
        """, (count,))
        bene_rows = self.cursor.fetchall()

        beneficiaries = []
        for row in bene_rows:
            sponsor_id = row["sponsor_id"]
            beneficiary_id = row["beneficiary_id"]

            self.cursor.execute("""
                SELECT building_number, street, apartment, city, state, zipcode
                FROM sponsors
                WHERE sponsor_id = ?
            """, (sponsor_id,))
            sponsor_addr = self.cursor.fetchone()
            address = Address(**sponsor_addr)

            self.cursor.execute("""
                SELECT code, amount FROM deductibles
                WHERE sponsor_id = ? AND  beneficiary_id = ?
            """, (sponsor_id, beneficiary_id))
            deductibles = {code: amount for code, amount in self.cursor.fetchall()}

            self.cursor.execute("""
                SELECT code, count FROM visit_counts
                WHERE sponsor_id = ? AND beneficiary_id = ?
            """, (sponsor_id, beneficiary_id))
            visit_counts = {code: count for code, count in self.cursor.fetchall()}

            bene = Beneficiary(
                ssn=row["ssn"],
                dob=date.fromisoformat(row["dob"]),
                first_name=row["first_name"],
                last_name=row["last_name"],
                gender=row["gender"],
                address=address,
                phone=row["phone"],
                insurance_company=row["insurance_company"],
                insurance_FID=row["insurance_FID"],
                middle_name=row["middle_name"],
                sponsor_id=sponsor_id,
                beneficiary_id=beneficiary_id,
                relationship=row["relationship"],
                deductibles=deductibles,
                visit_counts=visit_counts
            )
            beneficiaries.append(bene)
        return beneficiaries

    def total_beneficiaries(self):
        self.cursor.execute("SELECT COUNT(*) FROM beneficiaries")
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_all_ssns(self):
        sponsor_ssns = self.cursor.execute("SELECT ssn from sponsors").fetchall()
        beneficiary_ssns = self.cursor.execute("SELECT ssn from beneficiaries").fetchall()
        return [row["ssn"] for row in sponsor_ssns + beneficiary_ssns]

    def ssn_exists(self, ssn):
        self.cursor.execute("""
            SELECT 1 FROM sponsors WHERE ssn = ?
            UNION
            SELECT 1 FROM beneficiaries WHERE ssn = ?
        """, (ssn, ssn))
        return self.cursor.fetchone() is not None

    def get_sponsor_by_id(self, sponsor_id):
        self.cursor.execute("""
            SELECT * FROM sponsors
            WHERE sponsor_id = ?
        """, (sponsor_id,))
        row = self.cursor.fetchone()
        if not row:
            logger.warning(f"No sponsor found for ID: {sponsor_id}")
            return

        address = Address(
            building_number=row["building_number"],
            street=row["street"],
            apartment=row["apartment"],
            city=row["city"],
            state=row["state"],
            zipcode=row["zipcode"]
        )

        return Sponsor(
            sponsor_id=row["sponsor_id"],
            ssn=row["ssn"],
            dob=date.fromisoformat(row["dob"]),
            first_name=row["first_name"],
            middle_name=row["middle_name"],
            last_name=row["last_name"],
            gender=row["gender"],
            phone=row["phone"],
            insurance_company=row["insurance_company"],
            insurance_FID=row["insurance_FID"],
            address=address,
            deductibles={},
            visit_counts={},
            beneficiaries=[]
        )

    def get_sponsor_field(self, sponsor_id, field):
        pass

    def update_sponsor_field(self, sponsor_id, field, value):
        pass

    def get_beneficiary(self, sponsor_id, beneficiary_id):
        self.cursor.execute("""
                SELECT * FROM beneficiaries
                WHERE sponsor_id = ? AND beneficiary_id = ?
            """, (sponsor_id, beneficiary_id))
        row = self.cursor.fetchone()
        logger.debug(f"Fetching beneficiary: sponsor_id={sponsor_id}, beneficiary_id={beneficiary_id}")
        if not row:
            logger.warning(f"Beneficiary not found for sponsor_id={sponsor_id}, beneficiary_id={beneficiary_id}")
            return

        self.cursor.execute("""
                SELECT building_number, street, apartment, city, state, zipcode
                FROM sponsors
                WHERE sponsor_id = ?
            """, (sponsor_id,))
        sponsor_addr = self.cursor.fetchone()
        address = Address(**sponsor_addr)

        self.cursor.execute("""
                SELECT code, amount FROM deductibles
                WHERE sponsor_id = ? AND beneficiary_id = ?
            """, (sponsor_id, beneficiary_id))
        deductibles = {code: amount for code, amount in self.cursor.fetchall()}

        self.cursor.execute("""
                SELECT code, count FROM visit_counts
                WHERE sponsor_id = ? AND beneficiary_id = ?
            """, (sponsor_id, beneficiary_id))
        visit_counts = {code: count for code, count in self.cursor.fetchall()}

        return Beneficiary(
            ssn=row["ssn"],
            dob=date.fromisoformat(row["dob"]),
            first_name=row["first_name"],
            middle_name=row["middle_name"],
            last_name=row["last_name"],
            gender=row["gender"],
            phone=row["phone"],
            insurance_company=row["insurance_company"],
            insurance_FID=row["insurance_FID"],
            sponsor_id=row["sponsor_id"],
            beneficiary_id=row["beneficiary_id"],
            relationship=row["relationship"],
            address=address,
            deductibles=deductibles,
            visit_counts=visit_counts
        )

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
