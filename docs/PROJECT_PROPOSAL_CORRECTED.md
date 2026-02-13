# Project Parva: A Ritual Time Engine for Nepali Festival Date Calculation

---

**BSc CSIT Final Year Project Proposal**

---

**Submitted By**: Rohan Basnet  
**Roll Number**: [Your Roll Number]  
**Program**: Bachelor of Science in Computer Science and Information Technology  
**Supervisor**: [Supervisor Name]  
**Department**: Department of Computer Science and Information Technology  
**College**: [College Name]  
**Date**: February 2026

---

## DECLARATION

I hereby declare that the work presented in this project proposal entitled **"Project Parva: A Ritual Time Engine for Nepali Festival Date Calculation"** is an original work done by me under the supervision of my supervisor and has not been submitted elsewhere for the award of any degree.

**Signature**: _________________________  
**Date**: _________________________

---

## ACKNOWLEDGEMENT

I would like to express my sincere gratitude to my supervisor for their invaluable guidance and support throughout this project. I am also thankful to the Department of Computer Science and Information Technology for providing the necessary resources.

Special thanks to the Nepal Rashtriya Panchanga and Nepal Government calendar publications for providing authoritative reference data.

---

## ABSTRACT

**Project Parva** is a web-based festival discovery platform that calculates dates for major Nepali festivals using astronomical algorithms. The system supports three calendar systems—Bikram Sambat, Nepal Sambat, and the Hindu Tithi system—providing date conversions and festival lookup functionality.

The core **Ritual Time Engine** computes festival dates by applying lunisolar calendar rules, including tithi (lunar day) calculations using the Swiss Ephemeris astronomical library. The platform combines this calculation engine with cultural content (mythology, rituals) and an interactive temple map.

**Keywords**: Festival Calendar, Nepali Culture, Lunisolar Calculation, Bikram Sambat, REST API

---

## TABLE OF CONTENTS

