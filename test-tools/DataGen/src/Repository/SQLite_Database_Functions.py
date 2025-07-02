import sqlite3
import os
from Config.Config import get_local_db_path, FAMILY_DATABASE_DIRECTORY, FAMILY_DATABASE_SQLITE
from DataLayer.Interfaces import DataAccess


class SQLiteDBFunctions:
    def __init__(self, file=get_local_db_path(FAMILY_DATABASE_DIRECTORY, FAMILY_DATABASE_SQLITE)):
        self.file = file
        self.connect = sqlite3.connect(self.file)
        self.cursor = self.connect.cursor()
        self.init_tables()

    def init_tables(self):
        self.cursor.execute(

        )
