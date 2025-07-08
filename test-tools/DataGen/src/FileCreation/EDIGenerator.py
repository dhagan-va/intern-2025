import uuid
from datetime import date, timedelta

import FileCreation.EDISegments as Seg
from Config import Config
from Config.Config import logger
from Config.Data_Visualizer import log_data
from FileCreation.ErrorInjector import ErrorInjector


class EDI270Generator:
    def __init__(self, transaction_funcs, num_messages=None, error_rate=None):
        self.transaction_funcs = transaction_funcs
        self.claims = self.transaction_funcs.get_claim_transactions(
            status="Created",
            date=date.today().isoformat()
        )
        self.num_messages = len(self.claims)
        self.error_ctrl = ErrorInjector(num_messages, error_rate)
        logger.info(f"Initializing EDI270Generator with {self.num_messages} claims")

    @staticmethod
    def split_provider_name(name, entity_type):
        if entity_type == "2":
            return name, ""

        parts = name.replace(",", "").split()

        if len(parts) == 1:
            return parts[0], ""
        else:
            return parts[0], parts[1]

    def create_transaction(self, num, error_ctrl):
        if num - 1 >= len(self.claims) or num <= 0:
            logger.error(f"Index out of range for claim {num}")
            return

        self.error_ctrl.reset_error_inserted()
        claim = self.claims[num - 1]
        last, first = self.split_provider_name(claim.provider_name, claim.provider_entity_type)
        error_id = claim.beneficiary_id
        bene = self.transaction_funcs.family_db.get_beneficiary(claim.sponsor_id, claim.beneficiary_id)

        segments = [Seg.ISA().to_edi(),
                    Seg.GS("HS").to_edi(),
                    Seg.ST(270, num).to_edi(),
                    Seg.BHT("22", "13").to_edi(),
                    Seg.HL(1, "", 20, 1, error_ctrl, error_id).to_edi(),
                    Seg.NM1("PR", 2, Config.PAYER_QUALIFIER, "", "", "PI",
                            Config.PAYER_ID, error_ctrl, error_id).to_edi(),
                    Seg.HL(2, 1, 21, 1, error_ctrl, error_id).to_edi(),
                    Seg.NM1("1P", claim.provider_entity_type, last, first, "", "XX", claim.provider_npi, error_ctrl,
                            error_id).to_edi(),
                    Seg.HL(3, 2, 22, 0, error_ctrl, error_id).to_edi(),
                    Seg.NM1("IL", "1", bene.last_name, bene.first_name,
                            bene.middle_name, "MI", bene.beneficiary_id, error_ctrl, error_id).to_edi(),
                    Seg.EQ("30").to_edi(),
                    Seg.SE(10, num).to_edi(),
                    Seg.GE(1).to_edi(),
                    Seg.IEA().to_edi()
                    ]

        if self.error_ctrl.error_inserted is True:
            log_data["errors"]["error_ct_270"] += 1
            logger.warning(f"Error added in Message {num}")
        return segments

    def combine_segments(self):
        all_segments = []
        for i in range(1, self.num_messages + 1):
            all_segments.extend(self.create_transaction(i, self.error_ctrl))

        claim_ids = [claim.claim_id for claim in self.claims]
        self.transaction_funcs.update_claims_status(claim_ids, "270 Created")
        return all_segments


