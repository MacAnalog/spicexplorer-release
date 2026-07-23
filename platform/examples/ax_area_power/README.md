# Ax revival + area/power optimization demo

Two demos in one, on **two amplifier topologies**:

- **`amp_020`** — the unsized two-stage Miller OTA (`analog-db amp_020_two_stage_miller_cmfb`).
- **`amp_008`** — the three-stage **nested-Miller (NMCF)** op-amp (`analog-db amp_008_leung_nmcf`), a
  wider 15-knob search space that exercises the same path on a harder problem.

Both on `ihp-sg13g2` / ngspice.

1. **Engine swap** — the same `project_setup.yaml` runs under either optimizer, chosen by
   `optimizer_config.type` (`nevergrad` → evolutionary, `bayesian_ax` → Ax Bayesian). The Ax
   backend is revived per `doc/plan_ax_sprint.md`.
2. **Area + power as first-class metrics** — the `*_area_power.yaml` files add two target specs on
   top of the amplifier ones (gain / UGF / PM):
   - **`power`** — a Tier-1 op-point measurement `|I_supply|·VDD` (µW), `{meas: power_uw, probe: i(i_supply), vdd: …}`.
   - **`active_area`** — a **param-derived** metric `Σ W·L·m` (µm²), `{derived: active_area}` with
     **no `devices:` list**: it is computed by the **recursive netlist walk**
     (`spicexplorer_core.measurements.area`), which discovers *every* transistor in the DUT deck and
     resolves each multiplier from the deck's own `.param` ties — no simulation. (A hand-authored
     device list previously undercounted: amp_020 omitted the voutn twins XM9/XM10, and amp_008 saw
     7 of 24 devices — ~10× low once the ×4…×32 multipliers are counted.)

   Both are scored, normalized (by their spec `range`), and aggregated into the single objective
   **exactly like gain/UGF/PM** — nothing bespoke.

   Verify the area accounting for either deck (per-device table + JSON, no sim):

   ```bash
   python -m spicexplorer_core.measurements.area \
     examples/analog-db/raw/amp_008_leung_nmcf/ihp-sg13g2/ac_open_loop.spice --table
   ```

## Files

| File | What |
|---|---|
| `amp_020_baseline.yaml` / `amp_020_area_power.yaml` | two-stage OTA: perf-only / + `power` + `active_area`. |
| `amp_008_baseline.yaml` / `amp_008_area_power.yaml` | three-stage NMCF: perf-only / + `power` + `active_area`. |
| `run_demo.py` | Sweeps `{baseline, area+power} × {nevergrad, ax}` for a chosen circuit; prints a comparison table. |

`run_demo.py` flags: `--circuit {amp_020,amp_008,both}` (default `amp_020`), `--budget N`,
`--batch-size N` (Ax only — candidates per generation call; `1` = exact serial parity), and
`--parallel-sim`. Flip the engine per-YAML by editing `optimizer_config.type:` (or let the script
sweep both).

## Running (needs live ngspice + the ihp-sg13g2 PDK → the api container / EDA base image)

```bash
# From the worktree, in a container that has ngspice + PDK (+ the `ax` extra for the Ax runs):
docker run --rm --user root --entrypoint bash \
  -e WORK_ROOT=/tmp/sxwork -e HOME=/tmp -e LOG_LEVEL=ERROR \
  -v "$PWD/packages":/app/packages -v "$PWD/examples":/app/examples \
  -w /app spicexplorer-api:ax \
  -c 'export PATH=/opt/ngspice/bin:$PATH && python -u examples/ax_area_power/run_demo.py --circuit amp_008 --budget 10'
```

`run_demo.py` forces blocking sims (`--parallel-sim` opts back into the threaded `submit()` path)
and writes per-trial ngspice output to `/tmp/sxsim` (keeps a bind-mounted `examples/` clean).

## Results (seed 48 — indicative: short budget, run-to-run variance)

> **Note:** the `active_area` column below predates the recursive netlist-walk fix — it was
> produced by the old hand-listed `devices:` recipe (amp_020: 8 of 10 devices; amp_008: 7 of 24).
> Under the netlist walk the area is larger and complete (amp_020 default ≈ 20.8 µm²; amp_008
> default ≈ 236 µm² with the ×4…×32 multipliers), and the specs' `target`/`range` were rescaled to
> match. Re-run in the container to refresh these numbers; the exact per-device breakdown for any
> candidate is `python -m spicexplorer_core.measurements.area <deck> --table`.

**amp_020, two-stage OTA (budget 10):**

```
run                         score       dcgain          ugf           pm        power  active_area
area+power | nevergrad    -3.0183        25.06    2.264e+07        89.21       504 µW    20.75 µm²
area+power | ax           -1.8213        23.79    1.238e+07        82.70     377.9 µW    12.43 µm²
```

**amp_008, three-stage NMCF (budget 10) — wider search space:**

```
run                              score     dcgain        ugf       pm     power  active_area
amp_008 | baseline | nevergrad  -1.2439     88.73   7.211e+06   -5.977      nan         nan
amp_008 | baseline | ax          0.7985     73.89   3.404e+06    58.12      nan         nan
amp_008 | area+power | nevergrad -2.4554    90.16   6.655e+06   -7.373    551.9       33.40
amp_008 | area+power | ax        -0.0708    79.03   1.824e+06    66.98    262.5       14.62
```

Both engines run to completion on both circuits (the Ax revival works end-to-end). With area +
power added, the score picks up their normalized penalties and the optimizer trades performance
against silicon cost. On the harder 3-stage NMCF at short budget, Ax's Bayesian search finds a
**compensated** design (pm 67°) at **262 µW / 14.6 µm²**, where Nevergrad stalls uncompensated
(pm < 0). Numbers vary run to run (short budget; a few candidates diverge in SPICE → a max-penalty
trial).

### Batched Ax (`--batch-size N`)

`--batch-size 4` asks Ax for four candidates per generation call (Center+Sobol early, then
MBM/BoTorch batches of four); the loop drains one per step so budget still counts individual trials.
`N=1` is exact serial parity. Nevergrad ignores the knob. (Evaluating a batch's candidates
concurrently would need per-candidate wrappers — a further follow-up.)
