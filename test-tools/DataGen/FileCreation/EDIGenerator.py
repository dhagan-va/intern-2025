import uuid

from Repository.NPI_Functions import get_random_provider
import FileCreation.EDISegments as Seg
import config
from FileCreation.ErrorInjector import ErrorInjector
from Repository.Local_Database_Functions import LocalDBFunctions
from config import logger


class EDI834Generator:
    def __init__(self, sender=config.SENDER_ID, receiver=config.RECEIVER_ID, relationship_map=config.RELATIONSHIP_MAP,
                 max_messages=None, error_rate=None):
        self.sender = sender
        self.receiver = receiver
        self.relationship_map = relationship_map
        self.transaction_control_number = 0
        self.max_messages = max_messages
        self.error_rate = error_rate
        self.error_ctrl = ErrorInjector(max_messages, error_rate)
        logger.debug(f"Initialized EDI834Generator")

    def create_member(self, member, error_ctrl):
        self.transaction_control_number += 1
        sponsor_id = member.sponsor_id
        relationship_code = self.relationship_map.get(member.relationship)
        beneficiary_id = member.beneficiary_id
        error_id = member.beneficiary_id
        logger.debug(f"Creating segments for Beneficiary: {beneficiary_id} under Sponsor: {sponsor_id}")

        segments = [Seg.ST(834, self.transaction_control_number).to_edi(),
                    Seg.BGN(uuid.uuid4().hex.upper()).to_edi(),
                    Seg.N1("P5", member.insurance_company, member.insurance_FID, error_ctrl, error_id).to_edi(),
                    Seg.N1("IN", member.insurance_company, member.insurance_FID, error_ctrl, error_id).to_edi(),
                    Seg.INS(relationship_code).to_edi(),
                    Seg.REF("0F", sponsor_id, error_ctrl).to_edi(),
                    Seg.REF("6O", beneficiary_id, error_ctrl).to_edi(),
                    Seg.NM1("IL", "1", member.last_name, member.first_name, member.middle_name, "34", member.ssn,
                            error_ctrl, error_id).to_edi(),
                    Seg.PER(member.phone, error_ctrl, error_id).to_edi(),
                    Seg.N3(member.address.building_number, member.address.street, member.address.apartment,
                           error_ctrl, error_id).to_edi(),
                    Seg.N4(member.address.city, member.address.state, member.address.zipcode, error_ctrl,
                           error_id).to_edi()
                    ]

        for code, value in member.deductibles.items():
            segments.append(Seg.AMT(code, str(value), error_ctrl, error_id).to_edi())
        for code, value in member.visit_counts.items():
            segments.append(Seg.AMT(code, str(value), error_ctrl, error_id).to_edi())

        segments += [Seg.HD().to_edi(),
                     Seg.DTP().to_edi(),
                     Seg.SE(len(segments) + 3, self.transaction_control_number).to_edi()
                     ]

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
            all_segments.extend(self.create_transaction(sponsor))

        all_segments.append(Seg.GE(self.transaction_control_number).to_edi())
        all_segments.append(Seg.IEA().to_edi())

        logger.info(f"Generated total of {self.transaction_control_number} transactions")
        logger.info(f"There were {self.error_ctrl.error_count} errors")
        return all_segments


class EDI270Generator:
    def __init__(self, max_messages=None, provider_csv_path=None):
        self.localdb_funcs = LocalDBFunctions()
        self.localdb_funcs.loadfile()
        self.max_messages = max_messages
        self.provider_csv_path = provider_csv_path

    @staticmethod
    def split_provider_name(name, entity_type):
        if entity_type == "2":
            return name, "", ""
        else:
            parts = name.replace(",", "").split()
            if len(parts) == 1:
                return parts[0], ""
            elif len(parts) == 2:
                return parts[0], parts[1]
            else:
                return "Something", ""

    def create_transaction(self, num):
        beneficiary = self.localdb_funcs.get_random_beneficiary()
        state = beneficiary.address.state

        provider = get_random_provider(self.provider_csv_path, state)
        last, first = self.split_provider_name(provider["name"], provider["entity_type"])

        if not provider:
            logger.warning(f"No provider found for state: {state}. Using fallback")
            provider = {
                "name": "Ryan's company",
                "npi": "0000000000",
                "entity_type": 2
            }

        segments = [Seg.ISA().to_edi(),
                    Seg.GS("HS").to_edi(),
                    Seg.ST(270, num).to_edi(),
                    Seg.BHT().to_edi(),
                    Seg.HL(1, "", 20, 1).to_edi(),
                    Seg.NM1("PR", 2, beneficiary.insurance_company, "", "", "PI",
                            beneficiary.insurance_FID).to_edi(),
                    Seg.HL(2, 1, 21, 1).to_edi(),
                    Seg.NM1("1P", provider["entity_type"], last, first, "", "XX", provider["npi"]).to_edi(),
                    Seg.HL(3, 2, 22, 0).to_edi(),
                    Seg.NM1("IL", "1", beneficiary.last_name, beneficiary.first_name,
                            beneficiary.middle_name, "MI", beneficiary.beneficiary_id).to_edi(),
                    Seg.EQ("30", "", "").to_edi(),
                    Seg.SE(10, num).to_edi(),
                    Seg.GE(1).to_edi(),
                    Seg.IEA().to_edi()
                    ]
        return segments

    def combine_segments(self):
        all_segments = []
        for i in range(1, self.max_messages + 1):
            all_segments.extend(self.create_transaction(i))
        return all_segments
