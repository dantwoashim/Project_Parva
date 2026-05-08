import json
import subprocess
from pathlib import Path


def _best_artifact() -> Path:
    path = Path("data/future_bs/predictions/parva_future_bs_accuracy_best_2084_2200.json")
    if not path.exists():
        subprocess.run(["python", "scripts/future_bs/run_accuracy_loop.py", "--final"], check=True)
    return path


def test_wide_prediction_set_not_green_in_best_artifact():
    payload = json.loads(_best_artifact().read_text())
    for year, year_payload in payload["years"].items():
        for detail in year_payload["month_details"]:
            if len(detail.get("prediction_set_95") or []) > 1:
                assert detail["risk_label"] != "GREEN", f"{year}-{detail['month']}"
