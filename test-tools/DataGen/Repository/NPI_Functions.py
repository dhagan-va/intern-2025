import logging

import requests
import zipfile
import io
import datetime
import pandas as pd

import config
from config import logger
from pathlib import Path
import random


def get_week(date=None):
    if date is None:
        date = datetime.date.today()
    offset = (date.weekday() + 1) % 7
    end = date - datetime.timedelta(days=offset)
    start = end - datetime.timedelta(days=6)
    return start, end


def download_weekly_npi_data(download_path):
    start, end = get_week()
    filename = f"NPPES_Data_Dissemination_{start.strftime('%m%d%y')}_{end.strftime('%m%d%y')}_Weekly.zip"
    csv_pattern = f"npidata_pfile_{start.strftime('%Y%m%d')}-{end.strftime('%Y%m%d')}.csv"
    print(filename)
    print(csv_pattern)

    zip_path = Path(download_path) / filename
    csv_path = Path(download_path) / csv_pattern

    if csv_path.exists():
        logger.info(f"CSV already exists: {csv_path}")
        return csv_path

    url = f"https://download.cms.gov/nppes/{filename}"
    logger.info(f"Attempting to download: {url}")

    try:
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to download file. Status: {response.status_code}")
            return None

        with open(zip_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"Downloaded and saved: {zip_path}")

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for file in z.namelist():
                if "npidata_pfile" in file and file.endswith(".csv"):
                    z.extract(file, path=download_path)
                    extracted_csv = Path(download_path) / file
                    extracted_csv.rename(csv_path)
                    logger.info(f"Extracted and renamed CSV: {csv_path}")
                    return csv_path

        logger.error("CSV not found in Zip.")
        return None

    except Exception as e:
        logging.error(f"Error during download/extraction: {e}")
        return None


if __name__ == "__main__":
    csv_file = download_weekly_npi_data(config.DOWNLOAD_DIRECTORY)
