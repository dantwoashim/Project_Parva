#!/usr/bin/env python3
"""Generate the Phase 00 trust-arrest completion report from live app responses."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

PRIMARY_REPORT = PROJECT_ROOT / "reports" / "phase_00_trust_arrest.md"
DETAILED_REPORT = PROJECT_ROOT / "reports" / "phase_00_trust_arrest_public_surface_repair.md"


def _get(client: TestClient, path: str, *, params: dict[str, str] | None = None) -> dict[str, Any]:
    response = client.get(path, params=params)
    response.raise_for_status()
    return response.json()


def _summary(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("calculation_mode") == "compare":
        branches = payload["branches"]
        return {
            "calculation_mode": payload["calculation_mode"],
            "default_branch": payload["default_branch"],
            "selected_mode": payload["selected_mode"],
            "disagreement": payload["disagreement"],
            "review_required": payload["review_required"],
            "branch_totals": {
                key: value["total_days"] for key, value in sorted(branches.items())
            },
            "static_branch_confidence": branches["static_lookup"]["confidence"],
        }
    return {
        "calculation_mode": payload["calculation_mode"],
        "selected_mode": payload.get("selected_mode"),
        "total_days": payload["total_days"],
        "confidence": payload["confidence"],
        "source_status": payload["source_status"],
        "authority": payload["authority"],
        "review_required": payload["review_required"],
        "meta_confidence": payload["meta"]["confidence"],
        "meta_source": payload["meta"]["source"]["id"],
    }


def build_report() -> str:
    client = TestClient(app)
    canonical = _get(client, "/v3/api/enterprise/bs-months/2087")
    solar = _get(client, "/v3/api/enterprise/bs-months/2087", params={"mode": "solar_civil"})
    static = _get(client, "/v3/api/enterprise/bs-months/2087", params={"mode": "static_lookup"})
    compare = _get(client, "/v3/api/enterprise/bs-months/2087", params={"mode": "compare"})

    evidence = {
        "canonical_default": _summary(canonical),
        "solar_civil_explicit": _summary(solar),
        "static_lookup_explicit": _summary(static),
        "compare": _summary(compare),
    }
    evidence_json = json.dumps(evidence, indent=2, sort_keys=True)

    return f"""# Phase 00 Completion Report: Trust Arrest and Public Surface Repair

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
{evidence_json}
```

## Limitations
- Canonical mode is a Phase 00 policy-like selector, not the full future Policy VM.
- Project Parva remains decision-support infrastructure, not government, legal, tax, payroll, banking, religious, or panchanga authority.
- Static lookup remains available only for explicit compatibility/reference review.

## Next Phase Readiness
- Phase 01 can rely on BS month metadata no longer upgrading low-authority static lookup into high-authority-looking public output.
"""


def main() -> int:
    report = build_report()
    PRIMARY_REPORT.parent.mkdir(parents=True, exist_ok=True)
    PRIMARY_REPORT.write_text(report, encoding="utf-8")
    DETAILED_REPORT.write_text(report, encoding="utf-8")
    print(f"Wrote {PRIMARY_REPORT.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {DETAILED_REPORT.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
