import sqlite3

from Config.Config import logger, get_local_db_path, FAMILY_DATABASE_DIRECTORY, FAMILY_DATABASE_SQLITE, NPI_CSV_PATH
from Repository.DatabaseFactory import get_database_backend
from DataLayer.Interfaces import ClaimTransactionAccess
from DataLayer.Datatypes import ClaimTransaction
from Repository.NPI_Functions import NPIFunctions


class SQLite_Transaction_Functions(ClaimTransactionAccess):
    def __init__(self, file=get_local_db_path(FAMILY_DATABASE_DIRECTORY, FAMILY_DATABASE_SQLITE)):
        self.file = file
        self.connect = sqlite3.connect(self.file)
        self.connect.row_factory = sqlite3.Row
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
                provider_entity_type TEXT,
                provider_address_1 TEXT,
                provider_address_2 TEXT,
                provider_city TEXT,
                provider_state TEXT,
                provider_zip TEXT,
                provider_phone TEXT,
                amount REAL,
                payer_claim_id TEXT,
                FOREIGN KEY (sponsor_id, beneficiary_id)
                    REFERENCES beneficiaries(sponsor_id, beneficiary_id)
                )
            """)
        self.connect.commit()

    def save_claim_transaction(self, claim, commit=True):
        logger.debug(f"Saving claim transaction {claim.claim_id}")
        self.cursor.execute("""
            INSERT OR REPLACE INTO claim_transactions (
                claim_id, status, date, service_line_id,
                sponsor_id, beneficiary_id, provider_npi, provider_name,
                provider_entity_type, provider_address_1, provider_address_2, provider_city, provider_state,
                provider_zip, provider_phone, amount, payer_claim_id
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
            logger.info(f"Saving {len(claims)} claim transactions in bulk")
            self.connect.execute("BEGIN TRANSACTION")
            for claim in claims:
                self.save_claim_transaction(claim, commit=False)
            self.connect.commit()
        except Exception as e:
            self.connect.rollback()
            logger.error(f"No claims were saved due to an error: {e}")
            raise e

    def get_claim_transactions(self, status, date):
        logger.info(f"Fetching claim transactions with status={status} and date={date}")
        self.cursor.execute("""
            SELECT * FROM claim_transactions
            WHERE status = ? AND date = ?
        """, (status, date))
        rows = self.cursor.fetchall()
        return [ClaimTransaction.from_dict(dict(row)) for row in rows]

    def update_claims_status(self, claim_ids, new_status):
        logger.info(f"Updating status of {len(claim_ids)} claims to '{new_status}'")
        self.cursor.executemany("""
            UPDATE claim_transactions
            SET status = ?
            WHERE claim_id = ?
        """, [(new_status, cid) for cid in claim_ids])
        self.connect.commit()

    def total_claim_transactions(self):
        self.cursor.execute("SELECT COUNT(*) FROM claim_transactions")
        result = self.cursor.fetchone()
        return result[0] if result else 0
