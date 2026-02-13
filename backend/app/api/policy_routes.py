"""Policy metadata endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.policy import get_policy_metadata


router = APIRouter(prefix="/api/policy", tags=["policy"])


@router.get("")
@router.get("/")
async def get_policy():
    return {
        "policy": get_policy_metadata(),
    }
