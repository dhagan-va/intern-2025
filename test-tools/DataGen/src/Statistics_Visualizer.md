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
    "270" : 1000
    "837" : 1000
    "277" : 1000
    "834" : 2000
```


Total Number of Messages Generated: **5000**
## Throughput
```mermaid
xychart-beta
    title "Throughput (Transactions per Second)"
    x-axis ["270", "837", "277", "834"]
    y-axis "TPS" 0 --> 4256.337256754284
    bar [3861.0187684122334, 4255.337256754284, 3533.5938769885297]
```


## Error Count
```mermaid
xychart-beta
    title "Error Count in Messages"
    x-axis ["270", "837", "277", "834"]
    y-axis "Errors" 0 --> 51
    bar [50, 0, 0, 0]
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
    y-axis "Amount" 0 --> 50514.15440779614
    bar [49141.71714142923, 49105.410079960035, 49514.15440779614]
```


## AMT (visit) Averages
```mermaid
xychart-beta
    title "AMT (visit) Averages"
    x-axis ["C1", "P3", "B9"]
    y-axis "Number of Visits" 0 --> 8.696651674162919
    bar [7.4047976011994, 7.598700649675163, 7.6966516741629185]
```


## Average 270s per Beneficiary
- Average 270s per Beneficiary: **0.01**
