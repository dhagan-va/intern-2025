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
    "270" : 100
    "837" : 100
    "277" : 100
    "835" : 100
    "834" : 100
```


Total Number of Messages Generated: **500**
## Throughput
```mermaid
xychart-beta
    title "Throughput (Transactions per Second)"
    x-axis ["270", "837", "277", "835", "834"]
    y-axis "TPS" 0 --> 3449.394772233525
    bar [3125.097659301853, 2702.702702702703, 2777.6234653630354, 3170.074496750674, 3448.394772233525]
```


## Error Count
```mermaid
xychart-beta
    title "Error Count in Messages"
    x-axis ["270", "837", "277", "835", "834"]
    y-axis "Errors" 0 --> 1
    bar [0, 0, 0, 0, 0]
```


## Error Rate
```mermaid
xychart-beta
    title "Error Rate (%)"
    x-axis ["270", "837", "277", "835", "834"]
    y-axis "Percent" 0 --> 5
    bar [0, 0, 0, 0, 0]
```


## Family Size Distribution
```mermaid
xychart-beta
    title "Family Size Histogram"
    x-axis ["1", "2", "3", "4"]
    y-axis "Count" 0 --> 10046
    bar [10006, 9979, 9952, 10045]
```


```mermaid
pie title Family Size Breakdown
    "1" : 10006
    "2" : 9979
    "3" : 9952
    "4" : 10045
```


## Beneficiary Types
```mermaid
xychart-beta
    title "Beneficiary Code Distribution"
    x-axis ["Spouse (01)", "Child (19)", "Caregiver (26)", "Ex-Spouse (25)"]
    y-axis "Count" 0 --> 25099
    bar [25029, 24999, 25098, 24874]
```


```mermaid
pie title Beneficiary Relationship Types
    "Spouse (01)" : 25029
    "Child (19)" : 24999
    "Caregiver (26)" : 25098
    "Ex-Spouse (25)" : 24874
```


## AMT (deductible) Averages
```mermaid
xychart-beta
    title "AMT (deductible) Averages"
    x-axis ["D2", "FK", "R"]
    y-axis "Amount" 0 --> 53693.71227722773
    bar [52644.403465346564, 52693.71227722773, 47286.70643564357]
```


## AMT (visit) Averages
```mermaid
xychart-beta
    title "AMT (visit) Averages"
    x-axis ["C1", "P3", "B9"]
    y-axis "Number of Visits" 0 --> 9.118811881188119
    bar [8.118811881188119, 6.673267326732673, 7.564356435643564]
```


## Average 270s per Beneficiary
- Average 270s per Beneficiary: **0.00**
