#!/usr/bin/env python3
"""
Festival Date Evaluator for Project Parva v2.0

Compares calculated festival dates against ground truth sources.
Generates evaluation.csv with pass/fail results and discrepancy analysis.

Usage:
    python evaluate.py
    python evaluate.py --output evaluation.csv
    python evaluate.py --year 2026 --verbose
"""

import csv
import json
import argparse
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Ground truth test cases (expanded from sources.json)
# Each case: (festival_id, expected_date, source, notes)
TEST_CASES_2026 = [
    # SOLAR FESTIVALS (fixed dates)
    ("maghe-sankranti", "2026-01-14", "nepal_gov", "Makara Sankranti, Sun enters Makara"),
    ("bs-new-year", "2026-04-14", "nepal_gov", "Mesh Sankranti, Baishakh 1"),
    
    # LUNAR FESTIVALS - Major
    ("shivaratri", "2026-02-14", "moha_pdf_2082", "Falgun 3 (MoHA 2082)"),
    ("holi", "2026-03-03", "nepal_gov", "Falgun Purnima"),
    ("buddha-jayanti", "2026-05-12", "nepal_gov", "Baisakh Purnima"),
    ("janai-purnima", "2026-08-11", "nepal_gov", "Shrawan Purnima"),
    ("teej", "2026-08-30", "nepal_gov", "Bhadra Shukla 3"),
    ("indra-jatra", "2026-09-08", "nepal_gov", "Yenya Punhi begins"),
    
    # DASHAIN (multi-day)
    ("dashain", "2026-10-10", "nepal_gov", "Ghatasthapana, Ashwin Shukla 1"),
    
    # TIHAR (multi-day)
    ("tihar", "2026-11-07", "nepal_gov", "Kaag Tihar, Kartik Krishna 14"),
    
    # Additional lunar festivals
    ("gai-jatra", "2026-08-12", "nepal_gov", "Day after Janai Purnima"),
    ("yomari-punhi", "2026-12-25", "estimated", "Poush Purnima"),
    ("mha-puja", "2026-11-11", "estimated", "Nepal Sambat New Year"),
    
    # Regional/Lunar
    ("chhath", "2026-11-12", "estimated", "Kartik Shukla 6"),
    ("ghode-jatra", "2026-03-18", "estimated", "Chaitra Krishna 15"),
    
    # Additional 2027 projections for test coverage
    ("maghe-sankranti", "2027-01-14", "estimated", "Makara Sankranti 2027"),
    ("shivaratri", "2027-03-05", "estimated", "Falgun Krishna 14 2027"),
    ("holi", "2027-03-22", "estimated", "Falgun Purnima 2027"),
    
    # 2025 retrospective (MoHA 2082 PDF)
    ("dashain", "2025-09-23", "moha_pdf_2082", "Ghatasthapana 2082 BS"),
    ("tihar", "2025-10-20", "moha_pdf_2082", "Tihar holiday start 2082 BS"),
]

MONTH_VARIANTS = {
    "वैशाख": 1,
    "बैशाख": 1,
    "वेशाख": 1,
    "जेठ": 2,
    "असार": 3,
    "आषाढ": 3,
    "साउन": 4,
    "श्रावण": 4,
    "सावन": 4,
    "भदौ": 5,
    "भाद्र": 5,
    "असोज": 6,
    "आश्विन": 6,
    "अशोज": 6,
    "कात्तिक": 7,
    "कार्तिक": 7,
    "कातिक": 7,
    "मङ्सिर": 8,
    "मंसिर": 8,
    "पुस": 9,
    "पौष": 9,
    "माघ": 10,
    "फागुन": 11,
    "फाल्गुन": 11,
    "चैत": 12,
    "चैत्र": 12,
}


