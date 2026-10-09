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
    # Layout ↔ schematic co-optimization — one search space, one score

    **TL;DR** — the platform can size a schematic (W/L/m in a SPICE deck) and it can tune a
    *parameterized layout* (a generator's `LayoutParams`). This notebook does **both at once**:
    one `Project_Setup` whose `dut_params` carry the OTA's device widths *and* the layout's
    clearance constants, evaluated per candidate by the layout backend

    ```
    candidate = {sizing …, knobs …}
       │
       ├─ sizing  ──▶ build(params, sizing) ──▶ GDS      (devices change size)
       │              write_lvs_reference(p, sizing)     (the LVS "schematic" follows the sizing)
       │              tb_ac.spice `.param in_w=…`        (the pre-layout reference deck too)
       └─ knobs   ──▶ build(params, …)                   (the floorplan re-derives)
                         │
         DRC ──▶ LVS ──▶ kpex CC ──▶ ngspice AC on the EXTRACTED subckt
                         │
            area_um2 · drc_pass · lvs_match · c_<net>_ff · ugf · pm · dcgain
                         │
                  one score ──▶ Nevergrad ──▶ next candidate
    ```

    Why bother: a schematic-only optimizer prices `W` in *gm* and in a `.param`-derived area
    estimate. It cannot see that the wire it forced you to route past the output node costs
    0.6 fF, that the same `W` grew the row pitch by 4 µm², or that the layout knobs could have
    bought that area back for free. A layout-only optimizer has the opposite blind spot: it
    tunes clearances around a sizing nobody is allowed to question. **Co-optimization is the
    loop where both are variables and the physical toolchain is the referee.**

    **The example** — `amp_001_5t`, a 5T OTA in IHP SG13G2, drawn by the gdsfactory generator
    [`examples/layout/ihp-sg13g2/5t_ota_gf/gen_5t_ota_gf.py`](../../../examples/layout/ihp-sg13g2/5t_ota_gf/gen_5t_ota_gf.py).
    The co-optimization project lives next to it in
    [`5t_ota_gf/coopt/`](../../../examples/layout/ihp-sg13g2/5t_ota_gf/coopt/); its knobs-only
    sibling is `5t_ota_gf/opt/`.

    **What this notebook needs** — the full physical stack: a Python interpreter that owns
    gdsfactory + `ihp-gdsfactory` (`$GDS_PYTHON`), KLayout with the PDK's DRC/LVS decks, `kpex`,
    and live ngspice + `$PDK_ROOT`. The execution lane declares that as the **`live_layout`**
    requirement tag (`tests/test_notebooks.py`), so a CI job without the stack skips this
    notebook naming the missing capability. Every heavy cell below is *individually* gated: when
    the stack is absent the notebook still imports every API it teaches and replays the committed
    numbers from `coopt/coopt_replay.json`, so it reads correctly everywhere.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 0 · Capability probe — what "gated" means here

    `coopt_helpers.probe()` is the same check the notebook lane's `live_layout` gate performs,
    returning the first unmet capability as a sentence. `LIVE` drives every heavy cell below.
    """)
    return


@app.cell
def _():
    import sys
    import tempfile
    import warnings
    from pathlib import Path

    import pandas as pd
    from spicexplorer_core import project_root

    warnings.filterwarnings("ignore")
    pd.set_option("display.width", 160)

    CELL_DIR = project_root() / "examples/layout/ihp-sg13g2/5t_ota_gf"
    COOPT = CELL_DIR / "coopt"
    WORK = Path(tempfile.gettempdir()) / "coopt_nb"
    WORK.mkdir(parents=True, exist_ok=True)  # scratch: keeps the repo clean
    sys.path.insert(0, str(COOPT))  # the example's helper module (not a package)
    import coopt_helpers as H  # noqa: E402  # pyright: ignore[reportMissingImports] -- the example's helper module, importable once the line above puts coopt/ on sys.path

    PROBE = H.probe()
    LIVE = PROBE["ok"]
    REPLAY = H.load_replay()  # committed numbers, for the gated path

    print("live_layout:", "AVAILABLE" if LIVE else f"GATED — {PROBE['reason']}")
    print("replay available:", REPLAY is not None)
    H.tool_table(PROBE)
    return CELL_DIR, COOPT, H, LIVE, Path, REPLAY, WORK, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1 · The idea — sizing and layout are one problem

    Three couplings make the split-loop workflow lie, all of them visible on this 5T OTA.

    **(a) Parasitics scale with `W`.** The unity-gain frequency is
    $f_\mathrm{UGF} = g_{m1}/(2\pi C_\mathrm{out})$ with
    $C_\mathrm{out} = C_L + C_\mathrm{db} + C_\mathrm{wire}$. Widening the input pair raises
    $g_{m1}\propto\sqrt{W_1 I_D}$ — but it also grows $C_\mathrm{db}$, moves every device the
    router must reach, and lengthens the wires. Schematic-side that last term is invisible;
    extraction is the only honest source for it.

    **(b) Area is a *layout* number, not a device sum.** $\sum W L$ is not the core bbox.
    On this block the devices are ~60 % of the 206 µm² bbox; the rest is channels, rails, taps
    and well spacing — all of it `LayoutParams`. So "minimize area" is only meaningful when the
    floorplan constants are in the same vector as the widths.

    **(c) The pre→post gap moves with both.** The layout of record loses 0.70 MHz of UGF to
    extraction. That penalty is a *function* of the knobs (tighter channels ⇒ more coupling)
    **and** of the sizing (bigger devices ⇒ more junction C). Optimizing one with the other
    frozen optimizes the wrong surface.

    ### The contract the platform gives you

    | piece | what it is | where |
    |---|---|---|
    | `LayoutParams` | frozen dataclass, **one field per optimizer knob**, all with defaults | the generator module |
    | `BOUNDS` | `{knob: (lo, hi)}` — the legal range | the generator module |
    | `build(params, sizing=None)` | knobs **and** sizing in, `gdsfactory.Component` out | the generator module |
    | `write_lvs_reference(p, sizing, out)` | the LVS "schematic" for **this** candidate | the generator module |
    | `layout-flow/1` | the recipe: generator · DRC · LVS · PEX · post-layout benches | `coopt/flow.yaml` |
    | `sim_engine: layout` | selects `spicexplorer.backends.layout` in the backend factory | `coopt/project_setup.yaml` |

    The co-optimization seam is one key in the flow spec:

    ```yaml
    sizing:        sizing.json           # the FULL baseline sizing dict (um)
    sizing_params: [in_w, pld_w, tail_w] # these dut_params are SIZING, not layout knobs
    ```

    Per candidate the backend then (1) overlays them onto `sizing.json` → a per-run `sizing.json`
    → `build(params, sizing)`, (2) hands the merged dict to the LVS **writer** so the reference
    netlist follows the sizing, and (3) injects them as `.param <name>` into every post-layout
    testbench deck. A name that is also a `LayoutParams` field is rejected at load — a parameter
    is *either* sizing *or* a knob, never ambiguously both.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2 · The generator: knobs, bounds, and what the default layout looks like

    `load_generator` imports a generator module by path and exposes its contract; `params_schema`
    is the `{name, default, type, lo, hi}` table an optimizer or a UI needs. This cell is the one
    that *must* run in an interpreter that has gdsfactory — so on the notebook's own kernel we
    read the contract **without importing the module**: the backend's `introspect_generator`
    recovers `LayoutParams` defaults and `BOUNDS` via `ast`, which is exactly how the flow spec
    validates knob names on a host whose kernel has no gdsfactory.
    """)
    return


