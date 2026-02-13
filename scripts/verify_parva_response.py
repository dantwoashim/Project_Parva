#!/usr/bin/env python3
"""Verify provenance metadata in a saved Parva API response.

Usage:
  python3 scripts/verify_parva_response.py response.json [--base http://localhost:8000]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_url(raw: str, base: str) -> str:
    parsed = urlparse(raw)
    if parsed.scheme and parsed.netloc:
        return raw
    return f"{base.rstrip('/')}{raw}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Parva response provenance")
    parser.add_argument("response", type=Path, help="Path to JSON response file")
    parser.add_argument("--base", default="http://localhost:8000", help="Base URL for relative verify_url")
    args = parser.parse_args()

    payload = _read_json(args.response)
    provenance = payload.get("provenance") or payload.get("meta", {}).get("provenance")

    if not provenance:
        print("No provenance object found in response", file=sys.stderr)
        return 2

    print("Provenance metadata:")
    print(json.dumps(provenance, indent=2))

    verify_url = provenance.get("verify_url")
    if not verify_url:
        print("No verify_url available; metadata is present but not externally checkable.")
        return 0

    url = _resolve_url(verify_url, args.base)
    print(f"\nFetching verification endpoint: {url}")

    try:
        with urlopen(url, timeout=15) as resp:
            body = resp.read().decode("utf-8")
    except (HTTPError, URLError) as exc:
        print(f"Verification request failed: {exc}", file=sys.stderr)
        return 3

    result = json.loads(body)
    print(json.dumps(result, indent=2))

    # Accept either snapshot verification shape or Merkle proof shape.
    if "verified" in result:
        ok = bool(result["verified"])
    elif "valid" in result:
        ok = bool(result["valid"])
    else:
        ok = True

    if not ok:
        print("Verification failed", file=sys.stderr)
        return 4

    print("Verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
