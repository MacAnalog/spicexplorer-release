import marimo

__generated_with = "0.25.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Optimizer quickstart — YAML DSL → engines → analog-db raw decks

    **TL;DR** — the central workflow of this package is

    ```
    project_setup.yaml ──ws_root-portable──▶ Project_Setup.from_yaml()
            │  dut_params (search space)  ·  testbenches (netlists)  ·  target_specs (score)
            ▼
    Circuit_Optimizer_Orchestrator_with_SPICE ──▶ Nevergrad ask/tell loop
            │  every candidate: update_params → run → measure → score
            ▼
    the Simulator PROTOCOL (engine-neutral seam) ──ngspice (default) / spectre (bridge)──▶ SimResult
            ▼
    scorer (target_specs) + crash-safe checkpoints + Plotly reports
    ```

    This notebook walks that pipe end-to-end, **live where the env allows** (ngspice + the
    ihp-sg13g2 PDK), and degrades to recorded numbers elsewhere:

    1. load + inspect the **YAML DSL** (§1),
    2. the **simulator seam** — one protocol, hot-swappable engines (§2),
    3. **size a circuit live** over the *committed analog-db raw decks* — the
       optimizer ↔ analog-db integration with no hand-authored testbench (§3),
    4. declarative **measurement recipes** on target specs (Tier-1 Python / Tier-2 OCEAN) (§4),
    5. engine swap to **Spectre**, PVT corners, checkpoints/resume (§5) + a cheatsheet.

    | piece | where it lives |
    |---|---|
    | YAML DSL schema | `spicexplorer.core.domains` (`Project_Setup`, `DUT_Param`, `TargetSpec`, …) |
    | optimizer loop | `spicexplorer.optimization` (`orchestrator.py`, `base.py`, `stochastic/`) |
    | engine seam | core `spice_engine/protocol.py` + `optimization/simulator_factory.py` |
    | engines | core `NGSpice_Wrapper` (default) · `backends/spectre.py` (optional bridge) |
    | measurements | `spicexplorer_core.measurements` (Tier-1) · `backends/ocean_metrics.py` + the analog-db calculator table (Tier-2) |
    | analog-db integration | `backends/analog_db.py` (datasheet-driven `run_circuit`) · analog-db `raw_optimize/` (optimizer-driven, THIS notebook §3) |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1 · Load a project — the YAML DSL
    One `project_setup.yaml` declares everything a run needs. The example used throughout this
    notebook is **committed in analog-db** (`raw_optimize/amp_001_5t.yaml`): it sizes the 5T OTA
    by driving the repo's own generated `raw/` decks. Portability comes from `ws_root` (a
    relative value resolves against the YAML's own directory, so the committed example runs from
    any clone). Gotchas worth knowing: `optimizer_config.target_specs` returns a `ListTargetSpec`
    object — use `.targets` (or `.enabled_targets()`) for the list; an omitted `freeze` on a
    `dut_param` means *optimize it* (`freeze: true` pins it); duplicate `dut_param` names are
    rejected at load; eng-strings (`0.3u`, `50f`) parse everywhere via `parse_value`.
    """)
    return


@app.cell
def _():
    from pathlib import Path

    from spicexplorer.backends.analog_db import analog_db_root
    from spicexplorer.core.domains import Project_Setup

    # The corpus root, resolved like the library does: $SPICEXPLORER_ANALOG_DB, else
    # <project_root>/examples/analog-db (from the installed package — not the cwd).
    ADB = analog_db_root()
    YAML = ADB / "raw_optimize" / "amp_001_5t.yaml"
    ps = Project_Setup.from_yaml(str(YAML))

    print(ps.name, "—", ps.description)
    print("\nsearch space (dut_params):")
    for p in ps.dut_params:
        print(f"  {p.name:22s} [{p.min_val!s:>6} .. {p.max_val!s:<6}] freeze={p.freeze}")
    print("\ntestbenches:", [tb.name for tb in ps.testbenches if tb.enable])
    print("\ntarget_specs (name · goal · target · sim_type):")
    for t in ps.optimizer_config.target_specs.targets:  # ListTargetSpec -> .targets
        print(
            f"  {t.name:14s} {t.goal!s:>6} {t.target!s:>10}   sim={t.sim_type!s}  tb={t.testbench}"
        )
    return ADB, Path, YAML, ps


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2 · The simulator seam — one protocol, hot-swappable engines
    The loop (`optimization/base.py`) consumes only the core **`Simulator` protocol**
    (`update_params` → `run`/`submit` → a `SimResult` with `scalar(name, analysis)` /
    `wave(name, analysis)`), never a concrete wrapper. `simulator_factory.build_simulator`
    resolves the YAML's `sim_engine:` to a backend: **ngspice** (default, zero behaviour change)
    or **spectre** (optional — the virtuoso-bridge imports lazily, so ngspice-only installs pull
    in no Cadence dependency). Below: resolve a few spellings, then run ONE fixed simulation of
    the committed `ac_open_loop` raw deck and read the gain twice — once from the deck's own
    `meas` scalar, once through the engine-neutral measurement registry on the raw AC wave —
    the parity that makes an engine swap safe.
    """)
    return


