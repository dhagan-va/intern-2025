import os
import tomli
import logging
from datetime import datetime
from Config.BellShapes import BellShapes, fit_range_to_half_bel
from Repository.NPI_Functions import download_weekly_npi_data

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.toml")
with open(CONFIG_PATH, "rb") as f:
    config = tomli.load(f)

DATE = datetime.now()
YEAR = DATE.year
YMD = DATE.strftime("%y%m%d")
HM = DATE.strftime("%H%M")
YMDHM = DATE.strftime("%Y-%m-%d.%H%M")
SSMMM = DATE.strftime("%S%f")[:6]
FULL_DATE = DATE.strftime("%Y%m%d")

log_config = config.get("logging", {})
log_level = getattr(logging, log_config.get("level", "INFO").upper(), logging.INFO)
log_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
                       log_config.get("directory", "Output/Logs"))
log_filename = log_config.get("filename_template", "TestSuite_{date}.log").format(date=FULL_DATE)

os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=log_level,
    filename=os.path.join(log_dir, log_filename),
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def get_logger(name):
    return logging.getLogger(name)


logger = get_logger(__name__)

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOWNLOAD_DIRECTORY = os.path.join(ROOT_PATH, config["paths"]["download_directory"])

os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)

FAMILY_DATABASE_DIRECTORY = os.path.join(ROOT_PATH, config["paths"]["family_database_directory"])
EDI270_PATH = os.path.join(ROOT_PATH, config["paths"]["edi270_path"])
EDI837_PATH = os.path.join(ROOT_PATH, config["paths"]["edi837_path"])
EDI277CA_PATH = os.path.join(ROOT_PATH, config["paths"]["edi277ca_path"])
EDI835_PATH = os.path.join(ROOT_PATH, config["paths"]["edi835_path"])
EDI834_PATH = os.path.join(ROOT_PATH, config["paths"]["edi834_path"])
EDI999_PATH = os.path.join(ROOT_PATH, config["paths"]["edi999_path"])
NPI_CSV_PATH = download_weekly_npi_data(DOWNLOAD_DIRECTORY)

EDI270_FILE_NAME = config["filenames"]["edi270_file_template"].format(year=YEAR, ymd=YMD, hm=HM, claim_id="{claim_id}", full_date=FULL_DATE)
EDI277CA_FILE_NAME = config["filenames"]["edi277ca_file_template"].format(year=YEAR, ymd=YMD, hm=HM,full_date=FULL_DATE)
EDI837_FILE_NAME = config["filenames"]["edi837_file_template"].format(year=YEAR, ymd=YMD, hm=HM, full_date=FULL_DATE)
EDI835_FILE_NAME = config["filenames"]["edi835_file_template"].format(year=YEAR, ymd=YMD, hm=HM, full_date=FULL_DATE)
EDI834_FILE_NAME = config["filenames"]["edi834_file_template"].format(year=YEAR, ymd=YMD, hm=HM, full_date=FULL_DATE)
EDI999_FILE_NAME = config["filenames"]["edi999_file_template"].format(year=YEAR, ymd=YMD, hm=HM, full_date=FULL_DATE)
STATISTICS_MD = os.path.join(ROOT_PATH, config["filenames"]["statistics_md"])


def get_edi_path(edi_path, edi_file):
    os.makedirs(edi_path, exist_ok=True)
    logger.debug(f"Directory ensured: {edi_path}")
    return os.path.join(edi_path, edi_file)


def get_local_db_path(db_path, db_file):
    os.makedirs(db_path, exist_ok=True)
    logger.debug(f"Directory ensured: {db_path}")
    return os.path.join(db_path, db_file)

# Database/AWS configs
UPLOAD_TO_S3 = config["aws"]["upload_to_s3"]
BUCKET_NAME = config["aws"]["bucket_name"]
DATABASE_BACKEND = config["database"]["backend"]
FAMILY_DATABASE_JSONL = config["database"]["jsonl_path"]
FAMILY_DATABASE_SQLITE = config["database"]["sqlite_path"]

# Adjustable inputs
TOGGLE_NEW_LINE = config["inputs"]["toggle_new_line"]
TOTAL_ERROR_RATE = config["inputs"]["total_error_rate"]
MAX_BENEFICIARIES = config["inputs"]["max_beneficiaries"]
MIN_BENEFICIARIES = config["inputs"]["min_beneficiaries"]
MAX_DEDUCTIBLES = config["inputs"]["max_deductibles"]
MIN_DEDUCTIBLES = config["inputs"]["min_deductibles"]
MAX_VISITS = config["inputs"]["max_visits"]
MIN_VISITS = config["inputs"]["min_visits"]
INITIAL_USERS = config["inputs"]["initial_beneficiaries"]

# Constants
FAKER_SEED = config["seed"]["faker_seed"]
RANDOM_SEED = config["seed"]["random_seed"]
SENDER_ID = config["constants"]["sender_id"]
RECEIVER_ID = config["constants"]["receiver_id"]
SPONSOR_NAME = config["constants"]["sponsor_name"]
SPONSOR_ID = config["constants"]["sponsor_id"]
PAYER_NAME = config["constants"]["payer_name"]
PAYER_ID = config["constants"]["payer_id"]

DATE_TIME_FMT_QUALIFIER = config["constants"]["date_time_fmt_qualifier"]
RELATIONSHIP_MAP = config["relationship_map"]

edi270_fields = config["edi270_fields"]
# edi837_fields = config["edi837_fields"]
# edi277ca_fields = config["edi277ca_fields"]
# edi835_fields = config["edi835_fields"]
# edi834_fields = config["edi834_fields"]
# edi999_fields = config["edi999_fields"]


def get_number_of_tests(section):
    return fit_range_to_half_bel(
        avg=section["avg"],
        std=section["std"],
        min_val=section["min"],
        max_val=section["max"],
        shape=BellShapes[section["shape"]]
    )


NUMBER_OF_TESTS_834 = get_number_of_tests(config["test_size"]["834"])
NUMBER_OF_TESTS_270 = get_number_of_tests(config["test_size"]["270"])


def number_of_tests_834(n=None):
    return NUMBER_OF_TESTS_834 if n is None else n


def number_of_tests_270(n=None):
    return NUMBER_OF_TESTS_270 if n is None else n


def get_error_rate(n=None):
    return TOTAL_ERROR_RATE if n is None else n
