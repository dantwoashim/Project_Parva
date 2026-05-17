"""Structured policy traces for explainable candidate selection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PolicyTrace:
    policy_id: str
    steps: list[dict[str, Any]] = field(default_factory=list)

    def add(self, event: str, **detail: Any) -> None:
        self.steps.append({"event": event, "detail": detail})

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "policy_trace",
            "policy_id": self.policy_id,
            "steps": list(self.steps),
        }
