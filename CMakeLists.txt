cmake_minimum_required(VERSION 3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX VERSION ${SKBUILD_PROJECT_VERSION})

string(REGEX MATCH "^([0-9]+)\\.([0-9]+)\\.([0-9]+)"
       MY_PROGRAM_VERSION_MATCH ${SKBUILD_PROJECT_VERSION})
set(PROJECT_VERSION_MAJOR ${CMAKE_MATCH_1})
set(PROJECT_VERSION_MINOR ${CMAKE_MATCH_2})
set(PROJECT_VERSION_PATCH ${CMAKE_MATCH_3})

set(VERILATOR_TAG_VERSION "v${PROJECT_VERSION_MAJOR}.0${PROJECT_VERSION_MINOR}")
message("Verilator Tag: ${VERILATOR_TAG_VERSION}")

# Use fetch content to build verilator as a dependency.
# scikit-build-core will install all CMake targets into the wheel.

# Building Verilator on Windows requires using CMake, so this is the normal process
# for building Verilator. Before installing, you must install any dependencies. 
# Follow the Verilator user manual to see how to install.
# TODO: Maybe I can install flex/bison here too?

# Alegedly, building verilator with CMake on linux is still experimental.
# I am using Ubuntu 24.04 on WSL, and manylinux_2_28 and it seems to work just fine.
include(FetchContent)
FetchContent_Declare(
    verilator
    GIT_REPOSITORY https://github.com/verilator/verilator.git
    GIT_TAG ${VERILATOR_TAG_VERSION})
FetchContent_MakeAvailable(verilator)

# No need to do anything else.
