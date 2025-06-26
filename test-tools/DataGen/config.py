from log_config import get_logger
import os
from datetime import datetime
from Repository.NPI_Functions import download_weekly_npi_data

from BellShapes import BellShapes, fit_range_to_half_bel

# Time and File Info
DATE = datetime.now()

EDI834_FILE_NAME = f'834.VFMP.{DATE.year}.{DATE.strftime("%y%m%d")}.{DATE.strftime("%H%M")}.{DATE.strftime("%Y%m%d1")}.edi'
EDI270_FILE_NAME = f'270.VFMP.{DATE.year}.{DATE.strftime("%y%m%d")}.{DATE.strftime("%H%M")}.{DATE.strftime("%Y%m%d1")}.edi'
LOCAL_DATABASE = f"localdb.jsonl"
STATISTICS_MD = f"Statistics_Visualizer.md"

# Paths
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIRECTORY = os.path.join(ROOT_PATH, "Downloads")
LOCAL_DATABASE_DIRECTORY = os.path.join(ROOT_PATH, "Output", "Local_DB")
MARKDOWN_DIRECTORY = os.path.join(ROOT_PATH, "Output")
EDI834_PATH = os.path.join(ROOT_PATH, "Output", "EDI834_Output")
EDI270_PATH = os.path.join(ROOT_PATH, "Output", "EDI270_Output")

os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)
NPI_CSV_PATH = download_weekly_npi_data(DOWNLOAD_DIRECTORY)

logger = get_logger(__name__)


# Creates directory if nonexistent
def get_edi_path(edi_path, edi_file):
    os.makedirs(edi_path, exist_ok=True)
    logger.info(f"Directory exists: {edi_path}")
    return os.path.join(edi_path, edi_file)


def get_local_db_path():
    os.makedirs(LOCAL_DATABASE_DIRECTORY, exist_ok=True)
    logger.info(f"Directory exists: {LOCAL_DATABASE_DIRECTORY}")
    return os.path.join(LOCAL_DATABASE_DIRECTORY, LOCAL_DATABASE)


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
MAX_DEDUCTIBLES = 100_000
MIN_DEDUCTIBLES = 0
MAX_VISITS = 15
MIN_VISITS = 0

N1_SPONSOR_QUALIFIER = "OCC PAYER EDI"
N1_SPONSOR_ID = "841469824"
N1_PAYER_QUALIFIER = "CLAIMS XM"
N1_PAYER_ID = "831002042"

# Test size generator
NUMBER_OF_TESTS = fit_range_to_half_bel(avg=10627, std=13948, min_val=1, max_val=246778, shape=BellShapes.NORMAL)

# Message Error Rate
TOTAL_ERROR_RATE = 0.005  # 0.5%

# Toggle New Line (for edi segments)
TOGGLE_NEW_LINE = True


def number_of_tests(n=None):
    return NUMBER_OF_TESTS if n is None else n


def get_error_rate(n=None):
    return TOTAL_ERROR_RATE if n is None else n


log_data = {
    "num_834": 0,
    "num_270": 0,
    "time_834": 0,
    "time_270": 0,
    "avg_270_per_bene": 0,
    "throughput_834": 0,
    "throughput_270": 0,
    "error_rate_834": 0,
    "error_rate_270": 0,
    "error_ct_834": 0,
    "error_ct_270": 0,
    "family_size": 0,
    "avg_amt_D2": 0,
    "avg_amt_FK": 0,
    "avg_amt_R": 0,
    "avg_amt_C1": 0,
    "avg_amt_P3": 0,
    "avg_amt_B9": 0
}


def create_md():
    if not os.path.exists(MARKDOWN_DIRECTORY):
        os.makedirs(MARKDOWN_DIRECTORY)
    path = os.path.join(MARKDOWN_DIRECTORY, STATISTICS_MD)

    with open(path, "w") as f:
        f.write("# Data Visualizer \n\n")

        f.write("## Transaction Counts\n")
        f.write("```mermaid\n")
        f.write("xychart-beta\n")
        f.write('    title "Number of Messages"\n')
        f.write('    x-axis ["834", "270"]\n')
        f.write('    y-axis "Count" 0 --> {}\n'.format(max(log_data['num_834'], log_data['num_270']) + 100))
        f.write(f'    bar [{log_data["num_834"]}, {log_data["num_270"]}]\n')
        f.write("```\n\n")

