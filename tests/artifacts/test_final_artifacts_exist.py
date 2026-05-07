import subprocess


def test_verify_final_artifacts_script_passes():
    subprocess.run(["python", "scripts/future_bs/verify_final_artifacts.py"], check=True)