@app.cell
def _(CELL_DIR, COOPT, pd):
    from spicexplorer.backends.layout import LayoutFlowSpec, introspect_generator

    GEN = CELL_DIR / "gen_5t_ota_gf.py"
    spec = LayoutFlowSpec.from_yaml(COOPT / "flow.yaml")

    defaults, bounds = introspect_generator(GEN)
    knobs = pd.DataFrame(
        [
            {
                "knob": k,
                "default": defaults[k],
                "lo": bounds[k][0],
                "hi": bounds[k][1],
                "searched": "fixed" if k in spec.fixed_params else "yes",
            }
            for k in bounds
        ]
    )
    print(f"cell={spec.cell}  gds_python={spec.gds_python}")
    print(f"sizing_params (dut_param -> sizing key): {spec.sizing_params}")
    knobs
    return GEN, bounds, defaults, spec


@app.cell
def _(COOPT):
    import json

    BASE_SIZING = json.loads((COOPT / "sizing.json").read_text())
    print("baseline sizing (um):", BASE_SIZING)

    # `load_generator` + `params_schema` are the in-process API — they need gdsfactory, so they
    # belong in the `gds_python` interpreter. Shown here as the equivalent contract read:
    print("\nspicexplorer_layout.load_generator(GEN).bounds  ==  the BOUNDS above")
    print(
        "spicexplorer_layout.params_schema(gen)          ==  the table above, plus dataclass types"
    )
    return (BASE_SIZING,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The layout of record

    `GdsBuilder` turns the generator into the `params -> GDS` callable an optimizer trial calls,
    and `render_png` draws the result headless with the PDK's own layer colours (`klayout` python
    module, no GUI). Below is the **layout of record**: the generator's own `LayoutParams` defaults
    at the baseline sizing — three mirrored device rows (bias, input pair, mirror load) between the
    vdd and vss bars. Its area is the 205.9 µm² every number in this notebook is measured against.
    """)
    return


@app.cell
def _(COOPT, GEN, H, LIVE, WORK, defaults, spec):
    from IPython.display import Image, display
    from spicexplorer_layout import GdsBuilder, render_png

    BASE_PNG = WORK / "baseline.png"
    BASE_KNOBS = dict(defaults)  # the generator's own LayoutParams defaults

    if LIVE:
        # `GdsBuilder` is the `params -> GDS path` callable the optimizer trial uses. It runs the
        # generator in `gds_python` (a subprocess: gdsfactory caches components by name+params
        # within one interpreter, and PDK activation is process-global — the two classic ways to
        # accidentally rebuild yesterday's layout).
        builder = GdsBuilder(
            GEN,
            WORK / "baseline_gds",
            cell=spec.cell,
            sizing_json=COOPT / "sizing.json",
            python=spec.gds_python,
        )
        BASE_GDS = builder(BASE_KNOBS)
        assert builder.last is not None
        print(f"{BASE_GDS.name}: {builder.last.area_um2:.1f} um2, sha {builder.last.sha256[:12]}")
        render_png(BASE_GDS, BASE_PNG, size=(900, 900))
        display(Image(str(BASE_PNG), width=430))
    else:
        print(H.png_or_note(BASE_PNG))
    return BASE_PNG, render_png


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3 · Pre-layout baseline — the schematic's own answer

    The flow spec's `postlayout:` block names the DUT netlist and the testbenches that ride on it.
    `LayoutSimulator.run_prelayout_reference()` runs **those same decks on the schematic DUT** —
    same bench, same params, only the extracted subckt left out. That is the honest reference:
    any pre→post delta below is extraction, not a different testbench.

    Metrics come from the engine-neutral **measurement registry** (`{meas: ugf|pm|dcgain}`) — the
    same recipes the project's `target_specs` carry, so the numbers here and the numbers the
    optimizer scores are computed by one code path.
    """)
    return


