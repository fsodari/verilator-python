"""
Test if the package works.
"""

import verilator
import subprocess
from packaging.version import Version
import site
from pathlib import Path


def _parse_version_stdout(stdout: bytes):
    """Parse the version from stdout. Used to test if verilator works."""
    return Version(stdout.decode().strip().strip("rev "))


def test_verilator():
    """"""
    # Print the version
    result = verilator.verilator(["--version"], capture_output=True)

    # Parse the result
    v = _parse_version_stdout(result.stdout)

    # Make sure the version run by verilator matches
    assert v == Version(verilator.__version__)


def test_verilator_cli():
    """"""
    # Run subprocess instead. Print the version.
    result = subprocess.run(["verilator", "--version"], capture_output=True, check=True)

    # Parse the result
    v = _parse_version_stdout(result.stdout)

    # Make sure the version run by verilator matches
    assert v == Version(verilator.__version__)


def test_verilator_root():
    """"""
    # We expect this package to be installed at "verilator" in site-packages.
    expected_root = Path(site.getsitepackages()[0]) / "verilator"

    # Check the root.
    verilator_root = verilator.verilator_root()

    # I don't think this proves anything?
    assert verilator_root == expected_root

    # Check for expected files.
    assert Path(verilator_root / "bin/verilator_bin").exists()
    assert Path(verilator_root / "verilator-config.cmake").exists()