class EDI837PGenerator:
    def __init__(self, transaction_funcs, relationship_map=Config.RELATIONSHIP_MAP, error_rate=None):
        self.transaction_funcs = transaction_funcs
        self.relationship_map = relationship_map
        self.transaction_control_number = 1
        yesterday = date.today() - timedelta(days=1)
        self.claims = self.transaction_funcs.get_claim_transactions(
            status="270 Created",
            date=yesterday.isoformat()
        )
        self.num_messages = len(self.claims)
        self.error_ctrl = ErrorInjector(self.num_messages, error_rate)

        logger.info(f"Initializing EDI837PGenerator with {self.num_messages} claims")

    def get_num_messages(self):
        return self.num_messages

    @staticmethod
    def split_provider_name(name, entity_type):
        if entity_type == "2":
            return name, ""

        parts = name.replace(",", "").split()

        if len(parts) == 1:
            return parts[0], ""
        else:
            return parts[0], parts[1]

    def create_claim_anesthesia(self, num, error_ctrl):
        if num - 1 >= len(self.claims) or num <= 0:
            logger.error(f"Index out of range for claim {num}")
            return

        claim = self.claims[num - 1]
        bene = self.transaction_funcs.family_db.get_beneficiary(claim.sponsor_id, claim.beneficiary_id)
        sponsor = self.transaction_funcs.family_db.get_sponsor_by_id(claim.sponsor_id)
        last, first = self.split_provider_name(claim.provider_name, claim.provider_entity_type)
        bene_relationship = self.relationship_map.get(bene.relationship)
        error_id = bene.beneficiary_id

        if bene_relationship == "25" or bene_relationship == "26":
            bene_relationship = "G8"

        segments = [Seg.ST("837", num).to_edi(),
                    Seg.BHT("19", "00", "837").to_edi(),
                    Seg.NM1("41", "2", "Submitter Group",
                            "", "", "46", "133052274", error_ctrl).to_edi(),
                    Seg.PER("IC", "2403018701", error_ctrl, error_id).to_edi(),
                    Seg.NM1("40", "2", "Receiver Group", "", "", "46", "84146", error_ctrl).to_edi(),
                    Seg.HL("1", "", 20, 1, error_ctrl, error_id).to_edi(),
                    Seg.NM1("85", claim.provider_entity_type, last, first, "", "XX", claim.provider_npi, error_ctrl,
                            error_id).to_edi(),
                    Seg.N3(claim.provider_address_1, claim.provider_address_2, "", error_ctrl, error_id,
                           True).to_edi(),
                    Seg.N4(claim.provider_city, claim.provider_state, claim.provider_zip, error_ctrl,
                           error_id).to_edi(),
                    Seg.REF("EI", "123456789", error_ctrl).to_edi(),
                    Seg.HL("2", "1", 22, 1, error_ctrl, error_id).to_edi(),
                    # add SBR for bene
                    Seg.SBR("18", "123456").to_edi(),
                    Seg.NM1("IL", "1", sponsor.last_name, sponsor.first_name, sponsor.middle_name,
                            "MI", sponsor.sponsor_id, error_ctrl).to_edi(),
                    Seg.N3(sponsor.address.building_number, sponsor.address.street, sponsor.address.apartment,
                           error_ctrl).to_edi(),
                    Seg.N4(sponsor.address.city, sponsor.address.state, sponsor.address.zipcode, error_ctrl,
                           error_id).to_edi(),
                    Seg.DMG(sponsor.dob.strftime("%Y%m%d"), sponsor.gender).to_edi(),
                    Seg.NM1("PR", 2, Config.PAYER_QUALIFIER, "", "", "PI",
                            Config.PAYER_ID, error_ctrl, error_id).to_edi(),
                    Seg.N3("123", "Payer Ave").to_edi(),
                    Seg.N4("Payer City", "MD", "99999", error_ctrl, error_id).to_edi(),
                    Seg.HL("3", "2", 23, 0, error_ctrl, error_id).to_edi(),
                    Seg.PAT(bene_relationship).to_edi(),
                    Seg.NM1("QC", "1", bene.last_name, bene.first_name, bene.middle_name, "MI",
                            bene.beneficiary_id, error_ctrl).to_edi(),
                    Seg.N3(bene.address.building_number, bene.address.street, bene.address.apartment, error_ctrl,
                           error_id).to_edi(),
                    Seg.N4(bene.address.city, bene.address.state, bene.address.zipcode, error_ctrl, error_id).to_edi(),
                    Seg.DMG(bene.dob.strftime("%Y%m%d"), bene.gender).to_edi(),
                    Seg.CLM(claim.claim_id, "827", "22", "B", "1").to_edi(),
                    Seg.REF("D9", claim.claim_id, error_ctrl).to_edi(),
                    Seg.HI("BK", "36616").to_edi(),
                    Seg.NM1("82", "1", last, first, "", "XX", claim.provider_npi, error_ctrl).to_edi(),
                    Seg.PRV("PE", "PXC", "207L00000X").to_edi(),
                    Seg.LX("1").to_edi(),
                    Seg.SV1("HC:00142:QK:QS:P1", "827", "MJ", "61", 1).to_edi(),
                    Seg.DTP("472", "D8").to_edi(),
                    ]

        segments.append(Seg.SE(len(segments) + 1, self.transaction_control_number).to_edi())

        self.transaction_control_number += 1
        return segments

    def combine_segments(self):
        all_segments = [Seg.ISA().to_edi(),
                        Seg.GS("HC", Config.SENDER_ID, Config.RECEIVER_ID, "005010X222A1").to_edi()
                        ]

        for i in range(1, self.num_messages + 1):
            all_segments.extend(self.create_claim_anesthesia(i, self.error_ctrl))

        all_segments.append(Seg.GE(self.num_messages).to_edi())
        all_segments.append(Seg.IEA().to_edi())

        claim_ids = [claim.claim_id for claim in self.claims]
        self.transaction_funcs.update_claims_status(claim_ids, "837 Created")
        return all_segments


