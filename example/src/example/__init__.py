"""
Imports the contents of the nanobind module _example

Test the example by running
python -c "import example;example.run_simulation()"

"""

__version__ = "0.0.1"

# Import contents from the nanobind module.
from ._example import run_simulation
