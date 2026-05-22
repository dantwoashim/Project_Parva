#!/usr/bin/env python3
"""Generate public-safe Python coverage artifacts in report-only mode."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COVERAGE_DIR = PROJECT_ROOT / "reports" / "coverage" / "python-public"
XML_REPORT = COVERAGE_DIR / "coverage.xml"
JSON_REPORT = COVERAGE_DIR / "coverage.json"

PUBLIC_MARKER = "not private_source and not wide_corpus and not research_artifact"


def _verify_artifacts() -> None:
    missing = [path for path in (XML_REPORT, JSON_REPORT) if not path.exists() or path.stat().st_size <= 0]
    if missing:
        formatted = ", ".join(str(path.relative_to(PROJECT_ROOT)) for path in missing)
        raise SystemExit(f"Coverage artifact generation failed; missing or empty: {formatted}")
    payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))
    totals = payload.get("totals") or {}
    if "percent_covered" not in totals:
        raise SystemExit("Coverage JSON is missing totals.percent_covered")
    print(
        json.dumps(
            {
                "ok": True,
                "schema": "parva-public-python-coverage-v1",
                "coverage_percent": round(float(totals["percent_covered"]), 2),
                "xml": str(XML_REPORT.relative_to(PROJECT_ROOT)),
                "json": str(JSON_REPORT.relative_to(PROJECT_ROOT)),
            },
            sort_keys=True,
        )
    )


def main() -> int:
    COVERAGE_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-m",
        PUBLIC_MARKER,
        "--ignore=tests/performance",
        "--cov=backend/app",
        "--cov=packages/parva-python/parva",
        "--cov-report=term-missing",
        f"--cov-report=xml:{XML_REPORT}",
        f"--cov-report=json:{JSON_REPORT}",
    ]
    result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    if result.returncode != 0:
        return result.returncode
    _verify_artifacts()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
