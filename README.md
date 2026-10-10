# Verilator Python

This python package contains a pre-built installation of verilator, and a python wrapper to run verilator. It should function exactly the same as if you installed verilator through normal means.

Installing this python package will install "verilator-dspsim" into the python environments scripts/bin folder, which runs verilator with the same arguments. It can also be run with "python -m verilator". The verilator installation is placed in site-packages/verilator, where it can be found by find_package(verilator) in CMake.

The main goal of this project is to simplify distributing verilator and using it within a python application.

This project is not affiliated with Verilator.

# Installation


Pre-built wheels are available for Windows, Linux (manylinux) and macOS. Each wheel works with any supported python version.

Otherwise, you can build from source. This requires having a compatible compiler installed, and any dependencies. Read the verilator user manual for more information.

On Windows, verilator is built with its CMake build. On Linux and macOS, CMake is only used to run verilator's supported autoconf/configure/make build, so autoconf, make, flex, bison, perl and help2man are required. See [docs/BuildProcess.md](docs/BuildProcess.md) for details.


## Install Options

pypi.org
```
pip install verilator-dspsim
```

from source
```
pip install .
```

cached build directory
```
pip install --no-build-isolation -Cbuild-dir=build -v .
```

Editable installs are not supported.

## Example Project

The example project "example" in the root of this repository
uses scikit-build-core, nanobind, and verilator to build a simple
verilator simulation wrapped in a python package.

You will need to have am appropriate compiler installed.
Windows: MSVC, Linux: gcc, Mac: clang

- Install the verilator package from pypi.org, or from source.

- Build and install the example python extension

- Run the example

```
pip install verilator-dspsim
pip install ./example
python -c "import example;example.run_simulation()"
```
