from __future__ import annotations

from scripts.release import verify_clean_clone_assumptions as checker
from scripts.release.verify_public import _configured_python_candidates


def test_clean_clone_assumptions_pass() -> None:
    assert checker.verify_clean_clone_assumptions() == []


def _patch_minimal_project(monkeypatch, tmp_path, tracked: set[str]) -> None:
    (tmp_path / "config").mkdir(parents=True)
    (tmp_path / "config" / "ephemeris-kernels.yaml").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(checker, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(checker, "REQUIRED_PUBLIC_FILES", ())
    monkeypatch.setattr(checker, "OPTIONAL_PRIVATE_INPUTS", ())
    monkeypatch.setattr(checker, "_git_ls_files", lambda: tracked)
    monkeypatch.setattr(checker, "_is_ignored", lambda _path: False)


def test_clean_clone_assumptions_rejects_untracked_css_import(monkeypatch, tmp_path) -> None:
    source = tmp_path / "frontend" / "src" / "redesign"
    source.mkdir(parents=True)
    (source / "ParvaRedesign.css").write_text("@import './part01.css';\n", encoding="utf-8")
    (source / "part01.css").write_text(".x { color: red; }\n", encoding="utf-8")
    _patch_minimal_project(
        monkeypatch,
        tmp_path,
        {"frontend/src/redesign/ParvaRedesign.css"},
    )

    issues = checker.verify_clean_clone_assumptions()

    assert issues == [
        "frontend/src/redesign/ParvaRedesign.css: CSS import './part01.css' target "
        "frontend/src/redesign/part01.css exists locally but is not tracked"
    ]


def test_clean_clone_assumptions_rejects_untracked_js_import(monkeypatch, tmp_path) -> None:
    source = tmp_path / "frontend" / "src" / "pages"
    source.mkdir(parents=True)
    (source / "FeedSubscriptionsPage.jsx").write_text(
        "import { Card } from './FeedSubscriptionCards.jsx';\n",
        encoding="utf-8",
    )
    (source / "FeedSubscriptionCards.jsx").write_text("export const Card = () => null;\n", encoding="utf-8")
    _patch_minimal_project(
        monkeypatch,
        tmp_path,
        {"frontend/src/pages/FeedSubscriptionsPage.jsx"},
    )

    issues = checker.verify_clean_clone_assumptions()

    assert issues == [
        "frontend/src/pages/FeedSubscriptionsPage.jsx: JS import './FeedSubscriptionCards.jsx' target "
        "frontend/src/pages/FeedSubscriptionCards.jsx exists locally but is not tracked"
    ]


def test_clean_clone_assumptions_rejects_untracked_app_python_import(monkeypatch, tmp_path) -> None:
    source = tmp_path / "backend" / "app" / "rules"
    source.mkdir(parents=True)
    (source / "service.py").write_text("from app.rules.festival_engine import run\n", encoding="utf-8")
    (source / "festival_engine.py").write_text("def run():\n    return None\n", encoding="utf-8")
    _patch_minimal_project(
        monkeypatch,
        tmp_path,
        {"backend/app/rules/service.py"},
    )

    issues = checker.verify_clean_clone_assumptions()

    assert issues == [
        "backend/app/rules/service.py: Python import 'app.rules.festival_engine' target "
        "backend/app/rules/festival_engine.py exists locally but is not tracked"
    ]


def test_clean_clone_assumptions_allows_generated_package_dist(monkeypatch, tmp_path) -> None:
    source = tmp_path / "packages" / "parva-js" / "tests"
    source.mkdir(parents=True)
    (source / "client.test.mjs").write_text("import { Client } from '../dist/index.js';\n", encoding="utf-8")
    _patch_minimal_project(
        monkeypatch,
        tmp_path,
        {"packages/parva-js/tests/client.test.mjs"},
    )

    assert checker.verify_clean_clone_assumptions() == []


def test_verify_public_accepts_python_launcher_arguments() -> None:
    assert _configured_python_candidates("py -3.11", "") == [["py -3.11"], ["py", "-3.11"]]


def test_verify_public_supports_separate_python_args() -> None:
    assert _configured_python_candidates("py", "-3.11") == [["py", "-3.11"]]
