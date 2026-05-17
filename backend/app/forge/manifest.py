"""Static bundle manifest generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.sources.hashing import sha256_file


@dataclass(frozen=True)
class ManifestEntry:
    path: str
    sha256: str

    def as_dict(self) -> dict[str, str]:
        return {"path": self.path, "sha256": self.sha256}


def build_manifest(root: Path) -> dict[str, Any]:
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            entries.append(ManifestEntry(path.relative_to(root).as_posix(), sha256_file(path)).as_dict())
    return {"kind": "parva_static_manifest", "version": "1.0.0", "files": entries}
