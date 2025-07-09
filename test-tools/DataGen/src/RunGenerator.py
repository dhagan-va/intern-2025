from datetime import datetime, date, timedelta

import boto3

from dotenv import load_dotenv
from Config import Config
from Config.Config import logger, number_of_tests_834, number_of_tests_270, get_error_rate
from Config.Data_Visualizer import log_data, create_md
from FileCreation.DataGenerator import SponsorDataGenerator, generate_claim_transactions
from FileCreation.EDIGenerator import EDI834Generator, EDI270Generator, EDI837PGenerator, EDI277CAGenerator
from Repository.DatabaseFactory import get_database_backend
from Repository.Transaction_Storage_Functions import TransactionFunctions

load_dotenv()

transaction_funcs = TransactionFunctions()


def upload_to_s3(file_path, bucket_name, s3_key):
    s3 = boto3.client("s3")
    try:
        with open(file_path, "rb") as f:
            s3.put_object(Bucket=bucket_name, Key=s3_key, Body=f)
        logger.info(f"Uploaded to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        logger.error(f"Failed to upload to s3: {e}")


def Run270Generator(num_messages=None, error_rate=None, upload_s3=False):
    # Setup/Initialization
    now = datetime.now()
    num_messages = number_of_tests_270(num_messages)
    log_data["messages"]["count_270"] = num_messages
    error_rate = get_error_rate(error_rate)
    log_data["errors"]["error_rate_270"] = error_rate

    # Generate EDI file
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
    # log_data["errors"]["error_rate_837"] = error_rate

    logger.info(f"Generating transactions from saved 277CA information")
    edi277CA = EDI277CAGenerator(transaction_funcs=transaction_funcs, error_rate=error_rate)
    # log_data["messages"]["count_837"] = edi837.get_num_messages()
    logger.info(f"Generating transactions into EDI file")
    edi_out = edi277CA.combine_segments()

    with open(Config.get_edi_path(Config.EDI277CA_PATH, Config.EDI277CA_FILE_NAME), 'w') as f:
        f.writelines(edi_out)

    end_time = datetime.now() - now
    # log_data["messages"]["time_837"] = end_time.total_seconds()
    logger.info(f"It took {end_time} to generate {edi277CA.get_num_messages()} transactions for the 277CA file")


def Run834Generator(error_rate=None):
    # Setup/Initialization
    now = datetime.now()
    error_rate = get_error_rate(error_rate)
    log_data["errors"]["error_rate_834"] = error_rate

    # Generate EDI File
    edi834 = EDI834Generator(transaction_funcs=transaction_funcs, error_rate=error_rate)
    log_data["messages"]["count_837"] = edi834.get_num_messages()
    logger.info("Generating EDI file from stored data")
    edi_out = edi834.combine_segments()
    logger.info("EDI file generation complete")
    logger.info(f"File generation took: {datetime.now() - now}")

    # Create Directory/Write to file
    with open(Config.get_edi_path(Config.EDI834_PATH, Config.EDI834_FILE_NAME), 'w') as f:
        f.writelines(edi_out)

    # Display amount of time it takes to create
    end_time = datetime.now() - now
    log_data["messages"]["time_834"] = end_time.total_seconds()
    logger.info(f"It took {end_time} to generate {edi834.get_num_messages()} transactions for the 834 file")


def GenerateSponsors(num_gen):
    now = datetime.now()

    db = get_database_backend()
    data_creation = SponsorDataGenerator()
    current_users = db.total_beneficiaries()

    # want to create at least 100_000 users for db
    if current_users < 1000:
        num_gen = 1000 - current_users

    sponsors_created = data_creation.store_sponsor_and_beneficiaries(num_gen)

    end_time = datetime.now() - now
    logger.info(f"It took {end_time} to generate {num_gen} sponsors")

    return sponsors_created


def CreateClaimDB(num_gen, input_date=date.today(), status="Created"):
    now = datetime.now()

    claims = generate_claim_transactions(num_gen, transaction_funcs=transaction_funcs, input_date=input_date,
                                         status=status)

    end_time = datetime.now() - now
    logger.info(f"It took {end_time} to generate {num_gen} claims for status {status}")
    return claims


if __name__ == "__main__":
    curr = datetime.now()
    num = 100

    yesterday = date.today() - timedelta(days=1)
    week_before = date.today() - timedelta(days=7)

    sponsors = GenerateSponsors(num)
    CreateClaimDB(num, date.today(), "Created")
    CreateClaimDB(num, yesterday, "270 Created")
    CreateClaimDB(num, week_before, "837 Created")

    Run270Generator(num, 0.05, upload_s3=Config.UPLOAD_TO_S3)
    Run837PGenerator(0)
    Run277CAGenerator(0)
    # Run834Generator(0)

    end = datetime.now() - curr
    logger.info(f"It took {end} to generate the output")

    transaction_funcs.connect.close()
    create_md()
