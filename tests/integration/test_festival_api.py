"""
Integration Tests for Festival Discovery API
=============================================

These tests verify the complete API endpoints work correctly
with real calendar calculations and festival data.
"""

from app.festivals import router
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Create test app with festival routes
app = FastAPI()

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
        assert all("date_status" in festival for festival in data["festivals"])
        assert all("date_status_note" in festival for festival in data["festivals"])

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
        assert data["dates"]["start_date"] == "2026-10-11"
        assert data["dates"]["end_date"] == "2026-10-25"
        assert data["date_availability"]["status"] == "available"
        assert data["date_availability"]["resolved_year"] == 2026
        assert data["completeness"]["overall"] in {"complete", "partial", "minimal"}
        assert data["completeness"]["ritual_sequence"]["status"] in {
            "available",
            "partial",
            "missing",
        }

    def test_get_festival_detail_reports_missing_rule_truthfully(self):
        """Inventory-style festivals should explain why dates are absent."""
        response = client.get("/api/festivals/lhosar?year=2026")
        assert response.status_code == 200

        data = response.json()
        assert data["festival"]["id"] == "lhosar"
        assert data["dates"] is None
        assert data["date_availability"]["status"] == "missing_rule"
        assert "No computed rule is published" in data["date_availability"]["note"]
        assert data["completeness"]["dates"]["status"] == "missing"

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
        assert data[0]["start_date"] == "2026-10-11"

    def test_tihar_2026_dates(self):
        """Verify Tihar 2026 dates match official calendar."""
        response = client.get("/api/festivals/tihar/dates?years=1&start_year=2026")
        assert response.status_code == 200

        data = response.json()
        assert data[0]["start_date"] == "2026-11-08"  # Kaag Tihar
        assert data[0]["end_date"] == "2026-11-12"  # Bhai Tika

    def test_multi_year_lunar_dates_do_not_fall_back_to_prior_gregorian_year(self):
        """Autumn/spring lunar observances should not regress to prior-year dates."""
        for festival_id, start_year in [
            ("dashain", 2026),
            ("teej", 2027),
            ("ghode-jatra", 2027),
        ]:
            response = client.get(
                f"/api/festivals/{festival_id}/dates",
                params={"years": 2, "start_year": start_year},
            )
            assert response.status_code == 200

            data = response.json()
            assert data, f"Expected date rows for {festival_id}"
            for row in data:
                assert row["start_date"][:4] == str(row["gregorian_year"]), (
                    f"{festival_id} returned mismatched year row: {row}"
                )


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
            assert festival["date_status"] == "available"


class TestCalendarAccuracy:
    """Test calendar calculations match official dates."""

    def test_dashain_2083_official(self):
        """Dashain 2083 matches official Nepal govt calendar."""
        response = client.get("/api/festivals/dashain/dates?years=1&start_year=2026")
        data = response.json()

        # Official: Ghatasthapana = Ashwin 25 = October 11, 2026
        assert data[0]["start_date"] == "2026-10-11", "Ghatasthapana should be Oct 11"

    def test_tihar_2083_official(self):
        """Tihar 2083 matches official Nepal govt calendar."""
        response = client.get("/api/festivals/tihar/dates?years=1&start_year=2026")
        data = response.json()

        # Official: Kaag Tihar = Kartik 22 = November 8, 2026
        assert data[0]["start_date"] == "2026-11-08", "Kaag Tihar should be Nov 8"
        # Official: Bhai Tika = Kartik 26 = November 12, 2026
        assert data[0]["end_date"] == "2026-11-12", "Bhai Tika should be Nov 12"

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
