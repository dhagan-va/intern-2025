from flask import Flask
from . import samples
app = Flask(__name__)


@app.post("/270/")
def endpoint_270():
    return samples.SAMPLE_271

@app.post("/276/")
def endpoint_276():
    return samples.SAMPLE_277

@app.post("/278/")
def endpoint_278():
    return samples.SAMPLE_278