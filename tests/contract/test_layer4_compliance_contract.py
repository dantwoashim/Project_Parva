"""Layer 4 enterprise temporal compliance contract checks."""

from __future__ import annotations

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _meta(body: dict) -> dict:
    meta = body.get("meta")
    assert isinstance(meta, dict)
    assert isinstance(meta.get("source"), dict)
    assert isinstance(meta.get("confidence"), str)
    assert isinstance(meta.get("data_version"), str)
    assert meta.get("claim_boundary") == "enterprise_decision_support_not_legal_authority"
    assert isinstance(meta.get("warnings"), list)
    assert isinstance(meta.get("trace_id"), str)
    return meta


def test_compliance_profiles_are_listed_with_boundaries() -> None:
    response = client.get("/v3/api/compliance/profiles")

    assert response.status_code == 200
    body = response.json()
    profile_ids = {profile["profile_id"] for profile in body["profiles"]}
    assert {
        "nepal_public_general",
        "nepal_government_general",
        "nepal_banking_general",
        "nepal_private_company_default",
        "nepal_school_general",
        "custom_demo_company",
    }.issubset(profile_ids)
    assert "SATURDAY_NON_WORKING" in body["reason_codes"]
    meta = _meta(body)
    assert meta["source"]["id"] == "parva_enterprise_compliance_profiles"
    assert meta["trace_id"] == response.headers["X-Request-ID"]


def test_get_compliance_profile_detail() -> None:
    response = client.get("/v3/api/compliance/profiles/nepal_banking_general")

    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["profile_id"] == "nepal_banking_general"
    assert body["profile"]["holiday_policy"]["include_banking_holidays"] is True
    assert body["profile"]["risk_policy"]["require_official_holiday_source"] is True


