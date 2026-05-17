from __future__ import annotations

from scripts.release.check_ceiling_depth_semantics import _failures


def test_ceiling_depth_semantics_passes() -> None:
    assert _failures() == []
