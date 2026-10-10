"""
Verilator wrapper.

Running verilator typically requires having VERILATOR_ROOT set in the environment.
VERILATOR_ROOT is also used by find_package in CMake.

When importing or running this package, this will automatically
set VERILATOR_ROOT in the environment before running verilator.

When using this with scikit-build-core, scikit-build core will add the
site-packages directory to CMAKE_PREFIX_PATH, so find_package(verilator)
should work without any extra hints.

When using just CMake, you may need to set VERILATOR_ROOT env variable,
manually or set CMAKE_PREFIX_PATH.

run this python command to get verilator_root for convenience
python -c "import verilator;print(verilator.verilator_root())"
"""

# Use same version number as the checked out verilator version.
import importlib.metadata

__version__ = importlib.metadata.version("verilator-dspsim")

import os
import subprocess
import sys
from pathlib import Path


def _package_dir() -> Path:
    """The directory of this package, which is the prefix verilator is installed to."""
    return Path(__file__).parent.absolute()


def verilator_root() -> Path:
    """
    Get the path to verilator_root.

    This depends on how verilator was built. The CMake build (Windows) installs
    VERILATOR_ROOT directly into the package: site-packages/verilator
    The autotools build (Linux, macOS) installs into the package as a prefix,
    so VERILATOR_ROOT is at site-packages/verilator/share/verilator
    """
    share_root = _package_dir() / "share" / "verilator"
    if share_root.is_dir():
        return share_root
    return _package_dir()


# Set VERILATOR_ROOT in the environment when this package is imported. Verilator requires this.
os.environ["VERILATOR_ROOT"] = str(verilator_root())


def verilator_bin() -> Path:
    """
    Get the path to the verilator executable.
    This will typically be at site-packages/verilator/bin
    """
    if sys.platform == "win32":
        return _package_dir() / "bin/verilator_bin.exe"
    else:
        return _package_dir() / "bin/verilator"


def verilator(args: list[str], capture_output: bool = False, check: bool = False):
    """
    Run verilator with the given args.

    Returns the result of subprocess.run.
    """

    # Prepend the verilator_exe path to the verilator args.
    command_args = [verilator_bin()] + args

    # Run using subprocess.
    return subprocess.run(command_args, capture_output=capture_output, check=check)


def _verilator_cli() -> int:
    """
    Run verilator using command line arguments.
    Used by __main__

    Otherwise it's probably best to use verilator(sys.argv[1:])
    instead of calling this function.
    """
    result = verilator(sys.argv[1:], check=False)
    sys.exit(result.returncode)


__all__ = [
    "verilator",
    "verilator_bin",
    "verilator_root",
]
