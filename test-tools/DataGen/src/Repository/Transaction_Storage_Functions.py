import os
import json

from DataLayer.Datatypes import ClaimTransaction
from Config.Config import logger, get_local_db_path, TRANSACTIONS_DATABASE_DIRECTORY, TRANSACTIONS_DATABASE


class TransactionFunctions:
    def __init__(self):
        self.path = get_local_db_path(TRANSACTIONS_DATABASE_DIRECTORY, TRANSACTIONS_DATABASE)
        os.makedirs(self.path, exist_ok=True)
        self.transactions = []

    def load_transaction_db(self, file_name):
        self.transactions = []
        with open(file_name, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    self.transactions.append(ClaimTransaction(**data))

    def save_transaction(self, transaction):
        with open(self.path, "a") as f:
            json.dump(transaction.to_dict(), f)
            f.write("\n")
        self.transactions.append(transaction)

    def get_transactions(self):
        return self.transactions

    def reset_transactions(self):
        self.transactions = []

    def get_transaction_by_id(self, claim_id):
        for tx in self.transactions:
            if tx.claim_id == claim_id:
                return tx
        return None
