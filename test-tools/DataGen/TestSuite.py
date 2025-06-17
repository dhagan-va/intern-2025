from datetime import datetime

import config
from DataLayer.Datatypes import Sponsor
from FileCreation.DataCreation import Make834Data
from FileCreation.EDI_File_Generator import EDI834Generator
from config import get_logger, number_of_tests


def run_test_suite(n=None):
    # Setup/Initialization
    now = datetime.now()
    n = number_of_tests(n)
    logger = get_logger(__name__)

    # Generate 834 Data
    data_creation = Make834Data()
    edi_generator = EDI834Generator()

    # Generate Fake Data
    logger.info(f"Generating {n} families")
    new_sponsors = data_creation.create_sponsor_and_beneficiaries(n)
    logger.info(f"Data loading Initiated")
    data_creation.repo.loadfile()
    logger.info(f"Data Loading took: {datetime.now() - now}")
    logger.info(f"Data generation complete")
    logger.info(f"Data generation took: {datetime.now() - now}")

    # Generate EDI File
    logger.info("Generating EDI file from stored data")
    edi_file = edi_generator.combine_segments(new_sponsors)
    logger.info("EDI file generation complete")
    logger.info(f"File generation took: {datetime.now() - now}")

    # Create Directory/Write to file
    f = open(config.get_edi_path(), 'w')
    f.writelines(edi_file)
    f.close()

    # Display amount of time it takes to create
    end_time = datetime.now() - now
    logger.info(f"It took: {end_time}")
