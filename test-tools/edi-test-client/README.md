# EDI X12 27x Multi-Threaded Client & Mock Server Test Tool

## Overview

This tool provides comprehensive EDI X12 load testing with dynamic payload generation and error injection. It integrates with the DataGen module to create realistic EDI 270 transactions and tracks them using ST control numbers for production-compatible testing.

## Test Client Workflow

```mermaid
flowchart TD
    A[📋 Configure Test] --> B[🏭 Generate EDI Data]
    B --> C[🚀 Start Load Test]
    C --> D[📡 Send Requests]
    D --> E[📊 Collect Results]
    E --> F[📈 Generate Report]
    
    subgraph "DataGen"
        B1[Create EDI 270 Transactions]
        B2[Inject Errors]
    end
    
    subgraph "Load Testing"
        D1[HTTP Requests at Target RPS]
        D2[Track Connections]
    end
    
    subgraph "Analysis"
        E1[Response Processing]
        E2[Performance Metrics]
    end
    
    B --> B1
    D --> D1
    E --> E1
    
    classDef config fill:#e3f2fd,stroke:#1976d2
    classDef generation fill:#f3e5f5,stroke:#7b1fa2
    classDef testing fill:#e8f5e8,stroke:#388e3c
    classDef results fill:#fff8e1,stroke:#f57c00
    
    class A config
    class B,B1,B2 generation
    class C,D,D1,D2 testing
    class E,F,E1,E2 results
```

## Architecture

```mermaid
classDiagram
    class LoadClient {
        +start()
        +stop()
        +update_rps()
        +set_metadata_manager()
    }
    
    class RPSScheduler {
        +start_scheduling()
        +stop_scheduling()
        +update_rps()
    }
    
    class ResponseProcessor {
        +process_response()
        -_analyze_response()
    }
    
    class StatsCollector {
        +record_response()
        +snapshot()
    }
    
    class MetadataManager {
        +get_error_info()
        +load_metadata()
    }
    
    class EdiResponseAnalyzer {
        +categorize_edi_error()
        +has_edi_error()
    }
    
    class TrackedEDI270Generator {
        +generate_edi_270_payloads_with_metadata()
        +create_transaction()
    }
    
    LoadClient --> RPSScheduler : uses
    LoadClient --> ResponseProcessor : uses
    LoadClient --> StatsCollector : uses
    LoadClient --> MetadataManager : uses
    ResponseProcessor --> EdiResponseAnalyzer : uses
    ResponseProcessor --> StatsCollector : updates
    MetadataManager --> TrackedEDI270Generator : loads from
    RPSScheduler --> ResponseProcessor : callbacks
```

## Setup

### Prerequisites
- Python 3.8+
- Poetry (Python package manager)

### Installation
1. Clone the repository
   ```bash
   git clone https://github.com/dhagan-va/intern-2025.git
   ```
2. Navigate to test-tools/edi-test-client
   ```bash
   cd test-tools/edi-test-client
   ```
3. Create and start a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install dependencies with poetry
   ```bash
   pip install poetry
   poetry install
   ```

## Usage

### EDI Metadata Load Testing

Run EDI 270 metadata load tests with dynamic payload generation and error injection:


### Command Options
- `--transactions, -t`: Number of EDI transactions to generate and send (default: 10)
- `--rps, -r`: Requests per second rate (default: 5.0)
- `--error-rate, -e`: Error injection rate from 0.0 to 1.0 (default: 0.1)
- `--preset`: Use predefined configurations (`quick` or `stress`)
- `--output-metadata`: Save complete test results to JSON file
- `--verbose, -v`: Show detailed transaction information


### Starting the Mock Server

Before running the metadata load test, start the mock EDI server:

```bash
# In a separate terminal
./runserver.sh
```

The mock server will start on `http://localhost:5000` and handle EDI 270 requests.