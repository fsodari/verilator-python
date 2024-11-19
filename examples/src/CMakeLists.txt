nanobind_add_module(_example _example.cpp STABLE_ABI)
verilate(_example TRACE
    SOURCES example.sv)

nanobind_add_stub(
    _example_stub
    INSTALL_TIME
    MODULE _example
    OUTPUT example/_example.pyi
    PYTHON_PATH $<TARGET_FILE_DIR:_example>
    DEPENDS _example
    MARKER_FILE example/py.typed)

install(TARGETS _example LIBRARY DESTINATION example)
    