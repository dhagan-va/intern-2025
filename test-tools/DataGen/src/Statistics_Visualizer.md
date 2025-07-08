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
    "834" : 0
    "270" : 100
    "837" : 100
```


Total Number of Messages Generated: **200**
## Throughput
```mermaid
xychart-beta
    title "Throughput (Transactions per Second)"
    x-axis ["834", "270", "837"]
    y-axis "TPS" 0 --> 3704.155088135091
    bar [0.0, 3703.155088135091, 3225.8064516129034]
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
    y-axis "Count" 0 --> 108
    bar [100, 107, 97, 99]
```


```mermaid
pie title Family Size Breakdown
    "1" : 100
    "2" : 107
    "3" : 97
    "4" : 99
```


## Beneficiary Types
```mermaid
xychart-beta
    title "Beneficiary Code Distribution"
    x-axis ["Spouse (01)", "Child (19)", "Caregiver (26)", "Ex-Spouse (25)"]
    y-axis "Count" 0 --> 265
    bar [245, 235, 264, 256]
```


```mermaid
pie title Beneficiary Relationship Types
    "Spouse (01)" : 245
    "Child (19)" : 235
    "Caregiver (26)" : 264
    "Ex-Spouse (25)" : 256
```


## AMT (deductible) Averages
```mermaid
xychart-beta
    title "AMT (deductible) Averages"
    x-axis ["D2", "FK", "R"]
    y-axis "Amount" 0 --> 51052.58346534653
    bar [48506.10663366336, 50052.58346534653, 46622.208415841575]
```


## AMT (visit) Averages
```mermaid
xychart-beta
    title "AMT (visit) Averages"
    x-axis ["C1", "P3", "B9"]
    y-axis "Number of Visits" 0 --> 8.504950495049505
    bar [7.5049504950495045, 6.792079207920792, 7.198019801980198]
```


## Average 270s per Beneficiary
- Average 270s per Beneficiary: **0.10**
