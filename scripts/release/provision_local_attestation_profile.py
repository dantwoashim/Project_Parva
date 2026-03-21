#!/usr/bin/env python3
"""Provision a local provenance signing profile for release validation."""

from __future__ import annotations

import argparse
import json
import secrets
import socket
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIR = PROJECT_ROOT / ".verify" / "release"
KEY_PATH = PROFILE_DIR / "provenance_attestation.key"
KEY_ID_PATH = PROFILE_DIR / "provenance_attestation.key_id"


def _build_default_key_id() -> str:
    host = socket.gethostname().strip().lower().replace(" ", "-") or "local"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"local-release-{host}-{stamp}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace any existing local attestation profile.",
    )
    args = parser.parse_args(argv)

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    if args.force or not KEY_PATH.exists():
        KEY_PATH.write_text(secrets.token_hex(32), encoding="utf-8")

    if args.force or not KEY_ID_PATH.exists():
        KEY_ID_PATH.write_text(_build_default_key_id(), encoding="utf-8")

    payload = {
        "profile_dir": str(PROFILE_DIR),
        "key_file": str(KEY_PATH),
        "key_id_file": str(KEY_ID_PATH),
        "key_id": KEY_ID_PATH.read_text(encoding="utf-8").strip(),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
