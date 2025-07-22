"""
Each class is its own EDI segment
"""
from datetime import datetime
from typing import Optional

from Config import Config
from Config.Config import logger


class EDISegment:
    def __init__(self, nl_toggle=True):
        self.nl_toggle = nl_toggle

    def get_nl(self):
        return "~\n" if self.nl_toggle else "~"


# File Header
class ISA(EDISegment):
    def __init__(self, sender=Config.SENDER_ID, receiver=Config.RECEIVER_ID, nl_toggle=True):
        super().__init__(nl_toggle)
        now = datetime.now()
        self.sender = sender
        self.receiver = receiver
        self.id_qualifier = "ZZ"
        self.interCtrlNumber = now.strftime("%Y%m%d1")
        self.date = now.strftime("%y%m%d")
        self.time = now.strftime("%H%M")
        self.nl_toggle = nl_toggle

    def to_edi(self):
        nl = "~\n" if self.nl_toggle else "~"
        logger.debug("Generating ISA segment")
        return (
            f"ISA*00*          *00*          *{self.id_qualifier}*{self.sender:<15}*{self.id_qualifier}*"
            f"{self.receiver:<15}*{self.date}*{self.time}*$*00501*{self.interCtrlNumber}*0*T*:{nl}")


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
    def __init__(self, functional_id, sender=Config.SENDER_ID, receiver=Config.RECEIVER_ID, nl_toggle=True):
        now = datetime.now()
        self.functional_id = functional_id
        self.sender = sender
        self.receiver = receiver
        self.date = now.strftime("%Y%m%d")
        self.time = now.strftime("%H%M%S")
        self.nl_toggle = nl_toggle

    def to_edi(self):
        logger.debug("Generating GS segment")
        nl = "~\n" if self.nl_toggle else "~"
        segment = f"GS*{self.functional_id}*{self.sender}*{self.receiver}*{self.date}*{self.time}*61*X"
        match self.functional_id:
            case "HS":
                segment += "*005010X279A1"
            case "HC":
                segment += "*005010X222A2"
            case "HN":
                segment += "*005010X214"
            case "HP":
                segment += "*005010X221A1"
            case "BE":
                segment += "*005010X220A1"
            case "FA":
                segment += "*005010X231"
            case _:
                logger.warning(f"Unknown functional ID: {self.functional_id} in GS segment")
        return segment + nl


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
        segment = f"ST*{self.file_type}*{self.num:06}"
        match self.file_type:
            case "270":
                segment += "*005010X279A1"
            case "837":
                segment += "*005010X222A2"
            case "277":
                segment += "*005010X214"
            case "835":
                pass
            case "834":
                segment += "*005010X220A1"
            case "999":
                segment += "*005010X231"
            case _:
                logger.warning(f"Unknown file type: {self.file_type} in ST segment")
        return segment + "~\n"


# Transaction Set Trailer
class SE:
    def __init__(self, segment_count, control_num):
        self.segment_count = segment_count
        self.control_num = f"{control_num:06}"

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
    def __init__(self, entity_id_code, name, id_code_qualifier, id_code, error_ctrl, error_id):
        self.entity_id_code = entity_id_code
        self.name = name
        self.id_code_qualifier = id_code_qualifier
        self.id_code = id_code
        self.error_ctrl = error_ctrl
        self.error_id = error_id

    def to_edi(self):
        id_code = self.id_code
        if self.error_ctrl and self.error_ctrl.should_insert():
            erroneous = self.error_ctrl.insert(id_code, "missing")
            logger.warning(
                f"[ERROR INSERTED] N1 segment: ID code '{id_code}' changed to '{erroneous}' for member: {self.error_id}"
            )
            id_code = erroneous
        else:
            logger.debug("Generating N1 segment")
        return f"N1*{self.entity_id_code}*{self.name}*{self.id_code_qualifier}*{id_code}~\n"


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

        qualifier_desc = {
            "34": "SSN",
            "XX": "NPI",
            "MI": "Member ID",
            "PI": "Payer ID",
            "41": "Submitter"
        }.get(self.id_qualifier, "ID code")

        if self.error_ctrl and self.error_ctrl.should_insert():
            erroneous = self.error_ctrl.insert(id_code, "format")
            logger.warning(
                f"[ERROR INSERTED] NM1 segment: {qualifier_desc} '{id_code}' changed to '{erroneous}' for member: "
                f"{self.error_id}")
            id_code = erroneous
        else:
            logger.debug(f"Generating NM1 segment for {self.last_name}, {self.first_name}")
        return (
            f"NM1*{self.entity_id_code}*{self.entity_type}*{self.last_name}*{self.first_name}*{self.middle_name}*"
            f"**{self.id_qualifier}*{id_code}~\n"
        )


