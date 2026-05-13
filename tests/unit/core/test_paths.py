from __future__ import annotations

from app.core.paths import data_dir, frontend_dist_dir, output_dir, rules_dir, schema_dir


def test_resource_path_env_overrides(monkeypatch, tmp_path):
    data = tmp_path / "data-root"
    output = tmp_path / "output-root"
    schemas = tmp_path / "schema-root"
    rules = tmp_path / "rules-root"
    frontend = tmp_path / "frontend-dist"

    monkeypatch.setenv("PARVA_DATA_DIR", str(data))
    monkeypatch.setenv("PARVA_OUTPUT_DIR", str(output))
    monkeypatch.setenv("PARVA_SCHEMA_DIR", str(schemas))
    monkeypatch.setenv("PARVA_RULES_DIR", str(rules))
    monkeypatch.setenv("PARVA_FRONTEND_DIST_DIR", str(frontend))

    assert data_dir() == data.resolve()
    assert output_dir() == output.resolve()
    assert schema_dir() == schemas.resolve()
    assert rules_dir() == rules.resolve()
    assert frontend_dist_dir() == frontend.resolve()
