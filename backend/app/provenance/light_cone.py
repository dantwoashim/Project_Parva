"""Provenance light-cone and blast-radius helper."""

from __future__ import annotations


def blast_radius(source_id: str, dependencies: dict[str, list[str]]) -> list[str]:
    return sorted(identity for identity, sources in dependencies.items() if source_id in sources)
