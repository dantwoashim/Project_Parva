"""Authority-aware resolve endpoint checks."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_resolve_endpoint_supports_source_aware_authority_mode():
    response = client.get(
        "/v3/api/resolve",
        params={
            "date": "2026-10-10",
            "authority_mode": "source-aware",
            "source_hint": "nepal_gov",
            "notes_hint": "Ghatasthapana, Ashwin Shukla 1",
        },
    )
    assert response.status_code == 200

    body = response.json()
    assert body["date"] == "2026-10-10"
    dashain = next(row for row in body["observances"] if row["festival_id"] == "dashain")
    assert dashain["start_date"] == "2026-10-10"
    assert dashain["authority_mode"] == "source-aware"
    assert body["trace"]["subject"]["authority_mode"] == "source-aware"
    assert body["trace"]["inputs"]["source_hint"] == "nepal_gov"


def test_resolve_endpoint_keeps_canonical_default_mode():
    response = client.get("/v3/api/resolve", params={"date": "2026-10-11"})
    assert response.status_code == 200

    body = response.json()
    dashain = next(row for row in body["observances"] if row["festival_id"] == "dashain")
    assert dashain["start_date"] == "2026-10-11"
    assert dashain["authority_mode"] == "canonical"
