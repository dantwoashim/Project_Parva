import json
from pathlib import Path


def test_source_policy_metric_artifacts_exist():
    for name in [
        "source_policy_metrics.json",
        "official_strict_metrics.json",
        "medium_high_training_metrics.json",
        "all_witness_experimental_metrics.json",
    ]:
        path = Path("data/future_bs/accuracy_lab") / name
        assert path.exists(), path
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["publication_status"] == "computed_prediction_not_official"
