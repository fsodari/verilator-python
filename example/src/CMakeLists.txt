# Create nanobind module
nanobind_add_module(_example _example.cpp)

# Verilate the verilog module and link it to the nanobind module.
verilate(_example SOURCES example.sv)

# Generate nanobind type stubs.
nanobind_add_stub(
    _example_stub
    INSTALL_TIME
    MODULE _example
    OUTPUT example/_example.pyi
    PYTHON_PATH $<TARGET_FILE_DIR:_example>
    DEPENDS _example
    MARKER_FILE example/py.typed)

# Install the nanobind wheel.
install(TARGETS _example LIBRARY DESTINATION example)
install(FILES _example.cpp DESTINATION ${SKBUILD_HEADERS_DIR}) 