cmake_minimum_required(VERSION 3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX VERSION ${SKBUILD_PROJECT_VERSION})

# Use fetch content to build verilator as a dependency.
# scikit-build-core will install all CMake targets into the wheel.

# Building Verilator on Windows requires using CMake, so this is the normal process
# for building Verilator. Before installing, you must install any dependencies. 
# Follow the Verilator user manual to see how to install.
# TODO: Maybe I can install flex/bison here too?

# Alegedly, building verilator with CMake on linux is still experimental.
# I am using Ubuntu 22.04 on WSL, and it seems to work just fine.
include(FetchContent)
FetchContent_Declare(
    verilator
    GIT_REPOSITORY https://github.com/verilator/verilator.git
    GIT_TAG v5.030)
FetchContent_MakeAvailable(verilator)

# No need to do anything else.
