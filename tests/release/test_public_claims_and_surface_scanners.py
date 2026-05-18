from __future__ import annotations

from pathlib import Path

from scripts.release import check_public_claims, check_public_surface_security


def test_public_claim_compiler_rejects_bad_panchanga_and_package_claims(tmp_path: Path, monkeypatch) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text(
        "Project Parva is official Panchanga authority and available on npm with customer adoption proof.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(check_public_claims, "SCAN_ROOTS", (bad,))

    issues = check_public_claims.check_public_claims()

    assert any("official Panchanga authority" in issue for issue in issues)
    assert any("published package" in issue for issue in issues)
    assert any("customer adoption" in issue for issue in issues)


def test_public_claim_compiler_allows_bounded_negated_claims(tmp_path: Path, monkeypatch) -> None:
    safe = tmp_path / "safe.md"
    safe.write_text(
        "No official Panchanga authority. JPL-backed claim is allowed only when kernel hash evidence is configured.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(check_public_claims, "SCAN_ROOTS", (safe,))

    assert check_public_claims.check_public_claims() == []


def test_public_surface_security_rejects_private_route_leak(tmp_path: Path, monkeypatch) -> None:
    bad = tmp_path / "bad.md"
    bad.write_text("Public docs link to /v3/api/admin/users.\n", encoding="utf-8")
    monkeypatch.setattr(check_public_surface_security, "SCAN_ROOTS", [bad])
    monkeypatch.setattr(check_public_surface_security, "_check_openapi_public_profile", lambda: [])

    assert any("private route" in issue for issue in check_public_surface_security._check_text_files())
