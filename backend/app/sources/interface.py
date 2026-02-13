"""Source interfaces for rules/ground-truth loading."""

from __future__ import annotations

from typing import Protocol, Any


class SourceInterface(Protocol):
    """Data-source contract for loading canonical datasets."""

    def load_ground_truth(self) -> dict[str, Any]:
        """Load ground truth festival dates."""

    def load_festival_rules(self) -> dict[str, Any]:
        """Load computation rules."""

    def get_source_priority(self) -> list[str]:
        """Return ordered list of source precedence."""
