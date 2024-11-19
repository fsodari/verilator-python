__version__ = "5.30.0"
import os
import sys
from pathlib import Path
import subprocess

_verilator_root = Path(__file__).parent
os.environ["VERILATOR_ROOT"] = str(_verilator_root.absolute())

if sys.platform == "linux":
    _verilator_bin = _verilator_root / "bin/verilator"
else:
    _verilator_bin = _verilator_root / "bin/verilator_bin"


def verilator(args: list[str]) -> int:
    """Run verilator with the given args."""
    command_args = [_verilator_bin] + args
    proc = subprocess.run(command_args)
    return proc.returncode


def verilator_cli():
    """Run verilator using command line arguments."""
    verilator(sys.argv[1:])


def verilator_root() -> Path:
    """Get the path to verilator_root"""
    return _verilator_root
