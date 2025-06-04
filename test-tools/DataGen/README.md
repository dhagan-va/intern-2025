# EDI X12 Healthcare Data Generator

## Overview

This tool generates EDI X12 healthcare data for various transaction types, including batch and real-time processing. Designed to work in AWS Lambda, it efficiently handles up to 100,000 transactions per type in 5 minutes, ensuring data connectivity between transactions and saving output files to Amazon S3.

---

## Features

- **Supported Transactions:**
  - **834:** Enrollment & Eligibility batch
  - **270:** Eligibility Check (real-time) (FUTURE)
  - **837:** Claim batch (FUTURE)
  - **277CA:** Status batch (FUTURE)
  - **835:** Payment batch (FUTURE)
  - **999:** Acknowledgement batch (FUTURE)
- **AWS Lambda Integration:** Optimized for serverless execution.
- **High Performance:** Processes 100,000 transactions per transaction type in under 5 minutes.
- **Data Connectivity:** Ensures data relationships between transactions.
- **S3 File Storage:** Saves generated files directly to Amazon S3. (FUTURE if possible)
- **Configurable:** Parameters for transaction volume, concurrency, and file storage.

---

## Architecture

```mermaid
flowchart TD
  A[834 - Enrollment<br/>Sent from Sponsor to Payer] --> B[Member Enrollment<br/>Database Updated]

  C[270 - Eligibility Inquiry<br/>Sent from Provider to Payer] --> D[271 - Eligibility Response<br/>Returned to Provider]

  E[837 - Claim Submission<br/>Sent from Provider to Payer] --> F[Claim Receipt]
  F --> G[277CA - Acknowledgment<br/>Sent back to Provider]

  G --> H[Claim Adjudication]
  H --> I[835 - Remittance Advice<br/>Sent to Provider]