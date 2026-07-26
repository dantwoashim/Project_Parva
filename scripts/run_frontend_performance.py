#!/usr/bin/env python3
"""Run frontend performance measurements against the built FastAPI application."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
FRONTEND_DIST = FRONTEND_ROOT / "dist"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "release" / "frontend_performance.json"


def _resolve_report_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_http(
    url: str,
    process: subprocess.Popen[str] | None,
    timeout_seconds: int,
) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        if process and process.poll() is not None:
            raise RuntimeError("Backend exited before performance measurements started.")
        try:
            with urllib.request.urlopen(url, timeout=1.5) as response:
                if response.status < 500:
                    return
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
            time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def _ensure_playwright_browser() -> int:
    node_path = shutil.which("node")
    if node_path is None:
        print("node is required to run the performance walkthrough.")
        return 2

    playwright_cli = FRONTEND_ROOT / "node_modules" / ".bin" / (
        "playwright.cmd" if os.name == "nt" else "playwright"
    )
    if not playwright_cli.exists():
        print("Playwright is not installed in frontend/. Run `npm --prefix frontend install` first.")
        return 2

    probe = subprocess.run(
        [
            node_path,
            "-e",
            "const { chromium } = require('playwright'); process.stdout.write(chromium.executablePath())",
        ],
        cwd=FRONTEND_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    executable_path = probe.stdout.strip()
    if probe.returncode != 0:
        print(probe.stderr.strip() or "Unable to resolve Playwright browser path.")
        return probe.returncode or 1

    if not executable_path or not Path(executable_path).exists():
        install = subprocess.run(
            [str(playwright_cli), "install", "chromium"],
            cwd=FRONTEND_ROOT,
            check=False,
        )
        return install.returncode

    return 0


def _run_performance(base_url: str, report_path: Path) -> int:
    browser_status = _ensure_playwright_browser()
    if browser_status != 0:
        return browser_status

    node_path = shutil.which("node")
    env = os.environ.copy()
    env["PARVA_PERF_BASE_URL"] = base_url
    env["PARVA_PERF_REPORT_PATH"] = str(report_path)
    completed = subprocess.run(
        [node_path, "scripts/performance_walkthrough.mjs"],
        cwd=FRONTEND_ROOT,
        env=env,
        check=False,
    )
    return completed.returncode


def _start_backend(host: str, port: int) -> subprocess.Popen[str]:
    env = os.environ.copy()
    env["PARVA_SERVE_FRONTEND"] = "true"
    env["PARVA_FRONTEND_DIST"] = str(FRONTEND_DIST)
    env["PARVA_RATE_LIMIT_ENABLED"] = "false"
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    return subprocess.Popen(
        command,
        cwd=PROJECT_ROOT / "backend",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        text=True,
    )


def _write_failure(report_path: Path, base_url: str | None, error: str) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "status": "failed",
                "base_url": base_url,
                "runner": "playwright-chromium",
                "error": error,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run frontend performance measurements against Project Parva."
    )
    parser.add_argument("--base-url", help="Use an already running application.")
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument(
        "--report-path",
        default=str(DEFAULT_REPORT_PATH),
        help="JSON report path.",
    )
    args = parser.parse_args()
    report_path = _resolve_report_path(args.report_path)

    if not (FRONTEND_DIST / "index.html").exists():
        error = "Built frontend not found. Run `npm --prefix frontend run build` first."
        print(error)
        _write_failure(report_path, None, error)
        return 2

    if args.base_url:
        return _run_performance(args.base_url.rstrip("/"), report_path)

    host = "127.0.0.1"
    port = _find_free_port()
    base_url = f"http://{host}:{port}"
    process = _start_backend(host, port)
    try:
        _wait_for_http(f"{base_url}/health/live", process, args.timeout_seconds)
        return _run_performance(base_url, report_path)
    except Exception as exc:
        _write_failure(report_path, base_url, str(exc))
        raise
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
