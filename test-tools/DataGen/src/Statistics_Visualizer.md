# Data Visualizer 

## What Are 834 and 270 EDI Files?

**EDI 834 - Benefit Enrollment and Maintenance**  
The 834 file is used to electronically transmit enrollment data between employers, insurance providers, and government agencies. It includes information about plan members (sponsors and beneficiaries), such as:
- Enrollment or termination status (in our case it's enrollment)
- Subscriber and dependent details
- Coverage effective dates

**EDI 270 - Eligibility Inquiry**  
The 270 file is used to request information about a member's health insurance eligibility and benefits. It is typically sent by healthcare providers to insurers to confirm:
- Active coverage
- Service eligibility
- Co-pays, deductibles, or benefit limits

## Transaction Counts
```mermaid
pie title Message type distribution
    "834" : 5000
    "270" : 500
```


Total Number of Messages Generated: **5500**
## Throughput
```mermaid
xychart-beta
    title "Throughput (Transactions per Second)"
    x-axis ["834", "270"]
    y-axis "TPS" 0 --> 2801.3423138444446
    bar [2800.3423138444446, 155.249899553315]
```


## Error Count
```mermaid
xychart-beta
    title "Error Count in Messages"
    x-axis ["834", "270"]
    y-axis "Errors" 0 --> 26
    bar [25, 25]
```


## Error Rate
```mermaid
xychart-beta
    title "Error Rate (%)"
    x-axis ["834", "270"]
    y-axis "Percent" 0 --> 5
    bar [0.5, 5.0]
```


## Family Size Distribution
```mermaid
xychart-beta
    title "Family Size Histogram"
    x-axis ["1", "2", "3", "4"]
    y-axis "Count" 0 --> 533
    bar [467, 494, 532, 488]
```


```mermaid
pie title Family Size Breakdown
    "1" : 467
    "2" : 494
    "3" : 532
    "4" : 488
```


## Beneficiary Types
```mermaid
xychart-beta
    title "Beneficiary Code Distribution"
    x-axis ["Spouse (01)", "Child (19)", "Caregiver (26)", "Ex-Spouse (25)"]
    y-axis "Count" 0 --> 1287
    bar [1286, 1241, 1244, 1229]
```


```mermaid
pie title Beneficiary Relationship Types
    "Spouse (01)" : 1286
    "Child (19)" : 1241
    "Caregiver (26)" : 1244
    "Ex-Spouse (25)" : 1229
```


## AMT (deductible) Averages
```mermaid
xychart-beta
    title "AMT (deductible) Averages"
    x-axis ["D2", "FK", "R"]
    y-axis "Amount" 0 --> 51263.7152
    bar [49598.979, 50263.7152, 49522.9534]
```


## AMT (visit) Averages
```mermaid
xychart-beta
    title "AMT (visit) Averages"
    x-axis ["C1", "P3", "B9"]
    y-axis "Number of Visits" 0 --> 8.5304
    bar [7.5304, 7.4892, 7.4246]
```


## Average 270s per Beneficiary
- Average 270s per Beneficiary: **0.10**
