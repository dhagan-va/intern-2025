import os
import sys
from pathlib import Path
from datetime import datetime
import shutil
import subprocess


def run_datagen_270(num_messages: int = 100, error_rate: float = 0.0):
    current_file = Path(__file__).resolve()
    datagen_root = current_file.parent.parent.parent.parent.parent / "DataGen"
    
    if not datagen_root.exists():
        raise FileNotFoundError(f"DataGen directory not found at {datagen_root}")
    
    script_content = f"""
import sys
sys.path.insert(0, 'src')
from RunGenerator import Run270Generator, GenerateSponsors, CreateClaimDB
from Config import Config
from datetime import date, timedelta
from Repository.DatabaseFactory import get_database_backend

db = get_database_backend()
current_users = db.total_beneficiaries()

if current_users < {num_messages}:
    GenerateSponsors({num_messages})

today = date.today()
CreateClaimDB({num_messages}, today, "Created")

Run270Generator(num_messages={num_messages}, error_rate={error_rate}, upload_s3=False)
output_path = Config.get_edi_path(Config.EDI270_PATH, Config.EDI270_FILE_NAME)
print(f"GENERATED_FILE: {{output_path}}")
"""
    
    temp_script = datagen_root / "temp_270_gen.py"
    with open(temp_script, 'w') as f:
        f.write(script_content)
    
    try:
        result = subprocess.run(
            ["poetry", "run", "python", "temp_270_gen.py"],
            cwd=datagen_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"DataGen 270 generation failed: {result.stderr}")
        
        for line in result.stdout.split('\n'):
            if line.startswith("GENERATED_FILE: "):
                return line.replace("GENERATED_FILE: ", "").strip()
        
        raise RuntimeError("Could not find generated file path in output")
        
    finally:
        if temp_script.exists():
            temp_script.unlink()


def generate_edi_270_payloads(output_dir: str = "payloads", num_messages: int = 100, error_rate: float = 0.0):
    payload_dir = Path(__file__).parent.parent / "client" / output_dir
    payload_dir.mkdir(exist_ok=True)
    
    datagen_file_path = run_datagen_270(num_messages=num_messages, error_rate=error_rate)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload_filename = f"edi_270_{timestamp}_{num_messages}msgs.edi"
    payload_file_path = payload_dir / payload_filename
    
    shutil.copy2(datagen_file_path, payload_file_path)
    
    return [str(payload_file_path)]


if __name__ == "__main__":
    print("Generating EDI 270 payloads...")
    files = generate_edi_270_payloads(num_messages=100, error_rate=0.0)
    print(f"Generated: {files}")