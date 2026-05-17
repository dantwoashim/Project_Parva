from __future__ import annotations

from app.tvl.tokenizer import tokenize


def test_tokenizer_normalizes_devanagari_digits_and_aliases() -> None:
    assert tokenize("दशैं २०८२ कहिले") == ["dashain", "2082", "when"]
