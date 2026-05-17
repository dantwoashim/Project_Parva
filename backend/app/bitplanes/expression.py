"""Simple bitplane expression evaluation."""

from __future__ import annotations


def and_planes(*planes: tuple[bool, ...]) -> tuple[bool, ...]:
    if not planes:
        return ()
    return tuple(all(values) for values in zip(*planes, strict=True))
