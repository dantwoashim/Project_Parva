from __future__ import annotations

import json
from pathlib import Path

import pytest
from app.sources.archive import write_raw_source
from app.sources.docket import SourceDocket


def test_source_docket_fixture_loads() -> None:
    payload = json.loads(Path("data/sources/dockets/sample_2082_calendar_notice.json").read_text(encoding="utf-8-sig"))
    docket = SourceDocket.from_dict(payload)
    assert docket.source_id == "parva:src:v1:sample-2082-calendar-notice"
    assert docket.authority_class == "static_reference"


def test_raw_source_archive_does_not_overwrite(tmp_path) -> None:
    target = tmp_path / "raw.txt"
    write_raw_source(target, b"first")
    with pytest.raises(FileExistsError):
        write_raw_source(target, b"second")
