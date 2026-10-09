# Case-study notebooks

Three **marimo notebooks**: plain `.py` files that store no outputs, so every run recomputes the
tables, figures and simulations from the committed DUT netlists, testbenches and layout files. Each
replaces a jupytext percent-format source and the executed `.ipynb` built from it, cell for cell.

| Notebook | Runs on | Content |
|---|---|---|
| [`01_schematic_sizing.py`](01_schematic_sizing.py) | ngspice and the IHP SG13G2 open PDK | 3 DUT schematics, testbenches, nominal sizing, bias + S-parameter + eye characterization vs the EIC golden reference |
| [`02_layout_in_the_loop.py`](02_layout_in_the_loop.py) | the layout lane, listed in the notebook's first cell (gdsfactory, kpex, KLayout; the author's conda environment `ai_env`) | gdsfactory layout generation, DRC/LVS signoff, kpex PEX, and layout + electrical co-optimization (nx, tail, R_C, R_B, C_deg, V_casc) with the full toolchain in the loop; closes back to the schematic level |
| [`03_signoff.py`](03_signoff.py) | ngspice and the IHP SG13G2 open PDK; §0 and §0b read files that are in no repository | full signoff — DC transfer/DAC levels/swing, transient bias ramp + tran-vs-ac method cross-check, S21/S11/S22 sweeps, 48 GBd eye — running the *same* `driver_lib` benches on the schematic DUTs and the kpex post-layout netlist (`pex_sim.wrap_layout_dut` + `dut_ref=`); master table vs paper specs / paper measurements / EIC golden; documents the EIC-had-no-layout evidence and the two residual gaps (post-layout S22, swing) |

## Running

**Set the PDK, then open or run a notebook.** `testbenches/driver_lib.py` reads the models from
`$PDK_ROOT/$PDK` and falls back to `~/local/pdks/ihp-sg13g2`. The Python environment needs marimo,
numpy, matplotlib, pyyaml, pandas, IPython and the `klayout` module; the platform venv holds all of
them.

```sh
export PDK_ROOT=$HOME/local/pdks PDK=ihp-sg13g2
marimo edit 01_schematic_sizing.py              # interactive: tables and figures render in the browser
python 01_schematic_sizing.py                   # script: every cell in dependency order, exit 1 on the first cell that raises
NB_BUDGET=14 python 02_layout_in_the_loop.py    # on the layout lane only
```

- **A script run prints text only.** The tables that `md_table()` shows through
  `display(Markdown(...))` and the `display(Image(...))` figures print as
  `<IPython.core.display.Markdown object>` and `<IPython.core.display.Image object>`; `marimo edit`
  and `marimo export html <notebook>.py -o <file>.html` render them.
- **Notebook 02** runs the real signoff/PEX/simulate chain per optimizer trial (~30–90 s each;
  `NB_BUDGET` sets the trial count, default 8). Trial workspaces land in `nb_opt/` beside the
  notebook (only the best trial is kept).
- **Notebook 03** reuses the best-trial PEX netlist (`layout/out/pex/dut_pam4_best_post.spice`,
  copied from `nb_opt/pam4_best/`); regenerate it via notebook 02 or `layout/pex_sim.py` if absent.
  §0 reads the EIC-designer project (`~/code/EIC-designer/projects/lumped-broadband-driver/`) and
  prints a note when it is absent. §0b reads the kpex netlist
  `layout/out/pex/pam4/dut_pam4_nomim__pam4drv_pam4_lay/pam4drv_pam4_lay_k25d_pex_netlist.spice`,
  which `layout/pex_sim.py` writes on the layout lane and which is not committed; without it §0b
  raises FileNotFoundError, `python 03_signoff.py` stops there, and `marimo edit` runs the other
  cells, none of which reads a name §0b defines.

## Recorded outputs

The saved outputs of the last Jupyter run of two notebooks are kept beside them as static HTML,
each output under the code cell that produced it (home paths read `/home/<user>/`):

| Record | Why it is kept |
|---|---|
| [`02_layout_in_the_loop.recorded-outputs.html`](02_layout_in_the_loop.recorded-outputs.html) | 8 optimizer trials on the layout lane; the optimizer (nevergrad TwoPointsDE) is stochastic, so a re-run gives a different trial table |
| [`03_signoff.recorded-outputs.html`](03_signoff.recorded-outputs.html) | §0 and §0b read files that are in no repository; this is their only record |

Notebook 01 has no record: it reproduces its saved tables on ngspice and the open PDK.
