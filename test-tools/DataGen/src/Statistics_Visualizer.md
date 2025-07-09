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
    "270" : 1000
    "837" : 1000
```


Total Number of Messages Generated: **2000**
## Throughput
```mermaid
xychart-beta
    title "Throughput (Transactions per Second)"
    x-axis ["834", "270", "837"]
    y-axis "TPS" 0 --> 4220.409282700422
    bar [0.0, 4219.409282700422, 3508.7719298245615]
```


## Error Count
```mermaid
xychart-beta
    title "Error Count in Messages"
    x-axis ["834", "270", "837"]
    y-axis "Errors" 0 --> 51
    bar [0, 50, 0]
```


## Error Rate
```mermaid
xychart-beta
    title "Error Rate (%)"
    x-axis ["834", "270", "837"]
    y-axis "Percent" 0 --> 5
    bar [0, 5.0, 0]
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
    y-axis "Amount" 0 --> 50814.933206793234
    bar [48873.89018981021, 48488.28641358642, 49814.933206793234]
```


## AMT (visit) Averages
```mermaid
xychart-beta
    title "AMT (visit) Averages"
    x-axis ["C1", "P3", "B9"]
    y-axis "Number of Visits" 0 --> 8.740259740259742
    bar [7.4935064935064934, 7.4935064935064934, 7.740259740259741]
```


## Average 270s per Beneficiary
- Average 270s per Beneficiary: **0.01**
