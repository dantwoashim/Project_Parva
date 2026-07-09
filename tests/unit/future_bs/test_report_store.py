from app.research.future_bs.report_store import (
    list_reports,
    load_report,
    missing_report_payload,
    report_path,
)


def test_report_store_known_paths_and_missing_payload():
    path = report_path("claim_readiness_v_final")
    assert path.as_posix().endswith("data/future_bs/reports/claim_readiness_v_final.json")
    payload = missing_report_payload("claim_readiness_v_final")
    assert payload["error"] == "report_not_generated"
    assert payload["publication_status"] == "computed_prediction_not_official"


def test_report_store_lists_known_reports():
    payload = list_reports()
    assert "claim_readiness_v_final" in payload["reports"]
    assert payload["publication_status"] == "computed_prediction_not_official"


def test_report_store_load_missing_unknown_shape():
    payload = load_report("claim_readiness_v_final")
    assert payload.get("publication_status") == "computed_prediction_not_official"
