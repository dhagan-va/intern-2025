import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import IndexModel, ASCENDING
from dotenv import load_dotenv
import logging

load_dotenv()

MONGO_URI = os.getenv("MONGO_CONNECTION_STRING")
MONGO_SPONSOR_DB = os.getenv("MONGO_SPONSOR_DB")
MONGO_BENEFICIARY_DB = os.getenv("MONGO_BENEFICIARY_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "Test")
logger = logging.getLogger(__name__)

client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
sponsor_db = client[MONGO_SPONSOR_DB]
beneficiary_db = client[MONGO_BENEFICIARY_DB]
sponsor_collection = sponsor_db[MONGO_COLLECTION]
beneficiary_collection = beneficiary_db[MONGO_COLLECTION]


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


def initialize_indexes(sponsor_collection, beneficiary_collection):
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

    beneficiary_indexes = common_indexes + [
        IndexModel([("sponsor_id", ASCENDING)]),
        IndexModel([("beneficiary_id", ASCENDING)], unique=True)
    ]

    sponsor_collection.create_indexes(sponsor_indexes)
    logging.info("Initialized Sponsor Indexes")

    beneficiary_collection.create_indexes(beneficiary_indexes)
    logging.info("Initialized Beneficiary Indexes")


def is_duplicate_ssn(ssn, sponsor_collection, beneficiary_collection):
    sponsor_exists = sponsor_collection.find_one({"ssn":ssn}) is not None
    beneficiary_exists = beneficiary_collection.find_one({"ssn": ssn}) is not None
    return sponsor_exists or beneficiary_exists
