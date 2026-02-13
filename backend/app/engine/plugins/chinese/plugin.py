"""Chinese lunisolar plugin (v1 approximate, table-seeded)."""

from __future__ import annotations

from datetime import date, timedelta

from ..base import CalendarDate, CalendarMetadata


# Lunar New Year reference table (Gregorian) for year-boundary conversion.
LUNAR_NEW_YEAR = {
    2024: date(2024, 2, 10),
    2025: date(2025, 1, 29),
    2026: date(2026, 2, 17),
    2027: date(2027, 2, 6),
    2028: date(2028, 1, 26),
    2029: date(2029, 2, 13),
    2030: date(2030, 2, 3),
}

CHINESE_MONTH_NAMES = {
    1: "Zhengyue",
    2: "Eryue",
    3: "Sanyue",
    4: "Siyue",
    5: "Wuyue",
    6: "Liuyue",
    7: "Qiyue",
    8: "Bayue",
    9: "Jiuyue",
    10: "Shiyue",
    11: "Shiyi Yue",
    12: "Shier Yue",
}


class ChineseCalendarPlugin:
    plugin_id = "chinese"

    def metadata(self) -> CalendarMetadata:
        return CalendarMetadata(
            plugin_id=self.plugin_id,
            calendar_family="chinese_lunisolar",
            version="v1",
            confidence="approximate",
            supports_reverse=True,
            notes="Month/day mapping uses seeded Lunar New Year table and alternating month-length approximation.",
        )

    @staticmethod
    def _month_lengths(year: int) -> list[int]:
        # Approximate alternating lunar month lengths.
        return [30 if i % 2 == 0 else 29 for i in range(12)]

    def _lunar_year_for_date(self, value: date) -> int:
        years = sorted(LUNAR_NEW_YEAR.keys())
        for y in reversed(years):
            if value >= LUNAR_NEW_YEAR[y]:
                return y
        return years[0]

    def convert_from_gregorian(self, value: date) -> CalendarDate:
        ly = self._lunar_year_for_date(value)
        start = LUNAR_NEW_YEAR[ly]
        delta = (value - start).days
        month = 1
        day = delta + 1
        for ml in self._month_lengths(ly):
            if day > ml:
                day -= ml
                month += 1
            else:
                break
        if month > 12:
            month = 12
            day = min(day, self._month_lengths(ly)[-1])

        return CalendarDate(
            year=ly,
            month=month,
            day=day,
            month_name=CHINESE_MONTH_NAMES.get(month),
            formatted=f"CY {ly} M{month:02d} D{day:02d}",
        )

    def convert_to_gregorian(self, year: int, month: int, day: int) -> date:
        if year not in LUNAR_NEW_YEAR:
            raise ValueError("Chinese plugin v1 only supports years present in Lunar New Year table")
        if not self.validate(year, month, day):
            raise ValueError("Invalid Chinese date")

        start = LUNAR_NEW_YEAR[year]
        offset = day - 1
        for i in range(month - 1):
            offset += self._month_lengths(year)[i]
        return start + timedelta(days=offset)

    def month_lengths(self, year: int) -> list[int]:
        return self._month_lengths(year)

    def validate(self, year: int, month: int, day: int) -> bool:
        if month < 1 or month > 12:
            return False
        return 1 <= day <= self._month_lengths(year)[month - 1]
