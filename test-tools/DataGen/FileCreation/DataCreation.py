import logging
import random
from faker import Faker
from DataLayer.Datatypes import Address, Sponsor, Beneficiary
import config
from Repository.Local_Database_Functions import LocalDBFunctions

logger = logging.getLogger(__name__)


def create_amt_data():
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


class Make834Data:
    def __init__(self, faker_seed=config.FAKER_SEED, random_seed=config.RANDOM_SEED,
                 relationship_map=config.RELATIONSHIP_MAP, data_access=None):
        self.fake = Faker()
        Faker.seed(faker_seed)
        random.seed(random_seed)
        self.relationship_map = relationship_map
        self.used_ssns = set()

        if data_access:
            self.repo = data_access
        else:
            try:
                self.repo = MongoDBFunctions()
            except Exception as e:
                logger.warning("MongoDB is not available. Using local JSON")
                self.repo = LocalDBFunctions()

    def create_address(self):
        return Address(
            building_number=self.fake.building_number(),
            street=self.fake.street_name(),
            apartment=f"{self.fake.secondary_address().replace(".", "")}" if random.random() < 0.5 else "",
            city=self.fake.city(),
            state=self.fake.state_abbr(False, False),
            zipcode=self.fake.zipcode()
        )

    def generate_ssn(self):
        while True:
            ssn = self.fake.ssn().replace("-", "")
            if ssn not in self.used_ssns and not self.repo.ssn_exists(ssn):
                self.used_ssns.add(ssn)
                return int(ssn)

    def create_sponsor_and_beneficiaries(self, n):
        sponsor_ssn = self.generate_ssn()
        sponsor_id = f"{sponsor_ssn}V11111111"
        sponsor_last_name = self.fake.last_name()
        sponsor_address = self.create_address()
        sponsor_amt_data = create_amt_data()

        for _ in range(n):
            sponsor = Sponsor(
                ssn=sponsor_ssn,
                dob=self.fake.date_of_birth(),
                first_name=self.fake.first_name(),
                last_name=sponsor_last_name,
                address=sponsor_address,
                phone=self.fake.basic_phone_number(),
                insurance_company=self.fake.company(),
                insurance_FID=str(random.randint(100_000_000, 999_999_999)),
                middle_name=self.fake.first_name(),
                sponsor_id=sponsor_id,
                deductibles=sponsor_amt_data["deductibles"],
                visit_counts=sponsor_amt_data["visit_counts"]
            )

            # make it so that beneficiary age makes sense (child < age than sponsor)
            # also add weighted randomization to num of beneficiaries
            # should I make these outside?
            num_beneficiaries = random.randint(1, 4)
            for _ in range(num_beneficiaries):
                relationship = random.choice(list(self.relationship_map.keys()))
                beneficiary_ssn = self.generate_ssn()
                beneficiary_id = f"{beneficiary_ssn}V11111111"
                beneficiary_amt_data = create_amt_data()

                beneficiary = Beneficiary(
                    ssn=beneficiary_ssn,
                    dob=self.fake.date_of_birth(),
                    first_name=self.fake.first_name(),
                    last_name=sponsor_last_name,
                    address=sponsor_address,
                    phone=self.fake.basic_phone_number(),
                    insurance_company=self.fake.company(),
                    insurance_FID=str(random.randint(100_000_000, 999_999_999)),
                    middle_name=self.fake.first_name(),
                    sponsor_id=sponsor_id,
                    beneficiary_id=beneficiary_id,
                    relationship=relationship,
                    deductibles=beneficiary_amt_data["deductibles"],
                    visit_counts=beneficiary_amt_data["visit_counts"]
                )
                sponsor.beneficiaries.append(beneficiary)

            self.repo.save_sponsor(sponsor)

    def return_generated_data(self):
        return self.repo.data

    def save_generated_data(self):
        self.repo.save_all()
