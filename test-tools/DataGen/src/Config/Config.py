from Config.Log_Config import get_logger
import os
from datetime import datetime
from Repository.NPI_Functions import download_weekly_npi_data

from Config.BellShapes import BellShapes, fit_range_to_half_bel

# Time and File Info
DATE = datetime.now()

EDI834_FILE_NAME = f'834.VFMP.{DATE.year}.{DATE.strftime("%y%m%d")}.{DATE.strftime("%H%M")}.{DATE.strftime("%Y%m%d1")}.edi'
EDI270_FILE_NAME = f'270.VFMP.{DATE.year}.{DATE.strftime("%y%m%d")}.{DATE.strftime("%H%M")}.{DATE.strftime("%Y%m%d1")}.edi'
EDI837_FILE_NAME = f'837.VFMP.{DATE.year}.{DATE.strftime("%y%m%d")}.{DATE.strftime("%H%M")}.{DATE.strftime("%Y%m%d1")}.edi'

FAMILY_DATABASE_JSONL = "localdb.jsonl"
FAMILY_DATABASE_SQLITE = "localdb.sqlite"
TRANSACTIONS_DATABASE = "transactions.sqlite"

STATISTICS_MD = f"Statistics_Visualizer.md"

# Database selection: "jsonl", "sqlite"
DATABASE_BACKEND = os.getenv("DATABASE_BACKEND", "sqlite")

# Paths
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DOWNLOAD_DIRECTORY = os.path.join(ROOT_PATH, "Downloads")
FAMILY_DATABASE_DIRECTORY = os.path.join(ROOT_PATH, "Output", "Local_DB")
TRANSACTIONS_DATABASE_DIRECTORY = os.path.join(ROOT_PATH, "Output", "Transactions_DB")

MARKDOWN_DIRECTORY = os.path.join(ROOT_PATH)

EDI834_PATH = os.path.join(ROOT_PATH, "Output", "EDI834_Output")
EDI270_PATH = os.path.join(ROOT_PATH, "Output", "EDI270_Output")
EDI837_PATH = os.path.join(ROOT_PATH, "Output", "EDI837_Output")

os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)
NPI_CSV_PATH = download_weekly_npi_data(DOWNLOAD_DIRECTORY)

logger = get_logger(__name__)


# Creates directory if nonexistent
def get_edi_path(edi_path, edi_file):
    os.makedirs(edi_path, exist_ok=True)
    logger.info(f"Directory exists: {edi_path}")
    return os.path.join(edi_path, edi_file)


def get_local_db_path(db_path, db_file):
    os.makedirs(db_path, exist_ok=True)
    logger.info(f"Directory exists: {db_path}")
    return os.path.join(db_path, db_file)


# Constants and config
FAKER_SEED = 49245
RANDOM_SEED = 3
logger.info(f"Using RANDOM_SEED={RANDOM_SEED}, FAKER_SEED={FAKER_SEED}")

# 834 Constants
SENDER_ID = "83-1002022"
RECEIVER_ID = "841439824"

# Database user limit
USER_LIMIT = 500_000

RELATIONSHIP_MAP = {
    'Spouse': '01',
    'Child': '19',
    'Caregiver': '26',
    'Ex-Spouse': '25'
}

MAX_BENEFICIARIES = 4
MIN_BENEFICIARIES = 1
MAX_DEDUCTIBLES = 100_000.00
MIN_DEDUCTIBLES = 0.00
MAX_VISITS = 15
MIN_VISITS = 0

N1_SPONSOR_QUALIFIER = "OCC PAYER EDI"
N1_SPONSOR_ID = "841469824"
N1_PAYER_QUALIFIER = "CLAIMS XM"
N1_PAYER_ID = "831002042"

# Test size generator
NUMBER_OF_TESTS_834 = fit_range_to_half_bel(avg=10627, std=13948, min_val=1, max_val=246778, shape=BellShapes.NORMAL)
NUMBER_OF_TESTS_270 = fit_range_to_half_bel(avg=15000, std=5000, min_val=1, max_val=75000, shape=BellShapes.NORMAL)

# Message Error Rate
TOTAL_ERROR_RATE = 0.005  # 0.5%

# Toggle New Line (for edi segments)
TOGGLE_NEW_LINE = True


def number_of_tests_834(n=None):
    return NUMBER_OF_TESTS_834 if n is None else n


def number_of_tests_270(n=None):
    return NUMBER_OF_TESTS_270 if n is None else n


def get_error_rate(n=None):
    return TOTAL_ERROR_RATE if n is None else n