@app.cell
def _(BASE_SIZING, LIVE, REPLAY, WORK, bounds, defaults, spec):
    from spicexplorer.backends.layout import LayoutSimulator
    from spicexplorer_core.measurements import measure

    AC = {"out": "v(vout)"}

    def ac_metrics(result):
        return {
            m: float(measure(result, {"meas": m, **AC}, default_analysis="ac"))
            for m in ("dcgain", "ugf", "pm")
        }

    if LIVE:
        sim0 = LayoutSimulator(spec, output_folder=WORK / "baseline", testbench_name="layout")
        sim0.update_params(
            {
                **{k: v for k, v in defaults.items() if k in bounds and k not in spec.fixed_params},
                **{k: BASE_SIZING[k] for k in spec.sizing_params},
            }
        )
        pre = ac_metrics(sim0.run_prelayout_reference(WORK / "pre")["tb_ac"])
    else:
        pre = REPLAY["pre"]

    print(
        f"pre-layout   dcgain = {pre['dcgain']:6.2f} dB   ugf = {pre['ugf'] / 1e6:7.3f} MHz   pm = {pre['pm']:5.1f} deg"
    )
    return ac_metrics, pre, sim0


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4 · One post-layout evaluation — what extraction actually costs

    `LayoutSimulator.run()` is one trial: build → DRC → LVS → kpex → the same AC bench on the
    extracted subckt. It **never raises** on a physical failure — a failed stage is recorded, the
    stages it gates are skipped, and their scalars read `NaN` (which the scorer turns into
    `MAX_PENALTY`) while the ones that did compute — `area_um2` from the build — still score.
    Only *config* errors (bad spec, unknown knob) raise, and they raise at load.
    """)
    return


@app.cell
def _(H, LIVE, REPLAY, ac_metrics, sim0):
    import time

    if LIVE:
        _t0 = time.time()
        res0 = sim0.run(label="baseline")
        post = ac_metrics(res0)
        summary0 = res0.summary
        base_row = {
            "area_um2": res0.scalar("area_um2", "layout"),
            "drc_pass": res0.scalar("drc_pass", "layout"),
            "lvs_match": res0.scalar("lvs_match", "layout"),
            "pex_ok": res0.scalar("pex_ok", "layout"),
            "secs": round(time.time() - _t0, 1),
        }
    else:
        post, summary0, base_row = REPLAY["post"], REPLAY["summary0"], REPLAY["base_row"]

    print(
        f"status={summary0['status']}  area={base_row['area_um2']:.1f} um2  "
        f"DRC={base_row['drc_pass']:.0f}  LVS={base_row['lvs_match']:.0f}  PEX={base_row['pex_ok']:.0f}  "
        f"({base_row['secs']} s)"
    )
    H.stage_times(summary0)
    return base_row, post, summary0, time


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Where the parasitic went

    `c_<net>_ff` is the capacitance from a net to **{ground ∪ the flow's `ac_gnd_nets`}** — what a
    bench that AC-grounds `vdd`/`ibias` actually sees. `ctot_<net>_ff` is the Σ-to-anything sum;
    the gap between the two columns is that net's coupling into other *signal* nets.
    """)
    return


