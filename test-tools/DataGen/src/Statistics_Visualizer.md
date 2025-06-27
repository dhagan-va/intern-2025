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
    "834" : 45428
    "270" : 8420
```


Total Number of Messages Generated: **53848**
## Throughput
```mermaid
xychart-beta
    title "Throughput (Transactions per Second)"
    x-axis ["834", "270"]
    y-axis "TPS" 0 --> 2852.3681363690603
    bar [2851.3681363690603, 173.40007080571536]
```


## Error Count
```mermaid
xychart-beta
    title "Error Count in Messages"
    x-axis ["834", "270"]
    y-axis "Errors" 0 --> 229
    bar [228, 43]
```


## Error Rate
```mermaid
xychart-beta
    title "Error Rate (%)"
    x-axis ["834", "270"]
    y-axis "Percent" 0 --> 5
    bar [0.5, 0.5]
```


## Family Size Distribution
```mermaid
xychart-beta
    title "Family Size Histogram"
    x-axis ["1", "2", "3", "4"]
    y-axis "Count" 0 --> 4575
    bar [4558, 4550, 4492, 4574]
```


```mermaid
pie title Family Size Breakdown
    "1" : 4558
    "2" : 4550
    "3" : 4492
    "4" : 4574
```


## Beneficiary Types
```mermaid
xychart-beta
    title "Beneficiary Code Distribution"
    x-axis ["Spouse (01)", "Child (19)", "Caregiver (26)", "Ex-Spouse (25)"]
    y-axis "Count" 0 --> 11480
    bar [11479, 11318, 11311, 11320]
```


```mermaid
pie title Beneficiary Relationship Types
    "Spouse (01)" : 11479
    "Child (19)" : 11318
    "Caregiver (26)" : 11311
    "Ex-Spouse (25)" : 11320
```


## AMT (deductible) Averages
```mermaid
xychart-beta
    title "AMT (deductible) Averages"
    x-axis ["D2", "FK", "R"]
    y-axis "Amount" 0 --> 51179.05252267324
    bar [50006.73569164392, 50023.154067975694, 50179.05252267324]
```


## AMT (visit) Averages
```mermaid
xychart-beta
    title "AMT (visit) Averages"
    x-axis ["C1", "P3", "B9"]
    y-axis "Number of Visits" 0 --> 8.558246015673152
    bar [7.558246015673153, 7.497248393061548, 7.512107070529189]
```


## Average 270s per Beneficiary
- Average 270s per Beneficiary: **0.19**
