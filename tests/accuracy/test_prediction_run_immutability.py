"""Model-run immutability checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.future_bs.run_registry import DEFAULT_RUN_ID, get_model_run


def _stable_hash(payload: dict) -> str:
    copy = dict(payload)
    expected = copy.pop("hash", None)
    assert expected
    data = json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(data).hexdigest()


def test_default_model_run_hash_is_stable():
    run = get_model_run(DEFAULT_RUN_ID)

    assert run["run_id"] == DEFAULT_RUN_ID
    assert run["hash"] == _stable_hash(run)


def test_model_run_file_name_matches_run_id():
    path = Path("data/future_bs/model_runs") / f"{DEFAULT_RUN_ID}.json"

    if path.exists():
        assert json.loads(path.read_text(encoding="utf-8"))["run_id"] == DEFAULT_RUN_ID
    else:
        assert get_model_run(DEFAULT_RUN_ID)["run_id"] == DEFAULT_RUN_ID
