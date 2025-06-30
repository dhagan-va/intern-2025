from flask import Flask, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import load_settings
from client.load_client import LoadClient

app = Flask(__name__)
CORS(app)
client_instance = None

def get_client():
    global client_instance
    if client_instance is None:
        cfg = load_settings()
        client_instance = LoadClient(cfg)
    return client_instance
    

@app.post("/start")
def start_client():
    client = get_client()
    client.start()
    return jsonify({'message': 'Client started'})

@app.post("/stop")
def stop_client():
    client = get_client()
    client.stop()
    return jsonify({'message': 'Client stopped'})