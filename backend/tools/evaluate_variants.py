#!/usr/bin/env python3
"""Evaluate regional variant offsets against reference cases."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from app.rules import get_rule_service
from app.rules.variants import calculate_with_variants


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate variant offsets")
    parser.add_argument(
        "--fixture",
        default="tests/fixtures/variants/variant_reference_cases.json",
    )
    parser.add_argument(
        "--output",
        default="reports/variant_evaluation_report.json",
    )
    args = parser.parse_args()

    cases = json.loads(Path(args.fixture).read_text(encoding="utf-8")).get("cases", [])
    svc = get_rule_service()

    results = []
    passed = 0

    for case in cases:
        festival_id = case["festival_id"]
        year = int(case["year"])
        profile_id = case["profile_id"]
        expected_offset = int(case["expected_offset_days"])

        primary = svc.calculate(festival_id, year)
        variants = calculate_with_variants(festival_id, year)
        variant = next((v for v in variants if v.get("profile_id") == profile_id), None)

        if not primary or not variant:
            results.append({
                **case,
                "pass": False,
                "reason": "missing_primary_or_variant",
            })
            continue

        vdate = date.fromisoformat(variant["date"])
        actual_offset = (vdate - primary.start_date).days
        ok = actual_offset == expected_offset
        if ok:
            passed += 1

        results.append({
            **case,
            "primary_date": primary.start_date.isoformat(),
            "variant_date": vdate.isoformat(),
            "actual_offset_days": actual_offset,
            "pass": ok,
        })

    total = len(results)
    report = {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": (passed / total * 100.0) if total else 100.0,
        "results": results,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md_path = out.with_suffix(".md")
    lines = [
        "# Variant Evaluation Report",
        "",
        f"- Total: **{report['total']}**",
        f"- Passed: **{report['passed']}**",
        f"- Failed: **{report['failed']}**",
        f"- Pass rate: **{report['pass_rate']}%**",
        "",
        "| Festival | Profile | Expected Offset | Actual Offset | Pass |",
        "|---|---|---:|---:|---|",
    ]
    for r in report["results"]:
        lines.append(
            f"| {r['festival_id']} | {r['profile_id']} | {r['expected_offset_days']} | {r.get('actual_offset_days', 'n/a')} | {'✅' if r['pass'] else '❌'} |"
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({"output": str(out), "summary": {k: report[k] for k in ('total', 'passed', 'failed', 'pass_rate')}}, indent=2))

    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
