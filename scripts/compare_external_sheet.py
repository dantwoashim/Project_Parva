#!/usr/bin/env python3
"""Compare an external CSV/XLSX sheet against Parva predictions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.compare import compare_external_sheet  # noqa: E402
from app.future_bs.excel_importer import import_month_lengths_file  # noqa: E402
from app.services.future_bs_service import predict_bs_year  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--source-name", default="external_sheet")
    args = parser.parse_args()
    years = import_month_lengths_file(args.path)
    result = compare_external_sheet(args.source_name, years, predict_fn=predict_bs_year)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
