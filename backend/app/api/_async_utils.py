"""Async route helpers for isolating synchronous compute."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from fastapi.concurrency import run_in_threadpool

T = TypeVar("T")


async def run_cpu_bound(func: Callable[..., T], /, *args: Any, **kwargs: Any) -> T:
    """Run bounded synchronous compute outside the event loop."""
    return await run_in_threadpool(func, *args, **kwargs)

