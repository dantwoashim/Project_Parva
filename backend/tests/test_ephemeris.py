"""
Test Suite for Project Parva v2.0 Ephemeris Engine

Comprehensive tests covering:
- Swiss Ephemeris wrapper
- Tithi calculations
- Panchanga elements
- Sankranti detection
- Adhik Maas detection
- Festival date calculations

Target: 50+ test cases
"""

import pytest
from datetime import datetime, date, timezone, timedelta
from typing import Dict, Any


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def kathmandu_coords():
    """Kathmandu coordinates for sunrise tests."""
    return {
        "latitude": 27.7172,
        "longitude": 85.3240,
        "altitude": 1400.0
    }


@pytest.fixture
def known_dates():
    """
    Expected festival dates for validation.
    These are computed by ephemeris - may differ slightly from government calendars
    due to different calculation methods (udaya tithi vs purnimant vs amant).
    """
    return {
        # Dashain: Ashwin Shukla 1 (Ghatasthapana)
        "dashain_2026": date(2026, 10, 10),  # Ephemeris: Ashwin Shukla Pratipada
        # Tihar: Kartik Krishna 14 (Kaag Tihar)
        "tihar_2026": date(2026, 11, 7),
        "shivaratri_2026": date(2026, 2, 16),  # Krishna Chaturdashi
        "holi_2026": date(2026, 3, 3),
        "buddha_jayanti_2026": date(2026, 5, 12),
        "makara_sankranti_2026": date(2026, 1, 14),
        "bs_new_year_2083": date(2026, 4, 14),
    }


# =============================================================================
# SWISS EPHEMERIS TESTS
# =============================================================================

class TestSwissEphemeris:
    """Tests for swiss_eph.py module."""
    
    def test_julian_day_utc(self):
        """Test Julian Day calculation requires UTC timezone."""
        from app.calendar.ephemeris.swiss_eph import get_julian_day, TimezoneError
        
        # Should work with UTC
        dt = datetime(2026, 2, 6, 12, 0, 0, tzinfo=timezone.utc)
        jd = get_julian_day(dt)
        assert jd > 0
        assert abs(jd - 2461078.0) < 0.01  # Approximate expected value
    
    def test_julian_day_requires_timezone(self):
        """Test that naive datetime raises TimezoneError."""
        from app.calendar.ephemeris.swiss_eph import get_julian_day, TimezoneError
        
        dt = datetime(2026, 2, 6, 12, 0, 0)  # Naive
        with pytest.raises(TimezoneError):
            get_julian_day(dt)
    
    def test_julian_day_with_nepal_tz(self):
        """Test Julian Day calculation with Nepal timezone."""
        from app.calendar.ephemeris.swiss_eph import get_julian_day
        from app.calendar.ephemeris.time_utils import NEPAL_TZ
        
        dt_nepal = datetime(2026, 2, 6, 17, 45, 0, tzinfo=NEPAL_TZ)  # 17:45 NPT
        dt_utc = datetime(2026, 2, 6, 12, 0, 0, tzinfo=timezone.utc)  # Same instant
        
        jd_nepal = get_julian_day(dt_nepal)
        jd_utc = get_julian_day(dt_utc)
        
        assert abs(jd_nepal - jd_utc) < 0.0001  # Should be same JD
    
    def test_sun_longitude_range(self):
        """Test Sun longitude is in valid range."""
        from app.calendar.ephemeris.swiss_eph import get_sun_longitude
        
        dt = datetime(2026, 2, 6, 12, 0, 0, tzinfo=timezone.utc)
        sun_long = get_sun_longitude(dt)
        
        assert 0 <= sun_long < 360
    
    def test_moon_longitude_range(self):
        """Test Moon longitude is in valid range."""
        from app.calendar.ephemeris.swiss_eph import get_moon_longitude
        
        dt = datetime(2026, 2, 6, 12, 0, 0, tzinfo=timezone.utc)
        moon_long = get_moon_longitude(dt)
        
        assert 0 <= moon_long < 360
    
    def test_sunrise_calculation(self, kathmandu_coords):
        """Test sunrise calculation for Kathmandu."""
        from app.calendar.ephemeris.swiss_eph import calculate_sunrise
        from app.calendar.ephemeris.time_utils import to_nepal_time
        
        sunrise = calculate_sunrise(date(2026, 2, 6))
        sunrise_nepal = to_nepal_time(sunrise)
        
        # Sunrise should be between 5:30 and 7:00 AM Nepal time
        assert sunrise_nepal.hour in [5, 6]
    
    def test_ephemeris_info(self):
        """Test ephemeris info returns correct metadata."""
        from app.calendar.ephemeris.swiss_eph import get_ephemeris_info
        
        info = get_ephemeris_info()
        assert info["mode"] == "swiss_moshier"
        assert info["accuracy"] == "arcsecond"
        assert info["library"] == "pyswisseph"


