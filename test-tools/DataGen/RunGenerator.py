from datetime import datetime

from src.Config import Config
from src.FileCreation.DataGenerator import SponsorDataGenerator
from src.FileCreation.EDIGenerator import EDI834Generator, EDI270Generator
from src.Config.Config import logger, number_of_tests, get_error_rate
from src.Config.Data_Visualizer import create_md, log_data


def Run834Generator(max_messages=None, error_rate=None):
    # Setup/Initialization
    now = datetime.now()
    max_messages = number_of_tests(max_messages)
    log_data["messages"]["count_834"] = max_messages
    error_rate = get_error_rate(error_rate)
    log_data["errors"]["error_rate_834"] = error_rate

    # Generate Fake Data
    logger.info(f"Generating {max_messages} total members")
    data_creation = SponsorDataGenerator()
    new_sponsors = data_creation.store_sponsor_and_beneficiaries(max_messages)

    logger.info(f"Data loading Initiated")
    data_creation.repo.loadfile()
    logger.info(f"Data Loading took: {datetime.now() - now}")
    logger.info(f"Data generation complete")
    logger.info(f"Data generation took: {datetime.now() - now}")

    # Generate EDI File
    edi_generator = EDI834Generator(max_messages=max_messages, error_rate=error_rate)
    logger.info("Generating EDI file from stored data")
    edi_file = edi_generator.combine_segments(new_sponsors)
    logger.info("EDI file generation complete")
    logger.info(f"File generation took: {datetime.now() - now}")

    # Create Directory/Write to file
    f = open(Config.get_edi_path(Config.EDI834_PATH, Config.EDI834_FILE_NAME), 'w')
    f.writelines(edi_file)
    f.close()

    # Display amount of time it takes to create
    end_time = datetime.now() - now
    log_data["messages"]["time_834"] = end_time.total_seconds()
    logger.info(f"It took {end_time} to generate {max_messages} transactions for the 834 file")


def Run270Generator(max_messages=None, error_rate=None):
    # Setup/Initialization
    now = datetime.now()
    max_messages = number_of_tests(max_messages)
    log_data["messages"]["count_270"] = max_messages
    error_rate = get_error_rate(error_rate)
    log_data["errors"]["error_rate_270"] = error_rate
    provider_csv_path = Config.NPI_CSV_PATH

    # Generate EDI file
    logger.info(f"Generating transactions from NPI data and local database")
    edi270 = EDI270Generator(max_messages=max_messages, provider_csv_path=provider_csv_path, error_rate=error_rate)
    logger.info(f"Generating transactions into EDI file")
    edi_out = edi270.combine_segments()

    f = open(Config.get_edi_path(Config.EDI270_PATH, Config.EDI270_FILE_NAME), 'w')
    f.writelines(edi_out)
    f.close()
    end_time = datetime.now() - now
    log_data["messages"]["time_270"] = end_time.total_seconds()
    logger.info(f"It took {end_time} to generate {max_messages} transactions for the 270 file")


if __name__ == "__main__":
    curr = datetime.now()

    Run834Generator(5, 0)
    Run270Generator(5, 0)
    end = datetime.now() - curr
    logger.info(f"It took {end} to generate the output")

    create_md()
