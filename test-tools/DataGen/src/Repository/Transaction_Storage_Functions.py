import sqlite3

from Config.Config import logger, get_local_db_path,FAMILY_DATABASE_DIRECTORY, FAMILY_DATABASE_SQLITE, NPI_CSV_PATH
from Repository.DatabaseFactory import get_database_backend
from Repository.NPI_Functions import NPIFunctions


class TransactionFunctions:
    def __init__(self, file=get_local_db_path(FAMILY_DATABASE_DIRECTORY, FAMILY_DATABASE_SQLITE)):
        self.file = file
        self.connect = sqlite3.connect(self.file)
        self.cursor = self.connect.cursor()
        self.init_tables()
        self.family_db = get_database_backend()
        self.npi_funcs = NPIFunctions(NPI_CSV_PATH)

    def init_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS claim_transactions (
                claim_id TEXT PRIMARY KEY,
                status TEXT,
                date TEXT,
                service_line_id TEXT,
                sponsor_id TEXT,
                beneficiary_id TEXT,
                provider_npi TEXT,
                provider_name TEXT,
                entity_type TEXT,
                address_line_1 TEXT,
                address_line_2 TEXT,
                city TEXT,
                state TEXT,
                zipcode TEXT,
                phone TEXT,
                amount REAL,
                payer_claim_id TEXT,
                FOREIGN KEY (sponsor_id, beneficiary_id)
                    REFERENCES beneficiaries(sponsor_id, beneficiary_id)
                )
            """)
        self.connect.commit()

    def save_claim_transaction(self, claim, commit=True):
        self.cursor.execute("""
            INSERT OR REPLACE INTO claim_transactions (
                claim_id, status, date, service_line_id,
                sponsor_id, beneficiary_id, provider_npi, provider_name,
                entity_type, address_line_1, address_line_2, city, state,
                zipcode, phone, amount, payer_claim_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            claim.claim_id,
            claim.status,
            claim.date.isoformat(),
            claim.service_line_id,
            claim.sponsor_id,
            claim.beneficiary_id,
            claim.provider_npi,
            claim.provider_name,
            claim.provider_entity_type,
            claim.provider_address_1,
            claim.provider_address_2,
            claim.provider_city,
            claim.provider_state,
            claim.provider_zip,
            claim.provider_phone,
            claim.amount,
            claim.payer_claim_id
        ))

        if commit:
            self.connect.commit()

    def save_many_claims(self, claims):
        try:
            self.connect.execute("BEGIN TRANSACTION")
            for claim in claims:
                self.save_claim_transaction(claim, commit=False)
            self.connect.commit()
        except Exception as e:
            self.connect.rollback()
            logger.error(f"No sponsors were saved due to an error: {e}")
            raise e
