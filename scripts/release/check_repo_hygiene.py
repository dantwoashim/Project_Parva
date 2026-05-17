#!/usr/bin/env python3
"""Reject known non-Parva workspace residue in the repo root."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _tracked_path_issue(path: str) -> str | None:
    if path.startswith("frontend/dist/"):
        return "tracked frontend build artifact"
    allowed_reports = (
        "reports/compatibility/project-parva-reference-full.json",
        "reports/ephemeris_accuracy/README.md",
        "reports/ephemeris_accuracy/boundary_risk_summary.md",
        "reports/ephemeris_accuracy/solar_ingress_jpl_vs_swiss.json",
        "reports/ephemeris_accuracy/solar_ingress_jpl_vs_swiss.md",
        "reports/external_reviewer_packet/README.md",
        "reports/external_reviewer_packet/ai_tooling_boundary.md",
        "reports/external_reviewer_packet/architecture_summary.md",
        "reports/external_reviewer_packet/benchmark_summary.md",
        "reports/external_reviewer_packet/ci_status.md",
        "reports/external_reviewer_packet/commercial_readiness.md",
        "reports/external_reviewer_packet/jpl_accuracy_boundary.md",
        "reports/external_reviewer_packet/known_limitations.md",
        "reports/external_reviewer_packet/maturity_summary.md",
        "reports/external_reviewer_packet/release_readiness.md",
        "reports/external_reviewer_packet/trust_boundary_summary.md",
        "reports/external_reviewer_packet/verification_matrix.md",
        "reports/external_rules_audit.md",
        "reports/next_roadmap_execution/README.md",
        "reports/next_roadmap_execution/files_changed.md",
        "reports/next_roadmap_execution/next_handoff.md",
        "reports/next_roadmap_execution/unresolved_blockers.md",
        "reports/next_roadmap_execution/verification_matrix.json",
        "reports/next_roadmap_execution/verification_matrix.md",
        "reports/phase_07_future_bs_governance/module_classification.md",
        "reports/phase_08_performance_sre/latency_baseline.json",
        "reports/phase_09_frontend_sdk_dx/adoption_hardening_report.md",
        "reports/phase_00_trust_arrest.md",
        "reports/phase_00_trust_arrest_public_surface_repair.md",
        "reports/phase_01_authority_control.md",
        "reports/phase_01_trust_taint_field_provenance_policy_vm.md",
        "reports/phase_02_source_dockets.md",
        "reports/phase_02_source_dockets_extraction_receipts_archive.md",
        "reports/phase_03_canonical_boundary.md",
        "reports/phase_03_canonicalization_boundary_ignorance.md",
        "reports/phase_04_static_forge.md",
        "reports/phase_04_static_forge_causal_bitplane_foundation.md",
        "reports/phase_05_first_membrane.md",
        "reports/phase_05_first_membrane_capsule_artifact_verify.md",
        "reports/phase_06_proof_origami_timepacks.md",
        "reports/phase_06_witness_graph_proof_origami_timepacks.md",
        "reports/phase_07_constraint_solver.md",
        "reports/phase_07_causal_bitplane_solver_unsat_negative.md",
        "reports/phase_08_payroll_conformance.md",
        "reports/phase_08_payroll_date_risk_conformance_capsule.md",
        "reports/phase_09_tvl_devanagari_console.md",
        "reports/phase_09_temporal_ir_tvl_devanagari_console.md",
        "reports/phase_10_local_kernel_timeline_embed.md",
        "reports/phase_10_local_browser_kernel_timeline_embed.md",
        "reports/phase_11_freshness_transparency.md",
        "reports/phase_11_diff_freshness_light_cone_transparency.md",
        "reports/phase_12_polyphonic_time.md",
        "reports/phase_12_polyphonic_time_branch_skeptic_reports.md",
        "reports/phase_13_tempc_overlays.md",
        "reports/phase_13_tempc_overlays_counterfactual_engine.md",
        "reports/phase_14_notice_to_obligation.md",
        "reports/phase_14_notice_to_obligation_compliance_extension.md",
        "reports/phase_15_federated_ecosystem.md",
        "reports/phase_15_federated_witness_network_temporal_proof_ecosystem.md",
        "reports/release/frontend_bundle_budget.json",
        "reports/release/slo_dashboard_definition.json",
        "reports/release_readiness/final_verification_matrix.json",
        "reports/release_readiness/final_verification_matrix.md",
        "reports/release_readiness/public_claims_checklist.md",
        "reports/release_readiness/README.md",
        "reports/release_readiness/release_checklist.md",
        "reports/distribution_readiness/README.md",
        "reports/distribution_readiness/baseline.md",
        "reports/distribution_readiness/duplicate_runtime_cleanup.md",
        "reports/distribution_readiness/external_launch_checklist.md",
        "reports/distribution_readiness/final_verification_matrix.json",
        "reports/distribution_readiness/final_verification_matrix.md",
        "reports/distribution_readiness/next_30_days.md",
        "reports/real_world_readiness/README.md",
        "reports/real_world_readiness/baseline.md",
        "reports/real_world_readiness/duplicate_runtime_cleanup.md",
        "reports/real_world_readiness/final_verification_matrix.json",
        "reports/real_world_readiness/final_verification_matrix.md",
        "reports/real_world_readiness/forbidden_claims.md",
        "reports/real_world_readiness/next_30_days.md",
        "reports/real_world_readiness/remaining_blockers.md",
        "reports/real_world_readiness/safe_claims.md",
        "reports/red_check_closure/README.md",
        "reports/ceiling_execution/climax_demos.json",
        "reports/ceiling_execution/climax_demos.md",
        "reports/ceiling_execution/depth_hardening_plan.md",
        "reports/ceiling_execution/depth_inventory.json",
        "reports/ceiling_execution/phase_requirement_matrix.json",
        "reports/ceiling_execution/phase_requirement_matrix.md",
        "reports/ceiling_depth/architecture_gap_matrix.json",
        "reports/ceiling_depth/architecture_gap_matrix.md",
        "reports/ceiling_depth/remaining_blockers.md",
        "reports/samples/payroll_date_risk_sample.md",
        "reports/trust-status.json",
    )
    if path in allowed_reports:
        return None
    if path.startswith("reports/") or path == "evaluation.csv":
        return "tracked generated report artifact"
    if ".egg-info/" in path:
        return "tracked Python package metadata"
    if "__pycache__/" in path or path.endswith(".pyc"):
        return "tracked Python bytecode cache"
    if path.endswith(".DS_Store"):
        return "tracked macOS metadata"
    return None


def main() -> int:
    issues: list[str] = []

    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if tracked.returncode == 0:
        for path in tracked.stdout.splitlines():
            if not (PROJECT_ROOT / path).exists():
                continue
            issue = _tracked_path_issue(path)
            if issue:
                issues.append(f"{path}: {issue}")

    root_package = PROJECT_ROOT / "package.json"
    if root_package.exists():
        payload = _load_json(root_package)
        if payload.get("name") == "viral-sync-workspace":
            issues.append("Root package.json still identifies the repo as viral-sync-workspace.")
        workspaces = payload.get("workspaces") or []
        if any(item in {"app", "relayer", "server/actions", "cranks", "packages/*"} for item in workspaces):
            issues.append("Root package.json still declares unrelated viral-sync workspaces.")

    legacy_shared_package = PROJECT_ROOT / "packages" / "shared" / "package.json"
    if legacy_shared_package.exists():
        payload = _load_json(legacy_shared_package)
        package_name = str(payload.get("name") or "")
        if package_name.startswith("@viral-sync/"):
            issues.append("packages/shared/package.json still exports the unrelated @viral-sync package.")

    legacy_shared_source = PROJECT_ROOT / "packages" / "shared" / "src" / "index.ts"
    if legacy_shared_source.exists():
        source_text = legacy_shared_source.read_text(encoding="utf-8")
        if "LAMPORTS_PER_SOL" in source_text or "RELAYER_ROUTE_PREFIX" in source_text:
            issues.append("packages/shared/src/index.ts still contains unrelated relayer/Solana exports.")

    root_tsconfig = PROJECT_ROOT / "tsconfig.json"
    if root_tsconfig.exists():
        text = root_tsconfig.read_text(encoding="utf-8")
        if "packages/shared" in text or '"mocha"' in text:
            issues.append("Root tsconfig.json still references unrelated workspace test settings.")

    root_tsconfig_base = PROJECT_ROOT / "tsconfig.base.json"
    if root_tsconfig_base.exists():
        issues.append("Root tsconfig.base.json still exists even though Parva does not use a root TS workspace.")

    if issues:
        for issue in issues:
            print(f"[repo-hygiene] {issue}")
        raise SystemExit(1)

    print("Repository hygiene check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
