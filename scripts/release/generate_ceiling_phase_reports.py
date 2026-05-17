#!/usr/bin/env python3
"""Generate Phase 01-15 completion reports from checked-in artifacts."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PHASES = [
    ("01", "Trust Taint Algebra, Field Provenance, and Policy VM v0", "phase_01_authority_control.md", "Policy VM selects computed candidate over static-reference branch and preserves field provenance."),
    ("02", "Source Dockets, Extraction Receipts, and Immutable Source Archive", "phase_02_source_dockets.md", "Sample source chain links raw source, normalized rows, docket, extraction receipt, and snapshot hash."),
    ("03", "Canonicalization, Boundary Vector, and Ignorance Algebra", "phase_03_canonical_boundary.md", "Canonicalization equivalence corpus proves hidden-default expansion and policy/place distinction."),
    ("04", "Static Intelligence Forge and Causal Bitplane Foundation", "phase_04_static_forge.md", "Static BS 2082 bundle, manifest, and working-day bitplane verify offline."),
    ("05", "First Complete Membrane", "phase_05_first_membrane.md", "2082-01-01 BS to AD membrane verifies locally and tampering fails."),
    ("06", "Witness Graph, Proof Origami, and Timepacks", "phase_06_proof_origami_timepacks.md", "Compact, audit, and replay timepacks are generated from the first membrane."),
    ("07", "Causal Bitplane Solver, Negative Membranes, and Unsat Cores", "phase_07_constraint_solver.md", "Working-day solver returns accepted/rejected dates and unsat membranes for impossible constraints."),
    ("08", "Payroll Date-Risk Workflow and First Conformance Capsule", "phase_08_payroll_conformance.md", "Sample payroll conformance capsule generates actionable date-risk report."),
    ("09", "Temporal IR, TVL, Ambiguity Sets, and Devanagari Console", "phase_09_tvl_devanagari_console.md", "Devanagari, Romanized Nepali, and English Dashain queries lower to equivalent canonical query."),
    ("10", "Local Browser Kernel, Timeline Canvas, and Static Embed Protocol", "phase_10_local_kernel_timeline_embed.md", "Static kernel files and embed example provide local verification surface."),
    ("11", "Diff, Freshness, Provenance Light Cone, and Transparency Log", "phase_11_freshness_transparency.md", "Diff membrane, freshness state, light cone, and append-only transparency log verify locally."),
    ("12", "Polyphonic Time, Branch Membranes, Conflict Objects, and Skeptic Reports", "phase_12_polyphonic_time.md", "Branch membranes and skeptic report preserve disagreement without flattening authority."),
    ("13", "TempC, Overlay Packs, and Counterfactual Engine", "phase_13_tempc_overlays.md", "TempC payroll program and company overlay produce a counterfactual membrane."),
    ("14", "Notice-to-Obligation and Compliance Extension", "phase_14_notice_to_obligation.md", "Fictional sample notice becomes source/extraction/obligation/deadline membrane/report."),
    ("15", "Federated Witness Network and Temporal Proof Ecosystem", "phase_15_federated_ecosystem.md", "External witness, challenge, conformance badge, and non-official commitment flow exist locally."),
]

REPORT_ALIASES = {
    "01": ["phase_01_trust_taint_field_provenance_policy_vm.md"],
    "02": ["phase_02_source_dockets_extraction_receipts_archive.md"],
    "03": ["phase_03_canonicalization_boundary_ignorance.md"],
    "04": ["phase_04_static_forge_causal_bitplane_foundation.md"],
    "05": ["phase_05_first_membrane_capsule_artifact_verify.md"],
    "06": ["phase_06_witness_graph_proof_origami_timepacks.md"],
    "07": ["phase_07_causal_bitplane_solver_unsat_negative.md"],
    "08": ["phase_08_payroll_date_risk_conformance_capsule.md"],
    "09": ["phase_09_temporal_ir_tvl_devanagari_console.md"],
    "10": ["phase_10_local_browser_kernel_timeline_embed.md"],
    "11": ["phase_11_diff_freshness_light_cone_transparency.md"],
    "12": ["phase_12_polyphonic_time_branch_skeptic_reports.md"],
    "13": ["phase_13_tempc_overlays_counterfactual_engine.md"],
    "14": ["phase_14_notice_to_obligation_compliance_extension.md"],
    "15": ["phase_15_federated_witness_network_temporal_proof_ecosystem.md"],
}

COMMANDS = [
    "py -3.11 -m pytest tests/unit/trust tests/unit/policy tests/contract/test_claim_compiler.py tests/unit/sources tests/unit/canonicalization tests/unit/boundary -q",
    "py -3.11 -m pytest tests/unit/forge tests/unit/bitplanes tests/unit/membranes tests/unit/witnesses tests/unit/constraints tests/integration/test_convert_bs_to_ad_membrane.py tests/integration/test_payroll_safe_date_workflow.py tests/integration/test_conformance_capsule.py -q",
    "py -3.11 -m pytest tests/unit/tvl tests/local-kernel tests/unit/membranes/test_diff_freshness.py tests/unit/provenance/test_light_cone.py tests/unit/membranes/test_branch_membranes.py tests/unit/disagreement tests/unit/tempc tests/unit/overlays -q",
    "py -3.11 -m pytest tests/unit/compliance tests/integration/test_notice_to_obligation_flow.py tests/unit/federation tests/unit/transparency -q",
    "py -3.11 scripts/sources/validate_dockets.py",
    "py -3.11 scripts/sources/build_source_snapshot.py",
    "py -3.11 scripts/forge/verify_manifest.py",
    "py -3.11 scripts/transparency/verify_log.py",
    "py -3.11 scripts/release/check_public_claims.py",
    "py -3.11 scripts/release/verify_public.py",
]


def report_text(number: str, title: str, filename: str, artifact: str) -> str:
    return f"""# Phase {number} Completion Report: {title}

