"""Build deterministic year-level static bundles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.calendar.bikram_sambat import bs_to_gregorian, days_in_bs_month
from app.forge.manifest import build_manifest


def build_year_bundle(bs_year: int, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    months = []
    for month in range(1, 13):
        days = days_in_bs_month(bs_year, month)
        months.append(
            {
                "month": month,
                "days": days,
                "start_ad": bs_to_gregorian(bs_year, month, 1).isoformat(),
                "end_ad": bs_to_gregorian(bs_year, month, days).isoformat(),
            }
        )
    payload = {
        "kind": "parva_static_year_bundle",
        "bs_year": bs_year,
        "months": months,
        "claim_boundary": "static_bundle_not_authority",
    }
    (output_dir / f"bs-{bs_year}.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = build_manifest(output_dir)
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