class EDI277CAGenerator:
    def __init__(self, transaction_funcs, error_rate=None):
        self.transaction_funcs = transaction_funcs
        yesterday = date.today() - timedelta(days=1)
        self.claims = self.transaction_funcs.get_claim_transactions(
            status="837 Created",
            date=yesterday
        )
        self.num_messages = len(self.claims)
        self.error_ctrl = ErrorInjector(self.num_messages, error_rate)

    def get_num_messages(self):
        return self.num_messages

    def create_transaction(self, num, error_ctrl):
        if num - 1 >= len(self.claims) or num <= 0:
            logger.error(f"Index out of range for claim {num}")
            return

        self.error_ctrl.reset_error_inserted()
        claim = self.claims[num - 1]
        error_id = claim.beneficiary_id
        bene = self.transaction_funcs.family_db.get_beneficiary(claim.sponsor_id, claim.beneficiary_id)
        payer_claim_id = f"PAYER{claim.claim_id[-4:]}"

        segments = [Seg.ISA().to_edi(),
                    Seg.GS("HN", Config.SENDER_ID, Config.RECEIVER_ID).to_edi(),
                    Seg.ST("277", num).to_edi(),
                    Seg.BHT("19", "00").to_edi(),
                    Seg.HL("1", "", 20, 1).to_edi(),
                    Seg.NM1("41", "2", "Receiver Org", "", "", "46", Config.SENDER_ID, error_ctrl).to_edi(),
                    Seg.HL("2", "1", 21, 1).to_edi(),
                    Seg.
                    Seg.GE(1).to_edi(),
                    Seg.IEA().to_edi()
                    ]

        return segments

    def combine_segments(self):
        all_segments = []
        for i in range(1, self.num_messages + 1):
            all_segments.extend(self.create_transaction(i, self.error_ctrl))

        claim_ids = [claim.claim_id for claim in self.claims]
        self.transaction_funcs.update_claims_status(claim_ids, "277CA Created")
        return all_segments


