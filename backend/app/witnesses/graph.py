"""Dependency graph for witness and proof-pack lineage."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class WitnessNode:
    witness_id: str
    witness_hash: str
    kind: str

    def as_dict(self) -> dict[str, str]:
        return {
            "witness_id": self.witness_id,
            "witness_hash": self.witness_hash,
            "kind": self.kind,
        }


@dataclass
class WitnessGraph:
    nodes: dict[str, WitnessNode] = field(default_factory=dict)
    edges: dict[str, set[str]] = field(default_factory=dict)

    def add_node(self, node: WitnessNode) -> None:
        self.nodes[node.witness_id] = node
        self.edges.setdefault(node.witness_id, set())

    def add_edge(self, parent_id: str, child_id: str) -> None:
        if parent_id not in self.nodes or child_id not in self.nodes:
            raise ValueError("witness graph edge references unknown node")
        self.edges.setdefault(parent_id, set()).add(child_id)

    def lineage(self, root_id: str) -> list[str]:
        if root_id not in self.nodes:
            raise ValueError("unknown witness root")
        seen: set[str] = set()
        ordered: list[str] = []

        def visit(node_id: str) -> None:
            if node_id in seen:
                return
            seen.add(node_id)
            ordered.append(node_id)
            for child_id in sorted(self.edges.get(node_id, ())):
                visit(child_id)

        visit(root_id)
        return ordered

    def as_dict(self) -> dict[str, object]:
        return {
            "nodes": {key: node.as_dict() for key, node in sorted(self.nodes.items())},
            "edges": {key: sorted(value) for key, value in sorted(self.edges.items())},
        }
