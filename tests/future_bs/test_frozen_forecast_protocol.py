from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.future_bs import freeze_public_v7
from scripts.future_bs.score_frozen_forecast import score


def _truth_file(tmp_path: Path, *, published_at: str) -> Path:
    source = tmp_path / "official-calendar.pdf"
    source.write_bytes(b"synthetic official-calendar test artifact")
    truth = {
        "bs_year": 2084,
        "month_lengths": [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
        "source_type": "official_verified",
        "source_url": "https://example.gov.np/official-calendar-2084.pdf",
        "source_sha256": "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest(),
        "source_artifact_path": source.name,
        "published_at": published_at,
        "retrieved_at": "2027-04-02T00:00:00+05:45",
        "reviewed_by": ["reviewer-a", "reviewer-b"],
    }
    path = tmp_path / "truth.json"
    path.write_text(json.dumps(truth), encoding="utf-8")
    return path


def test_v7_freeze_matches_committed_artifacts() -> None:
    assert freeze_public_v7._check(freeze_public_v7._build_outputs()) == []


def test_frozen_forecast_scores_reviewed_post_freeze_truth(tmp_path: Path) -> None:
    result = score(_truth_file(tmp_path, published_at="2027-04-01T00:00:00+05:45"))

    assert result["freeze_id"] == "parva_future_bs_v7_2026-08-05"
    assert result["metrics"]["exact_month_matches"] == 12
    assert result["metrics"]["month_accuracy"] == 1.0
    assert result["metrics"]["exact_year_match"] is True
    assert result["metrics"]["wrong_high_support_count"] == 0


def test_pre_freeze_truth_cannot_be_called_prospective(tmp_path: Path) -> None:
    truth = _truth_file(tmp_path, published_at="2026-08-05T09:00:00Z")

    with pytest.raises(SystemExit, match="predates the freeze"):
        score(truth)
