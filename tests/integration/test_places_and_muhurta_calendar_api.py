from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_place_search_returns_normalized_candidates(monkeypatch):
    import app.api.place_routes as place_routes

    monkeypatch.setattr(
        place_routes,
        "search_places",
        lambda *, query, limit: {
            "query": query,
            "items": [
                {
                    "label": "Kathmandu, Bagmati Province, Nepal",
                    "latitude": 27.7172,
                    "longitude": 85.324,
                    "timezone": "Asia/Kathmandu",
                    "source": "openstreetmap_nominatim",
                    "timezone_source": "coordinate_lookup",
                }
            ],
            "total": 1,
            "source": "openstreetmap_nominatim",
            "attribution": "Search results use OpenStreetMap Nominatim data.",
        },
    )

    response = client.get("/v3/api/places/search", params={"q": "kathmandu", "limit": 4})

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "kathmandu"
    assert body["total"] == 1
    assert body["items"][0] == {
        "label": "Kathmandu, Bagmati Province, Nepal",
        "latitude": 27.7172,
        "longitude": 85.324,
        "timezone": "Asia/Kathmandu",
        "source": "openstreetmap_nominatim",
        "timezone_source": "coordinate_lookup",
    }
    assert body["method_profile"] == "place_search_v1"
    assert body["advisory_scope"] == "form_input"
    assert body["source_mode"] == "remote_geocoder"
    assert "privacy_notice" in body
    assert "service_notice" in body
    assert body["support_tier"] == "computed"
    assert body["engine_path"] == "nominatim_place_search"
    assert body["fallback_used"] is False
    assert body["calibration_status"] == "unavailable"


def test_place_search_surfaces_upstream_unavailability(monkeypatch):
    import app.api.place_routes as place_routes

    def _fail(*, query, limit):
        raise RuntimeError("Place search upstream is unavailable.")

    monkeypatch.setattr(place_routes, "search_places", _fail)

    response = client.get("/v3/api/places/search", params={"q": "pokhara"})

    assert response.status_code == 502
    assert response.json()["detail"] == "Place search upstream is unavailable."


def test_place_search_prefers_offline_gazetteer_for_known_nepal_places():
    response = client.get("/v3/api/places/search", params={"q": "kathmandu", "limit": 4})

    assert response.status_code == 200
    body = response.json()
    assert body["source_mode"] == "offline_gazetteer"
    assert body["source"] == "offline_nepal_gazetteer"
    assert body["engine_path"] == "offline_nepal_gazetteer_search"
    assert body["method"] == "offline_nepal_gazetteer_search"
    assert body["items"][0]["label"].startswith("Kathmandu")
    assert body["items"][0]["timezone"] == "Asia/Kathmandu"
    assert "resolved locally" in body["privacy_notice"].lower()


def test_place_search_can_be_disabled_for_privacy_sensitive_deployments(monkeypatch):
    import app.services.place_search_service as place_search_service

    monkeypatch.setattr(place_search_service, "_ALLOW_REMOTE", False)

    response = client.get("/v3/api/places/search", params={"q": "zzzz-not-a-nepal-place"})

    assert response.status_code == 502
    assert "Remote place search is disabled" in response.json()["detail"]


def test_muhurta_calendar_returns_ranked_dates(monkeypatch):
    import app.api.muhurta_calendar_routes as muhurta_calendar_routes

    monkeypatch.setattr(
        muhurta_calendar_routes,
        "build_muhurta_calendar",
        lambda **kwargs: {
            "from": "2026-03-21",
            "to": "2026-04-30",
            "location": {
                "latitude": kwargs["latitude"],
                "longitude": kwargs["longitude"],
                "timezone": kwargs["timezone_name"],
            },
            "type": kwargs["ceremony_type"],
            "assumption_set_id": kwargs["assumption_set"],
            "days": [
                {
                    "date": "2026-03-21",
                    "type": kwargs["ceremony_type"],
                    "has_viable_window": True,
                    "minimum_score": 25,
                    "top_score": 88,
                    "tone": "strong",
                    "window_count": 4,
                    "best_window": {
                        "index": 6,
                        "name": "Abhijit Muhurta",
                        "start": "2026-03-21T10:30:00+05:45",
                        "end": "2026-03-21T12:15:00+05:45",
                        "score": 88,
                        "quality": "auspicious",
                        "reason_codes": ["quality:auspicious"],
                        "rank_explanation": "Strong midday support.",
                    },
                    "caution": {
                        "rahu_kalam": {
                            "start": "2026-03-21T09:00:00+05:45",
                            "end": "2026-03-21T10:30:00+05:45",
                        },
                        "yamaganda": None,
                        "gulika": None,
                    },
                }
            ],
            "total": 1,
        },
    )

    response = client.get(
        "/v3/api/muhurta/calendar",
        params={
            "from": "2026-03-21",
            "to": "2026-04-30",
            "type": "vivah",
            "lat": "27.7172",
            "lon": "85.3240",
            "tz": "Asia/Kathmandu",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["from"] == "2026-03-21"
    assert body["to"] == "2026-04-30"
    assert body["type"] == "vivah"
    assert body["location"] == {
        "latitude": 27.7172,
        "longitude": 85.324,
        "timezone": "Asia/Kathmandu",
    }
    assert body["days"][0]["best_window"]["name"] == "Abhijit Muhurta"
    assert body["days"][0]["tone"] == "strong"
    assert body["warnings"] == []
    assert body["method_profile"] == "muhurta_calendar_v1"
    assert body["engine_path"] == "muhurta_calendar_ranking"
    assert body["fallback_used"] is False
    assert body["calibration_status"] == "unavailable"
    assert body["quality_band"] == "validated"


def test_muhurta_calendar_invalid_range_returns_400():
    response = client.get(
        "/v3/api/muhurta/calendar",
        params={
            "from": "2026-04-30",
            "to": "2026-03-21",
            "type": "general",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "'from' date must be <= 'to' date"
