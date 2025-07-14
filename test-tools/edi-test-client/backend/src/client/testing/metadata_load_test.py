"""
Simple callable interface for generating EDI 270 payloads and running load tests.
Generates payloads, passes them via dictionary, and runs with preset RPS.
"""

import sys
import time
import json
import tempfile
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
sys.path.insert(0, str(Path(__file__).parent.parent))


from utils.generate_payloads import generate_edi_270_payloads_with_metadata
from config import load_settings
from client.load_client import LoadClient
from client.metadata_manager import MetadataManager


def run_metadata_load_test(num_transactions, rps=10.0, error_rate=0.0):
    calculated_duration = (num_transactions / rps) + 5.0  
    max_duration = calculated_duration * 2.0  
    
    print(f"=== EDI 270 Load Test with Header-Based Error Categorization ===")
    print(f"Generating {num_transactions} EDI 270 transactions...")
    print(f"Target: {num_transactions} transactions at {rps} RPS")
    print(f"Calculated duration: {calculated_duration:.1f}s (max: {max_duration:.1f}s)")

    try:
        payload_result = generate_edi_270_payloads_with_metadata(
            num_messages=num_transactions, error_rate=error_rate
        )

        print(
            f"✓ Generated {payload_result['summary']['total_transactions']} transactions"
        )
        print(
            f"  - Clean transactions: {payload_result['summary']['clean_transactions']}"
        )
        print(
            f"  - Error transactions: {payload_result['summary']['error_transactions']}"
        )
        print(
            f"  - EDI payload size: {payload_result['metadata']['file_info']['file_size_bytes']} bytes"
        )
        
        if payload_result['metadata']['error_breakdown']:
            print(f"  - Error breakdown: {payload_result['metadata']['error_breakdown']}")

    except Exception as e:
        return {"error": f"Failed to generate payloads: {str(e)}"}

    try:
        cfg = load_settings()
        cfg.rps = rps
        cfg.transaction = 270

        client = LoadClient(cfg)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(payload_result, temp_file, indent=2)
            temp_metadata_path = temp_file.name
        
        metadata_manager = MetadataManager(temp_metadata_path)
        client.set_metadata_manager(metadata_manager)

        print(f"✓ Load client configured with header-based error categorization")
        print(f"  - RPS: {rps}")
        print(f"  - Target transactions: {num_transactions}")
        print(f"  - Transaction type: EDI 270")
        
        metadata_summary = metadata_manager.get_error_summary()
        print(f"  - Metadata loaded: {metadata_summary.get('total_transactions', 0)} transactions")
        print(f"  - Error transactions: {metadata_summary.get('error_transactions', 0)}")
        if metadata_summary.get('error_breakdown'):
            print(f"  - Error types: {list(metadata_summary['error_breakdown'].keys())}")

    except Exception as e:
        return {"error": f"Failed to configure load client: {str(e)}"}

    print(f"\nStarting load test with header-based error simulation...")
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
                print(f"Target reached: {current_count}/{num_transactions} transactions sent")
                break
                
            if elapsed > max_duration:
                print(f"Maximum duration reached ({max_duration:.1f}s), stopping at {current_count} transactions")
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
        
        total_error_responses = edi_error_responses + http_error_responses
        avg_latency = final_stats.get("avg_latency", 0)
        actual_rps = total_requests / actual_duration if actual_duration > 0 else 0
        edi_success_rate = (edi_success_responses / max(1, total_requests)) * 100
        
        completion_accuracy = (total_requests / num_transactions) * 100 if num_transactions > 0 else 0

        print(f"\nTest Results with EDI Error Categorization:")
        print(f"  - Target transactions: {num_transactions}")
        print(f"  - Total requests sent: {total_requests}")
        print(f"  - Completion accuracy: {completion_accuracy:.1f}% ({total_requests}/{num_transactions})")
        print(f"  - EDI successful responses: {edi_success_responses}")
        print(f"  - Error Response Breakdown:")
        print(f"    - EDI Format errors: {edi_errors_breakdown.get('edi_format_error', 0)}")
        print(f"    - EDI Member errors: {edi_errors_breakdown.get('edi_member_error', 0)}")
        print(f"    - EDI Amount errors: {edi_errors_breakdown.get('edi_amt_error', 0)}")
        print(f"    - EDI Validation errors: {edi_errors_breakdown.get('edi_validation_error', 0)}")
        print(f"    - EDI Other errors: {edi_errors_breakdown.get('edi_other_error', 0)}")
        print(f"    - HTTP/Network errors: {http_error_responses}")
        print(f"  - EDI success rate: {edi_success_rate:.1f}%")
        print(f"  - Average latency: {avg_latency:.2f}ms")
        print(f"  - Target RPS: {rps}, Actual RPS: {actual_rps:.1f}")
        print(f"  - Actual duration: {actual_duration:.1f}s")

        return {
            "payload_data": {
                "edi_content": payload_result["metadata"]["edi_payload"]["content"],
                "edi_lines": payload_result["metadata"]["edi_payload"]["lines"],
                "file_info": payload_result["metadata"]["file_info"],
                "transactions": payload_result["metadata"]["transactions"],
                "error_summary": payload_result["metadata"]["error_summary"],
            },
            "test_results": {
                "target_transactions": num_transactions,
                "total_requests": total_requests,
                "completion_accuracy": completion_accuracy,
                "edi_success_responses": edi_success_responses,
                "edi_error_responses": edi_error_responses,
                "http_error_responses": http_error_responses,
                "edi_error_breakdown": edi_errors_breakdown,
                "edi_success_rate": edi_success_rate,
                "avg_latency_ms": avg_latency,
                "target_rps": rps,
                "actual_rps": actual_rps,
                "duration_seconds": actual_duration,
                "calculated_duration": calculated_duration,
                "max_duration": max_duration,
            },
            "transaction_tracking": {
                "generated_count": payload_result["summary"]["total_transactions"],
                "generated_errors": payload_result["summary"]["error_transactions"],
                "sent_count": total_requests,
                "response_errors": total_error_responses,
                "tracking_data": payload_result["metadata"]["transactions"],
            },
            "summary": {
                "status": "completed",
                "generated_payloads": payload_result["summary"]["total_transactions"],
                "requests_sent": total_requests,
                "target_requests": num_transactions,
                "completion_accuracy": f"{completion_accuracy:.1f}%",
                "edi_success_rate": edi_success_rate,
                "performance": f"{actual_rps:.1f} RPS avg",
                "completion": f"{total_requests}/{num_transactions} transactions sent",
                "error_categorization": "edi-aware-header-based",
            },
        }

    except Exception as e:
        return {"error": f"Failed to collect results: {str(e)}"}


