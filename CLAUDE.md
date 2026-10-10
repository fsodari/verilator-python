# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`verilator-dspsim` is a PyPI package that ships a pre-built Verilator installation inside a wheel, plus a thin Python wrapper for running it. There is very little Python here; most of the work is packaging. Not affiliated with Verilator.

Naming, which is easy to mix up:

- Distribution name (pip / `importlib.metadata`): `verilator-dspsim`
- Import name: `verilator` (`src/verilator`). It has to be `verilator` so that CMake's `find_package(verilator)` locates the install in site-packages.
- Console script: `verilator-dspsim` (not `verilator`)

Some docstrings and the README still mention `site-packages/verilator_dspsim` or a `verilator` script; those are stale.

## Commands

The project uses `uv` (Python 3.12, see `.python-version`). Building compiles Verilator from source, so the first build is slow and needs a C++ compiler, flex, bison, and lz4 dev headers, plus autoconf, make, perl and help2man on Linux (on Windows: MSVC and winflexbison, see `scripts/win-install-winflexbison.ps1`).

```sh
# Editable install reusing the cached build/ directory (scripts/einstall.sh)
pip install --no-build-isolation -Cbuild-dir=build --config-settings=editable.rebuild=true -v -e .

# Regular install reusing build/ (scripts/install.sh)
pip install --no-build-isolation -Cbuild-dir=build -v .

# Tests (require the package to be installed; they run the real verilator binary)
pytest tests
pytest tests/test_verilator.py::test_verilate

# Lint / format
ruff check .
ruff format .

# sdist + wheels as CI builds them (scripts/cibw.sh)
uv build --sdist
uvx cibuildwheel --platform linux --output-dir dist
```

`--no-build-isolation` requires `scikit-build-core` in the environment (it is in the `dev` dependency group).

Example downstream project (scikit-build-core + nanobind + `verilate()` CMake function):

```sh
pip install ./example
python -c "import example;example.run_simulation()"
```

## Architecture

### Build: version drives everything

`pyproject.toml` `project.version` is the single source of truth for which Verilator gets built. The root `CMakeLists.txt` parses `SKBUILD_PROJECT_VERSION` and derives the git tag as `v<major>.0<minor>` (e.g. `5.52.1` → `v5.052`). The patch component is this package's own revision and is not part of the Verilator tag.

To upgrade Verilator, bump the major/minor in `pyproject.toml`; `uv.lock` records the version too and will change.

### Build: two build systems, two layouts

scikit-build-core always drives CMake, but how Verilator itself is built depends on the platform (`VERILATOR_USE_AUTOTOOLS`, default `OFF` on Windows and `ON` elsewhere; override with `-Ccmake.define.VERILATOR_USE_AUTOTOOLS=...`):

- **Windows**: Verilator's own CMake build, pulled in with `FetchContent`. Its install rules lay out the files like a `VERILATOR_ROOT` directory (`bin/`, `include/`, `verilator-config.cmake`).
- **Linux/other**: Verilator only supports autotools here, so `ExternalProject_Add` runs `autoconf`, `./configure --prefix=<build>/verilator-install --disable-defenv`, `make`, and `make install` (the man pages need `help2man`). The staging prefix is then copied into the wheel, minus `share/pkgconfig` (`verilator.pc` contains the staging path) and `verilator_bin_dbg` (hundreds of MB, only needed for `verilator --debug`).

`wheel.install-dir = "verilator"` puts the installed tree inside the `verilator` Python package directory, alongside the files from `src/verilator`. The result differs per build system:

| | CMake build | autotools build |
|---|---|---|
| executables | `verilator/bin/` | `verilator/bin/` |
| `VERILATOR_ROOT` | `verilator/` | `verilator/share/verilator/` |

In the autotools layout `bin/verilator` computes `VERILATOR_ROOT` from its own location and exits with an error if the environment variable points anywhere else, so the two must stay consistent.

### Runtime wrapper (`src/verilator`)

- `__init__.py`: `verilator_root()` returns `share/verilator` inside the package directory if it exists (autotools layout) and the package directory otherwise (CMake layout). Importing the package sets `os.environ["VERILATOR_ROOT"]` to it as a side effect. `verilator_bin()` is `bin/verilator_bin.exe` on Windows and `bin/verilator` elsewhere, relative to the package directory in both layouts. `verilator(args)` is a `subprocess.run` passthrough; `_verilator_cli` backs both the console script and `python -m verilator`.
- `utils.py`: `verilate()` maps Python arguments onto common Verilator flags and raises `VerilatorError` with stderr on a non-zero exit.

Because scikit-build-core adds site-packages to `CMAKE_PREFIX_PATH`, downstream projects only need `find_package(verilator CONFIG REQUIRED)`; `example/` demonstrates this. Both layouts are on CMake's config search path (`<prefix>/verilator/` and `<prefix>/verilator/share/verilator/`).

### Tests

Tests check the installed artifact rather than the source tree: that the binary's `--version` matches the package's major/minor, that the package lives directly under site-packages and `verilator_root()` contains `verilator-config.cmake`, and that verilating a small model produces `.h`/`.cpp` output. The test model is embedded as a string in `tests/test_verilator.py` so tests work from an sdist. cibuildwheel runs the same suite against each built wheel.

### CI / release

`.github/workflows/build_wheels.yaml` builds an sdist plus Windows and manylinux wheels (64-bit only, no musllinux, no win_arm64) on pushes to `main`, `releases/*`, and `v*` tags. Tag pushes starting with `v` publish to PyPI via trusted publishing. Linux build dependencies are installed through `[tool.cibuildwheel.linux] before-all` in `pyproject.toml`.
