"""Feed integration endpoint checks."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_feed_catalog_returns_platform_ready_links():
    response = client.get("/v3/api/feeds/integrations/catalog", params={"years": 2, "lang": "en"})
    assert response.status_code == 200

    body = response.json()
    assert body["platforms"]["apple"]["supports_webcal"] is True
    assert body["platforms"]["google"]["requires_desktop"] is True
    assert body["platforms"]["google"]["cta_label"] == "Copy link and open Google Calendar"
    assert body["presets"]
    first = body["presets"][0]
    assert first["feed_url"].startswith("http")
    assert first["webcal_url"].startswith("webcal://")
    assert "download=1" in first["download_url"]
    assert first["platform_links"]["apple"]["open_url"].startswith("webcal://")
    assert first["platform_links"]["google"]["open_url"].startswith("https://calendar.google.com/")
    assert first["stats"]["event_count"] >= 0
    assert "date_window" in first["stats"]


def test_feed_download_mode_sets_attachment_header():
    response = client.get("/v3/api/feeds/all.ics", params={"download": 1})
    assert response.status_code == 200
    assert response.headers["content-disposition"].startswith("attachment;")
    assert "VCALENDAR" in response.text


def test_custom_feed_plan_returns_platform_links_and_selection_metadata():
    response = client.get(
        "/v3/api/feeds/integrations/custom-plan",
        params={"festivals": "dashain,tihar", "years": 2, "lang": "en"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["key"] == "custom"
    assert body["selection_count"] == 2
    assert body["festival_ids"] == ["dashain", "tihar"]
    assert body["platform_links"]["apple"]["open_url"].startswith("webcal://")
    assert body["platform_links"]["google"]["copy_url"].startswith("http")
    assert body["stats"]["event_count"] >= 0
