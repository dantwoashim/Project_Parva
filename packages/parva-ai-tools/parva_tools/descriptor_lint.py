"""Descriptor linting for public-safe Parva AI tool wrappers."""

from __future__ import annotations

from .schemas import TOOL_SPECS, ParvaToolSpec

UNSAFE_AUTHORITY_PHRASES = (
    "official future",
    "government approved",
    "legal authority",
    "banking authority",
    "payroll authority",
    "tax authority",
    "religious authority",
    "guaranteed future",
)


def lint_tool_descriptors(specs: tuple[ParvaToolSpec, ...] = TOOL_SPECS) -> list[str]:
    issues: list[str] = []
    for spec in specs:
        description = spec.description.lower()
        for phrase in UNSAFE_AUTHORITY_PHRASES:
            if phrase in description:
                issues.append(f"{spec.name}: unsafe authority phrase `{phrase}`")
        descriptor = spec.descriptor()
        if descriptor.get("read_only") is not True:
            issues.append(f"{spec.name}: descriptor must be read-only")
        if "claim_boundary" not in descriptor.get("output_contract", ()):
            issues.append(f"{spec.name}: descriptor must include claim_boundary output")
        if descriptor.get("authority_boundary") is None:
            issues.append(f"{spec.name}: descriptor must include authority_boundary")
    return issues


def assert_tool_descriptors_safe(specs: tuple[ParvaToolSpec, ...] = TOOL_SPECS) -> None:
    issues = lint_tool_descriptors(specs)
    if issues:
        raise ValueError("; ".join(issues))
