"""
Each class is its own EDI segment
"""
from datetime import datetime
from typing import Optional

import config
from config import logger


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
        logger.debug("Generating ISA segment")
        return (
            f"ISA*00*          *00*          *{self.id_qualifier}*{self.sender:<15}*{self.id_qualifier}*"
            f"{self.receiver:<15}*{self.date}*{self.time}*$*00501*{self.interCtrlNumber}*0*T*:~\n")


# File Trailer
class IEA:
    def __init__(self):
        now = datetime.now()
        self.interCtrlNumber = now.strftime("%Y%m%d1")

    def to_edi(self):
        logger.debug("Generating IEA segment")
        return f"IEA*1*{self.interCtrlNumber}~\n"


# Group Header
class GS:
    def __init__(self, functional_id, sender=config.SENDER_ID, receiver=config.RECEIVER_ID):
        now = datetime.now()
        self.functional_id = functional_id
        self.sender = sender
        self.receiver = receiver
        self.date = now.strftime("%Y%m%d")
        self.time = now.strftime("%H%M%S")

    def to_edi(self):
        logger.debug("Generating GS segment")
        return f"GS*{self.functional_id}*{self.sender}*{self.receiver}*{self.date}*{self.time}*61*X*005010X220A1~\n"


# Group Trailer
class GE:
    def __init__(self, num):
        self.num = num

    def to_edi(self):
        logger.debug("Generating GE segment")
        return f"GE*{self.num}*61~\n"


# Transaction Set Header
class ST:
    def __init__(self, file_type, num):
        self.file_type = file_type
        self.num = num

    def to_edi(self):
        logger.debug(f"Generating ST segment for an {self.file_type} file, transaction #{self.num}")
        return f"ST*{self.file_type}*{self.num:04}~\n"


# Transaction Set Trailer
class SE:
    def __init__(self, segment_count, control_num):
        self.segment_count = segment_count
        self.control_num = f"{control_num:04}"

    def to_edi(self):
        logger.debug(f"Generating SE segment with count {self.segment_count} and control {self.control_num}")
        return f"SE*{self.segment_count}*{self.control_num}~\n"


# Beginning Segment
class BGN:
    def __init__(self, ref_id):
        now = datetime.now()
        self.ref_id = ref_id
        self.date = now.strftime("%Y%m%d")
        self.time = now.strftime("%H%M%S")

    def to_edi(self):
        logger.debug(f"Generating BGN segment with ref_id {self.ref_id}")
        return f"BGN*00*{self.ref_id}*{self.date}*{self.time}*UT***2~\n"


# Sponsor Name
class N1:
    def __init__(self, entity_id_code, name, id_code, error_ctrl, error_id):
        self.entity_id_code = entity_id_code
        self.name = name
        self.id_code = id_code
        self.error_ctrl = error_ctrl
        self.error_id = error_id

    def to_edi(self):
        id_code = self.id_code
        if self.error_ctrl and self.error_ctrl.should_insert():
            erroneous = self.error_ctrl.insert(id_code, "missing")
            logger.warning(
                f"[ERROR INSERTED] N1 segment: ID code '{id_code}' changed to '{erroneous}' for member: {self.error_id}")
            id_code = erroneous
        else:
            logger.debug(f"Generating N1 segment")
        return f"N1*{self.entity_id_code}*{self.name}*FI*{id_code}~\n"


# Insured Benefit
class INS:
    def __init__(self, relationship):
        self.relationship = relationship

    def to_edi(self):
        logger.debug(f"Generating INS segment with relationship {self.relationship}")
        return f"INS*Y*{self.relationship}*001**A***AC~\n"


# Reference Identification
class REF:
    def __init__(self, qualifier, reference_id, error_ctrl):
        self.qualifier = qualifier
        self.reference_id = reference_id
        self.error_ctrl = error_ctrl

    def to_edi(self):
        return f"REF*{self.qualifier}*{self.reference_id}~\n"


# Organization Name
class NM1:
    def __init__(self, entity_id_code, entity_type, last_name=None, first_name=None, middle_name=None,
                 id_qualifier=None, id_code=None, error_ctrl=None, error_id=None):
        self.entity_id_code = entity_id_code
        self.entity_type = entity_type
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name
        self.id_qualifier = id_qualifier
        self.id_code = id_code
        self.error_ctrl = error_ctrl
        self.error_id = error_id

    def to_edi(self):
        id_code = self.id_code
        if self.error_ctrl and self.error_ctrl.should_insert():
            erroneous = self.error_ctrl.insert(id_code, "format")
            logger.warning(
                f"[ERROR INSERTED] NM1 segment: SSN '{id_code}' changed to '{erroneous}' for member: {self.error_id}")
            id_code = erroneous
        else:
            logger.debug(f"Generating NM1 segment for {self.last_name}, {self.first_name}")
        return (
            f"NM1*{self.entity_id_code}*{self.entity_type}*{self.last_name}*{self.first_name}*{self.middle_name}*"
            f"**{self.id_qualifier}*{id_code}~\n"
        )