# =============================================================================
# POSITIONS TESTS
# =============================================================================

class TestPositions:
    """Tests for positions.py module."""
    
    def test_tithi_angle_range(self):
        """Test tithi angle (elongation) is in valid range."""
        from app.calendar.ephemeris.positions import get_tithi_angle
        
        dt = datetime(2026, 2, 6, 12, 0, 0, tzinfo=timezone.utc)
        elongation = get_tithi_angle(dt)
        
        assert 0 <= elongation < 360
    
    def test_nakshatra_valid(self):
        """Test nakshatra calculation returns valid result."""
        from app.calendar.ephemeris.positions import get_nakshatra
        
        dt = datetime(2026, 2, 6, 12, 0, 0, tzinfo=timezone.utc)
        num, name, progress = get_nakshatra(dt)
        
        assert 1 <= num <= 27
        assert len(name) > 0
        assert 0 <= progress < 1
    
    def test_yoga_valid(self):
        """Test yoga calculation returns valid result."""
        from app.calendar.ephemeris.positions import get_yoga
        
        dt = datetime(2026, 2, 6, 12, 0, 0, tzinfo=timezone.utc)
        num, name, progress = get_yoga(dt)
        
        assert 1 <= num <= 27
        assert len(name) > 0
        assert 0 <= progress < 1
    
    def test_karana_valid(self):
        """Test karana calculation returns valid result."""
        from app.calendar.ephemeris.positions import get_karana
        
        dt = datetime(2026, 2, 6, 12, 0, 0, tzinfo=timezone.utc)
        num, name = get_karana(dt)
        
        assert 1 <= num <= 60
        assert len(name) > 0
    
    def test_vaara_valid(self):
        """Test vaara (weekday) returns correct day."""
        from app.calendar.ephemeris.positions import get_vaara
        
        # Feb 6, 2026 is a Friday
        dt = datetime(2026, 2, 6, 12, 0, 0, tzinfo=timezone.utc)
        num, sanskrit, english = get_vaara(dt)
        
        assert english == "Friday"
        assert sanskrit == "Shukravara"
    
    def test_sun_rashi(self):
        """Test Sun rashi calculation."""
        from app.calendar.ephemeris.positions import get_sun_rashi
        
        # Feb 6, 2026 - Sun should be in Makara or Kumbha
        dt = datetime(2026, 2, 6, 12, 0, 0, tzinfo=timezone.utc)
        num, sanskrit, english = get_sun_rashi(dt)
        
        assert 1 <= num <= 12
        assert english in ["Capricorn", "Aquarius"]


# =============================================================================
# TITHI TESTS
# =============================================================================

class TestTithi:
    """Tests for tithi module."""
    
    def test_calculate_tithi_valid(self):
        """Test tithi calculation returns valid result."""
        from app.calendar.tithi.tithi_core import calculate_tithi
        
        dt = datetime(2026, 2, 6, 12, 0, 0, tzinfo=timezone.utc)
        result = calculate_tithi(dt)
        
        assert 1 <= result["number"] <= 30
        assert result["paksha"] in ["shukla", "krishna"]
        assert 0 <= result["progress"] <= 1
    
    def test_find_next_tithi(self):
        """Test finding next specific tithi."""
        from app.calendar.tithi.tithi_boundaries import find_next_tithi
        
        # Find next Purnima (Shukla 15)
        after = datetime(2026, 2, 6, tzinfo=timezone.utc)
        purnima = find_next_tithi(15, "shukla", after, within_days=30)
        
        assert purnima is not None
        assert purnima > after
    
    def test_find_tithi_end(self):
        """Test finding when current tithi ends."""
        from app.calendar.tithi.tithi_boundaries import find_tithi_end
        
        dt = datetime(2026, 2, 6, 12, 0, 0, tzinfo=timezone.utc)
        end_time = find_tithi_end(dt)
        
        assert end_time > dt
        # Should be within 2 days (max tithi length)
        assert end_time < dt + timedelta(days=2)
    
    def test_udaya_tithi(self):
        """Test udaya tithi (official sunrise-based tithi)."""
        from app.calendar.tithi.tithi_udaya import get_udaya_tithi
        
        result = get_udaya_tithi(date(2026, 2, 6))
        
        assert 1 <= result["tithi"] <= 30
        assert result["paksha"] in ["shukla", "krishna"]
        assert "sunrise_local" in result


