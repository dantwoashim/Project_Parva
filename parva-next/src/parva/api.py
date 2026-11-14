"""HTTP adapter for the calendar package. Run with ``uvicorn parva.api:app``."""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any, Literal
from zoneinfo import ZoneInfo

from fastapi import APIRouter, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, JSONResponse

from . import VERSION, bs, festivals, holidays, lunar, review
from .astro import KATHMANDU, NPT
from .evidence import read_data
from .ical import calendar_feed

router = APIRouter(prefix="/v1")


def ok(data: Any, source: str) -> dict[str, Any]:
    return {"data": data, "source": source, "version": VERSION}


def bs_dict(value: bs.BS) -> dict[str, Any]:
    return {
        "year": value.year,
        "month": value.month,
        "day": value.day,
        "text": str(value),
        "month_name": value.month_name,
        "month_name_ne": value.month_name_ne,
        "nepali": value.nepali(),
    }


@router.get("/convert")
def convert(ad: date | None = None, bs_date: Annotated[str | None, Query(alias="bs")] = None) -> dict[str, Any]:
    if (ad is None) == (bs_date is None):
        raise ValueError("Supply exactly one of ad or bs.")
    value = bs.to_bs(ad) if ad is not None else bs.parse(bs_date or "")
    return ok(
        {"ad": value.ad.isoformat(), "weekday": value.ad.strftime("%A"), "bs": bs_dict(value)}, ",".join(value.sources)
    )


@router.get("/today")
def today() -> dict[str, Any]:
    return convert(ad=datetime.now(NPT).date())


@router.get("/valid")
def valid(bs_date: Annotated[str, Query(alias="bs")]) -> dict[str, Any]:
    year, month, day = (int(part) for part in bs_date.split("-"))
    maximum = bs.month_days(year, month)
    return ok(
        {"bs": bs_date, "valid": 1 <= day <= maximum, "max_day": maximum}, ",".join(bs.BS(year, month, 1).sources)
    )


@router.get("/month/{year}/{month}")
def month(year: int, month: int) -> dict[str, Any]:
    count = bs.month_days(year, month)
    first, last = bs.to_ad(year, month, 1), bs.to_ad(year, month, count)
    rows = [
        row
        for row in holidays.of_year(year, "all")
        if date.fromisoformat(row["ad"]) <= last and date.fromisoformat(row["ad"]) + timedelta(days=row["days"]) > first
    ]
    return ok(
        {
            "bs_year": year,
            "month": month,
            "name": bs.NAMES[month - 1],
            "days": count,
            "start_ad": first.isoformat(),
            "end_ad": last.isoformat(),
            "start_weekday": first.weekday(),
            "holidays": rows,
            "coverage": holidays.coverage(year),
        },
        ",".join(bs.BS(year, month, 1).sources),
    )


@router.get("/holidays/{bs_year}.ics")
def holidays_ics(bs_year: int, scope: str = "national") -> Response:
    bs.month_days(bs_year, 1)
    return Response(calendar_feed(bs_year, scope), media_type="text/calendar; charset=utf-8")


@router.get("/holidays/{bs_year}")
def year_holidays(bs_year: int, scope: str = "national") -> dict[str, Any]:
    bs.month_days(bs_year, 1)
    return ok(holidays.of_year(bs_year, scope), holidays.source(bs_year) or "none")


@router.get("/coverage/{bs_year}")
def coverage(bs_year: int) -> dict[str, Any]:
    bs.month_days(bs_year, 1)
    return ok(
        {
            "year": bs_year,
            "coverage": holidays.coverage(bs_year),
            "note": holidays.coverage_note(bs_year),
            "scopes": holidays.scopes(),
        },
        holidays.source(bs_year) or "none",
    )


@router.get("/working-day")
def working_day(ad: date, weekend: Literal["sat", "fri-sat"] = "sat", scope: str = "national") -> dict[str, Any]:
    selected = holidays.FRIDAY_SATURDAY if weekend == "fri-sat" else holidays.SATURDAY
    result = holidays.evaluate(ad, weekend=selected, scope=scope)
    following = holidays.next_working_day(ad, weekend=selected, scope=scope)
    return ok(
        {
            "ad": ad.isoformat(),
            "bs": str(bs.to_bs(ad)),
            "working": result.working,
            "status": result.status,
            "reason": result.reason,
            "weekend": result.weekend,
            "holidays": result.holidays,
            "coverage": result.coverage,
            "next_working_day": following.isoformat() if following else None,
            "gazette_covers_year": result.coverage == "complete",
        },
        result.source or "none",
    )


