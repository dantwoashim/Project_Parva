"""Application settings and startup validation."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEV_ENV_VALUES = {"dev", "development", "local", "test"}
TEST_ENV_VALUES: Final[frozenset[str]] = frozenset({"test"})
DEFAULT_TEST_ADMIN_TOKEN = "-".join(("parva", "test", "admin", "token"))
DEFAULT_TEST_READ_KEY = "-".join(("parva", "test", "read", "key"))


def _parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_optional_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return None


@dataclass(frozen=True)
class APIKeyRecord:
    key_id: str
    secret: str
    scopes: frozenset[str]


@dataclass(frozen=True)
class AppSettings:
    environment: str
    license_mode: str
    source_url: str | None
    enable_experimental_api: bool
    allow_experimental_in_prod: bool
    serve_frontend: bool
    frontend_dist: Path
    max_request_bytes: int
    max_query_length: int
    admin_token: str | None
    api_keys: dict[str, APIKeyRecord] = field(default_factory=dict)
    rate_limit_enabled: bool = True
    rate_limit_backend: str = "memory"
    redis_url: str | None = None
    require_precomputed: bool = False
    precomputed_stale_hours: int = 24 * 30
    trusted_proxy_ips: frozenset[str] = field(default_factory=frozenset)

    @property
    def is_dev_environment(self) -> bool:
        return self.environment.strip().lower() in DEV_ENV_VALUES


def _allow_test_only_credentials(environment: str) -> bool:
    normalized = environment.strip().lower()
    if normalized in TEST_ENV_VALUES:
        return True
    if "pytest" in sys.modules:
        return True
    return bool(os.getenv("PYTEST_CURRENT_TEST"))


def _frontend_dist_from_env() -> Path:
    configured = os.getenv("PARVA_FRONTEND_DIST", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return (PROJECT_ROOT / "frontend" / "dist").resolve()


def _parse_api_keys(raw: str, *, environment: str) -> dict[str, APIKeyRecord]:
    records: dict[str, APIKeyRecord] = {}
    raw = raw.strip()
    if not raw and _allow_test_only_credentials(environment):
        raw = f"local-read:{DEFAULT_TEST_READ_KEY}:commercial.read|public.read"

    if not raw:
        return records

    for item in raw.split(";"):
        token = item.strip()
        if not token:
            continue
        parts = [part.strip() for part in token.split(":", 2)]
        if len(parts) != 3:
            raise ValueError(
                "PARVA_API_KEYS entries must follow key-id:secret:scope1|scope2 format"
            )
        key_id, secret, scopes_raw = parts
        scopes = frozenset(scope.strip() for scope in scopes_raw.split("|") if scope.strip())
        if not key_id or not secret or not scopes:
            raise ValueError("PARVA_API_KEYS entries must include key id, secret, and scopes")
        records[key_id] = APIKeyRecord(key_id=key_id, secret=secret, scopes=scopes)

    return records


def _parse_csv_set(raw: str) -> frozenset[str]:
    return frozenset(token.strip() for token in raw.split(",") if token.strip())


def _parse_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _validate_license_mode(settings: AppSettings) -> list[str]:
    normalized_license = settings.license_mode.strip().lower()
    if normalized_license in {"agpl-3.0-only", "agpl-3.0-or-later"}:
        return []
    return [
        "PARVA_LICENSE_MODE must stay AGPL-compatible for the zero-budget Swiss Ephemeris deployment path."
    ]


def _validate_source_url(settings: AppSettings) -> list[str]:
    errors: list[str] = []
    if settings.source_url and not settings.source_url.startswith(("http://", "https://", "/")):
        errors.append("PARVA_SOURCE_URL must be an absolute http(s) URL or an absolute site path.")
    if settings.source_url == "/source":
        errors.append("PARVA_SOURCE_URL cannot point to /source itself.")
    if settings.environment.lower() == "production" and not settings.source_url:
        errors.append(
            "Production deployments must publish corresponding source code via PARVA_SOURCE_URL."
        )
    return errors


def _validate_experimental_settings(settings: AppSettings) -> list[str]:
    errors: list[str] = []
    if settings.environment.lower() == "production" and settings.enable_experimental_api:
        if not settings.allow_experimental_in_prod:
            errors.append(
                "Experimental routes require PARVA_ALLOW_EXPERIMENTAL_IN_PROD=true in production."
            )
    if settings.enable_experimental_api and not settings.admin_token:
        errors.append("Experimental routes require PARVA_ADMIN_TOKEN.")
    return errors


def _validate_rate_limit_settings(settings: AppSettings) -> list[str]:
    if not settings.rate_limit_enabled:
        return []

    errors: list[str] = []
    backend = settings.rate_limit_backend.strip().lower()
    if backend not in {"memory", "redis"}:
        errors.append("PARVA_RATE_LIMIT_BACKEND must be either memory or redis.")
    if backend == "redis" and not settings.redis_url:
        errors.append("PARVA_REDIS_URL is required when PARVA_RATE_LIMIT_BACKEND=redis.")
    if settings.environment.lower() == "production" and backend == "memory":
        errors.append(
            "Production deployments must use PARVA_RATE_LIMIT_BACKEND=redis for distributed throttling."
        )
    return errors


def _validate_frontend_settings(settings: AppSettings) -> list[str]:
    if not settings.serve_frontend or settings.environment.lower() != "production":
        return []

    index_path = settings.frontend_dist / "index.html"
    if index_path.exists():
        return []
    return [f"Frontend serving enabled but built assets are missing at {index_path}."]


def load_settings() -> AppSettings:
    environment = os.getenv("PARVA_ENV", "development").strip() or "development"
    admin_token = os.getenv("PARVA_ADMIN_TOKEN", "").strip() or None
    if admin_token is None and _allow_test_only_credentials(environment):
        admin_token = DEFAULT_TEST_ADMIN_TOKEN
    require_precomputed_override = _parse_optional_bool(os.getenv("PARVA_REQUIRE_PRECOMPUTED"))
    require_precomputed = (
        require_precomputed_override
        if require_precomputed_override is not None
        else environment.strip().lower() == "production"
    )

    return AppSettings(
        environment=environment,
        license_mode=os.getenv("PARVA_LICENSE_MODE", "AGPL-3.0-or-later").strip()
        or "AGPL-3.0-or-later",
        source_url=_parse_optional_text(os.getenv("PARVA_SOURCE_URL")),
        enable_experimental_api=_parse_bool(
            os.getenv("PARVA_ENABLE_EXPERIMENTAL_API"), default=False
        ),
        allow_experimental_in_prod=_parse_bool(
            os.getenv("PARVA_ALLOW_EXPERIMENTAL_IN_PROD"), default=False
        ),
        serve_frontend=_parse_bool(os.getenv("PARVA_SERVE_FRONTEND"), default=False),
        frontend_dist=_frontend_dist_from_env(),
        max_request_bytes=int(os.getenv("PARVA_MAX_REQUEST_BYTES", "1048576")),
        max_query_length=int(os.getenv("PARVA_MAX_QUERY_LENGTH", "4096")),
        admin_token=admin_token,
        api_keys=_parse_api_keys(os.getenv("PARVA_API_KEYS", ""), environment=environment),
        rate_limit_enabled=_parse_bool(os.getenv("PARVA_RATE_LIMIT_ENABLED"), default=True),
        rate_limit_backend=(os.getenv("PARVA_RATE_LIMIT_BACKEND", "memory").strip() or "memory"),
        redis_url=_parse_optional_text(os.getenv("PARVA_REDIS_URL")),
        require_precomputed=require_precomputed,
        precomputed_stale_hours=int(os.getenv("PARVA_PRECOMPUTED_STALE_HOURS", str(24 * 30))),
        trusted_proxy_ips=_parse_csv_set(os.getenv("PARVA_TRUSTED_PROXY_IPS", "")),
    )


def validate_settings(settings: AppSettings) -> list[str]:
    errors: list[str] = []
    errors.extend(_validate_license_mode(settings))
    errors.extend(_validate_source_url(settings))
    errors.extend(_validate_experimental_settings(settings))
    errors.extend(_validate_rate_limit_settings(settings))
    errors.extend(_validate_frontend_settings(settings))
    return errors
