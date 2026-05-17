from __future__ import annotations

from app.witnesses.graph import WitnessGraph, WitnessNode
from app.witnesses.registry import WitnessRegistry
from app.witnesses.schema import Witness


def test_witness_registry_round_trip() -> None:
    witness = Witness("op", "sha256:in", "sha256:out", "verifier", "1", {}, ("src",))
    registry = WitnessRegistry()
    witness_id = registry.add(witness)
    assert registry.get(witness_id).witness_id == witness_id


def test_witness_graph_records_lineage() -> None:
    graph = WitnessGraph()
    graph.add_node(WitnessNode("root", "sha256:root", "membrane"))
    graph.add_node(WitnessNode("child", "sha256:child", "source_docket"))
    graph.add_edge("root", "child")
    assert graph.lineage("root") == ["root", "child"]
    assert graph.as_dict()["edges"]["root"] == ["child"]
