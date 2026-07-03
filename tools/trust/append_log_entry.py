#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from contextlib import suppress
from pathlib import Path
from uuid import uuid4

try:
    from .common import (
        DEFAULT_MANIFEST_PATH,
        DEFAULT_SIGNATURE_PATH,
        TRUST_LOG_PATH,
        TrustToolError,
        load_json,
        repo_path,
        sha256_file,
        sha256_prefixed,
        source_registry_hash_from_manifest,
    )
except ImportError:  # pragma: no cover - direct script execution
    from common import (
        DEFAULT_MANIFEST_PATH,
        DEFAULT_SIGNATURE_PATH,
        TRUST_LOG_PATH,
        TrustToolError,
        load_json,
        repo_path,
        sha256_file,
        sha256_prefixed,
        source_registry_hash_from_manifest,
    )


def build_release_log_entry(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    signature_path: Path = DEFAULT_SIGNATURE_PATH,
    *,
    timestamp: str,
) -> dict[str, object]:
    manifest_path = repo_path(manifest_path)
    signature_path = repo_path(signature_path)
    if not manifest_path.exists():
        raise TrustToolError(f"manifest not found: {manifest_path}")
    if not signature_path.exists():
        raise TrustToolError(f"signature artifact not found: {signature_path}")

    manifest = load_json(manifest_path)
    release_id = manifest.get("release_id")
    if not isinstance(release_id, str) or not release_id:
        raise TrustToolError("manifest release_id is missing")

    return {
        "entry_id": str(uuid4()),
        "event": "calendar.release.published",
        "release_id": release_id,
        "artifact_hash": sha256_prefixed(sha256_file(manifest_path)),
        "source_registry_hash": source_registry_hash_from_manifest(manifest),
        "timestamp": timestamp,
        "signature_ref": str(signature_path.relative_to(repo_path("."))).replace("\\", "/"),
    }


def append_log_entry(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    signature_path: Path = DEFAULT_SIGNATURE_PATH,
    log_path: Path = TRUST_LOG_PATH,
    *,
    timestamp: str,
) -> dict[str, object]:
    entry = build_release_log_entry(manifest_path, signature_path, timestamp=timestamp)
    log_path = repo_path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = log_path.with_suffix(log_path.suffix + ".lock")
    lock_fd: int | None = None
    deadline = time.monotonic() + 10
    while lock_fd is None:
        try:
            lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            if time.monotonic() >= deadline:
                raise TrustToolError(
                    f"timed out waiting for transparency log lock: {lock_path}"
                ) from exc
            time.sleep(0.1)
    try:
        with log_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
    finally:
        os.close(lock_fd)
        with suppress(FileNotFoundError):
            lock_path.unlink()
    return entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Append a public release event to the alpha transparency log.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST_PATH.relative_to(repo_path("."))))
    parser.add_argument("--signature", default=str(DEFAULT_SIGNATURE_PATH.relative_to(repo_path("."))))
    parser.add_argument("--log", default=str(TRUST_LOG_PATH.relative_to(repo_path("."))))
    parser.add_argument("--timestamp", required=True)
    args = parser.parse_args(argv)

    try:
        entry = append_log_entry(
            Path(args.manifest),
            Path(args.signature),
            Path(args.log),
            timestamp=args.timestamp,
        )
    except TrustToolError as exc:
        print(f"log append failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(entry, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
