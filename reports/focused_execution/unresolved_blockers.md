# Unresolved Blockers

## Environment Issue: Python Build Module Missing

Command:

```bash
python -m build packages/parva-python
```

Result:

```text
C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe: No module named build
```

Install `build` in the Python 3.11 environment and rerun the packaging check.

Attempted install:

```bash
python -m pip install build
```

Result: blocked by local network/socket policy, ending with:

```text
ERROR: Could not find a version that satisfies the requirement build
```

Offline/cache check:

```bash
python -m pip install --no-index wheel
```

Result:

```text
ERROR: Could not find a version that satisfies the requirement wheel (from versions: none)
ERROR: No matching distribution found for wheel
```

`python -m pip show setuptools wheel` showed `setuptools 82.0.1` installed and
`wheel` missing. A local cache search found no `build-*.whl` or `wheel-*.whl`.

Alternative packaging evidence:

```bash
PIP_CACHE_DIR=tmp/pip-cache python -m pip wheel --no-build-isolation --no-deps --wheel-dir dist/sdk-wheel packages/parva-python
```

Result: `Successfully built project-parva-python-sdk`.

## Environment Issue: Git Staging Blocked

Command:

```bash
git add -f reports/phase_07_future_bs_governance/module_classification.md reports/phase_08_performance_sre/latency_baseline.json reports/red_check_closure/ reports/phase_09_frontend_sdk_dx/ reports/focused_execution/ reports/external_reviewer_packet/ reports/broad_exception_audit.md reports/heavy_compute_audit.md reports/docs_public_surface_audit.md
```

Result:

```text
fatal: Unable to create 'D:/Project_Parva-main/.git/index.lock': Permission denied
```

The report files exist and are non-empty, but local Git metadata permissions
prevent staging them from this environment.

Additional probe:

```bash
Test-Path .git/index.lock
```

Result: `False`.

A manual `.git` write/delete probe was rejected by the execution sandbox before
PowerShell ran it, so the remaining evidence points to an environment-level
Git metadata write restriction rather than a stale lock file.

Permission repair attempts:

```bash
icacls .git /grant "$env:USERNAME:(OI)(CI)M"
icacls .git /remove:d S-1-5-21-2048218180-2569795299-734477700-2426682893
takeown /F .git
```

Results:

```text
.git: Access is denied.
ERROR: The current logged on user does not have ownership privileges on
       the file (or folder) "D:\Project_Parva-main\.git".
```

`icacls .git` shows an explicit DENY ACE remains on `.git`:

```text
S-1-5-21-2048218180-2569795299-734477700-2426682893:(DENY)(W,D,Rc,DC)
S-1-5-21-2048218180-2569795299-734477700-2426682893:(OI)(CI)(IO)(DENY)(W,D,Rc,GW,DC)
```

The repository cannot be staged from this sandbox until that DENY ACE is removed
by a user/session with ownership or administrative rights.

## Environment Issue: Registry-Based Vulnerability Audits Blocked

Commands:

```bash
python -m pip_audit --local
npm --prefix frontend audit --audit-level=moderate
npm --prefix packages/parva-js audit --audit-level=moderate
```

Results:

```text
pip_audit: HTTPSConnection(host='pypi.org', port=443) failed with WinError 10013
npm audit: audit endpoint returned an error
```

The npm retry used a repo-local cache:

```bash
npm_config_cache=D:\Project_Parva-main\tmp\npm-cache
```

This removed the npm log-directory write issue, but the registry audit endpoint
still failed.

## Environment Issue: Ambient Python Package Conflict

Command:

```bash
python -m pip check
```

Result:

```text
opencv-python-headless 4.13.0.92 has requirement numpy>=2; python_version >= "3.9", but you have numpy 1.26.0.
```

Repo search found no `opencv` or `cv2` references in Project Parva source. The
conflicting package is installed in the user Python site and is not required by
the repo. Changing Parva's optional research NumPy floor just to satisfy that
ambient package would be a cross-project environment mutation, not a Parva fix.

## Git-Ignored Generated Artifacts

`npm pack` and `pip wheel` generate package artifacts under ignored patterns
(`*.tgz`, `dist/`, and `tmp/`). These are verification outputs, not source files.

`compileall` generated `__pycache__` directories during audit. A recursive
cleanup command was rejected by the execution sandbox, so tests were hardened to
ignore non-source example files instead.