1. [Introduction](#1-introduction)
2. [Literature Review](#2-literature-review)
3. [Requirements Analysis](#3-requirements-analysis)
4. [Feasibility Study](#4-feasibility-study)
5. [System Design](#5-system-design)
6. [Methodology](#6-methodology)
7. [Algorithm Descriptions](#7-algorithm-descriptions)
8. [System Flowcharts](#8-system-flowcharts)
9. [Implementation Plan](#9-implementation-plan)
10. [Expected Outcomes](#10-expected-outcomes)
11. [Gantt Chart](#11-gantt-chart)
12. [References](#12-references)

---

## 1. INTRODUCTION

### 1.1 Background

Nepal operates on multiple calendar systems simultaneously: the official Bikram Sambat (BS), the indigenous Nepal Sambat (NS), and the international Gregorian calendar. Religious festivals are determined by complex lunisolar calculations involving lunar phases (tithi), solar months, and astronomical positions.

Unlike fixed holidays, festivals like Dashain and Tihar shift by 10-20 days each year relative to the Gregorian calendar. This variability stems from the lunisolar nature of the Bikram Sambat calendar, where months are tied to both solar and lunar cycles.

### 1.2 Problem Statement

The existing system for determining festival dates in Nepal suffers from several issues:

1. **Fragmented Sources**: Multiple applications and printed calendars provide inconsistent festival dates due to varying calculation methodologies.

2. **No Programmatic Access**: Developers lack a reliable API for accessing festival data programmatically.

3. **Loss of Traditional Knowledge**: The astronomical rules for calculating festival dates are understood by pundits but rarely documented in accessible digital form.

For the Nepali diaspora and tourism sector, this fragmentation causes missed festival celebrations and confusion when planning visits.

### 1.3 Proposed Solution

**Project Parva** addresses these problems through a **Ritual Time Engine**—a computational system that:

1. Calculates festival dates algorithmically using Bikram Sambat, Nepal Sambat, and tithi-based rules
2. Provides a REST API for integration into other applications
3. Displays cultural content including mythology and ritual sequences

The system is named "Parva" (पर्व), the Nepali word for festival.

### 1.4 Objectives

1. **Design and implement a calendar calculation engine** supporting Bikram Sambat ↔ Gregorian conversion with official lookup tables (2070-2095 BS) and estimated conversion beyond this range with labeled confidence.

2. **Develop a tithi calculator** using Swiss Ephemeris astronomical calculations for lunar phase determination.

3. **Create a festival rules engine** that determines dates for 20+ major Nepali festivals and provides this data via REST API.

### 1.5 Scope and Limitations

**In Scope**:
- Date calculation for 20+ major Hindu/Buddhist festivals
- Bikram Sambat conversion: official (2070-2095 BS), estimated beyond
- Tithi calculation with arcsecond-level accuracy
- Web-based user interface
- REST API with JSON responses

**Limitations**:
- BS conversion outside 2070-2095 BS uses estimated algorithms (not official data)
- Tithi calculation uses Swiss/Moshier ephemeris (not JPL DE431)
- Mobile native applications are out of scope
- User authentication is not included

---

## 2. LITERATURE REVIEW

### 2.1 Calendar Systems of Nepal

**Bikram Sambat (BS)**: The official calendar of Nepal since 1903 CE, dating from 57 BCE. It is a lunisolar calendar with variable month lengths (29-32 days). Month lengths are determined by astronomical calculations and differ each year (Sharma, 2015).

**Nepal Sambat (NS)**: An indigenous calendar beginning in 879 CE, used primarily by Newar communities. Nepal Sambat New Year falls on Kartik Shukla Pratipada.

**Tithi System**: Hindu festivals are determined by tithis—30 lunar days per month. A tithi is defined as the time required for the Moon to gain 12° of celestial longitude over the Sun (Meeus, 1991).

### 2.2 Existing Applications

| Application | Strengths | Limitations |
|-------------|-----------|-------------|
| Nepal Patro | Official-quality BS conversion | No API access |
| Hamro Patro | Popular, mobile-first | Proprietary, closed |
| Government Calendars | Authoritative | PDF-only, no integration |

**Gap**: No existing solution provides an open API with documented calculation methods.

### 2.3 Technical Approaches

The Swiss Ephemeris library (based on JPL planetary theories) provides accurate Sun/Moon position calculations. For tithi calculation, the formula is:

```
phase_angle = (lunar_longitude - solar_longitude) mod 360°
tithi = floor(phase_angle / 12°) + 1
```

---

## 3. REQUIREMENTS ANALYSIS

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR01 | Calculate Bikram Sambat dates from Gregorian input | High |
| FR02 | Calculate tithi (lunar day) for any given date | High |
| FR03 | Compute festival dates for multiple years | High |
| FR04 | Display mythology for major festivals | Medium |
| FR05 | Display temple locations on an interactive map | Medium |
| FR06 | Provide a REST API for external applications | High |

### 3.2 Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| **Accuracy** | BS conversion: 100% for official range (2070-2095 BS); labeled confidence for estimated dates |
| **Performance** | API response <500ms |
| **Usability** | Festival found in ≤3 clicks |

---

## 4. FEASIBILITY STUDY

### 4.1 Technical Feasibility

| Component | Technology | Justification |
|-----------|------------|---------------|
| Backend | Python/FastAPI | Type safety, async support |
| Frontend | React/Vite | Component architecture |
| Astronomy | pyswisseph | Swiss Ephemeris (built-in Moshier algorithm) |
| Maps | Leaflet + OpenStreetMap | Free, open-source |

**Note**: The system uses pyswisseph's built-in Swiss/Moshier ephemeris mode, which provides arcsecond-level accuracy. JPL DE431 ephemeris files could be configured for higher precision as a future upgrade.

**Conclusion**: Technically feasible.

### 4.2 Operational Feasibility

The system is web-based and requires only a modern browser. Target users include diaspora Nepalis, tourists, and developers.

**Conclusion**: Operationally feasible.

### 4.3 Economic Feasibility

| Item | Cost |
|------|------|
| Development Tools | $0 (open source) |
| Hosting (MVP) | $0 (free tier) |
| **Total** | **$0** |

**Conclusion**: Economically feasible.

---

## 5. SYSTEM DESIGN

### 5.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   React     │  │   Leaflet   │  │   Calendar  │             │
│  │   Frontend  │  │     Map     │  │   Widgets   │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER (FastAPI)                     │
│     /api/festivals    /api/calendar    /api/temples             │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ENGINE LAYER                               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │ Bikram Sambat │  │     Tithi     │  │   Festival    │       │
│  │   Converter   │  │   Calculator  │  │ Rules Engine  │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER (JSON)                         │
│     festivals.json    temples.json    bs_month_lengths.json     │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Use Case Diagram

```
                        ┌─────────────────────────────┐
                        │      Project Parva          │
    ┌─────────┐        │  ┌───────────────────────┐  │
    │  USER   │────────┼─>│ Search Festival       │  │
    │         │────────┼─>│ View Festival Detail  │  │
    │         │────────┼─>│ Convert Date (BS/AD)  │  │
    │         │────────┼─>│ View Temple Map       │  │
    └─────────┘        └─────────────────────────────┘
                        
    ┌─────────┐        ┌─────────────────────────────┐
    │DEVELOPER│────────┼─>│ GET /api/festivals    │  │
    │         │────────┼─>│ GET /api/calendar     │  │
    └─────────┘        └─────────────────────────────┘
```

---

## 6. METHODOLOGY

### 6.1 Development Model

The project follows a modified **Agile methodology** with four phases:

1. **BUILD Phase** (Week 1): Core calendar engines, API development
2. **CONTENT Phase** (Weeks 2-3): Cultural data creation, mythology research
3. **POLISH Phase** (Week 4): Testing, optimization
4. **DEMO Phase** (Week 5): Documentation, presentation

### 6.2 Justification

- **Short Timeline**: 4-5 weeks requires focused sprints
- **Solo Development**: No coordination overhead
- **Content-Heavy**: Requires substantial cultural content creation

---

## 7. ALGORITHM DESCRIPTIONS

### 7.1 Bikram Sambat Conversion Algorithm

The system uses a **hybrid approach**:

1. **Official Range (2070-2095 BS)**: Lookup table with verified month lengths from Nepal Government calendar data.

2. **Extended Range (outside 2070-2095)**: Estimated conversion using sankranti (solar ingress) detection. Results are labeled with `confidence: "estimated"`.

```
ALGORITHM: Gregorian to Bikram Sambat

INPUT: gregorian_date
OUTPUT: (bs_year, bs_month, bs_day, confidence)

1. IF date within 2070-2095 BS range:
   - Use lookup table
   - confidence = "official"
2. ELSE:
   - Detect Mesh Sankranti (BS New Year)
   - Calculate month boundaries using solar transits
   - confidence = "estimated"
   
3. RETURN (bs_year, bs_month, bs_day, confidence)
```

### 7.2 Tithi Calculation Algorithm

The system uses Swiss Ephemeris (Moshier algorithm) for planetary positions:

```
ALGORITHM: Calculate Tithi

INPUT: date
OUTPUT: (tithi_number, paksha, name)

1. Get Sun's sidereal longitude using pyswisseph
2. Get Moon's sidereal longitude using pyswisseph
3. Calculate elongation: (L_moon - L_sun) mod 360°
4. tithi = floor(elongation / 12°) + 1
5. paksha = "Shukla" if elongation < 180° else "Krishna"

RETURN (tithi, paksha, name)
```

**Note**: Uses Swiss/Moshier ephemeris (~1 arcsecond accuracy for planets, ~3 arcseconds for Moon). This is sufficient for tithi calculations where each tithi spans 12°.

### 7.3 Festival Rules Engine

Festivals are calculated using rules stored in JSON configuration:

```
ALGORITHM: Calculate Festival Date

INPUT: festival_id, year
OUTPUT: (start_date, end_date)

1. Check override database for official dates
   - IF found: RETURN override (method = "override")

2. Load festival rule from configuration
3. SWITCH rule.type:
   - "lunar_tithi": Find specified tithi in lunar month
   - "solar_fixed": Convert BS date directly
   - "solar_sankranti": Detect solar transit

4. RETURN (start_date, end_date, method)
```

---

## 8. SYSTEM FLOWCHARTS

### 8.1 Date Calculation Flow

```
    ┌─────────┐
    │  START  │
    └────┬────┘
         ▼
    ┌────────────────┐
    │ Input: Date    │
    └───────┬────────┘
            ▼
       ┌────────────┐
       │ Check if   │
       │ in official│
       │ BS range   │
       └─────┬──────┘
             │
      ┌──────┴──────┐
      ▼             ▼
   ┌─────┐       ┌─────────┐
   │ Yes │       │   No    │
   └──┬──┘       └────┬────┘
      ▼               ▼
┌──────────┐    ┌───────────┐
│ Use      │    │ Use       │
│ lookup   │    │ estimated │
│ table    │    │ algorithm │
└────┬─────┘    └─────┬─────┘
     │                │
     ▼                ▼
┌──────────┐    ┌───────────┐
│confidence│    │confidence │
│="official│    │="estimated│
└────┬─────┘    └─────┬─────┘
     └────────┬───────┘
              ▼
         ┌────────┐
         │ RETURN │
         │ result │
         └────────┘
```

---

## 9. IMPLEMENTATION PLAN

### 9.1 Technology Stack

| Layer | Technology |
|-------|------------|
| Backend Language | Python 3.11 |
| Web Framework | FastAPI |
| Astronomy Library | pyswisseph (Swiss/Moshier mode) |
| Frontend | React 18 + Vite |
| Maps | Leaflet.js |
| Data Storage | JSON files |

### 9.2 Module Structure

**Backend Modules**:
- `calendar/` — BS conversion, tithi calculation, panchanga
- `festivals/` — Festival API, rules engine
- `locations/` — Temple data API
- `mythology/` — Cultural content

**Frontend Components**:
- Festival list and detail views
- Interactive temple map
- Calendar conversion widget

### 9.3 API Endpoints (Planned)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/festivals` | List all festivals |
| GET | `/api/festivals/{id}` | Festival detail |
| GET | `/api/calendar/convert` | Date conversion |
| GET | `/api/temples` | List temples |

---

## 10. EXPECTED OUTCOMES

### 10.1 Deliverables

| Deliverable | Description |
|-------------|-------------|
| Ritual Time Engine | Calendar calculation backend with BS, tithi, and festival algorithms |
| Festival Database | 20+ festivals with calculation rules |
| REST API | Programmatic access to all data |
| Web Application | User interface for festival discovery |
| Temple Map | Interactive map with temple locations |

### 10.2 Success Criteria

1. BS conversion matches official government calendar for 2070-2095 BS range
2. Festival dates match official sources (when override data is available)
3. API responds to requests successfully
4. Web interface allows festival discovery in ≤3 clicks

---

## 11. GANTT CHART

| Week | Phase | Tasks |
|------|-------|-------|
| 1 | BUILD | Backend calendar engines, API setup |
| 2 | BUILD | Frontend components, integration |
| 3 | CONTENT | Festival data, mythology research |
| 4 | POLISH | Testing, bug fixes, optimization |
| 5 | DEMO | Documentation, presentation prep |

---

## 12. REFERENCES

[1] Sharma, N. D. (2015). *The Religious Festivals of the Hindus of Nepal*. Ratna Pustak Bhandar.

[2] Meeus, J. (1991). *Astronomical Algorithms*. Willmann-Bell.

[3] UNESCO. (2003). *Convention for the Safeguarding of the Intangible Cultural Heritage*. Paris.

[4] Nepal Government Ministry of Home Affairs. *Official Public Holiday List*. https://moha.gov.np/

[5] Swiss Ephemeris Development Team. *The Swiss Ephemeris*. Astrodienst AG. https://www.astro.com/swisseph/

[6] FastAPI Documentation. *FastAPI - Modern Python Web Framework*. https://fastapi.tiangolo.com/

---

*Prepared for BSc CSIT Final Year Project Proposal Defense*  
*February 2026*
