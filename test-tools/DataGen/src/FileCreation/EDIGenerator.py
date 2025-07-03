import uuid

from datetime import date
import FileCreation.EDISegments as Seg
from Config import Config
from Config.Config import logger
from Config.Data_Visualizer import log_data
from FileCreation.ErrorInjector import ErrorInjector


class EDI270Generator:
    def __init__(self, transaction_funcs, num_messages=None, error_rate=None):
        self.transaction_funcs = transaction_funcs
        self.claims = self.transaction_funcs.get_claim_transactions(
            status="created",
            date=date.today().isoformat()
        )
        self.num_messages = num_messages
        self.error_ctrl = ErrorInjector(num_messages, error_rate)
        logger.info(f"Initializing EDI270Generator with {len(self.claims)} claims")

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
                    Seg.NM1("PR", 2, Config.N1_PAYER_QUALIFIER, "", "", "PI",
                            Config.N1_PAYER_ID, error_ctrl, error_id).to_edi(),
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
        return segments

    def combine_segments(self):
        all_segments = []
        for i in range(1, self.num_messages + 1):
            all_segments.extend(self.create_transaction(i, self.error_ctrl))
        return all_segments


class EDI837PGenerator:
    def __init__(self, beneficiaries, providers, relationship_map=Config.RELATIONSHIP_MAP, num_messages=None,
                 error_rate=None):
        self.beneficiaries = beneficiaries
        self.providers = providers
        self.relationship_map = relationship_map
        self.transaction_control_number = 1
        self.num_messages = num_messages
        self.error_ctrl = ErrorInjector(num_messages, error_rate)

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
        if num - 1 >= len(self.beneficiaries) or num - 1 >= len(self.providers) or num - 1 < 0:
            logger.error(f"Index out of bounds for claim {num}. Beneficiaries or providers list is too short.")
            return []

        bene = self.beneficiaries[num - 1]
        provider = self.providers[num - 1]
        last, first = self.split_provider_name(provider["name"], provider["entity_type"])
        bene_relationship = self.relationship_map.get(bene.relationship)
        error_id = bene.beneficiary_id

        segments = [Seg.ST("837", num).to_edi(),
                    Seg.BHT("19", "00").to_edi(),
                    Seg.NM1("41", "2", "Submitter Group",
                            "", "", "46", "133052274", error_ctrl).to_edi(),
                    Seg.PER("IC", "2403018701", error_ctrl, error_id).to_edi(),
                    Seg.NM1("40", "2", "Receiver Group", "", "", "46", "84146", error_ctrl).to_edi(),
                    Seg.HL("1", "", 20, 1, error_ctrl, error_id).to_edi(),
                    Seg.NM1("85", provider["entity_type"], last, first, "", "XX", provider["npi"], error_ctrl,
                            error_id).to_edi(),
                    Seg.N3(provider.get("address_line_1", "Random Street"),
                           provider.get("address_line_2", "Random Apt"), "", error_ctrl, error_id).to_edi(),
                    Seg.N4(provider.get("city", "Random City"), provider.get("state", "Random State"),
                           provider.get("zipcode", "12345"), error_ctrl, error_id).to_edi(),
                    Seg.REF("EI", "123456789", error_ctrl).to_edi(),
                    Seg.HL("2", "1", 22, 1, error_ctrl, error_id).to_edi(),
                    Seg.SBR("18", "123456").to_edi(),
                    Seg.NM1("IL", "1", bene.last_name, bene.first_name, bene.middle_name,
                            "MI", bene.beneficiary_id, error_ctrl).to_edi(),
                    Seg.N3(bene.address.building_number, bene.address.street, bene.address.apartment,
                           error_ctrl).to_edi(),
                    Seg.N4(bene.address.city, bene.address.state, bene.address.zipcode, error_ctrl, error_id).to_edi(),
                    Seg.DMG(bene.dob.strftime("%Y%m%d"), bene.gender).to_edi(),
                    Seg.NM1("PR", 2, Config.N1_PAYER_QUALIFIER, "", "", "PI",
                            Config.N1_PAYER_ID, error_ctrl, error_id).to_edi(),
                    Seg.CLM("CLAIM2003", "827", "22", "B", "1").to_edi(),
                    Seg.HI("BK", "36616").to_edi(),
                    Seg.NM1("82", "1", last, first, "", "XX", provider["npi"], error_ctrl).to_edi(),
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

        all_segments.append(Seg.GE(self.transaction_control_number).to_edi())
        all_segments.append(Seg.IEA().to_edi())

        return all_segments


class EDI834Generator:
    def __init__(self, sender=Config.SENDER_ID, receiver=Config.RECEIVER_ID, relationship_map=Config.RELATIONSHIP_MAP,
                 num_messages=None, error_rate=None):
        self.sender = sender
        self.receiver = receiver
        self.relationship_map = relationship_map
        self.transaction_control_number = 0
        self.num_messages = num_messages
        self.error_ctrl = ErrorInjector(num_messages, error_rate)
        logger.debug(f"Initialized EDI834Generator")

    def create_member(self, member, error_ctrl):
        self.transaction_control_number += 1
        self.error_ctrl.reset_error_inserted()
        sponsor_id = member.sponsor_id
        relationship_code = self.relationship_map.get(member.relationship)
        beneficiary_id = member.beneficiary_id
        logger.debug(f"Creating segments for Beneficiary: {beneficiary_id} under Sponsor: {sponsor_id}")

        segments = [Seg.ST(834, self.transaction_control_number).to_edi(),
                    Seg.BGN(uuid.uuid4().hex.upper()).to_edi(),
                    Seg.N1("P5", Config.N1_SPONSOR_QUALIFIER, Config.N1_SPONSOR_ID, error_ctrl,
                           beneficiary_id).to_edi(),
                    Seg.N1("IN", Config.N1_PAYER_QUALIFIER, Config.N1_PAYER_ID, error_ctrl, beneficiary_id).to_edi(),
                    Seg.INS(relationship_code).to_edi(),
                    Seg.REF("0F", sponsor_id, error_ctrl).to_edi(),
                    Seg.REF("6O", beneficiary_id, error_ctrl).to_edi(),
                    Seg.NM1("IL", "1", member.last_name, member.first_name, member.middle_name, "34", member.ssn,
                            error_ctrl, beneficiary_id).to_edi(),
                    Seg.PER("IP", member.phone, error_ctrl, beneficiary_id).to_edi(),
                    Seg.N3(member.address.building_number, member.address.street, member.address.apartment,
                           error_ctrl, beneficiary_id).to_edi(),
                    Seg.N4(member.address.city, member.address.state, member.address.zipcode, error_ctrl,
                           beneficiary_id).to_edi()
                    ]

        for code, value in member.deductibles.items():
            segments.append(Seg.AMT(code, str(value), error_ctrl, beneficiary_id).to_edi())
            log_data["amt"][f"{code}"]["sum"] += value
            log_data["amt"][f"{code}"]["count"] += 1
        for code, value in member.visit_counts.items():
            segments.append(Seg.AMT(code, str(value), error_ctrl, beneficiary_id).to_edi())
            log_data["amt"][f"{code}"]["sum"] += value
            log_data["amt"][f"{code}"]["count"] += 1

        segments += [Seg.HD().to_edi(),
                     Seg.DTP(348, "D8").to_edi(),
                     Seg.SE(len(segments) + 3, self.transaction_control_number).to_edi()
                     ]

        if self.error_ctrl.error_inserted is True:
            log_data["errors"]["error_ct_834"] += 1
        logger.debug(f"Completed {len(segments)} segments for member {beneficiary_id}")
        return segments

    def create_transaction(self, sponsor):
        logger.debug(
            f"Generating  {len(sponsor.beneficiaries)} transactions for beneficiaries of Sponsor: {sponsor.sponsor_id}")

        segments = []
        for beneficiary in sponsor.beneficiaries:
            segments.extend(self.create_member(beneficiary, self.error_ctrl))
        return segments

    def combine_segments(self, sponsors):
        logger.debug(f"Starting EDI 834 generation for {len(list(sponsors))} sponsors")
        all_segments = [Seg.ISA().to_edi(),
                        Seg.GS("BE").to_edi()
                        ]

        for sponsor in sponsors:
            logger.debug(f"Sponsor {sponsor.sponsor_id} has {len(sponsor.beneficiaries)} beneficiaries")
            log_data["family"]["size"] += len(sponsor.beneficiaries)
            all_segments.extend(self.create_transaction(sponsor))

        log_data["family"]["count"] = len(sponsors)

        all_segments.append(Seg.GE(self.transaction_control_number).to_edi())
        all_segments.append(Seg.IEA().to_edi())

        logger.info(f"Generated total of {self.transaction_control_number} transactions")
        logger.info(f"There were {self.error_ctrl.error_count} errors")
        return all_segments

