#include "nanobind/nanobind.h"
#include "Vexample.h"

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
NB_MODULE(_example, m)
{
    m.doc() = "Python Verilator Example";

    m.def("run_simulation", &run_simulation);
}
