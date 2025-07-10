import argparse
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "utils"))

from generate_payloads import generate_edi_270_payloads_with_metadata


def main():
    parser = argparse.ArgumentParser(
        description="Generate EDI 270 payloads for load testing"
    )

    parser.add_argument(
        "--messages",
        "-m",
        type=int,
        default=100,
        help="Number of EDI 270 messages per file (default: 100)",
    )
    parser.add_argument(
        "--error-rate",
        "-e",
        type=float,
        default=0.0,
        help="Error rate for intentional errors (0.0 to 1.0, default: 0.0)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="payloads",
        help="Output directory for payload files (default: payloads)",
    )
    parser.add_argument(
        "--metadata-file",
        type=str,
        help="Optional: Save transaction metadata to JSON file",
    )
    parser.add_argument(
        "--show-errors",
        action="store_true",
        help="Show details of transactions with errors",
    )

    args = parser.parse_args()

    if not (0.0 <= args.error_rate <= 1.0):
        print("Error: Error rate must be between 0.0 and 1.0")
        sys.exit(1)

    try:

        result = generate_edi_270_payloads_with_metadata(
            output_dir=args.output_dir,
            num_messages=args.messages,
            error_rate=args.error_rate,
        )

        if args.metadata_file:
            metadata_path = Path(args.metadata_file)
            with open(metadata_path, "w") as f:
                json.dump(result["metadata"], f, indent=2)
            print(f"\nMetadata saved to: {metadata_path}")
            print(
                "This file contains detailed transaction tracking data for load testing"
            )

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