@app.cell
def _(ADB, Path):
    import shutil
    import tempfile

    from spicexplorer.optimization.simulator_factory import build_simulator, resolve_engine

    print("resolved:", [resolve_engine(v).value for v in ("ngspice", None, "SPECTRE")])
    try:
        resolve_engine("eldo")
    except ValueError as exc:
        print("unknown engine fails loudly:", exc)

    deck = ADB / "raw" / "amp_001_5t" / "ihp-sg13g2" / "ac_open_loop.spice"
    if shutil.which("ngspice") and deck.is_file():
        sim = build_simulator(
            "ngspice",
            netlist_filename=deck,
            output_folder=Path(tempfile.mkdtemp()),
            testbench_name="qs_ac",
        )
        res = sim.run()
        from spicexplorer_core.measurements import measure

        deck_meas = float(res.scalar("dcgain", "ac"))  # the deck's own `meas ac dcgain`
        registry = measure(res, {"meas": "dcgain", "out": "v(vout)"}, default_analysis="ac")
        print(f"dcgain — deck meas: {deck_meas:.2f} dB · registry recipe: {registry:.2f} dB")
    else:
        print(
            "ngspice/deck not available — recorded: dcgain deck meas 29.79 dB == registry 29.79 dB"
        )
    return (shutil,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3 · Size a circuit LIVE over committed analog-db raw decks
    The **optimizer ↔ analog-db integration**: `analog-db export-raw` writes self-contained decks
    (`raw/<circuit>/<pdk>/<bench>.spice`) whose `.control` blocks already `meas`/`let` the metrics
    and end with `write` + `quit` (the `quit` is what lets spicelib hand the RAW back). The
    committed `raw_optimize/*.yaml` projects point the optimizer straight at them — the deck's
    `.param x_dut_*` knobs are the search space, its written vectors are the target specs.
    Metric ↔ vector contract: a `meas` result is a **bare** name (`dcgain`, `ugf`, `pm`); a `let`
    scalar keeps its type prefix (`let i_supply = abs(i(Vdd))` → spec name **`i(i_supply)`**).
    Each `optimization_step()` = ask a candidate → rewrite the deck params → run every enabled
    bench → score against the spec bands:
    """)
    return


@app.cell
def _(YAML, ps, shutil):
    import math

    from spicexplorer.optimization.orchestrator import (
        Circuit_Optimizer_Orchestrator_with_SPICE as Orchestrator,
    )
    from spicexplorer.optimization.orchestrator import (
        Optimizer_Type_Enum,
    )

    if shutil.which("ngspice") and YAML.is_file():
        orch = Orchestrator(
            project_setup_path=str(YAML),
            optimizer_type=Optimizer_Type_Enum.NEVERGRAD_SINGLE,
            auto_load=False,
            verbose=False,
        )
        orch.initialize()
        opt = orch.get_optimizer()
        opt.parameterize()
        opt._create_optimizer_obj()
        specs = [t.name for t in ps.optimizer_config.target_specs.enabled_targets()]
        print("loop | score      | " + " | ".join(f"{s:>12}" for s in specs))
        best = (-math.inf, {})
        for i in range(1, 9):  # a taste — the committed budget is optimizer_config.budget
            _p, score, meta = opt.optimization_step()
            row = [f"{float(meta.get(s, {}).get('curr_val', float('nan'))):12.4g}" for s in specs]
            print(f"{i:4d} | {float(score):10.4g} | " + " | ".join(row))
            if float(score) > best[0]:
                best = (float(score), meta)
        print("best score:", f"{best[0]:.4g}")
    else:
        print(
            "ngspice not available — recorded 8-loop run (2026-07-10): score -0.26 -> -0.07;"
            " dcgain 23 -> 31 dB, ugf 55-84 MHz, pm 55-73 deg, i(i_supply) 34-41 uA"
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    For a *full* run — autosave **crash-safe checkpoints** (atomic JSON writes), resume, and the
    Plotly trace/report — call `optimizer.optimize(...)` instead of stepping by hand (see
    `examples/OTA/cascode/ihp-sg13g2/sizing/nevergrad_single_obj_opt.py`), or drive it over REST
    (`POST /api/optimize/start` + the SSE stream — run-config overrides like budget/seed/corner
    are applied in-memory, the YAML is never rewritten). analog-db's `raw_optimize/run.py` is the
    same bare loop as §3 with argparse.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4 · Declarative measurement recipes on target specs
    A `target_specs[].name` can read a vector the deck wrote (§3's contract) — but a spec can
    also carry a **`measurement:` recipe**, validated at load (a typo fails before any
    simulation) and merged back under the spec's name so the scorer seam is unchanged:

    * **Tier-1 (engine-neutral Python)** — `{meas: <name>, …}` computed from the result's own
      waves by `spicexplorer_core.measurements` for BOTH engines: `dcgain`/`ugf`/`pm`, `bw_3db`,
      `cmrr_db`/`psrr_vdd_db`, `icmr_*`, `t_settle`/`slew`, `thd*`/`iip3*` (tran-FFT and
      native-PSS twins), `pm_loop`/`gain_margin_db` (stb), `inoise_total`/`onoise_total`,
      `i_supply`.
    * **Tier-2 (OCEAN, Spectre only)** — `{result, expr}` (a raw SKILL line) or `{builder, …}`
      (a named `ocean_metrics` constructor), evaluated post-sim on the persisted raw dir by ONE
      warm `ocean -nograph` session (~10-30 ms/candidate, batched). The expression vocabulary is
      data too: analog-db's `_shared/engines/spectre/calculator.yaml` +
      `bench_ocean_measurements(circuit, tb)` render a bench's SKILL calculator set — see
      `analog_db_bench_validation.py` §4c for the live Python-vs-SKILL parity table.
    """)
    return


