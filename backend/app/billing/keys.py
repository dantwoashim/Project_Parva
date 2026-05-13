"""API-key generation and hashing utilities."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass

KEY_PREFIX = "parva_live"
PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 310_000


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
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        f"{secret}{pepper}".encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return "$".join(
        (
            PBKDF2_ALGORITHM,
            str(PBKDF2_ITERATIONS),
            base64.urlsafe_b64encode(salt).decode("ascii"),
            base64.urlsafe_b64encode(digest).decode("ascii"),
        )
    )


def _legacy_sha256_hash(secret: str, pepper: str) -> str:
    payload = f"{secret}{pepper}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def constant_time_hash_match(candidate_hash: str, stored_hash: str) -> bool:
    return hmac.compare_digest(str(candidate_hash or ""), str(stored_hash or ""))


def verify_api_key_secret(secret: str, pepper: str, stored_hash: str) -> bool:
    raw_hash = str(stored_hash or "")
    parts = raw_hash.split("$")
    if len(parts) == 4 and parts[0] == PBKDF2_ALGORITHM:
        try:
            iterations = int(parts[1])
            salt = base64.urlsafe_b64decode(parts[2].encode("ascii"))
            expected = base64.urlsafe_b64decode(parts[3].encode("ascii"))
        except (ValueError, TypeError):
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            f"{secret}{pepper}".encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(digest, expected)

    # Compatibility for any existing locally generated SHA-256 hashes. New
    # writes always use the versioned PBKDF2 format above.
    return hmac.compare_digest(_legacy_sha256_hash(secret, pepper), raw_hash)
