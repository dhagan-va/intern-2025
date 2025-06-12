# EDI X12 27x Multi-Threaded Client & Mock Server Test Tool

## Setup

### Prerequesites
Poetry is used for dependency management.
``` 
pip install poetry
```

### Installation
1. Clone the repository
   ```bash
   git clone https://github.com/dhagan-va/intern-2025.git
   ```
2. Navigate to test-tools/edi-test-client
3. Create and start a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
4. Install dependencies with poetry
   ```
   poetry install
   ```
5. Start mock Flask server
   ```
   ./runserver.sh
   ```
6. Start client
   ```
   ./runclient.sh
   ```
7. Run logs available in ```src/client/test.log```