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

import sys
from pathlib import Path
import subprocess
import os
from typing import Mapping


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


def verilator(args: list[str], capture_output: bool = False, check: bool = False):
    """
    Run verilator with the given args.

    Returns the result of subprocess.run.
    """

    # Set VERILATOR_ROOT in the environment. Verilator usually requires this.
    os.environ["VERILATOR_ROOT"] = str(verilator_root())

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
    exit(result.returncode)


def verilate(
    sources: list[Path],
    output_dir: Path | None = None,
    include_dirs: list[Path] = [],
    parameters: Mapping[str, str | int | float] = {},
    prefix: str | None = None,
    top_module: str | None = None,
    trace_vcd: bool = False,
    trace_fst: bool = False,
    threads: bool = False,
    trace_threads: bool = False,
    verilator_args: list[str] = [],
):
    """Run verilator with common options, converting python data types into appropriate arguments."""
    args = [s.as_posix() for s in sources]

    # Output directory
    if output_dir:
        args.extend(["--Mdir", output_dir.as_posix()])

    # Include directories.
    args.extend([f"-I{i}" for i in include_dirs])

    # Override generated module prefix
    if prefix:
        args.extend(["--prefix", prefix])

    # Specify module
    if top_module:
        args.extend(["--top-module", top_module])

    # Choose to use either vcd or fst tracing.
    if trace_vcd:
        args.append("--trace-vcd")
    elif trace_fst:
        args.append("--trace-fst")

    if threads:
        args.append("--threads")
    if trace_threads:
        args.append("--trace-threads")

    # Parameters. Scalar parameters only :(
    args.extend([f"-G{name}={value}" for name, value in parameters.items()])

    # Extra verilator args.
    args.extend(verilator_args)

    result = verilator(args, capture_output=True, check=False)

    if result.returncode:
        raise Exception(f"Verilate failed: {result.stderr.decode()}")

    return result.stdout.decode()


__all__ = [
    "verilator",
    "verilator_root",
    "verilator_bin",
    "verilate",
]
