# Project Parva v2.0 Implementation Plan
## 5-Day Ephemeris Upgrade Sprint

**Start Date:** February 6, 2026  
**End Date:** February 10, 2026  
**Scope:** Complete ephemeris-based astronomical calculation engine

---

## Overview

| Day | Theme | Key Outcome |
|-----|-------|-------------|
| 1 | Ephemeris + Tithi | Accurate Sun/Moon positions, tithi calculation |
| 2 | Sankranti + Calendar | Extended BS range, 50 festival rules |
| 3 | Verification + API | 45-case evaluation, production API |
| 4 | Blockchain + UI | On-chain provenance, frontend updates |
| 5 | Docs + Release | Architecture docs, demo, v2.0 release |

---

# DAY 1: Foundations + Ephemeris + Core Calculations
### February 6 (Thursday)

## Part 1: Setup & Ephemeris Integration (08:00-12:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 08:00-08:30 | Define requirements and scope | `requirements.md` |
| 08:30-09:30 | Install pyswisseph + DE431 | `ephemeris_spec.md` |
| 09:30-10:30 | Ephemeris loader + time conversions | `swiss_eph.py`, `time_utils.py` |
| 10:30-11:30 | Sun/Moon ecliptic longitudes | `positions.py` |
| 11:30-12:00 | Caching layer | `cache.py` |

### Acceptance Criteria
- [ ] pyswisseph installed and configured
- [ ] UTC↔NPT conversion working
- [ ] 10 known lunar positions match reference within 1 arcminute
- [ ] 100 date queries complete in < 1s

---

## Part 2: Tithi Engine (13:00-16:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 13:00-14:00 | Δλ(t) = λ_moon − λ_sun function | `tithi_core.py` |
| 14:00-15:00 | Root-finding for tithi boundaries | `tithi_boundaries.py` |
| 15:00-16:00 | Sunrise calculation for Kathmandu | `sunrise.py` |

### Acceptance Criteria
- [ ] Tithi = floor((moon_long - sun_long) / 12°) + 1
- [ ] Brent method finding boundaries to ±1 minute
- [ ] Sunrise matches reference within ±2 minutes

---

## Part 3: Panchanga Complete (16:00-20:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 16:00-17:00 | Udaya tithi (tithi at sunrise) | `tithi_udaya.py` |
| 17:00-18:00 | Nakshatra calculation | `nakshatra.py` |
| 18:00-19:00 | Yoga and Karana | `yoga.py`, `karana.py` |
| 19:00-20:00 | Full panchanga integration | `panchanga.py` |

### Acceptance Criteria
- [ ] Udaya tithi matches panchang ≥95%
- [ ] Nakshatra = floor(moon_long / 13.333°)
- [ ] Full 5-element panchanga working
- [ ] 50+ tests passing

### Day 1 Files Created
```
backend/app/calendar/ephemeris/
├── __init__.py
├── swiss_eph.py
├── positions.py
├── time_utils.py
└── cache.py

backend/app/calendar/tithi/
├── __init__.py
├── tithi_core.py
├── tithi_boundaries.py
├── tithi_udaya.py
└── sunrise.py

backend/app/calendar/panchanga/
├── __init__.py
├── panchanga.py
├── nakshatra.py
├── yoga.py
└── karana.py

docs/
├── requirements.md
└── ephemeris_spec.md
```

---

# DAY 2: Sankranti + BS Calendar + Festival Engine
### February 7 (Friday)

## Part 1: Solar Events (08:00-12:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 08:00-09:30 | Sankranti crossing detection | `sankranti.py` |
| 09:30-11:00 | Validate 12 sankrantis × 3 years | Tests + validation log |
| 11:00-12:00 | Document sankranti accuracy | `sankranti_eval.md` |

### Acceptance Criteria
- [ ] λ_sun = 30°·m detection working
- [ ] Makar Sankranti within ±2 hours
- [ ] All 12 sankrantis validated for 2082-2084 BS

---

## Part 2: BS Calendar Engine (13:00-16:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 13:00-14:00 | Official lookup table (2070-2095) | `bs_lookup.py` |
| 14:00-15:00 | Computed BS from sankranti | `bs_computed.py` |
| 15:00-16:00 | Hybrid converter + confidence flags | `calendar_convert.py` |

### Acceptance Criteria
- [ ] 100% match in lookup range
- [ ] Computed mode has stable month boundaries
- [ ] API returns `confidence: exact|computed`

