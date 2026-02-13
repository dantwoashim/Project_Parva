"""Generate boundary corpus for tithi transitions near sunrise."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from app.calendar.tithi.tithi_udaya import get_udaya_tithi, detect_vriddhi, detect_ksheepana


def main() -> None:
    start = date(2025, 1, 1)
    end = date(2028, 12, 31)

    rows = []
    cur = start
    while cur <= end and len(rows) < 30:
        info = get_udaya_tithi(cur)
        sunrise = info["sunrise"]
        tithi_end = info["end_time"]
        delta_hours = abs((tithi_end - sunrise).total_seconds()) / 3600

        # Boundary-sensitive cases: transition within ~2 hours of sunrise.
        if delta_hours <= 2.0:
            rows.append(
                {
                    "date": cur.isoformat(),
                    "tithi": info["tithi"],
                    "paksha": info["paksha"],
                    "vriddhi": detect_vriddhi(cur),
                    "ksheepana": detect_ksheepana(cur),
                    "sunrise_utc": sunrise.isoformat(),
                    "tithi_end_utc": tithi_end.isoformat(),
                    "delta_hours": round(delta_hours, 4),
                }
            )

        cur += timedelta(days=1)

    out = {
        "metadata": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "samples": len(rows),
            "criteria": "tithi boundary within 2h of sunrise",
            "range": f"{start.isoformat()}..{end.isoformat()}",
        },
        "samples": rows,
    }

    path = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "tithi_boundaries_30.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
