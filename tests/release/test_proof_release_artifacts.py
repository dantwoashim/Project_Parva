from __future__ import annotations

import json
from pathlib import Path

from app.membranes.proofpack import verify_proof_pack
from app.membranes.timepack import verify_timepack

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read_json(path: str) -> dict:
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


def test_committed_proofpack_and_timepack_examples_verify_offline() -> None:
    proofpacks = [
        "examples/external/proofpacks/civil-conversion.proofpack.json",
        "examples/external/proofpacks/panchanga-summary.proofpack.json",
        "examples/external/proofpacks/payroll-row.proofpack.json",
    ]
    timepacks = [
        "examples/external/timepacks/civil-conversion.timepack.json",
        "examples/external/timepacks/panchanga-summary.timepack.json",
        "examples/external/timepacks/payroll-date-risk.timepack.json",
    ]

    for path in proofpacks:
        assert verify_proof_pack(_read_json(path)) == (True, "verified")
    for path in timepacks:
        assert verify_timepack(_read_json(path)) == (True, "verified")


def test_openapi_contains_proof_system_schemas() -> None:
    schema = _read_json("docs/api-docs/openapi.public-reference.json")
    components = schema["components"]["schemas"]
    for name in [
        "ProofReceipt",
        "ProofPack",
        "Timepack",
        "BoundaryVector",
        "FieldProvenance",
        "MethodDocket",
        "EphemerisProviderMetadata",
        "PayrollDateRiskReport",
    ]:
        assert name in components


def test_source_coverage_report_and_release_manifest_are_non_authority_artifacts() -> None:
    coverage = _read_json("reports/source_coverage/coverage_matrix.json")
    manifest = _read_json("data/public/release-artifact-manifest.json")

    assert coverage["schema"] == "parva-source-coverage-v1"
    assert coverage["not_authority"] is True
    assert any(row["operation"] == "panchanga_summary" for row in coverage["rows"])
    assert manifest["schema"] == "parva-release-artifact-manifest-v1"
    assert manifest["not_authority"] is True
    assert any(item["path"].startswith("examples/external/proofpacks/") for item in manifest["artifacts"])


def test_local_kernel_formula_replay_source_is_present() -> None:
    source = (PROJECT_ROOT / "packages/parva-local-kernel/src/civil.ts").read_text(encoding="utf-8")
    assert "function bsToAd" in source
    assert "function adToBs" in source
    assert "function fiscalYearResult" in source
    assert "holidayResult" in source
    assert "workingDayResult" in source
    assert "verifyBsMonthReplay" in source
