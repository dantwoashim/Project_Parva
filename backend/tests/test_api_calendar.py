"""
API Integration Tests for Project Parva Calendar Endpoints

Tests the new ephemeris-based calendar API endpoints:
- /api/calendar/panchanga
- /api/calendar/panchanga/range
- /api/calendar/festivals/calculate/{id}
- /api/calendar/festivals/upcoming
- /api/calendar/sankranti/{year}
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client for API."""
    from app.main import app
    return TestClient(app)


# =============================================================================
# ROOT AND HEALTH ENDPOINTS
# =============================================================================

class TestRootEndpoints:
    """Test basic API endpoints."""
    
    def test_root(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Project Parva"
        assert "version" in data
    
    def test_health(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


# =============================================================================
# CALENDAR CONVERSION ENDPOINTS
# =============================================================================

class TestCalendarConversion:
    """Test calendar conversion endpoints."""
    
    def test_convert_date(self, client):
        """Test Gregorian to BS/NS conversion."""
        response = client.get("/api/calendar/convert?date=2026-02-06")
        assert response.status_code == 200
        data = response.json()
        
        assert data["gregorian"] == "2026-02-06"
        assert "bikram_sambat" in data
        assert data["bikram_sambat"]["year"] == 2082
        assert "tithi" in data
    
    def test_convert_invalid_date(self, client):
        """Test invalid date format returns error."""
        response = client.get("/api/calendar/convert?date=invalid")
        assert response.status_code == 400
    
    def test_today(self, client):
        """Test /today endpoint returns current date info."""
        response = client.get("/api/calendar/today")
        assert response.status_code == 200
        data = response.json()
        
        assert "gregorian" in data
        assert "bikram_sambat" in data
        assert "tithi" in data


# =============================================================================
# PANCHANGA ENDPOINTS
# =============================================================================

class TestPanchangaEndpoints:
    """Test ephemeris-based panchanga endpoints."""
    
    def test_panchanga_single_date(self, client):
        """Test single date panchanga."""
        response = client.get("/api/calendar/panchanga?date=2026-02-06")
        assert response.status_code == 200
        data = response.json()
        
        assert data["date"] == "2026-02-06"
        assert "panchanga" in data
        
        # Check all 5 elements
        panchanga = data["panchanga"]
        assert "tithi" in panchanga
        assert "nakshatra" in panchanga
        assert "yoga" in panchanga
        assert "karana" in panchanga
        assert "vaara" in panchanga
        
        # Verify tithi structure
        assert "number" in panchanga["tithi"]
        assert "name" in panchanga["tithi"]
        assert "paksha" in panchanga["tithi"]
        
        # Verify ephemeris metadata
        assert data["ephemeris"]["mode"] == "swiss_moshier"
        assert data["ephemeris"]["accuracy"] == "arcsecond"
    
    def test_panchanga_feb_6_2026_values(self, client):
        """Test specific panchanga values for Feb 6, 2026."""
        response = client.get("/api/calendar/panchanga?date=2026-02-06")
        data = response.json()
        
        # Feb 6, 2026 should be Friday (Shukravara)
        assert data["panchanga"]["vaara"]["name_english"] == "Friday"
    
    def test_panchanga_range(self, client):
        """Test panchanga range endpoint."""
        response = client.get("/api/calendar/panchanga/range?start=2026-02-01&days=7")
        assert response.status_code == 200
        data = response.json()
        
        assert data["start"] == "2026-02-01"
        assert data["days"] == 7
        assert len(data["panchangas"]) == 7
        
        # Each entry should have key elements
        for p in data["panchangas"]:
            assert "date" in p
            assert "tithi" in p
            assert "nakshatra" in p
    
    def test_panchanga_invalid_date(self, client):
        """Test invalid date returns error."""
        response = client.get("/api/calendar/panchanga?date=not-a-date")
        assert response.status_code == 400


# =============================================================================
# FESTIVAL CALCULATION ENDPOINTS
# =============================================================================

class TestFestivalEndpoints:
    """Test festival calculation endpoints."""
    
    def test_calculate_dashain(self, client):
        """Test Dashain calculation for 2026."""
        response = client.get("/api/calendar/festivals/calculate/dashain?year=2026")
        assert response.status_code == 200
        data = response.json()
        
        assert data["festival_id"] == "dashain"
        assert data["year"] == 2026
        assert "start" in data
        assert "end" in data
        assert data["duration_days"] >= 15  # Dashain is 15 days
    
    def test_calculate_tihar(self, client):
        """Test Tihar calculation for 2026."""
        response = client.get("/api/calendar/festivals/calculate/tihar?year=2026")
        assert response.status_code == 200
        data = response.json()
        
        assert data["festival_id"] == "tihar"
        assert data["duration_days"] >= 5
    
    def test_calculate_solar_festival(self, client):
        """Test solar festival (Maghe Sankranti) calculation."""
        response = client.get("/api/calendar/festivals/calculate/maghe-sankranti?year=2026")
        assert response.status_code == 200
        data = response.json()
        
        # Maghe Sankranti is usually Jan 14-15
        assert "2026-01" in data["start"]
    
    def test_unknown_festival(self, client):
        """Test unknown festival returns 404."""
        response = client.get("/api/calendar/festivals/calculate/fake-festival?year=2026")
        assert response.status_code == 404
    
    def test_upcoming_festivals(self, client):
        """Test upcoming festivals endpoint."""
        response = client.get("/api/calendar/festivals/upcoming?days=365")
        assert response.status_code == 200
        data = response.json()
        
        assert "from_date" in data
        assert "festivals" in data
        assert len(data["festivals"]) > 0
        
        # Each festival should have required fields
        for fest in data["festivals"]:
            assert "festival_id" in fest
            assert "start" in fest
            assert "end" in fest


# =============================================================================
# SANKRANTI ENDPOINTS
# =============================================================================

class TestSankrantiEndpoints:
    """Test sankranti detection endpoints."""
    
    def test_sankrantis_2026(self, client):
        """Test getting all sankrantis for 2026."""
        response = client.get("/api/calendar/sankranti/2026")
        assert response.status_code == 200
        data = response.json()
        
        assert data["year"] == 2026
        assert "sankrantis" in data
        
        # Should have multiple sankrantis
        assert len(data["sankrantis"]) >= 10
        
        # Each entry should have rashi, bs_month, date
        for s in data["sankrantis"]:
            assert "rashi" in s
            assert "bs_month" in s
            assert "date" in s
    
    def test_makara_sankranti_in_list(self, client):
        """Test Makara Sankranti appears correctly."""
        response = client.get("/api/calendar/sankranti/2026")
        data = response.json()
        
        # Find Makara
        makara = next((s for s in data["sankrantis"] if s["bs_month"] == "Magh"), None)
        assert makara is not None
        assert "2026-01-14" in makara["date"]


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

class TestPerformance:
    """Basic performance assertions."""
    
    def test_panchanga_response_time(self, client):
        """Test panchanga endpoint responds quickly."""
        import time
        
        start = time.time()
        response = client.get("/api/calendar/panchanga?date=2026-02-06")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0  # Should respond in under 2 seconds
    
    def test_festival_calculation_time(self, client):
        """Test festival calculation responds quickly."""
        import time
        
        start = time.time()
        response = client.get("/api/calendar/festivals/calculate/dashain?year=2026")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 3.0  # Complex calculation under 3 seconds


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
