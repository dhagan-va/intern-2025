import random

from faker import Faker

import config
from config import logger
from DataLayer.Datatypes import Address, Sponsor, Beneficiary
from Repository.Local_Database_Functions import LocalDBFunctions


def create_amt_data():
    data = {
        "deductibles": {
            "D2": random.randint(config.MIN_DEDUCTIBLES, config.MAX_DEDUCTIBLES),
            "FK": random.randint(config.MIN_DEDUCTIBLES, config.MAX_DEDUCTIBLES),
            "R": random.randint(config.MIN_DEDUCTIBLES, config.MAX_DEDUCTIBLES)
        },
        "visit_counts": {
            "C1": random.randint(config.MIN_VISITS, config.MAX_VISITS),
            "P3": random.randint(config.MIN_VISITS, config.MAX_VISITS),
            "B9": random.randint(config.MIN_VISITS, config.MAX_VISITS)
        }
    }
    logger.debug(f"Created AMT data: {data}")
    return data


class SponsorDataGenerator:
    def __init__(self, faker_seed=config.FAKER_SEED, random_seed=config.RANDOM_SEED,
                 relationship_map=config.RELATIONSHIP_MAP, data_access=None):
        self.fake = Faker()
        Faker.seed(faker_seed)
        random.seed(random_seed)
        self.relationship_map = relationship_map
        self.used_ssns = set()

        if data_access:
            self.repo = data_access
            logger.debug("Using local storage")
        else:
            try:
                self.repo = MongoDBFunctions()
                logger.info("Using MongoDB for storage")
            except Exception as e:
                logger.warning("MongoDB is not available")
                self.repo = LocalDBFunctions()

    def create_address(self):
        address = Address(
            building_number=self.fake.building_number(),
            street=self.fake.street_name().upper(),
            apartment=f"{self.fake.secondary_address().replace(".", "").upper()}" if random.random() < 0.5 else "",
            city=self.fake.city().upper(),
            state=self.fake.state_abbr(False, False).upper(),
            zipcode=self.fake.zipcode()
        )
        logger.debug(f"Created address: {address}")
        return address

    def generate_ssn(self):
        while True:
            ssn = self.fake.ssn()
            if ssn not in self.used_ssns and not self.repo.ssn_exists(ssn):
                self.used_ssns.add(ssn)
                logger.debug(f"Generated unique SSN: {ssn}")
                return ssn
            else:
                logger.debug(f"Duplicate SSN created (skipping): {ssn}")

    def generate_sponsor_and_beneficiaries(self, total):
        existing_users = len(self.repo.existing_ssns)
        remaining = config.USER_LIMIT - existing_users

        if remaining <= 0:
            logger.warning("User limit already reached. No data generated.")
            return []

        generated = 0
        new_sponsors = []

        while generated < total and remaining > 0:
            sponsor = self.create_sponsor()
            num_beneficiaries = min(random.randint(config.MIN_BENEFICIARIES, config.MAX_BENEFICIARIES), remaining)
            for _ in range(num_beneficiaries):
                beneficiary = self.create_beneficiary(sponsor)
                sponsor.beneficiaries.append(beneficiary)
                generated += 1
                remaining -= 1
                if generated >= total or remaining <= 0:
                    break

            new_sponsors.append(sponsor)

        return new_sponsors

    def store_sponsor_and_beneficiaries(self, total):
        sponsors = self.generate_sponsor_and_beneficiaries(total)
        for sponsor in sponsors:
            self.repo.save_sponsor(sponsor)
            logger.debug(f"Sponsor {sponsor.sponsor_id} with {len(sponsor.beneficiaries)} beneficiaries saved")
        logger.info(f"Finished generating {len(sponsors)} sponsors")
        return sponsors

    def create_sponsor(self):
        sponsor_ssn = self.generate_ssn()
        sponsor_id = f"{sponsor_ssn.replace("-", "")}V11111111"
        sponsor_last_name = self.fake.last_name().upper()
        sponsor_address = self.create_address()
        sponsor_amt_data = create_amt_data()

        sponsor = Sponsor(
            ssn=sponsor_ssn,
            dob=self.fake.date_of_birth(),
            first_name=self.fake.first_name().upper(),
            last_name=sponsor_last_name,
            address=sponsor_address,
            phone=self.fake.basic_phone_number(),
            insurance_company=self.fake.company().upper(),
            insurance_FID=str(random.randint(100_000_000, 999_999_999)),
            middle_name=self.fake.first_name().upper(),
            sponsor_id=sponsor_id,
            deductibles=sponsor_amt_data["deductibles"],
            visit_counts=sponsor_amt_data["visit_counts"]
        )

        logger.debug(f"Created Sponsor: {sponsor_id}")
        return sponsor

    def create_beneficiary(self, sponsor):
        relationship = random.choice(list(self.relationship_map.keys()))
        beneficiary_ssn = self.generate_ssn()
        beneficiary_id = f"{beneficiary_ssn.replace("-", "")}V11111111"
        beneficiary_amt_data = create_amt_data()

        beneficiary = Beneficiary(
            ssn=beneficiary_ssn,
            dob=self.fake.date_of_birth(),
            first_name=self.fake.first_name().upper(),
            last_name=sponsor.last_name,
            address=sponsor.address,
            phone=self.fake.basic_phone_number(),
            insurance_company=sponsor.insurance_company,
            insurance_FID=sponsor.insurance_FID,
            middle_name=self.fake.first_name().upper(),
            sponsor_id=sponsor.sponsor_id,
            beneficiary_id=beneficiary_id,
            relationship=relationship,
            deductibles=beneficiary_amt_data["deductibles"],
            visit_counts=beneficiary_amt_data["visit_counts"]
        )
        logger.debug(f"Created beneficiary: {beneficiary_id} for sponsor {sponsor.sponsor_id}")
        return beneficiary
