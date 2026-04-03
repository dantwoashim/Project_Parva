"""Festival trust and provenance helpers."""

from __future__ import annotations

from typing import Optional

from ..provenance import get_latest_snapshot_id, get_provenance_payload
from .models import ProvenanceMeta


def build_provenance(
    festival_id: Optional[str] = None,
    year: Optional[int] = None,
) -> ProvenanceMeta:
    snapshot_id = get_latest_snapshot_id()
    verify_url = "/v3/api/provenance/root"
    if festival_id and year and snapshot_id:
        verify_url = (
            f"/v3/api/provenance/proof?festival={festival_id}&year={year}&snapshot={snapshot_id}"
        )
    return ProvenanceMeta(**get_provenance_payload(verify_url=verify_url, create_if_missing=True))


__all__ = ["build_provenance"]
