import random
import uuid
from pathlib import Path

import pandas as pd
from faker import Faker

from Config import Config
from Config.Config import logger
from Config.Data_Visualizer import log_data
from DataLayer.Datatypes import Address, Sponsor, Beneficiary, ClaimTransaction


def generate_claim_transactions(num_gen, transaction_funcs, input_date, status):
    sponsor_generator = SponsorDataGenerator(transaction_funcs)
    sponsor_generator.store_sponsor_and_beneficiaries(total=0)

    csv_beneficiaries = transaction_funcs.get_beneficiaries_by_creation("CSV", num_gen)

    num_random_needed = num_gen - len(csv_beneficiaries)

    beneficiaries = csv_beneficiaries
    if num_random_needed > 0:
        logger.info(
            f"There were {len(csv_beneficiaries)} CSV beneficiaries, generating {num_random_needed} random beneficiaries.")
        random_beneficiaries = transaction_funcs.get_random_beneficiary(num_random_needed)
        beneficiaries.extend(random_beneficiaries)

    transactions = []

    for bene in beneficiaries:
        sponsor_id = bene.sponsor_id
        provider = transaction_funcs.npi_funcs.get_random_provider(bene.address.state)

        claim_id = f"CLM{uuid.uuid4().hex[:12]}"
        payer_claim_id = f"PCID{claim_id[-5:]}"

        claim = ClaimTransaction(
            status=status,
            date=input_date,
            claim_id=claim_id,
            service_line_id=f"SRV{bene.beneficiary_id}",
            sponsor_id=sponsor_id,
            beneficiary_id=bene.beneficiary_id,
            provider_npi=provider["npi"],
            provider_name=provider["name"],
            provider_entity_type=provider["entity_type"],
            provider_address_1=provider["address_line_1"],
            provider_address_2=provider["address_line_2"],
            provider_city=provider["city"],
            provider_state=provider["state"],
            provider_zip=provider["zipcode"],
            provider_phone=provider["phone"],
            amount=round(random.uniform(50, 1500), 2),
            payer_claim_id=payer_claim_id,
            creation=bene.creation
        )
        transactions.append(claim)
    transaction_funcs.save_many_claims(transactions)
    return transactions


def create_amt_data():
    data = {
        "deductibles": {
            "D2": round(random.uniform(Config.MIN_DEDUCTIBLES, Config.MAX_DEDUCTIBLES), 2),
            "FK": round(random.uniform(Config.MIN_DEDUCTIBLES, Config.MAX_DEDUCTIBLES), 2),
            "R": round(random.uniform(Config.MIN_DEDUCTIBLES, Config.MAX_DEDUCTIBLES), 2)
        },
        "visit_counts": {
            "C1": random.randint(Config.MIN_VISITS, Config.MAX_VISITS),
            "P3": random.randint(Config.MIN_VISITS, Config.MAX_VISITS),
            "B9": random.randint(Config.MIN_VISITS, Config.MAX_VISITS)
        }
    }
    logger.debug(f"Created AMT data: {data}")
    return data


