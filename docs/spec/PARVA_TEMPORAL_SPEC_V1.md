# Parva Temporal Specification v1.0 (Normative Core)

Status: Draft-Normative Core  
Version: 1.0.0  
Last updated: 2026-02-13

## 1. Purpose and Scope (Normative)
This document defines the minimum normative behavior for interoperable Nepali temporal computation in Parva-compatible implementations.

This core specification is limited to:
1. Bikram Sambat (BS) boundary and conversion behavior.
2. Udaya tithi determination (tithi at local sunrise).
3. Adhik Maas classification behavior for lunar month windows.
4. Conformance obligations and pass criteria.

Out of scope for this core version:
1. Full regional observance jurisprudence.
2. Personalized muhurta/kundali advisory logic.
3. Non-Nepali calendar families beyond integration interfaces.

## 2. Conformance Language (Normative)
The key words "MUST", "MUST NOT", "REQUIRED", "SHOULD", "SHOULD NOT", and "MAY" are to be interpreted as described in RFC 2119.

## 3. Canonical Time and Coordinate Model (Normative)
1. Calendar-date APIs MUST accept Gregorian dates in `YYYY-MM-DD` format.
2. Internal ephemeris calculations MUST be performed in UTC.
3. Udaya tithi decisions MUST use local sunrise for the target geolocation.
4. When location is omitted, implementations MUST default to Kathmandu coordinates and Nepal time profile.
5. Returned sunrise timestamps SHOULD include both UTC and local representation when available.

## 4. BS Conversion Core Rules (Normative)
### 4.1 Conversion modes
Implementations MUST support explicit confidence classes:
1. `official` for lookup-table-backed conversion in verified ranges.
2. `estimated` for projected conversion outside official lookup ranges.
3. `computed` MAY be used for algorithmic conversion where no official row exists.

### 4.2 Metadata requirements
Any endpoint returning BS conversion data MUST expose:
1. `confidence` level.
2. `source_range` (official span used by lookup-table mode).
3. `estimated_error_days` when confidence is `estimated`.

### 4.3 Deterministic conversion behavior
For the same Gregorian date and same lookup data snapshot, output BS `year/month/day` MUST be deterministic.

## 5. Udaya Tithi Core Rules (Normative)
### 5.1 Definition
Udaya tithi is the tithi prevailing at local sunrise for the target location/date.

### 5.2 Computation rule
Implementations MUST derive tithi index from elongation:

`elongation = (lambda_moon - lambda_sun) mod 360`

`absolute_tithi = floor(elongation / 12) + 1`  (range 1..30)

### 5.3 Display mapping
1. `absolute_tithi` in 1..15 MUST map to `paksha = shukla` and `display_tithi = absolute_tithi`.
2. `absolute_tithi` in 16..30 MUST map to `paksha = krishna` and `display_tithi = absolute_tithi - 15`.

### 5.4 Required fields
Endpoints returning tithi for daily use MUST include:
1. `method` (e.g., `ephemeris_udaya`, `lookup`, `hybrid`).
2. `sunrise_utc` or equivalent sunrise reference.
3. `sunrise_local` when timezone conversion is available.
4. `paksha`, `display_tithi`, and `absolute_tithi` (or equivalent canonical names).

### 5.5 Boundary risk
If uncertainty around boundary cases is available, implementations SHOULD expose boundary risk classification (`low|medium|high|unknown`).

## 6. Adhik Maas Core Rules (Normative)
### 6.1 Lunar month window model
Adhik classification MUST be based on lunar month windows bounded by consecutive Amavasya instants.

### 6.2 Classification rule
A lunar month window MUST be classified as `adhik` if no solar sankranti crossing occurs within that window.

### 6.3 Required behavior
1. Adhik detection MUST be deterministic for a fixed ephemeris mode and ayanamsa configuration.
2. Implementations MUST document the ayanamsa/ephemeris mode used for classification.
3. If approximate mode is used, confidence SHOULD be lowered and disclosed.

## 7. Festival Rule Classes (Normative Interface)
Implementations MAY support additional classes, but MUST recognize at least:
1. `solar`
2. `lunar`
3. `relative`
4. `transit`
5. `override`

Machine-readable schema references:
1. `/Users/rohanbasnet14/Documents/Project Parva/docs/spec/schemas/festival_rules_v4.schema.json`
2. `/Users/rohanbasnet14/Documents/Project Parva/docs/spec/schemas/calculation_trace.schema.json`
3. `/Users/rohanbasnet14/Documents/Project Parva/docs/spec/schemas/conformance_case.schema.json`

## 8. Required Authority Metadata (Normative)
Authority-track responses SHOULD be delivered in envelope form:

```json
{
  "data": {},
  "meta": {
    "confidence": { "level": "official|computed|estimated|unknown", "score": 0.0 },
    "method": "ephemeris_udaya|lookup|hybrid|override|unknown",
    "provenance": {
      "snapshot_id": "snap_xxx",
      "dataset_hash": "sha256:...",
      "rules_hash": "sha256:...",
      "signature": "sha256sig:...",
      "verify_url": "..."
    },
    "uncertainty": { "interval_hours": 0.0, "boundary_risk": "low|medium|high|unknown" },
    "trace_id": "tr_xxx",
    "policy": { "profile": "np-mainstream", "jurisdiction": "NP", "advisory": true }
  }
}
```

Normative requirements:
1. `confidence.level` MUST be present.
2. `method` MUST be present.
3. `provenance.snapshot_id`, `dataset_hash`, and `rules_hash` SHOULD be present when snapshot system is active.
4. `trace_id` SHOULD be present for trace-enabled endpoints.

## 9. Conformance Suite (Normative)
### 9.1 Case pack
Conformance case pack path:
- `/Users/rohanbasnet14/Documents/Project Parva/tests/conformance/conformance_cases.v1.json`

### 9.2 Runner
Conformance runner path:
- `/Users/rohanbasnet14/Documents/Project Parva/scripts/spec/run_conformance_tests.py`

### 9.3 Pass criteria
An implementation is conformant to this core when:
1. All required case-pack endpoints return HTTP 200.
2. Required keys in each case are present.
3. Summary pass rate is 100% for mandatory cases.

### 9.4 Report artifact
Conformance report MUST be emitted to:
- `/Users/rohanbasnet14/Documents/Project Parva/reports/conformance_report.json`

## 10. Versioning and Compatibility (Normative)
1. `/v3/api/*` is LTS compatibility track.
2. `/v4/api/*` is normalized envelope track.
3. `/v5/api/*` is authority metadata track.
4. Breaking contract changes MUST use a new major version path.

## 11. Security and Integrity Notes (Normative)
1. Trace identifiers SHOULD be deterministic for identical trace payloads.
2. Snapshot verification endpoints SHOULD be available for independent validation.
3. Any integrity claim MUST be backed by reproducible artifact checks.

## 12. Known Implementation Profiles (Informative)
This repository currently ships a Swiss Ephemeris Moshier mode baseline and exposes confidence/provenance metadata through v5 envelope adaptation.

## 13. Reference Implementations and Artifacts (Informative)
1. Core API implementation: `/Users/rohanbasnet14/Documents/Project Parva/backend/app/main.py`
2. Tithi logic: `/Users/rohanbasnet14/Documents/Project Parva/backend/app/calendar/tithi/`
3. Adhik Maas logic: `/Users/rohanbasnet14/Documents/Project Parva/backend/app/calendar/adhik_maas.py`
4. Public authority dashboard: `/Users/rohanbasnet14/Documents/Project Parva/docs/public_beta/authority_dashboard.md`
