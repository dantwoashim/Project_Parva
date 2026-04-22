from __future__ import annotations

from scripts.release import check_cloudrun_blueprint


def test_cloudrun_blueprint_passes_with_expected_assets(tmp_path, monkeypatch, capsys):
    dockerfile = tmp_path / "Dockerfile.cloudrun"
    dockerfile.write_text(
        'ENV PARVA_SERVE_FRONTEND=false\n'
        'CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --app-dir backend"]\n',
        encoding="utf-8",
    )
    cloudbuild = tmp_path / "cloudbuild.cloudrun.yaml"
    cloudbuild.write_text("steps:\n- Dockerfile.cloudrun\nimages:\n- ${_IMAGE}\n", encoding="utf-8")
    redirects = tmp_path / "frontend" / "public" / "_redirects"
    redirects.parent.mkdir(parents=True, exist_ok=True)
    redirects.write_text("/* /index.html 200\n", encoding="utf-8")

    monkeypatch.setattr(check_cloudrun_blueprint, "CLOUDRUN_DOCKERFILE", dockerfile)
    monkeypatch.setattr(check_cloudrun_blueprint, "CLOUDBUILD_CONFIG", cloudbuild)
    monkeypatch.setattr(check_cloudrun_blueprint, "PAGES_REDIRECTS", redirects)

    assert check_cloudrun_blueprint.main() == 0
    assert capsys.readouterr().out.strip() == "Cloud Run blueprint check passed."


def test_cloudrun_blueprint_reports_missing_backend_split_assets(tmp_path, monkeypatch, capsys):
    dockerfile = tmp_path / "Dockerfile.cloudrun"
    dockerfile.write_text('CMD ["uvicorn", "app.main:app"]\n', encoding="utf-8")
    cloudbuild = tmp_path / "cloudbuild.cloudrun.yaml"
    cloudbuild.write_text("steps:\n- name: docker\n", encoding="utf-8")
    redirects = tmp_path / "frontend" / "public" / "_redirects"
    redirects.parent.mkdir(parents=True, exist_ok=True)
    redirects.write_text("/docs /docs/index.html 200\n", encoding="utf-8")

    monkeypatch.setattr(check_cloudrun_blueprint, "CLOUDRUN_DOCKERFILE", dockerfile)
    monkeypatch.setattr(check_cloudrun_blueprint, "CLOUDBUILD_CONFIG", cloudbuild)
    monkeypatch.setattr(check_cloudrun_blueprint, "PAGES_REDIRECTS", redirects)

    assert check_cloudrun_blueprint.main() == 1
    output = capsys.readouterr().out
    assert "PARVA_SERVE_FRONTEND=false" in output
    assert "injected PORT" in output
    assert "configurable image tag" in output
    assert "SPA routing" in output
