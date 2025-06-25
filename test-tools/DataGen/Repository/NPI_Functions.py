import requests
import zipfile
import io
import datetime
import pandas as pd

from log_config import get_logger
from pathlib import Path

logger = get_logger(__name__)


def get_week(date=None):
    if date is None:
        date = datetime.date.today()
    offset = (date.weekday() + 1) % 7
    end = date - datetime.timedelta(days=offset)
    start = end - datetime.timedelta(days=6)
    return start, end


def download_weekly_npi_data(download_path):
    now = datetime.datetime.now()
    start, end = get_week()
    filename = f"NPPES_Data_Dissemination_{start.strftime('%m%d%y')}_{end.strftime('%m%d%y')}_Weekly.zip"
    csv_pattern = f"npidata_pfile_{start.strftime('%Y%m%d')}-{end.strftime('%Y%m%d')}.csv"

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
            msg = f"Failed to download file. Status: {response.status_code}"
            logger.error(msg)
            raise RuntimeError(msg)

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
                    logger.info(f"Extracting {filename} from zip took: {datetime.datetime.now() - now}")
                    return csv_path

        msg = "CSV not found in Zip."
        logger.error(msg)
        raise FileNotFoundError(msg)

    except Exception as e:
        logger.error(f"Error during download/extraction: {e}")
        raise


class NPIFunctions:
    def __init__(self, csv_path):
        self.csv_path = Path(csv_path)
        self.df = None

    def load_csv(self):
        if self.df is not None:
            return self.df

        logger.info(f"Loading provider CSV from: {self.csv_path}")
        try:
            self.df = pd.read_csv(
                self.csv_path,
                usecols=[
                    "NPI",
                    "Provider Organization Name (Legal Business Name)",
                    "Provider Last Name (Legal Name)",
                    "Provider First Name",
                    "Provider Business Mailing Address State Name"
                ],
                dtype=str,
                low_memory=False
            )
        except Exception as e:
            logger.error(f"Error reading CSV: {e}")
            raise

        return self.df

    def get_random_provider(self, state):
        org_col = "Provider Organization Name (Legal Business Name)"
        last_col = "Provider Last Name (Legal Name)"
        state_col = "Provider Business Mailing Address State Name"
        if not state:
            msg = "State must be provided to select provider"
            logger.error(msg)
            raise ValueError(msg)

        df = self.load_csv()

        df_filtered = df[
            (df[org_col].notna() | df[last_col]) &
            (df[state_col] == state.upper()) &
            (df[org_col].isna() | (df[org_col].str.len() <= 60))
            ]

        if df_filtered.empty:
            msg = f"Ermtosis, that's not supposed to happen, no provider is found in {state}"
            logger.error(msg)
            raise LookupError(msg)

        provider = df_filtered.sample(n=1).iloc[0]

        if pd.notna(provider[org_col]):
            name = provider[org_col]
            entity_type = "2"
        else:
            name = f"{provider[last_col]}, {provider['Provider First Name']}"
            entity_type = "1"

        return {
            "npi": provider["NPI"],
            "name": name,
            "entity_type": entity_type,
            "state": provider[state_col]
        }

