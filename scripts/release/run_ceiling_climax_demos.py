#!/usr/bin/env python3
"""Run executable climax demos for Phase 01-15 and write evidence artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.boundary.ignorance import IgnoranceKind, IgnoranceState  # noqa: E402
from app.boundary.vector import BoundaryVector  # noqa: E402
from app.canonicalization.equivalence import equivalent  # noqa: E402
from app.canonicalization.normalize import identity_hash  # noqa: E402
from app.compliance.notice_ingestion import ingest_notice  # noqa: E402
from app.compliance.report import render_obligation_report  # noqa: E402
from app.conformance.badges import generate_badge  # noqa: E402
from app.conformance.runner import run_conformance_capsule  # noqa: E402
from app.constraints.solver import solve_working_days  # noqa: E402
from app.disagreement.convergence import convergence_report  # noqa: E402
from app.federation.challenge import challenge_object  # noqa: E402
from app.federation.witness_submission import WitnessSubmission  # noqa: E402
from app.forge.verify import verify_manifest  # noqa: E402
from app.membranes.capsule import build_convert_bs_to_ad_capsule  # noqa: E402
from app.membranes.diff import diff_membrane  # noqa: E402
from app.membranes.freshness import resolve_freshness  # noqa: E402
from app.membranes.proof_origami import unfold  # noqa: E402
from app.membranes.timepack import build_timepack  # noqa: E402
from app.membranes.verifier import verify_membrane  # noqa: E402
from app.overlays.counterfactual import counterfactual_membrane  # noqa: E402
from app.policy.schema import PolicyCandidate  # noqa: E402
from app.policy.vm import PolicyVM  # noqa: E402
from app.provenance.light_cone import blast_radius  # noqa: E402
from app.sources.snapshot import build_source_snapshot, load_json_files  # noqa: E402
from app.tempc.compiler import compile_tempc  # noqa: E402
from app.tempc.interpreter import run_tempc  # noqa: E402
from app.trust.field_provenance import FieldProvenance, ProvenanceMap  # noqa: E402
from app.trust.taint import AuthorityTaint, TaintFlag  # noqa: E402
from app.tvl.parser import parse_temporal_query  # noqa: E402
from app.witnesses.graph import WitnessGraph, WitnessNode  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "reports" / "ceiling_execution"
OUTPUT_JSON = OUTPUT_DIR / "climax_demos.json"
OUTPUT_MD = OUTPUT_DIR / "climax_demos.md"
DETERMINISTIC_CREATED_AT = "2026-01-01T00:00:00+00:00"


def _candidate(candidate_id: str, authority: AuthorityTaint, result: dict[str, object]) -> PolicyCandidate:
    fields = {
        key: FieldProvenance(
            field_path=key,
            authority=authority,
            derivation="demo_derivation",
            source_docket_id="parva:src:v1:sample-2082-calendar-notice"
            if authority in {AuthorityTaint.STRUCTURED_OFFICIAL, AuthorityTaint.ARCHIVED_OFFICIAL}
            else None,
            flags=frozenset({TaintFlag.REVIEW_REQUIRED}) if authority == AuthorityTaint.STATIC_REFERENCE else frozenset(),
        )
        for key in result
    }
    provenance = ProvenanceMap(fields)
    return PolicyCandidate(
        candidate_id=candidate_id,
        method=candidate_id,
        result=result,
        authority=authority,
        field_provenance=provenance,
        boundary=BoundaryVector.from_provenance(provenance),
    )


def run_demos() -> dict[str, object]:
    computed = _candidate("computed_solar_civil", AuthorityTaint.COMPUTED_UNCERTIFIED, {"month_days": 31})
    static = _candidate("static_table", AuthorityTaint.STATIC_REFERENCE, {"month_days": 32})
    phase_01 = PolicyVM().select([static, computed]).as_dict()

    source_root = PROJECT_ROOT / "data" / "sources"
    dockets = load_json_files(list((source_root / "dockets").glob("*.json")))
    receipts = load_json_files(list((source_root / "extraction_receipts").glob("*.json")))
    source_snapshot = build_source_snapshot(dockets, receipts)
    phase_02 = {
        "source_snapshot_hash": source_snapshot["snapshot_hash"],
        "docket_count": len(source_snapshot["docket_hashes"]),
    }

    equivalent_queries = [
        {"operation": "find_festival_date", "input": {"festival": "दशैं", "year": "२०८२"}},
        {"operation": "find_festival_date", "input": {"festival": "dashain", "year": "2082"}},
    ]
    phase_03 = {
        "equivalent": equivalent(*equivalent_queries),
        "identity_hash": identity_hash(equivalent_queries[0]),
        "deferred_state": IgnoranceState(IgnoranceKind.AUTHORITY_DEFERRED, "future official source absent").as_dict(),
    }

    phase_04 = {"manifest_verified": verify_manifest(PROJECT_ROOT / "static" / "parva-index")}

    capsule = build_convert_bs_to_ad_capsule(2082, 1, 1)
    phase_05 = {"verify": verify_membrane(capsule), "identity_hash": capsule["identity_hash"]}

    graph = WitnessGraph()
    graph.add_node(WitnessNode("membrane", capsule["witness_hash"], "membrane"))
    graph.add_node(WitnessNode("source", "sha256:source", "source_docket"))
    graph.add_edge("membrane", "source")
    phase_06 = {
        "lineage": graph.lineage("membrane"),
        "folded": unfold(capsule, "compact"),
        "timepack": build_timepack(capsule, "audit"),
    }

    phase_07 = solve_working_days(bs_year=2082, bs_month=1, count=3, holidays={1})

    conformance_capsule = json.loads((PROJECT_ROOT / "examples" / "conformance" / "payroll_core_2082.json").read_text())
    phase_08 = run_conformance_capsule(conformance_capsule)

    phase_09 = {
        "devanagari": parse_temporal_query("२०८२ दशैं कहिले").as_dict(),
        "roman": parse_temporal_query("2082 dashain kahile").as_dict(),
    }

    phase_10 = {
        "local_kernel_files": sorted(path.name for path in (PROJECT_ROOT / "packages" / "parva-local-kernel" / "src").glob("*")),
        "embed_exists": (PROJECT_ROOT / "static" / "parva-embed.js").exists(),
    }

    version_a = {"date": "2082-01-01", "working_day": True}
    version_b = {"date": "2082-01-01", "working_day": False}
    diff = diff_membrane(version_a, version_b, ["payroll:sample"])
    phase_11 = {
        "diff": diff,
        "freshness": resolve_freshness("sha256:old", {"sha256:new"}, superseded_by="sha256:new"),
        "light_cone": blast_radius("source", {"report": ["source"], "payroll": ["report"]}),
    }

    phase_12 = {
        "convergence": convergence_report(
            [
                {"branch": "canonical", "result": {"date": "2082-01-01"}},
                {"branch": "community", "result": {"date": "2082-01-02"}},
            ]
        )
    }

    tempc_source = (PROJECT_ROOT / "examples" / "tempc" / "payroll_safe_dates.tempc").read_text(encoding="utf-8")
    program = compile_tempc(tempc_source)
    baseline = run_tempc(program, bs_year=2082, bs_month=1)
    overlay = json.loads((PROJECT_ROOT / "examples" / "overlays" / "company_payroll_overlay.json").read_text())
    phase_13 = counterfactual_membrane(baseline, overlay)

    notice = (PROJECT_ROOT / "examples" / "notices" / "sample_notice.md").read_text(encoding="utf-8")
    obligation_flow = ingest_notice(notice)
    phase_14 = {
        "flow": obligation_flow,
        "report_preview": render_obligation_report(obligation_flow).splitlines()[:8],
    }

    witness = WitnessSubmission(
        submitter_id="community:sample",
        claim={"date": "2083-01-01", "publication_status": "computed_prediction_not_official"},
        source_docket={"source_id": "parva:src:v1:sample"},
        proof_pack={"level": "sample"},
        signature=None,
        authority_scope="community_branch_only",
    ).as_dict()
    challenge = challenge_object("community:sample", "counter evidence submitted", {"source": "counter"})
    phase_15 = {
        "witness": witness,
        "challenge": challenge,
        "badge": generate_badge(phase_08),
    }

    return {
        "phase_01": phase_01,
        "phase_02": phase_02,
        "phase_03": phase_03,
        "phase_04": phase_04,
        "phase_05": phase_05,
        "phase_06": phase_06,
        "phase_07": phase_07,
        "phase_08": phase_08,
        "phase_09": phase_09,
        "phase_10": phase_10,
        "phase_11": phase_11,
        "phase_12": phase_12,
        "phase_13": phase_13,
        "phase_14": phase_14,
        "phase_15": phase_15,
    }


def _normalize_demo_payload(value: object) -> object:
    """Keep regenerated demo evidence stable for source-control checks."""
    if isinstance(value, dict):
        normalized: dict[str, object] = {}
        for key, child in value.items():
            if key == "created_at" and value.get("kind") == "parva_timepack":
                normalized[key] = DETERMINISTIC_CREATED_AT
            else:
                normalized[key] = _normalize_demo_payload(child)
        return normalized
    if isinstance(value, list):
        return [_normalize_demo_payload(child) for child in value]
    return value


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = _normalize_demo_payload(run_demos())
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Ceiling Climax Demo Evidence", ""]
    for phase, result in payload.items():
        lines.append(f"## {phase}")
        lines.append(f"- Evidence keys: {', '.join(sorted(result) if isinstance(result, dict) else ['value'])}")
        lines.append("")
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON} and {OUTPUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
