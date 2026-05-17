from __future__ import annotations

from pathlib import Path


def test_embed_example_and_kernel_files_exist() -> None:
    assert Path("examples/embed/basic.html").read_text(encoding="utf-8")
    assert "ParvaEmbed" in Path("static/parva-embed.js").read_text(encoding="utf-8")
    assert Path("packages/parva-local-kernel/src/verify.ts").exists()


def test_local_kernel_membrane_verifier_is_not_field_presence_only() -> None:
    source = Path("packages/parva-local-kernel/src/membranes.ts").read_text(encoding="utf-8")

    assert "Boolean(membrane.identity_hash && membrane.witness_hash)" not in source
    assert "proof_pack_result_hash_mismatch" in source
    assert "source_snapshot_hash_mismatch" in source
    assert "for (const field of Object.keys" in source
