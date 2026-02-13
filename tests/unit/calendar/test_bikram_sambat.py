"""
Unit Tests for Bikram Sambat Calendar Conversion
=================================================

Tests cover:
- BS to Gregorian conversion
- Gregorian to BS conversion  
- Edge cases (year boundaries, month boundaries)
- Validation functions
"""

import pytest
from datetime import date, timedelta

from app.calendar.bikram_sambat import (
    bs_to_gregorian,
    bs_to_gregorian_estimated,
    estimated_bs_to_gregorian,
    estimated_gregorian_to_bs,
    gregorian_to_bs,
    gregorian_to_bs_date,
    is_valid_bs_date,
    days_in_bs_month,
    get_bs_month_name,
    get_bs_month_name_nepali,
    get_bs_year_start,
    get_bs_year_end,
    format_bs_date,
    BSDate,
)


class TestBSToGregorian:
    """Test BS to Gregorian date conversion."""
    
    def test_bs_new_year_2080(self):
        """Test BS New Year 2080 conversion."""
        result = bs_to_gregorian(2080, 1, 1)
        assert result == date(2023, 4, 14)
    
    def test_bs_new_year_2083(self):
        """Test BS New Year 2083 (thesis year)."""
        result = bs_to_gregorian(2083, 1, 1)
        assert result == date(2026, 4, 14)
    
    def test_bs_new_year_2081(self):
        """Test BS New Year 2081."""
        result = bs_to_gregorian(2081, 1, 1)
        # 2080 has 365 days, so 2081 starts April 13/14 2024
        expected = date(2023, 4, 14) + timedelta(days=365)
        assert result == expected
    
    def test_mid_year_date(self):
        """Test conversion of mid-year date."""
        # 2080-06-01 (Ashwin 1)
        result = bs_to_gregorian(2080, 6, 1)
        # Calculate expected: sum of first 5 months
        expected = date(2023, 4, 14) + timedelta(days=31+31+32+31+31)
        assert result == expected
    
    def test_last_day_of_year(self):
        """Test last day of BS year."""
        result = bs_to_gregorian(2080, 12, 30)  # Chaitra 30
        # Should be one day before 2081 new year
        next_year_start = bs_to_gregorian(2081, 1, 1)
        assert result == next_year_start - timedelta(days=1)
    
    def test_various_years(self):
        """Test multiple year conversions."""
        test_cases = [
            (2070, 1, 1),
            (2075, 6, 15),
            (2085, 10, 1),
            (2090, 3, 20),
            (2095, 12, 1),
        ]
        for year, month, day in test_cases:
            result = bs_to_gregorian(year, month, day)
            assert isinstance(result, date)
    
    def test_invalid_year_raises(self):
        """Test that invalid year raises ValueError."""
        with pytest.raises(ValueError):
            bs_to_gregorian(1600, 1, 1)  # Far before extended range
        
        with pytest.raises(ValueError):
            bs_to_gregorian(2500, 1, 1)  # Far after extended range
    
    def test_invalid_month_raises(self):
        """Test that invalid month raises ValueError."""
        with pytest.raises(ValueError):
            bs_to_gregorian(2080, 0, 1)
        
        with pytest.raises(ValueError):
            bs_to_gregorian(2080, 13, 1)
    
    def test_invalid_day_raises(self):
        """Test that invalid day raises ValueError."""
        with pytest.raises(ValueError):
            bs_to_gregorian(2080, 1, 0)
        
        with pytest.raises(ValueError):
            bs_to_gregorian(2080, 1, 35)


class TestGregorianToBS:
    """Test Gregorian to BS date conversion."""
    
    def test_bs_new_year_2080(self):
        """Test Gregorian to BS for New Year 2080."""
        result = gregorian_to_bs(date(2023, 4, 14))
        assert result == (2080, 1, 1)
    
    def test_bs_new_year_2083(self):
        """Test Gregorian to BS for New Year 2083."""
        result = gregorian_to_bs(date(2026, 4, 14))
        assert result == (2083, 1, 1)
    
    def test_day_before_new_year(self):
        """Test last day of previous BS year."""
        result = gregorian_to_bs(date(2023, 4, 13))
        # Should be last day of 2079
        assert result[0] == 2079
        assert result[1] == 12  # Chaitra
    
    def test_day_after_new_year(self):
        """Test second day of BS year."""
        result = gregorian_to_bs(date(2023, 4, 15))
        assert result == (2080, 1, 2)
    
    def test_round_trip_conversion(self):
        """Test that BS -> Gregorian -> BS gives same result."""
        original = (2080, 6, 15)
        gregorian = bs_to_gregorian(*original)
        back_to_bs = gregorian_to_bs(gregorian)
        assert back_to_bs == original
    
    def test_multiple_round_trips(self):
        """Test round trip for various dates."""
        test_dates = [
            (2070, 1, 1),
            (2075, 6, 15),
            (2080, 12, 30),
            (2085, 3, 20),
            (2090, 9, 10),
        ]
        for bs_date in test_dates:
            gregorian = bs_to_gregorian(*bs_date)
            result = gregorian_to_bs(gregorian)
            assert result == bs_date, f"Round trip failed for {bs_date}"
    
    def test_out_of_range_raises(self):
        """Test that out-of-range date raises ValueError."""
        with pytest.raises(ValueError):
            gregorian_to_bs(date(1700, 1, 1))  # Far before extended range

    def test_estimated_wrapper_aliases(self):
        """Explicit estimated wrappers should be callable and consistent."""
        d = date(2050, 2, 15)
        y, m, day = estimated_gregorian_to_bs(d)
        g1 = bs_to_gregorian_estimated(y, m, day)
        g2 = estimated_bs_to_gregorian(y, m, day)
        assert g1 == g2


