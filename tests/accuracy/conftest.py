from __future__ import annotations

from pathlib import Path

import pytest

ACCURACY_TEST_ROOT = Path(__file__).resolve().parent


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        item_path = Path(str(item.fspath)).resolve()
        if item_path.parent == ACCURACY_TEST_ROOT:
            item.add_marker(pytest.mark.research_artifact)
