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
    "270" : 1796
    "837" : 1796
    "277" : 1796
    "835" : 1796
    "834" : 1796
```


Total Number of Messages Generated: **8980**
## Throughput
```mermaid
xychart-beta
    title "Throughput (Transactions per Second)"
    x-axis ["270", "837", "277", "835", "834"]
    y-axis "TPS" 0 --> 4021.2624810570874
    bar [4008.7496093924383, 3134.238237008443, 1637.0296843795832, 4020.2624810570874, 3634.7225286011785]
```


## Error Count
```mermaid
xychart-beta
    title "Error Count in Messages"
    x-axis ["270", "837", "277", "835", "834"]
    y-axis "Errors" 0 --> 10
    bar [9, 9, 9, 9, 9]
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
    y-axis "Amount" 0 --> 51181.24693934335
    bar [49331.44734557604, 50181.24693934335, 49128.62315525886]
```


## AMT (visit) Averages
```mermaid
xychart-beta
    title "AMT (visit) Averages"
    x-axis ["C1", "P3", "B9"]
    y-axis "Number of Visits" 0 --> 8.369504730105731
    bar [7.314412910406233, 7.365609348914858, 7.3695047301057315]
```


## Average 270s per Beneficiary
- Average 270s per Beneficiary: **0.02**