@app.cell
def _(H, summary0):
    H.pex_net_table(summary0)
    return


@app.cell
def _(base_row, pd, post, pre):
    d_ugf = (post["ugf"] - pre["ugf"]) / 1e6  # noqa: F841 -- the UGF shift in MHz, kept for the reader; the table below shows it as delta
    delta = (
        pd.DataFrame(
            [
                {
                    "metric": "UGF [MHz]",
                    "pre-layout": pre["ugf"] / 1e6,
                    "post-layout": post["ugf"] / 1e6,
                },
                {"metric": "PM [deg]", "pre-layout": pre["pm"], "post-layout": post["pm"]},
                {
                    "metric": "DC gain [dB]",
                    "pre-layout": pre["dcgain"],
                    "post-layout": post["dcgain"],
                },
            ]
        )
        .assign(delta=lambda d: d["post-layout"] - d["pre-layout"])
        .round(3)
    )
    print(f"core area: {base_row['area_um2']:.1f} um2\n")
    delta
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Read that table together with the delta above, net by net:

    * **`vout` is the net that matters.** It carries ~0.58 fF to AC ground and ~0.98 fF in total
      — against the bench's explicit `CL = 50 fF`, a ~1-2 % load increase. Since
      $f_\mathrm{UGF} \propto 1/C_\mathrm{out}$, that alone accounts for the UGF drop; the rest
      comes from C on the internal `outm` mirror node, which the pre-layout deck also does not have.
    * **DC gain does not move** (+0.01 dB). It is a ratio of conductances at DC, so a femtofarad
      of wiring is irrelevant — a useful sanity check that the extraction did not disturb topology
      or bias.
    * **PM *improves* slightly** (+0.45°). The added C is on the dominant (output) pole while the
      mirror pole is untouched, so the loop crosses unity gain *earlier*, where less of the
      non-dominant phase lag has accumulated. A pre→post PM improvement is normal for a
      single-stage OTA and is not a sign that something went wrong.
    * **`VSUBS` dominates the raw totals** (~15 fF) and is a red herring here: the substrate node
      is left floating in this flow (no `ground_nets:`, the layout backend's default), so those
      caps sit in series with each other rather than loading a signal net.

    **This is the number a schematic-only loop cannot produce, and the whole reason the optimizer
    below is allowed to see the layout.**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5 · The co-optimization project

    `coopt/project_setup.yaml` is an ordinary project YAML — the only layout-specific things are
    `sim_engine: layout` and a testbench whose `netlist:` is the flow spec instead of a SPICE deck.
    Everything else (Nevergrad, scoring, checkpoints, the UI's replay) is the usual DSL.

    **Search space (9 dims).** Three sizing params and six layout knobs, in one vector:

    | | param | meaning | why it is coupled |
    |---|---|---|---|
    | sizing | `in_w` | M1/M2 width | ↑ `gm` ⇒ ↑ UGF, but ↓ `ro` ⇒ ↓ gain, and ↑ area |
    | sizing | `pld_w` | M3/M4 width | ↑ `ro` of the load ⇒ ↑ gain, but ↑ C at `vout` and ↑ area |
    | sizing | `tail_w` | M5 width | mirror ratio `tail_w/ref_w` scales the tail current |
    | knob | `gap_x`, `ch_y`, `edge_x`, `ib_off`, `vdd_off`, `vss_off` | the floorplan clearances | pure area at (nearly) constant electricals — the currency the sizing spends |

    **Score.** One objective, `area_um2` minimized, plus three post-layout constraints
    (`ugf ≥ 32 MHz`, `dcgain ≥ 30 dB`, `pm ≥ 55°`) and four physical gates
    (`drc_pass`/`lvs_match`/`pex_ok`/`postlayout_ok` `== 1`). This is deliberately a *tense*
    problem: the baseline (206 µm², 29.4 MHz, 29.8 dB) **violates both** UGF and gain, and the
    only way to fix them is sizing that costs area — which the knobs then have to buy back.

    `seed_from_init: true` makes trial 0 exactly the `init` point, so the run starts from a
    known-feasible design instead of a random one.
    """)
    return


@app.cell
def _(COOPT, pd, spec):
    from spicexplorer.core.domains import Project_Setup

    ps = Project_Setup.from_yaml(str(COOPT / "project_setup.yaml"))
    sizing_names = tuple(spec.sizing_params)
    space = pd.DataFrame(
        [
            {
                "param": p.name,
                "kind": "sizing" if p.name in sizing_names else "layout knob",
                "min": p.min_val,
                "init": p.init,
                "max": p.max_val,
            }
            for p in ps.dut_params
        ]
    )
    print(
        f"{ps.name}: sim_engine={ps.sim_engine}  optimizer={ps.optimizer_config.name}  "
        f"budget={ps.optimizer_config.budget}  seed_from_init={ps.optimizer_config.seed_from_init}"
    )
    space
    return ps, sizing_names


@app.cell
def _(pd, ps):
    targets = pd.DataFrame(
        [
            {
                "spec": t.name,
                "goal": str(t.goal.value if hasattr(t.goal, "value") else t.goal),
                "target": t.target,
                "sim_type": t.get_analysis(),
                "weight": t.weight,
                "recipe": (t.measurement or {}).get("meas", "— flow scalar —")
                if isinstance(t.measurement, dict)
                else "— flow scalar —",
            }
            for t in ps.optimizer_config.target_specs.targets
        ]
    )
    targets
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Running it

    `Circuit_Optimizer_Orchestrator_with_SPICE` is the same entry point every project uses; the
    backend factory resolves `sim_engine: layout` to `LayoutSimulator`. The shell equivalent is
    `uv run spicexplorer-optimize project_setup.yaml --budget 12` from the `coopt/` directory.

    **Crash safety.** `autosave_checkpoint_freqeucny` writes an atomic JSON checkpoint every *n*
    trials (temp-in-same-dir → `fsync` → `os.replace`), so a killed process never leaves a torn
    file and never loses more than *n* trials. Each layout trial here costs ~40 s of real DRC /
    LVS / kpex / ngspice, which is exactly the regime where you want that. The optimizer *empties*
    its in-memory log after each autosave, so the complete trace is reassembled from the
    checkpoint files — which is also what a resume would read.

    **Parallelism, honestly.** Nevergrad's `num_workers` is an *ask-batching* hint, not process
    fan-out: the platform's trial loop is sequential today, and the concurrency that does exist is
    *within* a trial (testbenches × PVT corners, plus the flow spec's own `max_workers` for
    `submit()`). With a guide-sized budget we leave it at 1 so every ask sees the previous tell —
    raising it would only make a short run explore blind. Trial-level fan-out for slow physical
    backends is the obvious next step for this backend.
    """)
    return


@app.cell
def _(COOPT, H, LIVE, REPLAY, WORK, time):
    from spicexplorer.optimization.orchestrator import (
        Circuit_Optimizer_Orchestrator_with_SPICE as Orchestrator,
    )

    CKPT = WORK / "checkpoints"

    if LIVE:
        _t0 = time.time()
        orch = Orchestrator(
            project_setup_path=str(COOPT / "project_setup.yaml"), auto_load=False, verbose=False
        )
        orch.project_setup.outdir = WORK / "run_out"  # keep the repo clean
        orch.initialize()
        opt = orch.get_optimizer()
        opt.autosave_checkpoint_dir = CKPT
        opt.autosave_checkpoint_freqeucny = 4  # crash-safe every 4 trials
        opt.parameterize()
        opt.optimize(render_optimization_trace=False, keep_history=False)
        RUN_SECS = round(time.time() - _t0, 1)
        trials = H.trials_table(opt, checkpoint_dir=CKPT)
        print(
            f"{len(trials)} trials in {RUN_SECS / 60:.1f} min "
            f"({RUN_SECS / max(len(trials), 1):.0f} s/trial); "
            f"{len(list(CKPT.glob('*.json')))} checkpoints on disk"
        )
    else:
        trials, RUN_SECS = REPLAY["trials"], REPLAY["run_secs"]
        print(f"(replay) {len(trials)} trials, {RUN_SECS / 60:.1f} min on the reference host")
    return RUN_SECS, trials


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6 · What the optimizer traded

    One row per trial: the parameters (sizing first, then knobs), every target's achieved value,
    and the score. `run_dir` points at that trial's own artifacts — GDS, DRC/LVS reports, the kpex
    netlist, its `sizing.json`, and `summary.json`.

    > **Reading trial params — the one trap.** A log entry's `point.params` are **already in
    > physical units**: the optimizer denormalizes a candidate *before* evaluating it and logs what
    > it evaluated. Do **not** run them through `denormalize_params` again — nothing errors, every
    > value just silently lands outside its own `[min_val, max_val]` and the table becomes fiction.
    > `trials_table` takes them as-is and, where the trial's layout run dir is reachable, prefers
    > that run's `summary.json` (`params` + the per-run `sizing`), which is the flow's own record of
    > what it built — grid snapping included, and therefore the thing you would replay.
    """)
    return


@app.cell
def _(H, ps, sizing_names, trials):
    CONSTRAINTS = {"ugf": 32e6, "dcgain": 30.0, "pm": 55.0}
    GATES = ("drc_pass", "lvs_match", "pex_ok", "postlayout_ok")

    view = trials.copy()
    view["ugf_MHz"] = view["ugf"] / 1e6
    view["feasible"] = H.feasible_mask(view, CONSTRAINTS, gates=GATES)
    cols = (
        ["trial"]
        + list(sizing_names)
        + [p.name for p in ps.dut_params if p.name not in sizing_names]
        + ["area_um2", "ugf_MHz", "pm", "dcgain", "score", "feasible"]
    )
    view[cols].round(3)
    return CONSTRAINTS, view


@app.cell
def _(CONSTRAINTS, base_row, post, view):
    import matplotlib.pyplot as plt

    feas = view[view["feasible"]]
    best_i = feas["area_um2"].idxmin() if len(feas) else view["score"].idxmax()
    best = view.loc[best_i]

    _fig, _ax = plt.subplots(figsize=(7.2, 4.6))
    _ax.axvspan(
        CONSTRAINTS["ugf"] / 1e6,
        view["ugf_MHz"].max() * 1.02,
        color="#2e7d32",
        alpha=0.06,
        zorder=0,
    )
    _ax.axvline(
        CONSTRAINTS["ugf"] / 1e6,
        color="#2e7d32",
        lw=1.2,
        ls="--",
        zorder=1,
        label=f"UGF spec ({CONSTRAINTS['ugf'] / 1e6:.0f} MHz)",
    )
    for flag, colour, marker, lbl in (
        (False, "#b0563a", "x", "violates a spec"),
        (True, "#2c5f8a", "o", "feasible"),
    ):
        s = view[view["feasible"] == flag]
        _ax.scatter(
            s["ugf_MHz"],
            s["area_um2"],
            c=colour,
            marker=marker,
            s=54,
            alpha=0.85,
            linewidths=1.4,
            label=lbl,
            zorder=3,
        )
    _ax.scatter(
        best["ugf_MHz"],
        best["area_um2"],
        s=230,
        facecolors="none",
        edgecolors="#c9a227",
        linewidths=2.2,
        zorder=4,
        label="best (min area, feasible)",
    )
    _ax.scatter(
        post["ugf"] / 1e6,
        base_row["area_um2"],
        marker="*",
        s=280,
        c="#555",
        zorder=4,
        label="baseline (layout of record)",
    )
    for _, r in view.iterrows():
        _ax.annotate(
            int(r["trial"]),  # pyright: ignore[reportArgumentType] -- matplotlib draws the label with str(); the trial number prints as it did
            (r["ugf_MHz"], r["area_um2"]),
            fontsize=7.5,
            xytext=(4, 4),
            textcoords="offset points",
            color="#666",
        )
    _ax.set_xlabel("post-layout UGF  [MHz]")
    _ax.set_ylabel("core area  [µm²]")
    _ax.set_title("Co-optimization trials — area vs post-layout UGF", fontsize=11)
    _ax.grid(alpha=0.25, lw=0.6)
    _ax.set_axisbelow(True)
    for sp in ("top", "right"):
        _ax.spines[sp].set_visible(False)
    _ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    _fig.tight_layout()
    plt.show()

    gated = view[view["ugf_MHz"].isna()]
    print(
        f"best = trial {int(best['trial'])}:  area {best['area_um2']:.1f} um2   "
        f"ugf {best['ugf_MHz']:.2f} MHz   pm {best['pm']:.1f} deg   dcgain {best['dcgain']:.2f} dB"
    )
    print(
        f"{len(feas)}/{len(view)} trials feasible; {len(gated)} never reached the AC bench "
        f"(a DRC/LVS/PEX gate fired -> NaN -> MAX_PENALTY) and so have no point on the plot: "
        f"trials {sorted(int(t) for t in gated['trial'])}"
    )
    return best, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Baseline vs best — the geometry
    """)
    return


