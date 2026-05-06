"""CSV and XLSX exports for future BS predictions."""

from __future__ import annotations

import csv
import io
import math
import zipfile
from typing import Any
from xml.sax.saxutils import escape

from app.calendar.constants import BS_MONTH_NAMES


def predictions_to_csv(start: int, end: int, *, range_fn) -> str:
    rows = range_fn(start, end)["years"]
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "bs_year",
            *[name.lower() for name in BS_MONTH_NAMES],
            "year_total",
            "confidence",
            "method_version",
            "notes",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row["bs_year"],
                *row["months"],
                row["year_total"],
                row["confidence"],
                row["method_version"],
                ";".join(row["risk_flags"]) or "none",
            ]
        )
    return buffer.getvalue()


def _excel_cell(column_index: int, row_index: int) -> str:
    letters = ""
    index = column_index
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return f"{letters}{row_index}"


def _xlsx_sheet_xml(rows: list[list[Any]]) -> str:
    xml_rows: list[str] = []
    for row_index, row in enumerate(rows, start=1):
        cells: list[str] = []
        for column_index, value in enumerate(row, start=1):
            reference = _excel_cell(column_index, row_index)
            if isinstance(value, int | float) and not isinstance(value, bool) and not math.isnan(float(value)):
                cells.append(f'<c r="{reference}"><v>{value}</v></c>')
            else:
                cells.append(
                    f'<c r="{reference}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
                )
        xml_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(xml_rows)}</sheetData>'
        "</worksheet>"
    )


def predictions_to_xlsx(start: int, end: int, *, range_fn) -> bytes:
    rows_payload = range_fn(start, end)["years"]
    rows: list[list[Any]] = [
        [
            "bs_year",
            *[name.lower() for name in BS_MONTH_NAMES],
            "year_total",
            "confidence",
            "method_version",
            "notes",
        ]
    ]
    for row in rows_payload:
        rows.append(
            [
                row["bs_year"],
                *row["months"],
                row["year_total"],
                row["confidence"],
                row["method_version"],
                ";".join(row["risk_flags"]) or "none",
            ]
        )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                "</Types>"
            ),
        )
        archive.writestr(
            "_rels/.rels",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                "</Relationships>"
            ),
        )
        archive.writestr(
            "xl/workbook.xml",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                "<sheets><sheet name=\"Future BS\" sheetId=\"1\" r:id=\"rId1\"/></sheets>"
                "</workbook>"
            ),
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                "</Relationships>"
            ),
        )
        archive.writestr("xl/worksheets/sheet1.xml", _xlsx_sheet_xml(rows))
    return buffer.getvalue()
