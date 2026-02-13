#!/usr/bin/env python3
"""
Ingest Pradhan Law 2082 public holiday table and merge into overrides.

This scrapes the holiday table (English AD dates) and maps known holidays
to internal festival IDs. It will not overwrite existing overrides unless
--force is provided.
"""

import argparse
import re
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional
from html.parser import HTMLParser
import urllib.request


DEFAULT_URL = "https://pradhanlaw.com/publications/list-of-public-holidays-2082-bs-202526-ad"

ROOT = Path(__file__).parent.parent / "app" / "calendar"
OVERRIDES_PATH = ROOT / "ground_truth_overrides.json"


NAME_TO_FESTIVAL = {
    "new year": "bs-new-year",
    "chandi purnima": "buddha-jayanti",
    "buddha jayanti": "buddha-jayanti",
    "rakshya bandhan": "janai-purnima",
    "raksha bandhan": "janai-purnima",
    "gai jatra": "gai-jatra",
    "janmastami": "krishna-janmashtami",
    "krishna janmastami": "krishna-janmashtami",
    "haritalika": "teej",
    "teej": "teej",
    "indra jatra": "indra-jatra",
    "gatasthapana": "dashain",
    "ghatasthapana": "dashain",
    # Avoid mapping multi-day holiday ranges to single festival start
    # Use explicit start-day rows (e.g., Gatasthapana, Kaag Tihar) instead.
    "chhat parwa": "chhath",
    "chhath": "chhath",
    "dhanya purnima": "yomari-punhi",
    "yomari punhi": "yomari-punhi",
    "maghe sankranti": "maghe-sankranti",
    "maghi": "maghe-sankranti",
    "basanta panchami": "saraswati-puja",
    "saraswati": "saraswati-puja",
    "maha shivaratri": "shivaratri",
    "shivaratri": "shivaratri",
    "fagu purnima": "holi",
    "holi": "holi",
    "ghode jatra": "ghode-jatra",
}


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_td = False
        self.current_row: List[str] = []
        self.rows: List[List[str]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "td":
            self.in_td = True

    def handle_endtag(self, tag):
        if tag == "td":
            self.in_td = False
        if tag == "tr":
            if self.current_row:
                self.rows.append([c.strip() for c in self.current_row if c.strip()])
                self.current_row = []

    def handle_data(self, data):
        if self.in_td:
            self.current_row.append(data)


def load_overrides() -> dict:
    if OVERRIDES_PATH.exists():
        with open(OVERRIDES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"_meta": {"description": "Authoritative overrides"}}


def save_overrides(data: dict):
    with open(OVERRIDES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def extract_ad_date(text: str) -> Optional[date]:
    # Match "(April 14, 2025 A.D.)" or "April 14, 2025 A.D."
    m = re.search(r"([A-Za-z]+ \d{1,2}, \d{4})", text)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%B %d, %Y").date()
    except ValueError:
        return None


def map_name_to_festival(name: str) -> Optional[str]:
    name_l = name.lower()
    # Skip ambiguous multi-day holiday rows
    if "holiday" in name_l and ("dashain" in name_l or "tihar" in name_l):
        return None
    for key, fid in NAME_TO_FESTIVAL.items():
        if key in name_l:
            return fid
    return None


def ingest(url: str, force: bool = False):
    html = urllib.request.urlopen(url).read().decode("utf-8", errors="ignore")
    parser = TableParser()
    parser.feed(html)

    overrides = load_overrides()
    added = 0
    skipped = 0

    for row in parser.rows:
        # Expected columns after cleaning: Name, BS date, AD date, Remark
        if len(row) < 3:
            continue
        name = row[0]
        date_text = row[2]
        ad = extract_ad_date(date_text)
        if not ad:
            continue
        fid = map_name_to_festival(name)
        if not fid:
            continue
        year_key = str(ad.year)
        overrides.setdefault(year_key, {})
        if fid in overrides[year_key] and not force:
            # If existing entry lacks source, add it without overriding date
            if isinstance(overrides[year_key][fid], dict) and "source" not in overrides[year_key][fid]:
                overrides[year_key][fid]["source"] = "pradhanlaw_public_holidays_2082"
                overrides[year_key][fid]["confidence"] = "secondary"
                added += 1
            else:
                skipped += 1
            continue
        overrides[year_key][fid] = {
            "start": ad.isoformat(),
            "source": "pradhanlaw_public_holidays_2082",
            "confidence": "secondary"
        }
        added += 1

    save_overrides(overrides)
    print(f"✅ Ingested {added} override(s), skipped {skipped} existing.")


if __name__ == "__main__":
    import json
    parser = argparse.ArgumentParser(description="Ingest Pradhan Law 2082 holiday table")
    parser.add_argument("--url", default=DEFAULT_URL, help="Source URL")
    parser.add_argument("--force", action="store_true", help="Overwrite existing overrides")
    args = parser.parse_args()
    ingest(args.url, force=args.force)
