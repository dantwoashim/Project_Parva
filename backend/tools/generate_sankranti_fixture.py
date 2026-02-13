"""Generate 24-sankranti regression fixture for two years."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.calendar.sankranti import get_sankrantis_in_year


def main() -> None:
    years = [2026, 2027]
    rows = []
    for year in years:
        sankrantis = get_sankrantis_in_year(year)
        for s in sankrantis:
            rows.append(
                {
                    "year": year,
                    "rashi_index": s["rashi_index"],
                    "rashi_name": s["rashi_name"],
                    "date": s["date"].isoformat(),
                    "datetime_utc": s["datetime_utc"].isoformat(),
                }
            )

    out = {
        "metadata": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "years": years,
            "samples": len(rows),
            "source": "parva_ephemeris_regression_baseline",
        },
        "sankrantis": rows,
    }

    path = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "sankranti_24.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