# Administrative Communications Contact
class PER:
    def __init__(self, phone_number, error_ctrl, error_id):
        self.phone_number = phone_number
        self.error_ctrl = error_ctrl
        self.error_id = error_id

    def to_edi(self):
        phone_number = self.phone_number
        if self.error_ctrl and self.error_ctrl.should_insert():
            erroneous = self.error_ctrl.insert(phone_number, "missing")
            logger.warning(
                f"[ERROR INSERTED] PER segment: Phone '{phone_number}' changed to '{erroneous}' for member: {self.error_id}")
            phone_number = erroneous
        else:
            logger.debug("Generating PER segment")
        return f"PER*IP**TE*{phone_number}~\n"


# Address Information
class N3:
    def __init__(self, building_number, street, apartment: Optional[str] = None, error_ctrl=None, error_id=None):
        self.building_number = building_number
        self.street = street
        self.apartment = apartment if apartment else ""
        self.error_ctrl = error_ctrl
        self.error_id = error_id

    def to_edi(self):
        street = self.street
        if self.error_ctrl and self.error_ctrl.should_insert():
            erroneous = self.error_ctrl.insert(street, "invalid")
            logger.warning(
                f"[ERROR INSERTED] N3 segment: Street '{street}' changed to '{erroneous}' for member: {self.error_id}")
            street = erroneous
        else:
            logger.debug("Generating N3 segment")
        return f"N3*{self.building_number}{" "}{street}*{self.apartment}~\n"


# Location
class N4:
    def __init__(self, city, state, zipcode, error_ctrl, error_id):
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.error_ctrl = error_ctrl
        self.error_id = error_id

    def to_edi(self):
        city = self.city
        if self.error_ctrl and self.error_ctrl.should_insert():
            erroneous = self.error_ctrl.insert(city, "invalid")
            logger.warning(
                f"[ERROR INSERTED] N4 segment: City '{city}' changed to '{erroneous}' for member: {self.error_id}")
            city = erroneous
        else:
            logger.debug("Generating N4 segment")
        return f"N4*{city}*{self.state}*{self.zipcode}~\n"


# Monetary Amount
class AMT:
    def __init__(self, amount_qualifier_code, amount, error_ctrl, error_id):
        self.amount_qualifier_code = amount_qualifier_code
        self.amount = amount
        self.error_ctrl = error_ctrl
        self.error_id = error_id

    def to_edi(self):
        amount = self.amount
        if self.error_ctrl and self.error_ctrl.should_insert():
            erroneous = self.error_ctrl.insert(amount, "negative")
            logger.warning(
                f"[ERROR INSERTED] AMT segment: Amount '{amount}' changed to '{erroneous}' for member: {self.error_id}")
            amount = erroneous
        else:
            logger.debug(f"Generating AMT segment for code {self.amount_qualifier_code}")
        return f"AMT*{self.amount_qualifier_code}*{amount}~\n"


# Health Coverage
class HD:
    def __init__(self, maintenance_type_code="001", plan_coverage_description="MCVA1003"):
        self.maintenance_type_code = maintenance_type_code
        self.plan_coverage_description = plan_coverage_description

    def to_edi(self):
        logger.debug("Generating HD segment")
        return f"HD*{self.maintenance_type_code}**MM*{self.plan_coverage_description}~\n"


# Date/Time Period
class DTP:
    def __init__(self):
        now = datetime.now()
        self.date = now.strftime("%Y%m%d")

    def to_edi(self):
        logger.debug(f"Generating DTP segment for date {self.date}")
        return f"DTP*348*D8*{self.date}~\n"


class BHT:
    def __init__(self):
        now = datetime.now()
        self.date = now.strftime("%Y%m%d")
        self.time = now.strftime("%H%M")

    def to_edi(self):
        logger.debug(f"Generating BHT segment")
        # unsure of the value of BHT03
        return f"BHT*0022*13*123456789*{self.date}*{self.time}~\n"


class HL:
    def __init__(self, hl_id=None, hl_parent=None, hl_code=None, children=None, error_ctrl=None, error_id=None):
        self.hl_id = hl_id
        self.hl_parent = hl_parent
        self.hl_code = hl_code
        self.children = children
        self.error_ctrl = error_ctrl
        self.error_id = error_id

    def to_edi(self):
        hl_code = self.hl_code
        if self.error_ctrl and self.error_ctrl.should_insert():
            hl_code = self.error_ctrl.insert(hl_code, "missing")
            logger.warning(
                f"[ERROR INSERTED] HL segment: HL Code changed to '{hl_code}' for member: {self.error_id}"
            )
        else:
            logger.debug(f"Generating HL {hl_code} segment")
        return f"HL*{self.hl_id}*{self.hl_parent}*{hl_code}*{self.children}~\n"


class EQ:
    def __init__(self, service_code):
        self.service_code = service_code

    def to_edi(self):
        logger.debug(f"Generating EQ segment")
        return f"EQ*{self.service_code}~\n"
