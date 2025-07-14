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
    "270" : 3522
    "837" : 3522
    "277" : 3522
    "835" : 3522
    "834" : 3522
```


Total Number of Messages Generated: **17610**
## Throughput
```mermaid
xychart-beta
    title "Throughput (Transactions per Second)"
    x-axis ["270", "837", "277", "835", "834"]
    y-axis "TPS" 0 --> 3962.429488917108
    bar [3891.4633095337535, 3294.4614322582215, 3473.1535682166013, 3961.429488917108, 3551.7960167848078]
```


## Error Count
```mermaid
xychart-beta
    title "Error Count in Messages"
    x-axis ["270", "837", "277", "835", "834"]
    y-axis "Errors" 0 --> 3513
    bar [18, 3512, 18, 18, 18]
```


## Error Rate
```mermaid
xychart-beta
    title "Error Rate (%)"
    x-axis ["270", "837", "277", "835", "834"]
    y-axis "Percent" 0 --> 5
    bar [0.5, 0.5, 0.5, 0.5, 0.5]
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
    y-axis "Amount" 0 --> 50959.90747942101
    bar [48956.36153846157, 49959.90747942101, 49374.882500709704]
```


## AMT (visit) Averages
```mermaid
xychart-beta
    title "AMT (visit) Averages"
    x-axis ["C1", "P3", "B9"]
    y-axis "Number of Visits" 0 --> 8.543570820323588
    bar [7.461254612546125, 7.543570820323588, 7.467215441385183]
```


## Average 270s per Beneficiary
- Average 270s per Beneficiary: **0.04**
