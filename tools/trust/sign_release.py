#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from .common import DEFAULT_MANIFEST_PATH, DEFAULT_SIGNATURE_PATH, TrustToolError
    from .common import build_alpha_signature_payload, repo_path
except ImportError:  # pragma: no cover - direct script execution
    from common import DEFAULT_MANIFEST_PATH, DEFAULT_SIGNATURE_PATH, TrustToolError
    from common import build_alpha_signature_payload, repo_path


def sign_release(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    output_path: Path = DEFAULT_SIGNATURE_PATH,
    *,
    signed_at: str | None = None,
) -> dict[str, object]:
    manifest_path = repo_path(manifest_path)
    output_path = repo_path(output_path)
    if not manifest_path.exists():
        raise TrustToolError(f"manifest not found: {manifest_path}")
    payload = build_alpha_signature_payload(manifest_path, signed_at=signed_at)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create an alpha hash-only release signature artifact.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST_PATH.relative_to(repo_path("."))))
    parser.add_argument("--output", default=str(DEFAULT_SIGNATURE_PATH.relative_to(repo_path("."))))
    parser.add_argument("--signed-at", help="Optional deterministic signed_at timestamp")
    args = parser.parse_args(argv)

    try:
        payload = sign_release(Path(args.manifest), Path(args.output), signed_at=args.signed_at)
    except TrustToolError as exc:
        print(f"release signing failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
