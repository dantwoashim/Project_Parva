"""Festival trust and provenance helpers."""

from __future__ import annotations

from typing import Optional

from ..services.trust_surface_service import build_surface_provenance
from .models import ProvenanceMeta


def build_provenance(
    festival_id: Optional[str] = None,
    year: Optional[int] = None,
) -> ProvenanceMeta:
    return ProvenanceMeta(
        **build_surface_provenance(
            festival_id=festival_id,
            year=year,
            create_if_missing=True,
        )
    )


__all__ = ["build_provenance"]