---

## Part 3: Festival Rules Engine (16:00-20:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 16:00-17:00 | Rule schema definition | `festival_rules.schema.json` |
| 17:00-18:00 | Rule interpreter + dispatcher | `festival_rules.py` |
| 18:00-19:30 | Encode ALL 50 festivals | `festival_rules.json` |
| 19:30-20:00 | Adhik Maas detection | `adhik_maas.py` |

### Acceptance Criteria
- [ ] Schema validates all rule types: fixed, tithi, full_moon, relative
- [ ] 10 sample festivals match expected dates
- [ ] Multi-day spans (Dashain 10 days) working
- [ ] Adhik Maas detection for any year

### Day 2 Files Created
```
backend/app/calendar/
├── sankranti.py
├── bs_lookup.py
├── bs_computed.py
├── calendar_convert.py
└── adhik_maas.py

backend/app/festivals/
├── festival_rules.schema.json
├── festival_rules.py
└── festival_rules.json

data/
├── sources.json
└── festival_catalog.csv

docs/
└── sankranti_eval.md
```

---

# DAY 3: Verification + API + Performance
### February 8 (Saturday)

## Part 1: Evaluation Harness (08:00-12:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 08:00-09:30 | Build evaluator (calculated vs ground truth) | `evaluate.py` |
| 09:30-11:00 | Run 45-case test (15 festivals × 3 years) | `evaluation.csv` |
| 11:00-12:00 | Discrepancy analysis | `discrepancy_analysis.md` |

### Acceptance Criteria
- [ ] Automated comparison with ground truth
- [ ] ≥95% match rate in official range
- [ ] Each mismatch has documented reason

---

## Part 2: API Endpoints (13:00-16:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 13:00-14:00 | /api/calendar/panchanga endpoint | Full 5-element response |
| 14:00-15:00 | Update /api/calendar/convert | Extended range + confidence |
| 15:00-16:00 | Update /api/festivals | Calculated dates |

### Acceptance Criteria
- [ ] All endpoints return schema-valid responses
- [ ] OpenAPI docs auto-generated at /docs
- [ ] Extended date range working (2000-2200 BS)

---

## Part 3: Performance & Hardening (16:00-20:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 16:00-17:00 | API caching for tithi/festivals | Cache implementation |
| 17:00-18:00 | Load testing | `perf_summary.md` |
| 18:00-19:00 | Error handling + logging | No silent failures |
| 19:00-20:00 | Final evaluation report | `evaluation_report.md` |

### Acceptance Criteria
- [ ] P95 < 500ms
- [ ] Stable at 50 req/s
- [ ] `cache_policy.md` documented
- [ ] All error cases return proper HTTP codes

### Day 3 Files Created
```
backend/app/
├── evaluate.py
└── cache_config.py

data/
└── evaluation.csv

docs/
├── evaluation_report.md
├── discrepancy_analysis.md
├── cache_policy.md
└── perf_summary.md
```

---

# DAY 4: Blockchain + UI + Content
### February 9 (Sunday)

## Part 1: Blockchain Provenance (08:00-12:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 08:00-09:00 | Canonical JSON serialization | `snapshot.json` |
| 09:00-10:00 | SHA-256 hash generation | `snapshot_hash.txt` |
| 10:00-11:00 | Merkle tree + proof generator | `merkle.py` |
| 11:00-12:00 | Deploy contract to testnet | Contract address + tx hash |

### Acceptance Criteria
- [ ] Reproducible hash from canonical JSON
- [ ] Merkle proofs verify locally
- [ ] Contract stores root + version on-chain
- [ ] Transaction confirmed on Polygon testnet

---

## Part 2: Provenance API + UI (13:00-16:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 13:00-14:00 | /api/provenance/verify endpoint | Proof retrieval + validation |
| 14:00-15:00 | UI: "Verified on-chain" badge | Frontend component |
| 15:00-16:00 | UI: Confidence indicators | "Exact"/"Computed" labels |

### Acceptance Criteria
- [ ] Verify endpoint validates Merkle proofs
- [ ] Badge appears on verified data
- [ ] No broken layouts

---

## Part 3: Content + Frontend (16:00-20:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 16:00-17:30 | 15 major festival narratives | `festival_content.md` |
| 17:30-18:30 | Search + filter functionality | UI updates |
| 18:30-19:30 | Map integration updates | Location linkage |
| 19:30-20:00 | Frontend panchanga display | New API integration |

