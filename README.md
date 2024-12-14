# Verilator Python

This python package contains a pre-built installation of verilator, and a python wrapper to run verilator. It should function exactly the same as if you installed verilator through normal means.

Installing this python package will install "verilator.exe" into the python environments scripts/bin folder, so it can be ran and can easily be found by CMake.

The main goal of this project is to simplify distributing verilator and using it within a python application.

This project is not affiliated with Verilator.

# Installation


Verilator requires that the operating system used to build verilator is the same as the operating system used to run verilator, so wheels built on windows should work well.

Otherwise, you can build from source. This requires having a compatible compiler installed, and any dependencies. Read the verilator user manual for more information.


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

editable install
```
pip install --no-build-isolation -Cbuild-dir=build --config-settings=editable.rebuild=true -v -e .
```

## Example Project

The example project "example" in the root of this repository
uses scikit-build-core, nanobind, and verilator to build a simple
verilator simulation wrapped in a python package.

You will need to have am appropriate compiler installed.
Windows: MSVC, Linux: gcc, Mac: clang? (I don't have a Mac)

- Install the verilator package from pypi.org, or from source.

- Build and install the example python extension

- Run the example

```
pip install verilator-dspsim
pip install ./example
python -c "import example;example.run_simulation()"
```