# =============================================================================
# PANCHANGA TESTS
# =============================================================================

class TestPanchanga:
    """Tests for panchanga.py module."""
    
    def test_get_panchanga(self):
        """Test complete panchanga calculation."""
        from app.calendar.panchanga import get_panchanga
        
        p = get_panchanga(date(2026, 2, 6))
        
        # Check all 5 elements are present
        assert "tithi" in p
        assert "nakshatra" in p
        assert "yoga" in p
        assert "karana" in p
        assert "vaara" in p
        
        # Check accuracy metadata
        assert p["mode"] == "swiss_moshier"
        assert p["accuracy"] == "arcsecond"
    
    def test_panchanga_summary(self):
        """Test panchanga summary generation."""
        from app.calendar.panchanga import get_panchanga_summary
        
        summary = get_panchanga_summary(date(2026, 2, 6))
        
        assert "Date:" in summary
        assert "Tithi:" in summary
        assert "Nakshatra:" in summary
    
    def test_panchanga_range(self):
        """Test panchanga range generation."""
        from app.calendar.panchanga import get_panchanga_range
        
        panchangas = get_panchanga_range(date(2026, 2, 6), days=7)
        
        assert len(panchangas) == 7


# =============================================================================
# SANKRANTI TESTS
# =============================================================================

class TestSankranti:
    """Tests for sankranti.py module."""
    
    def test_find_makara_sankranti(self):
        """Test Makara Sankranti detection."""
        from app.calendar.sankranti import find_makara_sankranti
        from app.calendar.ephemeris.time_utils import to_nepal_time
        
        makara = find_makara_sankranti(2026)
        nepal_date = to_nepal_time(makara).date()
        
        # Should be around Jan 14-15
        assert nepal_date.month == 1
        assert 13 <= nepal_date.day <= 16
    
    def test_find_mesh_sankranti(self):
        """Test Mesh Sankranti (BS New Year) detection."""
        from app.calendar.sankranti import find_mesh_sankranti
        from app.calendar.ephemeris.time_utils import to_nepal_time
        
        mesh = find_mesh_sankranti(2026)
        nepal_date = to_nepal_time(mesh).date()
        
        # Should be around Apr 13-15
        assert nepal_date.month == 4
        assert 12 <= nepal_date.day <= 16
    
    def test_find_next_sankranti(self):
        """Test finding next sankranti."""
        from app.calendar.sankranti import find_next_sankranti
        
        after = datetime(2026, 2, 6, tzinfo=timezone.utc)
        rashi, name, dt = find_next_sankranti(after)
        
        assert 0 <= rashi <= 11
        assert len(name) > 0
        assert dt > after
    
    def test_bs_month_start(self):
        """Test BS month start calculation."""
        from app.calendar.sankranti import get_bs_month_start
        
        # Baishakh 2082 should start around April 14, 2025
        start = get_bs_month_start(2082, 1)
        assert start.month == 4
        assert start.year == 2025
    
    def test_compute_bs_month_lengths(self):
        """Test computed BS month lengths."""
        from app.calendar.sankranti import compute_bs_month_lengths
        
        lengths = compute_bs_month_lengths(2082)
        
        assert len(lengths) == 12
        assert all(28 <= l <= 33 for l in lengths)  # Reasonable range
        total = sum(lengths)
        assert 364 <= total <= 367  # Year should be ~365 days


# =============================================================================
# ADHIK MAAS TESTS
# =============================================================================

