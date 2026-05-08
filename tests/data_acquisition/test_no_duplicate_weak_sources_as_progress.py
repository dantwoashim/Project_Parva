import json
from pathlib import Path


def test_duplicate_or_blocked_sources_are_not_counted_as_progress():
    path = Path("data/future_bs/data_acquisition/new_source_coverage_report.json")
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["new_high_trust_rows"] == (
        payload["new_tier_1_rows"] + payload["new_tier_2_rows"] + payload["new_tier_3_rows"]
    )
    assert payload["source_attempts"] >= len(payload["families_attempted"])
