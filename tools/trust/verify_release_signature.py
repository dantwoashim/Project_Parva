#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from .common import (
        DEFAULT_MANIFEST_PATH,
        DEFAULT_SIGNATURE_PATH,
        TrustToolError,
        load_json,
        repo_path,
        validate_alpha_signature_payload,
    )
except ImportError:  # pragma: no cover - direct script execution
    from common import (
        DEFAULT_MANIFEST_PATH,
        DEFAULT_SIGNATURE_PATH,
        TrustToolError,
        load_json,
        repo_path,
        validate_alpha_signature_payload,
    )


def verify_release_signature(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    signature_path: Path = DEFAULT_SIGNATURE_PATH,
) -> list[str]:
    manifest_path = repo_path(manifest_path)
    signature_path = repo_path(signature_path)
    if not manifest_path.exists():
        raise TrustToolError(f"manifest not found: {manifest_path}")
    if not signature_path.exists():
        raise TrustToolError(f"signature artifact not found: {signature_path}")
    payload = load_json(signature_path)
    validate_alpha_signature_payload(payload, manifest_path=manifest_path)
    return [
        f"ok: signature {signature_path.relative_to(repo_path('.'))}",
        f"ok: release {payload['release_id']}",
        f"ok: algorithm {payload['signature_algorithm']}",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify an alpha hash-only release signature artifact.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST_PATH.relative_to(repo_path("."))))
    parser.add_argument("--signature", default=str(DEFAULT_SIGNATURE_PATH.relative_to(repo_path("."))))
    args = parser.parse_args(argv)

    try:
        messages = verify_release_signature(Path(args.manifest), Path(args.signature))
    except TrustToolError as exc:
        print(f"signature verification failed: {exc}", file=sys.stderr)
        return 1

    print("Project Parva release signature verification")
    for message in messages:
        print(message)
    print("signature verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
