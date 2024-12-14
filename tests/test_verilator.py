"""
Test if the package works.
"""

import verilator
import subprocess

# from packaging.version import Version
import site
from pathlib import Path


def _parse_version_stdout(stdout: bytes):
    """Parse the version from stdout. Used to test if verilator works."""
    major, minor = stdout.decode().strip().strip("rev ").split(".")
    return major, minor[1:]


def test_verilator():
    """"""
    # Print the version
    result = verilator.verilator(["--version"], capture_output=True)

    # Parse the result
    vbin_maj, vbin_min = _parse_version_stdout(result.stdout)

    vpkg_maj, vpkg_min, vpkg_patch = verilator.__version__.split(".")
    # Make sure the version run by verilator matches
    assert vbin_maj == vpkg_maj
    assert vbin_min == vpkg_min


def test_verilator_cli():
    """"""
    # Run subprocess instead. Print the version.
    result = subprocess.run(["verilator", "--version"], capture_output=True, check=True)

    # Parse the result
    vbin_maj, vbin_min = _parse_version_stdout(result.stdout)

    vpkg_maj, vpkg_min, vpkg_patch = verilator.__version__.split(".")
    # Make sure the version run by verilator matches
    assert vbin_maj == vpkg_maj
    assert vbin_min == vpkg_min


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
