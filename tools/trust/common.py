from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_STATUS = "computed_prediction_not_official"
SIGNATURE_ALGORITHM = "alpha_hash_only_sha256"
TRUST_LOG_PATH = ROOT / "data" / "public" / "transparency-log" / "parva-log.jsonl"
DEFAULT_MANIFEST_PATH = ROOT / "data" / "public" / "releases" / "parva-bs-public-demo.manifest.json"
DEFAULT_SIGNATURE_PATH = ROOT / "data" / "public" / "releases" / "parva-bs-public-demo.signature.json"


class TrustToolError(ValueError):
    pass


def repo_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    candidate = candidate.resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise TrustToolError(f"path escapes repository root: {path}") from exc
    return candidate


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise TrustToolError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise TrustToolError(f"{path}: root must be an object")
    return payload


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_prefixed(value: str) -> str:
    return f"sha256:{value}"


def release_id_from_manifest(manifest: dict[str, Any]) -> str:
    release_id = manifest.get("release_id")
    if not isinstance(release_id, str) or not release_id:
        raise TrustToolError("manifest release_id is missing")
    return release_id


def source_registry_hash_from_manifest(manifest: dict[str, Any]) -> str:
    for artifact in manifest.get("artifact_hashes", []):
        if isinstance(artifact, dict) and artifact.get("artifact_id") == "source-registry":
            digest = artifact.get("sha256")
            if isinstance(digest, str) and digest:
                return sha256_prefixed(digest)
    raise TrustToolError("manifest source-registry hash is missing")


def build_alpha_signature_payload(
    manifest_path: Path,
    *,
    signed_at: str | None = None,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    manifest_hash = sha256_file(manifest_path)
    release_id = release_id_from_manifest(manifest)
    artifact_hash = sha256_prefixed(manifest_hash)
    signed_at_value = signed_at or now_utc()
    signature_body = {
        "release_id": release_id,
        "artifact_hash": artifact_hash,
        "signature_algorithm": SIGNATURE_ALGORITHM,
        "signed_at": signed_at_value,
    }
    signature = sha256_prefixed(sha256_text(canonical_json(signature_body)))
    return {
        **signature_body,
        "signature": signature,
    }


def expected_alpha_signature(signature_payload: dict[str, Any]) -> str:
    body = {
        "release_id": signature_payload.get("release_id"),
        "artifact_hash": signature_payload.get("artifact_hash"),
        "signature_algorithm": signature_payload.get("signature_algorithm"),
        "signed_at": signature_payload.get("signed_at"),
    }
    return sha256_prefixed(sha256_text(canonical_json(body)))


def validate_alpha_signature_payload(
    payload: dict[str, Any],
    *,
    manifest_path: Path,
) -> None:
    manifest = load_json(manifest_path)
    expected_release_id = release_id_from_manifest(manifest)
    expected_artifact_hash = sha256_prefixed(sha256_file(manifest_path))
    if payload.get("release_id") != expected_release_id:
        raise TrustToolError("signature release_id does not match manifest")
    if payload.get("artifact_hash") != expected_artifact_hash:
        raise TrustToolError("signature artifact_hash does not match manifest")
    if payload.get("signature_algorithm") != SIGNATURE_ALGORITHM:
        raise TrustToolError("unsupported signature algorithm")
    if payload.get("signature") != expected_alpha_signature(payload):
        raise TrustToolError("signature value does not match alpha hash-only payload")
