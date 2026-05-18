#!/usr/bin/env python3
"""Generate/check the optional Panchanga JPL lane report."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.panchanga.ephemeris_provider import (  # noqa: E402
    BuiltInApproxProvider,
    JplEphemerisProvider,
)

OUT_JSON = PROJECT_ROOT / "reports/panchanga/jpl_lane_report.json"
OUT_MD = PROJECT_ROOT / "reports/panchanga/jpl_lane_report.md"


def build_report() -> dict[str, object]:
    fallback = BuiltInApproxProvider().metadata()
    configured = bool(os.getenv("PARVA_JPL_KERNEL_PATH") or os.getenv("PARVA_JPL_DE440_KERNEL"))
    jpl = JplEphemerisProvider().metadata()
    status = "configured" if configured and jpl.get("available") else "skipped"
    return {
        "schema": "parva-jpl-lane-report-v1",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "status": status,
        "real_jpl_kernel_claimed": bool(jpl.get("available") and jpl.get("jpl_backed")),
        "jpl_metadata": jpl,
        "fallback_metadata": fallback,
        "fallback_claims_jpl": bool(fallback.get("jpl_backed")),
        "skip_reason": None
        if status == "configured"
        else "PARVA_JPL_KERNEL_PATH/PARVA_JPL_DE440_KERNEL is not configured; default proof lane uses pinned fixtures and fallback metadata only.",
    }


def markdown(report: dict[str, object]) -> str:
    jpl = report["jpl_metadata"]  # type: ignore[index]
    fallback = report["fallback_metadata"]  # type: ignore[index]
    lines = [
        "# Panchanga JPL Lane Report",
        "",
        "This report does not claim official Panchanga or ritual authority. Real JPL execution is claimed only when a configured kernel is available and hashed.",
        "",
        f"- Status: {report['status']}",
        f"- Real JPL kernel claimed: {report['real_jpl_kernel_claimed']}",
        f"- Skip reason: {report['skip_reason'] or 'none'}",
        f"- JPL provider available: {jpl.get('available', False)}",
        f"- JPL kernel hash: {jpl.get('kernel_hash') or 'not configured'}",
        f"- Fallback provider: {fallback.get('provider_id')}",
        f"- Fallback claims JPL: {report['fallback_claims_jpl']}",
        "",
        "To run the optional real-kernel lane, set `PARVA_JPL_KERNEL_PATH` and optionally `PARVA_JPL_KERNEL_SHA256`, then run `pytest tests/integration/test_jpl_provider_optional.py -q`.",
    ]
    return "\n".join(lines) + "\n"


def write_report() -> None:
    report = build_report()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(markdown(report), encoding="utf-8")


def check_report() -> list[str]:
    expected = build_report()
    expected_json = json.dumps(expected, indent=2, sort_keys=True) + "\n"
    expected_md = markdown(expected)
    failures: list[str] = []
    if not OUT_JSON.exists() or OUT_JSON.read_text(encoding="utf-8") != expected_json:
        failures.append("reports/panchanga/jpl_lane_report.json is missing or stale")
    if not OUT_MD.exists() or OUT_MD.read_text(encoding="utf-8") != expected_md:
        failures.append("reports/panchanga/jpl_lane_report.md is missing or stale")
    if expected["fallback_claims_jpl"]:
        failures.append("fallback ephemeris provider must not claim JPL backing")
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
        print("Panchanga JPL lane report is current.")
        return 0
    write_report()
    print("Wrote reports/panchanga/jpl_lane_report.json and .md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