def test_evaluate_normal_working_day_for_private_profile() -> None:
    response = client.post(
        "/v3/api/compliance/evaluate-date",
        json={"profile_id": "nepal_private_company_default", "bs_date": "2082-04-02"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["date"] == {"bs": "2082-04-02", "ad": "2025-07-17"}
    assert body["decision"]["is_working_day"] is True
    assert body["decision"]["requires_human_review"] is False
    assert "WEEKDAY" in body["decision"]["reason_codes"]
    assert "NO_MATCHING_PUBLIC_HOLIDAY" in body["decision"]["reason_codes"]
    assert _meta(body)["confidence"] == "official_verified"


def test_evaluate_saturday_weekend_for_private_profile() -> None:
    response = client.post(
        "/v3/api/compliance/evaluate-date",
        json={"profile_id": "nepal_private_company_default", "bs_date": "2082-04-04"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["date"]["ad"] == "2025-07-19"
    assert body["decision"]["is_working_day"] is False
    assert "WEEKEND" in body["decision"]["reason_codes"]
    assert "SATURDAY_NON_WORKING" in body["decision"]["reason_codes"]


def test_evaluate_public_fixed_date_holiday_from_public_corpus() -> None:
    response = client.post(
        "/v3/api/compliance/evaluate-date",
        json={"profile_id": "nepal_private_company_default", "bs_date": "2083-01-01"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["is_working_day"] is False
    assert body["decision"]["holiday"]["holiday_id"] == "bs-new-year"
    assert "PUBLIC_HOLIDAY_MATCH" in body["decision"]["reason_codes"]
    assert "public_fixed_date_holiday_not_official_holiday_notice" in body["meta"]["warnings"]


def test_next_previous_and_add_working_day_helpers_are_bounded_and_source_aware() -> None:
    next_response = client.post(
        "/v3/api/compliance/next-working-day",
        json={"profile_id": "nepal_private_company_default", "bs_date": "2082-04-04"},
    )
    assert next_response.status_code == 200
    assert next_response.json()["date"] == {"bs": "2082-04-05", "ad": "2025-07-20"}
    assert next_response.json()["iterations"] == 1

    previous_response = client.post(
        "/v3/api/compliance/previous-working-day",
        json={"profile_id": "nepal_private_company_default", "bs_date": "2082-04-04"},
    )
    assert previous_response.status_code == 200
    assert previous_response.json()["date"] == {"bs": "2082-04-03", "ad": "2025-07-18"}

    add_response = client.post(
        "/v3/api/compliance/add-working-days",
        json={
            "profile_id": "nepal_private_company_default",
            "bs_date": "2082-04-02",
            "working_days": 2,
        },
    )
    assert add_response.status_code == 200
    assert add_response.json()["date"] == {"bs": "2082-04-05", "ad": "2025-07-20"}
    assert _meta(add_response.json())["trace_id"] == add_response.headers["X-Request-ID"]


def test_month_closing_day_and_fiscal_period() -> None:
    closing = client.post(
        "/v3/api/compliance/month-closing-day",
        json={"profile_id": "nepal_private_company_default", "bs_year": 2082, "bs_month": 4},
    )
    assert closing.status_code == 200
    closing_body = closing.json()
    assert closing_body["last_calendar_day"] == {"bs": "2082-04-32", "ad": "2025-08-16"}
    assert closing_body["last_working_day"] == {"bs": "2082-04-31", "ad": "2025-08-15"}

    fiscal = client.post(
        "/v3/api/compliance/fiscal-period",
        json={"profile_id": "nepal_private_company_default", "bs_date": "2082-04-01"},
    )
    assert fiscal.status_code == 200
    fiscal_body = fiscal.json()
    assert fiscal_body["fiscal_period"]["fiscal_year_label"] == "2082/83"
    assert fiscal_body["fiscal_period"]["fiscal_month"] == 1
    assert fiscal_body["fiscal_period"]["fiscal_quarter"] == 1
    assert "FISCAL_YEAR_BOUNDARY" in fiscal_body["decision"]["reason_codes"]


def test_low_confidence_or_official_required_profile_requires_review() -> None:
    response = client.post(
        "/v3/api/compliance/evaluate-date",
        json={"profile_id": "nepal_banking_general", "bs_date": "2085-04-02"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["requires_human_review"] is True
    assert body["decision"]["is_payroll_safe"] is False
    assert "PROFILE_REQUIRES_OFFICIAL_SOURCE" in body["decision"]["reason_codes"]
    assert "SOURCE_CONFIDENCE_TOO_LOW" in body["decision"]["reason_codes"]
    assert "FUTURE_DATE_REVIEW_REQUIRED" in body["decision"]["reason_codes"]
    assert body["meta"]["confidence"] == "unsupported"


def test_compliance_rejects_unsupported_or_ambiguous_inputs() -> None:
    ambiguous = client.post(
        "/v3/api/compliance/evaluate-date",
        json={
            "profile_id": "nepal_private_company_default",
            "bs_date": "2082-04-02",
            "ad_date": "2025-07-17",
        },
    )
    assert ambiguous.status_code == 400
    assert ambiguous.json()["error"]["code"] == "BAD_REQUEST"

    too_many = client.post(
        "/v3/api/compliance/add-working-days",
        json={
            "profile_id": "nepal_private_company_default",
            "bs_date": "2082-04-02",
            "working_days": 500,
        },
    )
    assert too_many.status_code == 422


def test_compliance_paths_are_present_in_full_openapi() -> None:
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    assert "/v3/api/compliance/profiles" in paths
    assert "/v3/api/compliance/evaluate-date" in paths
    assert "/v3/api/compliance/month-closing-day" in paths
    assert "ComplianceDateRequest" in schema["components"]["schemas"]


def test_public_demo_route_profile_excludes_compliance_preview(monkeypatch) -> None:
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_demo")
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "false")
    monkeypatch.setenv("PARVA_SHOW_PRIVATE_SCHEMA", "false")
    monkeypatch.setenv("PARVA_ENV", "public")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://github.com/dantwoashim/Project_Parva")
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")

    from app.bootstrap.app_factory import create_app

    public_demo_client = TestClient(create_app())
    assert public_demo_client.get("/v3/api/compliance/profiles").status_code == 404
    assert "/v3/api/compliance/profiles" not in public_demo_client.get("/openapi.json").json()["paths"]