@router.get("/fiscal-year")
def fiscal(ad: date) -> dict[str, Any]:
    year, start, end = holidays.fiscal_year(ad)
    return ok(
        {"fiscal_year": f"{year}/{(year + 1) % 100:02d}", "start": start.isoformat(), "end": end.isoformat()},
        ",".join(bs.to_bs(ad).sources),
    )


def festival_row(value: festivals.Occurrence) -> dict[str, Any]:
    return {
        **value.as_dict(),
        "name": festivals.INFO.get(value.id, {}).get("name", value.id),
        "name_ne": festivals.INFO.get(value.id, {}).get("name_nepali"),
    }


@router.get("/festivals")
def list_festivals(year: int | None = None) -> dict[str, Any]:
    values = festivals.in_year(year if year is not None else datetime.now(NPT).year)
    return ok([festival_row(value) for value in values if value.id in festivals.INFO], "mixed")


@router.get("/upcoming")
def upcoming(ad: date, count: Annotated[int, Query(ge=1, le=100)] = 6) -> dict[str, Any]:
    return ok(
        [festival_row(value) for value in festivals.upcoming(ad, 100) if value.id in festivals.INFO][:count], "mixed"
    )


@router.get("/festivals/{fid}")
def festival(fid: str, year: int | None = None) -> dict[str, Any]:
    if fid not in festivals.RULES:
        raise HTTPException(404, f"Unknown festival {fid!r}.")
    value = festivals.occurrence(fid, year if year is not None else datetime.now(NPT).year)
    return ok({**festivals.INFO.get(fid, {"id": fid}), "rule": festivals.RULES[fid], **value.as_dict()}, value.source)


@router.get("/panchanga")
def panchanga(
    ad: date,
    lat: Annotated[float, Query(ge=-90, le=90)] = KATHMANDU[1],
    lon: Annotated[float, Query(ge=-180, le=180)] = KATHMANDU[0],
    tz: str = "Asia/Kathmandu",
) -> dict[str, Any]:
    value = bs.to_bs(ad)
    try:
        zone = ZoneInfo(tz)
    except KeyError:
        raise ValueError(f"Unknown time zone {tz!r}.") from None
    data = lunar.panchanga(ad, (lon, lat, 0.0), zone)
    return ok({**data, "bs": bs_dict(value)}, "computed")


@router.get("/audit/{year}")
def audit(year: int) -> dict[str, Any]:
    rows = festivals.audit(year)
    compared = sum(1 for value in festivals.in_year(year) if value.gazette and value.engine)
    return ok(
        {"year": year, "compared": compared, "agree": compared - len(rows), "disagreements": rows},
        "gazette-vs-computed",
    )


@router.post("/check")
async def check(
    request: Request,
    column: str | None = None,
    force_bs: Annotated[bool, Query(alias="bs")] = False,
    scope: str = "national",
) -> dict[str, Any]:
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > review.MAX_CSV_BYTES:
            raise HTTPException(413, "CSV exceeds the 1 MiB limit.")
    try:
        text = body.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("CSV must be UTF-8 encoded.") from None
    rows = review.review(review.read_dates(text, column), force_bs=force_bs, scope=scope)
    return ok({"rows": rows, "to_review": sum(bool(row["flags"] or row["error"]) for row in rows)}, "per-row")


@router.get("/sources")
def sources() -> dict[str, Any]:
    return ok(
        {"sources": read_data("SOURCES.json"), "release": read_data("release.json"), "data_sha256": bs.DATA_SHA256},
        "self",
    )


def create_app(web_dist: Path | None = None) -> FastAPI:
    app = FastAPI(title="Parva", version=VERSION, description="The Nepali calendar, with its sources.")
    app.include_router(router)

    @app.exception_handler(ValueError)
    async def invalid_input(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    dist = (
        web_dist or Path(os.environ.get("PARVA_WEB_DIST") or Path(__file__).resolve().parents[2] / "web/dist")
    ).resolve()
    if (dist / "index.html").is_file():

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str) -> FileResponse:
            target = (dist / path).resolve()
            if not target.is_relative_to(dist) or path == "v1" or path.startswith("v1/"):
                raise HTTPException(404, "Not found")
            if target.is_file():
                return FileResponse(target, media_type="image/webp" if target.suffix == ".webp" else None)
            if Path(path).suffix:
                raise HTTPException(404, "Not found")
            return FileResponse(dist / "index.html")

    return app


app = create_app()
