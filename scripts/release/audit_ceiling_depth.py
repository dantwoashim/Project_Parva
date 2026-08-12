#!/usr/bin/env python3
"""Run local semantic checks for the proof architecture."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.bitplanes.causal import CausalBitplane  # noqa: E402
from app.forge.bitplanes import build_working_day_plane  # noqa: E402
from app.main import app  # noqa: E402
from app.membranes.adversarial import tamper_result_probe  # noqa: E402
from app.membranes.capsule import build_convert_bs_to_ad_capsule  # noqa: E402
from app.membranes.verifier import verify_membrane  # noqa: E402
from app.sources.hashing import canonical_json_hash  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@dataclass(frozen=True)
class AuditCheck:
    name: str
    status: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"name": self.name, "status": self.status, "detail": self.detail}


def _check(name: str, fn: Callable[[], str]) -> AuditCheck:
    try:
        detail = fn()
    except Exception as exc:  # noqa: BLE001 - audit scripts report exact failure text.
        return AuditCheck(name, "fail", f"{type(exc).__name__}: {exc}")
    return AuditCheck(name, "pass", detail)


def _required_paths() -> str:
    required = [
        "backend/app/forge/claim_indexes.py",
        "backend/app/policy/lenses.py",
        "backend/app/policy/trace.py",
        "backend/app/boundary/labels.py",
        "backend/app/membranes/adversarial.py",
        "packages/parva-local-kernel/src/policy.ts",
        "packages/parva-local-kernel/src/boundaries.ts",
        "packages/parva-local-kernel/src/proofpacks.ts",
        "frontend/src/proof/ProofPacketView.jsx",
        "frontend/src/workbench/TemporalWorkbench.jsx",
        "frontend/src/embed/BoundaryEmbed.jsx",
        "docs/spec/PARVA_TRUST_TAINT_ALGEBRA_v1.md",
        "docs/spec/PARVA_FIELD_PROVENANCE_v1.md",
        "docs/spec/PARVA_POLICY_VM_v1.md",
        "docs/spec/PARVA_CONFORMANCE_CAPSULE_v1.md",
    ]
    missing = [path for path in required if not (PROJECT_ROOT / path).exists()]
    if missing:
        raise AssertionError("missing=" + ", ".join(missing))
    return f"required_paths={len(required)}"


def _enterprise_month_contract() -> str:
    response = TestClient(app).get("/v3/api/enterprise/bs-months/2087")
    assert response.status_code == 200, response.text
    body = response.json()
    for key in (
        "requested_mode",
        "selected_method",
        "result",
        "policy_decision",
        "boundary",
        "field_provenance",
    ):
        assert key in body, f"missing {key}"
    assert body["requested_mode"] == "canonical"
    assert body["selected_method"] == "solar_civil"
    assert body["result"]["total_days"] == 365
    assert body["boundary"]["not_authority"] is True
    assert body["field_provenance"]["total_days"]["authority"] == "computed_uncertified"
    return "canonical payload carries proof-facing response contract"


def _enterprise_compare_branch_set() -> str:
    response = TestClient(app).get("/v3/api/enterprise/bs-months/2087", params={"mode": "compare"})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["membrane_kind"] == "branch_set"
    branch_set = body["branch_set"]
    assert branch_set["membrane_kind"] == "branch_set"
    branches = {branch["branch_id"] for branch in branch_set["branches"]}
    assert branches == {"canonical", "solar_civil", "static_lookup"}
    assert body["result"]["disagreement"] is True
    return "compare mode exposes explicit branch-set membrane"


def _capsule_depth() -> str:
    capsule = build_convert_bs_to_ad_capsule(2082, 1, 1)
    ok, reason = verify_membrane(capsule)
    assert ok, reason
    assert capsule["source_snapshot_hash"].startswith("sha256:")
    assert capsule["proof_pack"]["source_artifacts"]["source_snapshot_hash"] == capsule["source_snapshot_hash"]
    assert capsule["field_provenance"]["ad_date"]["source_docket_id"]
    probe = tamper_result_probe(capsule, "ad_date", "2025-04-15")
    assert probe["verified"] is False
    return "capsule binds source snapshot, docket, witness, and tamper failure"


def _bitplane_depth() -> str:
    plane = build_working_day_plane(31, {4, 11, 18, 25})
    payload = plane.as_dict()
    assert len(payload["bits"]) == len(payload["cause_stamps"]) == 31
    assert payload["cause_stamps"][3]["reason"] == "weekend_offset"
    try:
        CausalBitplane(
            name="bad",
            bits=(True,),
            witness_refs=("sample",),
            cause_stamps=(),
        )
    except ValueError:
        return f"cause_stamps=31 hash={payload['hash']}"
    raise AssertionError("unstamped bitplane accepted")


def _claim_index_depth() -> str:
    from app.forge.claim_indexes import ClaimIndexEntry, build_claim_index

    capsule = build_convert_bs_to_ad_capsule(2082, 1, 1)
    index = build_claim_index(
        [
            ClaimIndexEntry(
                claim_id="convert_bs_to_ad:2082-01-01",
                identity_hash=capsule["identity_hash"],
                witness_hash=capsule["witness_hash"],
                source_snapshot_hash=capsule["source_snapshot_hash"],
                boundary=capsule["boundary"],
            )
        ]
    )
    assert index["root_hash"] == f"sha256:{canonical_json_hash(index['leaf_hashes'])}"
    return f"claim_index_root={index['root_hash']}"


EXTERNAL_BLOCKERS = [
    {
        "blocker": "institutional signed review witnesses",
        "reason": "repo has local witness structures but no real external signatures from calendar, government, bank, payroll, or Panchanga institutions",
    },
    {
        "blocker": "external adoption proof",
        "reason": "repo has conformance artifacts and vendor packet, but no verifiable customers, pilots, registry acceptance, or package publication",
    },
    {
        "blocker": "official future-date authority",
        "reason": "must remain unclaimable; public Future-BS behavior is computed_prediction_not_official and review_required",
    },
]


def collect() -> dict[str, Any]:
    checks = [
        _check("required_architecture_paths", _required_paths),
        _check("enterprise_month_contract", _enterprise_month_contract),
        _check("enterprise_compare_branch_set", _enterprise_compare_branch_set),
        _check("conversion_capsule_depth", _capsule_depth),
        _check("causal_bitplane_depth", _bitplane_depth),
        _check("claim_index_depth", _claim_index_depth),
    ]
    return {
        "status": "pass" if all(check.status == "pass" for check in checks) else "fail",
        "scope": "local_ceiling_depth_audit",
        "hard_checks": [check.as_dict() for check in checks],
        "external_blockers": EXTERNAL_BLOCKERS,
        "claim": (
            "Local ceiling primitives are implemented and auditable."
            if all(check.status == "pass" for check in checks)
            else "Local ceiling primitives still have blocking gaps."
        ),
        "not_claimable": [
            "government authority",
            "legal/tax/payroll/banking authority",
            "official future date authority",
            "external certification",
            "customer/adoption proof",
            "public exact unsupported Future-BS predictions",
        ],
    }


def main() -> int:
    payload = collect()
    for check in payload["hard_checks"]:
        print(f"{check['status'].upper()}: {check['name']} - {check['detail']}")
    if payload["status"] != "pass":
        return 1
    print("Ceiling depth audit passed for local hard checks; external blockers remain documented.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
