#!/usr/bin/env python
import subprocess
from pathlib import Path
import sys


def main() -> int:
    """"""
    output_dir = Path("dist")

    # Windows builds.
    if sys.platform == "win32":
        win_args = [
            "pipx",
            "run",
            "cibuildwheel",
            "--platform",
            "windows",
            "--output-dir",
            output_dir,
        ]
        subprocess.run(win_args, check=True)

    # Mac builds???
    if sys.platform == "darwin":
        mac_args = [
            "pipx",
            "run",
            "cibuildwheel",
            "--platform",
            "macos",
            "--output-dir",
            output_dir,
        ]
        subprocess.run(mac_args, check=True)

    # Always build linux wheels in docker.
    args = [
        "pipx",
        "run",
        "cibuildwheel",
        "--platform",
        "linux",
        "--output-dir",
        output_dir,
    ]
    proc = subprocess.run(args)
    return proc.returncode


if __name__ == "__main__":
    exit(main())
