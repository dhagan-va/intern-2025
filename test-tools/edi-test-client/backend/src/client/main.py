from load_client import LoadClient
import threading
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import load_settings
import time


def rps_listener(client: LoadClient):
    while client._running:
        print("Enter r to update RPS, t for endpoint, or q to quit.")
        line = input()
        line = line.strip()
        if line.lower() == "q":
            client.stop()
        elif line.lower() == "r":
            line = input()
            line = line.strip()
            client.update_rps(float(line))
        elif line.lower == "t":
            line = input()
            line = line.strip()
            client.update_rps(float(line))
        else:
            client.update_rps(float(line))


def main():
    cfg = load_settings()
    client = LoadClient(cfg)
    client.start()

    rps_thread = threading.Thread(target=rps_listener, args=(client,), daemon=True)
    rps_thread.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.stop()


if __name__ == "__main__":
    main()
