"""
Unit Tests for Tithi (Lunar Day) Calculator
============================================

Tests cover:
- Moon phase calculation
- Tithi calculation
- Find next tithi functionality
- Moon phase names
"""

import pytest
from datetime import date, timedelta, datetime

from app.calendar.tithi import (
    calculate_moon_phase,
    calculate_tithi,
    get_tithi_name,
    find_next_tithi,
    find_purnima,
    find_amavasya,
    get_moon_phase_name,
    is_auspicious_tithi,
    PAKSHA_SHUKLA,
    PAKSHA_KRISHNA,
)


class TestMoonPhase:
    """Test moon phase calculation."""
    
    def test_known_new_moon(self):
        """Test moon phase on known new moon date."""
        # January 21, 2023 was a new moon
        phase = calculate_moon_phase(date(2023, 1, 21))
        # Should be close to 0 or 1 (new moon)
        assert phase < 0.05 or phase > 0.95
    
    def test_approximate_full_moon(self):
        """Test moon phase approximately 15 days after new moon."""
        # Full moon is roughly 14-15 days after new moon
        phase = calculate_moon_phase(date(2023, 1, 21) + timedelta(days=15))
        # Should be close to 0.5 (full moon)
        assert 0.45 < phase < 0.55
    
    def test_phase_range(self):
        """Test that moon phase is always between 0 and 1."""
        test_dates = [
            date(2023, 1, 1),
            date(2024, 6, 15),
            date(2025, 12, 31),
            date(2026, 9, 15),
        ]
        for d in test_dates:
            phase = calculate_moon_phase(d)
            assert 0 <= phase <= 1


class TestTithiCalculation:
    """Test tithi calculation."""
    
    def test_tithi_on_new_moon(self):
        """Test tithi on new moon day."""
        info = calculate_tithi(date(2023, 1, 21))
        tithi = info["display_number"]
        paksha = info["paksha"]
        # Near new moon should be either last tithi of Krishna or first of Shukla
        assert 1 <= tithi <= 15
        assert paksha in (PAKSHA_SHUKLA, PAKSHA_KRISHNA)
    
    def test_tithi_range(self):
        """Test that tithi is always 1-15."""
        for i in range(100):
            d = date(2023, 1, 1) + timedelta(days=i)
            info = calculate_tithi(d)
            tithi = info["display_number"]
            paksha = info["paksha"]
            assert 1 <= tithi <= 15
            assert paksha in (PAKSHA_SHUKLA, PAKSHA_KRISHNA)
    
    def test_full_lunar_cycle(self):
        """Test that a full lunar cycle covers both pakshas."""
        start = date(2023, 1, 21)  # New moon
        shukla_found = False
        krishna_found = False
        
        for i in range(30):
            d = start + timedelta(days=i)
            info = calculate_tithi(d)
            paksha = info["paksha"]
            if paksha == PAKSHA_SHUKLA:
                shukla_found = True
            if paksha == PAKSHA_KRISHNA:
                krishna_found = True
        
        assert shukla_found and krishna_found


class TestGetPaksha:
    """Test get_paksha function."""
    
    def test_get_paksha_returns_valid(self):
        """Test that paksha in calculate_tithi is valid."""
        info = calculate_tithi(date(2023, 1, 21))
        assert info["paksha"] in (PAKSHA_SHUKLA, PAKSHA_KRISHNA)


class TestTithiNames:
    """Test tithi name functions."""
    
    def test_tithi_name_english(self):
        """Test English tithi names."""
        assert get_tithi_name(1) == "Pratipada"
        assert get_tithi_name(8) == "Ashtami"
        assert get_tithi_name(15) == "Purnima"
    
    def test_tithi_name_nepali(self):
        """Test Nepali tithi names."""
        assert get_tithi_name(1, "nepali") == "प्रतिपदा"
        assert get_tithi_name(8, "nepali") == "अष्टमी"
    
    def test_invalid_tithi_raises(self):
        """Test that invalid tithi raises ValueError."""
        with pytest.raises(ValueError):
            get_tithi_name(0)
        with pytest.raises(ValueError):
            get_tithi_name(16)