@app.cell
def _():
    from spicexplorer_core.measurements import validate_recipe

    validate_recipe("pm_spec", {"meas": "pm", "out": "v(vout)"})  # OK — silent
    for bad in ({"meas": "phase_margarine", "out": "v"}, {"meas": "iip3_dbv", "out": "v"}):
        try:
            validate_recipe("bad_spec", bad)
        except ValueError as exc:
            print("caught at load:", str(exc)[:110], "…")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5 · Parameter ties — group knobs and `ungroup:` overrides

    analog-db ships every circuit an `abstract/params.yaml` (`spicexplorer/params@1`): the **atomic**
    per-instance parameter inventory plus the shipped *default* ties, tagged with machine-readable
    reasons (`matched_pair`, `mirror_length`, …). Ties lower into the committed decks as plain
    `.param xB = {xA}` lines — so the optimizer needs **zero** new machinery, and a projection can:

    - name a knob **by group** — `input_pair.w` resolves to the first member's atomic symbol;
    - **dissolve** shipped ties by name or by category with `ungroup:` — dissolved members are
      frozen at their current defaults (numerically identical until you sweep them).

    In a `raw_optimize/*.yaml` projection this looks like:

    ```yaml
    project:
      params_file: circuits/amp_001_5t/abstract/params.yaml   # relative → ws_root
      ungroup: ["kind:mirror_length"]                          # name | kind:<kind> | ratio:<ref>
      dut_params:
        - {name: input_pair.w, min_val: 0.3u, max_val: 4u}     # → x_dut_xm1_w
    ```

    `Project_Setup.from_yaml()` resolves all of this at load (`resolve_param_projection`); below,
    the same semantics through the module API on a self-contained example:
    """)
    return


@app.cell
def _(Path):
    from tempfile import TemporaryDirectory

    from spicexplorer.backends.params import (
        load_params_file,
        netlist_param_defaults,
        resolve_knob,
        shadow_params,
    )

    # The shipped contract (analog-db `abstract/params.yaml`, spicexplorer/params@1) —
    # atomic inventory + default ties tagged with WHY:
    PARAMS_YAML = """\
    schema: spicexplorer/params@1
    devices:
      XM1: {w: x_dut_xm1_w, l: x_dut_xm1_l, m: x_dut_xm1_m}
      XM2: {w: x_dut_xm2_w, l: x_dut_xm2_l, m: x_dut_xm2_m}
      XM3: {w: x_dut_xm3_w, l: x_dut_xm3_l, m: x_dut_xm3_m}
      XM4: {w: x_dut_xm4_w, l: x_dut_xm4_l, m: x_dut_xm4_m}
    groups:
    - {name: input_pair, kind: matched_pair, members: [XM1, XM2], tie: [w, l, m]}
    - {name: load_mirror_l, kind: mirror_length, members: [XM3, XM4], tie: [l]}
    """

    # …and the deck it lowers to: free-symbol defaults + a GENERATED tie block
    # (each tied symbol defined exactly ONCE → redefining it unties just that symbol):
    DECK = """\
    .param x_dut_xm1_w=2.0u
    .param x_dut_xm1_l=0.5u
    .param x_dut_xm1_m=1
    .param x_dut_xm3_w=4.0u
    .param x_dut_xm3_l=1.0u
    .param x_dut_xm3_m=1
    .param x_dut_xm4_w=4.0u
    .param x_dut_xm4_m=2
    * ---- GENERATED parameter ties (abstract/params.yaml groups/ratios) ----
    .param x_dut_xm2_w = {x_dut_xm1_w}
    .param x_dut_xm2_l = {x_dut_xm1_l}
    .param x_dut_xm2_m = {x_dut_xm1_m}
    .param x_dut_xm4_l = {x_dut_xm3_l}
    """

    with TemporaryDirectory() as td:
        params_path, deck_path = Path(td, "params.yaml"), Path(td, "_dut.spice")
        params_path.write_text(PARAMS_YAML)
        deck_path.write_text(DECK)
        cp = load_params_file(params_path)

        # A dut_param may name a GROUP knob — it resolves to the first member's atomic
        # symbol (the free knob under the D-3 lowering); free bias knobs pass through:
        print("input_pair.w   ->", resolve_knob(cp, "input_pair.w"))
        print("load_mirror_l  ->", resolve_knob(cp, "load_mirror_l"))  # 1-field tie: bare name OK
        print("i_tail         ->", resolve_knob(cp, "i_tail"))

        # `ungroup:` dissolves shipped ties by name or CATEGORY. The shadow set freezes
        # every dissolved member at its current default (read from the deck header), so
        # the untied deck is numerically identical until you actually sweep one:
        shadows = shadow_params(cp, ["kind:mirror_length"], netlist_param_defaults(deck_path))
        print("ungroup kind:mirror_length ->", shadows)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6 · Engine swap, PVT corners, resume — the knobs you'll reach for next
    * **`sim_engine: spectre`** (project block) routes the SAME loop through the native Spectre
      backend: the testbench `netlist:` is a hand-written `.scs` run in native-file injection
      mode (design vars rewrite the deck's `parameters` line per candidate — the bridge runs a
      fixed file and won't template), `work_dir=` persists each candidate's PSF raw dir (the
      OCEAN input), `deck_dir=` keeps the per-candidate decks as the audit trail. Without a
      bridge env it degrades loudly at build time, not mid-run.
    * **Datasheet-driven runs** (no optimizer): `backends.analog_db.run_circuit` routes a
      library circuit to its native engine off the committed `sim_engine` marker and scores its
      datasheet — `analog_db_in_library.py`, `analog_db_bench_validation.py`.
    * **PVT**: a top-level `pvt:` block makes corners first-class; `pvt.mode: multi` runs every
      enabled corner per trial and aggregates (`mean`/`sum`/`min`) — the guide is
      [`examples/notebooks/multi_corner_pvt_optimization.py`](../../../examples/notebooks/multi_corner_pvt_optimization.py).
    * **Resume**: checkpoints are atomic JSON; `Base_Optimizer.load_checkpoint` round-trips a
      real run, and the REST layer replays cached checkpoints without a PDK.

    ## Cheatsheet
    ```python
    ps  = Project_Setup.from_yaml('project_setup.yaml')      # the DSL, ws_root-portable
    orch = Orchestrator(project_setup_path=..., optimizer_type=Optimizer_Type_Enum.NEVERGRAD_SINGLE,
                        auto_load=False); orch.initialize()
    opt = orch.get_optimizer(); opt.parameterize(); opt._create_optimizer_obj()
    params, score, meta = opt.optimization_step()            # one ask→sim→score loop
    opt.optimize(...)                                        # full run: checkpoints + reports

    sim = build_simulator('ngspice', netlist_filename=deck, output_folder=out)  # the seam
    res = sim.run(); res.scalar('dcgain', 'ac'); res.wave('v(vout)', 'ac')
    ```
    Recorded live run of this notebook: research server, ngspice + ihp-sg13g2, analog-db
    `raw_optimize/amp_001_5t.yaml` (2026-07-10).
    """)
    return


if __name__ == "__main__":
    app.run()
