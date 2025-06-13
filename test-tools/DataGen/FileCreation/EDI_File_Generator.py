import uuid

import FileCreation.EDISegments as Seg
import config
from DataLayer.Datatypes import Sponsor


class EDI834Generator:
    def __init__(self, sender=config.SENDER_ID, receiver=config.RECEIVER_ID, relationship_map=config.RELATIONSHIP_MAP):
        self.sender = sender
        self.receiver = receiver
        self.relationship_map = relationship_map
        self.transaction_control_number = 0

    def create_member(self, member):
        self.transaction_control_number += 1

        if isinstance(member, Sponsor):
            relationship_code = '18'
            sponsor_id = member.sponsor_id
            beneficiary_id = member.sponsor_id
        else:
            relationship_code = self.relationship_map.get(member.relationship)
            sponsor_id = member.sponsor_id
            beneficiary_id = member.beneficiary_id

        segments = [Seg.ST(self.transaction_control_number).to_edi(),
                    Seg.BGN(uuid.uuid4().hex.upper()).to_edi(),
                    Seg.N1("P5", member.insurance_company, member.insurance_FID).to_edi(),
                    Seg.N1("IN", member.insurance_company, member.insurance_FID).to_edi(),
                    Seg.INS(relationship_code).to_edi(),
                    Seg.REF("0F", sponsor_id).to_edi(),
                    Seg.REF("6O", beneficiary_id).to_edi(),
                    Seg.NM1(member.last_name, member.first_name, member.middle_name, member.ssn).to_edi(),
                    Seg.PER(member.phone).to_edi(),
                    Seg.N3(member.address.building_number, member.address.street, member.address.apartment).to_edi(),
                    Seg.N4(member.address.city, member.address.state, member.address.zipcode).to_edi()
                    ]

        for code, value in member.deductibles.items():
            segments.append(Seg.AMT(code, str(value)).to_edi())
        for code, value in member.visit_counts.items():
            segments.append(Seg.AMT(code, str(value)).to_edi())

        segments += [Seg.HD().to_edi(),
                     Seg.DTP().to_edi(),
                     Seg.SE(len(segments) + 3, self.transaction_control_number).to_edi()
                     ]

        return segments

    def create_transaction(self, sponsor):
        segments = []
        segments.extend(self.create_member(sponsor))
        for beneficiary in sponsor.beneficiaries:
            segments.extend(self.create_member(beneficiary))
        return segments

    def generate_file(self, sponsors):
        all_segments = [Seg.ISA().to_edi(),
                        Seg.GS().to_edi()
                        ]

        for sponsor in sponsors:
            all_segments.extend(self.create_transaction(sponsor))

        all_segments.append(Seg.GE(self.transaction_control_number).to_edi())
        all_segments.append(Seg.IEA().to_edi())

        return all_segments