# Administrative Communications Contact
class PER:
    def __init__(self, contact_func, phone_number, error_ctrl, error_id):
        self.contact_func = contact_func
        self.phone_number = phone_number
        self.error_ctrl = error_ctrl
        self.error_id = error_id

    def to_edi(self):
        phone_number = self.phone_number
        if self.error_ctrl and self.error_ctrl.should_insert():
            erroneous = self.error_ctrl.insert(phone_number, "missing")
            logger.warning(
                f"[ERROR INSERTED] PER segment: Phone '{phone_number}' changed to '{erroneous}' for member: "
                f"{self.error_id}")
            phone_number = erroneous
        else:
            logger.debug("Generating PER segment")
        return f"PER*{self.contact_func}**TE*{phone_number}~\n"


# Address Information
class N3:
    def __init__(self, building_number, street, apartment: Optional[str] = None, error_ctrl=None,
                 error_id=None, npi=False):
        self.building_number = building_number
        self.street = street
        self.apartment = apartment if apartment else ""
        self.error_ctrl = error_ctrl
        self.error_id = error_id
        self.npi = npi

    def to_edi(self):
        street = self.street
        if self.error_ctrl and self.error_ctrl.should_insert():
            erroneous = self.error_ctrl.insert(street, "invalid")
            logger.warning(
                f"[ERROR INSERTED] N3 segment: Street '{street}' changed to '{erroneous}' for member: {self.error_id}")
            street = erroneous
        else:
            logger.debug("Generating N3 segment")
        if self.npi:
            return f"N3*{self.building_number}*{street}~\n"
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
    def __init__(self, date_type, date_format):
        now = datetime.now()
        self.date_type = date_type
        self.date_format = date_format
        self.date = now.strftime("%Y%m%d")

    def to_edi(self):
        logger.debug(f"Generating DTP segment for date {self.date}")
        return f"DTP*{self.date_type}*{self.date_format}*{self.date}~\n"


class BHT:
    def __init__(self, transaction_id, purpose_code, unique_id, file_type=None):
        now = datetime.now()
        self.file_type = file_type
        self.transaction_id = transaction_id
        self.purpose_code = purpose_code
        self.unique_id = unique_id
        self.date = now.strftime("%Y%m%d")
        self.time = now.strftime("%H%M")

    def to_edi(self):
        logger.debug("Generating BHT segment")
        segment = f"BHT*00{self.transaction_id}*{self.purpose_code}*{self.unique_id}*{self.date}*{self.time}"
        if self.file_type == "837":
            segment += "*CH"
        elif self.file_type == "277CA":
            segment += "*TH"
        return segment + "~\n"


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
        segment = f"HL*{self.hl_id}*{self.hl_parent}*{hl_code}"
        if self.children is not None:
            segment += f"*{self.children}"

        return segment + "~\n"


class EQ:
    def __init__(self, service_code):
        self.service_code = service_code

    def to_edi(self):
        logger.debug("Generating EQ segment")
        return f"EQ*{self.service_code}~\n"


class SBR:
    def __init__(self, relationship_code, group_id):
        self.relationship_code = relationship_code
        self.group_id = group_id

    def to_edi(self):
        logger.debug(f"Generating SBR with relationship {self.relationship_code} segment")
        return f"SBR*P*{self.relationship_code}*{self.group_id}******HM~\n"


class DMG:
    def __init__(self, dob, gender):
        self.dob = dob
        self.gender = gender

    def to_edi(self):
        logger.debug("Generating DMG segment")
        return f"DMG*D8*{self.dob}*{self.gender}~\n"


class CLM:
    def __init__(self, claim_id, charge_amt, place_of_service, fac_code_qual, claim_freq):
        self.claim_id = claim_id
        self.charge_amt = charge_amt
        self.place_of_service = place_of_service
        self.fac_code_qual = fac_code_qual
        self.claim_freq = claim_freq

    def to_edi(self):
        logger.debug("Generating CLM segment")
        return (f"CLM*{self.claim_id}*{self.charge_amt}***{self.place_of_service}:"
                f"{self.fac_code_qual}:{self.claim_freq}*Y*A*Y*Y~\n")


class HI:
    def __init__(self, qualifier, code):
        self.qualifier = qualifier
        self.code = code

    def to_edi(self):
        logger.debug("Generating HI segment")
        return f"HI*{self.qualifier}:{self.code}~\n"


class PRV:
    def __init__(self, provider_code, ref_type, taxonomy):
        self.provider_code = provider_code
        self.ref_type = ref_type
        self.taxonomy = taxonomy

    def to_edi(self):
        logger.debug("Generating PRV segment")
        return f"PRV*{self.provider_code}*{self.ref_type}*{self.taxonomy}~\n"


class LX:
    def __init__(self, number):
        self.number = number

    def to_edi(self):
        logger.debug(f"Generating LX segment line {self.number}")
        return f"LX*{self.number:04}~\n"


