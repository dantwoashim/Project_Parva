"""The MCP tools are plain functions over the API route functions."""

import pytest

pytest.importorskip("mcp")
pytest.importorskip("swisseph")
from parva import mcp


def test_convert_tool() -> None:
    out = mcp.convert(ad="2026-04-14")
    assert out["data"]["bs"]["text"] == "2083-01-01"
    assert out["data"]["weekday"] == "Tuesday"


def test_holidays_tool() -> None:
    out = mcp.holidays(bs_year=2083)
    assert any(h["id"] == "dashain-holidays" for h in out["data"])


def test_tools_registered() -> None:
    import asyncio

    tools = asyncio.run(mcp.server.list_tools())
    assert {t.name for t in tools} == {
        "convert",
        "working_day",
        "holidays",
        "festival",
        "festivals",
        "panchanga",
        "audit",
    }