class EDI834Generator:
    def __init__(self, transaction_funcs, sender=Config.SENDER_ID, receiver=Config.RECEIVER_ID,
                 relationship_map=Config.RELATIONSHIP_MAP, error_rate=None):
        self.transaction_funcs = transaction_funcs
        self.sender = sender
        self.receiver = receiver
        self.relationship_map = relationship_map
        week_before = date.today() - timedelta(days=7)
        # Change to 835 Created after EDI835Generator is created
        self.claims = self.transaction_funcs.get_claim_transactions(
            status="837 Created",
            date=week_before.isoformat()
        )
        self.transaction_control_number = 0
        self.num_messages = len(self.claims)
        self.error_ctrl = ErrorInjector(self.num_messages, error_rate)
        logger.debug(f"Initialized EDI834Generator")

    def get_num_messages(self):
        return self.num_messages

    def create_member(self, bene, error_ctrl):
        self.transaction_control_number += 1
        self.error_ctrl.reset_error_inserted()
        sponsor = self.transaction_funcs.family_db.get_sponsor_by_id(bene.sponsor_id)
        relationship_code = self.relationship_map.get(bene.relationship)
        error_id = bene.beneficiary_id

        segments = [Seg.ST(834, self.transaction_control_number).to_edi(),
                    Seg.BGN(uuid.uuid4().hex.upper()).to_edi(),
                    Seg.N1("P5", Config.SPONSOR_QUALIFIER, Config.SPONSOR_ID, error_ctrl,
                           error_id).to_edi(),
                    Seg.N1("IN", Config.PAYER_QUALIFIER, Config.PAYER_ID, error_ctrl, error_id).to_edi(),
                    Seg.INS(relationship_code).to_edi(),
                    Seg.REF("0F", sponsor.sponsor_id, error_ctrl).to_edi(),
                    Seg.REF("6O", bene.beneficiary_id, error_ctrl).to_edi(),
                    Seg.NM1("IL", "1", bene.last_name, bene.first_name, bene.middle_name, "34", bene.ssn,
                            error_ctrl, error_id).to_edi(),
                    Seg.PER("IP", bene.phone, error_ctrl, error_id).to_edi(),
                    Seg.N3(bene.address.building_number, bene.address.street, bene.address.apartment,
                           error_ctrl, error_id).to_edi(),
                    Seg.N4(bene.address.city, bene.address.state, bene.address.zipcode, error_ctrl,
                           error_id).to_edi()
                    ]

        for code, value in bene.deductibles.items():
            segments.append(Seg.AMT(code, str(value), error_ctrl, error_id).to_edi())
            log_data["amt"][f"{code}"]["sum"] += value
            log_data["amt"][f"{code}"]["count"] += 1
        for code, value in bene.visit_counts.items():
            segments.append(Seg.AMT(code, str(value), error_ctrl, error_id).to_edi())
            log_data["amt"][f"{code}"]["sum"] += value
            log_data["amt"][f"{code}"]["count"] += 1

        segments += [Seg.HD().to_edi(),
                     Seg.DTP(348, "D8").to_edi(),
                     Seg.SE(len(segments) + 3, self.transaction_control_number).to_edi()
                     ]

        if self.error_ctrl.error_inserted is True:
            log_data["errors"]["error_ct_834"] += 1
        logger.debug(f"Completed {len(segments)} segments for member {bene.beneficiary_id}")
        return segments

    def combine_segments(self):
        logger.debug(f"Starting EDI 834 generation for {self.num_messages} beneficiaries")
        all_segments = [Seg.ISA().to_edi(),
                        Seg.GS("BE").to_edi()
                        ]

        for claim in self.claims:
            bene = self.transaction_funcs.family_db.get_beneficiary(claim.sponsor_id, claim.beneficiary_id)
            log_data["family"]["size"] += 1
            all_segments.extend(self.create_member(bene, self.error_ctrl))

        log_data["family"]["count"] = len(self.claims)

        all_segments.append(Seg.GE(self.transaction_control_number).to_edi())
        all_segments.append(Seg.IEA().to_edi())

        logger.info(f"Generated total of {self.transaction_control_number} transactions")
        logger.info(f"There were {self.error_ctrl.error_count} errors")
        return all_segments
