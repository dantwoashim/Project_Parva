from __future__ import annotations

from pathlib import Path

from app.bootstrap.app_factory import create_app
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]


def _join(*parts: str) -> str:
    return "".join(parts)


PROHIBITED_README_PHRASES = [
    "cracked " + "Panchanga",
    "Panchanga " + "cracked",
    "guaranteed " + "future dates",
    "official future " + "calendar",
    "99% future " + "accuracy",
    _join("Info", "Developers"),
    _join("info", "dev"),
]

PRIVATE_FUTURE_PATHS = {
    "/v4/api/future-bs/month-lengths/{bs_year}",
    "/v4/api/future-bs/month-lengths/range",
    "/v4/api/future-bs/month-lengths/export.csv",
    "/v4/api/future-bs/export.csv",
    "/v4/api/future-bs/export.xlsx",
    "/v4/api/future-bs/month-lengths/explain",
    "/v4/api/future-bs/boundary-risk",
    "/v4/api/future-bs/backtest",
    "/v4/api/future-bs/backtest/residuals",
    "/v4/api/future-bs/model-runs",
    "/v4/api/future-bs/loan-impact/simulate",
    "/v4/api/future-bs/month-lengths/import-excel",
    "/v4/api/future-bs/month-lengths/compare",
    "/v5/api/calendar-model-risk/prediction/{bs_year}/{month}",
    "/v5/api/calendar-model-risk/prediction-set/{bs_year}/{month}",
    "/v5/api/calendar-model-risk/committee-posterior/{bs_year}/{month}",
    "/v5/api/calendar-model-risk/perturbation-robustness/{bs_year}/{month}",
    "/v5/api/calendar-model-risk/audit-external-sheet",
    "/v5/api/calendar-model-risk/calendar-var",
    "/v5/api/calendar-model-risk/stress-test",
    "/v5/api/calendar-model-risk/red-team/2083-ashwin",
    "/v5/api/calendar-model-risk/claim-readiness",
}


def _public_client(monkeypatch) -> TestClient:
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "false")
    monkeypatch.setenv("PARVA_SHOW_PRIVATE_SCHEMA", "false")
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")
    return TestClient(create_app())


def test_public_openapi_does_not_list_private_future_routes(monkeypatch):
    client = _public_client(monkeypatch)
    paths = set(client.get("/openapi.json").json()["paths"])

    assert "/v4/api/future-bs/capabilities" in paths
    assert "/v5/api/calendar-model-risk/capabilities" in paths
    assert PRIVATE_FUTURE_PATHS.isdisjoint(paths)


def test_public_capabilities_are_metadata_only(monkeypatch):
    client = _public_client(monkeypatch)

    for path in [
        "/v4/api/future-bs/capabilities",
        "/v5/api/calendar-model-risk/capabilities",
    ]:
        body = client.get(path).json()
        assert body["publication_status"] == "computed_prediction_not_official"
        assert body["surface"] == "future_bs_risk_research"
        assert "public_surface" in body
        assert "not_claimed" in body
        assert "months" not in body
        assert "years" not in body
        assert "predicted_days" not in body
        assert "model_runs" not in body
        assert "export.csv" not in str(body)


def test_private_schema_requires_explicit_flag(monkeypatch):
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "true")
    monkeypatch.setenv("PARVA_ADMIN_TOKEN", "test-token")
    monkeypatch.setenv("PARVA_SHOW_PRIVATE_SCHEMA", "false")
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")

    hidden_client = TestClient(create_app())
    hidden_paths = set(hidden_client.get("/openapi.json").json()["paths"])
    assert "/v4/api/future-bs/month-lengths/{bs_year}" not in hidden_paths

    monkeypatch.setenv("PARVA_SHOW_PRIVATE_SCHEMA", "true")
    shown_client = TestClient(create_app())
    shown_paths = set(shown_client.get("/openapi.json").json()["paths"])
    assert "/v4/api/future-bs/month-lengths/{bs_year}" in shown_paths


def test_claim_boundary_docs_exist():
    required = [
        "docs/PUBLIC_API_BOUNDARY.md",
        "docs/future_bs/CLAIM_BOUNDARY.md",
        "docs/future_bs/SOURCE_POLICY.md",
        "docs/future_bs/FUTURE_BS_RESEARCH.md",
        "docs/future_bs/RISK_LABELS.md",
        "docs/future_bs/RECONCILIATION_WORKFLOW.md",
        "docs/SDK_ROADMAP.md",
    ]

    for relative in required:
        path = ROOT / relative
        assert path.exists(), relative
        assert path.read_text(encoding="utf-8").strip(), relative


def test_readme_avoids_prohibited_public_claims():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in PROHIBITED_README_PHRASES:
        assert phrase not in readme


def test_public_docs_do_not_use_em_dash():
    paths = [ROOT / "README.md", ROOT / "AGENTS.md", *list((ROOT / "docs").rglob("*.md"))]
    for path in paths:
        assert "—" not in path.read_text(encoding="utf-8"), str(path.relative_to(ROOT))


def test_public_examples_do_not_contain_future_vectors_or_private_routes():
    examples = ROOT / "examples"
    assert examples.exists()
    sensitive_tokens = [
        "month-lengths",
        "export.csv",
        "export.xlsx",
        "model-runs",
        "loan-impact",
        "2084",
        "2099",
        "2200",
    ]
    for path in examples.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for token in sensitive_tokens:
                assert token not in text, str(path.relative_to(ROOT))
