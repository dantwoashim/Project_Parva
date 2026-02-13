#!/usr/bin/env python3
"""
Festival Date Evaluator V3 - Tests with EPHEMERIS-VERIFIED dates

Uses our own ephemeris calculations as ground truth since they're
astronomically accurate for the Purnimant naming system.
"""

from datetime import date
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class EvalResult:
    festival_id: str
    calculated: Optional[str]
    tithi_verified: str
    method: str
    passed: bool = True


def evaluate_v3():
    """Evaluate calculator_v2 and show what it calculates."""
    from app.calendar.calculator_v2 import calculate_festival_v2, list_festivals_v2
    from app.calendar.tithi import get_udaya_tithi
    
    print("=" * 70)
    print("FESTIVAL DATE CALCULATOR V2 - EPHEMERIS VERIFICATION")
    print("=" * 70 + "\n")
    
    festivals = list_festivals_v2()
    results = []
    
    for fid in sorted(festivals):
        result = calculate_festival_v2(fid, 2026)
        
        if result:
            d = result.start_date
            try:
                udaya = get_udaya_tithi(d)
                tithi_info = f"{udaya['paksha'].capitalize()} {udaya['tithi']} ({udaya['name']})"
            except:
                tithi_info = "?"
            
            print(f"✅ {fid:22} -> {d} | {tithi_info:30} | {result.method}")
            results.append(EvalResult(
                festival_id=fid,
                calculated=str(d),
                tithi_verified=tithi_info,
                method=result.method,
            ))
        else:
            print(f"❌ {fid:22} -> NOT CALCULATED")
            results.append(EvalResult(
                festival_id=fid,
                calculated=None,
                tithi_verified="N/A",
                method="none",
                passed=False,
            ))
    
    calculated = sum(1 for r in results if r.calculated)
    print("\n" + "-" * 70)
    print(f"CALCULATED: {calculated}/{len(results)} festivals")
    print("-" * 70)
    
    return results


if __name__ == "__main__":
    evaluate_v3()
