# `raw_optimize/` — optimize the generated raw decks directly

This folder shows the spicexplorer optimizer (the `project_setup.yaml` DSL) sizing a circuit by
driving the **committed `raw/` export decks** — the self-contained
`raw/<circuit>/<pdk>/<analysis>.spice` files that `analog-db export-raw` generates — with no
hand-authored testbench in between.

Each raw deck already embeds its analysis + a `meas`/`let` block that writes the metrics of
interest, and (since the `quit` fix) ends its `.control` block with `write` then `quit` — the
`quit` is what lets spicelib's ngspice runner close the interactive session and hand the RAW
back so the optimizer can read the result vectors.

## What's here

| File | Circuit | Testbenches (raw decks) | Sized | Specs |
|---|---|---|---|---|
| `amp_001_5t.yaml` | 5T OTA | `ac_open_loop`, `dc_op` | 5 W/L | dcgain, ugf, pm, i(i_supply) |
| `amp_004_folded_cascode.yaml` | folded-cascode OTA | `ac_open_loop`, `dc_op` | 7 widths | dcgain, ugf, pm, i(i_supply) |
| `ldo_007_pmos.yaml` | PMOS LDO | `dc_op`, `loop_stability`, `load_regulation`, `line_regulation` | 4 (widths + tail bias) | v(vout_dc), i(i_supply), zout_peak_db, load_reg, line_reg |
| `amp_022_ungroup_demo.yaml` | two-stage Miller | `ac_open_loop`, `dc_op` | 5 knobs, **group-addressed** | dcgain, ugf, pm, i(i_supply) |
| `ungroup_demo.py` | — | — | — | the live `ungroup:` demo engine (see below); notebook `notebooks/ungroup_resizing.ipynb` |
| `run.py` | — | — | — | a bare step loop that prints score + metrics per loop |

## How it wires up

- **`ws_root: ..`** resolves to the analog-db repo root, so each `testbench.netlist` is a
  committed `raw/.../*.spice` path and `outdir` is `raw_optimize/_runs/<id>` (gitignored, wiped
  each run — it must live outside `raw/`).
- **`dut_params[].name`** matches the deck's `.param x_dut_*` (or `w_pass`, `i_tail`, …) knobs
  verbatim; the wrapper rewrites those `.param` lines each loop.
- **`target_specs[].name`** is the exact vector the deck's control block wrote. A `meas` result
  (`dcgain`, `ugf`, `pm`, `zout_peak_db`, `load_reg`, `line_reg`) is a **bare** name; a `let`
  scalar is saved type-prefixed — `let i_supply = abs(i(Vdd))` → **`i(i_supply)`**,
  `let vout_dc = v(vout)` → **`v(vout_dc)`** — so those specs must use the `i(...)`/`v(...)` form
  (a bare `i_supply` reads NaN). **`sim_type`** selects the ngspice plot: `ac` → "AC Analysis",
  `op` → "Operating Point", `dc` → "DC transfer characteristic" (the LDO's load/line-regulation
  sweeps; usable since the spicelib DC plot-name fix).

## Run it (needs ngspice + the ihp-sg13g2 PDK)

Live SPICE runs in the api container / base image, not a bare macOS host. From the repo root:

```bash
docker compose up -d api                       # (in spicexplorer-platform)
docker compose exec -T -w /app/examples/analog-db/raw_optimize api \
    python run.py amp_001_5t.yaml --loops 12
docker compose exec -T -w /app/examples/analog-db/raw_optimize api \
    python run.py amp_004_folded_cascode.yaml --loops 12
docker compose exec -T -w /app/examples/analog-db/raw_optimize api \
    python run.py ldo_007_pmos.yaml --loops 12
```

