from abc import ABC, abstractmethod


class DataAccess(ABC):
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
    def get_bene_deductible(self, sponsor_id, bene_id, code): pass

    @abstractmethod
    def get_bene_visit(self, sponsor_id, bene_id, code): pass

    @abstractmethod
    def update_bene_deductible(self, sponsor_id, bene_id, code, value): pass

    @abstractmethod
    def update_bene_visit(self, sponsor_id, bene_id, code, value): pass
    