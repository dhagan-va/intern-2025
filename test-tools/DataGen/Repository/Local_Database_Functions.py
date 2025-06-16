import json
import logging
import os

import config
from DataLayer.Interfaces import DataAccess
from config import get_local_db_path

logger = logging.getLogger(__name__)


class LocalDBFunctions(DataAccess):
    def __init__(self, file=None):
        if file is None:
            file = get_local_db_path()
        self.data = []
        self.file = file
        self.existing_ssns = set()
        self.loadfile()

    def loadfile(self):
        if not os.path.exists(self.file):
            open(self.file, "w").close()
            logger.debug(f"{self.file} created")
        with open(self.file, "r") as f:
            for line in f:
                family = json.loads(line)
                self.data.append(family)
                self.add_ssns_to_set(family)

    def save_sponsor(self, sponsor):
        with open(self.file, "a") as f:
            json.dump(sponsor.to_dict(), f)
            f.write("\n")
        self.add_ssns_to_set(sponsor.to_dict())

    def add_ssns_to_set(self, sponsor_dict):
        self.existing_ssns.add(sponsor_dict["ssn"])
        for b in sponsor_dict.get("beneficiaries", []):
            self.existing_ssns.add(b["ssn"])

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
