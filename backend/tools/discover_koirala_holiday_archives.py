#!/usr/bin/env python3
"""
Discover annual holiday posts from the Koirala archive.

This is a lightweight harvesting helper for older public-holiday sources.
It scans archive pages and extracts post links that look like annual holiday
listings or Nepali calendar references.

Usage:
    python backend/tools/discover_koirala_holiday_archives.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = ROOT / "data" / "source_inventory" / "koirala_archive_discovery.json"

ARCHIVE_PAGES = {
    "2011-04": "https://koirala.com.np/content/date/2011/04",
    "2012-04": "https://koirala.com.np/content/date/2012/04",
    "2013-02": "https://koirala.com.np/content/date/2013/02",
    "2014-03": "https://koirala.com.np/content/date/2014/03",
}

ENTRY_RE = re.compile(
    r'<h3 class="entry-title"><a href="(?P<url>https://koirala\.com\.np/content/\d+\.html)"[^>]*>(?P<title>.*?)</a>',
    re.S,
)
TAG_RE = re.compile(r"<[^>]+>")
YEAR_RE = re.compile(r"([०१२३४५६७८९]{4})")
KEYWORDS = (
    "सार्वजनिक बिदा",
    "सार्वजनिक विदा",
    "बिदा",
    "विदा",
    "चाड-पर्व",
    "क्यालेन्डर",
    "पात्रो",
)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub("", text)).strip()


def discover() -> dict:
    results = []

    for archive_key, url in ARCHIVE_PAGES.items():
        with urlopen(url, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")
        for match in ENTRY_RE.finditer(html):
            title = _clean(match.group("title"))
            if not any(keyword in title for keyword in KEYWORDS):
                continue
            year_match = YEAR_RE.search(title)
            results.append(
                {
                    "archive_page": archive_key,
                    "title": title,
                    "url": match.group("url"),
                    "bs_year_hint": year_match.group(1) if year_match else None,
                }
            )

    payload = {
        "_meta": {
            "name": "Koirala Archive Holiday Discovery",
            "archive_pages": list(ARCHIVE_PAGES.values()),
            "result_count": len(results),
        },
        "results": results,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    payload = discover()
    print(f"Wrote {OUTPUT_PATH}")
    print(f"Discovered {payload['_meta']['result_count']} candidate posts")


if __name__ == "__main__":
    main()
