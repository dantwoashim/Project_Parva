import json
from pathlib import Path


def test_best_future_artifact_has_valid_totals_or_red():
    payload = json.loads(Path("data/future_bs/predictions/parva_future_bs_accuracy_best_2084_2200.json").read_text())
    for year, row in payload["years"].items():
        total = sum(row["months"])
        if total not in {365, 366}:
            assert all(detail["risk_label"] == "RED" for detail in row["month_details"]), year
