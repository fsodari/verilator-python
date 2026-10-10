# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`verilator-dspsim` is a PyPI package that ships a pre-built Verilator installation inside a wheel, plus a thin Python wrapper for running it. There is very little Python here; most of the work is packaging. Not affiliated with Verilator.

Naming, which is easy to mix up:

- Distribution name (pip / `importlib.metadata`): `verilator-dspsim`
- Import name: `verilator` (`src/verilator`). It has to be `verilator` so that CMake's `find_package(verilator)` locates the install in site-packages.
- Console script: `verilator-dspsim` (not `verilator`)

## Commands

The project uses `uv` (Python 3.12, see `.python-version`). Building compiles Verilator from source, so the first build is slow and needs a C++ compiler, flex, bison, and lz4 dev headers, plus autoconf, make, perl and help2man on Linux and macOS (on Windows: MSVC and winflexbison, see `scripts/win-install-winflexbison.ps1`).

```sh
# Install reusing the cached build/ directory (scripts/install.sh)
pip install --no-build-isolation -Cbuild-dir=build -v .
# or
uv sync --no-editable

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

Editable installs are not supported: `verilator_root()` is derived from `__file__`, which in an editable install points at `src/verilator` instead of where the binaries are installed.

Example downstream project (scikit-build-core + nanobind + `verilate()` CMake function):

```sh
# Isolated build: uses verilator-dspsim from PyPI (add --find-links <dir> to use a local wheel)
pip install ./example
# Uses the verilator-dspsim installed in the current environment
pip install --no-build-isolation ./example
python -c "import example;example.run_simulation()"
```

## Architecture

### Build: version drives everything

`pyproject.toml` `project.version` is the single source of truth for which Verilator gets built. The root `CMakeLists.txt` parses `SKBUILD_PROJECT_VERSION` and derives the git tag as `v<major>.0<minor>` (e.g. `5.52.1` → `v5.052`). The patch component is this package's own revision and is not part of the Verilator tag.

To upgrade Verilator, bump the major/minor in `pyproject.toml`; `uv.lock` records the version too and will change.

### Build: two build systems, two layouts

scikit-build-core always drives CMake, but how Verilator itself is built depends on the platform (`VERILATOR_USE_AUTOTOOLS`, default `OFF` on Windows and `ON` elsewhere; override with `-Ccmake.define.VERILATOR_USE_AUTOTOOLS=...`):

- **Windows**: Verilator's own CMake build, pulled in with `FetchContent`. Its install rules lay out the files like a `VERILATOR_ROOT` directory (`bin/`, `include/`, `verilator-config.cmake`).
- **Linux/macOS**: Verilator only supports autotools here, so `ExternalProject_Add` runs `autoconf`, `./configure --prefix=<build>/verilator-install --disable-defenv`, `make`, and `make install` (the man pages need `help2man`). The staging prefix is then copied into the wheel, minus `share/pkgconfig` (`verilator.pc` contains the staging path) and `verilator_bin_dbg` (hundreds of MB, only needed for `verilator --debug`).

`wheel.install-dir = "verilator"` puts the installed tree inside the `verilator` Python package directory, alongside the files from `src/verilator`. The result differs per build system:

| | CMake build | autotools build |
|---|---|---|
| executables | `verilator/bin/` | `verilator/bin/` |
| `VERILATOR_ROOT` | `verilator/` | `verilator/share/verilator/` |

[docs/BuildProcess.md](docs/BuildProcess.md) is the user-facing description of this; keep it in sync.

`wheel.py-api = "py3"` tags the wheel `py3-none-<platform>` since nothing uses the Python C API, so cibuildwheel only builds `cp312-*` and that one wheel per platform serves all Python versions.

In the autotools layout `bin/verilator` computes `VERILATOR_ROOT` from its own location and exits with an error if the environment variable points anywhere else, so the two must stay consistent.

### Runtime wrapper (`src/verilator`)

- `__init__.py`: `verilator_root()` returns `share/verilator` inside the package directory if it exists (autotools layout) and the package directory otherwise (CMake layout). Importing the package sets `os.environ["VERILATOR_ROOT"]` to it as a side effect. `verilator_bin()` is `bin/verilator_bin.exe` on Windows and `bin/verilator` elsewhere, relative to the package directory in both layouts. `verilator(args)` is a `subprocess.run` passthrough; `_verilator_cli` backs both the console script and `python -m verilator`.
- `utils.py`: `verilate()` maps Python arguments onto common Verilator flags and raises `VerilatorError` with stderr on a non-zero exit.

Because scikit-build-core adds site-packages to `CMAKE_PREFIX_PATH`, downstream projects only need `find_package(verilator CONFIG REQUIRED)`, plus `verilator-dspsim` in their `build-system.requires`; `example/` demonstrates this. The build requirement matters because builds are isolated: a verilator-dspsim installed only in the user's environment is invisible to the build unless `--no-build-isolation` is used. A `find_package` failure in a downstream project is almost always this, not the install layout. Both layouts are on CMake's config search path (`<prefix>/verilator/` and `<prefix>/verilator/share/verilator/`).

### Tests

Tests check the installed artifact rather than the source tree: that the binary's `--version` matches the package's major/minor, that the package lives directly under site-packages and `verilator_root()` contains `verilator-config.cmake`, and that verilating a small model produces `.h`/`.cpp` output. The test model is embedded as a string in `tests/test_verilator.py` so tests work from an sdist. cibuildwheel runs the same suite against each built wheel.

### CI / release

`.github/workflows/build_wheels.yaml` builds an sdist plus Windows, manylinux and macOS wheels (64-bit only, no musllinux, no win_arm64) on pushes to `main`, `releases/*`, and `v*` tags. macOS is a matrix over an arm64 and an Intel runner, since cibuildwheel builds for the runner's architecture. Tag pushes starting with `v` publish to PyPI via trusted publishing. Linux and macOS build dependencies are installed through `[tool.cibuildwheel.<platform>] before-all` in `pyproject.toml` (`yum` / `brew`).

`.github/workflows/check_verilator.yaml` makes releases automatic. Daily (and on manual dispatch, with an optional dry run) it runs `scripts/check_verilator_release.py`, which compares Verilator's newest `v<major>.<3-digit minor>` tag with the major/minor in `pyproject.toml`. When Verilator is newer it sets the version to `<major>.<minor>.0`, runs `uv lock`, pushes the commit and a `v<version>` tag to the default branch, and then starts the Build workflow on that tag with `gh workflow run`. The explicit start is required because pushes made with `GITHUB_TOKEN` do not trigger other workflows; this is also why the publish job checks `github.ref` rather than `github.event.ref`. Publishing must stay in `build_wheels.yaml` for PyPI trusted publishing to keep working. Scheduled workflows only run from the default branch.

There is no macOS machine to test on locally, so macOS changes can only be verified by pushing to a `releases/*` branch and checking the workflow run. Use `gh run list`, `gh run watch <id>` and `gh run view <id> --log-failed` to follow the result.
