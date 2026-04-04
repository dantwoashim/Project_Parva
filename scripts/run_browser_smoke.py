#!/usr/bin/env python3
"""Run browser smoke checks against a built frontend served by FastAPI."""

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
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "release" / "browser_smoke.json"


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_http(url: str, process: subprocess.Popen[str] | None, timeout_seconds: int) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        if process and process.poll() is not None:
            raise RuntimeError("Backend exited before smoke run started.")
        try:
            with urllib.request.urlopen(url, timeout=1.5) as response:
                if response.status < 500:
                    return
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
            time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def _run_playwright_smoke(base_url: str) -> int:
    node_path = shutil.which("node")
    if node_path is None:
        print("node is required to run the browser smoke suite.")
        return 2

    playwright_cli = FRONTEND_ROOT / "node_modules" / ".bin" / (
        "playwright.cmd" if os.name == "nt" else "playwright"
    )
    if not playwright_cli.exists():
        print("Playwright is not installed in frontend/. Run `npm --prefix frontend install` first.")
        return 2

    executable_probe = subprocess.run(
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
    executable_path = executable_probe.stdout.strip()
    if executable_probe.returncode != 0:
        print(executable_probe.stderr.strip() or "Unable to resolve Playwright browser path.")
        return executable_probe.returncode or 1

    if not executable_path or not Path(executable_path).exists():
        install = subprocess.run(
            [str(playwright_cli), "install", "chromium"],
            cwd=FRONTEND_ROOT,
            check=False,
        )
        if install.returncode != 0:
            return install.returncode

    env = os.environ.copy()
    env["PARVA_SMOKE_BASE_URL"] = base_url
    command = [node_path, "scripts/browser_smoke.mjs"]
    completed = subprocess.run(command, cwd=FRONTEND_ROOT, env=env, check=False)
    return completed.returncode


def _start_backend_server(host: str, port: int) -> subprocess.Popen[str]:
    env = os.environ.copy()
    env["PARVA_SERVE_FRONTEND"] = "true"
    env["PARVA_FRONTEND_DIST"] = str(FRONTEND_DIST)
    command = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", host, "--port", str(port)]
    return subprocess.Popen(
        command,
        cwd=PROJECT_ROOT / "backend",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        text=True,
    )


def _write_report(
    report_path: Path | None,
    *,
    status: str,
    base_url: str | None,
    timeout_seconds: int,
    used_existing_base_url: bool,
    output_dir: Path,
    error: str | None = None,
) -> None:
    if report_path is None:
        return

    report_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "base_url": base_url,
        "timeout_seconds": timeout_seconds,
        "used_existing_base_url": used_existing_base_url,
        "runner": "playwright-chromium",
        "artifacts_dir": str(output_dir),
    }
    if error:
        payload["error"] = error

    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run browser smoke against the Parva app.")
    parser.add_argument("--base-url", help="Use an already running app instead of starting a local server.")
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument(
        "--report-path",
        default=str(DEFAULT_REPORT_PATH),
        help="Optional JSON report path for smoke-run status and artifact location.",
    )
    args = parser.parse_args()
    report_path = Path(args.report_path) if args.report_path else None
    output_dir = PROJECT_ROOT / "output" / "playwright"

    if args.base_url:
        base_url = args.base_url.rstrip("/")
        result = _run_playwright_smoke(base_url)
        _write_report(
            report_path,
            status="passed" if result == 0 else "failed",
            base_url=base_url,
            timeout_seconds=args.timeout_seconds,
            used_existing_base_url=True,
            output_dir=output_dir,
            error=None if result == 0 else "Browser smoke command returned a non-zero exit code.",
        )
        return result

    if not (FRONTEND_DIST / "index.html").exists():
        print("Built frontend not found. Run `npm --prefix frontend run build` first.")
        _write_report(
            report_path,
            status="failed",
            base_url=None,
            timeout_seconds=args.timeout_seconds,
            used_existing_base_url=False,
            output_dir=output_dir,
            error="Built frontend not found.",
        )
        return 2

    host = "127.0.0.1"
    port = _find_free_port()
    base_url = f"http://{host}:{port}"
    process = _start_backend_server(host, port)

    try:
        _wait_for_http(f"{base_url}/health/live", process, args.timeout_seconds)
        result = _run_playwright_smoke(base_url)
        _write_report(
            report_path,
            status="passed" if result == 0 else "failed",
            base_url=base_url,
            timeout_seconds=args.timeout_seconds,
            used_existing_base_url=False,
            output_dir=output_dir,
            error=None if result == 0 else "Browser smoke command returned a non-zero exit code.",
        )
        return result
    except Exception as exc:
        _write_report(
            report_path,
            status="failed",
            base_url=base_url,
            timeout_seconds=args.timeout_seconds,
            used_existing_base_url=False,
            output_dir=output_dir,
            error=str(exc),
        )
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
