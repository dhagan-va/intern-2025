# EDI Test Client Project - Current State

*Last Updated: July 25, 2025*

## Architecture

### Core Components

The project follows a modular architecture with clear separation of concerns:

```
LoadClient (Main Orchestrator)
├── RPSScheduler (Request Rate Control)
├── StatsCollector (Metrics & Analytics)
├── ResponseProcessor (Response Handling)
├── MetadataManager (Error Injection)
├── ConnectionTracker (Connection Monitoring)
└── ThreadPoolExecutor (Concurrency)
```

### 1. **LoadClient** (`backend/src/client/load_client.py`)
**Status: ✅ Working**
- Main orchestrator that coordinates all components
- Manages lifecycle (start/stop) and configuration updates
- Supports EDI transactions: 270, 276, 278
- Thread-safe operations with proper locking
- Runtime configuration updates for RPS, transaction type, max connections

**Key Features:**
- Dynamic RPS adjustment during runtime
- Connection throttling with configurable limits
- Metadata-driven error injection
- CSV result export
- Comprehensive logging

### 2. **RPSScheduler** (`backend/src/client/core/rps_scheduler.py`)
**Status: ✅ Working with Connection Throttling**
- Controls request rate to maintain target RPS
- Implements connection throttling to prevent overwhelming the server
- Background thread with precise timing control
- Thread-safe RPS updates

**Key Features:**
- Maintains target RPS with sub-second precision
- Connection limit enforcement (default: 150 concurrent)
- Throttling statistics and logging
- Automatic catch-up when behind target
- Graceful degradation when connection limits are reached

### 3. **StatsCollector** (`backend/src/client/statistics/stats_collector.py`)
**Status: ✅ Working - Enhanced EDI Analytics**
- **LiveStats**: HTTP-level metrics (latency, status codes)
- **EdiStatsTracker**: EDI-specific error categorization
- **ConnectionTracker**: Concurrent connection monitoring

**Metrics Tracked:**
- HTTP response times and status codes
- EDI error types (Format, Member, Amount, Validation)
- Concurrent connection counts and peaks
- Success/failure rates with EDI vs HTTP distinction
- Real-time statistics via API endpoints

### 4. **ResponseProcessor** (`backend/src/client/processing/response_processor.py`)
**Status: ✅ Working**
- Processes HTTP responses and categorizes EDI errors
- Updates statistics and writes results to CSV
- Integrates with EdiResponseAnalyzer for intelligent error detection

### 5. **MetadataManager** (`backend/src/client/data/metadata_manager.py`)
**Status: ✅ Working**
- Loads error metadata from JSON files
- Provides transaction-specific error information
- Enables header-based error injection for load testing

## Frontend Dashboard

### React Web UI (`frontend/`)
**Status: ❌ Abandoned**


## Load Testing Scripts

### 1. **Metadata Load Test** (`backend/src/client/metadata_load_test.py`)
**Status: ❌ Broken**
- Integrates with DataGen module for realistic EDI 270 transactions
- Currently not working due to changes made in DataGen

### 2. **Simple Load Test** (`backend/src/client/testing/simple_270_load_test.py`)
**Status: ✅ Working**
- Standalone test with generated clean EDI 270 transactions
- No external dependencies on DataGen
- Connection throttling demonstration
- Command-line interface with presets

