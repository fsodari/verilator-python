cmake_minimum_required(VERSION 4.2)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX VERSION ${SKBUILD_PROJECT_VERSION})

string(REGEX MATCH "^([0-9]+)\\.([0-9]+)\\.([0-9]+)"
       MY_PROGRAM_VERSION_MATCH ${SKBUILD_PROJECT_VERSION})
set(PROJECT_VERSION_MAJOR ${CMAKE_MATCH_1})
set(PROJECT_VERSION_MINOR ${CMAKE_MATCH_2})
set(PROJECT_VERSION_PATCH ${CMAKE_MATCH_3})

# Format the Verilator tag version as v<major>.0<minor>
set(VERILATOR_TAG_VERSION "v${PROJECT_VERSION_MAJOR}.0${PROJECT_VERSION_MINOR}")
message("Verilator Tag: ${VERILATOR_TAG_VERSION}")

set(VERILATOR_GIT_REPOSITORY https://github.com/verilator/verilator.git)

# Verilator only supports its CMake build on Windows. Everywhere else (Linux, macOS) the
# supported process is autoconf/configure/make, so CMake is only used to drive that build.
# See docs/BuildProcess.md
# Override with -Ccmake.define.VERILATOR_USE_AUTOTOOLS=<ON|OFF>
if(WIN32)
    set(VERILATOR_USE_AUTOTOOLS_DEFAULT OFF)
else()
    set(VERILATOR_USE_AUTOTOOLS_DEFAULT ON)
endif()
option(VERILATOR_USE_AUTOTOOLS
       "Build Verilator with autoconf/configure/make instead of its CMake build"
       ${VERILATOR_USE_AUTOTOOLS_DEFAULT})
message("Verilator autotools build: ${VERILATOR_USE_AUTOTOOLS}")

if(NOT VERILATOR_USE_AUTOTOOLS)
    # Use fetch content to build verilator as a dependency.
    # scikit-build-core will install all CMake targets into the wheel.

    # Building Verilator on Windows requires using CMake, so this is the normal process
    # for building Verilator. Before installing, you must install any dependencies.
    # Follow the Verilator user manual to see how to install.
    # TODO: Maybe I can install flex/bison here too?
    include(FetchContent)
    FetchContent_Declare(
        verilator
        GIT_REPOSITORY ${VERILATOR_GIT_REPOSITORY}
        GIT_TAG ${VERILATOR_TAG_VERSION}
    )
    FetchContent_MakeAvailable(verilator)

    # No need to do anything else.
else()
    # Run the build from the Verilator user manual:
    #   autoconf
    #   ./configure
    #   make -j `nproc`
    #   make install
    # installing into a staging prefix, which is then copied into the wheel.
    include(ExternalProject)
    include(ProcessorCount)

    find_program(AUTOCONF_EXECUTABLE autoconf REQUIRED)
    find_program(MAKE_EXECUTABLE NAMES gmake make REQUIRED)

    if(DEFINED ENV{CMAKE_BUILD_PARALLEL_LEVEL})
        set(VERILATOR_BUILD_JOBS $ENV{CMAKE_BUILD_PARALLEL_LEVEL})
    else()
        ProcessorCount(VERILATOR_BUILD_JOBS)
    endif()
    if(NOT VERILATOR_BUILD_JOBS)
        set(VERILATOR_BUILD_JOBS 1)
    endif()

    set(VERILATOR_STAGING_DIR ${CMAKE_CURRENT_BINARY_DIR}/verilator-install)

    # A VERILATOR_ROOT left over in the environment would redirect parts of the build
    # to another installation.
    set(VERILATOR_BUILD_ENV ${CMAKE_COMMAND} -E env --unset=VERILATOR_ROOT)

    ExternalProject_Add(
        verilator
        GIT_REPOSITORY ${VERILATOR_GIT_REPOSITORY}
        GIT_TAG ${VERILATOR_TAG_VERSION}
        GIT_SHALLOW TRUE
        UPDATE_DISCONNECTED TRUE
        BUILD_IN_SOURCE TRUE
        INSTALL_DIR ${VERILATOR_STAGING_DIR}
        # --disable-defenv: the staging prefix does not exist once the wheel is installed,
        # so don't compile it into the binary. The python wrapper and the installed
        # bin/verilator script both set VERILATOR_ROOT at runtime.
        CONFIGURE_COMMAND ${VERILATOR_BUILD_ENV} ${AUTOCONF_EXECUTABLE}
        COMMAND ${VERILATOR_BUILD_ENV} ./configure --prefix=<INSTALL_DIR> --disable-defenv
        BUILD_COMMAND ${VERILATOR_BUILD_ENV} ${MAKE_EXECUTABLE} -j${VERILATOR_BUILD_JOBS}
        INSTALL_COMMAND ${VERILATOR_BUILD_ENV} ${MAKE_EXECUTABLE} install
        USES_TERMINAL_CONFIGURE TRUE
        USES_TERMINAL_BUILD TRUE
        USES_TERMINAL_INSTALL TRUE
    )

    # The install tree is relocatable (the scripts locate each other with relative paths),
    # except for verilator.pc which contains the staging prefix.
    # verilator_bin_dbg is only needed for "verilator --debug" and is far larger than
    # everything else combined, so leave it (and its redirect script) out of the wheel.
    install(
        DIRECTORY ${VERILATOR_STAGING_DIR}/
        DESTINATION .
        USE_SOURCE_PERMISSIONS
        PATTERN "pkgconfig" EXCLUDE
        PATTERN "verilator_bin_dbg" EXCLUDE
    )
endif()
