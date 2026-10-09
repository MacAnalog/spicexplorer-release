# 5-Transistor OTA Example

This example demonstrates a complete design and sizing flow for a classic 5-transistor Operational Transconductance Amplifier (OTA), a fundamental building block in analog integrated circuits.

## Circuit Overview

The 5T-OTA consists of a differential pair with a current mirror load. It's a simple yet versatile amplifier used in many applications, such as filters, integrators, and voltage-controlled oscillators.

## Directory Structure

This example is structured for the IHP SG13G2 open-source PDK.

-   **/ihp-sg13g2/xschem/**: Contains the circuit schematics (`.sch` files) for the OTA and its various testbenches, created using Xschem.
-   **/ihp-sg13g2/spice/**: Holds the SPICE netlists for simulation. This includes the main OTA netlist and testbench files for loop gain, noise, transient, and AC analysis.
-   **/ihp-sg13g2/sizing/**: Contains marimo notebooks (`uv run marimo edit <name>.py` opens one) that use `spicexplorer` to perform automated sizing of the OTA with the `Nevergrad` (evolutionary) optimizer. It also ships a **multi-corner PVT** sub-example — `run_multicorner_5t.py` (runner), `project_setup_multicorner.yaml` (the `pvt.mode: multi` setup), and `multicorner_results.md` (the recorded results).

> **Note:** the single-objective `Nevergrad` notebook and the multi-corner runner work with the base `uv sync`. `explore_load_optimization_trace.py` does not run today: it reads `checkpoints/LHSSearch_2000.json`, which is not committed, and the saved outputs of its last run are in `explore_load_optimization_trace_recorded_outputs.py` beside it (data in `explore_load_optimization_trace.recorded-outputs.csv`); run it to print the recorded outputs and rebuild the figures. The two multi-spec sizing notebooks (Ax and Nevergrad) were deleted in the 2026-09 close-out: they imported `symxplorer`, the earlier package the optimizer code came from, which the platform does not install.
