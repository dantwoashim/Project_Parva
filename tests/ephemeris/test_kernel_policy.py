from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.ephemeris.verify_kernel_hashes import verify


def _write_config(path: Path, expected_sha256: str | None) -> None:
    path.write_text(
        json.dumps(
            {
                "kernels": [
                    {
                        "id": "demo",
                        "path_env_var": "PARVA_TEST_KERNEL",
                        "expected_sha256": expected_sha256,
                        "public_runtime_required": False,
                        "private_or_research": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def test_absent_optional_kernel_is_skipped_without_path_leak(tmp_path, monkeypatch) -> None:
    config = tmp_path / "kernels.json"
    _write_config(config, "abc")
    monkeypatch.setenv("PARVA_TEST_KERNEL", str(tmp_path / "missing.bsp"))

    result = verify(config, project_root=tmp_path)

    assert result["ok"] is True
    assert result["results"][0]["status"] == "skipped_absent_optional_kernel"
    assert str(tmp_path) not in json.dumps(result)


def test_hash_mismatch_fails_without_path_leak(tmp_path, monkeypatch) -> None:
    kernel = tmp_path / "kernel.bsp"
    kernel.write_bytes(b"kernel")
    config = tmp_path / "kernels.json"
    _write_config(config, "0" * 64)
    monkeypatch.setenv("PARVA_TEST_KERNEL", str(kernel))

    result = verify(config, project_root=tmp_path)

    assert result["ok"] is False
    assert result["results"][0]["status"] == "fail_hash_mismatch"
    assert str(kernel) not in json.dumps(result)


def test_matching_hash_passes(tmp_path, monkeypatch) -> None:
    kernel = tmp_path / "kernel.bsp"
    kernel.write_bytes(b"kernel")
    expected = hashlib.sha256(b"kernel").hexdigest()
    config = tmp_path / "kernels.json"
    _write_config(config, expected)
    monkeypatch.setenv("PARVA_TEST_KERNEL", str(kernel))

    result = verify(config, project_root=tmp_path)

    assert result["ok"] is True
    assert result["results"][0]["status"] == "pass"
