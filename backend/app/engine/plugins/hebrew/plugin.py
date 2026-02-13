"""Hebrew calendar plugin (formulaic conversion)."""

from __future__ import annotations

from datetime import date
from math import floor

from ..base import CalendarDate, CalendarMetadata
from ..julian import gregorian_to_jd, jd_to_gregorian


HEBREW_EPOCH = 347995.5


class HebrewCalendarPlugin:
    plugin_id = "hebrew"

    def metadata(self) -> CalendarMetadata:
        return CalendarMetadata(
            plugin_id=self.plugin_id,
            calendar_family="hebrew",
            version="v1",
            confidence="computed",
            supports_reverse=True,
            notes="Formulaic Hebrew calendar conversion (Metonic leap cycle).",
        )

    @staticmethod
    def is_leap_year(year: int) -> bool:
        return ((7 * year) + 1) % 19 < 7

    @staticmethod
    def months_in_year(year: int) -> int:
        return 13 if HebrewCalendarPlugin.is_leap_year(year) else 12

    @staticmethod
    def delay_1(year: int) -> int:
        months = floor(((235 * year) - 234) / 19)
        parts = 12084 + (13753 * months)
        day = (months * 29) + floor(parts / 25920)
        if ((3 * (day + 1)) % 7) < 3:
            day += 1
        return day

    @staticmethod
    def delay_2(year: int) -> int:
        last = HebrewCalendarPlugin.delay_1(year - 1)
        present = HebrewCalendarPlugin.delay_1(year)
        next_ = HebrewCalendarPlugin.delay_1(year + 1)
        if (next_ - present) == 356:
            return 2
        if (present - last) == 382:
            return 1
        return 0

    @staticmethod
    def to_jd(year: int, month: int, day: int) -> float:
        jd = HEBREW_EPOCH + HebrewCalendarPlugin.delay_1(year) + HebrewCalendarPlugin.delay_2(year) + day + 1

        if month < 7:
            for m in range(7, HebrewCalendarPlugin.months_in_year(year) + 1):
                jd += HebrewCalendarPlugin.month_days(year, m)
            for m in range(1, month):
                jd += HebrewCalendarPlugin.month_days(year, m)
        else:
            for m in range(7, month):
                jd += HebrewCalendarPlugin.month_days(year, m)
        return jd

    @staticmethod
    def year_days(year: int) -> int:
        return int(HebrewCalendarPlugin.to_jd(year + 1, 7, 1) - HebrewCalendarPlugin.to_jd(year, 7, 1))

    @staticmethod
    def long_heshvan(year: int) -> bool:
        return HebrewCalendarPlugin.year_days(year) % 10 == 5

    @staticmethod
    def short_kislev(year: int) -> bool:
        return HebrewCalendarPlugin.year_days(year) % 10 == 3

    @staticmethod
    def month_days(year: int, month: int) -> int:
        if month in (2, 4, 6, 10, 13):
            return 29
        if month == 12 and not HebrewCalendarPlugin.is_leap_year(year):
            return 29
        if month == 8 and not HebrewCalendarPlugin.long_heshvan(year):
            return 29
        if month == 9 and HebrewCalendarPlugin.short_kislev(year):
            return 29
        return 30

    @staticmethod
    def from_jd(jd: float) -> tuple[int, int, int]:
        jd = floor(jd) + 0.5
        year = int((jd - HEBREW_EPOCH) / 366) + 1
        while jd >= HebrewCalendarPlugin.to_jd(year + 1, 7, 1):
            year += 1

        if jd < HebrewCalendarPlugin.to_jd(year, 1, 1):
            month = 7
            while month <= HebrewCalendarPlugin.months_in_year(year) and jd > HebrewCalendarPlugin.to_jd(
                year, month, HebrewCalendarPlugin.month_days(year, month)
            ):
                month += 1
        else:
            month = 1
            while month <= 6 and jd > HebrewCalendarPlugin.to_jd(
                year, month, HebrewCalendarPlugin.month_days(year, month)
            ):
                month += 1

        day = int(jd - HebrewCalendarPlugin.to_jd(year, month, 1) + 1)
        return year, month, day

    @staticmethod
    def month_name(year: int, month: int) -> str:
        if HebrewCalendarPlugin.is_leap_year(year):
            names = {
                1: "Nisan",
                2: "Iyar",
                3: "Sivan",
                4: "Tammuz",
                5: "Av",
                6: "Elul",
                7: "Tishrei",
                8: "Heshvan",
                9: "Kislev",
                10: "Tevet",
                11: "Shevat",
                12: "Adar I",
                13: "Adar II",
            }
        else:
            names = {
                1: "Nisan",
                2: "Iyar",
                3: "Sivan",
                4: "Tammuz",
                5: "Av",
                6: "Elul",
                7: "Tishrei",
                8: "Heshvan",
                9: "Kislev",
                10: "Tevet",
                11: "Shevat",
                12: "Adar",
            }
        return names.get(month, "Unknown")

    def convert_from_gregorian(self, value: date) -> CalendarDate:
        year, month, day = self.from_jd(gregorian_to_jd(value))
        return CalendarDate(
            year=year,
            month=month,
            day=day,
            month_name=self.month_name(year, month),
            formatted=f"HY {year} {month:02d}-{day:02d}",
        )

    def convert_to_gregorian(self, year: int, month: int, day: int) -> date:
        return jd_to_gregorian(self.to_jd(year, month, day))

    def month_lengths(self, year: int) -> list[int]:
        return [self.month_days(year, m) for m in range(1, self.months_in_year(year) + 1)]

    def validate(self, year: int, month: int, day: int) -> bool:
        if month < 1 or month > self.months_in_year(year):
            return False
        return 1 <= day <= self.month_days(year, month)
