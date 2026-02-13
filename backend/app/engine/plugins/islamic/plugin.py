"""Islamic calendar plugin with tabular conversion mode."""

from __future__ import annotations

from datetime import date
from math import ceil, floor

from ..base import CalendarDate, CalendarMetadata
from ..julian import gregorian_to_jd, jd_to_gregorian


ISLAMIC_EPOCH = 1948439.5
ISLAMIC_MONTH_NAMES = {
    1: "Muharram",
    2: "Safar",
    3: "Rabi al-Awwal",
    4: "Rabi al-Thani",
    5: "Jumada al-Awwal",
    6: "Jumada al-Thani",
    7: "Rajab",
    8: "Sha'ban",
    9: "Ramadan",
    10: "Shawwal",
    11: "Dhu al-Qadah",
    12: "Dhu al-Hijjah",
}


class IslamicCalendarPlugin:
    plugin_id = "islamic"

    def metadata(self) -> CalendarMetadata:
        return CalendarMetadata(
            plugin_id=self.plugin_id,
            calendar_family="islamic",
            version="v1",
            confidence="tabular|announced|astronomical",
            supports_reverse=True,
            notes="Tabular Hijri conversion implemented. Astronomical/announced modes carried as metadata options.",
        )

    @staticmethod
    def is_leap_year(year: int) -> bool:
        return ((11 * year) + 14) % 30 < 11

    @staticmethod
    def month_lengths(year: int) -> list[int]:
        lengths = [30 if i % 2 == 0 else 29 for i in range(12)]
        if IslamicCalendarPlugin.is_leap_year(year):
            lengths[-1] = 30
        return lengths

    @staticmethod
    def to_jd(year: int, month: int, day: int) -> float:
        return (
            day
            + ceil(29.5 * (month - 1))
            + (year - 1) * 354
            + floor((3 + 11 * year) / 30)
            + ISLAMIC_EPOCH
            - 1
        )

    @staticmethod
    def from_jd(jd: float) -> tuple[int, int, int]:
        jd = floor(jd) + 0.5
        year = floor((30 * (jd - ISLAMIC_EPOCH) + 10646) / 10631)
        month = int(min(12, ceil((jd - (29 + IslamicCalendarPlugin.to_jd(year, 1, 1))) / 29.5) + 1))
        day = int(jd - IslamicCalendarPlugin.to_jd(year, month, 1) + 1)
        return year, month, day

    def convert_from_gregorian(self, value: date) -> CalendarDate:
        year, month, day = self.from_jd(gregorian_to_jd(value))
        return CalendarDate(
            year=year,
            month=month,
            day=day,
            month_name=ISLAMIC_MONTH_NAMES.get(month),
            formatted=f"AH {year} {month:02d}-{day:02d}",
        )

    def convert_to_gregorian(self, year: int, month: int, day: int) -> date:
        jd = self.to_jd(year, month, day)
        return jd_to_gregorian(jd)

    def validate(self, year: int, month: int, day: int) -> bool:
        if month < 1 or month > 12:
            return False
        return 1 <= day <= self.month_lengths(year)[month - 1]
