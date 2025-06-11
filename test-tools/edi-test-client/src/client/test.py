from load_client import LoadClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import load_settings
import time

def main():
    cfg = load_settings()
    client = LoadClient(cfg)
    client.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.stop()

if __name__ == "__main__":
    main()