from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_ARTIFACT_DIRS = [
    PROJECT_ROOT / "data" / "public",
    PROJECT_ROOT / "backend" / "data" / "public_artifacts",
]
FORBIDDEN_FRAGMENTS = (
    "data/source_archive",
    "data\\source_archive",
    "data/future_bs/private",
    "data\\future_bs\\private",
    "/Users/",
    "C:" + "\\",
)


def test_public_artifacts_do_not_expose_private_or_local_paths() -> None:
    failures: list[str] = []
    for root in PUBLIC_ARTIFACT_DIRS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".json", ".jsonl", ".md", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for fragment in FORBIDDEN_FRAGMENTS:
                if fragment in text:
                    failures.append(f"{path.relative_to(PROJECT_ROOT)} contains {fragment}")

    assert not failures, "\n".join(failures)
