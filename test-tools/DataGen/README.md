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

## Sample

ISA&ast;**00**&ast;          &ast;**00**&ast;          &ast;**ZZ**&ast;**83-1002022     **&ast;**ZZ**&ast;**841439824      **&ast;210427&ast;2039&ast;**$**&ast;00501&ast;000000061&ast;**0**&ast;**T**&ast;**:**~
GS&ast;**BE**&ast;**83-1002022**&ast;**841439824**&ast;20210427&ast;20392689&ast;61&ast;**X**&ast;**005010X220A1**~
ST&ast;834&ast;0001~
BGN&ast;00&ast;0D0AACD687DA4FDEA7B90769916E6B06&ast;20210427&ast;203926&ast;MT&ast;&ast;&ast;2~
N1&ast;P5&ast;OCC&ast;FI&ast;123456678~
N1&ast;IN&ast;XX&ast;FI&ast;123356678~
INS&ast;Y&ast;18&ast;001&ast;&ast;A&ast;&ast;&ast;AC~
REF&ast;0F&ast;0032938645V20940530~
REF&ast;6O&ast;0048933446V10367343~
NM1&ast;IL&ast;1&ast;BLACK&ast;DEBORAH&ast;AMANDA&ast;&ast;&ast;34&ast;900823589~
PER&ast;IP&ast;&ast;TE&ast;6735697183~
N3&ast;4898 PINE BLVD&ast;APARTMENT 6381~
N4&ast;ARLINGTON&ast;GA&ast;12956~
AMT&ast;D2&ast;4~
AMT&ast;FK&ast;0~
AMT&ast;R&ast;7~
AMT&ast;C1&ast;6~
AMT&ast;P3&ast;3~
AMT&ast;B9&ast;5~
HD&ast;001&ast;&ast;MM&ast;MCVA1003~
DTP&ast;348&ast;D8&ast;20040726~
SE&ast;20&ast;0001~
ST&ast;834&ast;0002~
BGN&ast;00&ast;0D0AACD687DA4FDEA7B90769916E6B06&ast;20210427&ast;203926&ast;MT&ast;&ast;&ast;2~
N1&ast;P5&ast;OCC&ast;FI&ast;123456678~
N1&ast;IN&ast;XX&ast;FI&ast;123356678~
INS&ast;Y&ast;18&ast;001&ast;&ast;A&ast;&ast;&ast;AC~
REF&ast;0F&ast;0032938645V20940530~
REF&ast;6O&ast;0048933446V10367343~
NM1&ast;IL&ast;1&ast;BLACK&ast;DEBORAH&ast;AMANDA&ast;&ast;&ast;34&ast;900823589~
PER&ast;IP&ast;&ast;TE&ast;6735697183~
N3&ast;4898 PINE BLVD&ast;APARTMENT 6381~
N4&ast;ARLINGTON&ast;GA&ast;12956~
AMT&ast;D2&ast;4~
AMT&ast;FK&ast;0~
AMT&ast;R&ast;7~
AMT&ast;C1&ast;6~
AMT&ast;P3&ast;3~
AMT&ast;B9&ast;5~
HD&ast;001&ast;&ast;MM&ast;MCVA1003~
DTP&ast;348&ast;D8&ast;20040726~
SE&ast;20&ast;0002~
GE&ast;2&ast;61~
IEA&ast;1&ast;000000061~

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

