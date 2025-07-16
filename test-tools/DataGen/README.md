# EDI X12 Healthcare File Generator Suite

## Architecture

```mermaid
graph TD
    Generator["RunGenerator.py<br/>Main Script Execution"]
    SponsorGen["Sponsor & Beneficiary<br/>Data Generation"]
    ClaimGen["Claim Transaction<br/>Creation (270, 837, 277CA, 835, 834)"]
    EDIGen["EDI Generators<br/>270, 837, 277CA, 835, 834, 999"]
    S3Upload["Optional S3 Upload<br/>via boto3"]
    Markdown["Markdown Report<br/>Stats & Charts"]

    Generator --> SponsorGen
    SponsorGen --> ClaimGen
    ClaimGen --> EDIGen
    EDIGen --> S3Upload
    EDIGen --> Markdown

    classDef gen fill:#e1f5fe,stroke:#01579b
    classDef edi fill:#f3e5f5,stroke:#4a148c
    classDef data fill:#e8f5e8,stroke:#1b5e20

    class Generator gen
    class SponsorGen,ClaimGen data
    class EDIGen,S3Upload,Markdown edi
```

## Database ERD

```mermaid
erDiagram
    sponsors ||--o{ beneficiaries : has
    beneficiaries ||--o{ claim_transactions : has
    beneficiaries ||--o{ deductibles : has
    beneficiaries ||--o{ visit_counts : has

    sponsors {
        TEXT sponsor_id
        TEXT ssn
        TEXT dob
        TEXT first_name
        TEXT middle_name
        TEXT last_name
        TEXT gender
        TEXT phone
        TEXT insurance_company
        TEXT insurance_FID
        TEXT building_number
        TEXT street
        TEXT apartment
        TEXT city
        TEXT state
        TEXT zipcode
    }

    beneficiaries {
        TEXT sponsor_id
        TEXT beneficiary_id
        TEXT ssn
        TEXT dob
        TEXT first_name
        TEXT middle_name
        TEXT last_name
        TEXT gender
        TEXT phone
        TEXT insurance_company
        TEXT insurance_FID
        TEXT relationship
        TEXT building_number
        TEXT street
        TEXT apartment
        TEXT city
        TEXT state
        TEXT zipcode
    }

    claim_transactions {
        TEXT claim_id
        TEXT status
        TEXT date
        TEXT service_line_id
        TEXT sponsor_id
        TEXT beneficiary_id
        TEXT provider_npi
        TEXT provider_name
        TEXT provider_entity_type
        TEXT provider_address_1
        TEXT provider_address_2
        TEXT provider_city
        TEXT provider_state
        TEXT provider_zip
        TEXT provider_phone
        REAL amount
        TEXT payer_claim_id
    }

    deductibles {
        TEXT sponsor_id
        TEXT beneficiary_id
        TEXT code
        REAL amount
    }

    visit_counts {
        TEXT sponsor_id
        TEXT beneficiary_id
        TEXT code
        INTEGER count
    }
```

---

## Setup

### Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/dhagan-va/intern-2025.git
    cd test-tools/DataGen
    ```

2. Create and start a virtual environment

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
   
3. Install dependencies with poetry

   ```bash
   pip install poetry
   poetry install
   ```

---

## Initialization and Run Modes

### Output of both modes:
- Generate EDI file(s)
- Generates a Markdown summary: `Statistics_Visualizer.md`

### Initialization Logic

On first execution, the generator will:

- **Check if the database exists and is populated**.
- If **no beneficiaries** are found, it will generate the number set in `config.initial_beneficiaries`.
- If **no claim transactions** are found, it will create an **8-day backlog of transactions** following the standard file flow:

  1. `Created (Day 1)` → 270
  2. `270 Created (Day 2)` → 837
  3. `837 Created (Day 2)` → 277CA
  4. `277CA Created (Day 8)` → 835
  5. `835 Created (Day 8)` → 834

---

### Auto Mode

- Checks for missing sponsors or claims and runs **initialization** if needed.
- On subsequent daily runs:
  - Creates a new `270` transaction for today (if not already made).
  - Sequentially generates all EDI files (270, 837, 277CA, 835, 834) using appropriate transactions and updates their statuses.

This mode is ideal for **daily scheduled runs** or testing the full pipeline behavior.

```bash
cd src
python RunGenerator.py auto # for a random number of messages and error rate which you can alter in config.toml

# Example Usage
python RunGenerator.py auto
```

---

### Manual Mode

- Only creates transactions for the **specified file type**.
- Then generates the corresponding EDI file.

⚠️ If you run only one file type manually (e.g., 837), this may unintentionally generate transactions required for downstream files (e.g., 277CA, 835), which may **cause inconsistencies** in later stages.

Use this mode for **targeted testing or debugging**, not for full-pipeline simulation.

```bash
python RunGenerator.py cli <file_type> -n <count> -e <error_rate> [--upload_s3] # upload_s3 only for 270

# Example Usage
python RunGenerator.py cli 270 -n 500 -e 0.01 --upload_s3
python RunGenerator.py cli 835 -n 500 -e 0.05 
```

---
## Configuration

Edit `Config/config.toml` to adjust:

| Section         | Field                   | Description                      |
|-----------------|-------------------------|----------------------------------|
| `[seed]`        | `random_seed`           | Alter the seed                   |
| `[aws]`         | `upload_to_s3`          | Enable/disable S3 upload         |
| `[database]`    | `backend`               | Choose `sqlite` or `jsonl`       |
| `[constants]`   | `sender_id`, `payer_id` | Required identifiers             |
| `[paths]`       | `edi*_path`             | Output folders for EDI files     |
| `[test_size.*]` | `avg`, `min`, `max`     | Bell curve message distributions |

---

## Output Structure

| File Type | Directory                | Description                             |
|-----------|--------------------------|-----------------------------------------|
| 270       | `Output/EDI270_Output/`  | Eligibility Inquiry                     |
| 837P      | `Output/EDI837_Output/`  | Professional Claims                     |
| 277CA     | `Output/EDI277CA_Output/`| Claim Acknowledgment                    |
| 835       | `Output/EDI835_Output/`  | Remittance Advice                       |
| 834       | `Output/EDI834_Output/`  | Enrollment Updates                      |
| 999       | `Output/EDI999_Output/`  | Syntax Acknowledgment (coming)          |
| Logs      | `Output/Logs/`           | Execution logging                       |
| Markdown  | `Statistics_Visualizer.md`| Throughput, errors, relationships, etc. |

---

### Error Injection

Set via `config.toml`:
```toml
[constants]
total_error_rate = 0.005 # 0.5%
```
Types include:
- Missing values
- Malformed formats
- Invalid values
- Negative numbers (for amounts)

### Database Support

- SQLite -- [SQLite Browser](https://sqlitebrowser.org/)
- JSONL

---

## Example Output

```bash
INFO:Config.Config:Fetching claim transactions with status=835 Created and date=2025-07-03
INFO:Config.Config:Generating EDI file from stored data
INFO:Config.Config:Generated total of 500 transactions
INFO:Config.Config:There were 0 errors
INFO:Config.Config:EDI file generation complete
INFO:Config.Config:File generation took: 0:00:00.135001
INFO:Config.Config:It took 0:00:00.140000 to generate 500 transactions for the 834 file
INFO:Config.Config:It took 0:00:23.599000 to generate the output
```

