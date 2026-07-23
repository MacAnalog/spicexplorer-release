# Folded Cascode OTA Sizing Optimization

This directory contains files related to the sizing optimization of a folded cascode operational transconductance amplifier (OTA), structured for the IHP SG13G2 open-source PDK.

## Directory Structure

-   **/ihp-sg13g2/xschem/**: Xschem schematics (`.sch`) for the OTA and its testbenches.
-   **/ihp-sg13g2/spice/**: SPICE testbench netlists (`cora_testbench.spice`, plus AC and noise variants).
-   **/ihp-sg13g2/sizing/**: `project_setup.yaml` (the optimizer DSL config) alongside exploratory notebooks (`test_project_setup.ipynb`, `test_spicelib_wrapper.ipynb`, `test_nevergrad_single_obj.ipynb`).

> **TODO:** A standalone runnable sizing script is not yet present here — sizing is currently driven from the notebooks / `project_setup.yaml` above.
