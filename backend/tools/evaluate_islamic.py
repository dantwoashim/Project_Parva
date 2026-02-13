#!/usr/bin/env python3
"""Evaluate Islamic observance plugin against fixture cases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.rules.plugins.islamic.plugin import IslamicObservancePlugin


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Islamic plugin")
    parser.add_argument("--fixture", default="tests/fixtures/islamic/islamic_reference.json")
    parser.add_argument("--output", default="reports/islamic_validation_report.json")
    args = parser.parse_args()

    plugin = IslamicObservancePlugin()
    fixture = json.loads(Path(args.fixture).read_text(encoding="utf-8"))

    rows = []
    passed = 0
    for case in fixture.get("cases", []):
        rule_id = case["rule_id"]
        year = int(case["year"])
        mode = case.get("mode", "computed")
        expected = case.get("expected_date")

        result = plugin.calculate(rule_id, year, mode=mode)
        if not result:
            rows.append({**case, "pass": False, "reason": "no_result"})
            continue

        actual = result.start_date.isoformat()
        ok = True if expected is None else actual == expected
        if ok:
            passed += 1

        rows.append({
            **case,
            "actual_date": actual,
            "method": result.method,
            "confidence": result.confidence,
            "pass": ok,
        })

    total = len(rows)
    report = {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": (passed / total * 100.0) if total else 100.0,
        "rows": rows,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(out), "summary": {k: report[k] for k in ('total', 'passed', 'failed', 'pass_rate')}}, indent=2))

    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
