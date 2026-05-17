from __future__ import annotations

from pathlib import Path

EMBED_SOURCE = Path("static/parva-embed.js")


def test_embed_does_not_use_inner_html() -> None:
    source = EMBED_SOURCE.read_text(encoding="utf-8")

    assert "innerHTML" not in source


def test_embed_escapes_malicious_title() -> None:
    source = EMBED_SOURCE.read_text(encoding="utf-8")

    assert "title.textContent" in source
    assert "card.title" in source


def test_embed_escapes_malicious_boundary() -> None:
    source = EMBED_SOURCE.read_text(encoding="utf-8")

    assert "body.textContent" in source
    assert "card.boundary" in source


def test_embed_no_script_execution_from_card_data() -> None:
    source = EMBED_SOURCE.read_text(encoding="utf-8")

    assert "createElement('script')" not in source
    assert "eval(" not in source
    assert "Function(" not in source
