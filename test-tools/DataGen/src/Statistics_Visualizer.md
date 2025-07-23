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

## Data Generation Speed
```mermaid
xychart-beta
    title "Records Generated per Second"
    x-axis ["Claims", "Sponsors/Beneficiaries"]
    y-axis "Records/Second" 0 --> 486.77455005497364
    bar [476.77455005497364, 0.0]
```


## Transaction Counts
```mermaid
pie title Message type distribution
    "270" : 1088
    "837" : 0
    "277" : 0
    "835" : 0
    "834" : 8220
```


Total Number of Messages Generated: **9308**
## Throughput
```mermaid
xychart-beta
    title "Throughput (Transactions per Second)"
    x-axis ["270", "837", "277", "835", "834"]
    y-axis "TPS" 0 --> 2951.931607672566
    bar [1326.829268292683, 0.0, 0.0, 0.0, 2950.931607672566]
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
    y-axis "Count" 0 --> 1
    bar [0, 0, 0, 0]
```


```mermaid
pie title Family Size Breakdown
    "1" : 0
    "2" : 0
    "3" : 0
    "4" : 0
```


## Beneficiary Types
```mermaid
xychart-beta
    title "Beneficiary Code Distribution"
    x-axis ["Spouse (01)", "Child (19)", "Caregiver (26)", "Ex-Spouse (25)"]
    y-axis "Count" 0 --> 1
    bar [0, 0, 0, 0]
```


```mermaid
pie title Beneficiary Relationship Types
    "Spouse (01)" : 0
    "Child (19)" : 0
    "Caregiver (26)" : 0
    "Ex-Spouse (25)" : 0
```


## AMT (deductible) Averages
```mermaid
xychart-beta
    title "AMT (deductible) Averages"
    x-axis ["D2", "FK", "R"]
    y-axis "Amount" 0 --> 50968.84229899041
    bar [49968.84229899041, 49504.61438997693, 49842.71626322808]
```


## AMT (visit) Averages
```mermaid
xychart-beta
    title "AMT (visit) Averages"
    x-axis ["C1", "P3", "B9"]
    y-axis "Number of Visits" 0 --> 8.517820216518672
    bar [7.517820216518672, 7.4655151441430485, 7.428779953776913]
```


## Average 270s per Beneficiary
- Average 270s per Beneficiary: **0.01**
