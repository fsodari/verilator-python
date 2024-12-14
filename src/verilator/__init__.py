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

import importlib.metadata
import sys
from pathlib import Path
import subprocess
import os


def verilator_root() -> Path:
    """
    Get the path to verilator_root.
    This will typically be at site-packages/verilator
    """
    # Verilator is installed in the same directory as this package.
    return Path(__file__).parent.absolute()


def verilator_bin() -> Path:
    """
    Get the path to verilator_bin
    This will typically be at site-packages/verilator/bin
    """
    if sys.platform == "win32":
        return verilator_root() / "bin/verilator_bin.exe"
    else:
        return verilator_root() / "bin/verilator"


def verilator(args: list[str], capture_output: bool = False):
    """
    Run verilator with the given args.

    Returns the return code of
    """

    # Set VERILATOR_ROOT in the environment. Verilator usually requires this.
    os.environ["VERILATOR_ROOT"] = str(verilator_root())

    # Prepend the verilator_exe path to the verilator args.
    command_args = [verilator_bin()] + args

    # Run using subprocess.
    return subprocess.run(command_args, capture_output=capture_output, check=True)


def _verilator_cli() -> int:
    """
    Run verilator using command line arguments.
    Used by __main__

    Otherwise it's probably best to use verilator(sys.argv[1:])
    instead of calling this function.
    """
    result = verilator(sys.argv[1:])
    exit(result.returncode)


__all__ = [
    "verilator",
    "verilator_root",
    "verilator_bin",
]
