from abc import ABC, abstractmethod


class DataAccess(ABC):
    @abstractmethod
    def get_random_beneficiary(self, count): pass

    @abstractmethod
    def total_beneficiaries(self): pass

    @abstractmethod
    def save_sponsor(self, sponsor): pass

    @abstractmethod
    def save_many_sponsors(self, sponsors): pass

    @abstractmethod
    def get_all_ssns(self): pass

    @abstractmethod
    def ssn_exists(self, ssn): pass

    @abstractmethod
    def get_sponsor_by_id(self, sponsor_id): pass

    @abstractmethod
    def get_sponsor_field(self, sponsor_id, field): pass

    @abstractmethod
    def update_sponsor_field(self, sponsor_id, field, value): pass

    # Beneficiary methods
    @abstractmethod
    def get_beneficiary(self, sponsor_id, beneficiary_id): pass

    @abstractmethod
    def get_beneficiary_field(self, sponsor_id, beneficiary_id, field): pass

    @abstractmethod
    def update_beneficiary_field(self, sponsor_id, beneficiary_id, field, value): pass

    @abstractmethod
    def get_bene_deductible(self, sponsor_id, beneficiary_id, code): pass

    @abstractmethod
    def get_bene_visit(self, sponsor_id, beneficiary_id, code): pass

    @abstractmethod
    def update_bene_deductible(self, sponsor_id, beneficiary_id, code, value): pass

    @abstractmethod
    def update_bene_visit(self, sponsor_id, beneficiary_id, code, value): pass

    @abstractmethod
    def save_claim_transaction(self, claim, commit):
        pass

    @abstractmethod
    def save_many_claims(self, claims):
        pass

    @abstractmethod
    def get_claim_transactions(self, status, date):
        pass

    @abstractmethod
    def update_claims_status(self, claim_ids, new_status):
        pass

    @abstractmethod
    def total_claim_transactions(self):
        pass
