#!/usr/bin/env python3
"""Create a reviewed scaffold for a MoHA holiday release ingestion."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _source_payload(source: str) -> dict[str, object]:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        return {
            "source_kind": "url",
            "source_url": source,
            "source_sha256": None,
            "source_hash_status": "deferred_until_source_file_is_retained",
        }

    path = Path(source)
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    if not path.exists():
        raise SystemExit(f"source file not found: {path}")
    return {
        "source_kind": "local_file",
        "source_filename": path.name,
        "source_sha256": _sha256_file(path),
        "source_hash_status": "computed",
    }


def build_scaffold(source: str, *, year: int) -> dict[str, object]:
    return {
        "workflow": "moha_holiday_release_ingestion",
        "workflow_status": "scaffold_requires_human_structuring",
        "bs_year": year,
        "source_authority": "MoHA",
        "source_tier": "official",
        "claim_boundary": "official_source_interpretation_not_legal_authority",
        "publication_status": "source_metadata_recorded_not_machine_release",
        "generated_at": _now_utc(),
        **_source_payload(source),
        "required_next_steps": [
            "retain or link the human-readable source notice",
            "extract holiday rows into a machine-readable draft release",
            "validate the release schema",
            "generate evidence packets for changed holiday claims",
            "update the public release manifest hashes",
            "run python scripts/parva_trust_verify.py",
            "include only public-safe release artifacts in the offline bundle",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Local source file path or public URL.")
    parser.add_argument("--year", type=int, required=True, help="BS year for the MoHA notice.")
    parser.add_argument("--output", required=True, help="Output directory or JSON path.")
    args = parser.parse_args()

    output = Path(args.output)
    if not output.is_absolute():
        output = PROJECT_ROOT / output
    if output.suffix.lower() != ".json":
        output = output / f"moha_holiday_release_{args.year}.source_metadata.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = build_scaffold(args.source, year=args.year)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(output), "workflow_status": payload["workflow_status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

