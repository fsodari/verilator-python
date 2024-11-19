#include <nanobind/nanobind.h>

// Verilated model.
#include "Vexample.h"

// MSVC requires this must be defined.
double sc_time_stamp() { return 0; }

// Instatiate the model, and run it through a simulation.
void run_simulation()
{
    Vexample example;
    example.eval();

    for (int i = 0; i < 10; i++)
    {
        example.clk = 1;
        example.eval();
        example.clk = 0;
        example.eval();
    }
}

// Define the nanobind module.
NB_MODULE(_example, m)
{
    m.doc() = "Python Verilator Example";

    m.def("run_simulation", &run_simulation);
}
