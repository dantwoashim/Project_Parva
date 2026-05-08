import json
from pathlib import Path


def test_wrong_green_count_zero_or_claim_false():
    metrics = json.loads(Path("data/future_bs/accuracy_lab/best_metrics.json").read_text(encoding="utf-8"))
    readiness = json.loads(Path("data/future_bs/accuracy_lab/accuracy_readiness_final.json").read_text(encoding="utf-8"))
    if metrics["wrong_green_count"] > 0:
        assert readiness["claim_ready_99_green_zone"] is False
