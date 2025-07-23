import sys
import time
import json
import tempfile
from pathlib import Path
import argparse
import random
import string
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import load_settings
from client.load_client import LoadClient


EDI_270_TEMPLATE = """ISA*00*          *00*          *ZZ*SUBMITTER_ID  *ZZ*RECEIVER_ID   *{date}*{time}*^*00501*{isa_control}*0*P*:~
GS*HS*SUBMITTER_ID*RECEIVER_ID*{date}*{time}*{gs_control}*X*005010X279A1~
ST*270*{st_control}*005010X279A1~
BHT*0022*13*{trace_number}*{date}*{time}~
HL*1**20*1~
NM1*PR*2*HEALTH PLAN*****PI*HEALTH_PLAN_ID~
HL*2*1*21*1~
NM1*1P*2*PROVIDER NAME*****XX*{provider_npi}~
HL*3*2*22*0~
TRN*1*{trace_number}*{submitter_id}~
NM1*IL*1*{last_name}*{first_name}****MI*{member_id}~
DMG*D8*{birth_date}*{gender}~
DTP*291*D8*{service_date}~
EQ*30~
SE*13*{st_control}~
GE*1*{gs_control}~
IEA*1*{isa_control}~"""


def generate_random_string(length=8):
    """Generate a random alphanumeric string."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_random_npi():
    """Generate a random 10-digit NPI number."""
    return ''.join(random.choices(string.digits, k=10))


def generate_random_member_id():
    """Generate a random member ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


def generate_sample_270_payloads(num_transactions):
    """Generate multiple clean EDI 270 transactions for load testing."""
    transactions = []
    edi_lines = []
    
    current_date = datetime.now().strftime('%y%m%d')
    current_time = datetime.now().strftime('%H%M')
    
    first_names = ['JOHN', 'JANE', 'ROBERT', 'MARY', 'MICHAEL', 'PATRICIA', 'WILLIAM', 'JENNIFER']
    last_names = ['SMITH', 'JOHNSON', 'WILLIAMS', 'BROWN', 'JONES', 'GARCIA', 'MILLER', 'DAVIS']
    
    for i in range(num_transactions):
        isa_control = str(i + 1).zfill(9)
        gs_control = str(i + 1)
        st_control = str(i + 1).zfill(4)
        trace_number = generate_random_string(16)
        provider_npi = generate_random_npi()
        member_id = generate_random_member_id()
        submitter_id = "SUB" + generate_random_string(5)
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        gender = random.choice(['M', 'F'])
        
        birth_year = random.randint(1950, 2010)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  
        birth_date = f"{birth_year}{birth_month:02d}{birth_day:02d}"
        
        service_date = current_date
        
        edi_content = EDI_270_TEMPLATE.format(
            date=current_date,
            time=current_time,
            isa_control=isa_control,
            gs_control=gs_control,
            st_control=st_control,
            trace_number=trace_number,
            provider_npi=provider_npi,
            member_id=member_id,
            submitter_id=submitter_id,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            gender=gender,
            service_date=service_date
        )
        
        transaction_info = {
            'st_control_number': st_control,
            'trace_number': trace_number,
            'member_id': member_id,
            'beneficiary_id': f"{first_name} {last_name}",
            'provider_npi': provider_npi
        }
        transactions.append(transaction_info)
        
        edi_lines.extend(edi_content.strip().split('\n'))
    
    full_edi_content = '\n'.join(edi_lines)
    
    return {
        'edi_content': full_edi_content,
        'transactions': transactions,
        'summary': {
            'total_transactions': num_transactions,
            'file_size_bytes': len(full_edi_content.encode('utf-8')),
            'total_lines': len(edi_lines)
        }
    }


def create_metadata_for_client(payload_data):
    """Create metadata structure compatible with the load client."""
    return {
        'metadata': {
            'edi_payload': {
                'content': payload_data['edi_content'],
                'lines': payload_data['summary']['total_lines'],
                'format': 'EDI-270'
            },
            'file_info': {
                'filename': 'generated_270_payload.edi',
                'file_size_bytes': payload_data['summary']['file_size_bytes'],
                'total_lines': payload_data['summary']['total_lines']
            },
            'transactions': payload_data['transactions']
        },
        'summary': payload_data['summary']
    }