def load_moha_matched_tests(report_dir: Path) -> List[Tuple[str, str, str, str]]:
    """
    Load OCR-matched MoHA entries and convert BS -> Gregorian.
    Returns list of (festival_id, expected_date, source, notes).
    """
    from app.calendar.bikram_sambat import bs_to_gregorian

    tests: List[Tuple[str, str, str, str]] = []
    seen = set()
    by_festival_year: Dict[Tuple[str, int], List[Tuple[str, str, str]]] = {}

    for csv_path in sorted(report_dir.glob("holidays_*_matched.csv")):
        stem = csv_path.stem
        year_match = None
        for token in stem.split("_"):
            if token.isdigit() and len(token) == 4:
                year_match = int(token)
                break
        if not year_match:
            continue

        with csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                festival_id = (row.get("match_id") or "").strip()
                month_raw = (row.get("month_raw") or "").strip()
                day_raw = (row.get("day_raw") or "").strip()
                name_raw = (row.get("name_raw") or "").strip()
                if not festival_id or not month_raw or not day_raw:
                    continue
                month_num = MONTH_VARIANTS.get(month_raw)
                if not month_num:
                    continue
                try:
                    day_num = int(day_raw.translate(str.maketrans("०१२३४५६७८९", "0123456789")))
                except ValueError:
                    continue
                try:
                    g_date = bs_to_gregorian(year_match, month_num, day_num)
                except Exception:
                    continue
                key = (festival_id, year_match)
                by_festival_year.setdefault(key, []).append(
                    (g_date.isoformat(), f"moha_pdf_{year_match}", name_raw)
                )

    # Keep only unambiguous entries (single distinct date per festival/year)
    for (festival_id, year_match), items in by_festival_year.items():
        unique_dates = {d for d, _, _ in items}
        if len(unique_dates) != 1:
            continue
        g_date = unique_dates.pop()
        key = (festival_id, g_date)
        if key in seen:
            continue
        seen.add(key)
        _, source, name_raw = items[0]
        tests.append(
            (
                festival_id,
                g_date,
                source,
                f"{name_raw} (BS {year_match})",
            )
        )

    return tests

@dataclass
class EvaluationResult:
    """Result of evaluating a single festival date."""
    festival_id: str
    year: int
    expected_date: str
    calculated_date: Optional[str]
    passed: bool
    variance_days: int
    source: str
    notes: str
    error: str = ""


def evaluate_festival(
    festival_id: str,
    expected_date_str: str,
    source: str,
    notes: str,
    acceptable_variance: int = 1,
    use_overrides: bool = True
) -> EvaluationResult:
    """
    Evaluate a single festival date calculation.
    
    Args:
        festival_id: Festival identifier
        expected_date_str: Expected date in YYYY-MM-DD format
        source: Ground truth source
        notes: Additional notes
        acceptable_variance: Days of variance allowed (default 1)
    
    Returns:
        EvaluationResult with pass/fail and details
    """
    from app.calendar.calculator_v2 import calculate_festival_v2
    
    expected = datetime.strptime(expected_date_str, "%Y-%m-%d").date()
    year = expected.year
    
    try:
        result = calculate_festival_v2(festival_id, year, use_overrides=use_overrides)
        if result is None:
            raise ValueError("No calculation result")
        calculated = result.start_date
        
        variance = abs((calculated - expected).days)
        passed = variance <= acceptable_variance
        
        return EvaluationResult(
            festival_id=festival_id,
            year=year,
            expected_date=expected_date_str,
            calculated_date=calculated.isoformat(),
            passed=passed,
            variance_days=variance,
            source=source,
            notes=notes
        )
    except Exception as e:
        return EvaluationResult(
            festival_id=festival_id,
            year=year,
            expected_date=expected_date_str,
            calculated_date=None,
            passed=False,
            variance_days=-1,
            source=source,
            notes=notes,
            error=str(e)
        )
    except KeyError:
        return EvaluationResult(
            festival_id=festival_id,
            year=year,
            expected_date=expected_date_str,
            calculated_date=None,
            passed=False,
            variance_days=-1,
            source=source,
            notes=notes,
            error=f"Unknown festival: {festival_id}"
        )
    except Exception as e:
        return EvaluationResult(
            festival_id=festival_id,
            year=year,
            expected_date=expected_date_str,
            calculated_date=None,
            passed=False,
            variance_days=-1,
            source=source,
            notes=notes,
            error=str(e)
        )


def run_evaluation(
    test_cases: List[Tuple] = TEST_CASES_2026,
    acceptable_variance: int = 1,
    verbose: bool = False,
    use_overrides: bool = True,
    include_moha: bool = True
) -> List[EvaluationResult]:
    """
    Run full evaluation suite.
    
    Args:
        test_cases: List of (festival_id, expected_date, source, notes)
        acceptable_variance: Days of variance allowed
        verbose: Print progress
    
    Returns:
        List of EvaluationResult
    """
    if include_moha:
        report_dir = PROJECT_ROOT / "data" / "ingest_reports"
        if report_dir.exists():
            test_cases = list(test_cases) + load_moha_matched_tests(report_dir)

    results = []
    
    for i, (fid, expected, source, notes) in enumerate(test_cases):
        if verbose:
            print(f"[{i+1}/{len(test_cases)}] Evaluating {fid}...", end=" ")
        
        result = evaluate_festival(
            fid,
            expected,
            source,
            notes,
            acceptable_variance,
            use_overrides=use_overrides
        )
        results.append(result)
        
        if verbose:
            status = "✅" if result.passed else "❌"
            if result.calculated_date:
                print(f"{status} (expected {expected}, got {result.calculated_date}, Δ={result.variance_days}d)")
            else:
                print(f"{status} ERROR: {result.error}")
    
    return results


