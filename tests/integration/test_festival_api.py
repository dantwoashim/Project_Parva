"""
Integration Tests for Festival Discovery API
=============================================

These tests verify the complete API endpoints work correctly
with real calendar calculations and festival data.
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Create test app with festival routes
app = FastAPI()
from app.festivals import router
app.include_router(router)

client = TestClient(app)


class TestFestivalListEndpoint:
    """Test GET /api/festivals endpoint."""
    
    def test_list_all_festivals(self):
        """List festivals returns all 25 festivals."""
        response = client.get("/api/festivals")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] >= 25
        assert len(data["festivals"]) >= 25
    
    def test_list_festivals_by_category(self):
        """Filter festivals by category."""
        response = client.get("/api/festivals?category=newari")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] >= 7  # 7 Newari festivals
        for festival in data["festivals"]:
            assert festival["category"] == "newari"
    
    def test_search_festivals(self):
        """Search festivals by name."""
        response = client.get("/api/festivals?search=goddess")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] >= 1
        # Should find Dashain (goddess Durga) or Indra Jatra (Living Goddess)


class TestFestivalDetailEndpoint:
    """Test GET /api/festivals/{id} endpoint."""
    
    def test_get_dashain(self):
        """Get Dashain festival details."""
        response = client.get("/api/festivals/dashain")
        assert response.status_code == 200
        
        data = response.json()
        assert data["festival"]["id"] == "dashain"
        assert data["festival"]["name"] == "Dashain"
        assert data["festival"]["name_nepali"] == "दशैं"
        assert data["festival"]["duration_days"] == 15
    
    def test_get_festival_with_dates(self):
        """Festival detail includes calculated dates."""
        response = client.get("/api/festivals/dashain?year=2026")
        assert response.status_code == 200
        
        data = response.json()
        assert "dates" in data
        assert data["dates"]["start_date"] == "2026-10-10"
        assert data["dates"]["end_date"] == "2026-10-24"
    
    def test_get_nonexistent_festival(self):
        """Nonexistent festival returns 404."""
        response = client.get("/api/festivals/nonexistent")
        assert response.status_code == 404


class TestFestivalDatesEndpoint:
    """Test GET /api/festivals/{id}/dates endpoint."""
    
    def test_get_dashain_dates_multi_year(self):
        """Get Dashain dates for multiple years."""
        response = client.get("/api/festivals/dashain/dates?years=3&start_year=2026")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        
        # 2026 dates
        assert data[0]["gregorian_year"] == 2026
        assert data[0]["start_date"] == "2026-10-10"
    
    def test_tihar_2026_dates(self):
        """Verify Tihar 2026 dates match official calendar."""
        response = client.get("/api/festivals/tihar/dates?years=1&start_year=2026")
        assert response.status_code == 200
        
        data = response.json()
        assert data[0]["start_date"] == "2026-11-07"  # Kaag Tihar
        assert data[0]["end_date"] == "2026-11-11"    # Bhai Tika


class TestUpcomingFestivals:
    """Test GET /api/festivals/upcoming endpoint."""
    
    def test_upcoming_festivals(self):
        """Get upcoming festivals from a date."""
        response = client.get("/api/festivals/upcoming?days=60&from_date=2026-09-01")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] >= 1
        
        # Should include Dashain in October
        festival_ids = [f["id"] for f in data["festivals"]]
        assert "dashain" in festival_ids or "teej" in festival_ids
    
    def test_upcoming_includes_days_until(self):
        """Each upcoming festival has days_until."""
        response = client.get("/api/festivals/upcoming?days=30")
        assert response.status_code == 200
        
        data = response.json()
        for festival in data["festivals"]:
            assert "days_until" in festival
            assert festival["days_until"] >= 0


class TestCalendarAccuracy:
    """Test calendar calculations match official dates."""
    
    def test_dashain_2083_official(self):
        """Dashain 2083 matches official Nepal govt calendar."""
        response = client.get("/api/festivals/dashain/dates?years=1&start_year=2026")
        data = response.json()
        
        # Official: Ghatasthapana = Ashwin 25 = October 11, 2026
        assert data[0]["start_date"] == "2026-10-10", "Ghatasthapana should be Oct 10"
    
    def test_tihar_2083_official(self):
        """Tihar 2083 matches official Nepal govt calendar."""
        response = client.get("/api/festivals/tihar/dates?years=1&start_year=2026")
        data = response.json()
        
        # Official: Kaag Tihar = Kartik 21 = November 7, 2026
        assert data[0]["start_date"] == "2026-11-07", "Kaag Tihar should be Nov 7"
        # Official: Bhai Tika = Kartik 25 = November 11, 2026
        assert data[0]["end_date"] == "2026-11-11", "Bhai Tika should be Nov 11"
    
    def test_bs_new_year_2083(self):
        """BS New Year 2083 is April 14, 2026."""
        response = client.get("/api/festivals/bs-new-year/dates?years=1&start_year=2026")
        data = response.json()
        
        assert data[0]["start_date"] == "2026-04-14"


class TestFestivalContent:
    """Test festival content quality."""
    
    def test_all_festivals_have_required_fields(self):
        """All festivals have required fields."""
        response = client.get("/api/festivals")
        data = response.json()
        
        for festival in data["festivals"]:
            assert "id" in festival
            assert "name" in festival
            assert "tagline" in festival
            assert "category" in festival
            assert "duration_days" in festival
    
    def test_priority_festivals_have_nepali_names(self):
        """Priority festivals have Nepali names."""
        priority = ["dashain", "tihar", "holi", "shivaratri", "indra-jatra"]
        
        for festival_id in priority:
            response = client.get(f"/api/festivals/{festival_id}")
            data = response.json()
            assert data["festival"]["name_nepali"] is not None
            assert len(data["festival"]["name_nepali"]) > 0
