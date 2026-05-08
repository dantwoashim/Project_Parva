import json
from pathlib import Path


def test_wide_prediction_set_not_green_in_best_artifact():
    payload = json.loads(Path("data/future_bs/predictions/parva_future_bs_accuracy_best_2084_2200.json").read_text())
    for year, year_payload in payload["years"].items():
        for detail in year_payload["month_details"]:
            if len(detail.get("prediction_set_95") or []) > 1:
                assert detail["risk_label"] != "GREEN", f"{year}-{detail['month']}"
