import json
from pathlib import Path

import pytest


def test_high_trust_source_manifest_exists_and_logs_all_families():
    path = Path("data/future_bs/data_acquisition/high_trust_source_manifest.json")
    if not path.exists():
        pytest.skip("high-trust acquisition manifest is generated and not checked into the public tree")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert set(payload["families_attempted"]) >= {
        "rajpatra",
        "moha",
        "gorkhapatra",
        "archive_org_panchanga",
        "public_notices",
        "independent_newspapers",
    }
