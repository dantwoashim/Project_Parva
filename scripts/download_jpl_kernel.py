#!/usr/bin/env python3
"""Download and verify NAIF JPL SPK kernels used by Parva."""

from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
import urllib.request
from pathlib import Path

KERNELS = {
    "de440": {
        "url": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440.bsp",
        "md5": "c9d581bfd84209dbeee8b1583939b148",
        "output": Path("data/ephemeris/jpl/de440.bsp"),
    },
    "de441-part1": {
        "url": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de441_part-1.bsp",
        "md5": "7e5fcf9ecb5d08e1ab70c049baa60cd3",
        "output": Path("data/ephemeris/jpl/de441_part-1.bsp"),
    },
    "de441-part2": {
        "url": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de441_part-2.bsp",
        "md5": "ad8dfa4e505ef0e3a5d587a5b4705632",
        "output": Path("data/ephemeris/jpl/de441_part-2.bsp"),
    },
}


def md5sum(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, output: Path, expected_md5: str, quiet: bool = False) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and md5sum(output) == expected_md5:
        if not quiet:
            print(f"JPL kernel already present: {output}")
        return output

    with tempfile.NamedTemporaryFile(dir=str(output.parent), delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        if not quiet:
            print(f"Downloading {url} -> {output}")
        with urllib.request.urlopen(url, timeout=120) as response, tmp_path.open("wb") as fh:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                fh.write(chunk)
        actual = md5sum(tmp_path)
        if actual != expected_md5:
            raise RuntimeError(f"Checksum mismatch for {url}: expected {expected_md5}, got {actual}")
        tmp_path.replace(output)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    if not quiet:
        print(f"Verified JPL kernel {output} md5={expected_md5}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel", choices=sorted(KERNELS), default="de440")
    parser.add_argument("--url", default=None)
    parser.add_argument("--md5", default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    preset = KERNELS[args.kernel]
    url = args.url or str(preset["url"])
    expected_md5 = args.md5 or str(preset["md5"])
    output = args.output or preset["output"]
    try:
        download(url, output, expected_md5, quiet=args.quiet)
    except (OSError, RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
