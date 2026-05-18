#!/usr/bin/env python3
"""Generate/check the external reviewer packet dry-audit report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = PROJECT_ROOT / "reports/external/reviewer_dry_audit.json"
OUT_MD = PROJECT_ROOT / "reports/external/reviewer_dry_audit.md"

REQUIRED_DOCS = [
    "docs/external/REVIEWER_PACKET.md",
    "docs/external/AUDITOR_REPLAY_GUIDE.md",
    "docs/external/PANCHANGA_REVIEW_GUIDE.md",
    "docs/external/FORBIDDEN_CLAIMS.md",
    "docs/external/SAFE_CLAIMS.md",
    "docs/external/WITNESS_SUBMISSION_GUIDE.md",
    "docs/external/CONFORMANCE_REVIEW_CHECKLIST.md",
    "docs/external/REVIEW_CHECKLIST.md",
    "docs/external/REVIEWER_DRY_RUN.md",
]

REQUIRED_ARTIFACTS = [
    "examples/external/proofpacks/civil-conversion.proofpack.json",
    "examples/external/proofpacks/panchanga-summary.proofpack.json",
    "examples/external/timepacks/payroll-date-risk.timepack.json",
    "examples/external/reviewer-bundle/manifest.json",
    "reports/source_coverage/coverage_matrix.json",
    "reports/proof_contract/route_proof_matrix.json",
]


def build_report() -> dict[str, object]:
    docs = [{"path": path, "exists": (PROJECT_ROOT / path).exists()} for path in REQUIRED_DOCS]
    artifacts = [{"path": path, "exists": (PROJECT_ROOT / path).exists()} for path in REQUIRED_ARTIFACTS]
    missing = [item["path"] for item in docs + artifacts if not item["exists"]]
    return {
        "schema": "parva-external-review-dry-audit-v1",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "status": "pass" if not missing else "fail",
        "external_review_claimed": False,
        "live_api_required": False,
        "real_jpl_required": False,
        "verified_locally": [
            "reviewer dry-run instructions present",
            "civil proofpack artifact present",
            "Panchanga proofpack artifact present",
            "payroll/date-risk Timepack artifact present",
            "source coverage report present",
            "route proof matrix present",
        ],
        "skipped_or_external": [
            "real external reviewer signature",
            "institutional adoption",
            "third-party certification",
            "government approval",
            "real JPL kernel lane unless configured by reviewer",
        ],
        "missing": missing,
        "docs": docs,
        "artifacts": artifacts,
        "challenge_process": "Use docs/external/WITNESS_SUBMISSION_GUIDE.md and include artifact id, disputed field, source/method evidence, and proposed correction.",
    }


def markdown(report: dict[str, object]) -> str:
    lines = [
        "# External Reviewer Packet Dry Audit",
        "",
        "This is an internal dry audit of the reviewer packet. It is not a real external review.",
        "",
        f"- Status: {report['status']}",
        f"- External review claimed: {report['external_review_claimed']}",
        f"- Live API required: {report['live_api_required']}",
        f"- Real JPL required: {report['real_jpl_required']}",
        "",
        "## Verified Locally",
        "",
    ]
    lines.extend(f"- {item}" for item in report["verified_locally"])  # type: ignore[index]
    lines.extend(["", "## Skipped Or External", ""])
    lines.extend(f"- {item}" for item in report["skipped_or_external"])  # type: ignore[index]
    lines.extend(["", "## Missing", ""])
    missing = report["missing"]  # type: ignore[index]
    if missing:
        lines.extend(f"- {item}" for item in missing)
    else:
        lines.append("- none")
    lines.extend(["", "## Challenge Process", "", str(report["challenge_process"])])
    return "\n".join(lines) + "\n"


def write_report() -> None:
    report = build_report()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(markdown(report), encoding="utf-8")


def check_report() -> list[str]:
    expected = build_report()
    failures: list[str] = []
    if not OUT_JSON.exists() or OUT_JSON.read_text(encoding="utf-8") != json.dumps(expected, indent=2, sort_keys=True) + "\n":
        failures.append("reports/external/reviewer_dry_audit.json is missing or stale")
    if not OUT_MD.exists() or OUT_MD.read_text(encoding="utf-8") != markdown(expected):
        failures.append("reports/external/reviewer_dry_audit.md is missing or stale")
    if expected["missing"]:
        failures.append("external reviewer packet is missing required docs/artifacts")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        failures = check_report()
        if failures:
            for failure in failures:
                print(f"FAIL: {failure}")
            return 1
        print("External reviewer dry-audit report is current.")
        return 0
    write_report()
    print("Wrote reports/external/reviewer_dry_audit.json and .md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
