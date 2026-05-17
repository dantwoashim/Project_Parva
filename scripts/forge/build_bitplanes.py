#!/usr/bin/env python3
"""Build sample causal bitplanes for the static index."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.forge.bitplanes import build_working_day_plane  # noqa: E402
from app.sources.hashing import sha256_file  # noqa: E402


def main() -> int:
    plane = build_working_day_plane(31, {4, 11, 18, 25})
    output = PROJECT_ROOT / "static" / "parva-index" / "bitplane-working-day-2082-01.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plane.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    plane_file_hash = f"sha256:{sha256_file(output)}"
    attestation_output = output.with_suffix(".attestation.json")
    attestation_output.write_text(
        json.dumps(
            {
                "kind": "bitplane_attestation_card",
                "plane_hash": plane.hash,
                "manifest_entry_path": output.name,
                "manifest_entry_hash": plane_file_hash,
                "manifest_binding": "attestation_file_and_plane_file_are_included_in_static_manifest",
                "verifier": "scripts/forge/verify_manifest.py",
                "claim_boundary": "bitplane_attestation_not_official_authority",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {output.relative_to(PROJECT_ROOT)} {plane.hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
