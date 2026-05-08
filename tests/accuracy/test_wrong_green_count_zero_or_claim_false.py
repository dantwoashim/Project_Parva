import json
import subprocess
from pathlib import Path


def test_wrong_green_count_zero_or_claim_false():
    root = Path("data/future_bs/accuracy_lab")
    if not (root / "best_metrics.json").exists() or not (root / "accuracy_readiness_final.json").exists():
        subprocess.run(["python", "scripts/future_bs/run_accuracy_loop.py", "--final"], check=True)
    metrics = json.loads((root / "best_metrics.json").read_text(encoding="utf-8"))
    readiness = json.loads((root / "accuracy_readiness_final.json").read_text(encoding="utf-8"))
    if metrics["wrong_green_count"] > 0:
        assert readiness["claim_ready_99_green_zone"] is False
