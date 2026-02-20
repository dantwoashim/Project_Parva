"""Julian calendar plugin (Gregorian <-> Julian civil calendar)."""

from __future__ import annotations

from datetime import date

from ..base import CalendarDate, CalendarMetadata
from ..julian import gregorian_to_jd, jd_to_gregorian


_MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


class JulianCalendarPlugin:
    plugin_id = "julian"

    def metadata(self) -> CalendarMetadata:
        return CalendarMetadata(
            plugin_id=self.plugin_id,
            calendar_family="julian",
            version="v1",
            confidence="computed",
            supports_reverse=True,
            notes="Civil Julian calendar conversion via Julian Day arithmetic.",
        )

    @staticmethod
    def _from_jd(jd: float) -> tuple[int, int, int]:
        z = int(jd + 0.5)
        c = z + 32082
        d = (4 * c + 3) // 1461
        e = c - (1461 * d) // 4
        m = (5 * e + 2) // 153

        day = e - (153 * m + 2) // 5 + 1
        month = m + 3 - 12 * (m // 10)
        year = d - 4800 + (m // 10)
        return year, month, day

    @staticmethod
    def _to_jd(year: int, month: int, day: int) -> float:
        a = (14 - month) // 12
        y = year + 4800 - a
        m = month + 12 * a - 3
        jd_noon = day + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083
        return jd_noon - 0.5

    @staticmethod
    def _is_leap(year: int) -> bool:
        return year % 4 == 0

    @classmethod
    def _month_days(cls, year: int, month: int) -> int:
        if month == 2:
            return 29 if cls._is_leap(year) else 28
        if month in {4, 6, 9, 11}:
            return 30
        return 31

    def convert_from_gregorian(self, value: date) -> CalendarDate:
        year, month, day = self._from_jd(gregorian_to_jd(value))
        return CalendarDate(
            year=year,
            month=month,
            day=day,
            month_name=_MONTH_NAMES.get(month),
            formatted=f"JUL {year:04d}-{month:02d}-{day:02d}",
        )

    def convert_to_gregorian(self, year: int, month: int, day: int) -> date:
        return jd_to_gregorian(self._to_jd(year, month, day))

    def month_lengths(self, year: int) -> list[int]:
        return [self._month_days(year, month) for month in range(1, 13)]

    def validate(self, year: int, month: int, day: int) -> bool:
        if month < 1 or month > 12:
            return False
        return 1 <= day <= self._month_days(year, month)
