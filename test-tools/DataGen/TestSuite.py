import os
from FileCreation.DataCreation import Make834Data
from datetime import datetime
import config
from config import get_logger
from FileCreation.EDI_File_Generator import EDI834Generator

# Setup/Initialization
now = datetime.now()
directory = config.DIRECTORY_NAME
n = 100
logger = get_logger(__name__)

# Generate 834 Data
data_creation = Make834Data()
edi_generator = EDI834Generator()

# Generate Fake Data
logger.info(f"Generating {n} families")
sponsor_data = [data_creation.create_sponsor_and_beneficiaries() for _ in range(n)]
logger.info(f"Data generation complete")
logger.info(f"Data generation took: {datetime.now() - now}")

# Generate EDI File
logger.info("Generating EDI file from stored data")
edi_file = edi_generator.generate_file(sponsor_data)
logger.info("EDI file generation complete")
logger.info(f"File generation took: {datetime.now() - now}")

# Create Directory/Write to file
if not os.path.exists(config.DIRECTORY_NAME):
    os.mkdir(config.DIRECTORY_NAME)
    logger.info(f"Created directory: {config.DIRECTORY_NAME}")

file_name = f"834.VFMP.{now.year}.{now.strftime("%y%m%d")}.{now.strftime("%H%M")}.{now.strftime("%Y%m%d1")}.edi"
file_path = os.path.join(config.DIRECTORY_NAME, file_name)
f = open(file_path, 'w')
f.writelines(edi_file)
f.close()

# Display amount of time it takes to create
END_TIME = datetime.now() - now
logger.info(f"It took: {END_TIME}")
