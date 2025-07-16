from Config.Config import DATABASE_BACKEND
from Repository.JSON_Database_Functions import LocalDBFunctions
from Repository.SQLite_Database_Functions import SQLiteDBFunctions


def get_database_backend(file):
    if DATABASE_BACKEND == "sqlite":
        return SQLiteDBFunctions(file=file)
    elif DATABASE_BACKEND == "jsonl":
        return LocalDBFunctions
    else:
        raise ValueError(f"Unsupported database: {DATABASE_BACKEND}")
