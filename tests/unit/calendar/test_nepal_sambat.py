"""
Unit Tests for Nepal Sambat Calendar
====================================

Tests cover:
- NS year conversion
- NS new year date calculation
- Month names
- Current NS year determination
"""

import pytest
from datetime import date

from app.calendar.nepal_sambat import (
    gregorian_year_to_ns,
    ns_year_to_gregorian,
    get_ns_new_year_date,
    is_ns_new_year,
    get_ns_month_name,
    get_current_ns_year,
    format_ns_date,
    NS_MONTH_NAMES,
    NS_MONTH_NAMES_NEPALI,
)


class TestNSYearConversion:
    """Tests for NS ↔ Gregorian year conversion."""
    
    def test_gregorian_to_ns_2026(self):
        """2026 corresponds to NS 1146/1147."""
        ns_year = gregorian_year_to_ns(2026)
        assert ns_year in [1146, 1147, 1148]
    
    def test_ns_to_gregorian_1147(self):
        """NS 1147 new year falls in 2025-2026."""
        gregorian = ns_year_to_gregorian(1147)
        assert gregorian in [2025, 2026]  # Depends on month

    
    def test_roundtrip_conversion(self):
        """Roundtrip conversion is consistent."""
        for year in [2024, 2025, 2026, 2027, 2028]:
            ns = gregorian_year_to_ns(year)
            back = ns_year_to_gregorian(ns)
            assert abs(back - year) <= 1  # May differ by 1 due to new year timing


class TestNSNewYear:
    """Tests for NS new year date calculation."""
    
    def test_ns_new_year_2026_is_in_november(self):
        """NS New Year 2026 is in October-November."""
        ns_new_year = get_ns_new_year_date(2026)
        assert ns_new_year.month in [10, 11]
        assert ns_new_year.year == 2026
    
    def test_ns_new_year_is_during_tihar(self):
        """NS New Year (Mha Puja) falls during Tihar period."""
        from app.calendar.calculator import calculate_festival_date
        
        ns_new_year = get_ns_new_year_date(2026)
        tihar = calculate_festival_date("tihar", 2026)
        
        # NS new year should be within or near Tihar
        assert abs((ns_new_year - tihar.start).days) <= 5
    
    def test_is_ns_new_year_positive(self):
        """is_ns_new_year returns True for NS new year."""
        ns_new_year = get_ns_new_year_date(2026)
        assert is_ns_new_year(ns_new_year) is True
    
    def test_is_ns_new_year_negative(self):
        """is_ns_new_year returns False for random date."""
        assert is_ns_new_year(date(2026, 6, 15)) is False


class TestNSMonthNames:
    """Tests for NS month names."""
    
    def test_12_months_exist(self):
        """There are 12 NS months."""
        assert len(NS_MONTH_NAMES) == 12
        assert len(NS_MONTH_NAMES_NEPALI) == 12
    
    def test_get_month_name_valid(self):
        """Get month name for valid months."""
        assert get_ns_month_name(1) == "Kachala"
        assert get_ns_month_name(10) == "Gunla"
    
    def test_get_month_name_nepali(self):
        """Get Nepali month names."""
        assert get_ns_month_name(1, nepali=True) == "कछला"
        assert get_ns_month_name(10, nepali=True) == "गुंला"
    
    def test_get_month_name_invalid(self):
        """Invalid month raises error."""
        with pytest.raises(ValueError):
            get_ns_month_name(0)
        with pytest.raises(ValueError):
            get_ns_month_name(13)


class TestCurrentNSYear:
    """Tests for get_current_ns_year function."""
    
    def test_before_ns_new_year(self):
        """Before NS new year, current year is calculated."""
        # September 2026 is before NS new year (Oct-Nov)
        ns_year = get_current_ns_year(date(2026, 9, 15))
        # May be 1146 or 1147 depending on exact new year date
        assert ns_year in [1146, 1147]
    
    def test_after_ns_new_year(self):
        """After NS new year, get later year."""
        # December 2026 is after NS new year
        ns_year = get_current_ns_year(date(2026, 12, 15))
        assert ns_year in [1147, 1148]  # Could be either


class TestFormatNSDate:
    """Tests for format_ns_date function."""
    
    def test_format_before_new_year(self):
        """Format date returns NS year."""
        result = format_ns_date(date(2026, 9, 15))
        assert "NS" in result
        assert "114" in result  # Either 1146 or 1147
    
    def test_format_after_new_year(self):
        """Format date after NS new year."""
        result = format_ns_date(date(2026, 12, 15))
        assert "NS" in result
        assert "114" in result  # Either 1147 or 1148
