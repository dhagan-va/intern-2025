import random
import uuid

from faker import Faker

from datetime import date
from Config import Config
from Config.Config import logger
from DataLayer.Datatypes import Address, Sponsor, Beneficiary, ClaimTransaction
from Repository.DatabaseFactory import get_database_backend
from Config.Data_Visualizer import log_data


def generate_claim_transactions(num_claims, transaction_funcs, input_date=date.today(), status="Created"):
    npi_funcs = transaction_funcs.npi_funcs
    beneficiaries = transaction_funcs.get_random_beneficiary(num_claims)

    transactions = []

    for bene in beneficiaries:
        sponsor_id = bene.sponsor_id
        provider = npi_funcs.get_random_provider(bene.address.state)

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
            payer_claim_id=payer_claim_id
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
                 relationship_map=Config.RELATIONSHIP_MAP):
        self.fake = Faker()
        Faker.seed(faker_seed)
        random.seed(random_seed)
        self.relationship_map = relationship_map
        self.repo = database_backend
        existing_ssns = self.repo.get_all_ssns()
        self.used_ssns = set(existing_ssns)

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

        while generated < total:
            sponsor = self.create_sponsor()
            num_beneficiaries = random.randint(Config.MIN_BENEFICIARIES, Config.MAX_BENEFICIARIES)
            log_data["family"]["size_distribution"][num_beneficiaries] += 1
            for _ in range(num_beneficiaries):
                beneficiary = self.create_beneficiary(sponsor)
                sponsor.beneficiaries.append(beneficiary)
                generated += 1
                if generated >= total:
                    break

            new_sponsors.append(sponsor)
        return new_sponsors

    def store_sponsor_and_beneficiaries(self, total):
        sponsors = self.generate_sponsor_and_beneficiaries(total)
        self.repo.save_many_sponsors(sponsors)
        logger.info(f"Saved {len(sponsors)} sponsors")
        return sponsors

    def create_sponsor(self):
        sponsor_ssn = self.generate_ssn()
        sponsor_id = f'{sponsor_ssn.replace("-", "")}V11111111'
        sponsor_last_name = self.fake.last_name().upper()
        sponsor_address = self.create_address()
        sponsor_amt_data = create_amt_data()
        sponsor_gender = self.fake.passport_gender()
        if sponsor_gender == "X":
            sponsor_gender = random.choice(["M", "F"])
        sponsor_first = self.fake.first_name_male() if sponsor_gender == 'M' else self.fake.first_name_female()

        sponsor = Sponsor(
            ssn=sponsor_ssn,
            dob=self.fake.date_of_birth(),
            first_name=sponsor_first.upper(),
            last_name=sponsor_last_name,
            gender=sponsor_gender,
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
        relationship_code = self.relationship_map[relationship]
        log_data["family"]["relationship_distribution"][relationship_code] += 1
        beneficiary_ssn = self.generate_ssn()
        beneficiary_id = f'{beneficiary_ssn.replace("-", "")}V11111111'
        beneficiary_amt_data = create_amt_data()
        beneficiary_gender = self.fake.passport_gender()
        if beneficiary_gender == "X":
            beneficiary_gender = random.choice(["M", "F"])
        bene_first = self.fake.first_name_male() if beneficiary_gender == 'M' else self.fake.first_name_female()

        beneficiary = Beneficiary(
            ssn=beneficiary_ssn,
            dob=self.fake.date_of_birth(),
            first_name=bene_first.upper(),
            last_name=sponsor.last_name,
            gender=beneficiary_gender,
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
