#!/usr/bin/env python3
"""Prepare and optionally record transparency anchor payload."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.provenance.transparency import prepare_anchor_payload, record_anchor

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = PROJECT_ROOT / "reports" / "transparency_anchor_payload.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare transparency anchor payload")
    parser.add_argument("--note", default="")
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--tx-ref", default="")
    parser.add_argument("--network", default="testnet")
    args = parser.parse_args()

    payload = prepare_anchor_payload(note=args.note)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    out = {"prepared": payload, "recorded": None}
    if args.record:
        if not args.tx_ref:
            raise SystemExit("--tx-ref is required with --record")
        out["recorded"] = record_anchor(tx_ref=args.tx_ref, network=args.network, payload=payload)

    print(json.dumps(out, indent=2))
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
