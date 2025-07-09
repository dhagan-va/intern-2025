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
    "837" : 300
```


Total Number of Messages Generated: **400**
## Throughput
```mermaid
xychart-beta
    title "Throughput (Transactions per Second)"
    x-axis ["834", "270", "837"]
    y-axis "TPS" 0 --> 8571.938803496943
    bar [0.0, 3333.2222259258024, 8570.938803496943]
```


## Error Count
```mermaid
xychart-beta
    title "Error Count in Messages"
    x-axis ["834", "270", "837"]
    y-axis "Errors" 0 --> 6
    bar [0, 5, 0]
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
    y-axis "Count" 0 --> 15
    bar [14, 13, 8, 9]
```


```mermaid
pie title Family Size Breakdown
    "1" : 14
    "2" : 13
    "3" : 8
    "4" : 9
```


## Beneficiary Types
```mermaid
xychart-beta
    title "Beneficiary Code Distribution"
    x-axis ["Spouse (01)", "Child (19)", "Caregiver (26)", "Ex-Spouse (25)"]
    y-axis "Count" 0 --> 29
    bar [27, 19, 26, 28]
```


```mermaid
pie title Beneficiary Relationship Types
    "Spouse (01)" : 27
    "Child (19)" : 19
    "Caregiver (26)" : 26
    "Ex-Spouse (25)" : 28
```


## AMT (deductible) Averages
```mermaid
xychart-beta
    title "AMT (deductible) Averages"
    x-axis ["D2", "FK", "R"]
    y-axis "Amount" 0 --> 51291.69823920268
    bar [49849.246112956804, 50291.69823920268, 49418.41229235879]
```


## AMT (visit) Averages
```mermaid
xychart-beta
    title "AMT (visit) Averages"
    x-axis ["C1", "P3", "B9"]
    y-axis "Number of Visits" 0 --> 9.16611295681063
    bar [6.953488372093023, 8.16611295681063, 7.774086378737541]
```


## Average 270s per Beneficiary
- Average 270s per Beneficiary: **0.08**
