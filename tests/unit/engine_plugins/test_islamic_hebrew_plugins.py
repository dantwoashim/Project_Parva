from __future__ import annotations

from datetime import date

from app.engine.plugins.hebrew.plugin import HebrewCalendarPlugin
from app.engine.plugins.islamic.plugin import IslamicCalendarPlugin
from app.rules.plugins.hebrew.plugin import HebrewObservancePlugin
from app.rules.plugins.islamic.plugin import IslamicObservancePlugin


def test_islamic_roundtrip_basic():
    plugin = IslamicCalendarPlugin()
    d = date(2026, 2, 15)
    isl = plugin.convert_from_gregorian(d)
    back = plugin.convert_to_gregorian(isl.year, isl.month, isl.day)
    assert isinstance(back, date)


def test_islamic_announced_override():
    obs = IslamicObservancePlugin()
    out = obs.calculate("eid-al-fitr", 2026, mode="announced")
    assert out is not None
    assert out.method == "announced_override"
    assert out.start_date.isoformat() == "2026-03-20"


def test_hebrew_roundtrip_basic():
    plugin = HebrewCalendarPlugin()
    d = date(2026, 2, 15)
    heb = plugin.convert_from_gregorian(d)
    back = plugin.convert_to_gregorian(heb.year, heb.month, heb.day)
    assert isinstance(back, date)


def test_hebrew_observance_formulaic():
    obs = HebrewObservancePlugin()
    out = obs.calculate("rosh-hashanah", 2026)
    assert out is not None
    assert out.method == "formulaic"
    assert out.start_date.year == 2026