### Acceptance Criteria
- [ ] Each narrative has citation trail
- [ ] Search works across festivals
- [ ] Map shows festival locations
- [ ] Panchanga data displays correctly

### Day 4 Files Created
```
backend/app/provenance/
├── __init__.py
├── merkle.py
├── snapshot.py
└── verify.py

frontend/src/components/
├── ProvenanceBadge.jsx
├── ConfidenceIndicator.jsx
└── PanchangaDisplay.jsx

data/
├── snapshot.json
└── snapshot_hash.txt

docs/
└── festival_content.md
```

---

# DAY 5: Documentation + Demo + Release
### February 10 (Monday)

## Part 1: Technical Documentation (08:00-12:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 08:00-09:30 | Architecture + algorithm appendix | `architecture.md` |
| 09:30-10:30 | Security checklist | `security_checklist.md` |
| 10:30-12:00 | Developer README | `TECHNICAL_README.md` |

### Acceptance Criteria
- [ ] Can explain all algorithms without code
- [ ] Input validation documented
- [ ] Installation + testing guide complete

---

## Part 2: Demo Preparation (13:00-16:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 13:00-14:00 | Prepare demo data | Clean sample dataset |
| 14:00-15:00 | Write demo script | `demo_script.md` |
| 15:00-16:00 | Record 5-minute walkthrough | `demo.mp4` |

### Acceptance Criteria
- [ ] Demo flows smoothly
- [ ] Edge cases demonstrated
- [ ] Audio clear, visuals sharp

---

## Part 3: Release (16:00-20:00)

### Tasks
| Time | Task | Output |
|------|------|--------|
| 16:00-17:30 | Final QA sweep | All tests passing |
| 17:30-18:30 | Fix any remaining issues | Bug fixes |
| 18:30-19:30 | Write release notes | `release_notes.md` |
| 19:30-20:00 | Tag release | `git tag v2.0.0` |

### Acceptance Criteria
- [ ] All tests green
- [ ] All endpoints verified
- [ ] UI fully tested
- [ ] v2.0.0 tagged and ready

### Day 5 Files Created
```
docs/
├── architecture.md
├── security_checklist.md
├── TECHNICAL_README.md
├── demo_script.md
└── release_notes.md

media/
└── demo.mp4
```

---

# Complete Deliverable Checklist

## Core Engine
- [ ] Swiss Ephemeris integration
- [ ] Sun/Moon ecliptic longitudes
- [ ] Tithi calculation (Δλ/12°)
- [ ] Tithi boundary detection
- [ ] Sunrise for Kathmandu
- [ ] Udaya tithi (sunrise-based)
- [ ] Nakshatra, Yoga, Karana
- [ ] Full 5-element panchanga

## Calendar
- [ ] Sankranti detection (12 solar transits)
- [ ] BS lookup table (2070-2095)
- [ ] BS computed (any year)
- [ ] Hybrid converter with confidence
- [ ] Adhik Maas detection

## Festivals
- [ ] Rule schema
- [ ] Rule interpreter
- [ ] 50 festivals encoded
- [ ] Multi-day support

## Verification
- [ ] 45-case evaluation
- [ ] ≥95% accuracy achieved
- [ ] Discrepancies documented

## API
- [ ] /api/calendar/panchanga
- [ ] /api/calendar/convert (extended)
- [ ] /api/festivals (with dates)
- [ ] /api/provenance/verify
- [ ] P95 < 500ms

## Blockchain
- [ ] Canonical JSON snapshot
- [ ] Merkle tree
- [ ] Testnet contract deployment
- [ ] Proof verification

## UI
- [ ] Provenance badge
- [ ] Confidence indicators
- [ ] Panchanga display
- [ ] Search/filter
- [ ] Map integration

## Documentation
- [ ] requirements.md
- [ ] ephemeris_spec.md
- [ ] sankranti_eval.md
- [ ] evaluation_report.md
- [ ] discrepancy_analysis.md
- [ ] architecture.md
- [ ] TECHNICAL_README.md
- [ ] demo_script.md
- [ ] release_notes.md

## Release
- [ ] All tests passing
- [ ] Demo video recorded
- [ ] v2.0.0 tagged

---

**Ready to execute. Day 1 starts now.**
