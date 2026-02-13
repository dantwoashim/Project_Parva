#!/usr/bin/env python3
"""
Generate canonical festival snapshot for blockchain provenance.

Creates snapshot.json with all festival dates for 2024-2030,
then generates SHA-256 hash and Merkle root.
"""

import json
import hashlib
from datetime import date
from pathlib import Path
from typing import Dict, List, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.calendar.calculator_v2 import calculate_festival_v2, list_festivals_v2
from app.provenance.snapshot import create_snapshot


def generate_snapshot(years: List[int] = None) -> Dict[str, Any]:
    """
    Generate canonical snapshot of all festival dates.
    
    Args:
        years: List of years to include (default: 2024-2030)
    
    Returns:
        Snapshot dictionary with metadata and festival data
    """
    if years is None:
        years = list(range(2024, 2031))
    
    festivals = list(list_festivals_v2())
    data = {}
    
    for year in years:
        data[str(year)] = {}
        for fid in sorted(festivals):
            result = calculate_festival_v2(fid, year)
            if result:
                data[str(year)][fid] = {
                    "start": result.start_date.isoformat(),
                    "end": result.end_date.isoformat(),
                    "duration": result.duration_days,
                    "method": result.method,
                    "lunar_month": result.lunar_month,
                }
    
    snapshot = {
        "version": "1.0.0",
        "generated": date.today().isoformat(),
        "years": years,
        "festivals": list(sorted(festivals)),
        "total_entries": sum(len(data[str(y)]) for y in years),
        "data": data,
    }
    
    return snapshot


def compute_hash(snapshot: Dict) -> str:
    """Compute SHA-256 hash of snapshot."""
    # Sort keys for deterministic ordering
    canonical = json.dumps(snapshot, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode()).hexdigest()


def main():
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    
    print("Generating festival snapshot...")
    snapshot = generate_snapshot()
    
    # Save snapshot
    snapshot_path = output_dir / "snapshot.json"
    with open(snapshot_path, "w") as f:
        json.dump(snapshot, f, indent=2)
    print(f"✅ Saved: {snapshot_path}")
    
    # Compute and save hash
    hash_value = compute_hash(snapshot)
    hash_path = output_dir / "snapshot_hash.txt"
    with open(hash_path, "w") as f:
        f.write(f"{hash_value}\n")
    print(f"✅ Hash: {hash_value}")
    print(f"✅ Saved: {hash_path}")
    
    # Summary
    print(f"\nSnapshot contains:")
    print(f"  Years: {snapshot['years'][0]}-{snapshot['years'][-1]}")
    print(f"  Festivals: {len(snapshot['festivals'])}")
    print(f"  Total entries: {snapshot['total_entries']}")

    # Create a provenance snapshot record (hashes + metadata + festival snapshot copy)
    record = create_snapshot()
    print(f"✅ Created provenance snapshot record: {record.snapshot_id}")


if __name__ == "__main__":
    main()
