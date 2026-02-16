"""
Provenance API Routes

Endpoints for verifying festival date authenticity using hashes + Merkle proofs.
"""

import hashlib
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.calendar.merkle import (
    get_festival_proof,
    get_merkle_root,
    MerkleTree,
)
from app.provenance.snapshot import (
    LEGACY_FESTIVAL_SNAPSHOT,
    SNAPSHOT_DIR,
    SnapshotRecord,
    create_snapshot,
    get_latest_snapshot,
    load_snapshot,
    verify_snapshot,
)
from app.provenance.transparency import (
    append_entry,
    append_snapshot_event,
    list_anchors,
    load_log_entries,
    prepare_anchor_payload,
    record_anchor,
    replay_state,
    verify_log_integrity,
)
from app.explainability.store import get_reason_trace


router = APIRouter(prefix="/api/provenance", tags=["provenance"])
PROJECT_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_BETA_DASHBOARD = PROJECT_ROOT / "docs" / "public_beta" / "dashboard_metrics.json"


class ProofResponse(BaseModel):
    """Merkle proof response."""
    festival_id: str
    year: int
    leaf_hash: str
    proof: List[Dict[str, str]]
    merkle_root: str
    verified: bool


class RootResponse(BaseModel):
    """Merkle root response."""
    merkle_root: str
    snapshot_id: Optional[str] = None
    dataset_hash: Optional[str] = None
    rules_hash: Optional[str] = None
    total_entries: int


class SnapshotVerifyResponse(BaseModel):
    """Snapshot verification output."""
    snapshot_id: str
    valid: bool
    checks: Dict[str, bool]
    expected: Dict[str, str]
    actual: Dict[str, str]


class TraceVerifyResponse(BaseModel):
    """Trace verification output."""

    trace_id: str
    valid: bool
    checks: Dict[str, bool]
    detail: Dict[str, Any]


def _resolve_festival_snapshot_path(snapshot_id: Optional[str]) -> Optional[str]:
    """
    Resolve the frozen festival snapshot path from a snapshot record.
    """
    if snapshot_id:
        record = load_snapshot(snapshot_id)
    else:
        record = get_latest_snapshot(create_if_missing=False)

    if record and record.festival_snapshot_path:
        configured_path = Path(record.festival_snapshot_path)
        # Snapshot records may contain absolute paths from a different machine.
        # Rehydrate them by checking canonical local locations first.
        candidates = [
            configured_path,
            SNAPSHOT_DIR / configured_path.name,
        ]
        if record.snapshot_id:
            candidates.append(SNAPSHOT_DIR / f"{record.snapshot_id}.festival_snapshot.json")
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
    if LEGACY_FESTIVAL_SNAPSHOT.exists():
        return str(LEGACY_FESTIVAL_SNAPSHOT)
    return None


@router.get("/root")
async def get_provenance_root() -> RootResponse:
    """
    Get the current Merkle root and snapshot hash.
    
    This root can be anchored to a blockchain for immutable verification.
    """
    snapshot = get_latest_snapshot(create_if_missing=False)
    snapshot_path = _resolve_festival_snapshot_path(snapshot.snapshot_id if snapshot else None)
    merkle_root = get_merkle_root(Path(snapshot_path)) if snapshot_path else ""
    total_entries = 0
    if snapshot_path and Path(snapshot_path).exists():
        import json
        with open(snapshot_path, encoding="utf-8") as f:
            data = json.load(f)
            total_entries = data.get("total_entries", 0)

    return RootResponse(
        merkle_root=merkle_root,
        snapshot_id=snapshot.snapshot_id if snapshot else None,
        dataset_hash=snapshot.dataset_hash if snapshot else None,
        rules_hash=snapshot.rules_hash if snapshot else None,
        total_entries=total_entries,
    )