class TestAdhikMaas:
    """Tests for adhik_maas.py module."""
    
    def test_analyze_lunar_month(self):
        """Test lunar month analysis."""
        from app.calendar.adhik_maas import analyze_lunar_month
        
        after = datetime(2026, 2, 6, tzinfo=timezone.utc)
        analysis = analyze_lunar_month(after)
        
        assert "start" in analysis
        assert "end" in analysis
        assert "is_adhik" in analysis
        assert "month_name" in analysis
    
    def test_find_adhik_maas_2026(self):
        """Test finding Adhik Maas in 2026."""
        from app.calendar.adhik_maas import find_adhik_maas_years
        
        adhik_list = find_adhik_maas_years(2026, 2026)
        
        # 2026 has Adhik Jestha
        assert len(adhik_list) >= 1
        names = [a["month_name"] for a in adhik_list]
        assert any("Jestha" in n for n in names)
    
    def test_no_adhik_in_regular_month(self):
        """Test that regular months are not flagged as Adhik."""
        from app.calendar.adhik_maas import analyze_lunar_month
        
        # February 2026 should be regular Falgun
        after = datetime(2026, 2, 10, tzinfo=timezone.utc)
        analysis = analyze_lunar_month(after)
        
        # Current month (Falgun) should not be Adhik
        # (Adhik Jestha is in May 2026)
        assert not analysis["is_adhik"] or "Falgun" not in analysis["month_name"]


# =============================================================================
# FESTIVAL CALCULATOR TESTS
# =============================================================================

class TestFestivalCalculator:
    """Tests for calculator.py module."""
    
    def test_dashain_2026(self, known_dates):
        """Test Dashain 2026 calculation."""
        from app.calendar.calculator import calculate_festival_date
        
        result = calculate_festival_date("dashain", 2026)
        
        # Should be within 2 days of known date
        expected = known_dates["dashain_2026"]
        diff = abs((result.start - expected).days)
        assert diff <= 2, f"Expected ~{expected}, got {result.start}"
    
    def test_tihar_2026(self, known_dates):
        """Test Tihar 2026 calculation."""
        from app.calendar.calculator import calculate_festival_date
        
        result = calculate_festival_date("tihar", 2026)
        
        # Tihar starts with Kaag Tihar
        expected = known_dates["tihar_2026"]
        diff = abs((result.start - expected).days)
        assert diff <= 2, f"Expected ~{expected}, got {result.start}"
    
    def test_shivaratri_2026(self, known_dates):
        """Test Shivaratri 2026 calculation."""
        from app.calendar.calculator import calculate_festival_date
        
        result = calculate_festival_date("shivaratri", 2026)
        
        expected = known_dates["shivaratri_2026"]
        diff = abs((result.start - expected).days)
        assert diff <= 2
    
    def test_solar_festival(self):
        """Test solar-based festival (Maghe Sankranti)."""
        from app.calendar.calculator import calculate_festival_date
        
        result = calculate_festival_date("maghe-sankranti", 2026)
        
        # Should be January 14 or 15
        assert result.start.month == 1
        assert result.start.day in [13, 14, 15, 16]
    
    def test_list_festivals(self):
        """Test listing all supported festivals."""
        from app.calendar.calculator import list_all_festivals
        
        festivals = list_all_festivals()
        
        assert len(festivals) >= 20
        assert "dashain" in festivals
        assert "tihar" in festivals
        assert "holi" in festivals
    
    def test_get_upcoming_festivals(self):
        """Test getting upcoming festivals."""
        from app.calendar.calculator import get_upcoming_festivals
        
        upcoming = get_upcoming_festivals(date(2026, 10, 1), days=30)
        
        # Should find Dashain in October
        festival_ids = [f[0] for f in upcoming]
        assert any("dashain" in f for f in festival_ids)


# =============================================================================
# TIME UTILS TESTS
# =============================================================================

class TestTimeUtils:
    """Tests for time_utils.py module."""
    
    def test_nepal_timezone_offset(self):
        """Test Nepal timezone offset is correct."""
        from app.calendar.ephemeris.time_utils import NEPAL_TZ
        
        # Nepal is UTC+5:45
        offset = NEPAL_TZ.utcoffset(None)
        assert offset == timedelta(hours=5, minutes=45)
    
    def test_to_nepal_time(self):
        """Test UTC to Nepal time conversion."""
        from app.calendar.ephemeris.time_utils import to_nepal_time
        
        utc = datetime(2026, 2, 6, 0, 0, 0, tzinfo=timezone.utc)
        nepal = to_nepal_time(utc)
        
        assert nepal.hour == 5
        assert nepal.minute == 45
    
    def test_to_utc(self):
        """Test Nepal time to UTC conversion."""
        from app.calendar.ephemeris.time_utils import to_utc, NEPAL_TZ
        
        nepal = datetime(2026, 2, 6, 5, 45, 0, tzinfo=NEPAL_TZ)
        utc = to_utc(nepal)
        
        assert utc.hour == 0
        assert utc.minute == 0


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
