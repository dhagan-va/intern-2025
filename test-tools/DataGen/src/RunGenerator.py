import argparse
from datetime import datetime, date, timedelta

import boto3
from dotenv import load_dotenv

from Config import Config
from Config.Config import logger, number_of_tests_270, get_error_rate
from Config.Data_Visualizer import log_data, create_md
from FileCreation.DataGenerator import SponsorDataGenerator, generate_claim_transactions
from FileCreation.EDIGenerator import EDI834Generator, EDI270Generator, EDI837PGenerator, EDI277CAGenerator, \
    EDI835Generator
from Repository.DatabaseFactory import get_database_backend

load_dotenv()

transaction_funcs = get_database_backend()

status_map = {
    "270": ("Created", date.today()),
    "837": ("270 Created", date.today() - timedelta(days=1)),
    "277": ("837 Created", date.today() - timedelta(days=1)),
    "835": ("277CA Created", date.today() - timedelta(days=8)),
    "834": ("835 Created", date.today() - timedelta(days=8)),
}


def upload_to_s3(file_path, bucket_name, s3_key):
    s3 = boto3.client("s3")
    try:
        with open(file_path, "rb") as f:
            s3.put_object(Bucket=bucket_name, Key=s3_key, Body=f)
        logger.info(f"Uploaded to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        logger.error(f"Failed to upload to s3: {e}")


def create_claims(num_gen=number_of_tests_270(), input_date=date.today(), status="Created"):
    return generate_claim_transactions(num_gen, transaction_funcs=transaction_funcs, input_date=input_date,
                                       status=status)


def ensure_sponsors():
    db = get_database_backend()
    if db.total_beneficiaries() == 0:
        logger.info(f"No sponsors found -- generating {Config.INITIAL_USERS} sponsors first...")
        SponsorDataGenerator().store_sponsor_and_beneficiaries(Config.INITIAL_USERS)


def cli_mode(file_type, num, error_rate, upload_s3):
    if file_type not in status_map:
        logger.error("Invalid file type.")
        return

    ensure_sponsors()
    status, date_used = status_map[file_type]
    create_claims(num, date_used, status)

    if file_type == "270":
        Run270Generator(num, error_rate, upload_s3)
    elif file_type == "837":
        Run837PGenerator(error_rate)
    elif file_type == "277":
        Run277CAGenerator(error_rate)
    elif file_type == "835":
        Run835Generator(error_rate)
    elif file_type == "834":
        Run834Generator(error_rate)


def auto_mode():
    logger.info("Running automated daily generation...")

    ensure_sponsors()

    today = date.today()
    error_rate = get_error_rate()
    num_messages = number_of_tests_270()

    if transaction_funcs.total_claim_transactions() == 0:
        logger.info("No transactions found for today -- running initialization...")
        for delta in range(8, -1, -1):
            transaction_date = date.today() - timedelta(days=delta)
            num_messages = number_of_tests_270()

            logger.info(
                f"Creating {num_messages} claims for {transaction_date.isoformat()} with error rate {error_rate:.2%}")
            create_claims(num_messages, transaction_date, "Created")
            create_claims(num_messages, transaction_date - timedelta(days=1), "270 Created")
            create_claims(num_messages, transaction_date - timedelta(days=8), "277CA Created")

    # Daily run — only create 270 if not yet created today
    existing = transaction_funcs.get_claim_transactions(status="Created", date=today.isoformat())
    if not existing:
        logger.info(f"Creating today's 270 claims...")
        create_claims(num_messages, today, "Created")

    Run270Generator(num_messages, error_rate, Config.UPLOAD_TO_S3)
    Run837PGenerator(error_rate)
    Run277CAGenerator(error_rate)
    Run835Generator(error_rate)
    Run834Generator(error_rate)


def Run270Generator(num_messages=None, error_rate=None, upload_s3=False):
    now = datetime.now()
    log_data["messages"]["count_270"] = num_messages
    error_rate = get_error_rate(error_rate)
    log_data["errors"]["error_rate_270"] = error_rate

    logger.info(f"Generating transactions from NPI data and local database")
    edi = EDI270Generator(transaction_funcs=transaction_funcs, error_rate=error_rate)
    logger.info(f"Generating transactions into EDI file")
    edi_out = edi.combine_segments()

    file_path = Config.get_edi_path(Config.EDI270_PATH, Config.EDI270_FILE_NAME)
    with open(file_path, 'w') as f:
        f.writelines(edi_out)

    end_time = datetime.now() - now
    log_data["messages"]["time_270"] = end_time.total_seconds()
    logger.info(f"It took {end_time} to generate {num_messages} transactions for the 270 file")

    if upload_s3:
        file_name = Config.EDI270_FILE_NAME
        s3_key = f"270/{file_name}"
        upload_to_s3(file_path, Config.BUCKET_NAME, s3_key)


def Run837PGenerator(error_rate=None):
    now = datetime.now()
    error_rate = get_error_rate(error_rate)
    log_data["errors"]["error_rate_837"] = error_rate

    logger.info(f"Generating transactions from saved 837 information")
    edi837 = EDI837PGenerator(transaction_funcs=transaction_funcs, error_rate=error_rate)
    log_data["messages"]["count_837"] = edi837.get_num_messages()
    logger.info(f"Generating transactions into EDI file")
    edi_out = edi837.combine_segments()

    with open(Config.get_edi_path(Config.EDI837_PATH, Config.EDI837_FILE_NAME), 'w') as f:
        f.writelines(edi_out)

    end_time = datetime.now() - now
    log_data["messages"]["time_837"] = end_time.total_seconds()
    logger.info(f"It took {end_time} to generate {edi837.get_num_messages()} transactions for the 837 file")


def Run277CAGenerator(error_rate=None):
    now = datetime.now()
    error_rate = get_error_rate(error_rate)
    log_data["errors"]["error_rate_277CA"] = error_rate

    logger.info(f"Generating transactions from saved 277CA information")
    edi277CA = EDI277CAGenerator(transaction_funcs=transaction_funcs, error_rate=error_rate)
    log_data["messages"]["count_277CA"] = edi277CA.get_num_messages()
    logger.info(f"Generating transactions into EDI file")
    edi_out = edi277CA.combine_segments()

    with open(Config.get_edi_path(Config.EDI277CA_PATH, Config.EDI277CA_FILE_NAME), 'w') as f:
        f.writelines(edi_out)

    end_time = datetime.now() - now
    log_data["messages"]["time_277CA"] = end_time.total_seconds()
    logger.info(f"It took {end_time} to generate {edi277CA.get_num_messages()} transactions for the 277CA file")


def Run835Generator(error_rate=None):
    now = datetime.now()
    error_rate = get_error_rate(error_rate)
    log_data["errors"]["error_rate_835"] = error_rate

    logger.info(f"Generating transactions from saved 835 information")
    edi835 = EDI835Generator(transaction_funcs=transaction_funcs, error_rate=error_rate)
    log_data["messages"]["count_835"] = edi835.get_num_messages()
    logger.info(f"Generating transactions into EDI file")
    edi_out = edi835.combine_segments()

    with open(Config.get_edi_path(Config.EDI835_PATH, Config.EDI835_FILE_NAME), 'w') as f:
        f.writelines(edi_out)

    end_time = datetime.now() - now
    log_data["messages"]["time_835"] = end_time.total_seconds()
    logger.info(f"It took {end_time} to generate {edi835.get_num_messages()} transactions for the 835 file")


def Run834Generator(error_rate=None):
    now = datetime.now()
    error_rate = get_error_rate(error_rate)
    log_data["errors"]["error_rate_834"] = error_rate

    edi834 = EDI834Generator(transaction_funcs=transaction_funcs, error_rate=error_rate)
    log_data["messages"]["count_834"] = edi834.get_num_messages()
    logger.info("Generating EDI file from stored data")
    edi_out = edi834.combine_segments()
    logger.info("EDI file generation complete")

    with open(Config.get_edi_path(Config.EDI834_PATH, Config.EDI834_FILE_NAME), 'w') as f:
        f.writelines(edi_out)

    end_time = datetime.now() - now
    log_data["messages"]["time_834"] = end_time.total_seconds()
    logger.info(f"It took {end_time} to generate {edi834.get_num_messages()} transactions for the 834 file")


def main():
    parser = argparse.ArgumentParser(
        description="""
            EDI Transaction Generator
            --------------------------
            This tool supports both automated and manual generation of EDI files including:
            270 (Eligibility), 837P (Claim), 277CA (Acknowledgment), 835 (Remittance), 834 (Enrollment Update).

            Modes:
            - auto: Generate and run all files for the current day, including initialization if empty.
            - cli: Manually generate a specific file with custom settings.

            Example Usage:
            python RunGenerator.py auto
            python RunGenerator.py cli 270 -n 500 -e 0.05 --upload_s3
            python RunGenerator.py cli 835 -n 500 -e 0.01
            """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="mode", help="Choose between automated or manual mode.")

    cli_parser = subparsers.add_parser("cli", help="Manually generate a specific EDI file.")
    cli_parser.add_argument(
        "file_type", type=str, choices=["270", "837", "277", "835", "834"],
        help="EDI file type to generate. Choices: 270, 837, 277, 835, 834"
    )
    cli_parser.add_argument(
        "-n", "--num", type=int, required=True,
        help="Number of transactions to generate (e.g., 500)"
    )
    cli_parser.add_argument(
        "-e", "--error_rate", type=float, required=True,
        help="Error rate for injected errors (e.g., 0.05 for 5%)"
    )
    cli_parser.add_argument(
        "--upload_s3", action="store_true",
        help="Upload to AWS S3 bucket after generation (only applies to 270)"
    )

    subparsers.add_parser("auto", help="Automatically generate all EDI files for the current day.")

    args = parser.parse_args()

    if args.mode == "cli":
        cli_mode(args.file_type, args.num, args.error_rate, args.upload_s3)
    elif args.mode == "auto":
        auto_mode()
    else:
        parser.print_help()

    transaction_funcs.connect.close()
    create_md()


if __name__ == "__main__":
    main()
