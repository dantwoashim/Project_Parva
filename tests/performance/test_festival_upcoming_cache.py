from __future__ import annotations

import time
from datetime import date

from app.festivals.use_cases import upcoming_festivals_payload


def test_upcoming_festivals_warm_cache_latency_under_300ms():
    kwargs = {
        "days": 30,
        "from_date": date(2026, 10, 21),
        "quality_band": "all",
        "profile": None,
    }
    upcoming_festivals_payload(**kwargs)

    start = time.perf_counter()
    response = upcoming_festivals_payload(**kwargs)
    elapsed = time.perf_counter() - start

    assert response.festivals
    assert elapsed < 0.3
