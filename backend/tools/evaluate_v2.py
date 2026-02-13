#!/usr/bin/env python3
"""
Festival Date Evaluator V2 - Tests the CORRECT lunar month model

This evaluator tests calculator_v2.py which properly handles Adhik Maas.
"""

from datetime import date
from typing import List, Tuple, Optional
from dataclasses import dataclass


# Test cases with expected dates
TEST_CASES_V2 = [
    # (festival_id, expected_date, source, notes)
    
    # SOLAR FESTIVALS
    ("maghe-sankranti", "2026-01-14", "nepal_gov", "Makara Sankranti"),
    ("bs-new-year", "2026-04-14", "nepal_gov", "Mesh Sankranti"),
    
    # MAJOR LUNAR FESTIVALS
    ("shivaratri", "2026-02-15", "nepal_gov", "Falgun Krishna 14"),
    ("holi", "2026-03-03", "nepal_gov", "Falgun Purnima"),
    ("buddha-jayanti", "2026-05-12", "nepal_gov", "Baisakh Purnima"),
    ("janai-purnima", "2026-08-11", "nepal_gov", "Shrawan Purnima"),
    ("teej", "2026-08-30", "nepal_gov", "Bhadra Shukla 3"),
    ("indra-jatra", "2026-09-08", "nepal_gov", "Bhadra Shukla 12"),
    ("dashain", "2026-10-10", "nepal_gov", "Ashwin Shukla 1"),
    ("tihar", "2026-11-07", "nepal_gov", "Kartik Krishna 14"),
    
    # SECONDARY LUNAR FESTIVALS
    ("gai-jatra", "2026-08-12", "nepal_gov", "Shrawan Krishna 1"),
    ("krishna-janmashtami", "2026-08-19", "estimated", "Shrawan Krishna 8"),
    ("nag-panchami", "2026-07-27", "estimated", "Shrawan Shukla 5"),
    ("chhath", "2026-11-12", "estimated", "Kartik Shukla 6"),
    ("mha-puja", "2026-11-11", "estimated", "Nepal Sambat New Year (Mha Puja)"),
    ("bhai-tika", "2026-11-12", "estimated", "Kartik Shukla 2"),
    ("vijaya-dashami", "2026-10-19", "nepal_gov", "Ashwin Shukla 10"),
]


@dataclass
class EvalResult:
    festival_id: str
    expected: str
    calculated: Optional[str]
    variance: int
    passed: bool
    method: str
    error: str = ""


def evaluate_v2(acceptable_variance: int = 1, use_overrides: bool = True) -> List[EvalResult]:
    """Run evaluation using calculator_v2."""
    from app.calendar.calculator_v2 import calculate_festival_v2
    
    results = []
    
    for festival_id, expected_str, source, notes in TEST_CASES_V2:
        expected = date.fromisoformat(expected_str)
        year = expected.year
        
        try:
            result = calculate_festival_v2(festival_id, year, use_overrides=use_overrides)
            
            if result is None:
                results.append(EvalResult(
                    festival_id=festival_id,
                    expected=expected_str,
                    calculated=None,
                    variance=-1,
                    passed=False,
                    method="none",
                    error="No rule found"
                ))
                continue
            
            calculated = result.start_date
            variance = abs((calculated - expected).days)
            passed = variance <= acceptable_variance
            
            results.append(EvalResult(
                festival_id=festival_id,
                expected=expected_str,
                calculated=calculated.isoformat(),
                variance=variance,
                passed=passed,
                method=result.method,
            ))
            
        except Exception as e:
            results.append(EvalResult(
                festival_id=festival_id,
                expected=expected_str,
                calculated=None,
                variance=-1,
                passed=False,
                method="error",
                error=str(e)
            ))
    
    return results


def print_results(results: List[EvalResult]):
    """Print evaluation results."""
    print("\n" + "=" * 70)
    print("FESTIVAL DATE CALCULATOR V2 - EVALUATION")
    print("(Using CORRECT Lunar Month Model)")
    print("=" * 70 + "\n")
    
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    
    for r in results:
        status = "✅" if r.passed else "❌"
        calc = r.calculated or "N/A"
        
        if r.error:
            print(f"{status} {r.festival_id:20} | expected {r.expected} | ERROR: {r.error}")
        else:
            print(f"{status} {r.festival_id:20} | expected {r.expected} | got {calc} | Δ={r.variance}d | {r.method}")
    
    print("\n" + "-" * 70)
    print(f"RESULT: {passed}/{total} passed ({100*passed/total:.0f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    print("-" * 70)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate V2 festival calculator")
    parser.add_argument("--variance", "-d", type=int, default=1, help="Acceptable variance in days")
    parser.add_argument("--no-overrides", action="store_true", help="Disable authoritative overrides")
    args = parser.parse_args()
    results = evaluate_v2(acceptable_variance=args.variance, use_overrides=not args.no_overrides)
    print_results(results)
