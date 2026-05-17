from __future__ import annotations

from scripts.release.run_ceiling_climax_demos import run_demos


def test_ceiling_climax_demos_cover_every_remaining_phase() -> None:
    payload = run_demos()
    assert sorted(payload) == [f"phase_{index:02d}" for index in range(1, 16)]
    assert payload["phase_05"]["verify"][0] is True
    assert payload["phase_15"]["witness"]["status"] == "pending_untrusted"