class SponsorDataGenerator:
    def __init__(self, database_backend, faker_seed=Config.FAKER_SEED, random_seed=Config.RANDOM_SEED,
                 relationship_map=Config.RELATIONSHIP_MAP, csv_path=Config.DOWNLOAD_DIRECTORY):
        self.fake = Faker()
        Faker.seed(faker_seed)
        random.seed(random_seed)
        self.relationship_map = relationship_map
        self.repo = database_backend
        existing_ssns = self.repo.get_all_ssns()
        self.used_ssns = set(existing_ssns)
        self.csv_path = csv_path
        self.csv_rows = {}
        self.curr_csv_row = None
        self.load_csv_rows()

    def load_csv_rows(self):
        download_path = Path(self.csv_path)

        matching_csv = None
        for file in download_path.iterdir():
            if file.is_file() and file.suffix == ".csv":
                lower_name = file.stem.lower()
                if any(kw in lower_name for kw in ["insert", "database", "import"]):
                    matching_csv = file
                    break

        if not matching_csv:
            logger.info(f"No matching .csv file found in {download_path}. Using random data generation.")
            return

        try:
            df = pd.read_csv(matching_csv)
            for row in df.to_dict(orient="records"):
                key = row.get("Sponsor ICN") or row.get("Sponsor SSN")
                if not key:
                    logger.warning(f"Skipping row with no Sponsor ICN/SSN: {row}")
                    continue
                self.csv_rows.setdefault(key, []).append(row)

            logger.info(f"Loaded {len(self.csv_rows)} sponsor groups from CSV: {matching_csv.name}")

        except Exception as e:
            logger.error(f"Failed to load CSV {matching_csv}: {e}")
            self.csv_rows = {}

    def create_address(self):
        address = Address(
            building_number=self.fake.building_number(),
            street=self.fake.street_name().upper(),
            apartment=f'{self.fake.secondary_address().replace(".", "").upper()}' if random.random() < 0.5 else "",
            city=self.fake.city().upper(),
            state=self.fake.state_abbr(False, False).upper(),
            zipcode=self.fake.zipcode()
        )
        logger.debug(f"Created address: {address}")
        return address

    def generate_ssn(self):
        while True:
            ssn = self.fake.ssn()
            if ssn not in self.used_ssns:
                self.used_ssns.add(ssn)
                logger.debug(f"Generated unique SSN: {ssn}")
                return ssn
            else:
                logger.debug(f"Duplicate SSN created (skipping): {ssn}")

    def generate_sponsor_and_beneficiaries(self, total):
        generated = 0
        new_sponsors = []
        all_sponsor_ids = self.repo.get_all_sponsor_ids()

        if self.csv_rows:
            for sponsor_key, rows in self.csv_rows.items():
                first_row = rows[0]
                sponsor_ssn = first_row.get("Sponsor SSN")
                sponsor_icn = first_row.get("Sponsor ICN")

                if (sponsor_ssn and self.repo.ssn_exists(sponsor_ssn)) or (
                        sponsor_icn and sponsor_icn in all_sponsor_ids):
                    logger.warning(f"Skipping duplicate sponsor from CSV: SSN={sponsor_ssn}, ICN={sponsor_icn}")
                    continue

                self.curr_csv_row = first_row
                sponsor = self.create_sponsor()

                for row in rows:
                    self.curr_csv_row = row
                    bene = self.create_beneficiary(sponsor)
                    sponsor.beneficiaries.append(bene)
                    generated += 1

                new_sponsors.append(sponsor)

        self.curr_csv_row = None

        while generated < total:
            sponsor = self.create_sponsor()
            num_benes = min(random.randint(1, Config.MAX_BENEFICIARIES), total - generated)
            for _ in range(num_benes):
                bene = self.create_beneficiary(sponsor)
                sponsor.beneficiaries.append(bene)
                generated += 1

            new_sponsors.append(sponsor)

        return new_sponsors

    def store_sponsor_and_beneficiaries(self, total):
        sponsors = self.generate_sponsor_and_beneficiaries(total)
        self.repo.save_many_sponsors(sponsors)
        logger.info(f"Saved {len(sponsors)} sponsors")
        return sponsors

    def create_sponsor(self):
        row = self.curr_csv_row or {}

        sponsor_ssn = row.get("Sponsor SSN", self.generate_ssn())
        sponsor_id = row.get("Sponsor ICN", f"{sponsor_ssn.replace('-', '')}V11111111")
        dob = pd.to_datetime(row.get("Sponsor DOB", self.fake.date_of_birth())).date()
        sponsor_last_name = row.get("Sponsor Last Name", self.fake.last_name()).upper()
        sponsor_first_name = row.get("Sponsor First Name", self.fake.first_name()).upper()

        sponsor_address = self.create_address()

        sponsor_amt_data = create_amt_data()

        sponsor_gender = self.fake.passport_gender()
        if sponsor_gender == "X":
            sponsor_gender = random.choice(["M", "F"])

        sponsor = Sponsor(
            ssn=sponsor_ssn,
            dob=dob,
            first_name=sponsor_first_name,
            last_name=sponsor_last_name,
            gender=sponsor_gender,
            address=sponsor_address,
            phone=self.fake.basic_phone_number(),
            insurance_company=self.fake.company().upper(),
            insurance_FID=str(random.randint(100_000_000, 999_999_999)),
            middle_name=self.fake.first_name().upper(),
            sponsor_id=sponsor_id,
            deductibles=sponsor_amt_data["deductibles"],
            visit_counts=sponsor_amt_data["visit_counts"],
            creation="CSV" if self.curr_csv_row else "Faker"
        )

        logger.debug(f"Created Sponsor: {sponsor_id}")
        return sponsor

    def create_beneficiary(self, sponsor):
        row = self.curr_csv_row or {}

        relationship = random.choice(list(self.relationship_map.keys()))
        relationship_code = self.relationship_map[relationship]
        log_data["family"]["relationship_distribution"][relationship_code] += 1
        beneficiary_ssn = row.get("Bene SSN", self.generate_ssn())
        beneficiary_id = row.get("Bene ICN", f"{beneficiary_ssn.replace('-', '')}V11111111")
        dob = pd.to_datetime(row.get("Bene DOB", self.fake.date_of_birth())).date()
        bene_first_name = row.get("Bene First Name", self.fake.first_name()).upper()
        bene_last_name = row.get("Bene Last Name", sponsor.last_name).upper()
        beneficiary_amt_data = create_amt_data()
        beneficiary_gender = self.fake.passport_gender()

        if beneficiary_gender == "X":
            beneficiary_gender = random.choice(["M", "F"])

        beneficiary = Beneficiary(
            ssn=beneficiary_ssn,
            dob=dob,
            first_name=bene_first_name,
            last_name=bene_last_name,
            gender=beneficiary_gender,
            address=sponsor.address,
            phone=self.fake.basic_phone_number(),
            insurance_company=sponsor.insurance_company,
            insurance_FID=sponsor.insurance_FID,
            middle_name=self.fake.first_name().upper() if self.curr_csv_row is None else "",
            sponsor_id=sponsor.sponsor_id,
            beneficiary_id=beneficiary_id,
            relationship=relationship,
            deductibles=beneficiary_amt_data["deductibles"],
            visit_counts=beneficiary_amt_data["visit_counts"],
            creation="CSV" if self.curr_csv_row else "Faker"
        )
        logger.debug(f"Created beneficiary: {beneficiary_id} for sponsor {sponsor.sponsor_id}")
        return beneficiary
