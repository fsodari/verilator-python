"""
Check if verilator has published a release newer than the one this package builds.

If so, update the version in pyproject.toml to <major>.<minor>.0

Used by .github/workflows/check_verilator.yaml. Writes "release" (true/false) and "version"
to GITHUB_OUTPUT when it is set.

python scripts/check_verilator_release.py [--dry-run]
"""

import argparse
import os
import re
import subprocess
from pathlib import Path

VERILATOR_REPOSITORY = "https://github.com/verilator/verilator.git"
PYPROJECT = Path(__file__).parent.parent / "pyproject.toml"

# Verilator release tags are v<major>.<3 digit minor>, e.g. v5.052
VERILATOR_TAG = re.compile(r"refs/tags/v(\d+)\.(\d{3})$")
# The first version in pyproject.toml is the project version.
PROJECT_VERSION = re.compile(r'^version = "(\d+)\.(\d+)\.(\d+)"$', re.MULTILINE)


def latest_verilator_release() -> tuple[int, int]:
    """Get the (major, minor) of the newest verilator release tag."""
    result = subprocess.run(
        ["git", "ls-remote", "--tags", "--refs", VERILATOR_REPOSITORY, "v*"],
        capture_output=True,
        check=True,
        text=True,
    )
    releases = [
        (int(m.group(1)), int(m.group(2)))
        for line in result.stdout.splitlines()
        if (m := VERILATOR_TAG.search(line))
    ]
    if not releases:
        raise RuntimeError("No verilator release tags found.")
    return max(releases)


def project_version(pyproject: str) -> tuple[int, int, int]:
    match = PROJECT_VERSION.search(pyproject)
    if not match:
        raise RuntimeError(f"No version found in {PYPROJECT}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't modify pyproject.toml"
    )
    args = parser.parse_args()

    pyproject = PYPROJECT.read_text()
    current = project_version(pyproject)
    latest = latest_verilator_release()

    release = latest > current[:2]
    if release:
        version = f"{latest[0]}.{latest[1]}.0"
        if not args.dry_run:
            PYPROJECT.write_text(
                PROJECT_VERSION.sub(f'version = "{version}"', pyproject, count=1)
            )
    else:
        version = ".".join(str(v) for v in current)

    print(f"Latest verilator release: v{latest[0]}.{latest[1]:03}")
    print(f"Current project version: {'.'.join(str(v) for v in current)}")
    print(f"New release: {version}" if release else "Up to date.")

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as fp:
            fp.write(f"release={str(release).lower()}\n")
            fp.write(f"version={version}\n")


if __name__ == "__main__":
    main()
