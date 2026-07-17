#!/usr/bin/env python3
"""Download and verify NAIF JPL SPK kernels used by Parva."""

from __future__ import annotations

import argparse
import sys
import tempfile
import urllib.request
from pathlib import Path

from app.panchanga.spk_kernel import SpkValidationError, validate_planetary_spk

KERNELS = {
    "de440": {
        "url": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440.bsp",
        "sha256": "a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5",
        "size": 119_799_808,
        "output": Path("data/ephemeris/jpl/de440.bsp"),
    },
    "de441-part1": {
        "url": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de441_part-1.bsp",
        "sha256": None,
        "size": 1_651_119_104,
        "output": Path("data/ephemeris/jpl/de441_part-1.bsp"),
    },
    "de441-part2": {
        "url": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de441_part-2.bsp",
        "sha256": None,
        "size": 1_656_830_976,
        "output": Path("data/ephemeris/jpl/de441_part-2.bsp"),
    },
}


def download(
    url: str,
    output: Path,
    expected_sha256: str,
    expected_size: int,
    quiet: bool = False,
) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        try:
            validate_planetary_spk(
                output,
                expected_sha256=expected_sha256,
                expected_size=expected_size,
            )
        except (OSError, SpkValidationError):
            pass
        else:
            if not quiet:
                print(f"JPL kernel already present and verified: {output}")
            return output

    with tempfile.NamedTemporaryFile(dir=str(output.parent), delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        if not quiet:
            print(f"Downloading {url} -> {output}")
        with urllib.request.urlopen(url, timeout=120) as response, tmp_path.open("wb") as fh:
            content_length = response.headers.get("Content-Length")
            if content_length is not None and int(content_length) != expected_size:
                raise RuntimeError(
                    f"Content-Length mismatch for {url}: expected {expected_size}, got {content_length}"
                )
            downloaded = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                downloaded += len(chunk)
                if downloaded > expected_size:
                    raise RuntimeError(f"Download exceeded the expected size for {url}")
                fh.write(chunk)
        validate_planetary_spk(
            tmp_path,
            expected_sha256=expected_sha256,
            expected_size=expected_size,
        )
        tmp_path.replace(output)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    if not quiet:
        print(f"Verified JPL kernel {output} sha256={expected_sha256}")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernel", choices=sorted(KERNELS), default="de440")
    parser.add_argument("--url", default=None)
    parser.add_argument("--sha256", default=None)
    parser.add_argument("--size", type=int, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    preset = KERNELS[args.kernel]
    url = args.url or str(preset["url"])
    expected_sha256 = args.sha256 or preset["sha256"]
    if not expected_sha256:
        parser.error(f"--sha256 is required for {args.kernel}")
    expected_size = args.size or int(preset["size"])
    output = args.output or preset["output"]
    try:
        download(url, output, str(expected_sha256), expected_size, quiet=args.quiet)
    except (OSError, RuntimeError, SpkValidationError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
