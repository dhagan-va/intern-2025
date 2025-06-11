"""
Defines data classes for database
"""
import datetime
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


@dataclass
class Sponsor(Base):
    sponsor_id: str
    middle_name: Optional[str] = None
    deductibles: Dict[str, float] = field(default_factory=dict)
    visit_counts: Dict[str, int] = field(default_factory=dict)
    beneficiaries: List[Beneficiary] = field(default_factory=list)
