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
    "270" : 500
    "837" : 500
    "277" : 1000
    "835" : 500
    "834" : 2000
```


Total Number of Messages Generated: **4500**
## Throughput
```mermaid
xychart-beta
    title "Throughput (Transactions per Second)"
    x-axis ["270", "837", "277", "835", "834"]
    y-axis "TPS" 0 --> 4133.094806783247
    bar [4098.360655737705, 3424.657534246576, 3246.753246753247, 4132.094806783247, 2541.3089774280934]
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
    x-axis ["270", "837", "277", "834"]
    y-axis "Percent" 0 --> 5
    bar [0, 0, 0, 0, 0]
```


## Family Size Distribution
```mermaid
xychart-beta
    title "Family Size Histogram"
    x-axis ["1", "2", "3", "4"]
    y-axis "Count" 0 --> 59
    bar [58, 53, 43, 52]
```


```mermaid
pie title Family Size Breakdown
    "1" : 58
    "2" : 53
    "3" : 43
    "4" : 52
```


## Beneficiary Types
```mermaid
xychart-beta
    title "Beneficiary Code Distribution"
    x-axis ["Spouse (01)", "Child (19)", "Caregiver (26)", "Ex-Spouse (25)"]
    y-axis "Count" 0 --> 144
    bar [128, 110, 143, 119]
```


```mermaid
pie title Beneficiary Relationship Types
    "Spouse (01)" : 128
    "Child (19)" : 110
    "Caregiver (26)" : 143
    "Ex-Spouse (25)" : 119
```


## AMT (deductible) Averages
```mermaid
xychart-beta
    title "AMT (deductible) Averages"
    x-axis ["D2", "FK", "R"]
    y-axis "Amount" 0 --> 51188.104092953516
    bar [50188.104092953516, 49817.734702648566, 49241.71635682155]
```


## AMT (visit) Averages
```mermaid
xychart-beta
    title "AMT (visit) Averages"
    x-axis ["C1", "P3", "B9"]
    y-axis "Number of Visits" 0 --> 8.437281359320341
    bar [7.395302348825587, 7.43728135932034, 7.399300349825087]
```


## Average 270s per Beneficiary
- Average 270s per Beneficiary: **0.00**
