"""Integration tests for the future BS month-length validation engine."""

from __future__ import annotations

import base64
import zipfile
from io import BytesIO

from app.future_bs.models import METHOD_VERSION
from app.main import app
from app.services.future_bs_service import predict_bs_year
from fastapi.testclient import TestClient

client = TestClient(app)


def _single_mismatch_months(bs_year: int, month_index: int = 1) -> list[int]:
    months = list(predict_bs_year(bs_year)["months"])
    months[month_index] = 32 if months[month_index] != 32 else 31
    return months


def test_future_bs_capabilities_is_public_v4_without_experimental_flag():
    response = client.get("/v4/api/future-bs/capabilities")

    assert response.status_code == 200
    body = response.json()
    assert body["surface"] == "future_bs_month_length_validation"
    assert body["status"] == "evaluation_ready"
    assert "external_sheet_comparison" in body["stable"]
    assert "official_future_publication" in body["not_claimed"]
    jpl_adapter = next(
        adapter for adapter in body["model_registry"]["ephemeris_adapters"] if adapter["name"] == "jpl_de440"
    )
    if jpl_adapter["available"]:
        assert response.headers["X-Parva-Ephemeris"] == "jpl-de440-lahiri-sidereal"


def test_predict_2085_uses_computed_future_path_not_unverified_static_truth():
    response = client.get("/v4/api/future-bs/month-lengths/2085")

    assert response.status_code == 200
    body = response.json()
    assert body["bs_year"] == 2085
    assert len(body["months"]) == 12
    assert all(29 <= days <= 32 for days in body["months"])
    assert body["source"]["type"] == "computed_prediction"
    assert body["source"]["supporting_corpus_source"]["type"] == "third_party_reference"
    assert body["source_status"] == "computed_prediction"
    assert body["publication_status"] == "not_official_publication"
    assert body["confidence"].startswith("computed_")
    assert body["month_details"][4]["month_name"] == "Bhadra"


def test_predict_future_year_returns_probabilities_and_risk_flags():
    response = client.get("/v4/api/future-bs/month-lengths/2112")

    assert response.status_code == 200
    body = response.json()
    assert body["bs_year"] == 2112
    assert len(body["months"]) == 12
    assert all(29 <= days <= 32 for days in body["months"])
    assert body["method_version"] == METHOD_VERSION
    assert body["model_family"] == "computational_solar_ingress"
    assert body["computational_model_outputs"]
    assert body["legacy_model_output"]
    assert body["source"]["type"] == "computed_prediction"
    assert body["source_status"] == "computed_prediction"
    assert body["publication_status"] == "not_official_publication"
    assert body["run_id"]
    assert "outside_static_lookup" in body["risk_flags"]
    assert body["month_details"][0]["probability"]


def test_predict_range_returns_requested_years():
    response = client.get("/v4/api/future-bs/month-lengths/range?start=2084&end=2085")

    assert response.status_code == 200
    body = response.json()
    assert body["total_years"] == 2
    assert [row["bs_year"] for row in body["years"]] == [2084, 2085]


