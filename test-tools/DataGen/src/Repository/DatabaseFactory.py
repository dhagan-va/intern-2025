from Config.Config import DATABASE_BACKEND
from Repository.JSON_Database_Functions import LocalDBFunctions
from Repository.SQLite_Database_Functions import SQLiteDBFunctions
from Repository.SQLite_Transaction_Functions import SQLite_Transaction_Functions


def get_database_backend():
    if DATABASE_BACKEND == "sqlite":
        return SQLiteDBFunctions()
    elif DATABASE_BACKEND == "jsonl":
        return LocalDBFunctions
    else:
        raise ValueError(f"Unsupported database: {DATABASE_BACKEND}")


def get_claim_transaction_backend():
    if DATABASE_BACKEND == "sqlite":
        return SQLite_Transaction_Functions()
    else:
        raise ValueError(f"Unsupported database: {DATABASE_BACKEND}")
