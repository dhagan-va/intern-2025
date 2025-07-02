from flask import Flask, jsonify, request
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
    """Starts the current client instance."""
    client = get_client()
    if client._running:
        return jsonify({"message": "Client already running"}), 400
    client.start()
    return jsonify({"message": "Client started"})


@app.post("/stop")
def stop_client():
    """Stops the current client instance"""
    client = get_client()
    if not client._running:
        return jsonify({"message": "Client not running"}), 400
    client.stop()
    return jsonify({"message": "Client stopped"})


@app.post("/reset")
def reset_client():
    """Reset the client - stops current instance and creates a new one"""
    global client_instance

    if client_instance and client_instance._running:
        client_instance.stop()

    cfg = load_settings()
    client_instance = LoadClient(cfg)

    return jsonify({"message": "Client reset successfully"})


@app.get("/status")
def get_status():
    """Get current client status including running state and configuration"""
    client = get_client()
    return jsonify(
        {
            "running": client._running,
            "rps": client.rps,
            "transaction": client.transaction,
            "threads": client.threads,
            "endpoint": client.endpoints.get(client.transaction, "Unknown"),
        }
    )


@app.get("/stats")
def get_stats():
    """Get live statistics from the client"""
    client = get_client()
    stats = client._stats.snapshot()
    return jsonify(
        {
            "total_requests": stats.get("count", 0),
            "average_latency": stats.get("avg_latency", 0),
            "status_codes": stats.get("codes", {}),
            "successful_requests": stats.get("codes", {}).get(200, 0),
            "failed_requests": stats.get("count", 0)
            - stats.get("codes", {}).get(200, 0),
            "current_rps": client.rps,
            "timestamp": stats.get("timestamp"),
        }
    )


@app.post("/rps")
def update_rps():
    """Update requests per second dynamically"""
    data = request.get_json()
    if not data or "rps" not in data:
        return jsonify({"error": "RPS value required"}), 400

    try:
        new_rps = float(data["rps"])
        if new_rps <= 0:
            return jsonify({"error": "RPS must be greater than 0"}), 400

        client = get_client()
        client.update_rps(new_rps)
        return jsonify({"message": f"RPS updated to {new_rps}"})
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid RPS value"}), 400


@app.post("/transaction")
def update_transaction():
    """Update transaction type (270, 276, or 278)"""
    data = request.get_json()
    if not data or "transaction" not in data:
        return jsonify({"error": "Transaction value required"}), 400

    try:
        new_transaction = int(data["transaction"])
        valid_transactions = [270, 276, 278]
        if new_transaction not in valid_transactions:
            return (
                jsonify(
                    {
                        "error": f"Invalid transaction. Must be one of {valid_transactions}"
                    }
                ),
                400,
            )

        client = get_client()
        client.update_transaction(new_transaction)
        return jsonify({"message": f"Transaction updated to {new_transaction}"})
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid transaction value"}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
