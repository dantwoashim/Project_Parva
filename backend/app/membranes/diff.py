"""Diff membranes."""

from __future__ import annotations


def diff_membrane(before: dict, after: dict, affected_identities: list[str]) -> dict:
    changed = {
        key: {"before": before.get(key), "after": after.get(key)}
        for key in sorted(set(before) | set(after))
        if before.get(key) != after.get(key)
    }
    return {
        "kind": "parva_membrane",
        "membrane_kind": "diff",
        "changed_fields": changed,
        "affected_identities": affected_identities,
    }
