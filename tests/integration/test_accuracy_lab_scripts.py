import json
import subprocess
from pathlib import Path


def test_accuracy_loop_final_outputs_exist():
    subprocess.run(["python", "scripts/future_bs/run_accuracy_loop.py", "--final"], check=True)
    root = Path("data/future_bs/accuracy_lab")
    metrics = json.loads((root / "best_metrics.json").read_text(encoding="utf-8"))
    assert metrics["wrong_green_count"] == 0
    assert metrics["invalid_future_year_total_rate"] == 0.0
    assert (root / "accuracy_readiness_final.md").exists()
    assert Path("data/future_bs/predictions/parva_future_bs_accuracy_best_2084_2200.json").exists()
