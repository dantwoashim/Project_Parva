"""
Offline Package Generator
==========================

Generates self-contained JSON packages for offline use.
No API or internet connection needed after download.

Usage:
    python -m backend.tools.generate_offline --bs-year 2082 --output offline_2082.json
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.calendar.calculator_v2 import calculate_festival_v2, list_festivals_v2
from app.calendar.bikram_sambat import gregorian_to_bs, get_bs_month_name, get_bs_confidence
from app.calendar.tithi.tithi_udaya import get_udaya_tithi
from app.calendar.panchanga import get_panchanga


def generate_festival_package(year: int) -> Dict:
    """Generate all festival dates for a year."""
    festivals = {}
    for fid in list_festivals_v2():
        try:
            result = calculate_festival_v2(fid, year)
            if result:
                festivals[fid] = {
                    "start": result.start_date.isoformat(),
                    "end": result.end_date.isoformat(),
                    "duration": result.duration_days,
                    "method": result.method,
                    "lunar_month": result.lunar_month,
                }
        except Exception:
            continue
    return festivals


def generate_panchanga_package(start_date: date, days: int = 365) -> list:
    """Generate panchanga for N days."""
    entries = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        try:
            panchanga = get_panchanga(d)
            bs_y, bs_m, bs_d = gregorian_to_bs(d)
            entries.append({
                "date": d.isoformat(),
                "bs": {"year": bs_y, "month": bs_m, "day": bs_d, "month_name": get_bs_month_name(bs_m)},
                "tithi": panchanga["tithi"]["name"],
                "nakshatra": panchanga["nakshatra"]["name"],
                "yoga": panchanga["yoga"]["name"],
                "vaara": panchanga["vaara"]["name_english"],
            })
        except Exception:
            entries.append({"date": d.isoformat(), "error": True})
    return entries


def generate_bs_calendar_package(bs_year: int) -> Dict:
    """Generate complete BS calendar for a year."""
    from app.calendar.bikram_sambat import bs_to_gregorian, days_in_bs_month

    months = {}
    for month in range(1, 13):
        try:
            month_days = days_in_bs_month(bs_year, month)
            month_data = {
                "name": get_bs_month_name(month),
                "days": month_days,
                "dates": [],
            }
            for day in range(1, month_days + 1):
                try:
                    greg = bs_to_gregorian(bs_year, month, day)
                    month_data["dates"].append({
                        "bs_day": day,
                        "gregorian": greg.isoformat(),
                    })
                except Exception:
                    break
            months[month] = month_data
        except Exception:
            continue
    return months


def generate_offline_package(bs_year: int, output_path: str = None) -> Dict:
    """Generate complete offline package."""
    greg_year = bs_year - 57  # Approximate

    package = {
        "parva_offline_package": "1.0",
        "bs_year": bs_year,
        "gregorian_year": greg_year,
        "generated": date.today().isoformat(),
        "festivals": generate_festival_package(greg_year),
        "bs_calendar": generate_bs_calendar_package(bs_year),
        "panchanga_sample": generate_panchanga_package(date(greg_year, 1, 1), days=30),
    }

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(package, f, indent=2)

    return package


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate Parva Offline Package")
    parser.add_argument("--bs-year", type=int, default=2082)
    parser.add_argument("--output", type=str, default="offline_package.json")
    args = parser.parse_args()

    package = generate_offline_package(args.bs_year, args.output)
    print(f"Generated offline package for BS {args.bs_year}")
    print(f"  Festivals: {len(package['festivals'])}")
    print(f"  BS months: {len(package['bs_calendar'])}")
    print(f"  Panchanga days: {len(package['panchanga_sample'])}")
    print(f"  Output: {args.output}")


if __name__ == "__main__":
    main()
