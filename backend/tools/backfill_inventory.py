#!/usr/bin/env python3
"""Inventory available MoHA PDF years and report coverage gaps."""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
OUT_MD = PROJECT_ROOT / "docs" / "DATA_BACKFILL_INVENTORY.md"

NEP_TO_ASCII = str.maketrans("०१२३४५६७८९", "0123456789")


def extract_bs_year(name: str) -> int | None:
    text = name.translate(NEP_TO_ASCII)
    m = re.search(r"(20[0-9]{2})", text)
    return int(m.group(1)) if m else None


def main() -> None:
    pdfs = sorted(DATA_DIR.glob("*.pdf"))
    years = sorted({extract_bs_year(p.name) for p in pdfs if extract_bs_year(p.name)})

    lines = [
        "# Data Backfill Inventory",
        "",
        f"- PDF files discovered: **{len(pdfs)}**",
        f"- BS years discovered: **{', '.join(map(str, years)) if years else 'none'}**",
        "",
    ]

    if years:
        min_y, max_y = min(years), max(years)
        expected = set(range(min_y, max_y + 1))
        missing = sorted(expected - set(years))
        lines += [
            f"- Continuous range scanned: `{min_y}-{max_y}`",
            f"- Missing years in range: `{', '.join(map(str, missing)) if missing else 'none'}`",
            "",
            "## Source Files",
            "",
            "| File | Parsed BS Year |",
            "|---|---:|",
        ]

        for p in pdfs:
            lines.append(f"| {p.name} | {extract_bs_year(p.name) or '-'} |")
    else:
        lines.append("No year-identifiable PDF files found.")

    lines += [
        "",
        "## Next Steps",
        "",
        "1. Add archived MoHA PDFs for missing years to improve overlap coverage.",
        "2. Re-run OCR ingest + normalization after each new source addition.",
        "",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
