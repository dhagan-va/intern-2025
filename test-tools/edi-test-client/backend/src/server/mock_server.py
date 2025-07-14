from flask import Flask, request
import random
import time
import logging
from . import samples

app = Flask(__name__)
logger = logging.getLogger(__name__)

ERROR_CONFIG = {
    "timeout_rate": 0.03,
    "bad_gateway_rate": 0.02,
    "service_unavailable_rate": 0.02,
    "bad_request_rate": 0.01,
}

EDI_ERROR_RESPONSES = {
    "segment:ISA": samples.SAMPLE_271_INPUT_ERROR,
    "segment:NM1": samples.SAMPLE_271_INVALID_NPI,
    "segment:HL": samples.SAMPLE_271_INPUT_ERROR,
    "type:injected": samples.SAMPLE_271_INPUT_ERROR,
    "format": samples.SAMPLE_271_INPUT_ERROR,
    "missing": samples.SAMPLE_271_MISSING_ID,
}


def get_edi_error_response():
    has_errors = request.headers.get("X-Has-Errors", "false").lower() == "true"

    if not has_errors:
        return None

    transaction_num = request.headers.get("X-Transaction-Number", "unknown")
    beneficiary_id = request.headers.get("X-Beneficiary-ID", "unknown")
    error_types = request.headers.get("X-Error-Types", "")
    error_line = request.headers.get("X-Error-Line", "unknown")

    logger.info(
        f"Processing EDI error transaction {transaction_num} for beneficiary {beneficiary_id} "
        f"with errors: {error_types} at line {error_line}"
    )

    if error_types:
        for error_type in error_types.split(","):
            error_type = error_type.strip()
            if error_type in EDI_ERROR_RESPONSES:
                edi_response = EDI_ERROR_RESPONSES[error_type]
                logger.info(f"Returning EDI 271 error response for {error_type}")
                return edi_response

    logger.info("Returning default EDI 271 input error response")
    return samples.SAMPLE_271_INPUT_ERROR


def random_error():
    """Network/infrastructure error function - returns HTTP error codes."""
    rand = random.random()

    if rand < ERROR_CONFIG["timeout_rate"]:
        return "Internal Server Error", 500

    if rand < ERROR_CONFIG["timeout_rate"] + ERROR_CONFIG["bad_gateway_rate"]:
        return "Bad Gateway", 502

    if rand < (
        ERROR_CONFIG["timeout_rate"]
        + ERROR_CONFIG["bad_gateway_rate"]
        + ERROR_CONFIG["service_unavailable_rate"]
    ):
        return "Service Temporarily Unavailable", 503

    if rand < (
        ERROR_CONFIG["timeout_rate"]
        + ERROR_CONFIG["bad_gateway_rate"]
        + ERROR_CONFIG["service_unavailable_rate"]
        + ERROR_CONFIG["bad_request_rate"]
    ):
        return "Bad Request", 400

    return None


@app.post("/270/")
def endpoint_270():
    network_error = random_error()
    if network_error:
        return network_error

    edi_error_response = get_edi_error_response()
    if edi_error_response:
        return edi_error_response, 200, {"Content-Type": "application/x-edi"}

    posted_data = request.get_data(as_text=True)
    response_content = posted_data if posted_data else samples.SAMPLE_271
    return response_content, 200, {"Content-Type": "application/x-edi"}


@app.post("/276/")
def endpoint_276():
    network_error = random_error()
    if network_error:
        return network_error
    return samples.SAMPLE_277, 200, {"Content-Type": "application/x-edi"}


@app.post("/278/")
def endpoint_278():
    network_error = random_error()
    if network_error:
        return network_error
    return samples.SAMPLE_278, 200, {"Content-Type": "application/x-edi"}
