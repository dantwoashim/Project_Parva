"""Contract tests for public claim and OpenAPI boundary linting."""

from __future__ import annotations

import json

from scripts.release import check_public_claims


def test_openapi_operation_linter_catches_boundary_sensitive_claims(tmp_path, monkeypatch) -> None:
    api_docs = tmp_path / "docs" / "api-docs"
    api_docs.mkdir(parents=True)
    (api_docs / "openapi.json").write_text(
        json.dumps(
            {
                "paths": {
                    "/v3/api/enterprise/bs-months/{bs_year}": {
                        "get": {
                            "summary": "Enterprise-ready BS month truth",
                            "description": "Return authoritative source-backed month lengths.",
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(check_public_claims, "PROJECT_ROOT", tmp_path)

    issues = check_public_claims._check_openapi_operation_claims()

    assert any("enterprise-ready" in issue for issue in issues)
    assert any("authoritative" in issue for issue in issues)
    assert any("source-backed" in issue for issue in issues)


def test_openapi_operation_linter_allows_negative_boundary_language(tmp_path, monkeypatch) -> None:
    api_docs = tmp_path / "docs" / "api-docs"
    api_docs.mkdir(parents=True)
    (api_docs / "openapi.json").write_text(
        json.dumps(
            {
                "paths": {
                    "/v3/api/enterprise/bs-months/{bs_year}": {
                        "get": {
                            "description": (
                                "Return BS month metadata. This is not authoritative, "
                                "not production-safe for final payroll, and not source-backed "
                                "unless the response metadata says so."
                            ),
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(check_public_claims, "PROJECT_ROOT", tmp_path)

    assert check_public_claims._check_openapi_operation_claims() == []
