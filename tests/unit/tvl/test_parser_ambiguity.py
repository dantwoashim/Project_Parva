from __future__ import annotations

from app.tir.lower import lower_to_canonical
from app.tvl.parser import parse_temporal_query


def test_dashain_query_maps_across_surfaces() -> None:
    queries = ["दशैं २०८२ कहिले", "dashain 2082 kahile", "when is dashain 2082"]
    canonical = [lower_to_canonical(parse_temporal_query(query)) for query in queries]
    assert canonical[0] == canonical[1] == canonical[2]
    assert parse_temporal_query(queries[0]).language_surface == "ne-Deva"


def test_ambiguous_input_returns_structured_ambiguity() -> None:
    ir = parse_temporal_query("next good date")
    assert ir.intent == "unknown"
    assert ir.ambiguities
    assert ir.interpretation_confidence == 0.0
