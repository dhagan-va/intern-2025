import os
import uuid
from datetime import date, timedelta

import FileCreation.EDISegments as Seg
from Config import Config
from Config.Config import logger
from Config.Data_Visualizer import log_data
from FileCreation.ErrorInjector import ErrorInjector


def split_provider_name(name, entity_type):
    if entity_type == "2":
        return name, ""

    parts = name.replace(",", "").split()

    if len(parts) == 1:
        return parts[0], ""
    else:
        return parts[0], parts[1]


class EDI270Generator:
    def __init__(self, transaction_funcs, error_rate=None):
        self.transaction_funcs = transaction_funcs
        self.claims = self.transaction_funcs.get_claim_transactions(
            status="Created",
            date=date.today().isoformat()
        )
        self.claims = sorted(self.claims, key=lambda c: c.creation != "CSV")
        self.num_messages = len(self.claims)
        self.error_ctrl = ErrorInjector(self.num_messages, error_rate)
        logger.info(f"Initializing EDI270Generator with {self.num_messages} claims")

    def create_2000A_loop(self, error_ctrl, error_id):
        segments = [Seg.HL(hl_id=1, hl_parent="", hl_code=20, children=1, error_ctrl=error_ctrl, error_id=error_id).to_edi()]
        segments.extend(self.create_2100A_loop(error_ctrl, error_id))
        return segments

    def create_2100A_loop(self, error_ctrl, error_id):
        return [Seg.NM1(Config.edi270_fields["payer_entity_identifier_code"], Config.edi270_fields["payer_entity_type_qualifier"], Config.PAYER_NAME, "", "", Config.edi270_fields["payer_id_code_qualifier"],
                        Config.PAYER_ID, error_ctrl, error_id).to_edi()]

    def create_2000B_loop(self, claim, claim_last, claim_first, error_ctrl, error_id):
        segments = [Seg.HL(hl_id=2, hl_parent=1, hl_code=21, children=1, error_ctrl=error_ctrl, error_id=error_id).to_edi()]
        segments.extend(self.create_2100B_loop(claim, claim_last, claim_first, error_ctrl, error_id))
        return segments

    def create_2100B_loop(self, claim, claim_last, claim_first, error_ctrl, error_id):
        return [Seg.NM1(Config.edi270_fields["provider_entity_identifier_code"], claim.provider_entity_type, claim_last, claim_first, "", Config.edi270_fields["provider_id_code_qualifier"],
                        claim.provider_npi, error_ctrl,
                        error_id).to_edi()]

    def create_2000C_loop(self, sponsor, error_ctrl, error_id):
        segments = [Seg.HL(hl_id=3, hl_parent=2, hl_code=22, children=0, error_ctrl=error_ctrl, error_id=error_id).to_edi()]
        segments.extend(self.create_2100C_loop(sponsor, error_ctrl, error_id))
        return segments

    def create_2100C_loop(self, sponsor, error_ctrl, error_id):
        return [Seg.NM1(Config.edi270_fields["subscriber_entity_identifier_code"], Config.edi270_fields["subscriber_entity_type_qualifier"], sponsor.last_name, sponsor.first_name,
                        sponsor.middle_name, Config.edi270_fields["subscriber_id_code_qualifier"], sponsor.sponsor_id, error_ctrl, error_id).to_edi()]

    def create_2000D_loop(self, bene, error_ctrl, error_id):
        segments = [Seg.HL(hl_id=4, hl_parent=3, hl_code=23, children=0, error_ctrl=error_ctrl, error_id=error_id).to_edi()]
        segments.extend(self.create_2100D_loop(bene, error_ctrl, error_id))
        return segments

    def create_2100D_loop(self, bene, error_ctrl, error_id):
        segments = [Seg.NM1(Config.edi270_fields["dependent_entity_identifier_code"], Config.edi270_fields["dependent_entity_type_qualifier"], bene.last_name, bene.first_name,
                            bene.middle_name, id_qualifier=None, id_code=None, error_ctrl=error_ctrl,
                            error_id=error_id).to_edi(),
                    Seg.DMG(bene.dob.strftime("%Y%m%d"), bene.gender).to_edi(),
                    Seg.DTP(Config.edi270_fields["dtp_qualifier"], Config.DATE_TIME_FMT_QUALIFIER).to_edi()]
        segments.extend(self.create_2110D_loop())
        return segments

    def create_2110D_loop(self):
        return [Seg.EQ(Config.edi270_fields["eq_service_type_code"]).to_edi()]

    def create_transaction(self, num, error_ctrl):
        if num - 1 >= len(self.claims) or num <= 0:
            logger.error(f"Index out of range for claim {num}")
            return None

        self.error_ctrl.reset_error_inserted()
        claim = self.claims[num - 1]
        last, first = split_provider_name(claim.provider_name, claim.provider_entity_type)
        error_id = claim.beneficiary_id
        bene = self.transaction_funcs.get_beneficiary(claim.sponsor_id, claim.beneficiary_id)
        sponsor = self.transaction_funcs.get_sponsor_by_id(bene.sponsor_id)

        segments = [Seg.ST("270", num).to_edi(),
                    Seg.BHT(Config.edi270_fields["hierarchical_structure_code"], Config.edi270_fields["transaction_set_purpose_code"], claim.claim_id).to_edi()]

        segments.extend(self.create_2000A_loop(self.error_ctrl, error_id))
        segments.extend(self.create_2000B_loop(claim, last, first, self.error_ctrl, error_id))
        segments.extend(self.create_2000C_loop(sponsor, self.error_ctrl, error_id))
        segments.extend(self.create_2000D_loop(bene, self.error_ctrl, error_id))

        segments.append(Seg.SE(len(segments) + 1, num).to_edi())

        if self.error_ctrl.error_inserted:
            log_data["errors"]["error_ct_270"] += 1
            logger.warning(f"[ERROR INSERTED] Transaction {num}")

        return segments

    def combine_segments(self):
        file_paths = []
        output_dir = os.path.join(Config.EDI270_PATH, Config.YMDHM)
        for i in range(1, self.num_messages + 1):
            transaction_segments = [Seg.ISA().to_edi(),
                                    Seg.GS(Config.edi270_fields["gs_functional_identifier_code"]).to_edi()
                                    ]
            transaction_segments.extend(self.create_transaction(i, self.error_ctrl))
            transaction_segments += [Seg.GE(1).to_edi(),
                                     Seg.IEA().to_edi()
                                     ]

            edi_content = "".join(transaction_segments)
            byte_size = len(edi_content.encode('utf-8'))
            transaction_id = f"MPII{i:02}"
            header = f"{byte_size:06d}{transaction_id}"

            file_name = Config.EDI270_FILE_NAME.format(
                year=Config.YEAR, ymd=Config.YMD, hm=Config.HM, claim_id=transaction_id, full_date=Config.FULL_DATE
            )
            file_path = Config.get_edi_path(output_dir, file_name)

            with open(file_path, 'w') as f:
                f.write(header + "\n")
                f.write(edi_content)
            file_paths.append(file_path)

        claim_ids = [claim.claim_id for claim in self.claims]
        self.transaction_funcs.update_claims_status(claim_ids, "270 Created")
        return file_paths


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

    def create_1000A_1000B_loop(self, error_ctrl, error_id):
        segments = [Seg.NM1(Config.edi837_fields['submitter_entity_identifier_code'], Config.edi837_fields['submitter_entity_type_qualifier'], Config.edi837_fields['submitter_name'],
                            "", "", Config.edi837_fields['submitter_id_code_qualifier'], Config.edi837_fields['submitter_id'], error_ctrl).to_edi(),
                    Seg.PER(Config.edi837_fields['per_contact_function_code'], Config.edi837_fields['per_communication_number'], error_ctrl, error_id).to_edi(),
                    Seg.NM1(Config.edi837_fields['receiver_entity_identifier_code'], Config.edi837_fields['receiver_entity_type_qualifier'], Config.edi837_fields['receiver_name'], "", "", Config.edi837_fields['receiver_id_code_qualifier'], Config.edi837_fields['receiver_id'], error_ctrl).to_edi()]
        return segments

    def create_2000A_loop(self, claim, claim_last, claim_first, error_ctrl, error_id):
        segments = [Seg.HL("1", "", 20, 1, error_ctrl, error_id).to_edi()]
        segments.extend(self.create_2010A_loop(claim, claim_last, claim_first, error_ctrl, error_id))
        return segments

    def create_2010A_loop(self, claim, claim_last, claim_first, error_ctrl, error_id):
        segments = [
            Seg.NM1(Config.edi837_fields['billing_provider_entity_identifier_code'], claim.provider_entity_type, claim_last, claim_first, "", Config.edi837_fields['billing_provider_id_code_qualifier'], claim.provider_npi, error_ctrl,
                    error_id).to_edi(),
            Seg.N3(claim.provider_address_1, claim.provider_address_2, "", error_ctrl, error_id,
                   True).to_edi(),
            Seg.N4(claim.provider_city, claim.provider_state, claim.provider_zip, error_ctrl,
                   error_id).to_edi(),
            Seg.REF(Config.edi837_fields['ref_billing_provider_qualifier'], Config.edi837_fields['ref_billing_provider_id'], error_ctrl).to_edi()]
        return segments

    def create_2000B_loop(self, sponsor, error_ctrl, error_id):
        segments = [Seg.HL("2", "1", 22, 1, error_ctrl, error_id).to_edi(),
                    Seg.SBR(Config.edi837_fields['sbr_payer_relationship_code'], Config.edi837_fields['sbr_group_id']).to_edi()]
        segments.extend(self.create_2010BA_loop(sponsor, error_ctrl, error_id))
        segments.extend(self.create_2010BB_loop(error_ctrl, error_id))
        return segments

    def create_2010BA_loop(self, sponsor, error_ctrl, error_id):
        segments = [
            Seg.NM1(Config.edi837_fields['subscriber_entity_identifier_code'], Config.edi837_fields['subscriber_entity_type_qualifier'], sponsor.last_name, sponsor.first_name, sponsor.middle_name,
                    Config.edi837_fields['subscriber_id_code_qualifier'], sponsor.sponsor_id, error_ctrl).to_edi(),
            Seg.N3(sponsor.address.building_number, sponsor.address.street, sponsor.address.apartment,
                   error_ctrl).to_edi(),
            Seg.N4(sponsor.address.city, sponsor.address.state, sponsor.address.zipcode, error_ctrl,
                   error_id).to_edi(),
            Seg.DMG(sponsor.dob.strftime("%Y%m%d"), sponsor.gender).to_edi()]
        return segments

    def create_2010BB_loop(self, error_ctrl, error_id):
        segments = [Seg.NM1(Config.edi837_fields['payer_entity_identifier_code'], Config.edi837_fields['payer_entity_type_qualifier'], Config.PAYER_NAME, "", "", Config.edi837_fields['payer_id_code_qualifier'],
                            Config.PAYER_ID, error_ctrl, error_id).to_edi(),
                    Seg.N3(Config.edi837_fields['payer_address_1'], Config.edi837_fields['payer_address_2']).to_edi(),
                    Seg.N4(Config.edi837_fields['payer_city'], Config.edi837_fields['payer_state'], Config.edi837_fields['payer_zip'], error_ctrl, error_id).to_edi()]
        return segments

    def create_2000C_loop(self, bene, bene_relationship, error_ctrl, error_id):
        segments = [Seg.HL("3", "2", 23, 0, error_ctrl, error_id).to_edi(),                    Seg.PAT(bene_relationship).to_edi()]
        segments.extend(self.create_2010CA_loop(bene, error_ctrl, error_id))
        return segments

    def create_2010CA_loop(self, bene, error_ctrl, error_id):
        segments = [
            Seg.NM1(Config.edi837_fields['patient_entity_identifier_code'], Config.edi837_fields['patient_entity_type_qualifier'], bene.last_name, bene.first_name, bene.middle_name, id_qualifier=None, id_code=None,
                    error_ctrl=error_ctrl, error_id=bene.beneficiary_id).to_edi(),
            Seg.N3(bene.address.building_number, bene.address.street, bene.address.apartment, error_ctrl,
                   error_id).to_edi(),
            Seg.N4(bene.address.city, bene.address.state, bene.address.zipcode, error_ctrl, error_id).to_edi(),
            Seg.DMG(bene.dob.strftime("%Y%m%d"), bene.gender).to_edi()]
        return segments

    def create_2300_loop(self, claim, claim_last, claim_first, error_ctrl):
        segments = [Seg.CLM(claim.claim_id, Config.edi837_fields['clm_charge_amount'], Config.edi837_fields['clm_facility_code'], Config.edi837_fields['clm_facility_qualifier'], Config.edi837_fields['clm_frequency']).to_edi(),
                    Seg.REF(Config.edi837_fields['ref_claim_qualifier'], claim.claim_id, error_ctrl).to_edi(),
                    Seg.HI(Config.edi837_fields['hi_diagnosis_code_qualifier'], Config.edi837_fields['hi_diagnosis_code']).to_edi()]
        segments.extend(self.create_2310B_loop(claim, claim_last, claim_first, error_ctrl))
        return segments

    def create_2310B_loop(self, claim, claim_last, claim_first, error_ctrl):
        segments = [Seg.NM1(Config.edi837_fields['rendering_provider_entity_identifier_code'], Config.edi837_fields['rendering_provider_entity_type_qualifier'], claim_last, claim_first, "", Config.edi837_fields['rendering_provider_id_code_qualifier'], claim.provider_npi, error_ctrl).to_edi(),
                    Seg.PRV(Config.edi837_fields['prv_provider_code'], Config.edi837_fields['prv_reference_identification_qualifier'], Config.edi837_fields['prv_provider_taxonomy_code']).to_edi()]
        return segments

    def create_2400_loop(self, claim, error_ctrl):
        service_date_qualifier = Config.edi837_fields['dtp_service_date_qualifier']
        segments = [Seg.LX("1").to_edi(),
                    Seg.SV1(Config.edi837_fields['sv1_procedure_identifier'], Config.edi837_fields['sv1_line_item_charge_amount'], Config.edi837_fields['sv1_unit_or_basis_for_measurement_code'], Config.edi837_fields['sv1_service_unit_count'], 1).to_edi(),
                    Seg.DTP(service_date_qualifier, Config.DATE_TIME_FMT_QUALIFIER).to_edi(),
                    Seg.REF(Config.edi837_fields['ref_line_item_qualifier'], claim.claim_id, error_ctrl).to_edi()]
        return segments

    def create_claim_anesthesia(self, num, error_ctrl):
        if num - 1 >= len(self.claims) or num <= 0:
            logger.error(f"Index out of range for claim {num}")
            return None

        claim = self.claims[num - 1]
        bene = self.transaction_funcs.get_beneficiary(claim.sponsor_id, claim.beneficiary_id)
        sponsor = self.transaction_funcs.get_sponsor_by_id(claim.sponsor_id)
        bene_relationship = self.relationship_map.get(bene.relationship)
        error_id = bene.beneficiary_id
        last, first = split_provider_name(claim.provider_name, claim.provider_entity_type)

        if bene_relationship == "25" or bene_relationship == "26":
            bene_relationship = "G8"

        segments = [Seg.ST("837", num).to_edi(),
                    Seg.BHT(Config.edi837_fields['bht_structure_code'], Config.edi837_fields['bht_purpose_code'], claim.claim_id, "837").to_edi()]

        segments.extend(self.create_1000A_1000B_loop(error_ctrl, error_id))
        segments.extend(self.create_2000A_loop(claim, last, first, error_ctrl, error_id))
        segments.extend(self.create_2000B_loop(sponsor, error_ctrl, error_id))
        segments.extend(self.create_2000C_loop(bene, bene_relationship, error_ctrl, error_id))
        segments.extend(self.create_2300_loop(claim, last, first, error_ctrl))
        segments.extend(self.create_2400_loop(claim, error_ctrl))

        segments.append(Seg.SE(len(segments) + 1, self.transaction_control_number).to_edi())
        self.transaction_control_number += 1

        if self.error_ctrl.error_inserted:
            log_data["errors"]["error_ct_837"] += 1

        return segments

    def combine_segments(self):
        all_segments = [Seg.ISA().to_edi(),
                        Seg.GS(Config.edi837_fields['gs_functional_identifier_code']).to_edi()
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
            date=yesterday.isoformat()
        )
        self.num_messages = len(self.claims)
        self.error_ctrl = ErrorInjector(self.num_messages, error_rate)
        self.optional_L2220D = True

    def get_num_messages(self):
        return self.num_messages

    def create_2000A_loop(self, claim, error_ctrl, error_id):
        segments = [Seg.HL("1", "", 20, 1).to_edi()]
        segments.extend(self.create_2100A_loop(error_ctrl, error_id))
        segments.extend(self.create_2200A_loop(claim, error_ctrl, error_id))
        return segments

    def create_2100A_loop(self, error_ctrl, error_id):
        return [Seg.NM1(Config.edi277ca_fields['payer_entity_identifier_code'], Config.edi277ca_fields['payer_entity_type_qualifier'], Config.PAYER_NAME, "", "", Config.edi277ca_fields['payer_id_code_qualifier'],
                        Config.PAYER_ID, error_ctrl, error_id).to_edi()]

    def create_2200A_loop(self, claim, error_ctrl, error_id):
        segments = [Seg.TRN(Config.edi277ca_fields['trn_originating_company_identifier'], claim.payer_claim_id, error_ctrl=error_ctrl, error_id=error_id).to_edi(),
                    Seg.DTP(Config.edi277ca_fields['dtp_receipt_date_qualifier'], Config.DATE_TIME_FMT_QUALIFIER).to_edi(),
                    Seg.DTP(Config.edi277ca_fields['dtp_process_date_qualifier'], Config.DATE_TIME_FMT_QUALIFIER).to_edi()]
        return segments

    def create_2000B_loop(self, claim, error_ctrl, error_id):
        segments = [Seg.HL("2", "1", 21, 1).to_edi()]
        segments.extend(self.create_2100B_loop(error_ctrl))
        segments.extend(self.create_2200B_loop(claim, error_ctrl, error_id))
        return segments

    def create_2100B_loop(self, error_ctrl):
        return [Seg.NM1(Config.edi277ca_fields['submitter_entity_identifier_code'], Config.edi277ca_fields['submitter_entity_type_qualifier'], Config.edi277ca_fields['submitter_name'],
                        "", "", Config.edi277ca_fields['submitter_id_code_qualifier'], Config.edi277ca_fields['submitter_id'], error_ctrl).to_edi()]

    def create_2200B_loop(self, claim, error_ctrl, error_id):
        segments = [Seg.TRN(Config.edi277ca_fields['trn_trace_type_code'], claim.claim_id, error_ctrl=error_ctrl, error_id=error_id).to_edi(),
                    Seg.STC("277CA_2200B", Config.edi277ca_fields['stc_claim_status_category_code'], Config.edi277ca_fields['stc_status_information_code'], Config.edi277ca_fields['stc_entity_identifier_code'], error_ctrl, error_id).to_edi(),
                    Seg.AMT("YU", claim.amount, error_ctrl, error_id).to_edi()]
        return segments

    def create_2000C_loop(self, claim, error_ctrl, error_id):
        segments = [Seg.HL("3", "2", 19, 1).to_edi()]
        segments.extend(self.create_2100C_loop(claim, error_ctrl, error_id))
        segments.extend(self.create_2200C_loop(claim, error_ctrl, error_id))
        return segments

    def create_2100C_loop(self, claim, error_ctrl, error_id):
        last, first = split_provider_name(claim.provider_name, claim.provider_entity_type)
        return [Seg.NM1(Config.edi277ca_fields['provider_entity_identifier_code'], claim.provider_entity_type, last, first, "", Config.edi277ca_fields['provider_id_code_qualifier'], claim.provider_npi, error_ctrl,
                        error_id).to_edi()]

    def create_2200C_loop(self, claim, error_ctrl, error_id):
        return [Seg.TRN(Config.edi277ca_fields['trn_originating_company_identifier'], claim.payer_claim_id, error_ctrl=error_ctrl, error_id=error_id).to_edi()]

    def create_2000D_loop(self, claim, bene, error_ctrl, error_id):
        segments = [Seg.HL("4", "3", Config.edi277ca_fields['hl_patient_code']).to_edi()]
        segments.extend(self.create_2100D_loop(bene, error_ctrl))
        segments.extend(self.create_2200D_loop(claim, error_ctrl, error_id))
        return segments

    def create_2100D_loop(self, bene, error_ctrl):
        return [Seg.NM1(Config.edi277ca_fields['patient_entity_identifier_code'], Config.edi277ca_fields['patient_entity_type_qualifier'], bene.last_name, bene.first_name, bene.middle_name, Config.edi277ca_fields['patient_id_code_qualifier'],
                        bene.beneficiary_id, error_ctrl).to_edi()]

    def create_2200D_loop(self, claim, error_ctrl, error_id):
        segments = [Seg.TRN(Config.edi277ca_fields['trn_trace_type_code'], claim.claim_id, error_ctrl=error_ctrl, error_id=error_id).to_edi(),
                    Seg.STC("277CA_2200D", Config.edi277ca_fields['stc_claim_status_category_code_patient'], Config.edi277ca_fields['stc_status_information_code_patient'], claim.amount, error_ctrl, error_id).to_edi(),
                    Seg.REF(Config.edi277ca_fields['ref_payer_claim_control_number_qualifier'], claim.payer_claim_id, error_ctrl).to_edi(),
                    Seg.DTP(Config.edi277ca_fields['dtp_service_date_qualifier'], Config.DATE_TIME_FMT_QUALIFIER).to_edi()
                    ]
        return segments

    def create_2220D_loop(self, claim, error_ctrl, error_id):
        segments = [Seg.SVC("277CA", Config.edi277ca_fields['svc_procedure_identifier'], claim.amount, Config.edi277ca_fields['svc_line_item_charge_amount']).to_edi(),
                    Seg.STC("277CA_2220D", Config.edi277ca_fields['stc_claim_status_category_code_service'], Config.edi277ca_fields['stc_status_information_code_service'], claim.amount, error_ctrl, error_id).to_edi(),
                    Seg.REF(Config.edi277ca_fields['ref_line_item_control_number_qualifier'], claim.claim_id, error_ctrl).to_edi(),
                    Seg.DTP(Config.edi277ca_fields['dtp_service_date_qualifier'], Config.DATE_TIME_FMT_QUALIFIER).to_edi()
                    ]
        return segments

    def create_transaction(self, num, error_ctrl):
        if num - 1 >= len(self.claims) or num <= 0:
            logger.error(f"Index out of range for claim {num}")
            return None

        self.error_ctrl.reset_error_inserted()
        claim = self.claims[num - 1]
        error_id = claim.beneficiary_id
        bene = self.transaction_funcs.get_beneficiary(claim.sponsor_id, claim.beneficiary_id)

        segments = [Seg.ST("277", num).to_edi(),
                    Seg.BHT(Config.edi277ca_fields['bht_structure_code'], Config.edi277ca_fields['bht_purpose_code'], claim.claim_id, "277CA").to_edi()]

        segments.extend(self.create_2000A_loop(claim, error_ctrl, error_id))
        segments.extend(self.create_2000B_loop(claim, error_ctrl, error_id))
        segments.extend(self.create_2000C_loop(claim, error_ctrl, error_id))
        segments.extend(self.create_2000D_loop(claim, bene, error_ctrl, error_id))

        if self.optional_L2220D:
            segments.extend(self.create_2220D_loop(claim, error_ctrl, error_id))
            logger.debug("L2220D conditional in 277CA -- Claim is rejected")

        segments.append(Seg.SE(len(segments) + 1, num).to_edi())

        if self.error_ctrl.error_inserted:
            log_data["errors"]["error_ct_277CA"] += 1

        return segments

    def combine_segments(self):
        all_segments = []
        for i in range(1, self.num_messages + 1):
            all_segments += [Seg.ISA().to_edi(),
                             Seg.GS(Config.edi277ca_fields['gs_functional_identifier_code']).to_edi()
                             ]
            all_segments.extend(self.create_transaction(i, self.error_ctrl))
            all_segments += [Seg.GE(1).to_edi(),
                             Seg.IEA().to_edi()
                             ]

        claim_ids = [claim.claim_id for claim in self.claims]
        self.transaction_funcs.update_claims_status(claim_ids, "277CA Created")
        return all_segments


