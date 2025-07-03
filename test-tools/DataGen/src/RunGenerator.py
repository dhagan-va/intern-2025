from datetime import datetime

from Config import Config
from Config.Config import logger, number_of_tests_834, number_of_tests_270, get_error_rate
from Config.Data_Visualizer import log_data, create_md
from FileCreation.DataGenerator import SponsorDataGenerator, generate_claim_transactions
from FileCreation.EDIGenerator import EDI834Generator, EDI270Generator, EDI837PGenerator
from Repository.DatabaseFactory import get_database_backend


def Run834Generator(num_messages=None, error_rate=None):
    # Setup/Initialization
    now = datetime.now()
    num_messages = number_of_tests_834(num_messages)
    log_data["messages"]["count_834"] = num_messages
    error_rate = get_error_rate(error_rate)
    log_data["errors"]["error_rate_834"] = error_rate

    # Generate EDI File
    edi_generator = EDI834Generator(num_messages=num_messages, error_rate=error_rate)
    logger.info("Generating EDI file from stored data")
    edi_file = edi_generator.combine_segments(sponsors)
    logger.info("EDI file generation complete")
    logger.info(f"File generation took: {datetime.now() - now}")

    # Create Directory/Write to file
    with open(Config.get_edi_path(Config.EDI834_PATH, Config.EDI834_FILE_NAME), 'w') as f:
        f.writelines(edi_file)

    # Display amount of time it takes to create
    end_time = datetime.now() - now
    log_data["messages"]["time_834"] = end_time.total_seconds()
    logger.info(f"It took {end_time} to generate {num_messages} transactions for the 834 file")


def Run270Generator(num_messages=None, error_rate=None):
    # Setup/Initialization
    now = datetime.now()
    num_messages = number_of_tests_270(num_messages)
    log_data["messages"]["count_270"] = num_messages
    error_rate = get_error_rate(error_rate)
    log_data["errors"]["error_rate_270"] = error_rate
    provider_csv_path = Config.NPI_CSV_PATH

    # Generate EDI file
    logger.info(f"Generating transactions from NPI data and local database")
    edi = EDI270Generator(num_messages=num_messages, provider_csv_path=provider_csv_path, error_rate=error_rate)
    logger.info(f"Generating transactions into EDI file")
    edi_out = edi.combine_segments()

    with open(Config.get_edi_path(Config.EDI270_PATH, Config.EDI270_FILE_NAME), 'w') as f:
        f.writelines(edi_out)

    end_time = datetime.now() - now
    log_data["messages"]["time_270"] = end_time.total_seconds()
    logger.info(f"It took {end_time} to generate {num_messages} transactions for the 270 file")

    return edi


def Run837PGenerator(beneficiaries, providers, num_messages=None, error_rate=None):
    now = datetime.now()
    num_messages = number_of_tests_270(num_messages)
    log_data["messages"]["count_837"] = num_messages
    error_rate = get_error_rate(error_rate)
    log_data["errors"]["error_rate_837"] = error_rate

    logger.info(f"Generating transactions from saved 837 information")
    edi837 = EDI837PGenerator(beneficiaries=beneficiaries, providers=providers, num_messages=num_messages,
                              error_rate=error_rate)
    logger.info(f"Generating transactions into EDI file")
    edi_out = edi837.combine_segments()

    with open(Config.get_edi_path(Config.EDI837_PATH, Config.EDI837_FILE_NAME), 'w') as f:
        f.writelines(edi_out)

    end_time = datetime.now() - now
    log_data["messages"]["time_837"] = end_time.total_seconds()
    logger.info(f"It took {end_time} to generate {num_messages} transactions for the 837 file")


def GenerateSponsors(num_gen):
    db = get_database_backend()
    data_creation = SponsorDataGenerator()
    current_users = db.total_beneficiaries()

    # want to create at least 100_000 users for db
    if current_users < 100_000:
        num_gen = 100_000 - current_users

    sponsors_created = data_creation.store_sponsor_and_beneficiaries(num_gen)
    return sponsors_created


def CreateDailyClaimDB(num_gen):
    claims = generate_claim_transactions(num_gen)
    return claims


if __name__ == "__main__":
    curr = datetime.now()
    num = 1

    sponsors = GenerateSponsors(num)
    CreateDailyClaimDB(num)

    # edi270 = Run270Generator(num, 0)
    #
    # Run837PGenerator(transaction_store, num, 0)
    #
    # Run834Generator(sponsors, num, 0)

    end = datetime.now() - curr
    logger.info(f"It took {end} to generate the output")

    create_md()
