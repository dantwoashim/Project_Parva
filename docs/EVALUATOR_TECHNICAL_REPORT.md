# Project Parva — Technical Audit & Evaluation Report

**Student:** Rohan Basnet  
**Program:** BSc CSIT  
**Date:** February 2026  
**Repository:** `/Users/rohanbasnet14/Documents/Nepal as a System/Project Parva`

---

## 0) Scope of This Report

This report audits the **entire codebase** and documentation for Project Parva.  
It covers:
- Architecture and module boundaries
- Algorithms and mathematics (ephemeris, tithi, panchanga, sankranti, lunar months)
- Data sources and ingestion pipeline (including OCR from MoHA PDFs)
- Accuracy evaluation and test coverage
- Gaps, inconsistencies, and risks
- Recommendations to finalize a defensible, accurate system

All statements below are grounded in the current code and files present in this repository.

---

## 1) Codebase Metrics (Current Snapshot)

- **Python files:** 12,375 LOC  
  (sum of all `*.py` excluding `node_modules`)
- **Frontend JS/JSX files:** 2,349 LOC  
  (sum of `*.js` + `*.jsx` excluding `node_modules`)
- **Total code files (py/js/jsx):** 81
- **Tests:**
  - `backend/tests/test_ephemeris.py` (514 lines)
  - `backend/tests/test_api_calendar.py` (273 lines)
  - `tests/unit/calendar/test_tithi.py` (234 lines)
  - Additional unit/integration tests under `/tests/`

---

## 2) System Architecture (As Implemented)

### 2.1 Backend
**Framework:** FastAPI (`backend/app/main.py`)  
**Service domains:**
- **Calendar Engine:** `backend/app/calendar/`
  - Ephemeris wrapper (`ephemeris/`)
  - Tithi engine (`tithi/`)
  - BS conversion (`bikram_sambat.py`)
  - Nepal Sambat approximation (`nepal_sambat.py`)
  - Panchanga (`panchanga.py`)
  - Sankranti (`sankranti.py`)
  - Lunar month + Adhik Maas (`lunar_calendar.py`, `adhik_maas.py`)
  - Festival calculators (`calculator.py`, `calculator_v2.py`)
  - Overrides + provenance (`overrides.py`, `merkle.py`)
- **Festivals API:** `backend/app/festivals/`
- **Locations API:** `backend/app/locations/`
- **Mythology API:** `backend/app/mythology/`
- **Provenance API:** `backend/app/provenance/`

### 2.2 Frontend
**Framework:** React + Vite (`frontend/`)
- Festival browsing and detail view
- Ritual timeline UI
- Temple map (Leaflet)
- Calendar info UI
- Data via REST endpoints in `frontend/src/services/api.js`

---

## 3) Core Algorithms & Mathematics

This section documents the actual computation logic used in code.

### 3.1 Ephemeris Engine (Astronomical Core)
**File:** `backend/app/calendar/ephemeris/swiss_eph.py`

Key points:
- Uses **pyswisseph** with **built-in Swiss/Moshier ephemeris** (no JPL files configured).
- Time handling is strict: `get_julian_day()` **requires timezone-aware datetime**; naive input raises error.
- Ayanamsa: Lahiri (sidereal correction).

**Implication:**  
**Code is honest about Moshier**, but some docs still claim JPL DE431. This is a documentation mismatch (see Findings).

### 3.2 Sun/Moon Positions
**Files:**
- `backend/app/calendar/ephemeris/positions.py`
- `backend/app/calendar/ephemeris/swiss_eph.py`

Mathematics:
- **Elongation** (tithi angle):  
  
  Δλ = (λ_moon − λ_sun) mod 360°

- **Tithi number:**  
  
  t = floor(Δλ / 12°) + 1, for t in 1..30

- **Nakshatra:**  
  
  n = floor(λ_moon / 13°20′) + 1, for n in 1..27

- **Yoga:**  
  
  y = floor(((λ_sun + λ_moon) mod 360°) / 13°20′) + 1

- **Karana:**  
  
  k = floor(Δλ / 6°) + 1

### 3.3 Tithi Engine (Ephemeris-Based)
**Files:**
- `backend/app/calendar/tithi/tithi_core.py`
- `backend/app/calendar/tithi/tithi_boundaries.py`
- `backend/app/calendar/tithi/tithi_udaya.py`

Features:
- **Accurate tithi at any instant** using ephemeris elongation
- **Boundary search** (binary search across ~30-hour window)
- **Udaya tithi**: tithi at sunrise (Kathmandu), which is the official religious convention
- Handles **Vriddhi** (repeated tithi) and **Ksheepana** (skipped tithi) using sunrise comparisons

### 3.4 Sunrise (Udaya) Calculation
**File:** `backend/app/calendar/ephemeris/swiss_eph.py`

Sunrise computed via Swiss Ephemeris `swe.rise_trans` using:
- Kathmandu coordinates (default)
- Returns UTC datetime
- No fallback; errors are surfaced to avoid incorrect religious dates

