#!/usr/bin/env python3
"""Audit reconstructed witness corpus and regenerate quality reports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.research.future_bs.data_acquisition import (  # noqa: E402
    coverage_metrics,
    write_corpus_quality_report,
    write_coverage_report,
)


def main() -> int:
    metrics = coverage_metrics()
    write_coverage_report(metrics)
    write_corpus_quality_report(metrics)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
