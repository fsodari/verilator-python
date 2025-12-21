"""
Test if the package works.
"""

import verilator
import subprocess

# from packaging.version import Version
import site
from pathlib import Path
from tempfile import TemporaryDirectory


def _parse_version_stdout(stdout: bytes):
    """Parse the version from stdout. Used to test if verilator works."""
    major, minor_full = stdout.decode().strip().strip("rev ").split(".")

    # Split full version on intermediate builds. Remove leading zero.
    minor = str(int(minor_full.split("-")[0]))
    return major, minor


def test_verilator():
    """"""
    # Print the version
    result = verilator.verilator(["--version"], capture_output=True)

    # Parse the result
    vbin_maj, vbin_min = _parse_version_stdout(result.stdout)

    vpkg_maj, vpkg_min, vpkg_patch = verilator.__version__.split(".")
    # Make sure the version run by verilator matches
    assert vbin_maj == vpkg_maj
    assert vbin_min == vpkg_min


def test_verilator_cli():
    """"""
    # Run subprocess instead. Print the version.
    result = subprocess.run(["verilator", "--version"], capture_output=True, check=True)

    # Parse the result
    vbin_maj, vbin_min = _parse_version_stdout(result.stdout)

    vpkg_maj, vpkg_min, vpkg_patch = verilator.__version__.split(".")
    # Make sure the version run by verilator matches
    assert vbin_maj == vpkg_maj
    assert vbin_min == vpkg_min


def test_verilator_root():
    """"""
    # Check the root.
    verilator_root = verilator.verilator_root()

    # We expect this package to be installed in site-packages.
    assert verilator_root.parent in [Path(p) for p in site.getsitepackages()]

    # Check for expected files.
    assert verilator_root.exists()
    assert verilator.verilator_bin().exists()
    assert Path(verilator_root / "verilator-config.cmake").exists()


# Need to define in code so it can built from sdist.
test_model = """
module TestModel #(
    parameter DW = 24
) (
    input  logic clk,
    input  logic [DW-1:0] d,
    output logic signed [DW-1:0] q
);

always @(posedge clk) begin
    q <= d;
end

endmodule
"""


def test_verilate():
    """"""
    #

    include_dirs = [Path("tests")]
    parameters = {"DW": 8}

    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Generate source files.
        source_file = tmpdir / "TestModel.sv"
        with open(source_file, "w") as fp:
            fp.write(test_model)

        sources = [source_file]
        # Verilate the model, generating a cpp model.
        _stdout = verilator.verilate(
            sources,
            tmpdir,
            include_dirs,
            parameters,
            trace_vcd=True,
            verilator_args=["--cc", "--quiet"],
        )

        # Check that the .h and .cpp files were generated.
        for source in sources:
            prefix = f"V{source.stem}"
            required_suffixes = [".h", ".cpp"]
            for suffix in required_suffixes:
                assert (tmpdir / prefix).with_suffix(suffix).exists()
