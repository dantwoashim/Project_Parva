"""Resolve the pinned Parva Node runtime for local validation commands."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path
import shutil
import subprocess

SUPPORTED_NODE_MAJOR = "20"
MANAGED_NODE_SPEC = "node@20"


@dataclass(frozen=True)
class NodeRuntime:
    executable: Path
    version: str
    source: str
    managed: bool

    @property
    def bin_dir(self) -> Path:
        return self.executable.parent

    def build_env(self, base_env: dict[str, str] | None = None) -> dict[str, str]:
        env = dict(base_env or os.environ)
        path_entries = [str(self.bin_dir)]
        existing_path = env.get("PATH")
        if existing_path:
            path_entries.append(existing_path)
        env["PATH"] = os.pathsep.join(path_entries)
        env["PARVA_NODE_BIN"] = str(self.executable)
        return env

    def describe(self) -> str:
        detail = f"Node v{self.version}"
        if self.managed:
            return f"{detail} ({self.source})"
        return detail


def _run_version(executable: str, env: dict[str, str] | None = None) -> tuple[bool, str]:
    resolved = shutil.which(executable, path=(env or os.environ).get("PATH"))
    if not resolved:
        return False, f"{executable} not found"

    result = subprocess.run(
        [resolved, "--version"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "command failed"
        return False, detail
    return True, result.stdout.strip()


def _resolve_node_candidate(executable: str, source: str, managed: bool) -> NodeRuntime | None:
    ok, detail = _run_version(executable)
    if not ok:
        return None

    version = detail.removeprefix("v")
    major = version.split(".", 1)[0]
    if major != SUPPORTED_NODE_MAJOR:
        return None

    resolved = shutil.which(executable)
    if not resolved:
        return None

    return NodeRuntime(
        executable=Path(resolved),
        version=version,
        source=source,
        managed=managed,
    )


def _resolve_env_candidate() -> NodeRuntime | None:
    explicit = os.environ.get("PARVA_NODE_BIN")
    if not explicit:
        return None

    executable = Path(explicit)
    if not executable.exists():
        return None

    result = subprocess.run(
        [str(executable), "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    version = result.stdout.strip().removeprefix("v")
    major = version.split(".", 1)[0]
    if major != SUPPORTED_NODE_MAJOR:
        return None

    return NodeRuntime(
        executable=executable,
        version=version,
        source="managed via PARVA_NODE_BIN",
        managed=True,
    )


def _resolve_managed_candidate() -> NodeRuntime | None:
    npx = shutil.which("npx")
    if not npx:
        return None

    result = subprocess.run(
        [npx, "-y", MANAGED_NODE_SPEC, "-p", "process.execPath"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None

    candidate = Path(result.stdout.strip())
    if not candidate.exists():
        return None

    version_result = subprocess.run(
        [str(candidate), "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    if version_result.returncode != 0:
        return None

    version = version_result.stdout.strip().removeprefix("v")
    major = version.split(".", 1)[0]
    if major != SUPPORTED_NODE_MAJOR:
        return None

    return NodeRuntime(
        executable=candidate,
        version=version,
        source=f"managed via npx {MANAGED_NODE_SPEC}",
        managed=True,
    )


@lru_cache(maxsize=1)
def resolve_node_runtime() -> NodeRuntime | None:
    return (
        _resolve_env_candidate()
        or _resolve_node_candidate("node", "system", managed=False)
        or _resolve_managed_candidate()
    )


def current_npm_version(runtime: NodeRuntime | None = None) -> tuple[bool, str]:
    env = runtime.build_env() if runtime else None
    return _run_version("npm", env=env)
