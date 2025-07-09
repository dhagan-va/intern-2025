from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import logging
import time
import threading


def setup_simple_logging():
    """Simple logging setup for edi-test-client."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


logger = setup_simple_logging()


def monitor_error_injections(datagen_root: Path, duration: int = 60):
    """Monitor DataGen logs specifically for error injection messages."""
    log_dir = datagen_root / "src" / "Output" / "Logs"
    today = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"TestSuite_{today}.log"

    if not log_file.exists():
        logger.warning(f"DataGen log file not found: {log_file}")
        return []

    logger.info("Monitoring DataGen for error injections...")
    initial_size = log_file.stat().st_size if log_file.exists() else 0
    error_transactions = []

    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            current_size = log_file.stat().st_size

            if current_size > initial_size:
                with open(log_file, "r", encoding="utf-8") as f:
                    f.seek(initial_size)
                    new_content = f.read()

                    for line in new_content.splitlines():
                        if "[ERROR INSERTED] Transaction" in line:
                            try:
                                trans_num = line.split("Transaction ")[1].strip()
                                if trans_num not in error_transactions:
                                    error_transactions.append(trans_num)
                                    logger.warning(
                                        f"Error injected in transaction: {trans_num}"
                                    )
                            except (IndexError, ValueError):
                                pass

                initial_size = current_size

            time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error monitoring DataGen logs: {e}")
            break

    if error_transactions:
        logger.info(
            f"Total transactions with errors: {len(error_transactions)} - {error_transactions}"
        )
    else:
        logger.info("No error injections detected")

    return error_transactions


def run_datagen_270(num_messages: int = 1000, error_rate: float = 0.005):
    current_file = Path(__file__).resolve()
    datagen_root = current_file.parent.parent.parent.parent.parent / "DataGen"

    if not datagen_root.exists():
        raise FileNotFoundError(f"DataGen directory not found at {datagen_root}")

    script_content = f"""
import sys
sys.path.insert(0, 'src')
from RunGenerator import Run270Generator, GenerateSponsors, CreateClaimDB
from Config import Config
from datetime import date
from Repository.DatabaseFactory import get_database_backend

db = get_database_backend()
if db.total_beneficiaries() < {num_messages}:
    GenerateSponsors({num_messages})

CreateClaimDB({num_messages}, date.today(), "Created")
Run270Generator(num_messages={num_messages}, error_rate={error_rate}, upload_s3=False)

output_path = Config.get_edi_path(Config.EDI270_PATH, Config.EDI270_FILE_NAME)
print(f"GENERATED_FILE: {{output_path}}")
"""

    temp_script = datagen_root / "temp_270_gen.py"
    with open(temp_script, "w") as f:
        f.write(script_content)

    error_transactions = []
    monitor_thread = threading.Thread(
        target=lambda: error_transactions.extend(
            monitor_error_injections(datagen_root, 30)
        ),
        daemon=True,
    )
    monitor_thread.start()

    try:
        result = subprocess.run(
            ["poetry", "run", "python", "temp_270_gen.py"],
            cwd=datagen_root,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"DataGen 270 generation failed: {result.stderr}")

        monitor_thread.join(timeout=5)

        for line in result.stdout.split("\n"):
            if line.startswith("GENERATED_FILE: "):
                return line.replace("GENERATED_FILE: ", "").strip()

        raise RuntimeError("Could not find generated file path in output")

    finally:
        if temp_script.exists():
            temp_script.unlink()


def generate_edi_270_payloads(
    output_dir: str = "payloads", num_messages: int = 100, error_rate: float = 0.0
):
    payload_dir = Path(__file__).parent.parent / "client" / output_dir
    payload_dir.mkdir(exist_ok=True)

    logger.info(
        f"Generating {num_messages} EDI 270 messages with {error_rate} error rate"
    )

    datagen_file_path = run_datagen_270(
        num_messages=num_messages, error_rate=error_rate
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload_filename = f"edi_270_{timestamp}_{num_messages}msgs.edi"
    payload_file_path = payload_dir / payload_filename

    shutil.copy2(datagen_file_path, payload_file_path)

    logger.info(f"Generated: {payload_filename}")
    return [str(payload_file_path)]


if __name__ == "__main__":
    files = generate_edi_270_payloads(num_messages=100, error_rate=0.0)
    print(f"Generated: {files}")