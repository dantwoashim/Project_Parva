from __future__ import annotations

from pathlib import Path


def test_embed_example_and_kernel_files_exist() -> None:
    assert Path("examples/embed/basic.html").read_text(encoding="utf-8")
    assert "ParvaEmbed" in Path("static/parva-embed.js").read_text(encoding="utf-8")
    assert Path("packages/parva-local-kernel/src/verify.ts").exists()
    assert Path("packages/parva-local-kernel/package.json").exists()
    assert Path("packages/parva-local-kernel/tsconfig.json").exists()


def test_local_kernel_membrane_verifier_is_not_field_presence_only() -> None:
    source = Path("packages/parva-local-kernel/src/membranes.ts").read_text(encoding="utf-8")

    assert "Boolean(membrane.identity_hash && membrane.witness_hash)" not in source
    assert "proof_pack_result_hash_mismatch" in source
    assert "source_snapshot_hash_mismatch" in source
    assert "for (const field of Object.keys" in source
    assert "replayMembrane" in source
    assert "fixture_not_found" in source


def test_shared_proof_fixtures_exist_for_local_kernel_replay() -> None:
    civil = sorted(Path("tests/fixtures/proof/civil").glob("*.json"))
    panchanga = sorted(Path("tests/fixtures/proof/panchanga").glob("*.json"))

    assert len(civil) >= 12
    assert panchanga
