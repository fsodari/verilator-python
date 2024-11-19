cmake_minimum_required(VERSION 3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX VERSION ${SKBUILD_PROJECT_VERSION})

find_package(Python COMPONENTS Interpreter Development.Module ${SKBUILD_SABI_MODULE} REQUIRED)
find_package(verilator CONFIG REQUIRED)
find_package(nanobind CONFIG REQUIRED)

message("Found Python: ${Python_EXECUTABLE}")
message("Found Verilator: ${verilator_DIR}")
message("Found Nanobind: ${nanobind_DIR}")

add_subdirectory(src)