class TestBSDateNamedTuple:
    """Test BSDate named tuple."""
    
    def test_bsdate_creation(self):
        """Test creating BSDate."""
        bs = BSDate(2080, 6, 15)
        assert bs.year == 2080
        assert bs.month == 6
        assert bs.day == 15
    
    def test_bsdate_str(self):
        """Test BSDate string representation."""
        bs = BSDate(2080, 6, 15)
        assert str(bs) == "2080-06-15"
    
    def test_bsdate_month_name(self):
        """Test BSDate month name property."""
        bs = BSDate(2080, 6, 15)
        assert bs.month_name == "Ashwin"
    
    def test_gregorian_to_bs_date(self):
        """Test gregorian_to_bs_date function."""
        bs = gregorian_to_bs_date(date(2023, 4, 14))
        assert bs.year == 2080
        assert bs.month == 1
        assert bs.day == 1
        assert bs.month_name == "Baishakh"


class TestValidation:
    """Test validation functions."""
    
    def test_valid_date(self):
        """Test is_valid_bs_date for valid dates."""
        assert is_valid_bs_date(2080, 1, 15) is True
        assert is_valid_bs_date(2080, 6, 30) is True
        assert is_valid_bs_date(2080, 3, 32) is True  # Ashadh has 32 days
    
    def test_invalid_year(self):
        """Test is_valid_bs_date for invalid year."""
        assert is_valid_bs_date(2050, 1, 1) is False
        assert is_valid_bs_date(2100, 1, 1) is False
    
    def test_invalid_month(self):
        """Test is_valid_bs_date for invalid month."""
        assert is_valid_bs_date(2080, 0, 1) is False
        assert is_valid_bs_date(2080, 13, 1) is False
    
    def test_invalid_day(self):
        """Test is_valid_bs_date for invalid day."""
        assert is_valid_bs_date(2080, 1, 0) is False
        assert is_valid_bs_date(2080, 1, 35) is False


class TestMonthLength:
    """Test month length functions."""
    
    def test_days_in_month(self):
        """Test days_in_bs_month."""
        # 2080: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
        assert days_in_bs_month(2080, 1) == 31  # Baishakh
        assert days_in_bs_month(2080, 3) == 32  # Ashadh
        assert days_in_bs_month(2080, 8) == 29  # Mangsir
    
    def test_invalid_month_raises(self):
        """Test that invalid month raises ValueError."""
        with pytest.raises(ValueError):
            days_in_bs_month(2080, 0)
        with pytest.raises(ValueError):
            days_in_bs_month(2080, 13)


class TestMonthNames:
    """Test month name functions."""
    
    def test_english_month_names(self):
        """Test get_bs_month_name."""
        assert get_bs_month_name(1) == "Baishakh"
        assert get_bs_month_name(6) == "Ashwin"
        assert get_bs_month_name(12) == "Chaitra"
    
    def test_nepali_month_names(self):
        """Test get_bs_month_name_nepali."""
        assert get_bs_month_name_nepali(1) == "बैशाख"
        assert get_bs_month_name_nepali(6) == "आश्विन"
    
    def test_invalid_month_raises(self):
        """Test that invalid month raises ValueError."""
        with pytest.raises(ValueError):
            get_bs_month_name(0)
        with pytest.raises(ValueError):
            get_bs_month_name(13)


class TestYearBoundaries:
    """Test year start/end functions."""
    
    def test_get_bs_year_start(self):
        """Test get_bs_year_start."""
        assert get_bs_year_start(2080) == date(2023, 4, 14)
        assert get_bs_year_start(2083) == date(2026, 4, 14)
    
    def test_get_bs_year_end(self):
        """Test get_bs_year_end."""
        year_end = get_bs_year_end(2080)
        next_year_start = get_bs_year_start(2081)
        assert year_end == next_year_start - timedelta(days=1)
    
    def test_year_continuity(self):
        """Test that year end + 1 day = next year start."""
        for year in range(2070, 2095):
            year_end = get_bs_year_end(year)
            next_start = get_bs_year_start(year + 1)
            assert year_end + timedelta(days=1) == next_start


class TestFormatting:
    """Test date formatting."""
    
    def test_format_long(self):
        """Test long format."""
        result = format_bs_date(2080, 6, 15)
        assert result == "15 Ashwin, 2080"
    
    def test_format_short(self):
        """Test short format."""
        result = format_bs_date(2080, 6, 15, style="short")
        assert result == "2080-06-15"
    
    def test_format_nepali(self):
        """Test Nepali format."""
        result = format_bs_date(2080, 6, 15, style="nepali")
        assert "आश्विन" in result
        assert "२०८०" in result
