import os
from FileCreation.DataCreation import Make834Data
from datetime import datetime
import config
from config import get_logger
from FileCreation.EDI_File_Generator import EDI834Generator
from DataLayer.Datatypes import Sponsor

# Setup/Initialization
now = datetime.now()
directory = config.OUTPUT_DIRECTORY_NAME
n = 100_000
logger = get_logger(__name__)

# Generate 834 Data
data_creation = Make834Data()
edi_generator = EDI834Generator()

# Generate Fake Data
logger.info(f"Generating {n} families")
data_creation.create_sponsor_and_beneficiaries(n)
sponsor_data = data_creation.return_generated_data()
logger.info(f"Data generation complete")
logger.info(f"Data generation took: {datetime.now() - now}")

# Store Data to database
logger.info(f"Storing data to database")
data_creation.save_generated_data()
logger.info(f"Data storage complete")
logger.info(f"Data storage took: {datetime.now() - now}")

# Generate EDI File
logger.info("Generating EDI file from stored data")
edi_file = edi_generator.generate_file(Sponsor.from_dict(s) for s in sponsor_data)
logger.info("EDI file generation complete")
logger.info(f"File generation took: {datetime.now() - now}")

# Create Directory/Write to file
if not os.path.exists(config.OUTPUT_DIRECTORY_NAME):
    os.mkdir(config.OUTPUT_DIRECTORY_NAME)
    logger.info(f"Created directory: {config.OUTPUT_DIRECTORY_NAME}")

file_name = f'834.VFMP.{now.year}.{now.strftime("%y%m%d")}.{now.strftime("%H%M")}.{now.strftime("%Y%m%d1")}.edi'
file_path = os.path.join(config.OUTPUT_DIRECTORY_NAME, file_name)
f = open(file_path, 'w')
f.writelines(edi_file)
f.close()

# Display amount of time it takes to create
END_TIME = datetime.now() - now
logger.info(f"It took: {END_TIME}")
