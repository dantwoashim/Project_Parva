"""Deterministic source snapshot hashing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.sources.hashing import canonical_json_hash


def load_json_files(paths: list[Path]) -> list[dict[str, Any]]:
    return [json.loads(path.read_text(encoding="utf-8-sig")) for path in sorted(paths)]


def build_source_snapshot(dockets: list[dict[str, Any]], receipts: list[dict[str, Any]]) -> dict[str, Any]:
    docket_hashes = [canonical_json_hash(docket) for docket in sorted(dockets, key=lambda row: row["source_id"])]
    receipt_hashes = [
        canonical_json_hash(receipt)
        for receipt in sorted(receipts, key=lambda row: row.get("receipt_id", ""))
    ]
    snapshot_hash = canonical_json_hash({"dockets": docket_hashes, "receipts": receipt_hashes})
    return {
        "kind": "source_snapshot",
        "snapshot_hash": f"sha256:{snapshot_hash}",
        "docket_hashes": [f"sha256:{item}" for item in docket_hashes],
        "receipt_hashes": [f"sha256:{item}" for item in receipt_hashes],
    }
