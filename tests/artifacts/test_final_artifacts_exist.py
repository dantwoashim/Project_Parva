import subprocess

import pytest

pytestmark = pytest.mark.research_artifact


def test_verify_final_artifacts_script_passes():
    subprocess.run(["python", "scripts/future_bs/generate_all_final_artifacts.py"], check=True)
    subprocess.run(["python", "scripts/future_bs/verify_final_artifacts.py"], check=True)
