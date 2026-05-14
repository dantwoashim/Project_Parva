from __future__ import annotations

import pytest
from app.services import rulelang_service

from .test_no_eval_exec import _base_rule


def test_rulelang_rejects_oversized_input_payload(monkeypatch):
    monkeypatch.setattr(rulelang_service, "MAX_INPUT_BYTES", 64)
    rule = _base_rule({"return": {"ok": True}})

    with pytest.raises(rulelang_service.RuleLangError, match="size limit"):
        rulelang_service.execute_rule(
            rule,
            {"date": "2080-01-01", "extra": "x" * 256},
        )