@router.post("/snapshot/create")
async def create_provenance_snapshot() -> Dict[str, Any]:
    """
    Create a fresh provenance snapshot record.
    """
    record: SnapshotRecord = create_snapshot()
    append_snapshot_event(
        snapshot_id=record.snapshot_id,
        dataset_hash=record.dataset_hash,
        rules_hash=record.rules_hash,
    )
    return {
        "snapshot_id": record.snapshot_id,
        "created_at": record.created_at,
        "dataset_hash": record.dataset_hash,
        "rules_hash": record.rules_hash,
    }


@router.get("/snapshot/{snapshot_id}/verify", response_model=SnapshotVerifyResponse)
async def verify_snapshot_endpoint(snapshot_id: str) -> SnapshotVerifyResponse:
    """
    Verify stored snapshot hashes against current dataset/rules.
    """
    try:
        details = verify_snapshot(snapshot_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SnapshotVerifyResponse(**details)


@router.get("/verify/{festival_id}", response_model=ProofResponse)
async def verify_festival(
    festival_id: str,
    year: int = Query(..., description="Year to verify", ge=2000, le=2200),
    snapshot: Optional[str] = Query(None, description="Snapshot id (optional)"),
) -> ProofResponse:
    """
    Get Merkle proof for a specific festival date.
    
    Use this proof to verify that the festival date comes from
    the canonical, auditable dataset.
    """
    snapshot_path = _resolve_festival_snapshot_path(snapshot)
    if not snapshot_path:
        raise HTTPException(
            status_code=503,
            detail="Snapshot not available"
        )

    proof = get_festival_proof(Path(snapshot_path), year, festival_id)
    
    if proof is None:
        raise HTTPException(
            status_code=404,
            detail=f"Festival {festival_id} not found for year {year}"
        )
    
    # Verify the proof is valid
    verified = MerkleTree.verify_proof(
        proof.leaf_hash,
        proof.proof,
        proof.root
    )
    
    return ProofResponse(
        festival_id=festival_id,
        year=year,
        leaf_hash=proof.leaf_hash,
        proof=[{"hash": h, "position": p} for h, p in proof.proof],
        merkle_root=proof.root,
        verified=verified,
    )


@router.get("/verify/trace/{trace_id}", response_model=TraceVerifyResponse)
async def verify_trace(trace_id: str) -> TraceVerifyResponse:
    """
    Verify deterministic integrity of a stored explainability trace.

    Checks:
    - trace exists
    - required fields present
    - trace_id matches deterministic hash of canonical payload
    """
    trace = get_reason_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace '{trace_id}' not found")

    required = ["trace_type", "subject", "inputs", "outputs", "steps", "provenance"]
    required_present = all(k in trace for k in required)

    canonical_payload = {
        "trace_type": trace.get("trace_type"),
        "subject": trace.get("subject"),
        "inputs": trace.get("inputs"),
        "outputs": trace.get("outputs"),
        "steps": trace.get("steps"),
        "provenance": trace.get("provenance"),
    }
    canonical = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    expected_trace_id = f"tr_{digest[:20]}"
    deterministic_id_match = trace_id == expected_trace_id

    checks = {
        "exists": True,
        "required_fields_present": required_present,
        "deterministic_id_match": deterministic_id_match,
    }
    valid = all(checks.values())

    detail = {
        "expected_trace_id": expected_trace_id,
        "created_at": trace.get("created_at"),
        "trace_type": trace.get("trace_type"),
        "subject": trace.get("subject"),
    }
    return TraceVerifyResponse(
        trace_id=trace_id,
        valid=valid,
        checks=checks,
        detail=detail,
    )


@router.get("/proof", response_model=ProofResponse)
async def get_proof(
    festival: str = Query(..., description="Festival id"),
    year: int = Query(..., ge=2000, le=2200),
    snapshot: Optional[str] = Query(None, description="Snapshot id"),
) -> ProofResponse:
    """
    Query-style proof endpoint for easier external verification tooling.
    """
    return await verify_festival(festival_id=festival, year=year, snapshot=snapshot)


@router.get("/batch-verify")
async def batch_verify(
    year: int = Query(..., description="Year to verify", ge=2000, le=2200),
    festivals: str = Query(None, description="Comma-separated festival IDs (optional)"),
    snapshot: Optional[str] = Query(None, description="Snapshot id (optional)"),
) -> Dict[str, Any]:
    """
    Verify multiple festivals at once.
    
    Returns Merkle root and individual verification status.
    """
    snapshot_path = _resolve_festival_snapshot_path(snapshot)
    if not snapshot_path:
        raise HTTPException(status_code=503, detail="Snapshot not available")

    import json
    with open(snapshot_path, encoding="utf-8") as f:
        snapshot_data = json.load(f)

    year_data = snapshot_data.get("data", {}).get(str(year), {})
    
    if festivals:
        festival_ids = [f.strip() for f in festivals.split(",")]
    else:
        festival_ids = list(year_data.keys())
    
    results = []
    for fid in festival_ids:
        if fid in year_data:
            proof = get_festival_proof(Path(snapshot_path), year, fid)
            if proof:
                verified = MerkleTree.verify_proof(
                    proof.leaf_hash, proof.proof, proof.root
                )
                results.append({
                    "festival_id": fid,
                    "verified": verified,
                    "date": year_data[fid].get("start"),
                })
    
    return {
        "year": year,
        "merkle_root": get_merkle_root(Path(snapshot_path)),
        "total_verified": sum(1 for r in results if r["verified"]),
        "festivals": results,
    }


@router.get("/transparency/log")
async def get_transparency_log(limit: int = Query(100, ge=1, le=1000)) -> Dict[str, Any]:
    """
    Return transparency log tail for public inspection.
    """
    rows = load_log_entries()
    sliced = rows[-limit:]
    return {
        "total_entries": len(rows),
        "returned": len(sliced),
        "entries": sliced,
    }


@router.get("/transparency/audit")
async def audit_transparency_log() -> Dict[str, Any]:
    """
    Verify transparency log hash-chain integrity.
    """
    return verify_log_integrity()


@router.get("/transparency/replay")
async def transparency_replay() -> Dict[str, Any]:
    """
    Replay append-only transparency log and expose derived state.
    """
    return replay_state()


@router.post("/transparency/append")
async def append_transparency_event(
    event_type: str = Query(..., description="Event type label"),
    note: Optional[str] = Query(None, description="Optional note"),
) -> Dict[str, Any]:
    """
    Append an ad-hoc transparency event (for audited operations).
    """
    row = append_entry(event_type, {"note": note} if note else {})
    return row.to_dict()


@router.get("/transparency/anchor/prepare")
async def prepare_anchor(note: Optional[str] = Query(None)) -> Dict[str, Any]:
    """
    Prepare an external anchoring payload (optional blockchain mirror).
    """
    return prepare_anchor_payload(note=note or "")


@router.post("/transparency/anchor/record")
async def save_anchor_record(
    tx_ref: str = Query(..., description="External transaction/hash reference"),
    network: str = Query(..., description="Anchor network label, e.g. ethereum, bitcoin, testnet"),
) -> Dict[str, Any]:
    """
    Record an external anchor reference for auditability.
    """
    return record_anchor(tx_ref=tx_ref, network=network)


@router.get("/transparency/anchors")
async def get_anchor_records(limit: int = Query(50, ge=1, le=500)) -> Dict[str, Any]:
    """
    Return recorded external anchor references.
    """
    rows = list_anchors(limit=limit)
    return {
        "count": len(rows),
        "anchors": rows,
    }


@router.get("/dashboard")
async def get_public_beta_dashboard() -> Dict[str, Any]:
    """
    Return public beta dashboard metrics (generated artifact).
    """
    if not PUBLIC_BETA_DASHBOARD.exists():
        raise HTTPException(
            status_code=404,
            detail="Dashboard metrics not generated yet. Run backend/tools/generate_beta_dashboard.py",
        )
    import json

    return json.loads(PUBLIC_BETA_DASHBOARD.read_text(encoding="utf-8"))