def test_compare_external_sheet_reports_mismatch():
    external_months = _single_mismatch_months(2085)
    response = client.post(
        "/v4/api/future-bs/month-lengths/compare",
        json={
            "source_name": "infodevelopers_excel",
            "years": [
                {
                    "bs_year": 2085,
                    "months": external_months,
                }
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["years_compared"] == 1
    assert body["summary"]["mismatches"] == 1
    assert body["mismatches"][0]["month_name"] == "Jestha"
    assert body["mismatches"][0]["their_days"] == external_months[1]
    assert body["mismatches"][0]["parva_days"] == predict_bs_year(2085)["months"][1]


def test_backtest_model_returns_accuracy_metrics():
    response = client.get(
        "/v4/api/future-bs/month-lengths/backtest"
        "?train_start=2040&train_end=2075&test_start=2076&test_end=2083"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["months_tested"] == 96
    assert 0 <= body["accuracy"] <= 100
    assert body["mode"] == "computational_solar_ingress_holdout"
    assert body["method_version"] == METHOD_VERSION


def test_backtest_v2_full_and_residual_routes_work():
    full = client.get("/v4/api/future-bs/backtest?mode=full&test_start=2076&test_end=2076")
    assert full.status_code == 200
    assert full.json()["mode"] == "full_replay"

    residuals = client.get(
        "/v4/api/future-bs/backtest/residuals?train_start=2040&train_end=2075&test_start=2076&test_end=2076"
    )
    assert residuals.status_code == 200
    assert residuals.json()["residual_count"] >= 0


def test_explain_month_returns_model_outputs():
    response = client.get("/v4/api/future-bs/month-lengths/explain?year=2112&month=8")

    assert response.status_code == 200
    body = response.json()
    assert body["bs_year"] == 2112
    assert body["month"] == 8
    assert body["month_name"] == "Mangsir"
    assert body["model_outputs"]
    assert body["computational_model_outputs"]
    assert body["legacy_model_output"]
    assert body["interpretation"]


def test_boundary_risk_route_returns_review_payload():
    response = client.get("/v4/api/future-bs/boundary-risk?year=2112&month=8")

    assert response.status_code == 200
    body = response.json()
    assert body["bs_year"] == 2112
    assert body["month"] == 8
    assert body["boundary_risk"] in {"low", "medium", "high", "critical", "unknown"}
    assert body["method_version"] == METHOD_VERSION


def test_import_csv_and_compare_route_detects_mismatch():
    external_months = _single_mismatch_months(2085)
    csv_body = "bs_year,baishakh,jestha,ashadh,shrawan,bhadra,ashwin,kartik,mangsir,poush,magh,falgun,chaitra\n"
    csv_body += "2085," + ",".join(str(days) for days in external_months) + "\n"
    encoded = base64.b64encode(csv_body.encode("utf-8")).decode("ascii")

    response = client.post(
        "/v4/api/future-bs/month-lengths/import-excel",
        json={"source_name": "infodev_excel", "file_format": "csv", "content_base64": encoded},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["imported_years"] == 1
    assert body["comparison"]["summary"]["mismatches"] == 1


def test_export_csv_contains_prediction_rows():
    response = client.get("/v4/api/future-bs/month-lengths/export.csv?start=2084&end=2085")
    expected_2085_prefix = "2085," + ",".join(str(days) for days in predict_bs_year(2085)["months"][:6])

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "bs_year,baishakh,jestha" in response.text
    assert expected_2085_prefix in response.text


def test_export_alias_routes_are_available():
    csv_response = client.get("/v4/api/future-bs/export.csv?start=2084&end=2084")
    xlsx_response = client.get("/v4/api/future-bs/export.xlsx?start=2084&end=2084")

    assert csv_response.status_code == 200
    assert xlsx_response.status_code == 200


def test_export_xlsx_is_valid_zip_workbook():
    response = client.get("/v4/api/future-bs/month-lengths/export.xlsx?start=2084&end=2085")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    with zipfile.ZipFile(BytesIO(response.content)) as workbook:
        assert "xl/worksheets/sheet1.xml" in workbook.namelist()


def test_loan_impact_simulates_interest_difference_from_external_mismatch():
    response = client.post(
        "/v4/api/future-bs/loan-impact/simulate",
        json={
            "loan_start_bs": "2085-05-01",
            "term_months": 1,
            "principal": 1_000_000,
            "annual_rate": 12,
            "day_count_method": "actual_365",
            "external_years": [
                {
                    "bs_year": 2085,
                    "months": [31, 31, 32, 31, 30, 31, 30, 29, 30, 29, 30, 30],
                }
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["calendar_mismatches_affecting_schedule"] == 1
    assert body["summary"]["risk_level"] == "medium"
    assert body["impacted_periods"][0]["bs_month"] == "2085-05"
    assert body["impacted_periods"][0]["day_difference"] == 1


def test_model_runs_are_listed_and_fetchable():
    response = client.get("/v4/api/future-bs/model-runs")

    assert response.status_code == 200
    runs = response.json()["runs"]
    assert runs
    run_id = runs[0]["run_id"]

    detail = client.get(f"/v4/api/future-bs/model-runs/{run_id}")
    assert detail.status_code == 200
    assert detail.json()["run_id"] == run_id
