# Case-study notebooks

Authored as **jupytext percent-format `.py` sources** (the `.py` files are
the single source of truth; the committed `.ipynb` are executed outputs).

| Source | Notebook | Content |
|---|---|---|
| `01_schematic_sizing.py` | `01_schematic_sizing.ipynb` | 3 DUT schematics, testbenches, nominal sizing, bias + S-parameter + eye characterization vs the EIC golden reference |
| `02_layout_in_the_loop.py` | `02_layout_in_the_loop.ipynb` | gdsfactory layout generation, DRC/LVS signoff, kpex PEX, and layout + electrical co-optimization (nx, tail, R_C, R_B, C_deg, V_casc) with the full toolchain in the loop; closes back to the schematic level |
| `03_signoff.py` | `03_signoff.ipynb` | full signoff — DC transfer/DAC levels/swing, transient bias ramp + tran-vs-ac method cross-check, S21/S11/S22 sweeps, 48 GBd eye — running the *same* `driver_lib` benches on the schematic DUTs and the kpex post-layout netlist (`pex_sim.wrap_layout_dut` + `dut_ref=`); master table vs paper specs / paper measurements / EIC golden; documents the EIC-had-no-layout evidence and the two residual gaps (post-layout S22, swing) |

Build / re-execute (conda `ai_env`; `PDK_ROOT=$HOME/local/pdks`):

```sh
jupytext --sync 01_schematic_sizing.py            # .py <-> .ipynb pairing
jupytext --to notebook --execute 01_schematic_sizing.py
NB_BUDGET=14 jupytext --to notebook --execute 02_layout_in_the_loop.py
```

Notebook 02 runs the real signoff/PEX/simulate chain per optimizer trial
(~30–90 s each; `NB_BUDGET` sets the trial count). Trial workspaces land in
`nb_opt/` (only the best trial is kept).

Notebook 03 build:

```sh
jupytext --to notebook --execute 03_signoff.py
```

It reuses the best-trial PEX netlist (`layout/out/pex/dut_pam4_best_post.spice`,
copied from `nb_opt/pam4_best/`); regenerate it via notebook 02 or
`layout/pex_sim.py` if absent.
