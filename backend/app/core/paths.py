"""Central filesystem path resolver for runtime resources.

Runtime code should not infer the repository root repeatedly. These helpers keep
source-checkout defaults while allowing Docker, packaged installs, and private
deployments to point resources at explicit directories.
"""

from __future__ import annotations

import os
from pathlib import Path


def project_root() -> Path:
    configured = os.getenv("PARVA_PROJECT_ROOT", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[3]


def resolve_resource_path(env_name: str, default_relative: str | Path) -> Path:
    configured = os.getenv(env_name, "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return (project_root() / default_relative).resolve()


def data_dir() -> Path:
    return resolve_resource_path("PARVA_DATA_DIR", "data")


def output_dir() -> Path:
    return resolve_resource_path("PARVA_OUTPUT_DIR", "dist")


def schema_dir() -> Path:
    return resolve_resource_path("PARVA_SCHEMA_DIR", "schemas")


def rules_dir() -> Path:
    return resolve_resource_path("PARVA_RULES_DIR", Path("data") / "rules")


def frontend_dist_dir() -> Path:
    return resolve_resource_path("PARVA_FRONTEND_DIST_DIR", Path("frontend") / "dist")


__all__ = [
    "data_dir",
    "frontend_dist_dir",
    "output_dir",
    "project_root",
    "resolve_resource_path",
    "rules_dir",
    "schema_dir",
]
