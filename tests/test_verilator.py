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
    assert v.major == Version(verilator.__version__).major
    assert v.minor == Version(verilator.__version__).minor


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
    # Check the root.
    verilator_root = verilator.verilator_root()

    # We expect this package to be installed in site-packages.
    assert verilator_root.parent in [Path(p) for p in site.getsitepackages()]

    # Check for expected files.
    assert verilator_root.exists()
    assert verilator.verilator_bin().exists()
    assert Path(verilator_root / "verilator-config.cmake").exists()