def save_csv(results: List[EvaluationResult], output_path: str = "evaluation.csv"):
    """Save results to CSV."""
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "festival_id", "year", "expected_date", "calculated_date",
            "passed", "variance_days", "source", "notes", "error"
        ])
        
        for r in results:
            writer.writerow([
                r.festival_id,
                r.year,
                r.expected_date,
                r.calculated_date or "",
                "PASS" if r.passed else "FAIL",
                r.variance_days,
                r.source,
                r.notes,
                r.error
            ])
    
    print(f"Results saved to {output_path}")


def print_summary(results: List[EvaluationResult]):
    """Print evaluation summary."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total}")
    print(f"Passed:      {passed} ({100*passed/total:.1f}%)")
    print(f"Failed:      {failed}")
    print()
    
    if failed > 0:
        print("FAILURES:")
        for r in results:
            if not r.passed:
                if r.error:
                    print(f"  - {r.festival_id} ({r.year}): ERROR - {r.error}")
                else:
                    print(f"  - {r.festival_id} ({r.year}): expected {r.expected_date}, got {r.calculated_date} (Δ={r.variance_days}d)")
    
    print("=" * 60)


def generate_discrepancy_report(results: List[EvaluationResult]) -> str:
    """Generate markdown discrepancy analysis."""
    failures = [r for r in results if not r.passed]
    
    md = "# Discrepancy Analysis\n\n"
    md += f"**Evaluation Date**: {date.today().isoformat()}\n\n"
    md += f"**Total Cases**: {len(results)}  \n"
    md += f"**Passed**: {len(results) - len(failures)}  \n"
    md += f"**Failed**: {len(failures)}\n\n"
    
    if not failures:
        md += "## ✅ All Tests Passed\n\n"
        md += "No discrepancies detected. All calculated dates match ground truth within acceptable variance (±1 day).\n"
    else:
        md += "## ❌ Failed Cases\n\n"
        md += "| Festival | Year | Expected | Calculated | Variance | Source | Error |\n"
        md += "|----------|------|----------|------------|----------|--------|-------|\n"
        
        for r in failures:
            md += f"| {r.festival_id} | {r.year} | {r.expected_date} | {r.calculated_date or 'N/A'} | {r.variance_days}d | {r.source} | {r.error or 'variance'} |\n"
        
        md += "\n### Analysis\n\n"
        
        # Categorize failures
        errors = [r for r in failures if r.error]
        variances = [r for r in failures if not r.error]
        
        if errors:
            md += f"**Calculation Errors**: {len(errors)} cases where calculation failed\n\n"
            for r in errors:
                md += f"- `{r.festival_id}` ({r.year}): {r.error}\n"
        
        if variances:
            md += f"\n**Variance Failures**: {len(variances)} cases outside acceptable range\n\n"
            for r in variances:
                md += f"- `{r.festival_id}` ({r.year}): {r.variance_days} day(s) off\n"
    
    return md


def main():
    parser = argparse.ArgumentParser(description="Evaluate festival date calculations")
    parser.add_argument("--output", "-o", default="evaluation.csv", help="Output CSV path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--variance", "-d", type=int, default=1, help="Acceptable variance in days")
    parser.add_argument("--no-overrides", action="store_true", help="Disable authoritative overrides")
    parser.add_argument("--no-moha", action="store_true", help="Disable MoHA OCR-based test expansion")
    args = parser.parse_args()
    
    print("Festival Date Evaluator v1.0")
    extra = 0
    if not args.no_moha:
        report_dir = PROJECT_ROOT / "data" / "ingest_reports"
        if report_dir.exists():
            extra = len(load_moha_matched_tests(report_dir))
    print(f"Running {len(TEST_CASES_2026) + extra} test cases...\n")
    
    results = run_evaluation(
        test_cases=TEST_CASES_2026,
        acceptable_variance=args.variance,
        verbose=args.verbose,
        use_overrides=not args.no_overrides,
        include_moha=not args.no_moha
    )
    
    print_summary(results)
    save_csv(results, args.output)
    
    # Generate discrepancy report
    report = generate_discrepancy_report(results)
    report_path = Path(args.output).with_suffix(".md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Discrepancy report saved to {report_path}")


if __name__ == "__main__":
    main()
