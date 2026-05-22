#!/usr/bin/env python3
"""Detect import cycles in Project Parva Python packages."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _module_name(path: Path, root: Path) -> str:
    relative = path.relative_to(root).with_suffix("")
    parts = relative.parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(("app", *parts))


def _known_modules(root: Path) -> dict[str, Path]:
    return {_module_name(path, root): path for path in root.rglob("*.py") if "__pycache__" not in path.parts}


def _resolve_import_from(current: str, node: ast.ImportFrom, known: set[str]) -> str | None:
    if node.level:
        parts = current.split(".")
        package_parts = parts[:-1]
        if node.level > len(package_parts) + 1:
            return None
        base = package_parts[: len(package_parts) - node.level + 1]
        if node.module:
            base.extend(node.module.split("."))
        target = ".".join(base)
    else:
        target = node.module or ""
    if target in known:
        return target
    for alias in node.names:
        candidate = f"{target}.{alias.name}" if target else alias.name
        if candidate in known:
            return candidate
    return None


def _resolve_import(name: str, known: set[str]) -> str | None:
    parts = name.split(".")
    for index in range(len(parts), 0, -1):
        candidate = ".".join(parts[:index])
        if candidate in known:
            return candidate
    return None


def build_graph(root: Path) -> dict[str, set[str]]:
    known_map = _known_modules(root)
    known = set(known_map)
    graph: dict[str, set[str]] = {module: set() for module in known}
    for module, path in known_map.items():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            raise SystemExit(f"{path.relative_to(PROJECT_ROOT)}: Python parse failed: {exc.msg}") from exc
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target = _resolve_import(alias.name, known)
                    if target and target != module:
                        graph[module].add(target)
            elif isinstance(node, ast.ImportFrom):
                target = _resolve_import_from(module, node, known)
                if target and target != module:
                    graph[module].add(target)
    return graph


def _cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    visiting: list[str] = []
    visited: set[str] = set()
    emitted: set[tuple[str, ...]] = set()

    def canonical(cycle: list[str]) -> tuple[str, ...]:
        body = cycle[:-1]
        rotations = [tuple(body[index:] + body[:index]) for index in range(len(body))]
        return min(rotations)

    def visit(node: str) -> None:
        if node in visiting:
            start = visiting.index(node)
            cycle = [*visiting[start:], node]
            key = canonical(cycle)
            if key not in emitted:
                emitted.add(key)
                cycles.append(cycle)
            return
        if node in visited:
            return
        visiting.append(node)
        for target in sorted(graph.get(node, ())):
            visit(target)
        visiting.pop()
        visited.add(node)

    for node in sorted(graph):
        visit(node)
    return cycles


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    root = (PROJECT_ROOT / (argv[0] if argv else "backend/app")).resolve()
    graph = build_graph(root)
    cycles = _cycles(graph)
    if cycles:
        for cycle in cycles:
            print(" -> ".join(cycle))
        return 1
    print(f"No import cycles found under {root.relative_to(PROJECT_ROOT).as_posix()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
