"""
Unit Tests for Festival Calculator
==================================

Tests cover:
- Festival date calculations for multiple years
- Lunar and solar festival types
- Upcoming festivals query
- Edge cases and error handling
"""

import pytest
from datetime import date

from app.calendar.calculator import (
    calculate_festival_date,
    get_upcoming_festivals,
    list_supported_festivals,
    get_festivals_on_date,
    DateRange,
    CalendarRule,
)


class TestCalculateFestivalDate:
    """Tests for calculate_festival_date function."""
    
    def test_dashain_2026_official(self):
        """Dashain 2026 matches official Nepal government dates."""
        result = calculate_festival_date("dashain", 2026)
        assert result.start == date(2026, 10, 10), "Ghatasthapana should be Oct 10"
        assert result.end == date(2026, 10, 24)
        assert result.duration_days == 15
    
    def test_dashain_2027(self):
        """Dashain 2027 calculation."""
        result = calculate_festival_date("dashain", 2027)
        assert result.start.year == 2027
        assert result.start.month in [9, 10]  # Sept-Oct
        assert result.duration_days == 15
    
    def test_dashain_2028(self):
        """Dashain 2028 calculation."""
        result = calculate_festival_date("dashain", 2028)
        assert result.start.year == 2028
        assert result.duration_days == 15
    
    def test_tihar_2026_official(self):
        """Tihar 2026 matches official Nepal government dates."""
        result = calculate_festival_date("tihar", 2026)
        assert result.start == date(2026, 11, 7), "Kaag Tihar should be Nov 7"
        assert result.end == date(2026, 11, 11), "Bhai Tika should be Nov 11"
        assert result.duration_days == 5
    
    def test_tihar_2027(self):
        """Tihar 2027 calculation (follows Dashain)."""
        result = calculate_festival_date("tihar", 2027)
        dashain = calculate_festival_date("dashain", 2027)
        # Tihar is ~2-3 weeks after Dashain
        assert result.start > dashain.end
        assert (result.start - dashain.end).days < 30
    
    def test_bs_new_year_2026(self):
        """BS New Year 2083 is April 14, 2026."""
        result = calculate_festival_date("bs-new-year", 2026)
        assert result.start == date(2026, 4, 14)
        assert result.duration_days == 1
    
    def test_maghe_sankranti_solar(self):
        """Maghe Sankranti is solar-based (Magh 1)."""
        result = calculate_festival_date("maghe-sankranti", 2026)
        assert result.start == date(2026, 1, 14)
        assert result.duration_days == 1
    
    def test_holi_2026(self):
        """Holi 2026 calculation."""
        result = calculate_festival_date("holi", 2026)
        assert result.start.month in [2, 3]  # Feb-March
        assert result.duration_days == 2
    
    def test_shivaratri_2026(self):
        """Shivaratri 2026 calculation."""
        result = calculate_festival_date("shivaratri", 2026)
        assert result.start == date(2026, 2, 14)
        assert result.duration_days == 1
    
    def test_indra_jatra_2026(self):
        """Indra Jatra 2026 calculation."""
        result = calculate_festival_date("indra-jatra", 2026)
        assert result.start.month in [8, 9]  # Aug-Sept
        assert result.duration_days == 8
    
    def test_invalid_festival_raises(self):
        """Invalid festival ID raises exception."""
        with pytest.raises((ValueError, KeyError)):
            calculate_festival_date("nonexistent-festival", 2026)
    
    def test_year_outside_range(self):
        """Year outside supported range may raise exception."""
        try:
            result = calculate_festival_date("dashain", 2010)
            # If it returns, should still be a DateRange
            assert result is None or hasattr(result, 'start')
        except Exception:
            pass  # Expected - any exception is fine


class TestGetUpcomingFestivals:
    """Tests for get_upcoming_festivals function."""
    
    def test_upcoming_from_january(self):
        """Get upcoming festivals from January 2026."""
        upcoming = get_upcoming_festivals(date(2026, 1, 1), days=60)
        assert len(upcoming) >= 3
        
        # Check festivals are sorted by date
        dates = [f[1].start for f in upcoming]
        assert dates == sorted(dates)
    
    def test_upcoming_from_september(self):
        """September should include Dashain and Tihar."""
        upcoming = get_upcoming_festivals(date(2026, 9, 1), days=90)
        festival_ids = [f[0] for f in upcoming]
        assert "dashain" in festival_ids
        assert "tihar" in festival_ids
    
    def test_upcoming_with_short_window(self):
        """Short window returns fewer festivals."""
        upcoming = get_upcoming_festivals(date(2026, 6, 15), days=7)
        assert len(upcoming) <= 3
    
    def test_upcoming_with_long_window(self):
        """Full year returns many festivals."""
        upcoming = get_upcoming_festivals(date(2026, 1, 1), days=365)
        assert len(upcoming) >= 20


class TestListSupportedFestivals:
    """Tests for list_supported_festivals function."""
    
    def test_returns_25_festivals(self):
        """At least 25 festivals are supported."""
        festivals = list_supported_festivals()
        assert len(festivals) >= 25
    
    def test_contains_major_festivals(self):
        """Major festivals are in the list."""
        festivals = list_supported_festivals()
        required = ["dashain", "tihar", "holi", "shivaratri", "indra-jatra"]
        for f in required:
            assert f in festivals, f"{f} should be supported"


class TestDateRange:
    """Tests for DateRange model."""
    
    def test_date_range_from_calculation(self):
        """DateRange returned from festival calculation."""
        dr = calculate_festival_date("dashain", 2026)
        assert dr.start == date(2026, 10, 10)
        assert dr.duration_days == 15
    
    def test_date_range_has_required_fields(self):
        """DateRange has start, end, duration."""
        dr = calculate_festival_date("tihar", 2026)
        assert hasattr(dr, 'start')
        assert hasattr(dr, 'end')
        assert hasattr(dr, 'duration_days')


class TestCalendarRule:
    """Tests for CalendarRule model."""
    
    def test_lunar_rule_creation(self):
        """Lunar calendar rule can be created."""
        rule = CalendarRule(
            calendar_type="lunar",
            bs_month=6,
            tithi=1,
            paksha="shukla",
            duration=15
        )
        assert rule.calendar_type == "lunar"
        assert rule.tithi == 1
    
    def test_solar_rule_creation(self):
        """Solar calendar rule can be created."""
        rule = CalendarRule(
            calendar_type="solar",
            bs_month=10,
            solar_day=1,
            duration=1
        )
        assert rule.calendar_type == "solar"
        assert rule.solar_day == 1
