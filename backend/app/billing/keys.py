"""API-key generation and hashing utilities."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass

KEY_PREFIX = "parva_live"


@dataclass(frozen=True)
class ParsedAPIKey:
    key_prefix: str
    secret: str


def generate_api_key() -> tuple[str, str, str]:
    """Return full key, searchable prefix, and secret hash input."""
    key_prefix = secrets.token_hex(4)
    secret = secrets.token_urlsafe(32)
    full_key = f"{KEY_PREFIX}_{key_prefix}_{secret}"
    return full_key, key_prefix, secret


def parse_api_key(raw_key: str) -> ParsedAPIKey | None:
    parts = str(raw_key or "").strip().split("_", 3)
    if len(parts) != 4:
        return None
    product, environment, key_prefix, secret = parts
    if f"{product}_{environment}" != KEY_PREFIX or not key_prefix or not secret:
        return None
    return ParsedAPIKey(key_prefix=key_prefix, secret=secret)


def hash_api_key_secret(secret: str, pepper: str) -> str:
    payload = f"{secret}{pepper}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def constant_time_hash_match(candidate_hash: str, stored_hash: str) -> bool:
    return hmac.compare_digest(str(candidate_hash or ""), str(stored_hash or ""))