class EDI835Generator:
    def __init__(self, transaction_funcs, sender=Config.SENDER_ID, receiver=Config.RECEIVER_ID, error_rate=None):
        self.transaction_funcs = transaction_funcs
        self.sender = sender
        self.receiver = receiver
        week_and_day_before = date.today() - timedelta(days=8)
        self.claims = self.transaction_funcs.get_claim_transactions(
            status="277CA Created",
            date=week_and_day_before.isoformat()
        )
        self.transaction_control_number = 0
        self.num_messages = len(self.claims)
        self.error_ctrl = ErrorInjector(self.num_messages, error_rate)
        logger.debug("Initialized EDI835Generator")

    def get_num_messages(self):
        return self.num_messages

    # Payer Identification Loop
    def create_1000A_loop(self, error_ctrl, error_id):
        segments = [Seg.N1(Config.edi835_fields['payer_entity_identifier_code'], Config.PAYER_NAME, Config.edi835_fields['payer_id_code_qualifier'], Config.PAYER_ID, error_ctrl, error_id).to_edi(),
                    Seg.N3(Config.edi835_fields['payer_address_1'], Config.edi835_fields['payer_address_2']).to_edi(),
                    Seg.N4(Config.edi835_fields['payer_city'], Config.edi835_fields['payer_state'], Config.edi835_fields['payer_zip'], error_ctrl, error_id).to_edi(),
                    Seg.PER(Config.edi835_fields['per_contact_function_code'], Config.edi835_fields['per_communication_number'], error_ctrl, error_id).to_edi()]
        return segments

    # Payee Identification Loop
    def create_1000B_loop(self, claim, error_ctrl, error_id):
        return [Seg.N1(Config.edi835_fields['payee_entity_identifier_code'], claim.provider_name, Config.edi835_fields['payee_id_code_qualifier'], claim.provider_npi, error_ctrl, error_id).to_edi()]

    # Header Number Loop
    def create_2000_loop(self, claim, bene, error_ctrl):
        segments = [Seg.LX("1").to_edi()]
        segments.extend(self.create_2100_loop(claim, bene, error_ctrl))
        return segments

    # Claim Payment Information Loop
    def create_2100_loop(self, claim, bene, error_ctrl):
        segments = [Seg.CLP(claim.claim_id, Config.edi835_fields['clp_claim_status_code'], claim.amount, claim.amount, Config.edi835_fields['clp_patient_responsibility_amount'], claim.payer_claim_id).to_edi(),
                    Seg.NM1(Config.edi835_fields['patient_entity_identifier_code'], Config.edi835_fields['patient_entity_type_qualifier'], bene.last_name, bene.first_name, bene.middle_name, Config.edi835_fields['patient_id_code_qualifier'],
                            bene.beneficiary_id, error_ctrl).to_edi()]
        segments.extend(self.create_2110_loop(claim, error_ctrl))
        return segments

    # Service Payment Information Loop
    def create_2110_loop(self, claim, error_ctrl):
        segments = [Seg.SVC("835", Config.edi835_fields['svc_procedure_identifier'], claim.amount, Config.edi835_fields['svc_line_item_charge_amount'], Config.edi835_fields['svc_unit_or_basis_for_measurement_code'], Config.edi835_fields['svc_service_unit_count']).to_edi(),
                    Seg.REF(Config.edi835_fields['ref_line_item_qualifier'], claim.claim_id, error_ctrl).to_edi()]
        return segments

    # Header and Trailer
    def create_transaction(self, num, error_ctrl):
        if num - 1 >= len(self.claims) or num <= 0:
            logger.error(f"Index out of range for claim {num}")
            return None

        self.error_ctrl.reset_error_inserted()
        claim = self.claims[num - 1]
        error_id = claim.beneficiary_id
        bene = self.transaction_funcs.get_beneficiary(claim.sponsor_id, claim.beneficiary_id)

        segments = [Seg.ST("835", num).to_edi(),
                    Seg.BPR(Config.edi835_fields['bpr_transaction_handling_code'], claim.amount, Config.edi835_fields['bpr_credit_debit_code'], Config.edi835_fields['bpr_payment_method']).to_edi(),
                    Seg.TRN(Config.edi835_fields['trn_trace_type_code'], Config.edi835_fields['trn_check_or_eft_trace_number'], Config.edi835_fields['trn_payer_id']).to_edi()]
        segments.extend(self.create_1000A_loop(error_ctrl, error_id)),
        segments.extend(self.create_1000B_loop(claim, error_ctrl, error_id))
        segments.extend(self.create_2000_loop(claim, bene, error_ctrl))
        segments.append(Seg.SE(len(segments) + 1, num).to_edi())

        if self.error_ctrl.error_inserted:
            log_data["errors"]["error_ct_835"] += 1

        return segments

    def combine_segments(self):
        all_segments = []
        for i in range(1, self.num_messages + 1):
            all_segments += [Seg.ISA().to_edi(),
                             Seg.GS(Config.edi835_fields['gs_functional_identifier_code']).to_edi()
                             ]
            all_segments.extend(self.create_transaction(i, self.error_ctrl))
            all_segments += [Seg.GE(1).to_edi(),
                             Seg.IEA().to_edi()
                             ]

        claim_ids = [claim.claim_id for claim in self.claims]
        self.transaction_funcs.update_claims_status(claim_ids, "835 Created")
        return all_segments