def quick_test(num_transactions=10, rps=5.0):
    return run_metadata_load_test(
        num_transactions=num_transactions, rps=rps, error_rate=0.1
    )


def stress_test(num_transactions=100, rps=50.0):
    return run_metadata_load_test(
        num_transactions=num_transactions, rps=rps, error_rate=0.02
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="EDI 270 Metadata Load Testing - Generate payloads and run load tests"
    )

    parser.add_argument(
        "--transactions",
        "-t",
        type=int,
        default=10,
        help="Number of transactions to generate and send (default: 10)",
    )

    parser.add_argument(
        "--rps",
        "-r",
        type=float,
        default=5.0,
        help="Requests per second rate (default: 5.0)",
    )

    parser.add_argument(
        "--error-rate",
        "-e",
        type=float,
        default=0.1,
        help="Error injection rate 0.0 to 1.0 (default: 0.1)",
    )

    parser.add_argument(
        "--preset", choices=["quick", "stress"], help="Use a preset test configuration"
    )

    parser.add_argument(
        "--output-metadata", type=str, help="Save metadata to JSON file"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed transaction information",
    )

    args = parser.parse_args()

    if not (0.0 <= args.error_rate <= 1.0):
        print("Error: Error rate must be between 0.0 and 1.0")
        sys.exit(1)

    if args.transactions <= 0:
        print("Error: Number of transactions must be positive")
        sys.exit(1)

    if args.rps <= 0:
        print("Error: RPS must be positive")
        sys.exit(1)

    calculated_duration = (args.transactions / args.rps) + 5.0
    
    print("=== EDI 270 Metadata Load Testing ===\n")

    if args.preset == "quick":
        print("Using quick test preset...")
        result = quick_test(num_transactions=5, rps=3.0)
    elif args.preset == "stress":
        print("Using stress test preset...")
        result = stress_test(num_transactions=50, rps=20.0)
    else:
        print(f"Running custom test:")
        print(f"  Transactions: {args.transactions}")
        print(f"  RPS: {args.rps}")
        print(f"  Calculated duration: {calculated_duration:.1f}s")
        print(f"  Error rate: {args.error_rate}")
        print()

        result = run_metadata_load_test(
            num_transactions=args.transactions,
            rps=args.rps,
            error_rate=args.error_rate,
        )

    if "error" in result:
        print(f"Test failed: {result['error']}")
        sys.exit(1)
    else:
        print(f"   Test completed successfully!")
        print(f"   Generated: {result['summary']['generated_payloads']} payloads")
        print(f"   Sent: {result['summary']['requests_sent']} requests")
        print(f"   EDI Success rate: {result['summary']['edi_success_rate']:.1f}%")
        print(f"   Performance: {result['summary']['performance']}")
        print(f"   Completion: {result['summary']['completion']}")

        if args.verbose:
            print(f"\nDetailed Results:")
            print(f"  Payload Details:")
            print(
                f"    - EDI content size: {result['payload_data']['file_info']['file_size_bytes']} bytes"
            )
            print(
                f"    - Total lines: {result['payload_data']['file_info']['total_lines']}"
            )
            print(
                f"    - Generated errors: {result['payload_data']['error_summary']['total_errors']}"
            )

            print(f"  Performance Metrics:")
            print(
                f"    - Average latency: {result['test_results']['avg_latency_ms']:.2f}ms"
            )
            print(f"    - Target RPS: {result['test_results']['target_rps']}")
            print(f"    - Actual RPS: {result['test_results']['actual_rps']:.2f}")
            print(f"    - Calculated duration: {result['test_results']['calculated_duration']:.1f}s")
            print(f"    - Actual duration: {result['test_results']['duration_seconds']:.1f}s")

            print(f"  Transaction Breakdown:")
            for i, txn in enumerate(
                result["payload_data"]["transactions"][:5], 1
            ):  
                print(
                    f"    {i}. ST#{txn['st_control_number']} - {txn['beneficiary_id']} - "
                    f"{'ERROR' if txn['error_injected'] else 'CLEAN'}"
                )

            if len(result["payload_data"]["transactions"]) > 5:
                print(
                    f"    ... and {len(result['payload_data']['transactions']) - 5} more"
                )

        if args.output_metadata:
            import json

            with open(args.output_metadata, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\nFull results saved to: {args.output_metadata}")
