from __future__ import annotations

from scripts.release.verify_clean_clone_assumptions import verify_clean_clone_assumptions


def test_clean_clone_assumptions_pass() -> None:
    assert verify_clean_clone_assumptions() == []
