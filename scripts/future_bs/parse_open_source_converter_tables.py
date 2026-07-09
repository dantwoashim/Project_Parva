#!/usr/bin/env python3
"""Parse public open-source BS/AD converter tables as software witnesses."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.research.future_bs.data_acquisition import (  # noqa: E402
    WITNESS_DIR,
    WITNESS_FIELDS,
    extract_open_source_converter_tables,
)


def main() -> int:
    witnesses, attempts, failures = extract_open_source_converter_tables()
    out = WITNESS_DIR / "open_source_converter_witnesses.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=WITNESS_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(witnesses)
    print(json.dumps({"rows": len(witnesses), "attempts": len(attempts), "failures": len(failures), "out": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
