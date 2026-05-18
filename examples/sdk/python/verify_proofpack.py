from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "backend"), str(ROOT / "packages/parva-python")]

from app.membranes.proofpack import verify_proof_pack  # noqa: E402


def main(path: str = "examples/external/proofpacks/civil-conversion.proofpack.json") -> int:
    artifact = json.loads((ROOT / path).read_text(encoding="utf-8"))
    ok, reason = verify_proof_pack(artifact)
    boundary = artifact.get("boundary") or (artifact.get("membrane") or {}).get("boundary", {})
    print(json.dumps({"verified": ok, "reason": reason, "boundary": boundary}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "examples/external/proofpacks/civil-conversion.proofpack.json"))
