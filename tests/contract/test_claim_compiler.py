from __future__ import annotations

from scripts.claims.compile_public_claims import main


def test_public_claim_compiler_passes_current_tree() -> None:
    assert main() == 0
