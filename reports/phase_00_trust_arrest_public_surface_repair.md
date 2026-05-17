# Phase 00 Completion Report: Trust Arrest and Public Surface Repair

## Status
- Completed: explicit `canonical`, `solar_civil`, `static_lookup`, and `compare` modes for enterprise BS month metadata.
- Completed: static lookup can appear only as explicit compatibility output or inside compare branches.
- Completed: public claim linting now checks OpenAPI operation wording for boundary-sensitive claims.
- Blocked: none for Phase 00 acceptance criteria.

## Climax Artifact
- What was produced: `/v3/api/enterprise/bs-months/2087` now demonstrates the trust arrest in default, static, and compare modes.
- How to inspect it:
  - `GET /v3/api/enterprise/bs-months/2087`
  - `GET /v3/api/enterprise/bs-months/2087?mode=static_lookup`
  - `GET /v3/api/enterprise/bs-months/2087?mode=compare`
- Why it is complete on its own: a reviewer can see canonical output refuse static-table truth, see static lookup marked unverified/review-required, and compare separate branches without merged authority.

## Changed Files
- `backend/app/api/enterprise_routes.py`
- `backend/app/services/bs_month_metadata_service.py`
- `backend/app/services/enterprise_calendar_service.py`
- `backend/app/api/engine_routes.py`
- `scripts/release/check_public_claims.py`
- `scripts/release/generate_phase_00_trust_arrest_report.py`
- `tests/unit/services/test_bs_month_metadata_service.py`
- `tests/integration/test_enterprise_routes.py`
- `tests/integration/test_enterprise_bs_months.py`
- `tests/contract/test_public_claims_contract.py`
- `docs/API_QUICKSTART.md`
- `docs/API_REFERENCE_V3.md`
- `docs/KNOWN_LIMITATIONS.md`
- `docs/CANONICAL_RUNTIME.md`
- `docs/VENDOR_DATE_RISK_AUDIT.md`
- `docs/api-docs/openapi*.json`

## New Invariants
- Default enterprise BS month metadata uses `calculation_mode=canonical` and selects `solar_civil`.
- Static lookup output uses `confidence=static_lookup_unverified`, `source_status=static_reference`, `authority=static_reference`, and `review_required=true`.
- Static lookup cannot serialize as `source_backed` or official enterprise truth.
- Compare mode returns explicit `canonical`, `solar_civil`, and `static_lookup` branches.
- Top-level `confidence` and nested `meta.confidence` match for BS month metadata modes.
- OpenAPI operation summaries/descriptions cannot use unsupported boundary-sensitive authority wording.

## Tests Added
- `tests/integration/test_enterprise_bs_months.py`
- `tests/contract/test_public_claims_contract.py`

## Commands Run
```bash
py -3.11 -m pytest tests/unit/services/test_bs_month_metadata_service.py tests/integration/test_enterprise_routes.py tests/integration/test_enterprise_bs_months.py tests/contract/test_public_claims_contract.py -q
py -3.11 scripts/release/check_public_claims.py
py -3.11 scripts/check_docs_links.py
py -3.11 scripts/release/check_route_inventory.py
py -3.11 scripts/release/check_documented_routes.py
py -3.11 scripts/check_future_bs_public_leakage.py
PYTHONPATH=backend:. py -3.11 scripts/release/check_public_openapi_drift.py
```

## Evidence
```json
{
  "canonical_default": {
    "authority": "computed_reference_not_authority",
    "calculation_mode": "canonical",
    "confidence": "canonical_solar_civil_computed",
    "meta_confidence": "canonical_solar_civil_computed",
    "meta_source": "parva_astronomical_engine",
    "review_required": true,
    "selected_mode": "solar_civil",
    "source_status": "computed_solar_civil",
    "total_days": 365
  },
  "compare": {
    "branch_totals": {
      "canonical": 365,
      "solar_civil": 365,
      "static_lookup": 367
    },
    "calculation_mode": "compare",
    "default_branch": "canonical",
    "disagreement": true,
    "review_required": true,
    "selected_mode": "canonical",
    "static_branch_confidence": "static_lookup_unverified"
  },
  "solar_civil_explicit": {
    "authority": "computed_reference_not_authority",
    "calculation_mode": "solar_civil",
    "confidence": "solar_civil_computed",
    "meta_confidence": "solar_civil_computed",
    "meta_source": "parva_astronomical_engine",
    "review_required": true,
    "selected_mode": null,
    "source_status": "computed_solar_civil",
    "total_days": 365
  },
  "static_lookup_explicit": {
    "authority": "static_reference",
    "calculation_mode": "static_lookup",
    "confidence": "static_lookup_unverified",
    "meta_confidence": "static_lookup_unverified",
    "meta_source": "parva_static_lookup_table",
    "review_required": true,
    "selected_mode": null,
    "source_status": "static_reference",
    "total_days": 367
  }
}
```

## Limitations
- Canonical mode is a Phase 00 policy-like selector, not the full future Policy VM.
- Project Parva remains decision-support infrastructure, not government, legal, tax, payroll, banking, religious, or panchanga authority.
- Static lookup remains available only for explicit compatibility/reference review.

## Next Phase Readiness
- Phase 01 can rely on BS month metadata no longer upgrading low-authority static lookup into high-authority-looking public output.
