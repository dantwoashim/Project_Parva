from __future__ import annotations

from pathlib import Path


def test_embed_example_and_kernel_files_exist() -> None:
    assert Path("examples/embed/basic.html").read_text(encoding="utf-8")
    assert "ParvaEmbed" in Path("static/parva-embed.js").read_text(encoding="utf-8")
    assert Path("packages/parva-local-kernel/src/verify.ts").exists()
