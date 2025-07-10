from pathlib import Path
from datetime import datetime, date
import shutil
import logging
import json
import sys
from typing import Dict, List, Any

datagen_root = Path(__file__).resolve().parent.parent.parent.parent.parent / "DataGen"
sys.path.insert(0, str(datagen_root / "src"))

from RunGenerator import GenerateSponsors, CreateClaimDB
from Config import Config
from Repository.DatabaseFactory import get_database_backend
from Repository.Transaction_Storage_Functions import TransactionFunctions
from FileCreation.EDIGenerator import EDI270Generator


def setup_simple_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


logger = setup_simple_logging()


class TrackedEDI270Generator(EDI270Generator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transaction_metadata = []

    def create_transaction(self, num, error_ctrl):
        segments = super().create_transaction(num, error_ctrl)

        if self._is_valid_transaction_index(num):
            transaction_data = self._extract_transaction_data(num, error_ctrl, segments)
            self.transaction_metadata.append(transaction_data)

        return segments

    def _is_valid_transaction_index(self, num):
        return (
            hasattr(self, "claims")
            and self.claims
            and num > 0
            and num - 1 < len(self.claims)
        )

    def _extract_transaction_data(self, num, error_ctrl, segments):
        claim = self.claims[num - 1]

        bene = None
        try:
            bene = self.transaction_funcs.family_db.get_beneficiary(
                claim.sponsor_id, claim.beneficiary_id
            )
        except Exception:
            pass

        transaction_data = {
            "st_control_number": f"{num:06}",
            "transaction_type": "270",
            "icn": claim.claim_id,
            "beneficiary_id": claim.beneficiary_id,
            "sponsor_id": claim.sponsor_id,
            "provider_npi": getattr(claim, "provider_npi", None),
            "error_injected": error_ctrl.error_inserted if error_ctrl else False,
            "error_type": None,
            "error_segment": None,
            "line_number_in_file": None,
            "searchable_identifiers": {
                "st_control_number": f"{num:06}",
                "beneficiary_id": claim.beneficiary_id,
                "provider_npi": getattr(claim, "provider_npi", None),
            },
        }

        if bene:
            transaction_data["beneficiary_name"] = f"{bene.first_name} {bene.last_name}"
            transaction_data["beneficiary_dob"] = str(bene.dob) if bene.dob else None

        if error_ctrl and error_ctrl.error_inserted and segments:
            transaction_data["error_type"] = "injected"
            error_segment = self._find_error_segment(segments)
            if error_segment:
                transaction_data["error_segment"] = error_segment

        return transaction_data

    def _find_error_segment(self, segments):
        for segment in segments:
            if segment and self._has_error_markers(segment):
                segment_type = segment.split("*")[0] if "*" in segment else "unknown"
                return segment_type
        return None

    def _has_error_markers(self, segment):
        if not segment:
            return False
        return (
            "!@#" in segment
            or "~" in segment.split("*")[-1]
            or segment.strip().endswith("*")
            or segment.count("*") != segment.count("*")
        )

    def get_transaction_metadata(self):
        return self.transaction_metadata


def run_datagen_270_with_tracking(num_messages: int = 1000, error_rate: float = 0.005):

    if num_messages <= 0:
        raise ValueError("num_messages must be positive")
    if not (0.0 <= error_rate <= 1.0):
        raise ValueError("error_rate must be between 0.0 and 1.0")

    try:
        db = get_database_backend()
        if db.total_beneficiaries() < num_messages:
            logger.info(f"Generating {num_messages} beneficiaries...")
            GenerateSponsors(num_messages)

        logger.info(f"Creating claim database with {num_messages} claims...")
        CreateClaimDB(num_messages, date.today(), "Created")

        transaction_funcs = TransactionFunctions()
        edi = TrackedEDI270Generator(
            transaction_funcs=transaction_funcs, error_rate=error_rate
        )

        logger.info("Generating EDI segments...")
        edi_out = edi.combine_segments()

        output_path = Config.get_edi_path(Config.EDI270_PATH, Config.EDI270_FILE_NAME)
        logger.info(f"Writing EDI file to {output_path}")

        with open(output_path, "w") as f:
            f.writelines(edi_out)
        if not Path(output_path).exists():
            raise RuntimeError(f"Failed to create EDI file at {output_path}")

        _calculate_line_numbers(edi.transaction_metadata, output_path)

        return {
            "file_path": output_path,
            "num_transactions": len(edi.transaction_metadata),
            "error_count": sum(
                1 for t in edi.transaction_metadata if t["error_injected"]
            ),
            "transactions": edi.transaction_metadata,
        }

    except Exception as e:
        logger.error(f"Error in DataGen 270 generation: {str(e)}")
        raise RuntimeError(f"DataGen 270 generation failed: {str(e)}") from e


def _calculate_line_numbers(transaction_metadata, file_path):
    try:
        with open(file_path, "r") as f:
            for line_num, line in enumerate(f, 1):
                if line.startswith("ST*270*"):
                    try:
                        parts = line.split("*")
                        if len(parts) >= 3:
                            control_num = parts[2].strip("~\n")
                            for transaction in transaction_metadata:
                                if transaction["st_control_number"] == control_num:
                                    transaction["line_number_in_file"] = line_num
                                    break
                    except (IndexError, ValueError):
                        continue
    except Exception as e:
        logger.warning(f"Could not calculate line numbers: {e}")
        for transaction in transaction_metadata:
            transaction["line_number_in_file"] = None


def generate_edi_270_payloads_with_metadata(
    output_dir: str = "payloads", num_messages: int = 100, error_rate: float = 0.0
) -> Dict[str, Any]:
    payload_dir = Path(__file__).parent.parent / "client" / output_dir
    payload_dir.mkdir(exist_ok=True)

    logger.info(
        f"Generating {num_messages} EDI 270 messages with {error_rate} error rate"
    )

    datagen_results = run_datagen_270_with_tracking(
        num_messages=num_messages, error_rate=error_rate
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload_filename = f"edi_270_{timestamp}_{num_messages}msgs.edi"
    payload_file_path = payload_dir / payload_filename

    shutil.copy2(datagen_results["file_path"], payload_file_path)

    with open(datagen_results["file_path"], "r") as f:
        edi_content = f.read()

    edi_lines = edi_content.splitlines()

    metadata = {
        "file_info": {
            "original_path": datagen_results["file_path"],
            "payload_path": str(payload_file_path),
            "filename": payload_filename,
            "generated_at": timestamp,
            "num_transactions": datagen_results["num_transactions"],
            "file_size_bytes": len(edi_content),
            "total_lines": len(edi_lines),
        },
        "edi_payload": {
            "content": edi_content,
            "lines": edi_lines,
            "encoding": "utf-8",
            "format": "X12_EDI_270",
        },
        "error_summary": {
            "total_errors": datagen_results["error_count"],
            "error_rate_actual": (
                datagen_results["error_count"] / datagen_results["num_transactions"]
                if datagen_results["num_transactions"] > 0
                else 0
            ),
            "error_rate_requested": error_rate,
        },
        "transactions": datagen_results["transactions"],
        "transactions_by_error_status": {
            "clean": [
                t for t in datagen_results["transactions"] if not t["error_injected"]
            ],
            "with_errors": [
                t for t in datagen_results["transactions"] if t["error_injected"]
            ],
        },
        "error_breakdown": {},
    }

    for transaction in datagen_results["transactions"]:
        if transaction["error_injected"] and transaction["error_segment"]:
            segment = transaction["error_segment"]
            if segment not in metadata["error_breakdown"]:
                metadata["error_breakdown"][segment] = 0
            metadata["error_breakdown"][segment] += 1

    logger.info(f"Generated: {payload_filename}")
    logger.info(f"Total transactions: {datagen_results['num_transactions']}")
    logger.info(f"Transactions with errors: {datagen_results['error_count']}")
    if metadata["error_breakdown"]:
        logger.info(f"Error breakdown by segment: {metadata['error_breakdown']}")

    return {
        "file_path": str(payload_file_path),
        "metadata": metadata,
        "summary": {
            "total_transactions": datagen_results["num_transactions"],
            "clean_transactions": len(
                metadata["transactions_by_error_status"]["clean"]
            ),
            "error_transactions": len(
                metadata["transactions_by_error_status"]["with_errors"]
            ),
            "error_segments": list(metadata["error_breakdown"].keys()),
        },
    }


def generate_edi_270_payloads(
    output_dir: str = "payloads", num_messages: int = 100, error_rate: float = 0.0
) -> List[str]:
    result = generate_edi_270_payloads_with_metadata(
        output_dir, num_messages, error_rate
    )
    return [result["file_path"]]


if __name__ == "__main__":
    result = generate_edi_270_payloads_with_metadata(num_messages=10, error_rate=0.1)

    print(f"Generated file: {result['file_path']}")
    print(f"Summary: {result['summary']}")

    for transaction in result["metadata"]["transactions"]:
        if transaction["error_injected"]:
            print(
                f"Error transaction - ICN: {transaction['icn']}, "
                f"ST#: {transaction['st_control_number']}, "
                f"Segment: {transaction['error_segment']}, "
                f"Line: {transaction['line_number_in_file']}"
            )
