#!/usr/bin/env python3
"""Validate the Cloud Run deployment assets for the split-hosting path."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLOUDRUN_DOCKERFILE = PROJECT_ROOT / "Dockerfile.cloudrun"
CLOUDBUILD_CONFIG = PROJECT_ROOT / "cloudbuild.cloudrun.yaml"
PAGES_REDIRECTS = PROJECT_ROOT / "frontend" / "public" / "_redirects"


def main() -> int:
    failures: list[str] = []

    if not CLOUDRUN_DOCKERFILE.exists():
        failures.append("Dockerfile.cloudrun is missing.")
    else:
        dockerfile_text = CLOUDRUN_DOCKERFILE.read_text(encoding="utf-8")
        expected_fragments = {
            "PARVA_SERVE_FRONTEND=false": "Cloud Run backend must default to PARVA_SERVE_FRONTEND=false.",
            "--port ${PORT:-8080}": "Cloud Run backend must listen on the injected PORT (fallback 8080).",
        }
        for fragment, message in expected_fragments.items():
            if fragment not in dockerfile_text:
                failures.append(message)
        if "COPY --from=frontend-builder" in dockerfile_text:
            failures.append("Dockerfile.cloudrun must not bundle frontend build artifacts.")

    if not CLOUDBUILD_CONFIG.exists():
        failures.append("cloudbuild.cloudrun.yaml is missing.")
    else:
        config_text = CLOUDBUILD_CONFIG.read_text(encoding="utf-8")
        if "Dockerfile.cloudrun" not in config_text:
            failures.append("cloudbuild.cloudrun.yaml must build Dockerfile.cloudrun.")
        if "${_IMAGE}" not in config_text:
            failures.append("cloudbuild.cloudrun.yaml must publish a configurable image tag.")

    if not PAGES_REDIRECTS.exists():
        failures.append("frontend/public/_redirects is missing.")
    else:
        redirects_text = PAGES_REDIRECTS.read_text(encoding="utf-8")
        if "/* /index.html 200" not in redirects_text:
            failures.append("frontend/public/_redirects must preserve SPA routing for Pages.")

    if failures:
        for failure in failures:
            print(f"[cloudrun-blueprint] {failure}")
        return 1

    print("Cloud Run blueprint check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
