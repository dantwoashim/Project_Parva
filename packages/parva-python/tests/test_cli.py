from __future__ import annotations

import pytest
from parva.cli import _split_bs_date, build_parser


def test_cli_parser_accepts_public_commands() -> None:
    parser = build_parser()

    today = parser.parse_args(["--base-url", "https://calendar.example/v3/api", "today"])
    convert = parser.parse_args(["convert", "bs", "2083-01-01"])
    capabilities = parser.parse_args(["capabilities", "future-bs"])

    assert today.base_url == "https://calendar.example/v3/api"
    assert convert.from_calendar == "bs"
    assert capabilities.surface == "future-bs"


def test_split_bs_date_requires_numeric_yyyy_mm_dd() -> None:
    assert _split_bs_date("2083-01-01") == (2083, 1, 1)

    with pytest.raises(Exception):
        _split_bs_date("2083-01")
