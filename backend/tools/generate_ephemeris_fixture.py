"""Generate deterministic 500-timestamp ephemeris regression fixture.

This fixture is used to detect accidental changes in Sun/Moon longitude
calculations for the active ephemeris configuration.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

from app.calendar.ephemeris.swiss_eph import get_sun_moon_positions
from app.engine.ephemeris_config import get_ephemeris_config


def random_dt(rng: random.Random, start_year: int = 2000, end_year: int = 2100) -> datetime:
    year = rng.randint(start_year, end_year)
    month = rng.randint(1, 12)
    # conservative day range for all months
    day = rng.randint(1, 28)
    hour = rng.randint(0, 23)
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)


def main() -> None:
    rng = random.Random(42)
    cfg = get_ephemeris_config()

    rows = []
    for _ in range(500):
        dt = random_dt(rng)
        sun, moon = get_sun_moon_positions(dt)
        rows.append(
            {
                "datetime_utc": dt.isoformat(),
                "sun_longitude": round(sun, 8),
                "moon_longitude": round(moon, 8),
            }
        )

    out = {
        "metadata": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "samples": len(rows),
            "seed": 42,
            "range": "2000-2100",
            "coordinate_system": cfg.coordinate_system,
            "ayanamsa": cfg.ayanamsa,
            "ephemeris_mode": cfg.ephemeris_mode,
            "purpose": "regression_fixture",
        },
        "samples": rows,
    }

    fixture_path = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "ephemeris_500.json"
    fixture_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {fixture_path} with {len(rows)} samples")


if __name__ == "__main__":
    main()
