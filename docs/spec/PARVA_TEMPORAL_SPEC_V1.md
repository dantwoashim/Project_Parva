# Parva Temporal Specification v1.0

Status: Draft (Normative + Informative)
Last Updated: 2026-02-12

## 1. Scope (Normative)
This specification defines the minimum interoperable behavior for Nepali temporal computation in Parva-compatible implementations.

Required domains:
1. Bikram Sambat conversion metadata and confidence classification.
2. Udaya tithi determination (tithi at sunrise).
3. Adhik Maas-sensitive lunar observance calculation behavior.
4. Festival rule taxonomy and machine-readable rule model.
5. Conformance case pack and pass criteria.

## 2. Terminology (Normative)
1. `Official`: Result derived from verified lookup/official source records.
2. `Computed`: Result derived by algorithmic ephemeris/rule computation.
3. `Estimated`: Result outside official lookup range using projected model.
4. `Udaya Tithi`: Tithi prevailing at local sunrise.
5. `Trace`: Deterministic machine-readable record of computation path and intermediates.

## 3. Required API Semantics (Normative)
A conformant authority-track API must support versioned endpoints under `/v5/api/*` and return envelope:

```json
{
  "data": {},
  "meta": {
    "trace_id": "tr_xxx",
    "confidence": { "level": "official|computed|estimated|unknown", "score": 0.0 },
    "method": "ephemeris_udaya|lookup|hybrid|override|unknown",
    "provenance": {
      "snapshot_id": "snap_xxx",
      "dataset_hash": "sha256:...",
      "rules_hash": "sha256:...",
      "signature": "...",
      "verify_url": "..."
    },
    "uncertainty": { "interval_hours": 0.0, "boundary_risk": "low|medium|high|unknown" },
    "policy": { "profile": "np-mainstream", "jurisdiction": "NP", "advisory": true }
  }
}
```

## 4. BS Conversion Requirements (Normative)
1. Conversion functions must include confidence classification.
2. Out-of-range projections must explicitly expose estimated error metadata.
3. `month_name` must resolve to canonical BS month naming table.

## 5. Udaya Tithi Requirements (Normative)
1. Official tithi for daily observance is tithi at local sunrise.
2. Implementation must record sunrise timestamp used for decision.
3. Boundary-risk metadata must be present for uncertainty reporting.

## 6. Festival Rule Taxonomy (Normative)
Supported rule classes:
1. `solar`
2. `lunar`
3. `mixed`
4. `relative`
5. `transit`
6. `override`

Machine-readable schema references:
1. `docs/spec/schemas/festival_rules_v4.schema.json`
2. `docs/spec/schemas/calculation_trace.schema.json`
3. `docs/spec/schemas/conformance_case.schema.json`

## 7. Conformance Protocol (Normative)
1. Conformance case pack file: `tests/conformance/conformance_cases.v1.json`
2. Runner: `scripts/spec/run_conformance_tests.py`
3. Passing requirement: all required keys present and HTTP 200 for each case.
4. Report artifact: `reports/conformance_report.json`

## 8. Informative Notes
1. Swiss Ephemeris mode and ayanamsa choices may differ by deployment profile.
2. Differences vs printed panchang must be disclosed with discrepancy notes.
3. Regional profile variants are expected and should be explicit, not hidden.

## 9. Versioning and Compatibility
1. v3 remains LTS compatibility mode.
2. v4 is normalized envelope mode.
3. v5 is authority-track with richer meta semantics.

## 10. Security and Trust Notes
1. Snapshot hashes and rule hashes must be published in response provenance.
2. Trace verification endpoint should allow independent replay/integrity checks.
3. Transparency logs should be append-only and audit-replayable.