class EDI834Generator:
    def __init__(self, transaction_funcs, sender=Config.SENDER_ID, receiver=Config.RECEIVER_ID,
                 relationship_map=Config.RELATIONSHIP_MAP, error_rate=None):
        self.transaction_funcs = transaction_funcs
        self.sender = sender
        self.receiver = receiver
        self.relationship_map = relationship_map
        week_and_day_before = date.today() - timedelta(days=8)
        self.claims = self.transaction_funcs.get_claim_transactions(
            status="835 Created",
            date=week_and_day_before.isoformat()
        )
        self.transaction_control_number = 0
        self.num_messages = len(self.claims)
        self.error_ctrl = ErrorInjector(self.num_messages, error_rate)
        logger.debug(f"Initialized EDI834Generator")

    def get_num_messages(self):
        return self.num_messages

    # Sponsor Name Loop
    def create_1000A_loop(self, error_ctrl, error_id):
        return Seg.N1(Config.edi834_fields['sponsor_entity_identifier_code'], Config.SPONSOR_NAME, Config.edi834_fields['sponsor_id_code_qualifier'], Config.SPONSOR_ID, error_ctrl,
                      error_id).to_edi()

    # Payer Loop
    def create_1000B_loop(self, error_ctrl, error_id):
        return Seg.N1(Config.edi834_fields['payer_entity_identifier_code'], Config.PAYER_NAME, Config.edi834_fields['payer_id_code_qualifier'], Config.PAYER_ID, error_ctrl, error_id).to_edi()

    # Member Level Detail Loop
    def create_2000_loop(self, sponsor, bene, error_ctrl, error_id):
        relationship_code = self.relationship_map.get(bene.relationship)

        segments = [Seg.INS(relationship_code).to_edi(),
                    Seg.REF(Config.edi834_fields['ref_subscriber_id_qualifier'], sponsor.sponsor_id, error_ctrl).to_edi(),
                    Seg.REF(Config.edi834_fields['ref_member_policy_number_qualifier'], bene.beneficiary_id, error_ctrl).to_edi(),
                    Seg.NM1(Config.edi834_fields['member_entity_identifier_code'], Config.edi834_fields['member_entity_type_qualifier'], bene.last_name, bene.first_name, bene.middle_name, Config.edi834_fields['member_id_code_qualifier'], bene.ssn,
                            error_ctrl, error_id).to_edi(),
                    Seg.PER(Config.edi834_fields['per_contact_function_code'], bene.phone, error_ctrl, error_id).to_edi(),
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

        segments.extend(self.create_2300_loop())
        return segments

    # Health Coverage Loop
    def create_2300_loop(self):
        segments = [Seg.HD().to_edi(),
                    Seg.DTP(Config.edi834_fields['dtp_eligibility_begin_qualifier'], Config.DATE_TIME_FMT_QUALIFIER).to_edi()
                    ]
        return segments

    # Header and Trailer + Transaction
    def create_transaction(self, bene, error_ctrl):
        self.transaction_control_number += 1
        self.error_ctrl.reset_error_inserted()
        sponsor = self.transaction_funcs.get_sponsor_by_id(bene.sponsor_id)

        error_id = bene.beneficiary_id

        segments = [Seg.ST("834", self.transaction_control_number).to_edi(),
                    Seg.BGN(uuid.uuid4().hex.upper()).to_edi()]

        segments.extend(self.create_1000A_loop(error_ctrl, error_id))
        segments.extend(self.create_1000B_loop(error_ctrl, error_id))
        segments.extend(self.create_2000_loop(sponsor, bene, error_ctrl, error_id))

        segments.append(Seg.SE(len(segments) + 1, self.transaction_control_number).to_edi())

        if self.error_ctrl.error_inserted:
            log_data["errors"]["error_ct_834"] += 1
        logger.debug(f"Completed {len(segments)} segments for member {bene.beneficiary_id}")
        return segments

    def combine_segments(self):
        logger.debug(f"Starting EDI 834 generation for {self.num_messages} beneficiaries")
        all_segments = [Seg.ISA().to_edi(),
                        Seg.GS(Config.edi834_fields['gs_functional_identifier_code']).to_edi()
                        ]

        for claim in self.claims:
            bene = self.transaction_funcs.get_beneficiary(claim.sponsor_id, claim.beneficiary_id)
            log_data["family"]["size"] += 1
            all_segments.extend(self.create_transaction(bene, self.error_ctrl))

        log_data["family"]["count"] = len(self.claims)

        all_segments.append(Seg.GE(self.transaction_control_number).to_edi())
        all_segments.append(Seg.IEA().to_edi())

        logger.info(f"Generated total of {self.transaction_control_number} transactions")
        logger.info(f"There were {self.error_ctrl.error_count} errors")

        claim_ids = [claim.claim_id for claim in self.claims]
        self.transaction_funcs.update_claims_status(claim_ids, "834 Created")
        return all_segments


class EDI999Generator:
    def __init__(self, transaction_funcs, error_rate=None):
        self.transaction_funcs = transaction_funcs
        week_and_day_before = date.today() - timedelta(days=8)
        self.claims = self.transaction_funcs.get_claim_transactions(
            status="834 Created",
            date=week_and_day_before
        )
        self.num_messages = len(self.claims)
        self.error_ctrl = ErrorInjector(self.num_messages, error_rate)
        logger.debug(f"Initialized EDI999Generator with {self.num_messages} claims")

    def get_num_messages(self):
        return self.num_messages

    # Transaction Set Response Header Loop
    def create_2000_loop(self, file_type, ctrl_num):
        segments = []
        segments.append(Seg.AK2(file_type, ctrl_num).to_edi())
        segments.append(Seg.IK5(Config.edi999_fields["ik5_implementation_ack_code"]).to_edi())
        return segments

    # Header and Trailer + Transaction
    def create_transaction(self, num):
        if num - 1 >= len(self.claims) or num <= 0:
            logger.error(f"Index out of range for claim {num}")
            return None

        # HC corresponds to 005010X222A1 (837)
        # BE corresponds to 005010X220A1 (834)
        segments = [Seg.ST("999", num).to_edi(),
                    Seg.AK1(Config.edi999_fields["ak1_functional_identifier_code"], num).to_edi(),
                    ]
        segments.extend(self.create_2000_loop("837", num))
        segments.extend([Seg.AK9(Config.edi999_fields["ak9_functional_group_ack_code"], self.num_messages, self.num_messages, self.num_messages).to_edi()])
        segments.extend(Seg.SE(len(segments) + 1, num).to_edi())

        if self.error_ctrl.error_inserted:
            log_data["errors"]["error_ct_999"] += 1

        return segments

    # Envelope
    def combine_segments(self):
        all_segments = []
        for i in range(1, self.num_messages + 1):
            all_segments += [Seg.ISA().to_edi(),
                             Seg.GS(Config.edi999_fields["gs_functional_identifier_code"]).to_edi()
                             ]
            all_segments.extend(self.create_transaction(i))
            all_segments += [Seg.GE(1).to_edi(),
                             Seg.IEA().to_edi()
                             ]

        return all_segments
