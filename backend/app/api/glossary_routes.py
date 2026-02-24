"""Bilingual glossary endpoint for explanatory UI."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.services import get_glossary

router = APIRouter(prefix="/api/glossary", tags=["glossary"])


@router.get("")
async def glossary_endpoint(
    domain: str = Query(..., description="panchanga|muhurta|kundali"),
    lang: str = Query("en", description="en|ne"),
):
    try:
        return get_glossary(domain=domain, lang=lang)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
