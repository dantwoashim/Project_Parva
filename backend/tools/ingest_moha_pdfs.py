#!/usr/bin/env python3
"""
Ingest MoHA holiday PDFs (scanned) into ground_truth_overrides.json.

Pipeline:
1) Convert PDF pages to images (pdftoppm)
2) OCR with tesseract (nep+eng)
3) Parse holiday lines: "<name> - <month> <day> गते"
4) Map Nepali names to festival IDs (high-precision mapping)
5) Convert BS dates to Gregorian and merge into overrides

Outputs:
- data/ingest_reports/holidays_<bs_year>_parsed.csv
- data/ingest_reports/holidays_<bs_year>_matched.csv
- Updates backend/app/calendar/ground_truth_overrides.json
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from app.calendar.bikram_sambat import bs_to_gregorian

PROJECT_ROOT = Path(__file__).resolve().parents[2]

NEPALI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


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


def canonical(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[\-–—:|।,]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    # Remove list markers like "(क)" or "क)" or "a)"
    text = re.sub(r"^\(?[क-ह]\)?\s*", "", text)
    text = re.sub(r"^[a-z]\)\s*", "", text)
    text = text.replace("बिदा", " ").replace("विदा", " ")
    text = text.replace("पर्व", " ").replace("व्रत", " ")
    text = text.replace("जयन्ती", " ").replace("जयंती", " ")
    text = text.replace("दिवस", " ").replace("पूजा", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"\s+", "", text)


FESTIVAL_MAP = {
    canonical("नव वर्ष"): "bs-new-year",
    canonical("नयाँ वर्ष"): "bs-new-year",
    canonical("बुद्ध जयन्ती"): "buddha-jayanti",
    canonical("बुद्ध जयंती"): "buddha-jayanti",
    canonical("चण्डी पूर्णिमा"): "buddha-jayanti",
    canonical("वैशाख पूर्णिमा"): "buddha-jayanti",
    canonical("रक्षाबन्धन"): "janai-purnima",
    canonical("रक्षा बन्धन"): "janai-purnima",
    canonical("जनै पूर्णिमा"): "janai-purnima",
    canonical("श्रीकृष्ण जन्माष्टमी"): "krishna-janmashtami",
    canonical("कृष्ण जन्माष्टमी"): "krishna-janmashtami",
    canonical("घटस्थापना"): "dashain",
    canonical("दशैं"): "dashain",
    canonical("तिहार बिदा"): "tihar",
    canonical("तिहार"): "tihar",
    canonical("छठ पर्व"): "chhath",
    canonical("तमू ल्होछार"): "tamu-lhosar",
    canonical("तमू ल्होसार"): "tamu-lhosar",
    canonical("तमु ल्होसार"): "tamu-lhosar",
    canonical("सोनम ल्होछार"): "sonam-lhosar",
    canonical("सोनम ल्होसार"): "sonam-lhosar",
    canonical("ग्याल्पो ल्होसार"): "gyalpo-lhosar",
    canonical("माघी पर्व"): "maghe-sankranti",
    canonical("माघी पर्ब"): "maghe-sankranti",
    canonical("माघे संक्रान्ति"): "maghe-sankranti",
    canonical("माघे सङ्क्रान्ति"): "maghe-sankranti",
    canonical("महाशिवरात्री"): "shivaratri",
    canonical("रामनवमी"): "ram-navami",
    canonical("गाईजात्रा"): "gai-jatra",
    canonical("इन्द्रजात्रा"): "indra-jatra",
    canonical("घोडेजात्रा"): "ghode-jatra",
    canonical("हरितालिका तीज"): "teej",
    canonical("हरितालिका (तीज) व्रत"): "teej",
    canonical("वसन्त पञ्चमी"): "saraswati-puja",
    canonical("सरस्वती पूजा"): "saraswati-puja",
    canonical("उभौली पर्व"): "ubhauli",
    canonical("उधौली पर्व"): "udhauli",
}


MONTH_PATTERN = "|".join(sorted(MONTH_VARIANTS.keys(), key=len, reverse=True))
LINE_RE = re.compile(
    rf"^(.*?)\s*[-–—]\s*({MONTH_PATTERN})\s*([०-९0-9]+)\s*गते"
)
LINE_RE_FUZZY = re.compile(
    rf"^(.*?)\s*[-–—]\s*({MONTH_PATTERN})\s*([०-९0-9]+)"
)

CONFIDENCE_ORDER = {"high": 3, "medium": 2, "low": 1}


@dataclass
class HolidayEntry:
    bs_year: int
    name_raw: str
    month_raw: str
    day_raw: str
    month_num: int
    day_num: int
    line: str
    matched_id: Optional[str] = None
    parse_confidence: str = "high"


def _is_nepali_numeric(text: str) -> bool:
    return bool(re.fullmatch(r"[०-९]+", text))


def _score_parse_confidence(name_raw: str, month_raw: str, day_raw: str, fuzzy: bool) -> str:
    score = 3
    if fuzzy:
        score -= 1
    if not _is_nepali_numeric(day_raw):
        # OCR often emits ASCII digits; still parseable but less reliable.
        score -= 1
    if month_raw not in MONTH_VARIANTS:
        score -= 1
    if len(name_raw) < 3:
        score -= 1
    if score >= 3:
        return "high"
    if score == 2:
        return "medium"
    return "low"


def parse_bs_year_from_filename(path: Path) -> Optional[int]:
    text = path.name.translate(NEPALI_DIGITS)
    m = re.search(r"(20[0-9]{2})", text)
    return int(m.group(1)) if m else None


def ocr_pdf_to_text(pdf_path: Path, tmp_dir: Path) -> str:
    prefix = tmp_dir / "page"
    subprocess.run(
        ["pdftoppm", "-r", "300", "-png", str(pdf_path), str(prefix)],
        check=True,
    )
    parts: List[str] = []
    for img in sorted(tmp_dir.glob("page-*.png")):
        out_base = tmp_dir / img.stem
        subprocess.run(
            ["tesseract", str(img), str(out_base), "-l", "nep+eng", "--psm", "6"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        txt_path = out_base.with_suffix(".txt")
        if txt_path.exists():
            parts.append(txt_path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def normalize_ocr_text(text: str) -> str:
    """
    Second-pass OCR correction:
    - Fix common Nepali OCR substitutions
    - Normalize month spellings
    - Remove stray ASCII noise between day and weekday
    """
    # Normalize month spellings
    replacements = {
        "वेशाख": "वैशाख",
        "बैशाख": "वैशाख",
        "श्रावण": "साउन",
        "सावन": "साउन",
        "भाद्र": "भदौ",
        "आश्विन": "असोज",
        "अशोज": "असोज",
        "कार्तिक": "कात्तिक",
        "कातिक": "कात्तिक",
        "मंसिर": "मङ्सिर",
        "पौष": "पुस",
        "फाल्गुन": "फागुन",
        "चैत्र": "चैत",
        # Common OCR mistakes in festival names
        "कशक्ष्मी": "लक्ष्मी",
        "ल्होसार": "ल्होसार",
        "ल्होछार": "ल्होछार",
        "सङक्रान्ति": "सङ्क्रान्ति",
        "संक्रान्ति": "सङ्क्रान्ति",
        "तिहारबिदा": "तिहार बिदा",
        "जनयुद्ध": "जन युद्ध",
        "जयन्ती": "जयंती",
        "ल्हो सार": "ल्होसार",
        "ल्हो छार": "ल्होछार",
        "ंग्सिर": "मङ्सिर",
        "मसिर": "मंसिर",
        "भदो": "भदौ",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)

    # Remove stray ASCII fragments between day and weekday
    weekdays = "(सोमबार|मंगलबार|मङ्गलबार|बुधबार|बिहीबार|शुक्रबार|शनिबार|आइतबार)"
    text = re.sub(rf"(\\d)\\s*[A-Za-z]{{1,3}}\\s*{weekdays}", r"\\1 \\2", text)
    text = text.replace("O", "०").replace("o", "०")

    return text


def extract_entries(text: str, bs_year: int) -> List[HolidayEntry]:
    entries: List[HolidayEntry] = []
    for raw in text.splitlines():
        line = raw.strip()
        if "-" not in line:
            continue
        if "गते" not in line and "देखि" not in line:
            continue
        line = re.sub(r"\s+", " ", line)
        line = line.replace("–", "-").replace("—", "-")
        line = re.sub(r"^[\-\s]+", "", line)
        m = LINE_RE.search(line)
        fuzzy = False
        if not m:
            # Allow lines without "गते" if they indicate a range (देखि)
            if "देखि" not in line:
                continue
            m = LINE_RE_FUZZY.search(line)
            if not m:
                continue
            fuzzy = True
        name_raw = m.group(1).strip()
        month_raw = m.group(2).strip()
        day_raw = m.group(3).strip()
        if not name_raw:
            continue
        if month_raw in name_raw:
            continue
        if name_raw in {"दिवस", "दिवस (धान्य पूर्णिमा)"}:
            continue
        day_num = int(day_raw.translate(NEPALI_DIGITS))
        month_num = MONTH_VARIANTS[month_raw]
        parse_confidence = _score_parse_confidence(name_raw, month_raw, day_raw, fuzzy)
        entries.append(
            HolidayEntry(
                bs_year=bs_year,
                name_raw=name_raw,
                month_raw=month_raw,
                day_raw=day_raw,
                month_num=month_num,
                day_num=day_num,
                line=line,
                parse_confidence=parse_confidence,
            )
        )
    return entries


def map_entries(entries: List[HolidayEntry]) -> None:
    for entry in entries:
        if "बिदा" in entry.name_raw and "तिहार" not in entry.name_raw:
            entry.matched_id = None
            entry.parse_confidence = "low"
            continue
        key = canonical(entry.name_raw)
        entry.matched_id = FESTIVAL_MAP.get(key)
        if entry.matched_id is None and entry.parse_confidence == "high":
            entry.parse_confidence = "medium"


def deduplicate_entries(entries: List[HolidayEntry]) -> List[HolidayEntry]:
    """
    Remove duplicate OCR rows while preserving best-confidence candidates.
    """
    # Pass 1: exact duplicates by canonical text + date
    exact: Dict[Tuple[int, int, int, str], HolidayEntry] = {}
    for entry in entries:
        key = (entry.bs_year, entry.month_num, entry.day_num, canonical(entry.name_raw))
        prev = exact.get(key)
        if prev is None or CONFIDENCE_ORDER[entry.parse_confidence] > CONFIDENCE_ORDER[prev.parse_confidence]:
            exact[key] = entry

    # Pass 2: collapse multiple rows mapping to same festival+date.
    by_festival: Dict[Tuple[int, str, int, int], HolidayEntry] = {}
    leftovers: List[HolidayEntry] = []
    for entry in exact.values():
        if not entry.matched_id:
            leftovers.append(entry)
            continue
        key = (entry.bs_year, entry.matched_id, entry.month_num, entry.day_num)
        prev = by_festival.get(key)
        if prev is None or CONFIDENCE_ORDER[entry.parse_confidence] > CONFIDENCE_ORDER[prev.parse_confidence]:
            by_festival[key] = entry

    return list(by_festival.values()) + leftovers


def write_csv(path: Path, entries: Iterable[HolidayEntry], matched: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if matched:
            writer.writerow(
                [
                    "bs_year",
                    "name_raw",
                    "month_raw",
                    "day_raw",
                    "match_id",
                    "parse_confidence",
                    "line",
                ]
            )
            for e in entries:
                writer.writerow([e.bs_year, e.name_raw, e.month_raw, e.day_raw, e.matched_id or "", e.parse_confidence, e.line])
        else:
            writer.writerow(["bs_year", "name_raw", "month_raw", "day_raw", "parse_confidence", "line"])
            for e in entries:
                writer.writerow([e.bs_year, e.name_raw, e.month_raw, e.day_raw, e.parse_confidence, e.line])


def merge_overrides(
    overrides_path: Path,
    entries: List[HolidayEntry],
    source_tag: str,
    dry_run: bool = False,
) -> int:
    overrides = json.loads(overrides_path.read_text())
    # Remove known bad OCR-derived entries
    for year, data in list(overrides.items()):
        if year.startswith("_"):
            continue
        if "buddha-jayanti" in data:
            notes = data["buddha-jayanti"].get("notes", "")
            if "जनयुद्ध" in notes:
                del data["buddha-jayanti"]
    added = 0
    # Resolve conflicts on same (gregorian year, festival_id) by confidence.
    selected: Dict[Tuple[str, str], HolidayEntry] = {}
    for e in entries:
        if not e.matched_id:
            continue
        try:
            g_date = bs_to_gregorian(e.bs_year, e.month_num, e.day_num)
        except Exception:
            continue
        key = (str(g_date.year), e.matched_id)
        prev = selected.get(key)
        if prev is None or CONFIDENCE_ORDER[e.parse_confidence] > CONFIDENCE_ORDER[prev.parse_confidence]:
            selected[key] = e

    for e in selected.values():
        g_date = bs_to_gregorian(e.bs_year, e.month_num, e.day_num)
        g_year = str(g_date.year)
        overrides.setdefault(g_year, {})
        current = overrides[g_year].get(e.matched_id)
        if current and current.get("confidence") == "official":
            continue
        overrides[g_year][e.matched_id] = {
            "start": g_date.isoformat(),
            "source": source_tag,
            "confidence": "official",
            "notes": (
                f"BS {e.bs_year}-{e.month_num:02d}-{e.day_num:02d} "
                f"({e.month_raw} {e.day_raw}) {e.name_raw} "
                f"[ocr_confidence={e.parse_confidence}]"
            ),
        }
        added += 1
    if not dry_run:
        overrides_path.write_text(json.dumps(overrides, ensure_ascii=False, indent=2))
    return added


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        default=str(PROJECT_ROOT / "data"),
        help="Directory containing MoHA PDF files",
    )
    parser.add_argument(
        "--overrides",
        default=str(PROJECT_ROOT / "backend" / "app" / "calendar" / "ground_truth_overrides.json"),
        help="Path to ground_truth_overrides.json",
    )
    parser.add_argument(
        "--reports-dir",
        default=str(PROJECT_ROOT / "data" / "ingest_reports"),
        help="Directory to write parsed/matched CSVs",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    overrides_path = Path(args.overrides)
    reports_dir = Path(args.reports_dir)

    pdfs = sorted(data_dir.glob("*.pdf"))
    if not pdfs:
        raise SystemExit("No PDFs found in data directory.")

    total_added = 0
    for pdf in pdfs:
        bs_year = parse_bs_year_from_filename(pdf)
        if not bs_year:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            text = ocr_pdf_to_text(pdf, tmp_dir)
        text = normalize_ocr_text(text)
        entries = extract_entries(text, bs_year)
        map_entries(entries)
        entries = deduplicate_entries(entries)

        parsed_csv = reports_dir / f"holidays_{bs_year}_parsed.csv"
        matched_csv = reports_dir / f"holidays_{bs_year}_matched.csv"
        write_csv(parsed_csv, entries, matched=False)
        write_csv(matched_csv, entries, matched=True)

        added = merge_overrides(
            overrides_path,
            entries,
            source_tag=f"moha_pdf_{bs_year}",
            dry_run=args.dry_run,
        )
        total_added += added

    print(f"Overrides added: {total_added}")


if __name__ == "__main__":
    main()
