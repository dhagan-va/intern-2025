import json
import logging
import os
import random

from Config import Config
from DataLayer.Datatypes import Sponsor
from DataLayer.Interfaces import DataAccess
from Config.Config import get_local_db_path, logger, FAMILY_DATABASE_DIRECTORY, FAMILY_DATABASE_JSONL


class LocalDBFunctions(DataAccess):
    def __init__(self, file=get_local_db_path(FAMILY_DATABASE_DIRECTORY, FAMILY_DATABASE_JSONL)):
        self.data = []
        self.all_bene = []
        self.file = file
        self.existing_ssns = set()
        self.load_localdb()

    def load_localdb(self):
        if not os.path.exists(self.file):
            return
        with open(self.file, "r") as f:
            for line in f:
                sponsor_dict = json.loads(line)
                sponsor = Sponsor.from_dict(sponsor_dict)
                self.data.append(sponsor)
                self.all_bene.extend(sponsor.beneficiaries)
                self.add_ssns_to_set(sponsor)
        logging.debug(f"There are {len(self.existing_ssns)} users in the database")

    def get_random_beneficiary(self, count):
        if not self.all_bene:
            logging.error("There are no beneficiaries to choose")
            raise ValueError("There are no beneficiaries to choose")

        if count > len(self.all_bene):
            logging.warning("Requested more than available. Returning all available")
            count = len(self.all_bene)

        return random.sample(self.all_bene, count)

    def save_sponsor(self, sponsor):
        total_users = len(self.existing_ssns)
        curr_user_count = 1 + len(sponsor.beneficiaries)
        if total_users + curr_user_count > Config.USER_LIMIT:
            logger.warning("Max User Limit reached. Skipping save.")
            return

        sponsor_dict = sponsor.to_dict()

        with open(self.file, "a") as f:
            json.dump(sponsor_dict, f)
            f.write("\n")
        self.add_ssns_to_set(sponsor)
        logger.debug(f"Saved sponsor: {sponsor_dict}")

    def total_beneficiaries(self):
        return len(self.all_bene)

    def add_ssns_to_set(self, sponsor):
        self.existing_ssns.add(sponsor.ssn)
        logger.debug(f"Added sponsor SSN to set: {sponsor.ssn}")
        for b in sponsor.beneficiaries:
            self.existing_ssns.add(b.ssn)
            logger.debug(f"Added beneficiary SSN to set: {b.ssn}")

    def ssn_exists(self, ssn):
        return ssn in self.existing_ssns

    def get_sponsor_by_id(self, sponsor_id):
        return next((s for s in self.data if s["sponsor_id"] == sponsor_id), None)

    def get_sponsor_field(self, sponsor_id, field):
        sponsor = self.get_sponsor_by_id(sponsor_id)
        return sponsor.get(field) if sponsor else None

    def update_sponsor_field(self, sponsor_id, field, value):
        for sponsor in self.data:
            if sponsor["sponsor_id"] == sponsor_id:
                sponsor[field] = value
                return True
        return False

    def get_beneficiary(self, sponsor_id, beneficiary_id):
        sponsor = self.get_sponsor_by_id(sponsor_id)
        if sponsor:
            for b in sponsor.get("beneficiaries", []):
                if b["beneficiary_id"] == beneficiary_id:
                    return b
        return None

    def update_beneficiary_field(self, sponsor_id, beneficiary_id, field, value):
        sponsor = self.get_sponsor_by_id(sponsor_id)
        if sponsor:
            for b in sponsor.get("beneficiaries", []):
                if b["beneficiary_id"] == beneficiary_id:
                    b[field] = value
                    return True
        return False

    def get_beneficiary_field(self, sponsor_id, beneficiary_id, field):
        beneficiary = self.get_beneficiary(sponsor_id, beneficiary_id)
        return beneficiary.get(field) if beneficiary else None

    def get_bene_deductible(self, sponsor_id, beneficiary_id, code):
        beneficiary = self.get_beneficiary(sponsor_id, beneficiary_id)
        if beneficiary:
            return beneficiary.get("deductibles", {}).get(code)
        return None

    def get_bene_visit(self, sponsor_id, beneficiary_id, code):
        beneficiary = self.get_beneficiary(sponsor_id, beneficiary_id)
        if beneficiary:
            return beneficiary.get("visit_counts", {}).get(code)
        return None

    def update_bene_deductible(self, sponsor_id, beneficiary_id, code, value):
        sponsor = self.get_sponsor_by_id(sponsor_id)
        if sponsor:
            for b in sponsor.get("beneficiaries", []):
                if b["beneficiary_id"] == beneficiary_id:
                    b["deductibles"][code] = value
                    return True
        return False

    def update_bene_visit(self, sponsor_id, beneficiary_id, code, value):
        sponsor = self.get_sponsor_by_id(sponsor_id)
        if sponsor:
            for b in sponsor.get("beneficiaries", []):
                if b["beneficiary_id"] == beneficiary_id:
                    b["visit_counts"][code] = value
                    return True
        return False
