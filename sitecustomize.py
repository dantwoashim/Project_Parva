"""Keep bare ``python`` commands on the interpreter required by this project.

Some Windows shells on this machine resolve ``python`` to MSYS Python 3.10.
Project Parva declares Python 3.11 in ``pyproject.toml`` and its runtime
dependencies are installed there, so repo-local Python commands are re-run
through the Python launcher when an older interpreter starts inside the repo.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from pathlib import Path


def _command_args() -> list[str]:
    if os.name != "nt":
        return sys.argv

    try:
        argc = ctypes.c_int()
        kernel32 = ctypes.windll.kernel32
        shell32 = ctypes.windll.shell32
        kernel32.GetCommandLineW.restype = ctypes.c_wchar_p
        shell32.CommandLineToArgvW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
        shell32.CommandLineToArgvW.restype = ctypes.POINTER(ctypes.c_wchar_p)
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        command_line = kernel32.GetCommandLineW()
        argv = shell32.CommandLineToArgvW(command_line, ctypes.byref(argc))
    except Exception:
        return sys.argv

    if not argv:
        return sys.argv

    try:
        return [argv[i] for i in range(1, argc.value)]
    finally:
        kernel32.LocalFree(argv)


def _inside_project() -> bool:
    root = Path(__file__).resolve().parent
    cwd = Path.cwd().resolve()
    return cwd == root or root in cwd.parents


if (
    sys.version_info < (3, 11)
    and os.environ.get("PARVA_PYTHON311_REEXEC") != "1"
    and os.environ.get("PARVA_DISABLE_PYTHON311_REEXEC") != "1"
    and _inside_project()
):
    env = {**os.environ, "PARVA_PYTHON311_REEXEC": "1"}
    completed = subprocess.run(["py", "-3.11", *_command_args()], env=env)
    os._exit(completed.returncode)
