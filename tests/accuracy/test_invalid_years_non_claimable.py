import json
import subprocess
from pathlib import Path


def _best_artifact() -> Path:
    path = Path("data/future_bs/predictions/parva_future_bs_accuracy_best_2084_2200.json")
    if not path.exists():
        subprocess.run(["python", "scripts/future_bs/run_accuracy_loop.py", "--final"], check=True)
    return path


def test_best_future_artifact_has_valid_totals_or_red():
    payload = json.loads(_best_artifact().read_text())
    for year, row in payload["years"].items():
        total = sum(row["months"])
        if total not in {365, 366}:
            assert all(detail["risk_label"] == "RED" for detail in row["month_details"]), year
