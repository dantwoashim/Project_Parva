#!/usr/bin/env python3
"""Generate/check the public route proof contract matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ROUTES: list[dict[str, object]] = [
    {
        "route": "/v3/api/calendar/bs-to-gregorian",
        "method": "POST",
        "operation": "bs_to_ad",
        "stable_public": True,
        "proof_modes_supported": ["none", "compact", "audit", "replay", "membrane"],
        "contract_test_file": "tests/contract/test_route_proof_contract_matrix.py",
        "openapi_schema_refs": ["ProofReceipt", "MembraneArtifact", "BoundaryVector", "FieldProvenance"],
        "verification_status": "covered",
    },
    {
        "route": "/v3/api/calendar/convert",
        "method": "GET",
        "operation": "ad_to_bs",
        "stable_public": True,
        "proof_modes_supported": ["none", "compact", "audit", "replay", "membrane"],
        "contract_test_file": "tests/contract/test_route_proof_contract_matrix.py",
        "openapi_schema_refs": ["ProofReceipt", "MembraneArtifact", "BoundaryVector", "FieldProvenance"],
        "verification_status": "covered",
    },
    {
        "route": "/v3/api/calendar/validate-bs-date",
        "method": "GET",
        "operation": "validate_bs_date",
        "stable_public": True,
        "proof_modes_supported": ["none", "compact", "audit", "replay", "membrane"],
        "contract_test_file": "tests/contract/test_route_proof_contract_matrix.py",
        "openapi_schema_refs": ["ProofReceipt", "NegativeMembrane", "BoundaryVector", "FieldProvenance"],
        "verification_status": "covered",
    },
    {
        "route": "/v3/api/compliance/holiday",
        "method": "GET",
        "operation": "holiday",
        "stable_public": True,
        "proof_modes_supported": ["none", "compact", "audit", "replay", "membrane"],
        "contract_test_file": "tests/contract/test_route_proof_contract_matrix.py",
        "openapi_schema_refs": ["ProofReceipt", "MembraneArtifact", "BoundaryVector", "FieldProvenance"],
        "verification_status": "covered",
    },
    {
        "route": "/v3/api/compliance/evaluate-date",
        "method": "POST",
        "operation": "working_day",
        "stable_public": True,
        "proof_modes_supported": ["none", "compact", "audit", "replay", "membrane"],
        "contract_test_file": "tests/contract/test_route_proof_contract_matrix.py",
        "openapi_schema_refs": ["ProofReceipt", "MembraneArtifact", "BoundaryVector", "FieldProvenance"],
        "verification_status": "covered",
    },
    {
        "route": "/v3/api/enterprise/fiscal-year/{bs_year}",
        "method": "GET",
        "operation": "fiscal_year",
        "stable_public": True,
        "proof_modes_supported": ["none", "compact", "audit", "replay", "membrane"],
        "contract_test_file": "tests/contract/test_route_proof_contract_matrix.py",
        "openapi_schema_refs": ["ProofReceipt", "MembraneArtifact", "BoundaryVector", "FieldProvenance"],
        "verification_status": "covered",
    },
    {
        "route": "/v3/api/enterprise/bs-months/{bs_year}",
        "method": "GET",
        "operation": "bs_months",
        "stable_public": True,
        "proof_modes_supported": ["none", "compact", "audit", "replay", "membrane"],
        "contract_test_file": "tests/contract/test_route_proof_contract_matrix.py",
        "openapi_schema_refs": ["ProofReceipt", "BranchMembrane", "BoundaryVector", "FieldProvenance"],
        "verification_status": "covered",
    },
    {
        "route": "/v3/api/calendar/panchanga",
        "method": "GET",
        "operation": "panchanga_summary",
        "stable_public": True,
        "proof_modes_supported": ["none", "compact", "audit", "replay", "membrane"],
        "contract_test_file": "tests/contract/test_route_proof_contract_matrix.py",
        "openapi_schema_refs": [
            "ProofReceipt",
            "PanchangaProofArtifact",
            "MethodDocket",
            "EphemerisProviderMetadata",
            "BoundaryVector",
            "FieldProvenance",
        ],
        "verification_status": "covered",
    },
]


def _payload() -> dict[str, object]:
    return {
        "schema": "parva-route-proof-matrix-v1",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "route_count": len(ROUTES),
        "required_proof_modes": ["none", "compact", "audit", "replay", "membrane"],
        "routes": ROUTES,
    }


def _markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Route Proof Contract Matrix",
        "",
        "This matrix records stable public routes with proof-mode contract tests. It does not claim official authority or external validation.",
        "",
        "| Route | Method | Operation | Proof modes | Test | OpenAPI refs | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for route in payload["routes"]:  # type: ignore[index]
        refs = ", ".join(route["openapi_schema_refs"])  # type: ignore[index]
        modes = ", ".join(route["proof_modes_supported"])  # type: ignore[index]
        lines.append(
            f"| {route['route']} | {route['method']} | {route['operation']} | {modes} | "
            f"{route['contract_test_file']} | {refs} | {route['verification_status']} |"
        )
    return "\n".join(lines) + "\n"


def _write() -> None:
    out_dir = PROJECT_ROOT / "reports/proof_contract"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = _payload()
    (out_dir / "route_proof_matrix.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "route_proof_matrix.md").write_text(_markdown(payload), encoding="utf-8")


def _check() -> list[str]:
    payload = _payload()
    expected_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    expected_md = _markdown(payload)
    failures: list[str] = []
    json_path = PROJECT_ROOT / "reports/proof_contract/route_proof_matrix.json"
    md_path = PROJECT_ROOT / "reports/proof_contract/route_proof_matrix.md"
    if not json_path.exists() or json_path.read_text(encoding="utf-8") != expected_json:
        failures.append("reports/proof_contract/route_proof_matrix.json is missing or stale")
    if not md_path.exists() or md_path.read_text(encoding="utf-8") != expected_md:
        failures.append("reports/proof_contract/route_proof_matrix.md is missing or stale")
    for route in payload["routes"]:  # type: ignore[index]
        modes = route["proof_modes_supported"]  # type: ignore[index]
        if modes != ["none", "compact", "audit", "replay", "membrane"]:
            failures.append(f"{route['route']} does not list the full proof-mode contract")
        if not (PROJECT_ROOT / str(route["contract_test_file"])).exists():
            failures.append(f"missing contract test file for {route['route']}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        failures = _check()
        if failures:
            for failure in failures:
                print(f"FAIL: {failure}")
            return 1
        print("Route proof contract matrix is current.")
        return 0
    _write()
    print("Wrote reports/proof_contract/route_proof_matrix.json and .md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
