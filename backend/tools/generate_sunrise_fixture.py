"""Generate Kathmandu sunrise fixture for 50 dates across a year."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from app.calendar.ephemeris.swiss_eph import calculate_sunrise, LAT_KATHMANDU, LON_KATHMANDU
from app.calendar.ephemeris.time_utils import to_nepal_time


def main() -> None:
    start = date(2026, 1, 1)
    rows = []
    current = start
    while len(rows) < 50:
        sunrise_utc = calculate_sunrise(current, LAT_KATHMANDU, LON_KATHMANDU)
        sunrise_npt = to_nepal_time(sunrise_utc)
        rows.append(
            {
                "date": current.isoformat(),
                "sunrise_utc": sunrise_utc.isoformat(),
                "sunrise_npt": sunrise_npt.isoformat(),
                "sunrise_npt_hhmm": sunrise_npt.strftime("%H:%M"),
            }
        )
        current += timedelta(days=7)

    out = {
        "metadata": {
            "location": "Kathmandu",
            "latitude": LAT_KATHMANDU,
            "longitude": LON_KATHMANDU,
            "samples": len(rows),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "notes": "Regression corpus generated from Swiss Ephemeris sunrise calculation.",
        },
        "samples": rows,
    }

    path = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "sunrise_kathmandu_50.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