class TestFindNextTithi:
    """Test find_next_tithi function."""
    
    def test_find_next_purnima(self):
        """Test finding next full moon."""
        start = date(2023, 1, 1)
        result = find_next_tithi(15, PAKSHA_SHUKLA, start)
        assert result is not None
        result_date = result.date() if isinstance(result, datetime) else result
        assert result_date > start
        
        # Verify it's actually Purnima
        info = calculate_tithi(result)
        assert info["display_number"] == 15
        assert info["paksha"] == PAKSHA_SHUKLA
    
    def test_find_next_amavasya(self):
        """Test finding next new moon."""
        start = date(2023, 1, 25)  # After Jan 21 new moon
        result = find_next_tithi(15, PAKSHA_KRISHNA, start)
        assert result is not None
        result_date = result.date() if isinstance(result, datetime) else result
        assert result_date > start
    
    def test_find_specific_tithi(self):
        """Test finding a specific tithi."""
        start = date(2026, 9, 1)
        # Find Shukla Pratipada (Dashain start)
        result = find_next_tithi(1, PAKSHA_SHUKLA, start)
        assert result is not None
        result_date = result.date() if isinstance(result, datetime) else result
        assert result_date > start
    
    def test_invalid_tithi_raises(self):
        """Test that invalid tithi raises ValueError."""
        with pytest.raises(ValueError):
            find_next_tithi(0, PAKSHA_SHUKLA, date(2023, 1, 1))
        with pytest.raises(ValueError):
            find_next_tithi(16, PAKSHA_SHUKLA, date(2023, 1, 1))
    
    def test_invalid_paksha_raises(self):
        """Test that invalid paksha raises ValueError."""
        with pytest.raises(ValueError):
            find_next_tithi(1, "invalid", date(2023, 1, 1))


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_find_purnima(self):
        """Test find_purnima convenience function."""
        result = find_purnima(date(2023, 1, 1))
        assert result is not None
        result_date = result.date() if isinstance(result, datetime) else result
        assert result_date > date(2023, 1, 1)
    
    def test_find_amavasya(self):
        """Test find_amavasya convenience function."""
        result = find_amavasya(date(2023, 1, 1))
        assert result is not None
        result_date = result.date() if isinstance(result, datetime) else result
        assert result_date > date(2023, 1, 1)


class TestMoonPhaseName:
    """Test moon phase name function."""
    
    def test_new_moon_name(self):
        """Test moon phase name on new moon."""
        name = get_moon_phase_name(date(2023, 1, 21))
        assert name == "New Moon"
    
    def test_full_moon_name(self):
        """Test moon phase name around full moon."""
        # Approximately 15 days after new moon
        name = get_moon_phase_name(date(2023, 1, 21) + timedelta(days=15))
        assert name == "Full Moon"
    
    def test_all_phases_covered(self):
        """Test that various phase names are returned over a month."""
        phases = set()
        for i in range(30):
            d = date(2023, 1, 21) + timedelta(days=i)
            phases.add(get_moon_phase_name(d))
        
        # Should have multiple phase names
        assert len(phases) >= 4


class TestAuspiciousTithi:
    """Test auspicious tithi function."""
    
    def test_auspicious_tithis(self):
        """Test known auspicious tithis."""
        # 2, 3, 5, 7, 10, 11, 12, 13, 15 are auspicious
        assert is_auspicious_tithi(2) is True
        assert is_auspicious_tithi(5) is True
        assert is_auspicious_tithi(15) is True
    
    def test_inauspicious_tithis(self):
        """Test rikta (inauspicious) tithis."""
        # 4, 9, 14 are rikta
        assert is_auspicious_tithi(4) is False
        assert is_auspicious_tithi(9) is False
        assert is_auspicious_tithi(14) is False