`run.py` prints a per-loop table (score + each spec's measured value) and a final `RESULT: OK`
when finite metrics were extracted. For a full run with autosave checkpoints and Plotly traces,
call `optimizer.optimize(...)` instead (see `examples/OTA/.../nevergrad_single_obj_opt.py`).

## The `ungroup:` affordance — group-addressed knobs & freeing a shipped tie

The three YAMLs above name raw `.param x_dut_*` symbols directly. The **parameterization layer**
(`spicexplorer/params@1`; platform pf #49) adds a second, higher-level way to project a circuit: a
projection may set **`params_file:`** (the circuit's `abstract/params.yaml`) and then

- **address knobs by GROUP** — a `dut_param` named `<group>.<field>` (e.g. `input_pair.w`,
  `nmos_load_mirror.l`) resolves to the group's FIRST-member atomic symbol under the D-3 lowering.
  Availability is atomic (every device is in the inventory), but the default search stays
  low-dimensional and speaks the circuit's own vocabulary; and
- **dissolve a shipped tie** with **`ungroup: ["<group>" | "kind:<kind>" | "ratio:<ref>"]`**. A
  shipped tie is just a `.param xB = {xA}` line in the lowered deck; `ungroup:` **shadows** it —
  appends a FROZEN `.param xB = <xA's current deck default>` — so the untied deck is *numerically
  identical* until the freed symbol is actually swept (untying = shadowing). Promote that symbol to
  its own free `dut_param` and the search space gains exactly that dimension. **No optimizer-core
  change**: the frozen shadows ride the optimizer's existing verbatim `.param` rewrite, and both
  engine lanes get it through the `Simulator` protocol.

### Worked example — amp_022, freeing `stage2_load_width`

[`amp_022_ungroup_demo.yaml`](amp_022_ungroup_demo.yaml) is the LIVE worked case (the notebook
[`../notebooks/ungroup_resizing.ipynb`](../notebooks/ungroup_resizing.ipynb) is the guided, executed
counterpart; [`ungroup_demo.py`](ungroup_demo.py) is the reusable engine). It drives amp_022's
committed `ihp-sg13g2` decks with 5 group-addressed knobs, then dissolves ONE tie:
**`stage2_load_width`** (`kind: shared_geometry`) — the legacy `x_nload_w` opinion welding the
2nd-stage common-source device width `XM2.w` to the stage-1 mirror-load width `XM3.w` (one knob,
three devices: `XM3`, its mirror partner `XM4`, and `XM2`). Its own `params.yaml` description says
*"no single structural cause — dissolve freely."*

`ungroup: [stage2_load_width]` shadows `x_dut_xm2_w` at XM3.w's `6u` default; adding `x_dut_xm2_w` as
a free knob frees the 2nd-stage width from the mirror load. Two short **seeded live ngspice** runs
(`NGOpt`, budget 20, seed 48; ~24 s total on the research server) show the effect:

| metric | (a) tied — 5 knobs | (b) ungrouped — 6 knobs |
|---|---|---|
| free knobs | 5 | **6** (`+x_dut_xm2_w`) |
| best score | −0.2868 | **−0.2049** |
| dcgain [dB] | 56.2 | 52.4 |
| ugf [MHz] | 25.3 | 20.8 |
| pm [deg] | 76.7 | 78.4 |
| i_supply [µA] | 238 | **119** |

Freeing `XM2.w` lets the optimizer shrink the 2nd stage **independent** of the stage-1 load — it
still clears the gain / UGF / PM targets while roughly **halving the quiescent supply current**, the
exact trade the shipped tie forecloses. (This is a *demonstration* of the affordance — tens of
trials, not a real campaign — but the numbers are live ngspice, not asserted.)

### Connection to the sizing lane

This is the mechanism that turns the metrics analog-db **skips by default** (THD / IIP3 / PM
headroom / supply current) into **tuned** numbers. The shipped low-dim projection keeps a circuit's
opinionated geometry intact so a baseline run is fast and well-biased; `ungroup:` then opens *only*
the dimension a particular spec needs, without hand-editing the deck or losing the rest of the
circuit's tying. Freeing a shipped tie is how an upstream user searches a dimension analog-db tied
on purpose — the sizing-lane campaign (turning the baseline skips into datasheet numbers) is exactly
a curated set of these `ungroup:` moves per target spec.

## Generated variants (`generated/`)

The three top-level YAMLs are hand-tuned. `generated/` holds one config **per circuit** produced
mechanically so they stay in sync with the decks — the no-arg sweep covers every amplifier and LDO
(32 circuits); a circuit whose only scorable vector is `i(i_supply)` is skipped, since minimizing
quiescent current with no performance objective is degenerate (broadening `_SPEC_REGISTRY` to score
comparators / diff-pairs / temp-sensors is the follow-up).

```bash
analog-db export-raw-project --circuit ldo_007_pmos --pdk ihp-sg13g2   # one circuit
analog-db export-raw-project                                           # every scorable circuit → generated/
```

The generator (`src/spicexplorer_analog_db/raw_project.py`) points one testbench at each committed
raw deck, **parses** the deck's `.control` block for the vectors it writes (applying the
`meas`→bare / `let`→`i()`/`v()` naming rule), and keeps only the whitelisted, well-characterised
metrics (`_SPEC_REGISTRY`) whose goal/target is known. `dut_params` come from `sizing.yaml` — the
geometry/bias knobs are searched over a band around each committed default, while integer counts,
passives and the reference are frozen so the operating point (and any regulation target) stays
well-defined. Run them exactly like the hand-tuned ones: `python ../run.py generated/<id>.yaml`.
