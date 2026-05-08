#!/usr/bin/env python3
"""Parse public Rat32/NepaliCalendar month pages into witness rows."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.data_acquisition import (  # noqa: E402
    WITNESS_DIR,
    WITNESS_FIELDS,
    extract_rat32_pages,
)


def main() -> int:
    witnesses, attempts, failures = extract_rat32_pages()
    out = WITNESS_DIR / "rat32_extracted_witnesses.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=WITNESS_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(witnesses)
    print(json.dumps({"rows": len(witnesses), "attempts": len(attempts), "failures": len(failures), "out": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
