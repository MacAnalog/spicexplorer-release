# Native Spectre + OCEAN metrics — example (template)

A minimal project showing how to drive the **Spectre backend natively** and score a design
with **canonical OCEAN measurements**, wired straight into the optimizer loop
(`doc/plan_virtuoso_bridge.md`, the `Project_Setup`/YAML wiring). It is a **template**: it
requires the research server (Cadence Spectre + a licensed PDK + `virtuoso-bridge`) to
simulate. On a PDK-less host it loads and validates but cannot run.

## What it demonstrates

- **`sim_engine: spectre`** selects the Spectre backend. Everything else is the SAME YAML
  shape as an ngspice project.
- **`testbenches[].netlist`** — a native Spectre `.scs` **file** (here
  `spice/ota_5t_tb_ac.scs`), exactly as an ngspice testbench points at a `.spice`. Its
  `parameters` line declares the design variables (lowercase — the injected namespace); the
  optimizer rewrites that line per candidate. This is the injection path — the bridge runs a
  fixed file per run and in local mode ignores its `params` argument, so injection happens on
  our side. The PVT corner's `include "…" section=…` replaces the deck's default model include.
- **`target_specs[].measurement`** — each spec's canonical metric, evaluated **post-sim** by
  a persistent `ocean -nograph` session on the run's PSF raw dir and merged back under the
  spec's own name, so the scorer reads it through the unchanged `result.scalar(name, …)`.
  Two authoring styles:
  - raw: `measurement: {result: ac, expr: 'dB20(value(v("v_out") 1e3))'}` (the DC-gain spec's
    verbatim expr in this project's `project_setup.yaml`).
  - builder: `measurement: {builder: device_op_param, instance: xota.XM1, param: gm}`
    (a named `spicexplorer.backends.ocean_metrics` constructor; validated at load — as used by
    the `id_gm_in` spec, and `{builder: ac_gain_bw_product, signal: v_out}` by `ugbw`).
- **`pvt`** supplies the model `include`/section, supply and temperature for the composed deck.

## Running it (research server)

```bash
# point at your licensed model library (NEVER commit the path) + the bridge/ocean profile
export SPICEXPLORER_VB_ENV_FILE="$HOME/.virtuoso-bridge/local.env"   # sets VB_CADENCE_CSHRC
# edit project_setup.yaml: pvt.corners[].model_includes[].lib_file → your models.scs
```

The persistent OCEAN session holds one ADE license token for the run's lifetime and is
closed at loop teardown. See `test_spectre_ocean_wiring_live.py` for the runnable live proof
and `backends/ocean_metrics.py` for the measurement helpers / OCEAN naming truths.
