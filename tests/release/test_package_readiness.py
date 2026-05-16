from __future__ import annotations

from scripts.release.check_package_readiness import check_all


def test_public_packages_have_distribution_metadata():
    assert check_all() == []
