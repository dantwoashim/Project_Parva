from app.core.calculation_trace import demo_bs_to_ad_trace


def test_demo_trace_matches_public_claim_boundary():
    payload = demo_bs_to_ad_trace().model_dump()

    assert payload["trace_id"] == "tr_demo_bs_to_ad_2083_01_01"
    assert payload["operation"] == "bs_to_ad"
    assert payload["release_id"] == "parva-bs-public-demo"
    assert payload["source_policy"] == "public_demo"
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert [step["name"] for step in payload["steps"]] == [
        "validate_bs_date",
        "resolve_month_start",
        "add_day_offset",
        "project_to_gregorian",
    ]