class SV1:
    def __init__(self, proc_code, charge_amt, unit, quantity, diagnosis_ptr):
        self.proc_code = proc_code
        self.charge_amt = charge_amt
        self.unit = unit
        self.quantity = quantity
        self.diagnosis_ptr = diagnosis_ptr

    def to_edi(self):
        logger.debug("Generating SV1 segment")
        return f"SV1*{self.proc_code}*{self.charge_amt}*{self.unit}*{self.quantity}***{self.diagnosis_ptr}~\n"


class PAT:
    def __init__(self, bene_relationship):
        self.bene_relationship = bene_relationship

    def to_edi(self):
        logger.debug("Generating PAT segment")
        return f"PAT*{self.bene_relationship}~\n"


class TRN:
    def __init__(self, trace_code, ref_id, payer_id=None, error_ctrl=None, error_id=None):
        self.trace_code = trace_code
        self.ref_id = ref_id
        self.payer_id = payer_id
        self.error_ctrl = error_ctrl
        self.error_id = error_id

    def to_edi(self):
        ref_id = self.ref_id
        if self.error_ctrl and self.error_ctrl.should_insert():
            ref_id = self.error_ctrl.insert(ref_id, "missing")
            logger.warning(
                f"[ERROR INSERTED] TRN segment: reference ID changed to '{ref_id}' for member: {self.error_id}")
        else:
            logger.debug("Generating TRN segment")
        segment = f"TRN*{self.trace_code}*{ref_id}"
        if self.payer_id is not None:
            segment += f"*1{self.payer_id}"

        return segment + "~\n"


class STC:
    def __init__(self, status_info, action_code, units, error_ctrl, error_id):
        now = datetime.now()
        self.status_info = status_info
        self.action_code = action_code
        self.date = now.strftime("%Y%m%d")
        self.units = units
        self.error_ctrl = error_ctrl
        self.error_id = error_id

    def to_edi(self):
        status_info = self.status_info
        if self.error_ctrl and self.error_ctrl.should_insert():
            status_info = self.error_ctrl.insert(status_info, "format")
            logger.warning(
                f"[ERROR INSERTED] STC segment: status info changed to '{status_info}' for member: {self.error_id}")
        else:
            logger.debug("Generating STC segment")

        return f"STC*{status_info}*{self.date}*{self.action_code}*{self.units}~\n"


class SVC:
    def __init__(self, proc_code, charge_amt, quantity, unit, diagnosis_ptr):
        now = datetime.now()
        self.proc_code = proc_code
        self.charge_amt = charge_amt
        self.unit = unit
        self.quantity = quantity
        self.diagnosis_ptr = diagnosis_ptr
        self.date = now.strftime("%Y%m%d")

    def to_edi(self):
        logger.debug("Generating SVC segment")
        return f"SVC*{self.proc_code}*{self.charge_amt}*{self.quantity}*{self.unit}*{self.diagnosis_ptr}~\n"


class BPR:
    def __init__(self, transaction_handling_code, amt, credit_debit_code, payment_method):
        now = datetime.now()
        self.transaction_handling_code = transaction_handling_code
        self.amt = amt
        self.credit_debit_code = credit_debit_code
        self.payment_method = payment_method
        self.date = now.strftime("%Y%m%d")

    def to_edi(self):
        logger.debug("Generating BPR segment")
        return (f"BPR*{self.transaction_handling_code}*{self.amt}*{self.credit_debit_code}*{self.payment_method}******"
                f"******{self.date}~\n")


class CLP:
    def __init__(self, claim_id, claim_status, total_amt, paid_amt, filing_code, ctrl_num):
        self.claim_id = claim_id
        self.claim_status = claim_status
        self.total_amt = total_amt
        self.paid_amt = paid_amt
        self.filing_code = filing_code
        self.ctrl_num = ctrl_num

    def to_edi(self):
        logger.debug("Generating CLP segment")
        return (f"CLP*{self.claim_id}*{self.claim_status}*{self.total_amt}*{self.paid_amt}**{self.filing_code}*"
                f"{self.ctrl_num}~\n")


class AK1:
    def __init__(self, functional_id, group_ctrl_num):
        self.group_ctrl_num = group_ctrl_num
        self.functional_id = functional_id

    def to_edi(self):
        logger.debug("Generating AK1 segment")
        segment = f"AK1*{self.functional_id}*{self.group_ctrl_num:06}"

        match self.functional_id:
            case "HC":
                segment += "*005010X222A1"
            case "BE":
                segment += "*005010X220A1"
            case _:
                logger.warning(f"Unknown functional id: {self.functional_id} in AK1 segment")

        return segment + "~\n"


class AK9:
    def __init__(self, functional_code, number_sets, number_received, number_accepted):
        self.functional_code = functional_code
        self.number_sets = number_sets
        self.number_received = number_received
        self.number_accepted = number_accepted

    def to_edi(self):
        logger.debug("Generating AK9 segment")
        return f"AK9*{self.functional_code}*{self.number_sets}*{self.number_received}*{self.number_accepted}~\n"
