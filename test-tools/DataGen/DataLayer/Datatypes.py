"""
Defines data classes for database
"""
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Address:
    building_number: str
    street: str
    apartment: str
    city: str
    state: str
    zipcode: str

    def to_dict(self):
        return {
            "building_number": self.building_number,
            "street": self.street,
            "apartment": self.apartment,
            "city": self.city,
            "state": self.state,
            "zipcode": self.zipcode,
        }


@dataclass
class Base:
    ssn: str
    dob: datetime
    first_name: str
    last_name: str
    address: Address
    phone: str
    insurance_company: str
    insurance_FID: str


@dataclass
class Beneficiary(Base):
    sponsor_id: str
    beneficiary_id: str
    relationship: str
    middle_name: Optional[str] = None
    deductibles: Dict[str, int] = field(default_factory=dict)
    visit_counts: Dict[str, int] = field(default_factory=dict)

    def to_dict(self):
        return {
            "ssn": self.ssn,
            "dob": self.dob,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address.to_dict(),
            "phone": self.phone,
            "insurance_company": self.insurance_company,
            "insurance_FID": self.insurance_FID,
            "sponsor_id": self.sponsor_id,
            "beneficiary_id": self.beneficiary_id,
            "relationship": self.relationship,
            "middle_name": self.middle_name,
            "deductibles": self.deductibles,
            "visit_counts": self.visit_counts
        }


@dataclass
class Sponsor(Base):
    sponsor_id: str
    middle_name: Optional[str] = None
    deductibles: Dict[str, float] = field(default_factory=dict)
    visit_counts: Dict[str, int] = field(default_factory=dict)
    beneficiaries: List[Beneficiary] = field(default_factory=list)

    def to_dict(self):
        return {
            "ssn": self.ssn,
            "dob": self.dob.isoformat(),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address.to_dict(),
            "phone": self.phone,
            "insurance_company": self.insurance_company,
            "insurance_FID": self.insurance_FID,
            "sponsor_id": self.sponsor_id,
            "middle_name": self.middle_name,
            "deductibles": self.deductibles,
            "visit_counts": self.visit_counts,
            "beneficiaries": [b.to_dict() for b in self.beneficiaries]
        }