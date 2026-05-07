"""Regression coverage for existing non-future-BS Parva surfaces."""

import sys
from pathlib import Path

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[2]


def test_existing_conversion_routes_still_work():
    ad_to_bs = client.get("/api/calendar/convert?date=2026-02-15")
    assert ad_to_bs.status_code == 200
    assert ad_to_bs.json()["gregorian"] == "2026-02-15"

    bs_to_ad = client.post("/api/calendar/bs-to-gregorian", json={"year": 2082, "month": 11, "day": 3})
    assert bs_to_ad.status_code == 200
    assert "gregorian" in bs_to_ad.json()


def test_existing_enterprise_fiscal_and_month_routes_still_work():
    fiscal = client.get("/api/enterprise/fiscal-year/2082")
    assert fiscal.status_code == 200
    assert fiscal.json()["fiscal_year"].startswith("2082")

    months = client.get("/api/enterprise/bs-months/2082")
    assert months.status_code == 200
    assert len(months.json()["months"]) == 12


def test_existing_observance_and_panchanga_routes_still_work():
    observances = client.get("/api/observances?date=2026-02-15")
    assert observances.status_code == 200
    assert "observances" in observances.json()

    panchanga = client.get("/api/calendar/panchanga?date=2026-02-15")
    assert panchanga.status_code == 200
    assert "tithi" in panchanga.json()["panchanga"]


def test_existing_sdk_imports_still_work():
    sys.path.insert(0, str(ROOT / "sdk" / "python"))
    import parva_sdk

    assert hasattr(parva_sdk, "__all__")