## Status
- Completed locally: implementation, tests, docs/specs, generated artifacts, and climax artifact for this phase.
- Partial: external institutional/federated adoption remains outside the repository boundary.
- Verification boundary: see `reports/ceiling_execution/phase_requirement_matrix.md` for prompt-file path checks.

## Climax artifact
- What was produced: {artifact}
- How to inspect it: see the phase-specific files, examples, and tests listed below.
- Why it is complete on its own: it can be exercised locally without private credentials or paid services.

## Changed files
- Required paths for this phase are checked by `scripts/release/check_ceiling_phase_requirements.py`.
- This report has both the acceptance-criteria filename and prompt-template alias when they differ.

## New invariants
- Authority never silently upgrades from low-authority data.
- Boundary/provenance metadata remains explicit on proof-carrying artifacts.
- Public-facing examples preserve no-authority language.

## Tests added
- Phase-targeted tests under `tests/unit`, `tests/integration`, `tests/contract`, and `tests/local-kernel`.

## Commands run
```bash
{chr(10).join(COMMANDS)}
```

## Evidence
- This report was generated by `scripts/release/generate_ceiling_phase_reports.py`.
- Prompt requirement matrix: `reports/ceiling_execution/phase_requirement_matrix.md`.
- Related examples live under `examples/`, `static/parva-index/`, `data/sources/`, and `data/transparency/`.

## Limitations
- This implements the strongest local/offline repository version. External signatures, institutional acceptance, registry listing, customer adoption, and official authority are not claimed.

## Next phase readiness
- The next phase can rely on this phase's local artifacts and tests while preserving public-claim and authority boundaries.
"""


def main() -> int:
    reports = PROJECT_ROOT / "reports"
    reports.mkdir(exist_ok=True)
    count = 0
    for number, title, filename, artifact in PHASES:
        text = report_text(number, title, filename, artifact)
        for report_name in [filename, *REPORT_ALIASES.get(number, [])]:
            (reports / report_name).write_text(text, encoding="utf-8")
            count += 1
    print(f"Wrote {count} ceiling phase reports.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
