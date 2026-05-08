import csv
from pathlib import Path

import pytest
from app.future_bs.high_trust_acquisition import HIGH_TRUST_FIELDS


def test_high_trust_witness_outputs_follow_schema():
    paths = [
        Path("data/future_bs/witnesses/new_high_trust_witnesses.csv"),
        Path("data/future_bs/witnesses/rajpatra_witnesses.csv"),
        Path("data/future_bs/witnesses/moha_holiday_witnesses.csv"),
        Path("data/future_bs/witnesses/gorkhapatra_masthead_witnesses.csv"),
        Path("data/future_bs/witnesses/archive_panchanga_witnesses.csv"),
        Path("data/future_bs/witnesses/public_notice_witnesses.csv"),
        Path("data/future_bs/witnesses/independent_newspaper_witnesses.csv"),
    ]
    for path in paths:
        if not path.exists():
            pytest.skip("high-trust witness outputs are generated and not checked into the public tree")
        with path.open(newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            assert set(HIGH_TRUST_FIELDS).issubset(reader.fieldnames or [])