def run_simple_270_load_test(num_transactions, rps=10.0):
    """Run a simple EDI 270 load test using clean sample transactions."""
    calculated_duration = (num_transactions / rps) + 5.0
    max_duration = calculated_duration * 2.0

    print(f"=== Simple EDI 270 Load Test ===")
    print(f"Generating {num_transactions} clean EDI 270 transactions...")
    print(f"Target: {num_transactions} transactions at {rps} RPS")
    print(f"Calculated duration: {calculated_duration:.1f}s (max: {max_duration:.1f}s)")

    try:
        payload_data = generate_sample_270_payloads(num_transactions)
        
        print(f"✓ Generated {payload_data['summary']['total_transactions']} transactions")
        print(f"  - EDI payload size: {payload_data['summary']['file_size_bytes']} bytes")
        print(f"  - Total lines: {payload_data['summary']['total_lines']}")

    except Exception as e:
        return {"error": f"Failed to generate payloads: {str(e)}"}

    try:
        cfg = load_settings()
        cfg.rps = rps
        cfg.transaction = 270
        cfg.threads = max(10, int(rps * 0.1) + 5)

        client = LoadClient(cfg)

        metadata_structure = create_metadata_for_client(payload_data)
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            json.dump(metadata_structure, temp_file, indent=2)
            temp_metadata_path = temp_file.name

        try:
            from client.data.metadata_manager import MetadataManager
            metadata_manager = MetadataManager(temp_metadata_path)
            client.set_metadata_manager(metadata_manager)
            print(f"✓ Load client configured with metadata")
        except ImportError:
            print(f"✓ Load client configured")

        print(f"  - RPS: {rps}")
        print(f"  - Target transactions: {num_transactions}")
        print(f"  - Threads: {cfg.threads}")

    except Exception as e:
        return {"error": f"Failed to configure load client: {str(e)}"}

    print(f"\nStarting load test...")
    try:
        client.start()
        start_time = time.time()

        print("Monitoring progress...")
        check_interval = 0.5
        last_count = 0

        while True:
            current_time = time.time()
            elapsed = current_time - start_time

            current_stats = client._stats.snapshot()
            current_count = current_stats.get("count", 0)

            if current_count >= num_transactions:
                print(f"✓ Target reached: {current_count}/{num_transactions} transactions sent")
                break

            if elapsed > max_duration:
                print(f"⚠ Maximum duration reached ({max_duration:.1f}s), stopping at {current_count} transactions")
                break

            if current_count != last_count:
                progress_pct = (current_count / num_transactions) * 100
                current_rps = current_count / elapsed if elapsed > 0 else 0
                print(f"  Progress: {current_count}/{num_transactions} ({progress_pct:.1f}%) - {current_rps:.1f} RPS actual")
                last_count = current_count

            time.sleep(check_interval)

        print(f"Stopping load test...")
        client.stop()
        actual_duration = time.time() - start_time

    except Exception as e:
        if client._running:
            client.stop()
        return {"error": f"Load test failed: {str(e)}"}
    finally:
        try:
            Path(temp_metadata_path).unlink()
        except:
            pass

    time.sleep(0.5)

    try:
        final_stats = client._stats.snapshot()

        total_requests = final_stats.get("count", 0)
        edi_success_responses = final_stats.get("edi_success_count", 0)
        edi_error_responses = final_stats.get("edi_error_count", 0)
        http_error_responses = final_stats.get("http_error_count", 0)
        edi_errors_breakdown = final_stats.get("edi_errors", {})

        avg_latency = final_stats.get("avg_latency", 0)
        actual_rps = total_requests / actual_duration if actual_duration > 0 else 0
        edi_success_rate = (edi_success_responses / max(1, total_requests)) * 100
        completion_accuracy = (total_requests / num_transactions) * 100 if num_transactions > 0 else 0

        print(f"\n=== Test Results ===")
        print(f"  Target transactions: {num_transactions}")
        print(f"  Total requests sent: {total_requests}")
        print(f"  Completion accuracy: {completion_accuracy:.1f}% ({total_requests}/{num_transactions})")
        print(f"  EDI successful responses: {edi_success_responses}")
        print(f"  EDI error responses: {edi_error_responses}")
        print(f"  HTTP/Network errors: {http_error_responses}")
        print(f"  EDI success rate: {edi_success_rate:.1f}%")
        print(f"  Average latency: {avg_latency:.2f}ms")
        print(f"  Target RPS: {rps}, Actual RPS: {actual_rps:.1f}")
        print(f"  Duration: {actual_duration:.1f}s")

        return {
            "payload_data": {
                "file_info": {
                    "filename": "generated_270_payload.edi",
                    "file_size_bytes": payload_data['summary']['file_size_bytes'],
                    "total_lines": payload_data['summary']['total_lines']
                },
                "transactions": payload_data['transactions']
            },
            "test_results": {
                "target_transactions": num_transactions,
                "total_requests": total_requests,
                "completion_accuracy": completion_accuracy,
                "edi_success_count": edi_success_responses,
                "edi_error_count": edi_error_responses,
                "http_error_count": http_error_responses,
                "edi_error_breakdown": edi_errors_breakdown,
                "edi_success_rate": edi_success_rate,
                "avg_latency_ms": avg_latency,
                "target_rps": rps,
                "actual_rps": actual_rps,
                "duration_seconds": actual_duration
            },
            "summary": {
                "status": "completed",
                "generated_payloads": payload_data['summary']['total_transactions'],
                "requests_sent": total_requests,
                "edi_success_rate": edi_success_rate,
                "performance": f"{actual_rps:.1f} RPS avg",
                "completion": f"{total_requests}/{num_transactions} transactions sent"
            }
        }

    except Exception as e:
        return {"error": f"Failed to collect results: {str(e)}"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple EDI 270 Load Testing - Clean transactions only"
    )

    parser.add_argument(
        "--transactions", "-t", type=int, default=10,
        help="Number of transactions to generate and send (default: 10)"
    )

    parser.add_argument(
        "--rps", "-r", type=float, default=5.0,
        help="Requests per second rate (default: 5.0)"
    )

    parser.add_argument(
        "--preset", choices=["quick", "stress", "minimal"],
        help="Use a preset test configuration"
    )

    parser.add_argument(
        "--output", "-o", type=str,
        help="Save results to JSON file"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show detailed transaction information"
    )

    args = parser.parse_args()

    if args.transactions <= 0:
        print("Error: Number of transactions must be positive")
        sys.exit(1)

    if args.rps <= 0:
        print("Error: RPS must be positive")
        sys.exit(1)

    if args.preset:
        if args.preset == "quick":
            args.transactions = 50
            args.rps = 10.0
        elif args.preset == "stress":
            args.transactions = 1000
            args.rps = 50.0
        elif args.preset == "minimal":
            args.transactions = 10
            args.rps = 5.0

    print("=== Simple EDI 270 Load Testing ===\n")
    
    if args.preset:
        print(f"Using preset: {args.preset}")
    else:
        print(f"Custom configuration:")
    
    print(f"  Transactions: {args.transactions}")
    print(f"  RPS: {args.rps}")
    print()

    result = run_simple_270_load_test(
        num_transactions=args.transactions,
        rps=args.rps
    )

    if "error" in result:
        print(f"❌ Test failed: {result['error']}")
        sys.exit(1)
    else:
        print(f"\n✓ Test completed successfully!")
        print(f"  Generated: {result['summary']['generated_payloads']} payloads")
        print(f"  Sent: {result['summary']['requests_sent']} requests")
        print(f"  EDI Success rate: {result['summary']['edi_success_rate']:.1f}%")
        print(f"  Performance: {result['summary']['performance']}")

        if args.verbose and result['payload_data']['transactions']:
            print(f"\nSample Transactions:")
            for i, txn in enumerate(result['payload_data']['transactions'][:5], 1):
                print(f"  {i}. ST#{txn['st_control_number']} - {txn['beneficiary_id']}")

            if len(result['payload_data']['transactions']) > 5:
                print(f"  ... and {len(result['payload_data']['transactions']) - 5} more")

        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\nResults saved to: {args.output}")