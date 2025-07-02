"""
Defines data classes for database
"""
from dataclasses import dataclass, field, asdict
from datetime import date
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

    @staticmethod
    def from_dict(data):
        return Address(**data)


@dataclass
class Base:
    ssn: str
    dob: date
    first_name: str
    last_name: str
    gender: str
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
    deductibles: Dict[str, float] = field(default_factory=dict)
    visit_counts: Dict[str, int] = field(default_factory=dict)

    def to_dict(self):
        return {
            "ssn": self.ssn,
            "dob": self.dob.isoformat(),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "gender": self.gender,
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

    @staticmethod
    def from_dict(data):
        return Beneficiary(
            ssn=data["ssn"],
            dob=date.fromisoformat(data["dob"]),
            first_name=data["first_name"],
            last_name=data["last_name"],
            gender=data["gender"],
            address=Address.from_dict(data["address"]),
            phone=data["phone"],
            insurance_company=data["insurance_company"],
            insurance_FID=data["insurance_FID"],
            middle_name=data["middle_name"],
            sponsor_id=data["sponsor_id"],
            beneficiary_id=data["beneficiary_id"],
            relationship=data["relationship"],
            deductibles=data["deductibles"],
            visit_counts=data["visit_counts"]
        )


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
            "gender": self.gender,
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

    @staticmethod
    def from_dict(data):
        return Sponsor(
            ssn=data["ssn"],
            dob=date.fromisoformat(data["dob"]),
            first_name=data["first_name"],
            last_name=data["last_name"],
            gender=data["gender"],
            address=Address.from_dict(data["address"]),
            phone=data["phone"],
            insurance_company=data["insurance_company"],
            insurance_FID=data["insurance_FID"],
            middle_name=data["middle_name"],
            sponsor_id=data["sponsor_id"],
            deductibles=data["deductibles"],
            visit_counts=data["visit_counts"],
            beneficiaries=[
                Beneficiary.from_dict(b) for b in data.get("beneficiaries", [])
            ]
        )


@dataclass
class ClaimTransaction:
    state: str
    claim_id: str
    service_line_id: str
    sponsor_id: str
    beneficiary_id: str
    provider_npi: str
    amount: float
    payer_claim_id: Optional[str] = None

    def to_dict(self):
        return asdict(self)