### 3.5 Panchanga (Five Elements)
**File:** `backend/app/calendar/panchanga.py`

Panchanga elements computed from ephemeris:
1. Tithi
2. Nakshatra
3. Yoga
4. Karana
5. Vaara (weekday)

### 3.6 Sankranti (Solar Transit)
**File:** `backend/app/calendar/sankranti.py`

Algorithm:
- Determine Sun’s rashi (zodiac sign) by longitude.
- If already inside target rashi, search backward for entry point.
- Binary search to 1-minute precision.

This supports:
- Solar festivals (BS New Year, Maghe Sankranti)
- Adhik Maas detection

### 3.7 Lunar Month Model (Adhik Maas Safe)
**Files:**
- `backend/app/calendar/lunar_calendar.py`
- `backend/app/calendar/adhik_maas.py`

Model:
- **Amavasya → Amavasya** month boundaries
- **Purnimant naming** (month named by Sun’s rashi at Purnima)
- **Adhik month detection:** a lunar month is Adhik if **no sankranti** occurs inside it

### 3.8 Festival Calculation Pipeline
There are **two calculators**:

1) **Legacy / V1**
   - **File:** `backend/app/calendar/calculator.py`
   - Uses BS month + tithi rules.
   - Does not handle Adhik Maas correctly for all festivals.
   - Loaded by `evaluate.py` and some older routes.

2) **Lunar V2 (Corrected Model)**
   - **File:** `backend/app/calendar/calculator_v2.py`
   - Uses `festival_rules_v3.json` with **lunar_month names** + **adhik_policy**.
   - Proper Adhik Maas handling.
   - Used by `backend/app/festivals/repository.py` for API festival dates.

**Official Overrides:**  
`backend/app/calendar/overrides.py` reads `ground_truth_overrides.json` (MoHA + other sources).

### 3.9 Bikram Sambat Conversion (BS ↔ Gregorian)
**Files:**
- `backend/app/calendar/bikram_sambat.py`
- `backend/app/calendar/constants.py`

Current implementation:
- **Lookup table** for BS month lengths (2070–2095 BS)
- **Reference epoch:** 2080-01-01 BS = 2023-04-14 AD
- Out-of-range years raise error

### 3.10 Nepal Sambat (NS)
**File:** `backend/app/calendar/nepal_sambat.py`

Current state:
- Approximate NS year based on Mha Puja (Kartik Amavasya)
- Does **not** compute full month/day inside NS (year only)
- Uses tithi finder to locate Mha Puja

---

## 4) Data Sources & Ingestion

### 4.1 Festival Content
**File:** `data/festivals/festivals.json`  
Contains:
- Festival metadata, descriptions, mythology, rituals, and regional variations
- Structured fields for 50 festivals

### 4.2 MoHA PDF OCR Pipeline
**File:** `backend/tools/ingest_moha_pdfs.py`  
**Inputs:**
- `data/२०८०_*.pdf`
- `data/२०८१_*.pdf`
- `data/२०८२_*.pdf`

Pipeline steps:
1. Convert PDF → PNG (`pdftoppm`)
2. OCR (Tesseract `nep+eng`)
3. Normalize OCR errors (digits, month spellings, common substitutions)
4. Extract holiday lines
5. Map Nepali festival names to canonical festival IDs
6. Convert BS → Gregorian
7. Merge into `ground_truth_overrides.json`

Outputs:
- `data/ingest_reports/holidays_2080/81/82_parsed.csv`
- `data/ingest_reports/holidays_2080/81/82_matched.csv`
- `backend/app/calendar/ground_truth_overrides.json`

### 4.3 Source Register
**Reference:** `docs/DATA_SOURCES.md`

Includes:
- MoHA
- Rashtriya Panchang
- Nepal Patro / Hamro Patro
- Drik Panchang
- Academic references (Toffin, Slusser, etc.)

---

## 5) Accuracy Evaluation & Tests

### 5.1 Automated Evaluation (Current State)
**File:** `backend/evaluation.csv`  
**Generated by:** `backend/tools/evaluate.py`

Summary (current file content):
- **Total cases:** 20
- **Pass:** 8
- **Fail:** 12

Important note:
- `evaluate.py` uses **`calculator.py` (V1)**, which does **not** include the corrected lunar month model.
- This explains why `evaluation.csv` under-reports accuracy.

### 5.2 Reported Accuracy (Documentation)
**Reference:** `docs/EVALUATION_REPORT.md`, `docs/DATE_ACCURACY_EVALUATION.md`

These documents claim:
- **100% accuracy** on 21/21 festivals (v2 evaluation)
- Verification against MoHA + Rashtriya Panchang

**Action required:**  
Align `evaluate.py` with `calculator_v2` to reconcile automated results with documented claims.

