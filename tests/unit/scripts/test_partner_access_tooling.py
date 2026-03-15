from __future__ import annotations

from scripts.release.check_render_blueprint import _parse_env_vars
from scripts.release.generate_partner_api_key import generate_record


def test_generate_partner_record_formats_env_entry():
    record = generate_record(
        key_id="municipality-kathmandu-prod",
        scopes=("commercial.read", "public.read"),
        bytes_length=24,
    )

    assert record.key_id == "municipality-kathmandu-prod"
    assert record.scopes == ("commercial.read", "public.read")
    assert record.env_entry().startswith("municipality-kathmandu-prod:")
    assert record.env_entry().endswith(":commercial.read|public.read")
    assert len(record.secret) > 20


def test_generate_partner_record_rejects_short_secrets():
    try:
        generate_record(
            key_id="partner-prod",
            scopes=("commercial.read",),
            bytes_length=8,
        )
    except ValueError as exc:
        assert "at least 16" in str(exc)
    else:
        raise AssertionError("Expected generate_record to reject too-short secrets.")


def test_render_blueprint_parser_extracts_key_fields():
    payload = """
services:
  - type: web
    envVars:
      - key: PARVA_ENV
        value: production
      - key: PARVA_SOURCE_URL
        sync: false
""".strip()

    envs = _parse_env_vars(payload)

    assert envs["PARVA_ENV"]["value"] == "production"
    assert envs["PARVA_SOURCE_URL"]["sync"] == "false"
