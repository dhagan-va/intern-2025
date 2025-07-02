from flask import Flask
import random
import time
from . import samples

app = Flask(__name__)

ERROR_CONFIG = {
    "server_error_rate": 0.05,
    "timeout_rate": 0.03,
    "bad_gateway_rate": 0.02,
    "service_unavailable_rate": 0.02,
    "bad_request_rate": 0.01,
    "timeout_delay": 30.0,
}


def random_error():
    rand = random.random()

    if rand < ERROR_CONFIG["timeout_rate"]:
        time.sleep(ERROR_CONFIG["timeout_delay"])
        return None

    if rand < ERROR_CONFIG["timeout_rate"] + ERROR_CONFIG["server_error_rate"]:
        return "Internal Server Error", 500

    if rand < (
        ERROR_CONFIG["timeout_rate"]
        + ERROR_CONFIG["server_error_rate"]
        + ERROR_CONFIG["bad_gateway_rate"]
    ):
        return "Bad Gateway", 502

    if rand < (
        ERROR_CONFIG["timeout_rate"]
        + ERROR_CONFIG["server_error_rate"]
        + ERROR_CONFIG["bad_gateway_rate"]
        + ERROR_CONFIG["service_unavailable_rate"]
    ):
        return "Service Temporarily Unavailable", 503

    if rand < (
        ERROR_CONFIG["timeout_rate"]
        + ERROR_CONFIG["server_error_rate"]
        + ERROR_CONFIG["bad_gateway_rate"]
        + ERROR_CONFIG["service_unavailable_rate"]
        + ERROR_CONFIG["bad_request_rate"]
    ):
        return "Bad Request", 400

    return None


@app.post("/270/")
def endpoint_270():
    error = random_error()
    if error:
        return error
    return samples.SAMPLE_271


@app.post("/276/")
def endpoint_276():
    error = random_error()
    if error:
        return error
    return samples.SAMPLE_277


@app.post("/278/")
def endpoint_278():
    error = random_error()
    if error:
        return error
    return samples.SAMPLE_278
