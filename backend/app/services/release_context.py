"""Shared public release context helpers."""

from __future__ import annotations

import os

DEFAULT_RELEASE_ID = "parva-bs-public-demo"


def active_release_id() -> str:
    return os.getenv("PARVA_ACTIVE_RELEASE_ID", DEFAULT_RELEASE_ID).strip() or DEFAULT_RELEASE_ID
