# Build Process

scikit-build-core runs CMake on every platform, but verilator itself is built with whichever
build system verilator supports on that platform. The choice is made in the root `CMakeLists.txt`
with the `VERILATOR_USE_AUTOTOOLS` option, which defaults to `OFF` on Windows and `ON` everywhere else.

The verilator version is taken from the version in `pyproject.toml`: `5.52.x` builds the tag `v5.052`.

## Linux and macOS: autotools

This is the build process from the verilator user manual:

```
autoconf         # Create ./configure script
./configure      # Configure and create Makefile
make -j `nproc`  # Build Verilator itself (if error, try just 'make')
sudo make install
```

CMake runs these steps with `ExternalProject_Add`, with two differences:

- `./configure --prefix=<build dir>/verilator-install --disable-defenv`. Verilator is installed
  into a staging directory instead of the system (no `sudo`), and the staging path is not compiled
  into the binary since it won't exist once the wheel is installed.
- The staging directory is copied into the wheel without `verilator_bin_dbg` (over 200 MB, only
  needed for `verilator --debug`) and without `share/pkgconfig/verilator.pc` (it contains the staging path).

Requirements: a C++ compiler, autoconf, make, flex, bison, perl, python3 and help2man (for the man pages).
cibuildwheel installs these with `yum` on Linux and `brew` on macOS, see `before-all` in `pyproject.toml`.

## Windows: CMake

Verilator's own CMake build is added with `FetchContent` and scikit-build-core installs its targets
into the wheel. This requires MSVC and winflexbison, with `WIN_FLEX_BISON` set to its install
directory (`scripts/win-install-winflexbison.ps1`).

## Installed layout

Both builds install into the python package directory, `site-packages/verilator`, but the layouts differ.

| | Linux, macOS | Windows |
|---|---|---|
| executables | `verilator/bin` | `verilator/bin` |
| `VERILATOR_ROOT` | `verilator/share/verilator` | `verilator` |
| man pages | `verilator/share/man` | not installed |

Use `verilator.verilator_root()` and `verilator.verilator_bin()` instead of hardcoding paths.
`find_package(verilator)` finds either layout when site-packages is on `CMAKE_PREFIX_PATH`,
which scikit-build-core does automatically.

## Wheels

The wheels don't use the Python C API, so they are tagged `py3-none-<platform>` and one wheel per
platform works for every supported python version. Editable installs are not supported.

To use the other build system for testing:

```
pip install -Ccmake.define.VERILATOR_USE_AUTOTOOLS=OFF .
```
