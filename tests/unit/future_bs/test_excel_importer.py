from __future__ import annotations

import pytest
from app.research.future_bs.excel_importer import _parse_xlsx_xml, import_month_lengths_bytes


def test_import_month_lengths_csv_parses_valid_rows():
    payload = b"2083,31,31,32,31,31,31,30,29,30,29,30,30\n"

    assert import_month_lengths_bytes(payload, "csv") == [
        {"bs_year": 2083, "months": [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]}
    ]


def test_xlsx_xml_parser_rejects_dtd_and_entities():
    with pytest.raises(ValueError, match="DTD or entity"):
        _parse_xlsx_xml(b"<!DOCTYPE x [<!ENTITY e 'boom'>]><x>&e;</x>")
