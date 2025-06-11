import random
from faker import Faker
from Datatypes import Address, Sponsor, Beneficiary
import config
from Database_Functions import get_collection


class Make834Data:
    def __init__(self, faker_seed=config.FAKER_SEED, random_seed=config.RANDOM_SEED,
                 relationship_map=config.RELATIONSHIP_MAP):
        self.fake = Faker()
        Faker.seed(faker_seed)
        random.seed(random_seed)
        self.collection = get_collection()
        self.relationship_map = relationship_map

    def create_address(self):
        return Address(
            building_number=self.fake.building_number(),
            street=self.fake.street_name(),
            apartment=f'{self.fake.secondary_address().replace(".", "")}" if random.random() < 0.5 else "',
            city=self.fake.city(),
            state=self.fake.state_abbr(False, False),
            zipcode=self.fake.zipcode()
        )

    def create_amt_data(self):
        return {
            "deductibles": {
                "D2": random.randint(0, 100_000),
                "FK": random.randint(0, 100_000),
                "R": random.randint(0, 100_000)
            },
            "visit_counts": {
                "C1": random.randint(0, 15),
                "P3": random.randint(0, 15),
                "B9": random.randint(0, 15)
            }
        }

    def ssn_exists(self, ssn):
        return self.collection.find_one(
            {"$or": [{"ssn": ssn}, {"beneficiaries.ssn": ssn}]}
        ) is not None

    def generate_ssn(self):
        while True:
            ssn = self.fake.ssn()
            if not self.ssn_exists(ssn):
                return ssn

    def sponsor_id_exists(self, sponsor_id):
        return self.collection.find_one({"sponsor_id": sponsor_id}) is not None

    def beneficiary_id_exists(self, beneficiary_id):
        return self.collection.find_one({"beneficiaries.beneficiary_id": beneficiary_id}) is not None

    def generate_sponsor_id(self):
        while True:
            candidate = f"1111111111V{random.randint(10_000_000, 99_999_999)}"
            if not self.sponsor_id_exists(candidate):
                return candidate

    def generate_beneficiary_id(self):
        while True:
            candidate = f"1111111111V{random.randint(10_000_000, 99_999_999)}"
            if not self.beneficiary_id_exists(candidate):
                return candidate

    def create_sponsor_and_beneficiaries(self):
        sponsor_id = self.generate_sponsor_id()
        sponsor_last_name = self.fake.last_name()
        sponsor_address = self.create_address()
        amt_data = self.create_amt_data()

        sponsor = Sponsor(
            ssn=self.generate_ssn(),
            dob=self.fake.date_of_birth(),
            first_name=self.fake.first_name(),
            last_name=sponsor_last_name,
            address=sponsor_address,
            phone=self.fake.basic_phone_number(),
            insurance_company=self.fake.company(),
            insurance_FID=str(random.randint(100_000_000, 999_999_999)),
            middle_name=self.fake.first_name(),
            sponsor_id=sponsor_id,
            deductibles=amt_data["deductibles"],
            visit_counts=amt_data["visit_counts"]
        )

        # make it so that beneficiary age makes sense (child < age than sponsor)
        # also add weighted randomization to num of beneficiaries
        num_beneficiaries = random.randint(1, 4)
        for _ in range(num_beneficiaries):
            relationship = random.choice(list(self.relationship_map.keys()))

            beneficiary = Beneficiary(
                ssn=self.generate_ssn(),
                dob=self.fake.date_of_birth(),
                first_name=self.fake.first_name(),
                last_name=sponsor_last_name,
                address=sponsor_address,
                phone=self.fake.basic_phone_number(),
                insurance_company=self.fake.company(),
                insurance_FID=str(random.randint(100_000_000, 999_999_999)),
                middle_name=self.fake.first_name(),
                sponsor_id=sponsor_id,
                beneficiary_id=self.generate_beneficiary_id(),
                relationship=relationship,
                deductibles=amt_data["deductibles"],
                visit_counts=amt_data["visit_counts"]
            )
            sponsor.beneficiaries.append(beneficiary)

        return sponsor
