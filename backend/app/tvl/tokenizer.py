"""Tokenizer for TVL v0."""

from __future__ import annotations

import re

from app.canonicalization.normalize import normalize_scalar
from app.tvl.phonetic import ALIASES


def tokenize(text: str) -> list[str]:
    raw = re.findall(r"[\w\u0900-\u097F]+", text.lower())
    return [ALIASES.get(str(normalize_scalar(token)), str(normalize_scalar(token))) for token in raw]
