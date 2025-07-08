#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "utils"))

from generate_payloads import generate_edi_270_payloads


def main():
    parser = argparse.ArgumentParser(description="Generate EDI 270 payloads for load testing")
    
    parser.add_argument("--messages", "-m", type=int, default=100, 
                       help="Number of EDI 270 messages per file (default: 100)")
    parser.add_argument("--error-rate", "-e", type=float, default=0.0,
                       help="Error rate for intentional errors (0.0 to 1.0, default: 0.0)")
    parser.add_argument("--output-dir", "-o", type=str, default="payloads",
                       help="Output directory for payload files (default: payloads)")
    
    args = parser.parse_args()
    
    if not (0.0 <= args.error_rate <= 1.0):
        print("Error: Error rate must be between 0.0 and 1.0")
        sys.exit(1)
    
    try:
        print(f"Generating EDI 270 payload...")
        print(f"Messages: {args.messages}")
        print(f"Error rate: {args.error_rate}")
        print(f"Output directory: {args.output_dir}")
        
        files = generate_edi_270_payloads(
            output_dir=args.output_dir,
            num_messages=args.messages,
            error_rate=args.error_rate
        )
        
        print(f"\nGenerated: {files[0]}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()