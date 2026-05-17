"""Deterministic TVL parser for common public-safe queries."""

from __future__ import annotations

from app.tir.schema import TemporalIR
from app.tvl.tokenizer import tokenize


def _language_surface(text: str) -> str:
    return "ne-Deva" if any("\u0900" <= char <= "\u097F" for char in text) else "mixed-roman"


def parse_temporal_query(text: str) -> TemporalIR:
    tokens = tokenize(text)
    year = next((token for token in tokens if token.isdigit() and len(token) == 4), None)
    if "dashain" in tokens and year:
        return TemporalIR(
            intent="find_festival_date",
            entities=({"type": "festival", "value": "dashain"},),
            constraints=({"type": "year", "value": year},),
            ambiguities=(),
            target="festival_date",
            interpretation_confidence=0.95,
            surface_form=text,
            language_surface=_language_surface(text),
        )
    return TemporalIR(
        intent="unknown",
        entities=(),
        constraints=(),
        ambiguities=({"reason": "unsupported_or_ambiguous", "tokens": tokens},),
        target=None,
        interpretation_confidence=0.0,
        surface_form=text,
        language_surface=_language_surface(text),
    )
