"""Extract legacy OCR candidates into a new review directory. Never updates release data.

Usage: python tools/import_legacy.py --output-dir /path/to/new/candidates

Candidates require source-page review before promotion. Weekday agreement alone
does not establish the date span, scope, closure status or completeness.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ---------------------------------------------------------------- gazette vocabulary
BS_MONTHS_NE = {
    "वैशाख": 1,
    "बैशाख": 1,
    "जेठ": 2,
    "जेष्ठ": 2,
    "असार": 3,
    "आषाढ": 3,
    "साउन": 4,
    "श्रावण": 4,
    "भदौ": 5,
    "भाद्र": 5,
    "असोज": 6,
    "आश्विन": 6,
    "कात्तिक": 7,
    "कार्तिक": 7,
    "मंसिर": 8,
    "मङ्सिर": 8,
    "पुस": 9,
    "पौष": 9,
    "माघ": 10,
    "फागुन": 11,
    "फाल्गुन": 11,
    "चैत": 12,
    "चैत्र": 12,
}
WEEKDAYS_NE = {  # Python weekday(): Monday = 0
    "सोमबार": 0,
    "मङ्गलबार": 1,
    "मंगलबार": 1,
    "बुधबार": 2,
    "बिहीबार": 3,
    "शुक्रबार": 4,
    "शनिबार": 5,
    "आइतबार": 6,
}
DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")

# (regex on the gazette name, holiday id, scope).  First match wins.
# scope is Parva's classification of the gazette's grouping; the gazette text is kept verbatim.
HOLIDAY_IDS: list[tuple[str, str, str]] = [
    (r"नव वर्ष", "bs-new-year", "national"),
    (r"गणतन्त्र", "republic-day", "national"),
    (r"बुद्ध|वैशाखरपूर्णिमा", "buddha-jayanti", "national"),
    (r"रक्षाबन्धन", "janai-purnima", "national"),
    (r"जन्माष्टमी", "krishna-janmashtami", "national"),
    (r"घटस्थापना", "ghatasthapana", "national"),
    (r"दशैँ बिदा|दशैं बिदा", "dashain-holidays", "national"),
    (r"तिहार बिदा", "tihar-holidays", "national"),
    (r"लक्ष्मी", "laxmi-puja", "national"),
    (r"गाई तिहार", "gai-tihar", "national"),
    (r"भाइ", "bhai-tika", "national"),
    (r"छठ", "chhath", "national"),
    (r"संविधान", "constitution-day", "national"),
    (r"तमु|तमू", "tamu-lhosar", "national"),
    (r"सोनम|सोनाम", "sonam-lhosar", "national"),
    (r"ग्याल्पो|ल्होसार", "gyalpo-lhosar", "national"),
    (r"शिवरात्री", "shivaratri", "national"),
    (r"वसन्त पञ्चमी", "saraswati-puja", "national"),
    (r"रामनवमी", "ram-navami", "national"),
    (r"पृथ्वी|एकता", "prithvi-jayanti", "national"),
    (r"जेनजी", "genz-martyrs-day", "national"),
    (r"शहीद|सहिद", "martyrs-day", "national"),
    (r"प्रजातन्त्र", "democracy-day", "national"),
    (r"जन युद्ध", "peoples-war-day", "national"),
    (r"डिसेम्बर|^२५\)", "christmas", "national"),
    (r"गुरु नानक", "guru-nanak-jayanti", "community:sikh"),
    (r"हरितालिका|तीज", "teej", "women"),
    (r"महिला दिवस", "womens-day", "women"),
    (r"जितिया", "jitiya", "women"),
    (r"गाईजात्रा", "gai-jatra", "community:newar"),
    (r"इन्द्रजात्रा", "indra-jatra", "kathmandu-valley"),
    (r"घोडेजात्रा", "ghode-jatra", "kathmandu-valley"),
    (r"योमरी|ज्याप", "yomari-punhi", "community:newar"),
    (r"उभौली", "ubhauli", "community:kirat"),
    (r"उधौली", "udhauli", "community:kirat"),
    (r"गोरा|गौरा", "gaura-parva", "region:sudurpaschim"),
    (r"फागुनन्द", "falgunanda-jayanti", "community:kirat"),
    (r"दुरा", "dura-mhaipru-nakuma", "community:dura"),
    (r"निजामती", "civil-service-day", "civil-service"),
]
NAMES_EN = {
    "bs-new-year": "Nepali New Year",
    "republic-day": "Republic Day",
    "buddha-jayanti": "Buddha Jayanti",
    "janai-purnima": "Janai Purnima / Rakshabandhan",
    "krishna-janmashtami": "Krishna Janmashtami",
    "ghatasthapana": "Ghatasthapana",
    "dashain-holidays": "Dashain holidays",
    "tihar-holidays": "Tihar holidays",
    "laxmi-puja": "Laxmi Puja",
    "gai-tihar": "Gai Tihar",
    "bhai-tika": "Bhai Tika",
    "chhath": "Chhath",
    "constitution-day": "Constitution Day",
    "tamu-lhosar": "Tamu Lhosar",
    "sonam-lhosar": "Sonam Lhosar",
    "gyalpo-lhosar": "Gyalpo Lhosar",
    "shivaratri": "Maha Shivaratri",
    "saraswati-puja": "Basanta Panchami / Saraswati Puja",
    "ram-navami": "Ram Navami",
    "prithvi-jayanti": "Prithvi Jayanti / National Unity Day",
    "genz-martyrs-day": "Gen Z Martyrs' Day",
    "martyrs-day": "Martyrs' Day",
    "democracy-day": "National Democracy Day",
    "peoples-war-day": "People's War Day",
    "christmas": "Christmas",
    "guru-nanak-jayanti": "Guru Nanak Jayanti",
    "teej": "Haritalika Teej",
    "womens-day": "International Women's Day",
    "jitiya": "Jitiya",
    "gai-jatra": "Gai Jatra",
    "indra-jatra": "Indra Jatra",
    "ghode-jatra": "Ghode Jatra",
    "yomari-punhi": "Yomari Punhi",
    "ubhauli": "Ubhauli",
    "udhauli": "Udhauli",
    "gaura-parva": "Gaura Parva",
    "falgunanda-jayanti": "Falgunanda Jayanti",
    "dura-mhaipru-nakuma": "Dura Mhaipru Nakuma",
    "civil-service-day": "Civil Service Day",
}


# ---------------------------------------------------------------- bs_months.json
LAST_YEAR = 2095  # legacy 2096 sums to 364 days (impossible); 2097/2099 disagree with nepali-datetime. Not shipped.
ROW_FIXES = {
    # legacy row sums to 367 days (impossible).  nepali-datetime 1.0.8.5 has Mangsir = 29 (366 days).
    2087: [31, 31, 32, 31, 31, 31, 30, 29, 30, 30, 30, 30],
}


def build_bs_months(legacy: Path) -> dict:
    ns: dict = {}
    src = (legacy / "backend/app/calendar/constants.py").read_text("utf-8")
    exec(src.split("# Minimum and maximum supported years")[0], {"date": date}, ns)
    exec(re.search(r"BS_REFERENCE_START = .*\nBS_REFERENCE_YEAR = .*", src).group(0), {"date": date}, ns)
    table = {y: ROW_FIXES.get(y, m) for y, m in ns["BS_MONTH_LENGTHS"].items() if y <= LAST_YEAR}
    bad = {y: sum(m) for y, m in table.items() if len(m) != 12 or sum(m) not in (365, 366)}
    assert not bad, f"impossible BS years: {bad}"
    return {
        "version": "2083.1",
        "anchor": {
            "bs": [ns["BS_REFERENCE_YEAR"], 1, 1],
            "ad": ns["BS_REFERENCE_START"].isoformat(),
            "source": "moha-2082",
        },
        "months": {str(y): m for y, m in sorted(table.items())},
        "sources": [
            {"years": [2078, 2083], "sources": ["moha-gazette-weekdays", "doib-2082", "table-2000-2095"]},
            {"years": [2000, 2077], "sources": ["table-2000-2095"]},
            {"years": [2084, LAST_YEAR], "sources": ["table-provisional"]},
        ],
    }


class Table:
    """Just enough BS<->AD to convert gazette rows; the real thing lives in parva/bs.py."""

    def __init__(self, data: dict) -> None:
        self.months = {int(y): m for y, m in data["months"].items()}
        (ay, _, _), ad = data["anchor"]["bs"], date.fromisoformat(data["anchor"]["ad"])
        self.start = {ay: ad}
        for y in range(ay + 1, max(self.months) + 1):
            self.start[y] = self.start[y - 1] + timedelta(days=sum(self.months[y - 1]))
        for y in range(ay - 1, min(self.months) - 1, -1):
            self.start[y] = self.start[y + 1] - timedelta(days=sum(self.months[y]))

    def to_ad(self, y: int, m: int, d: int) -> date:
        if not 1 <= d <= self.months[y][m - 1]:
            raise ValueError(f"BS {y}-{m:02d}-{d:02d} does not exist")
        return self.start[y] + timedelta(days=sum(self.months[y][: m - 1]) + d - 1)


# ---------------------------------------------------------------- holidays/<year>.json
GAZETTE_DATE = re.compile(r"([\u0900-\u097F]+)\s+(\d{1,3})\s*(?:गते|wd)")  # "<month> <day> गते"


def classify(name_raw: str) -> tuple[str, str] | None:
    name = re.sub(r"^\([^)]{1,3}\)\.?\s*", "", name_raw).strip()  # drop the "(क)" enumerator only
    for pattern, hid, scope in HOLIDAY_IDS:
        if re.search(pattern, name):
            return hid, scope
    return None


def build_holidays(legacy: Path, table: Table, bs_year: int, log: list[str]) -> dict | None:
    path = legacy / f"data/ingest_reports/holidays_{bs_year}_matched.csv"
    if not path.exists():
        return None
    days: dict[tuple[str, str], dict] = {}
    for row in csv.DictReader(path.open(encoding="utf-8")):
        line = row["line"].translate(DEVANAGARI_DIGITS)
        found = classify(row["name_raw"])
        m = GAZETTE_DATE.search(line)
        if not found or not m or m.group(1) not in BS_MONTHS_NE:
            log.append(f"{bs_year}: skipped (unparsed) {row['line']!r}")
            continue
        month, day = BS_MONTHS_NE[m.group(1)], int(m.group(2))
        try:
            ad = table.to_ad(bs_year, month, day)
        except (KeyError, ValueError) as exc:
            log.append(f"{bs_year}: skipped ({exc}) {row['line']!r}")
            continue
        printed = next((v for k, v in WEEKDAYS_NE.items() if k in row["line"]), None)
        if printed is not None and printed != ad.weekday():
            log.append(f"{bs_year}: REJECTED weekday mismatch {row['line']!r} -> {ad} is {ad:%A}")
            continue
        hid, scope = found
        entry = {
            "id": hid,
            "name": NAMES_EN[hid],
            "bs": f"{bs_year:04d}-{month:02d}-{day:02d}",
            "ad": ad.isoformat(),
            "days": 1,
            "scope": scope,
            "weekday_verified": printed is not None,
            "text": row["line"].strip(),
        }
        if "देखि" in line:  # "from <date> ... until <date>": a multi-day block
            end = re.search(r"देखि\s*(?:([\u0900-\u097F]+)\s+)?(\d{1,2})", line)
            if end:
                end_month = BS_MONTHS_NE.get(end.group(1) or "", month)
                entry["days"] = (table.to_ad(bs_year, end_month, int(end.group(2))) - ad).days + 1
            else:
                log.append(f"{bs_year} {hid}: missing end date; excluded")
                continue
        entry["review"] = "pending"
        days.setdefault((hid, entry["ad"]), entry)
    return {
        "bs_year": bs_year,
        "source": f"moha-{bs_year}",
        "scope_note": "scope is Parva's classification of the gazette's grouping; `text` is the gazette line itself",
        "days": sorted(days.values(), key=lambda e: e["ad"]),
    }


# ---------------------------------------------------------------- SOURCES.json
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_sources(legacy: Path, years: list[int]) -> dict:
    sources = {
        "table-2000-2095": {
            "title": "Community BS month-length table, BS 2000-2095",
            "note": "Identical to nepali-datetime 1.0.8.5 for every shipped year except 2087 (see below); identical "
            "to nepali-date-converter 3.4.0 and nepali-date-library 1.1.15 on 2078-2083 (legacy "
            "public-benchmark/results/competitor-comparison.md). Anchored 2082-01-01 BS = 2025-04-14 AD. "
            "Legacy rows 2096-2099 are not shipped: 2096 sums to 364 days; 2097/2099 disagree between sources.",
        },
        "table-provisional": {
            "title": "Same table, years 2084-2095",
            "note": "Not yet published by Nepal Panchanga Nirnayak Bikas Samiti; expect one-day changes in some "
            "months. 2087 uses the nepali-datetime row (366 days) because the legacy row summed to 367.",
        },
        "moha-gazette-weekdays": {
            "title": "Weekday checksum of MoHA gazette lines against the table",
            "note": "Every dated line in the MoHA public-holiday notices names a weekday. "
            "tools/import_legacy.py converts each line with the table and keeps it only if the weekdays agree.",
        },
        "doib-2082": {
            "title": "Department of Information and Broadcasting table calendar, BS 2082",
            "url": "https://giwmscdnone.gov.np/media/pdf_upload/Table%20calendar%202082_Final_kngovbv.pdf",
        },
        "computed": {
            "title": "Swiss Ephemeris (Moshier), Lahiri ayanamsa, upper-limb sunrise, amanta months named by "
            "sankranti, purnimanta festival rules, udaya/aparahna/pradosh/nishita anchoring (parva/lunar.py)",
        },
    }
    for y in years:
        pdf = legacy / f"data/source_archive/moha/{y}_public_holidays.pdf"
        if pdf.exists():
            sources[f"moha-{y}"] = {
                "title": f"Ministry of Home Affairs, Government of Nepal - public holiday notice, BS {y}",
                "sha256": sha256(pdf),
                "size_bytes": pdf.stat().st_size,
                "note": "OCR'd in the legacy repository (data/ingest_reports); each row re-verified by weekday here.",
            }
    return sources


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--legacy", type=Path, default=HERE.parent.parent)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    legacy = args.legacy.resolve()
    output = args.output_dir.resolve()
    if output.is_relative_to(HERE.parent / "src"):
        ap.error("Candidate output cannot be inside the runtime source tree.")
    log: list[str] = []
    output.mkdir(parents=True, exist_ok=False)
    (output / "holidays").mkdir(exist_ok=True)

    bs_months = build_bs_months(legacy)
    write(output / "bs_months.json", bs_months)
    table = Table(bs_months)

    years = []
    for y in range(2070, 2100):
        payload = build_holidays(legacy, table, y, log)
        if payload and payload["days"]:
            write(output / "holidays" / f"{y}.json", payload)
            years.append(y)
            print(f"holidays/{y}.json  {len(payload['days']):3d} rows")

    festivals = json.loads((legacy / "data/festivals/festivals.json").read_text("utf-8"))
    write(output / "festivals.json", festivals)
    write(output / "SOURCES.json", build_sources(legacy, years))

    print("\n".join(log), file=sys.stderr)
    print(f"\n{len(log)} rows skipped or rejected (see stderr).  Data written to {output}")
    return 0


def write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
