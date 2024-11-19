cmake_minimum_required(VERSION 3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX VERSION ${SKBUILD_PROJECT_VERSION})

include(FetchContent)
FetchContent_Declare(
    verilator
    GIT_REPOSITORY https://github.com/verilator/verilator.git
    GIT_TAG v5.030)
FetchContent_MakeAvailable(verilator)
