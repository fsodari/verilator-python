"""
Run the verilator_cli command when running this package as a module.

python -m verilator

Alternatively, this package will install scripts in the python environment under bin or Scripts
This directory is on the path so you can just run "verilator" on the command line.

I'm not sure what happens if verilator is already on the path elsewhere...

Either option is available for use.
"""

from . import _verilator_cli

if __name__ == "__main__":
    exit(_verilator_cli())
