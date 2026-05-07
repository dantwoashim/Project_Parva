from app.future_bs.backtest import rolling_validation


def test_no_wrong_green_on_selected_official_time_travel():
    payload = rolling_validation(2000, 2078, 2083, source_policy="official_only", model="parva_solar_civil_v1")
    wrong_green = 0
    for run in payload["runs"]:
        for mismatch in run.get("mismatch_details", []):
            if mismatch.get("risk_label") == "GREEN":
                wrong_green += 1
    assert wrong_green == 0
    assert payload["green_zone_accuracy"] >= 99.0
    assert payload["green_zone_coverage"] >= 85.0
