#!/usr/bin/env python3
"""Generate a public Parva offline bundle."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.protocol_service import offline_bundle_manifest_payload  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    manifest = offline_bundle_manifest_payload()
    for item in manifest["contents"]:
        source = PROJECT_ROOT / item["path"]
        if not source.exists():
            continue
        target = output / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    (output / "bundle-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (output / "protocol-version.txt").write_text(manifest["protocol_version"] + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(output), "contents": len(manifest["contents"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
