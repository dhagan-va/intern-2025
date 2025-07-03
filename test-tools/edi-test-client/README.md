# EDI X12 27x Multi-Threaded Client & Mock Server Test Tool

## Architecture

```mermaid
graph TB
    Frontend[React Frontend<br/>Web Dashboard<br/>Port 5173]
    
    API[Client API<br/>Flask Server<br/>Port 5001]
    
    LoadClient[Load Test Client<br/>Multi-threaded]
    
    MockServer[Mock EDI Server<br/>Flask Server<br/>Port 5000]
    
    Frontend -->|HTTP Requests| API
    API -->|Start/Stop/Config| LoadClient
    LoadClient -->|EDI Transactions| MockServer
    MockServer -->|EDI Responses| LoadClient
    LoadClient -->|Statistics| API
    API -->|Live Data| Frontend
    
    classDef frontend fill:#e1f5fe,stroke:#01579b
    classDef server fill:#f3e5f5,stroke:#4a148c
    classDef client fill:#e8f5e8,stroke:#1b5e20
    
    class Frontend frontend
    class API,MockServer server
    class LoadClient client
```

## Setup

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
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

### Frontend Setup
5. Navigate to frontend directory
   ```bash
   cd frontend
   ```
6. Install frontend dependencies
   ```bash
   npm install
   ```
7. Start the frontend development server
   ```bash
   npm run dev
   ```

### Running the Application
8. Start mock Flask server (in new terminal)
   ```bash
   cd test-tools/edi-test-client
   source .venv/bin/activate
   ./runserver.sh
   ```
9. Start the API backend (in new terminal)
   ```bash
   cd test-tools/edi-test-client
   source .venv/bin/activate
   python backend/src/client_api/api.py
   ```
10. Access the web dashboard at `http://localhost:5173`

### Testing
11. Run unit tests
    ```bash
    python -m pytest tests/ -v
    ```
12. Run with coverage
    ```bash
    python -m pytest tests/ --cov=backend/src --cov-report=html
    ```

### Command Line Usage
Alternatively, run the client directly from command line:
```bash
./runclient.sh
```

### Logs
- Backend logs: `backend/src/client/test.log`
- API logs: `backend/src/client_api/test.log`
- Frontend logs: Browser console

## Usage

1. **Web Dashboard**: Access `http://localhost:5173` for the React frontend
2. **Mock Server**: Runs on `http://localhost:5000`
3. **API Backend**: Runs on `http://localhost:5001`

### Configuration
- Default settings: `backend/src/conf/default.toml`
- Modify RPS, transaction types, and endpoints through the web interface