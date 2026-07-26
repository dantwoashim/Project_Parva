"""Compatibility helpers for inspecting routes registered with FastAPI."""

from __future__ import annotations

from collections.abc import Iterable, Iterator


def iter_registered_routes(routes: Iterable[object]) -> Iterator[object]:
    """Yield effective routes across flattened and grouped FastAPI registries."""
    for route in routes:
        effective_contexts = getattr(route, "effective_route_contexts", None)
        if callable(effective_contexts):
            yield from effective_contexts()
            continue

        if isinstance(getattr(route, "path", None), str):
            yield route
