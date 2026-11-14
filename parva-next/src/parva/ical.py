"""RFC 5545 export of source-reviewed closures only."""

from datetime import date, timedelta

from . import VERSION, holidays
from .evidence import read_data


def escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )


def fold(line: str) -> str:
    """Fold on UTF-8 octet boundaries, including the continuation space."""
    parts: list[str] = []
    current = ""
    for char in line:
        if len((current + char).encode("utf-8")) > 75:
            parts.append(current)
            current = " "
        current += char
    return "\r\n".join([*parts, current])


def calendar_feed(year: int, scope: str = "national") -> str:
    stamp = read_data("release.json")["reviewed_on"].replace("-", "") + "T000000Z"
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        f"PRODID:-//Parva//{VERSION}//EN",
        f"X-WR-CALNAME:Parva BS {year} — partial holiday calendar",
    ]
    for row in holidays.of_year(year, scope):
        if not row.get("closure", True) or row.get("review") != "source_checked":
            continue
        start = date.fromisoformat(row["ad"])
        description = f"{row['text']}\n{holidays.source(year)}, PDF page {row.get('source_page')}. Partial coverage."
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{row['id']}-{row['ad']}@parva",
                f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{start:%Y%m%d}",
                f"DTEND;VALUE=DATE:{start + timedelta(days=row['days']):%Y%m%d}",
                f"SUMMARY:{escape(row['name'])}",
                f"DESCRIPTION:{escape(description)}",
                "END:VEVENT",
            ]
        )
    return "\r\n".join(fold(line) for line in [*lines, "END:VCALENDAR", ""])
