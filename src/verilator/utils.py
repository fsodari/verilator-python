from collections.abc import Mapping
from pathlib import Path

from . import verilator


class VerilatorError(Exception):
    pass


def verilate(
    sources: list[Path],
    output_dir: Path | None = None,
    include_dirs: list[Path] | None = None,
    parameters: Mapping[str, str | int | float] | None = None,
    prefix: str | None = None,
    top_module: str | None = None,
    trace_vcd: bool = False,
    trace_fst: bool = False,
    threads: bool = False,
    trace_threads: bool = False,
    verilator_args: list[str] | None = None,
):
    """Run verilator with common options, converting python data types into appropriate arguments."""
    args = [s.as_posix() for s in sources]

    # Output directory
    if output_dir:
        args.extend(["--Mdir", output_dir.as_posix()])

    # Include directories.
    if include_dirs:
        args.extend([f"-I{i}" for i in include_dirs])

    # Override generated module prefix
    if prefix:
        args.extend(["--prefix", prefix])

    # Specify module
    if top_module:
        args.extend(["--top-module", top_module])

    # Choose to use either vcd or fst tracing.
    if trace_vcd:
        args.append("--trace-vcd")
    elif trace_fst:
        args.append("--trace-fst")

    if threads:
        args.append("--threads")
    if trace_threads:
        args.append("--trace-threads")

    # Parameters. Scalar parameters only :(
    if parameters:
        args.extend([f"-G{name}={value}" for name, value in parameters.items()])

    # Extra verilator args.
    if verilator_args:
        args.extend(verilator_args)

    result = verilator(args, capture_output=True, check=False)

    if result.returncode:
        raise VerilatorError(f"Verilate failed: {result.stderr.decode()}")

    return result.stdout.decode()
