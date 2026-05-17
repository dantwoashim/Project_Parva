"""Versioned canonicalization migration checks."""

from __future__ import annotations

from dataclasses import dataclass

from app.canonicalization.normalize import canonical_json


@dataclass(frozen=True)
class MigrationDrift:
    changed: bool
    before: dict
    after: dict
    reason: str

    def as_dict(self) -> dict:
        return {
            "changed": self.changed,
            "before": self.before,
            "after": self.after,
            "reason": self.reason,
        }


def detect_migration_drift(before: dict, after: dict) -> MigrationDrift:
    changed = canonical_json(before) != canonical_json(after)
    return MigrationDrift(
        changed=changed,
        before=before,
        after=after,
        reason="canonical_meaning_changed" if changed else "canonical_meaning_preserved",
    )
