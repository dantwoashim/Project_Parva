#!/usr/bin/env python3
"""Promote a reviewed public evidence packet to a benchmark candidate."""

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
from app.evidence.review import promote_to_benchmark_candidate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet")
    args = parser.parse_args()
    raw = json.loads(Path(args.packet).read_text(encoding="utf-8"))
    source = ingest_source_record(raw)
    packet = EvidencePacket(
        source=source,
        extracted_rows=raw["extracted_rows"],
        normalized_rows=raw["normalized_rows"],
        review_status=raw["review_status"],
        reviewer_required=raw["reviewer_required"],
        benchmark_candidate=True,
    )
    print(json.dumps(promote_to_benchmark_candidate(packet), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

