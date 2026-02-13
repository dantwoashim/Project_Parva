#!/usr/bin/env python3
"""Run plugin validation suite and write report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.engine.plugins.validation import PluginValidationSuite


def main() -> None:
    parser = argparse.ArgumentParser(description="Plugin validation suite")
    parser.add_argument(
        "--fixture",
        default="tests/fixtures/plugins/plugin_validation_cases.json",
        help="Fixture path",
    )
    parser.add_argument(
        "--output",
        default="reports/plugin_validation_report.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    suite = PluginValidationSuite()
    cases = suite.load_cases(Path(args.fixture))
    report = suite.run(cases)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "total": report["total"],
        "passed": report["passed"],
        "failed": report["failed"],
        "pass_rate": report["pass_rate"],
        "output": str(out_path),
    }, indent=2))

    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