### 5.3 Test Coverage
**Core tests:**
- Ephemeris accuracy: `backend/tests/test_ephemeris.py`
- API correctness: `backend/tests/test_api_calendar.py`
- Tithi logic: `tests/unit/calendar/test_tithi.py`

**Note:** Tests are strong in ephemeris/tithi; festival accuracy evaluation needs to be unified with V2.

---

## 6) Frontend Data Integrity Check

### 6.1 Ritual Timeline Schema
**Files:**
- `frontend/src/components/Festival/FestivalDetail.jsx`
- `frontend/src/components/Festival/RitualTimeline.jsx`

Data mismatch:
- `festivals.json` uses `daily_rituals` as an **array** of day objects
- `RitualTimeline` expects `ritualSequence.days` (object shape)
- `normalizeRitualData` currently **does not handle array `daily_rituals`**

Impact: Ritual timeline may appear empty despite data existing.

---

## 7) Provenance & Blockchain Readiness

The project includes a **Merkle Tree** system for provenance:
- **File:** `backend/app/calendar/merkle.py`
- **API:** `backend/app/provenance/routes.py`

Capabilities:
- Generates Merkle root for festival snapshot data
- Provides proofs for individual festival dates
- Ready for anchoring to a blockchain ledger

This is a strong, **non-forceful blockchain integration**: the blockchain is optional, and the system remains fully usable without it.

---

## 8) Documentation vs Implementation Gaps (Critical Findings)

1. **Ephemeris Mode Mismatch**
   - README/ephemeris_spec claim **JPL DE431**
   - Code in `backend/app/calendar/ephemeris/swiss_eph.py` uses **Swiss/Moshier**
   - Recommendation: either configure DE431 files or update docs to reflect Moshier

2. **BS Conversion Range (Updated)**
   - Runtime now supports dual-mode conversion:
     - **Official lookup** for `2070–2095 BS`
     - **Estimated sankranti-based mode** outside lookup range
   - Recommendation: keep confidence labels explicit in all clients (`official|estimated`)

3. **Festival Calculators Are Split**
   - V1 in `calculator.py` (BS-month-based)
   - V2 in `calculator_v2.py` (lunar-month-based, Adhik aware)
   - Evaluation tool uses V1
   - Recommendation: consolidate on V2

4. **Legacy Tithi Module Still Present**
   - `backend/app/calendar/tithi.py` contains legacy synodic helpers
   - Active API/runtime now uses ephemeris package (`calendar/tithi/`) with udaya metadata
   - Recommendation: keep module clearly marked as compatibility-only, then remove in final cleanup

5. **Ritual Timeline UI Mismatch (Resolved)**
   - Frontend now normalizes `daily_rituals` / `simple_rituals` into `ritualSequence.days`
   - Recommendation: preserve adapter tests to prevent schema regressions

---

## 9) Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Mismatch between docs and ephemeris configuration | High (academic credibility) | High | Align code + docs |
| Adhik Maas handling in V1 paths | Medium | Medium | Migrate to V2 |
| BS lookup range limits | Medium | Medium | Use dual-mode + explicit confidence |
| Evaluation script uses old calculator | High | High | Update evaluation tool to V2 |
| Ritual timeline not rendering | Low | Medium | Fix data adapter |

---

## 10) Recommendations (Actionable)

1. **Unify Calculator**
   - Make `calculator_v2` the single source of truth
   - Deprecate or redirect V1 routes to V2

2. **Update Evaluation**
   - Modify `backend/tools/evaluate.py` to use V2
   - Regenerate `evaluation.csv` and align with `EVALUATION_REPORT.md`

3. **Ephemeris Clarity**
   - Either configure DE431 files **or** update all docs to “Moshier”

4. **BS Range**
   - Keep dual-mode policy explicit:
     - official lookup range: 2070–2095 BS
     - estimated mode outside range
   - Publish overlap behavior in `docs/BS_OVERLAP_REPORT.md`

5. **Frontend Ritual Schema**
   - Adapter is implemented; keep it covered by UI/integration tests

---

## 11) Conclusion

Project Parva is technically strong and academically defensible, with a correct ephemeris-driven lunar engine, Adhik Maas handling, and provenance via Merkle proofs. The **core astronomy and tithi math are sound**, and the architecture is cleanly modular.

The remaining issues are mostly **integration and alignment problems**, not algorithmic flaws:
- Evaluation tooling must use V2
- Docs must match actual ephemeris mode
- BS range claims must be clarified

Once these are aligned, the project is ready for final evaluation.

---

## 12) Reproducibility Commands (For Evaluator)

```bash
# API server
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Example: Panchanga for a date
curl "http://localhost:8000/api/calendar/panchanga?date=2026-02-15"

# Example: Convert date
curl "http://localhost:8000/api/calendar/convert?date=2026-02-15"

# Evaluate (current evaluator uses V1)
python backend/tools/evaluate.py

# V2 verification listing
python backend/tools/evaluate_v3.py
```
