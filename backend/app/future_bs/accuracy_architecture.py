"""Artifact-backed accuracy architecture runner.

The runner produces source-policy, truth-fusion, lattice, hard-case, and
certification artifacts from the reconstructed corpus. It keeps official,
medium/high, and weak experimental policies separated so weak witnesses cannot
create official claim-readiness.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .active_learning.promotion_plan import build_human_review_promotion_plan
from .hard_cases.hard_case_benchmark import build_hard_case_benchmark
from .month_start.month_start_corpus import build_month_start_corpus
from .month_start.month_start_features import build_month_start_features
from .precedent.witness_precedent import build_witness_precedent_cases
from .program_synthesis.program_search import run_program_synthesis
from .regime.regime_model import detect_regime_changes
from .risk.green_certification import certify_green_predictions
from .rule_inversion.inversion_runner import run_hidden_rule_inversion
from .sequence.month_start_lattice_decoder import decode_month_start_lattice
from .source_policy import (
    INVALID_RECONSTRUCTED_ROWS,
    explain_official_witness_mismatch,
    policy_metrics,
    read_reconstructed_lengths,
)
from .truth_fusion.latent_truth_model import infer_latent_truth
from .truth_fusion.source_copy_detection import detect_source_copy_patterns
from .truth_fusion.source_independence import build_source_independence_graph
from .truth_fusion.weak_label_fusion import fuse_month_start_candidates

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = PROJECT_ROOT / "data" / "future_bs"
LAB_DIR = DATA_ROOT / "accuracy_lab"
REPORT_DIR = DATA_ROOT / "reports"
PUBLICATION_STATUS = "computed_prediction_not_official"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _source_policy_outputs() -> dict[str, Any]:
    rows = read_reconstructed_lengths()
    policies = {
        "official_strict": policy_metrics("official_strict", rows),
        "medium_high_training": policy_metrics("medium_high_training", rows),
        "all_witness_experimental": policy_metrics("all_witness_experimental", rows),
    }
    _write_json(LAB_DIR / "official_strict_metrics.json", policies["official_strict"])
    _write_json(LAB_DIR / "medium_high_training_metrics.json", policies["medium_high_training"])
    _write_json(LAB_DIR / "all_witness_experimental_metrics.json", policies["all_witness_experimental"])
    summary = {
        "publication_status": PUBLICATION_STATUS,
        "policies": policies,
        "tier_5_6_official_claim_blocked": True,
        "official_witness_mismatch_explanation": explain_official_witness_mismatch(72, policies["official_strict"]["month_cases"]),
    }
    _write_json(LAB_DIR / "source_policy_metrics.json", summary)
    _write_md(
        LAB_DIR / "source_policy_metrics.md",
        [
            "# Source Policy Metrics",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            f"- Official strict month cases: {policies['official_strict']['month_cases']}",
            f"- Medium/high training month cases: {policies['medium_high_training']['month_cases']}",
            f"- All-witness experimental month cases: {policies['all_witness_experimental']['month_cases']}",
            "- Tier 5/6 witnesses cannot affect official_strict claim-readiness.",
        ],
    )
    excluded = {
        "publication_status": PUBLICATION_STATUS,
        "excluded_rows": [
            {"bs_year": year, "bs_month": month, "reason": "invalid_or_fragile_reconstructed_row"}
            for year, month in sorted(INVALID_RECONSTRUCTED_ROWS)
        ],
        "policy": "Excluded from training and claim metrics.",
    }
    _write_json(LAB_DIR / "excluded_rows.json", excluded)
    _write_md(
        LAB_DIR / "excluded_rows.md",
        [
            "# Excluded Reconstructed Rows",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            *[f"- {row['bs_year']}-{row['bs_month']:02d}: {row['reason']}" for row in excluded["excluded_rows"]],
        ],
    )
    return summary


def _truth_fusion_outputs() -> dict[str, Any]:
    fusion = fuse_month_start_candidates()
    independence = build_source_independence_graph()
    copy = detect_source_copy_patterns(independence)
    latent = infer_latent_truth(fusion)
    _write_json(LAB_DIR / "weak_label_fusion_results.json", fusion)
    _write_md(
        LAB_DIR / "weak_label_fusion_summary.md",
        [
            "# Weak Label Fusion Summary",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            f"- Cases fused: {fusion['case_count']}",
            f"- Low-margin cases: {fusion['low_margin_count']}",
            "- Weak-label fusion is reported for training/experimental analysis, not official_strict proof.",
        ],
    )
    _write_json(LAB_DIR / "source_independence_graph.json", independence)
    _write_md(
        LAB_DIR / "source_copy_detection_report.md",
        [
            "# Source Copy Detection Report",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            f"- Source nodes: {independence['source_count']}",
            f"- Pair edges: {independence['edge_count']}",
            f"- Copy-risk pairs: {copy['copy_risk_edges']}",
            "- Copy-risk pairs are down-weighted and cannot promote official_strict claim-readiness.",
        ],
    )
    _write_json(LAB_DIR / "latent_truth_month_starts.json", latent)
    _write_md(
        LAB_DIR / "latent_truth_summary.md",
        [
            "# Latent Truth Summary",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            f"- Month-start cases: {latent['case_count']}",
            f"- Manual review required: {latent['manual_review_required_count']}",
        ],
    )
    return {"fusion": fusion, "independence": independence, "copy": copy, "latent": latent}


def _month_rule_outputs() -> dict[str, Any]:
    corpus = build_month_start_corpus()
    features = build_month_start_features()
    inversion = run_hidden_rule_inversion(features)
    regimes = detect_regime_changes(features)
    synthesis = run_program_synthesis(features)
    _write_json(LAB_DIR / "month_start_corpus.json", corpus)
    _write_json(LAB_DIR / "month_start_features.json", features)
    _write_json(LAB_DIR / "hidden_rule_inversion.json", inversion)
    _write_json(LAB_DIR / "effective_cutoff_surfaces.json", inversion["effective_cutoff_surfaces"])
    _write_md(
        LAB_DIR / "hidden_rule_inversion.md",
        [
            "# Hidden Rule Inversion",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            f"- Cases used: {inversion['case_count']}",
            f"- Selected rule family: {inversion['selected_rule_family']}",
            f"- Limitation: {inversion['effective_cutoff_surfaces']['limitation']}",
        ],
    )
    _write_json(LAB_DIR / "regime_change_report.json", regimes)
    _write_json(LAB_DIR / "regime_assignments.json", {"publication_status": PUBLICATION_STATUS, "assignments": regimes["assignments"]})
    _write_md(
        LAB_DIR / "regime_change_report.md",
        [
            "# Regime Change Report",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            f"- Regime counts: {json.dumps(regimes['regime_counts'], sort_keys=True)}",
            f"- Change points: {len(regimes['change_points'])}",
        ],
    )
    _write_json(LAB_DIR / "program_synthesis_results.json", synthesis)
    _write_json(LAB_DIR / "best_rule_program.json", synthesis.get("selected_program") or {})
    _write_md(
        LAB_DIR / "program_synthesis_report.md",
        [
            "# Program Synthesis Report",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            f"- Mode: {synthesis['synthesis_mode']}",
            f"- Selected program: {(synthesis.get('selected_program') or {}).get('name', 'none')}",
            f"- Limitation: {synthesis['limitation']}",
        ],
    )
    return {"corpus": corpus, "features": features, "inversion": inversion, "regimes": regimes, "synthesis": synthesis}


def _risk_outputs() -> dict[str, Any]:
    precedent = build_witness_precedent_cases()
    hard_cases = build_hard_case_benchmark()
    lattice = decode_month_start_lattice()
    green = certify_green_predictions()
    _write_json(LAB_DIR / "precedent_tower_search_results.json", {"publication_status": PUBLICATION_STATUS, "witness_precedent_cases": precedent["cases"][:50]})
    _write_json(LAB_DIR / "best_precedent_config.json", {"publication_status": PUBLICATION_STATUS, "k": 5, "distance_metric": "witness_hybrid", "source_policy_aware": True})
    _write_md(
        LAB_DIR / "precedent_tower_report.md",
        [
            "# Precedent Tower Report",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            f"- Witness precedent cases retained: {precedent['case_count']}",
            "- Features: month, previous/next length, year modulo 19/28/57, source tier, agreement score, boundary sensitivity.",
        ],
    )
    _write_json(LAB_DIR / "hard_case_benchmark.json", hard_cases)
    _write_md(
        LAB_DIR / "hard_case_benchmark.md",
        [
            "# Hard Case Benchmark",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            f"- Cases: {hard_cases['case_count']}",
            "- Hard cases focus on Ashwin/Kartik, source disagreements, fragile totals, and 2083-style risk.",
        ],
    )
    _write_json(LAB_DIR / "month_start_lattice_decoding.json", lattice)
    _write_md(
        LAB_DIR / "month_start_lattice_report.md",
        [
            "# Month-Start Lattice Report",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            f"- Years decoded: {lattice['year_count']}",
            f"- Invalid decoded years: {lattice['invalid_year_count']}",
            "- Invalid years are RED/non-claimable.",
        ],
    )
    _write_json(LAB_DIR / "green_certification_report.json", green)
    _write_md(
        LAB_DIR / "green_certification_report.md",
        [
            "# Green Certification Report",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            f"- Certified GREEN months: {green.get('certified_green_months', 0)}",
            f"- Wide prediction-set GREEN violations: {green.get('wide_prediction_set_green_violation_count', 0)}",
            "- A wide prediction set cannot be GREEN.",
        ],
    )
    return {"precedent": precedent, "hard_cases": hard_cases, "lattice": lattice, "green": green}


def _final_metrics_outputs(source_metrics: dict[str, Any], risk: dict[str, Any]) -> dict[str, Any]:
    best_metrics = _load_json(LAB_DIR / "best_metrics.json")
    readiness = _load_json(LAB_DIR / "accuracy_readiness_final.json")
    official_cases = source_metrics["policies"]["official_strict"]["month_cases"]
    metric_threshold_passed = bool(best_metrics.get("metric_threshold_passed", False))
    claim_ready = bool(metric_threshold_passed and official_cases >= 528)
    readiness.update(
        {
            "publication_status": PUBLICATION_STATUS,
            "metric_threshold_passed": metric_threshold_passed,
            "claim_ready_with_sufficient_corpus": claim_ready,
            "claim_ready_99_green_zone": claim_ready,
            "claim_ready_99_overall": False,
            "official_cases": official_cases,
            "required_official_cases": 528,
            "source_policy_metrics_path": "data/future_bs/accuracy_lab/source_policy_metrics.json",
            "invalid_reconstructed_rows_excluded": len(INVALID_RECONSTRUCTED_ROWS),
        }
    )
    if official_cases < 528:
        blockers = set(readiness.get("claim_blockers", []))
        blockers.add("official_strict_cases_below_required_threshold")
        readiness["claim_blockers"] = sorted(blockers)
    _write_json(LAB_DIR / "accuracy_readiness_final.json", readiness)
    _write_md(
        LAB_DIR / "accuracy_readiness_final.md",
        [
            "# Accuracy Readiness Final",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            f"- Metric threshold passed: {readiness['metric_threshold_passed']}",
            f"- Claim ready with sufficient corpus: {readiness['claim_ready_with_sufficient_corpus']}",
            f"- Claim ready 99 green-zone: {readiness['claim_ready_99_green_zone']}",
            f"- Official strict cases: {official_cases}",
            f"- Required official cases: {readiness['required_official_cases']}",
            f"- Wrong GREEN count: {best_metrics.get('wrong_green_count', 'unknown')}",
            f"- Green-zone accuracy: {best_metrics.get('green_zone_accuracy', 'unknown')}%",
            f"- Green-zone coverage: {best_metrics.get('green_zone_coverage', 'unknown')}%",
            f"- Invalid reconstructed rows excluded: {len(INVALID_RECONSTRUCTED_ROWS)}",
            "",
            "## Blockers",
            *[f"- {blocker}" for blocker in readiness.get("claim_blockers", [])],
        ],
    )
    threshold_report = {
        "publication_status": PUBLICATION_STATUS,
        "objective": "wrong_green_count_zero_first",
        "wide_prediction_set_green_violation_count": risk["green"].get("wide_prediction_set_green_violation_count", 0),
        "selected_thresholds_path": "data/future_bs/accuracy_lab/best_risk_thresholds.json",
        "claim_ready_99_green_zone": readiness["claim_ready_99_green_zone"],
    }
    _write_json(LAB_DIR / "risk_threshold_report.json", threshold_report)
    _write_md(
        LAB_DIR / "risk_threshold_report.md",
        [
            "# Risk Threshold Report",
            "",
            f"Publication status: `{PUBLICATION_STATUS}`",
            "",
            "- Objective order: wrong GREEN count, false GREEN rate, green-zone accuracy, then coverage.",
            f"- Wide prediction-set GREEN violations: {threshold_report['wide_prediction_set_green_violation_count']}",
        ],
    )
    return readiness


def run_full_accuracy_architecture() -> dict[str, Any]:
    LAB_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    source_metrics = _source_policy_outputs()
    fusion = _truth_fusion_outputs()
    month_rule = _month_rule_outputs()
    risk = _risk_outputs()
    promotion = build_human_review_promotion_plan()
    readiness = _final_metrics_outputs(source_metrics, risk)
    residual_path = LAB_DIR / "residual_analysis.md"
    if not residual_path.exists():
        _write_md(residual_path, ["# Residual Analysis", "", f"Publication status: `{PUBLICATION_STATUS}`", "", "No residual artifact was available before this architecture pass."])
    return {
        "publication_status": PUBLICATION_STATUS,
        "source_policy_month_cases": {
            key: value["month_cases"] for key, value in source_metrics["policies"].items()
        },
        "weak_label_low_margin": fusion["fusion"]["low_margin_count"],
        "latent_truth_review_cases": fusion["latent"]["manual_review_required_count"],
        "month_start_cases": month_rule["corpus"]["case_count"],
        "invalid_lattice_years": risk["lattice"]["invalid_year_count"],
        "promotion_plan_rows": len(promotion),
        "claim_ready_99_green_zone": readiness.get("claim_ready_99_green_zone"),
    }


__all__ = ["run_full_accuracy_architecture"]
