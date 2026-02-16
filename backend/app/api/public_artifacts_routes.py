"""Public artifact discovery and static data exposure endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PRECOMPUTED_DIR = PROJECT_ROOT / "output" / "precomputed"
REPORTS_DIR = PROJECT_ROOT / "reports"
DOCS_PUBLIC_BETA = PROJECT_ROOT / "docs" / "public_beta"

router = APIRouter(prefix="/api/public", tags=["public-artifacts"])


def _artifact_row(path: Path, category: str) -> dict:
    stat = path.stat()
    return {
        "name": path.name,
        "category": category,
        "size_bytes": stat.st_size,
        "modified_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "path": str(path),
    }


def _iter_precomputed_candidates() -> List[Path]:
    candidates = sorted(PRECOMPUTED_DIR.glob("*.json"))
    if candidates:
        return candidates
    # In clean CI clones, output/ is gitignored. Fall back to checked-in
    # public-beta JSON artifacts so manifest remains useful and deterministic.
    return sorted(DOCS_PUBLIC_BETA.glob("*.json"))


@router.get("/artifacts/manifest")
async def get_artifacts_manifest() -> Dict[str, object]:
    """
    List publicly consumable generated artifacts.
    """
    PRECOMPUTED_DIR.mkdir(parents=True, exist_ok=True)
    files: List[dict] = []

    for path in _iter_precomputed_candidates():
        files.append(_artifact_row(path, "precomputed"))

    authority_json = REPORTS_DIR / "authority_dashboard.json"
    if authority_json.exists():
        files.append(_artifact_row(authority_json, "dashboard"))

    conformance = REPORTS_DIR / "conformance_report.json"
    if conformance.exists():
        files.append(_artifact_row(conformance, "conformance"))

    published_dashboard = DOCS_PUBLIC_BETA / "authority_dashboard.json"
    if published_dashboard.exists():
        files.append(_artifact_row(published_dashboard, "published-dashboard"))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_files": len(files),
        "files": files,
    }


@router.get("/artifacts/precomputed/{filename}")
async def get_precomputed_artifact(filename: str):
    """
    Download precomputed JSON artifacts (panchanga/festival year files).
    """
    if "/" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON artifacts are exposed")

    path = PRECOMPUTED_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(path, media_type="application/json", filename=filename)


@router.get("/artifacts/dashboard")
async def get_authority_dashboard_artifact():
    path = REPORTS_DIR / "authority_dashboard.json"
    if not path.exists():
        path = DOCS_PUBLIC_BETA / "authority_dashboard.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Dashboard artifact not generated yet")
    return FileResponse(path, media_type="application/json", filename=path.name)
