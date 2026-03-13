from __future__ import annotations

from datetime import datetime, timezone

from app.calendar.adhik_maas import get_lunar_month_boundaries
from app.calendar.adhik_maas import get_lunar_month_name as get_shared_lunar_month_name
from app.calendar.tithi.tithi_core import get_lunar_month_name


def test_tithi_core_lunar_month_name_uses_shared_sankranti_rule():
    _, purnima, _ = get_lunar_month_boundaries(datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert get_lunar_month_name(purnima) == get_shared_lunar_month_name(purnima)


def test_tithi_core_lunar_month_requires_datetime():
    try:
        get_lunar_month_name(180.0)  # type: ignore[arg-type]
    except TypeError as exc:
        assert "datetime" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected TypeError for non-datetime input")
