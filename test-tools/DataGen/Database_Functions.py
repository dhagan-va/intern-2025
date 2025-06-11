import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import IndexModel, ASCENDING
from dotenv import load_dotenv
import logging

load_dotenv()

MONGO_URI = os.getenv("MONGO_CONNECTION_STRING")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
logger = logging.getLogger(__name__)

client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
sponsor_db = client[MONGO_DB]
collection = sponsor_db[MONGO_COLLECTION]


def get_collection():
    return collection


def get_common_indexes():
    return [
        IndexModel([("ssn", ASCENDING)], unique=True),
        IndexModel([("dob", ASCENDING)]),
        IndexModel([("first_name", ASCENDING)]),
        IndexModel([("middle_initial", ASCENDING)]),
        IndexModel([("last_name", ASCENDING)]),
        IndexModel([("deductibles.D2", ASCENDING)]),
        IndexModel([("deductibles.FK", ASCENDING)]),
        IndexModel([("deductibles.R", ASCENDING)]),
        IndexModel([("visit_counts.C1", ASCENDING)]),
        IndexModel([("visit_counts.P3", ASCENDING)]),
        IndexModel([("visit_counts.B9", ASCENDING)])
    ]


def initialize_indexes(collection):
    common_indexes = get_common_indexes()

    sponsor_indexes = common_indexes + [
        IndexModel([("sponsor_id", ASCENDING)], unique=True),
        IndexModel([
            ("ssn", ASCENDING),
            ("first_name", ASCENDING),
            ("last_name", ASCENDING),
            ("sponsor_id", ASCENDING)
        ])
    ]