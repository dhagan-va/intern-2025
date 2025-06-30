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
    "834" : 5
    "270" : 5
```


Total Number of Messages Generated: **10**
## Throughput
```mermaid
xychart-beta
    title "Throughput (Transactions per Second)"
    x-axis ["834", "270", "837"]
    y-axis "TPS" 0 --> 93.5925925925926
    bar [92.5925925925926, 21.929824561403507, 0.0]
```


## Error Count
```mermaid
xychart-beta
    title "Error Count in Messages"
    x-axis ["834", "270", "837"]
    y-axis "Errors" 0 --> 1
    bar [0, 0, 0]
```


## Error Rate
```mermaid
xychart-beta
    title "Error Rate (%)"
    x-axis ["834", "270", "837"]
    y-axis "Percent" 0 --> 5
    bar [0, 0, 0]
```


## Family Size Distribution
```mermaid
xychart-beta
    title "Family Size Histogram"
    x-axis ["1", "2", "3", "4"]
    y-axis "Count" 0 --> 2
    bar [0, 0, 1, 1]
```


```mermaid
pie title Family Size Breakdown
    "1" : 0
    "2" : 0
    "3" : 1
    "4" : 1
```


## Beneficiary Types
```mermaid
xychart-beta
    title "Beneficiary Code Distribution"
    x-axis ["Spouse (01)", "Child (19)", "Caregiver (26)", "Ex-Spouse (25)"]
    y-axis "Count" 0 --> 3
    bar [0, 2, 1, 2]
```


```mermaid
pie title Beneficiary Relationship Types
    "Spouse (01)" : 0
    "Child (19)" : 2
    "Caregiver (26)" : 1
    "Ex-Spouse (25)" : 2
```


## AMT (deductible) Averages
```mermaid
xychart-beta
    title "AMT (deductible) Averages"
    x-axis ["D2", "FK", "R"]
    y-axis "Amount" 0 --> 73412.6
    bar [72412.6, 65015.0, 31323.4]
```


## AMT (visit) Averages
```mermaid
xychart-beta
    title "AMT (visit) Averages"
    x-axis ["C1", "P3", "B9"]
    y-axis "Number of Visits" 0 --> 13.2
    bar [12.2, 7.6, 9.8]
```


## Average 270s per Beneficiary
- Average 270s per Beneficiary: **0.20**
