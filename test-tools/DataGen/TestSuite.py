import os
from datetime import datetime

import config
from DataLayer.Datatypes import Sponsor
from FileCreation.DataCreation import Make834Data
from FileCreation.EDI_File_Generator import EDI834Generator
from config import get_logger

# Setup/Initialization
now = datetime.now()
directory = config.OUTPUT_DIRECTORY_NAME
n = 100
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
sponsor_data = [s.to_dict() for s in new_sponsors]
logger.info(f"Data generation complete")
logger.info(f"Data generation took: {datetime.now() - now}")

# Generate EDI File
logger.info("Generating EDI file from stored data")
edi_file = edi_generator.combine_segments(Sponsor.from_dict(s) for s in sponsor_data)
logger.info("EDI file generation complete")
logger.info(f"File generation took: {datetime.now() - now}")

# Create Directory/Write to file
if not os.path.exists(config.OUTPUT_DIRECTORY_NAME):
    os.mkdir(config.OUTPUT_DIRECTORY_NAME)
    logger.info(f"Created directory: {config.OUTPUT_DIRECTORY_NAME}")

file_name = config.TEST_FILE_NAME
file_path = os.path.join(config.OUTPUT_DIRECTORY_NAME, config.TEST_FILE_NAME)
f = open(file_path, 'w')
f.writelines(edi_file)
f.close()

# Display amount of time it takes to create
END_TIME = datetime.now() - now
logger.info(f"It took: {END_TIME}")
