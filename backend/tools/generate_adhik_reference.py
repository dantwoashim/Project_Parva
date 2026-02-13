"""Generate Adhik-Maas reference fixture for BS 2000-2030.

Note: this is a computed regression baseline, not an official publication.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.calendar.lunar_calendar import get_lunar_year


def main() -> None:
    rows = []
    for bs_year in range(2000, 2031):
        gregorian_year = bs_year - 57
        lunar_year = get_lunar_year(gregorian_year)

        adhik_months = sorted({m.full_name for m in lunar_year.months if m.is_adhik})
        rows.append(
            {
                "bs_year": bs_year,
                "gregorian_year": gregorian_year,
                "has_adhik": bool(adhik_months),
                "adhik_months": adhik_months,
            }
        )

    out = {
        "metadata": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "range_bs": "2000-2030",
            "source": "parva_ephemeris_regression_baseline",
        },
        "years": rows,
    }

    path = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "adhik_maas_reference.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
