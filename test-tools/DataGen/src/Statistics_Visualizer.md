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
    "270" : 5
    "837" : 5
    "277" : 5
    "834" : 35
```


Total Number of Messages Generated: **50**
## Throughput
```mermaid
xychart-beta
    title "Throughput (Transactions per Second)"
    x-axis ["270", "837", "277", "834"]
    y-axis "TPS" 0 --> 2693.5148088314486
    bar [555.4938340184424, 499.90001999600076, 625.1562890722681, 2692.5148088314486]
```


## Error Count
```mermaid
xychart-beta
    title "Error Count in Messages"
    x-axis ["270", "837", "277", "834"]
    y-axis "Errors" 0 --> 2
    bar [1, 0, 0, 0]
```


## Error Rate
```mermaid
xychart-beta
    title "Error Rate (%)"
    x-axis ["270", "837", "277", "834"]
    y-axis "Percent" 0 --> 5
    bar [5.0, 0, 0, 0]
```


## Family Size Distribution
```mermaid
xychart-beta
    title "Family Size Histogram"
    x-axis ["1", "2", "3", "4"]
    y-axis "Count" 0 --> 2
    bar [0, 1, 1, 0]
```


```mermaid
pie title Family Size Breakdown
    "1" : 0
    "2" : 1
    "3" : 1
    "4" : 0
```


## Beneficiary Types
```mermaid
xychart-beta
    title "Beneficiary Code Distribution"
    x-axis ["Spouse (01)", "Child (19)", "Caregiver (26)", "Ex-Spouse (25)"]
    y-axis "Count" 0 --> 4
    bar [1, 1, 0, 3]
```


```mermaid
pie title Beneficiary Relationship Types
    "Spouse (01)" : 1
    "Child (19)" : 1
    "Caregiver (26)" : 0
    "Ex-Spouse (25)" : 3
```


## AMT (deductible) Averages
```mermaid
xychart-beta
    title "AMT (deductible) Averages"
    x-axis ["D2", "FK", "R"]
    y-axis "Amount" 0 --> 54975.928611111114
    bar [48691.38861111111, 45329.902500000004, 53975.928611111114]
```


## AMT (visit) Averages
```mermaid
xychart-beta
    title "AMT (visit) Averages"
    x-axis ["C1", "P3", "B9"]
    y-axis "Number of Visits" 0 --> 10.0
    bar [6.944444444444445, 9.0, 6.666666666666667]
```


## Average 270s per Beneficiary
- Average 270s per Beneficiary: **0.00**
