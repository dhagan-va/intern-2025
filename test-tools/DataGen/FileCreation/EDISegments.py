"""
Each class is its own EDI segment
"""
import logging
from datetime import datetime
from typing import Optional

import config

# Need to add logging to this file
logger = logging.getLogger(__name__)


# File Header
class ISA:
    def __init__(self, sender=config.SENDER_ID, receiver=config.RECEIVER_ID):
        now = datetime.now()
        self.sender = sender
        self.receiver = receiver
        self.id_qualifier = "ZZ"
        self.interCtrlNumber = now.strftime("%Y%m%d1")
        self.date = now.strftime("%y%m%d")
        self.time = now.strftime("%H%M")

    def to_edi(self):
        return (
            f"ISA*00*          *00*          *{self.id_qualifier}*{self.sender:<15}*{self.id_qualifier}*{self.receiver:<15}*{self.date}*{self.time}*$*00501"
            f"*{self.interCtrlNumber}*0*T*:~\n")


# File Trailer
class IEA:
    def __init__(self):
        now = datetime.now()
        self.interCtrlNumber = now.strftime("%Y%m%d1")

    def to_edi(self):
        return f"IEA*1*{self.interCtrlNumber}~"


# Group Header
class GS:
    def __init__(self, sender=config.SENDER_ID, receiver=config.RECEIVER_ID):
        now = datetime.now()
        self.sender = sender
        self.receiver = receiver
        self.date = now.strftime("%Y%m%d")
        self.time = now.strftime("%H%M%S")

    def to_edi(self):
        return f"GS*BE*{self.sender}*{self.receiver}*{self.date}*{self.time}*61*X*005010X220A1~\n"


# Group Trailer
class GE:
    def __init__(self, num):
        self.num = num

    def to_edi(self):
        return f"GE*{self.num}*61~\n"


# Message Contents
class ST:
    def __init__(self, num):
        self.num = num

    def to_edi(self):
        return f"ST*834*{self.num:04}~\n"


class SE:
    def __init__(self, segment_count, control_num):
        self.segment_count = segment_count
        self.control_num = f"{control_num:04}"

    def to_edi(self):
        return f"SE*{self.segment_count}*{self.control_num}~\n"


class BGN:
    def __init__(self, ref_id):
        now = datetime.now()
        self.ref_id = ref_id
        self.date = now.strftime("%Y%m%d")
        self.time = now.strftime("%H%M%S")

    def to_edi(self):
        return f"BGN*00*{self.ref_id}*{self.date}*{self.time}*UT***2~\n"


class N1:
    def __init__(self, entity_id_code, name, id_code):
        self.entity_id_code = entity_id_code
        self.name = name
        self.id_code = id_code

    def to_edi(self):
        return f"N1*{self.entity_id_code}*{self.name}*FI*{self.id_code}~\n"


class INS:
    def __init__(self, relationship):
        self.relationship = relationship

    def to_edi(self):
        return f"INS*Y*{self.relationship}*001**A***AC~\n"


class REF:
    def __init__(self, qualifier, reference_id):
        self.qualifier = qualifier
        self.reference_id = reference_id

    def to_edi(self):
        return f"REF*{self.qualifier}*{self.reference_id}~\n"


class NM1:
    def __init__(self, last_name, first_name, middle_name, ssn):
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.ssn = ssn

    def to_edi(self):
        return f"NM1*IL*1*{self.last_name}*{self.first_name}*{self.middle_name}***34*{self.ssn}~\n"


class PER:
    def __init__(self, phone_number):
        self.phone_number = phone_number

    def to_edi(self):
        return f"PER*IP**TE*{self.phone_number}~\n"


class N3:
    def __init__(self, building_number, street, apartment: Optional[str] = None):
        self.building_number = building_number
        self.street = street
        self.apartment = apartment if apartment else ""

    def to_edi(self):
        return f"N3*{self.building_number}{" "}{self.street}*{self.apartment}~\n"


class N4:
    def __init__(self, city, state, zipcode):
        self.city = city
        self.state = state
        self.zipcode = zipcode

    def to_edi(self):
        return f"N4*{self.city}*{self.state}*{self.zipcode}~\n"


class AMT:
    def __init__(self, amount_qualifier_code, amount):
        self.amount_qualifier_code = amount_qualifier_code
        self.amount = amount

    def to_edi(self):
        return f"AMT*{self.amount_qualifier_code}*{self.amount}~\n"


class HD:
    def __init__(self, maintenance_type_code="001", plan_coverage_description="MCVA1003"):
        self.maintenance_type_code = maintenance_type_code
        self.plan_coverage_description = plan_coverage_description

    def to_edi(self):
        return f"HD*{self.maintenance_type_code}**MM*{self.plan_coverage_description}~\n"


class DTP:
    def __init__(self):
        now = datetime.now()
        self.date = now.strftime("%Y%m%d")

    def to_edi(self):
        return f"DTP*348*D8*{self.date}~\n"
