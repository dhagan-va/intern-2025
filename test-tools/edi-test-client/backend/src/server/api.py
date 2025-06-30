from flask import Flask
from flask_cors import CORS
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from client import load_client

app = Flask(__name__)
