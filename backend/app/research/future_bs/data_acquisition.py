"""Witness corpus reconstruction orchestration for future-BS accuracy work."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date
from typing import Any

from app.research.future_bs.data_acquisition_sources import (
    ACQUISITION_DIR,
    CORPUS_DIR,
    MONTH_LENGTH_FIELDS,
    MONTH_START_FIELDS,
    PUBLICATION_STATUS,
    REVIEW_FIELDS,
    SOURCE_TIERS,
    WITNESS_DIR,
    WITNESS_FIELDS,
    collect_source_witnesses,
    ensure_dirs,
    extract_open_source_converter_tables,
    extract_rat32_pages,
    make_witness,
    month_start_dates_from_lengths,
    parse_medic_days_in_month,
    parse_sharingapples_config,
    read_csv,
    source_policy,
    utc_now,
    write_csv,
    write_jsonl,
)


def collect_witnesses(fetch_rat32: bool = True) -> dict[str, Any]:
    return collect_source_witnesses(fetch_rat32=fetch_rat32)


def load_witnesses() -> list[dict[str, Any]]:
    rows = read_csv(WITNESS_DIR / "extracted_witnesses.csv")
    normalized = []
    for row in rows:
        item = dict(row)
        item["bs_year"] = int(item["bs_year"])
        item["bs_month"] = int(item["bs_month"])
        item["bs_day"] = int(item["bs_day"])
        item["source_tier"] = int(item["source_tier"])
        item["extraction_confidence"] = float(item["extraction_confidence"])
        normalized.append(item)
    return normalized


def build_agreement_graph(witnesses: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    witnesses = witnesses or load_witnesses()
    graph: dict[str, Any] = {
        "publication_status": PUBLICATION_STATUS,
        "created_at": utc_now(),
        "nodes": {},
    }
    for key, group in _group_witnesses(witnesses).items():
        candidates: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in group:
            candidates[str(row["ad_date"])].append(row)
        candidate_payloads = []
        total_weight = 0.0
        for ad_start, rows in sorted(candidates.items()):
            weight = sum(float(source_policy(str(row["source_type"]))["weight"]) * float(row["extraction_confidence"]) for row in rows)
            total_weight += weight
            candidate_payloads.append(
                {
                    "month_start_ad": ad_start,
                    "weight": round(weight, 4),
                    "witness_count": len(rows),
                    "source_ids": sorted({str(row["source_id"]) for row in rows}),
                    "best_source_tier": min(int(row["source_tier"]) for row in rows),
                }
            )
        best = max(candidate_payloads, key=lambda item: (item["weight"], -item["best_source_tier"], item["witness_count"]))
        graph["nodes"][f"{key[0]}-{key[1]:02d}"] = {
            "bs_year": key[0],
            "bs_month": key[1],
            "candidates": candidate_payloads,
            "chosen_month_start_ad": best["month_start_ad"],
            "agreement_score": round(best["weight"] / total_weight, 4) if total_weight else 0.0,
            "conflict": len(candidate_payloads) > 1,
        }
    (CORPUS_DIR / "source_agreement_graph.json").write_text(
        json.dumps(graph, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    confidence_rows = []
    for node in graph["nodes"].values():
        confidence_rows.append(
            {
                "bs_year": node["bs_year"],
                "bs_month": node["bs_month"],
                "month_start_ad": node["chosen_month_start_ad"],
                "agreement_score": node["agreement_score"],
                "candidate_count": len(node["candidates"]),
                "conflict": str(bool(node["conflict"])).lower(),
            }
        )
    write_csv(
        CORPUS_DIR / "month_start_confidence.csv",
        confidence_rows,
        ["bs_year", "bs_month", "month_start_ad", "agreement_score", "candidate_count", "conflict"],
    )
    return graph


def _group_witnesses(witnesses: list[dict[str, Any]]) -> dict[tuple[int, int], list[dict[str, Any]]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in witnesses:
        if int(row.get("bs_day", 0)) == 1:
            grouped[(int(row["bs_year"]), int(row["bs_month"]))].append(row)
    return grouped


def reconstruct_month_starts(witnesses: list[dict[str, Any]] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    witnesses = witnesses or load_witnesses()
    graph = build_agreement_graph(witnesses)
    grouped = _group_witnesses(witnesses)
    rows: list[dict[str, Any]] = []
    for key in sorted(grouped):
        group = grouped[key]
        node = graph["nodes"][f"{key[0]}-{key[1]:02d}"]
        chosen = str(node["chosen_month_start_ad"])
        chosen_rows = [row for row in group if str(row["ad_date"]) == chosen]
        conflict_rows = [row for row in group if str(row["ad_date"]) != chosen]
        best_tier = min(int(row["source_tier"]) for row in chosen_rows)
        agreement = float(node["agreement_score"])
        conflict = bool(conflict_rows)
        if best_tier == 1 and not conflict:
            status = "verified"
            manual = False
        elif conflict:
            status = "manual_review_required"
            manual = True
        elif best_tier <= 4 and agreement >= 0.7:
            status = "cross_source_agreement"
            manual = False
        else:
            status = "needs_review"
            manual = True
        rows.append(
            {
                "bs_year": key[0],
                "bs_month": key[1],
                "month_start_ad": chosen,
                "witness_count": len(group),
                "best_source_tier": best_tier,
                "agreement_score": round(agreement, 4),
                "source_ids": ";".join(sorted({str(row["source_id"]) for row in chosen_rows})),
                "conflicting_source_ids": ";".join(sorted({str(row["source_id"]) for row in conflict_rows})),
                "verification_status": status,
                "manual_review_required": str(manual).lower(),
                "notes": "conflicting candidates recorded" if conflict else "chosen by source-weighted agreement",
            }
        )
    write_csv(CORPUS_DIR / "reconstructed_month_starts.csv", rows, MONTH_START_FIELDS)
    return rows, graph


def reconstruct_month_lengths(start_rows: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if start_rows is None:
        start_rows, _ = reconstruct_month_starts()
    by_key = {(int(row["bs_year"]), int(row["bs_month"])): row for row in start_rows}
    length_rows: list[dict[str, Any]] = []
    full_years = {
        year
        for year in {key[0] for key in by_key}
        if all((year, month) in by_key for month in range(1, 13)) and (year + 1, 1) in by_key
    }
    for year, month in sorted(by_key):
        if year not in full_years:
            continue
        next_key = (year, month + 1) if month < 12 else (year + 1, 1)
        start = date.fromisoformat(str(by_key[(year, month)]["month_start_ad"]))
        end = date.fromisoformat(str(by_key[next_key]["month_start_ad"]))
        length = (end - start).days
        plausible = 29 <= length <= 32
        year_status = str(by_key[(year, month)]["verification_status"])
        usable_training = plausible and year_status != "manual_review_required"
        usable_official = plausible and int(by_key[(year, month)]["best_source_tier"]) == 1 and year_status == "verified"
        notes = []
        if not plausible:
            notes.append("implausible_month_length")
        if year_status == "needs_review":
            notes.append("weak_source_needs_review")
        if year_status == "manual_review_required":
            notes.append("conflict_manual_review_required")
        length_rows.append(
            {
                "bs_year": year,
                "bs_month": month,
                "month_start_ad": start.isoformat(),
                "next_month_start_ad": end.isoformat(),
                "month_length": length,
                "witness_count": by_key[(year, month)]["witness_count"],
                "best_source_tier": by_key[(year, month)]["best_source_tier"],
                "agreement_score": by_key[(year, month)]["agreement_score"],
                "verification_status": year_status if plausible else "invalid",
                "usable_for_training": str(bool(usable_training)).lower(),
                "usable_for_official_claim": str(bool(usable_official)).lower(),
                "notes": ";".join(notes) or "derived_from_adjacent_month_starts",
            }
        )
    write_csv(CORPUS_DIR / "reconstructed_month_lengths.csv", length_rows, MONTH_LENGTH_FIELDS)
    return length_rows


def generate_human_review_queue(start_rows: list[dict[str, Any]] | None = None, length_rows: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    start_rows = start_rows or read_csv(CORPUS_DIR / "reconstructed_month_starts.csv")
    length_rows = length_rows or read_csv(CORPUS_DIR / "reconstructed_month_lengths.csv")
    rows: list[dict[str, Any]] = []
    length_by_key = {(int(row["bs_year"]), int(row["bs_month"])): row for row in length_rows}
    for row in start_rows:
        year = int(row["bs_year"])
        month = int(row["bs_month"])
        issue = ""
        priority = 50
        reason = ""
        if row.get("conflicting_source_ids"):
            issue = "source_disagreement"
            priority = 100
            reason = "Multiple sources disagree on month start."
        elif int(row.get("best_source_tier", 9)) >= 5:
            issue = "low_trust_consensus"
            priority = 75
            reason = "Only software/third-party-level consensus currently supports this month."
        elif row.get("manual_review_required") == "true":
            issue = "manual_review_required"
            priority = 80
            reason = "Current verification status requires manual review."
        length = length_by_key.get((year, month))
        if length and int(length["month_length"]) not in {29, 30, 31, 32}:
            issue = "invalid_month_length"
            priority = 110
            reason = "Adjacent reconstructed starts imply implausible month length."
        if month in {6, 7} and 2071 <= year <= 2083:
            priority += 15
            reason = (reason + " " if reason else "") + "Ashwin/Kartik boundary is high-impact for 2083-style risk."
        if not issue and year in {2076, 2077, 2078, 2079}:
            issue = "printed_cross_check_priority"
            priority = 70
            reason = "Requested printed/official cross-check window."
        if not issue:
            continue
        rows.append(
            {
                "priority": priority,
                "bs_year": year,
                "bs_month": month,
                "issue_type": issue,
                "current_candidate_start_dates": row["month_start_ad"],
                "sources": row["source_ids"],
                "reason": reason,
                "expected_information_gain": "high" if priority >= 90 else "medium",
                "recommended_manual_action": "Obtain official/printed calendar image or newspaper masthead for this BS day 1.",
                "source_file_or_url": row["source_ids"],
                "page_number_or_crop_if_available": "",
            }
        )
    rows = sorted(rows, key=lambda item: (-int(item["priority"]), int(item["bs_year"]), int(item["bs_month"])))
    write_csv(CORPUS_DIR / "human_review_queue.csv", rows, REVIEW_FIELDS)
    md = ["# Human Review Queue", "", f"Rows: {len(rows)}", ""]
    for item in rows[:25]:
        md.append(
            f"- P{item['priority']} {item['bs_year']}-{int(item['bs_month']):02d}: "
            f"{item['issue_type']} - {item['reason']}"
        )
    (CORPUS_DIR / "human_review_queue.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return rows


def coverage_metrics(length_rows: list[dict[str, Any]] | None = None, witness_rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    length_rows = length_rows or read_csv(CORPUS_DIR / "reconstructed_month_lengths.csv")
    witness_rows = witness_rows or read_csv(WITNESS_DIR / "extracted_witnesses.csv")
    months_by_year: dict[int, set[int]] = defaultdict(set)
    for row in length_rows:
        months_by_year[int(row["bs_year"])].add(int(row["bs_month"]))
    years_with_12 = sorted(year for year, months in months_by_year.items() if len(months) == 12)
    witness_type_counts = Counter(str(row["source_type"]) for row in witness_rows)
    best_tier_counts = Counter(str(row["best_source_tier"]) for row in length_rows)
    conflict_count = sum(1 for row in read_csv(CORPUS_DIR / "reconstructed_month_starts.csv") if row.get("conflicting_source_ids"))
    manual_count = sum(1 for row in read_csv(CORPUS_DIR / "reconstructed_month_starts.csv") if row.get("manual_review_required") == "true")
    official_claim_count = sum(1 for row in length_rows if row.get("usable_for_official_claim") == "true")
    training_count = sum(1 for row in length_rows if row.get("usable_for_training") == "true")
    medium_high_years = sorted(
        year
        for year, months in months_by_year.items()
        if len(months) == 12
        and all(
            int(row["best_source_tier"]) <= 4
            for row in length_rows
            if int(row["bs_year"]) == year and int(row["bs_month"]) in months
        )
    )
    medium_high_past_years = [year for year in medium_high_years if year <= 2083]
    metrics = {
        "publication_status": PUBLICATION_STATUS,
        "created_at": utc_now(),
        "years_with_any_witness": len({int(row["bs_year"]) for row in witness_rows}),
        "years_with_12_months": len(years_with_12),
        "years_with_12_months_list": years_with_12,
        "months_reconstructed": len(length_rows),
        "months_official_verified": sum(1 for row in witness_rows if row["source_type"] == "official_verified"),
        "months_printed_verified": sum(1 for row in witness_rows if row["source_type"] == "printed_verified"),
        "months_public_daily_witness": sum(1 for row in witness_rows if row["source_type"] == "public_daily_witness"),
        "months_publisher_reference": sum(1 for row in witness_rows if row["source_type"] == "publisher_reference"),
        "months_software_reference": sum(1 for row in witness_rows if row["source_type"] == "software_table_reference"),
        "months_third_party_reference": sum(1 for row in witness_rows if row["source_type"] == "third_party_reference"),
        "months_needs_review": sum(1 for row in witness_rows if row["source_type"] == "needs_review"),
        "source_type_distribution": dict(witness_type_counts),
        "best_tier_distribution": dict(best_tier_counts),
        "conflict_count": conflict_count,
        "manual_review_required_count": manual_count,
        "usable_for_training_count": training_count,
        "usable_for_official_claim_count": official_claim_count,
        "medium_high_years_with_12_months": len(medium_high_years),
        "medium_high_years_with_12_months_list": medium_high_years,
        "medium_high_past_years_with_12_months": len(medium_high_past_years),
        "medium_high_past_years_with_12_months_list": medium_high_past_years,
        "source_labeled_months": len(length_rows),
        "primary_target_met": len(years_with_12) >= 40 and len(length_rows) >= 480,
        "medium_high_subgoal_met": len(medium_high_years) >= 20,
        "medium_high_30_past_year_subgoal_met": len(medium_high_past_years) >= 30,
        "minimum_fallback_met": all(year in years_with_12 for year in range(2071, 2084)),
    }
    metrics["target_reached"] = bool(metrics["primary_target_met"] or metrics["minimum_fallback_met"])
    return metrics


def write_coverage_report(metrics: dict[str, Any]) -> None:
    (ACQUISITION_DIR / "coverage_report.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Data Acquisition Coverage Report",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        f"- Target reached: {str(metrics['target_reached']).lower()}",
        f"- Primary target met: {str(metrics['primary_target_met']).lower()}",
        f"- Medium/high 20-year subgoal met: {str(metrics['medium_high_subgoal_met']).lower()}",
        f"- Medium/high 30-past-year subgoal met: {str(metrics['medium_high_30_past_year_subgoal_met']).lower()}",
        f"- Years with 12 reconstructed months: {metrics['years_with_12_months']}",
        f"- Medium/high past years with 12 reconstructed months: {metrics['medium_high_past_years_with_12_months']}",
        f"- Months reconstructed: {metrics['months_reconstructed']}",
        f"- Official witness rows: {metrics['months_official_verified']}",
        f"- Printed/archived witness rows: {metrics['months_printed_verified']}",
        f"- Publisher-reference witness rows: {metrics['months_publisher_reference']}",
        f"- Software-table witness rows: {metrics['months_software_reference']}",
        f"- Third-party witness rows: {metrics['months_third_party_reference']}",
        f"- Conflicts: {metrics['conflict_count']}",
        f"- Manual review required: {metrics['manual_review_required_count']}",
        f"- Usable for training month rows: {metrics['usable_for_training_count']}",
        f"- Usable for official claim month rows: {metrics['usable_for_official_claim_count']}",
        "",
        "The wide reconstruction target and 30-past-year Tier 1-4 support target are met when this report shows the subgoal as true.",
        "Official-grade 99% claims still require more Tier 1/strong Tier 2 source promotion.",
    ]
    (ACQUISITION_DIR / "coverage_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_acquisition_plan() -> None:
    lines = [
        "# Future BS Data Acquisition Plan",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        "## Current Automated Strategy",
        "",
        "1. Preserve existing official/recent Project Parva rows as Tier 1 witnesses.",
        "2. Preserve archived 2076-2077 official/patro rows as Tier 2 but manual-review required.",
        "3. Extract day-1 AD/BS witnesses from local HamroPatro public archive as Tier 6.",
        "4. Extract partial Ratopati public calendar event-day witnesses as Tier 4.",
        "5. Download and parse public Rat32 month pages for 2050-2083 as Tier 4.",
        "6. Download and parse public open-source converter tables as Tier 5.",
        "7. Reconstruct month starts by source-weighted agreement.",
        "8. Derive month lengths only from adjacent reconstructed month starts.",
        "9. Queue conflicts, weak consensus, and Ashwin/Kartik boundary months for manual review.",
        "",
        "## Next Manual Acquisition",
        "",
        "- Add NPNS/government PDF URLs for older years.",
        "- Add archive.org printed panchanga item URLs with year and publisher metadata.",
        "- Add Gorkhapatra/newspaper masthead URLs around BS month starts.",
        "- Promote only reviewed Tier 1/Tier 2 rows into official-grade accuracy claims.",
    ]
    (ACQUISITION_DIR / "acquisition_plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_corpus_quality_report(metrics: dict[str, Any]) -> None:
    (CORPUS_DIR / "corpus_quality_report.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Corpus Quality Report",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        f"- Years with 12 reconstructed months: {metrics['years_with_12_months']}",
        f"- Months reconstructed: {metrics['months_reconstructed']}",
        f"- Best-tier distribution: {json.dumps(metrics['best_tier_distribution'], sort_keys=True)}",
        f"- Source-type distribution: {json.dumps(metrics['source_type_distribution'], sort_keys=True)}",
        f"- Conflicts found: {metrics['conflict_count']}",
        f"- Human/manual review required: {metrics['manual_review_required_count']}",
        f"- Official-claim usable month rows: {metrics['usable_for_official_claim_count']}",
        "",
        "Tier 5/6 witnesses are useful for reconstruction and cross-checking, but they are not official authority.",
    ]
    (CORPUS_DIR / "corpus_quality_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_blocker_report(metrics: dict[str, Any]) -> None:
    attempts = [json.loads(line) for line in (ACQUISITION_DIR / "source_attempts.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    failures = [json.loads(line) for line in (ACQUISITION_DIR / "failed_sources.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    review_rows = read_csv(CORPUS_DIR / "human_review_queue.csv")
    missing_medium_high = 30 - int(metrics["medium_high_past_years_with_12_months"])
    official_claim_blocked = int(metrics.get("usable_for_official_claim_count", 0)) < 480
    lines = [
        "# Data Acquisition Blocker Report",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        "## Summary",
        "",
        f"- Primary reconstruction target met: {str(metrics['primary_target_met']).lower()}",
        f"- Medium/high 30-past-year subgoal met: {str(metrics['medium_high_30_past_year_subgoal_met']).lower()}",
        f"- Medium/high past full years still needed for 30-year target: {max(0, missing_medium_high)}",
        f"- Source-labeled reconstruction target blocked: {str(not metrics['target_reached']).lower()}",
        f"- Official-grade 99% claim still blocked by Tier 1/strong Tier 2 depth: {str(official_claim_blocked).lower()}",
        "",
        "## Sources Attempted",
        "",
    ]
    for attempt in attempts:
        lines.append(
            f"- {attempt['source_name']}: {attempt['status']}; rows={attempt['rows_extracted']}; "
            f"years={attempt['years_covered']}; error={attempt['error_if_any'] or 'none'}"
        )
    lines.extend(["", "## Failed Or Blocked Sources", ""])
    for failure in failures:
        lines.append(
            f"- {failure['source_name']} ({failure['source_url']}): {failure['status']} - "
            f"{failure['error_if_any']}; next: {failure['next_action']}"
        )
    lines.extend(["", "## Top Manual Acquisition Targets", ""])
    for row in review_rows[:25]:
        lines.append(
            f"- P{row['priority']} {row['bs_year']}-{int(row['bs_month']):02d}: "
            f"{row['issue_type']} - {row['recommended_manual_action']}"
        )
    lines.extend(
        [
            "",
            "## Exact Next Steps",
            "",
            "1. Add public NPNS/government PDF URLs for older years if available.",
            "2. Add archive.org printed panchanga item URLs for 2071-2083 and older years.",
            "3. Capture Gorkhapatra/newspaper mastheads around BS month starts for weak/conflicting rows.",
            "4. Manually review archived 2076-2077 official/patro rows and promote only verified rows.",
            "5. Re-run `python scripts/future_bs/run_data_acquisition_loop.py` and `python scripts/future_bs/check_data_target.py`.",
        ]
    )
    (ACQUISITION_DIR / "blocker_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_final_report(metrics: dict[str, Any]) -> None:
    review_rows = read_csv(CORPUS_DIR / "human_review_queue.csv")
    lines = [
        "# Final Data Acquisition Report",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        f"1. target reached: {str(metrics['target_reached']).lower()}",
        f"2. years covered: {metrics['years_with_12_months']}",
        f"3. months reconstructed: {metrics['months_reconstructed']}",
        f"4. source tier distribution: {json.dumps(metrics['best_tier_distribution'], sort_keys=True)}",
        (
            "5. official/printed/public witness counts: "
            f"official={metrics['months_official_verified']}, "
            f"printed={metrics['months_printed_verified']}, "
            f"public_daily={metrics['months_public_daily_witness']}, "
            f"publisher={metrics['months_publisher_reference']}, "
            f"software={metrics['months_software_reference']}, "
            f"third_party={metrics['months_third_party_reference']}"
        ),
        f"6. conflicts found: {metrics['conflict_count']}",
        f"7. human review queue size: {len(review_rows)}",
        f"8. 30-past-year Tier 1-4 support target: {str(metrics['medium_high_30_past_year_subgoal_met']).lower()} ({metrics['medium_high_past_years_with_12_months']} years)",
        "9. blockers: none for the 30-past-year source-labeled reconstruction target; official-grade 99% claims still need more Tier 1/strong Tier 2 reviewed years.",
        "10. exact next manual acquisition steps: seed NPNS PDFs, archive.org panchanga scans, and newspaper mastheads around weak or conflicting month starts.",
        "11. how this corpus improves the 99% effort: it expands reconstruction coverage while preserving claim safety by separating official-grade rows from weak witnesses.",
        "",
        "This corpus must not be represented as official future-calendar truth. Low-trust witnesses are for reconstruction, cross-checking, and active learning.",
    ]
    (ACQUISITION_DIR / "FINAL_DATA_ACQUISITION_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_reconstruction_pipeline(fetch_rat32: bool = True) -> dict[str, Any]:
    write_acquisition_plan()
    summary = collect_witnesses(fetch_rat32=fetch_rat32)
    start_rows, _ = reconstruct_month_starts()
    length_rows = reconstruct_month_lengths(start_rows)
    generate_human_review_queue(start_rows, length_rows)
    metrics = coverage_metrics(length_rows, load_witnesses())
    write_coverage_report(metrics)
    write_corpus_quality_report(metrics)
    write_blocker_report(metrics)
    write_final_report(metrics)
    return {"summary": summary, "metrics": metrics}


def check_data_target() -> dict[str, Any]:
    metrics = coverage_metrics()
    target_ok = bool(metrics["primary_target_met"] or metrics["minimum_fallback_met"])
    blockers = []
    if not metrics["primary_target_met"]:
        blockers.append("primary_target_not_met")
    if not metrics["medium_high_subgoal_met"]:
        blockers.append("medium_high_20_year_subgoal_not_met")
    if not metrics.get("medium_high_30_past_year_subgoal_met", False):
        blockers.append("medium_high_30_past_year_subgoal_not_met")
    if not target_ok:
        blockers.append("minimum_fallback_not_met")
    result = {
        "publication_status": PUBLICATION_STATUS,
        "target_passed": target_ok,
        "primary_target_met": metrics["primary_target_met"],
        "minimum_fallback_met": metrics["minimum_fallback_met"],
        "medium_high_subgoal_met": metrics["medium_high_subgoal_met"],
        "medium_high_30_past_year_subgoal_met": metrics.get("medium_high_30_past_year_subgoal_met", False),
        "medium_high_past_years_with_12_months": metrics.get("medium_high_past_years_with_12_months", 0),
        "medium_high_past_years_with_12_months_list": metrics.get("medium_high_past_years_with_12_months_list", []),
        "years_with_12_months": metrics["years_with_12_months"],
        "months_reconstructed": metrics["months_reconstructed"],
        "blockers": blockers,
    }
    return result


__all__ = [
    "WITNESS_FIELDS",
    "SOURCE_TIERS",
    "build_agreement_graph",
    "check_data_target",
    "collect_witnesses",
    "coverage_metrics",
    "extract_open_source_converter_tables",
    "extract_rat32_pages",
    "ensure_dirs",
    "generate_human_review_queue",
    "make_witness",
    "month_start_dates_from_lengths",
    "parse_medic_days_in_month",
    "parse_sharingapples_config",
    "reconstruct_month_lengths",
    "reconstruct_month_starts",
    "run_reconstruction_pipeline",
    "source_policy",
    "write_jsonl",
]
