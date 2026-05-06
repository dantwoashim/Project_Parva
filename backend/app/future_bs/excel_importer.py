"""Import InfoDevelopers-style month-length CSV/XLSX files."""

from __future__ import annotations

import base64
import csv
import io
import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

MONTH_COUNT = 12


def _rows_from_csv_bytes(data: bytes) -> list[list[str]]:
    text = data.decode("utf-8-sig")
    return [row for row in csv.reader(io.StringIO(text)) if row]


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        raw = archive.read("xl/sharedStrings.xml")
    except KeyError:
        return []
    root = ElementTree.fromstring(raw)
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    strings = []
    for item in root.findall("x:si", ns):
        text = "".join(node.text or "" for node in item.findall(".//x:t", ns))
        strings.append(text)
    return strings


def _rows_from_xlsx_bytes(data: bytes) -> list[list[str]]:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        strings = _shared_strings(archive)
        root = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rows: list[list[str]] = []
    for row in root.findall(".//x:row", ns):
        values: list[str] = []
        for cell in row.findall("x:c", ns):
            value = cell.find("x:v", ns)
            raw = value.text if value is not None else ""
            if cell.attrib.get("t") == "s" and raw:
                raw = strings[int(raw)]
            values.append(raw or "")
        if any(values):
            rows.append(values)
    return rows


def _normalize_rows(rows: list[list[str]]) -> list[dict[str, Any]]:
    parsed: list[dict[str, Any]] = []
    for row in rows:
        numeric = [int(value) for value in row if re.fullmatch(r"\d+", str(value).strip())]
        if len(numeric) < 13:
            continue
        bs_year = numeric[0]
        months = numeric[1:13]
        if all(29 <= days <= 32 for days in months):
            parsed.append({"bs_year": bs_year, "months": months})
    if not parsed:
        raise ValueError("No valid rows found. Expected bs_year plus 12 month lengths.")
    return parsed


def import_month_lengths_bytes(data: bytes, file_format: str) -> list[dict[str, Any]]:
    if file_format == "csv":
        rows = _rows_from_csv_bytes(data)
    elif file_format == "xlsx":
        rows = _rows_from_xlsx_bytes(data)
    else:
        raise ValueError("file_format must be csv or xlsx.")
    return _normalize_rows(rows)


def import_month_lengths_base64(content_base64: str, file_format: str) -> list[dict[str, Any]]:
    return import_month_lengths_bytes(base64.b64decode(content_base64), file_format)


def import_month_lengths_file(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower().lstrip(".")
    file_format = "xlsx" if suffix == "xlsx" else "csv"
    return import_month_lengths_bytes(path.read_bytes(), file_format)
