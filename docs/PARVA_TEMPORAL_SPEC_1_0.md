# Parva Temporal Spec 1.0

## 1. Scope
Parva Temporal Spec defines a verifiable API contract for:
- Nepali calendar conversion (BS, NS, Gregorian)
- Panchanga computation (tithi, nakshatra, yoga, karana, vaara)
- Festival date computation and explainability traces
- Provenance and trust metadata
- Confidence and uncertainty semantics

## 2. Non-Goals
- Replacing local religious authorities for binding observance decisions
- Guaranteeing exact agreement with every regional tradition

## 3. Versioning
- Stable target: `/v3/api/*`
- LTS policy documented in `/Users/rohanbasnet14/Documents/Project Parva/docs/LTS_POLICY.md`
- Response-shape breaking changes require new major version

## 4. Core Algorithms
### 4.1 Tithi
- Elongation: `delta = (lambda_moon - lambda_sun) mod 360`
- Tithi index: `tithi = floor(delta / 12) + 1`
- Udaya mode chooses tithi at local sunrise

### 4.2 Sankranti
- Solve for `sun_longitude(t) = target_rashi_degree`
- Use bracketing + root-finding around crossing windows

### 4.3 Lunar Month / Adhik Maas
- Month windows modeled from Amavasya to Amavasya
- Adhik month identified when no sankranti occurs inside lunar month window

### 4.4 Festival Resolution
- Rule classes: fixed solar, lunar tithi, relative
- Override layer can supersede computed date for official listings

## 5. Required Metadata
All key temporal responses SHOULD include:
- `confidence`
- `uncertainty`
- `provenance` (`dataset_hash`, `rules_hash`, `snapshot_id`)
- `policy`

## 6. Explainability
- Festival explanation endpoint returns `calculation_trace_id`
- Trace retrieval endpoint provides deterministic ordered steps:
  - rule loading
  - calendar/tithi resolution
  - final date selection

## 7. Trust Layer
- Snapshot hashes and Merkle proof endpoints are required
- Transparency log endpoints provide append-only audit events

## 8. Conformance
Implementations are conformant if they pass:
- Contract shape checks
- Conformance suite in `/Users/rohanbasnet14/Documents/Project Parva/scripts/spec/run_conformance_tests.py`
- Benchmark pack execution with no critical failures
