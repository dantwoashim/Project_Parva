#!/usr/bin/env python3
"""Generate a public-safe evidence packet from a source record and rows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.evidence.ingestion import ingest_source_record  # noqa: E402
from app.evidence.models import EvidencePacket  # noqa: E402
from app.evidence.normalization import normalize_source_rows  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--rows", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--reviewed", action="store_true")
    args = parser.parse_args()

    source = ingest_source_record(json.loads(Path(args.source).read_text(encoding="utf-8")))
    extracted_rows = json.loads(Path(args.rows).read_text(encoding="utf-8"))
    packet = EvidencePacket(
        source=source,
        extracted_rows=extracted_rows,
        normalized_rows=normalize_source_rows(extracted_rows),
        review_status="reviewed" if args.reviewed else "unreviewed",
        reviewer_required=not args.reviewed,
        benchmark_candidate=False,
    )
    issues = packet.validate()
    if issues:
        for issue in issues:
            print(f"[evidence] {issue}")
        return 1
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(packet.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(out), "checksum": packet.to_dict()["checksum"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