@app.cell
def _(BASE_PNG, H, LIVE, Path, WORK, base_row, best, plt, post, render_png):
    BEST_PNG = WORK / "best.png"
    best_gds = Path(str(best["run_dir"])) / "ota_5t_gf.gds" if best.get("run_dir") else None

    if LIVE and best_gds and best_gds.is_file():
        render_png(best_gds, BEST_PNG, size=(900, 900))
    if BASE_PNG.is_file() and BEST_PNG.is_file():
        import matplotlib.image as mpimg

        _fig, axes = plt.subplots(1, 2, figsize=(9.6, 5.0))
        for _ax, png, title in (
            (
                axes[0],
                BASE_PNG,
                f"baseline — {base_row['area_um2']:.1f} µm², {post['ugf'] / 1e6:.2f} MHz",
            ),
            (
                axes[1],
                BEST_PNG,
                f"co-optimized — {best['area_um2']:.1f} µm², {best['ugf_MHz']:.2f} MHz",
            ),
        ):
            _ax.imshow(mpimg.imread(png))
            _ax.set_title(title, fontsize=10)
            _ax.axis("off")
        _fig.tight_layout()
        plt.show()
    else:
        print(H.png_or_note(BEST_PNG))
    return


@app.cell
def _(BASE_SIZING, H, best, bounds, defaults, sizing_names, spec):
    BASELINE_POINT = {
        **{k: BASE_SIZING[k] for k in sizing_names},
        **{k: defaults[k] for k in bounds if k not in spec.fixed_params},
    }
    H.knob_delta(BASELINE_POINT, {k: float(best[k]) for k in BASELINE_POINT}, BASELINE_POINT.keys())
    return


