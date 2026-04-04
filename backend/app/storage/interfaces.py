"""Storage abstractions for trace, snapshot, and transparency persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class TraceStore(ABC):
    @abstractmethod
    def create(
        self,
        *,
        trace_type: str,
        subject: dict[str, Any],
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        steps: list[dict[str, Any]],
        provenance: dict[str, Any] | None = None,
        visibility: str | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get(self, trace_id: str, *, include_private: bool = False) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def list_recent(
        self, limit: int = 20, *, include_private: bool = False
    ) -> list[dict[str, Any]]:
        raise NotImplementedError


class SnapshotStore(ABC):
    @abstractmethod
    def create(self, snapshot_id: Optional[str] = None) -> Any:
        raise NotImplementedError

    @abstractmethod
    def load(self, snapshot_id: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def latest_id(self) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def latest(self, *, create_if_missing: bool = False) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    def verify(self, snapshot_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def provenance_payload(
        self,
        *,
        verify_url: Optional[str] = None,
        create_if_missing: bool = True,
    ) -> dict[str, Any]:
        raise NotImplementedError


class TransparencyLogStore(ABC):
    @abstractmethod
    def load_entries(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def append_entry(self, event_type: str, payload: dict[str, Any]) -> Any:
        raise NotImplementedError

    @abstractmethod
    def verify_integrity(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def replay_state(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def record_anchor(
        self,
        tx_ref: str,
        network: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def list_anchors(self, limit: int = 50) -> list[dict[str, Any]]:
        raise NotImplementedError
