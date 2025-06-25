from flask import Flask
from samples import SAMPLE_271, SAMPLE_277, SAMPLE_278
app = Flask(__name__)


@app.post("/270/")
def endpoint_270():
    return SAMPLE_271

@app.post("/276")
def endpoint_276():
    return SAMPLE_277

@app.post("/278")
def endpoint_278():
    return SAMPLE_278