@app.cell
def _(CONSTRAINTS, base_row, best, pd, post):
    scoreboard = (
        pd.DataFrame(
            [
                {
                    "": "baseline (layout of record)",
                    "area [µm²]": base_row["area_um2"],
                    "UGF [MHz]": post["ugf"] / 1e6,
                    "PM [deg]": post["pm"],
                    "DC gain [dB]": post["dcgain"],
                },
                {
                    "": "co-optimized best",
                    "area [µm²]": best["area_um2"],
                    "UGF [MHz]": best["ugf_MHz"],
                    "PM [deg]": best["pm"],
                    "DC gain [dB]": best["dcgain"],
                },
                {
                    "": "spec",
                    "area [µm²]": float("nan"),
                    "UGF [MHz]": CONSTRAINTS["ugf"] / 1e6,
                    "PM [deg]": CONSTRAINTS["pm"],
                    "DC gain [dB]": CONSTRAINTS["dcgain"],
                },
            ]
        )
        .set_index("")
        .round(2)
    )
    scoreboard
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### What the optimizer actually traded

    Three numbers tell the whole story:

    | | area | UGF | PM | DC gain | meets spec? |
    |---|---|---|---|---|---|
    | **baseline** — layout of record, default sizing | **205.9 µm²** | 29.45 MHz | 61.9° | 29.78 dB | ✗ UGF, ✗ gain |
    | **sizing alone** — trial 8, the seed: specs met by widening devices on the *record's* floorplan | **217.0 µm²** | 32.52 MHz | 61.4° | 30.51 dB | ✓ |
    | **co-optimized** — trial 14, sizing **and** knobs moved together | **208.3 µm²** | 32.61 MHz | 61.4° | 30.23 dB | ✓ |

    The baseline is the block as drawn, and it misses **both** performance specs. Buying them with
    sizing is easy and expensive: the seed point widens M1/M2 and M3/M4, meets everything, and pays
    **+11.0 µm² (+5.4 %)** for it — every one of those µm² spent on bigger devices *and* on the
    extra pitch, rails and well spacing that surround them.

    The co-optimized point buys the same specs for **+2.3 µm² (+1.1 %)**. It gives back
    **8.7 µm² — 79 % of what the sizing cost** — and it does it in the half of the design space a
    schematic-only loop cannot reach:

    * **Devices grew, but less than the seed's.** `in_w` 0.50 → 0.61 µm and `pld_w` 1.50 → 1.88 µm
      (the seed used 0.62 / 2.00). `in_w` is the UGF lever ($g_{m1}\propto\sqrt{W_1 I_D}$) and
      `pld_w` is the gain lever (a wider load at the same current runs at lower $V^*$, so higher
      $r_o$) — and because widening `in_w` *costs* gain, the two have to move together. `tail_w`
      barely moved (2.00 → 2.05), so the tail current is essentially unchanged: the optimizer bought
      its UGF from geometry, not from burning more current.
    * **The floorplan paid for it.** `edge_x` 1.57 → 1.45, `ib_off` 1.10 → 0.97, `vss_off`
      1.44 → 1.31, `vdd_off` 1.35 → 1.30 — the clearance constants collapsed inward around the now
      larger devices. `ch_y` barely moved (0.92 µm, already all but sitting on its 0.90 µm floor); `gap_x` was
      the one knob that *grew* (1.46 → 1.55), which is the search declining to trade the input
      pair's centre channel for area.
    * **Nothing was smuggled past the toolchain.** All 16 candidates are DRC-clean and LVS-match
      against a reference regenerated from their own sizing, and every metric above is measured on
      the kpex-extracted netlist. The 10 infeasible trials are infeasible on *performance*, not on
      physics.

    The honest caveat: 16 trials in a 9-dimensional space is a demonstration, not a campaign, and
    the run leans on `seed_from_init` for a feasible starting point. Trial 1 and trial 15 both found
    ~202.6 µm² — genuinely smaller than anything above — and were rejected only because they land
    1.7 and 2.1 MHz short on UGF. That is where a longer run would go looking, and it is also the reminder
    that these constraints are **soft**: they are weighted terms in one score, so a slightly
    infeasible point can still out-score a feasible one. Make one hard by raising its `weight` or
    shrinking its `range` until the penalty dominates.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7 · Reusing this on another cell

    Nothing above is 5T-OTA-specific except the files in `coopt/`. To co-optimize a different
    block you provide five things:

    1. **A generator** — a module with `LayoutParams` (a frozen dataclass, one field per knob,
       every field with a default), `BOUNDS`, and `build(params, sizing=None) -> Component`.
       Sizes come from `sizing`, *never* from `LayoutParams`; that split is what lets the two
       halves of the search space stay unambiguous.
    2. **An LVS writer** — `write_lvs_reference(params, sizing, out)` in the same module,
       emitting the flat reference netlist for **this** sizing (fingers folded into total `W`).
       A fixed `lvs: {reference: …}` file is only correct when the sizing is frozen; the moment
       `sizing_params` is non-empty a fixed reference makes every LVS verdict a lie.
    3. **A flow spec** (`flow.yaml`, `schema: layout-flow/1`) — generator, cell, `gds_python`,
       `sizing` + `sizing_params`, `drc`/`lvs`/`pex`, and either a `postlayout:` block (the
       platform's own ngspice testbenches on the extracted subckt, as here) **or** a `measure:`
       hook (a `measure(request) -> {name: value}` callable, for a block whose benches live in
       its own harness — the H12 LPF lane works this way).
    4. **A post-layout testbench deck + its parameterized DUT** — the DUT's `.subckt` header and
       pin **order** must match what the extractor produces, and its `W`/`L` cards read the
       global `.param`s the deck declares (`w={in_w*1e-6}` — the sizing dict is in µm, and `u`
       after a brace expression is *not* a multiplier in ngspice).
    5. **A project YAML** — `sim_engine: layout`, one testbench whose `netlist:` is the flow spec,
       `dut_params` = sizing + knobs, `target_specs` = your objective plus the physical gates
       (`drc_pass`/`lvs_match`/`pex_ok`/`postlayout_ok`).

    Two things worth budgeting for before you start a campaign:

    * **Cost per trial.** Here it is ~40 s, and DRC is over half of it. Turn `retain: summary`
      (or `none`) on for long runs so the trial dirs do not fill the disk, and size your budget
      in *wall time*, not trials.
    * **Reachability of the specs.** Probe three or four hand-picked points first (as this
      notebook's §4 does) and confirm a feasible point exists inside the bounds. An optimizer
      handed an infeasible box spends its whole budget proving it.

    ### See also

    * `packages/spicexplorer/notebooks/optimizer_quickstart.py` — the YAML DSL and the
      simulator seam this backend plugs into
    * `examples/layout/ihp-sg13g2/5t_ota_gf/opt/` — the knobs-only layout project (sizing frozen)
    * `packages/spicexplorer-signoff/` — the DRC / LVS / PEX runners and `postlayout` splice
    * `packages/spicexplorer-layout/` — the generator contract, `GdsBuilder`, `render_png`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    #### Refreshing the committed replay

    The cell below re-freezes `coopt/coopt_replay.json` (the numbers the gated path shows) from a
    live run. It is a no-op unless the stack is present *and* `COOPT_WRITE_REPLAY=1`, so the test
    lane and a casual re-execution never rewrite committed data.
    """)
    return


@app.cell
def _(H, LIVE, RUN_SECS, base_row, post, pre, summary0, trials):
    import os

    if LIVE and os.environ.get("COOPT_WRITE_REPLAY") == "1":
        p = H.save_replay(
            {
                "pre": pre,
                "post": post,
                "summary0": summary0,
                "base_row": base_row,
                "run_secs": RUN_SECS,
                "trials": trials.to_dict(orient="records"),
            }
        )
        print("wrote", p)
    else:
        print("replay not rewritten (set COOPT_WRITE_REPLAY=1 on a live host to refresh it)")
    return


if __name__ == "__main__":
    app.run()
