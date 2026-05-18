#!/usr/bin/env python3
"""Generate committed offline proofpack and Timepack examples for reviewers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.membranes.proofpack import proof_pack
from app.membranes.timepack import build_timepack
from app.sources.hashing import canonical_json_hash
from app.workflows.date_risk_audit import build_date_risk_timepack

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = PROJECT_ROOT / "tests" / "fixtures" / "proof"
EXAMPLE_ROOT = PROJECT_ROOT / "examples" / "external"
PAYROLL_EXAMPLES = PROJECT_ROOT / "examples" / "payroll"


def _load_fixture(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _stable_timepack(membrane: dict[str, Any], level: str = "replay") -> dict[str, Any]:
    payload = build_timepack(membrane, level)
    payload["created_at"] = "2026-01-01T00:00:00+00:00"
    return payload


def _payroll_rows() -> list[dict[str, str]]:
    return [
        {
            "employee_id": "sample-001",
            "bs_date": "2082-01-02",
            "workflow_type": "payroll_cutoff",
            "expected_behavior": "working_day",
            "actual_ad_date": "2025-04-15",
        },
        {
            "employee_id": "sample-002",
            "bs_date": "2082-01-01",
            "workflow_type": "payroll_cutoff",
            "expected_behavior": "working_day",
            "actual_ad_date": "2025-04-14",
        },
        {
            "employee_id": "sample-003",
            "bs_date": "2082-01-32",
            "workflow_type": "payroll_cutoff",
            "expected_behavior": "valid_bs_date",
            "actual_ad_date": "",
        },
    ]


def _write_payroll_examples(rows: list[dict[str, str]], timepack: dict[str, Any]) -> None:
    PAYROLL_EXAMPLES.mkdir(parents=True, exist_ok=True)
    headers = ["employee_id", "bs_date", "workflow_type", "expected_behavior", "actual_ad_date"]
    clean = [rows[0]]
    risky = rows
    for name, content_rows in (("clean.csv", clean), ("risky.csv", risky)):
        lines = [",".join(headers)]
        for row in content_rows:
            lines.append(",".join(str(row.get(header, "")) for header in headers))
        (PAYROLL_EXAMPLES / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    _write_json(PAYROLL_EXAMPLES / "report.example.timepack.json", timepack)


def main() -> int:
    civil = _load_fixture(FIXTURE_ROOT / "civil" / "bs_to_ad_valid.json")["membrane"]
    panchanga = _load_fixture(FIXTURE_ROOT / "panchanga" / "summary_kathmandu_2025_04_14.json")["membrane"]
    payroll_rows = _payroll_rows()
    payroll_timepack = build_date_risk_timepack(payroll_rows)
    payroll_timepack["created_at"] = "2026-01-01T00:00:00+00:00"

    examples = {
        EXAMPLE_ROOT / "proofpacks" / "civil-conversion.proofpack.json": proof_pack(civil, "replay"),
        EXAMPLE_ROOT / "proofpacks" / "panchanga-summary.proofpack.json": proof_pack(panchanga, "replay"),
        EXAMPLE_ROOT / "proofpacks" / "payroll-row.proofpack.json": payroll_timepack["proof_packs"][0],
        EXAMPLE_ROOT / "timepacks" / "civil-conversion.timepack.json": _stable_timepack(civil),
        EXAMPLE_ROOT / "timepacks" / "panchanga-summary.timepack.json": _stable_timepack(panchanga),
        EXAMPLE_ROOT / "timepacks" / "payroll-date-risk.timepack.json": payroll_timepack,
    }
    for path, payload in examples.items():
        _write_json(path, payload)
    _write_payroll_examples(payroll_rows, payroll_timepack)

    manifest = {
        "artifact_count": len(examples),
        "artifacts": [
            {"path": path.relative_to(PROJECT_ROOT).as_posix(), "sha256": canonical_json_hash(payload)}
            for path, payload in sorted(examples.items(), key=lambda item: item[0].as_posix())
        ],
        "claim_boundary": "offline_review_examples_not_external_validation",
        "not_authority": True,
    }
    _write_json(EXAMPLE_ROOT / "reviewer-bundle" / "manifest.json", manifest)
    print(f"Wrote {len(examples)} proof artifacts under {EXAMPLE_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
