import json
from pathlib import Path

import pytest


def test_merge_high_trust_delta_report_is_truthful():
    path = Path("data/future_bs/data_acquisition/post_acquisition_delta_report.json")
    if not path.exists():
        pytest.skip("high-trust merge delta report is generated and not checked into the public tree")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["rows_after_merge"] >= payload["base_rows_before"]
    assert payload["new_rows_added"] == payload["rows_after_merge"] - payload["base_rows_before"]
