#!/usr/bin/env python3
"""Evaluate Hebrew plugin conversion/observance fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.engine.plugins.hebrew.plugin import HebrewCalendarPlugin
from app.rules.plugins.hebrew.plugin import HebrewObservancePlugin


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Hebrew plugin")
    parser.add_argument("--fixture", default="tests/fixtures/hebrew/hebrew_reference.json")
    parser.add_argument("--output", default="reports/hebrew_validation_report.json")
    args = parser.parse_args()

    conv = HebrewCalendarPlugin()
    obs = HebrewObservancePlugin()
    fixture = json.loads(Path(args.fixture).read_text(encoding="utf-8"))

    rows = []
    passed = 0

    for case in fixture.get("cases", []):
        if "gregorian" in case:
            y, m, d = [int(v) for v in case["gregorian"].split("-")]
            converted = conv.convert_from_gregorian(__import__("datetime").date(y, m, d))
            back = conv.convert_to_gregorian(converted.year, converted.month, converted.day)
            ok = back.year == y
            rows.append({**case, "converted": converted.formatted, "roundtrip": back.isoformat(), "pass": ok})
            if ok:
                passed += 1
        else:
            result = obs.calculate(case["rule_id"], int(case["year"]))
            ok = result is not None and result.start_date.year == int(case["year"])
            rows.append({**case, "date": result.start_date.isoformat() if result else None, "pass": ok})
            if ok:
                passed += 1

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
