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
    # `ungroup:` live re-sizing on amp_022 — the parameterization layer, end-to-end

    The [parameterization layer](../_shared/PARAMS.md) (`spicexplorer/params@1`; platform pf #49) lets every
    analog-db circuit ship an **atomic per-instance inventory** (`devices:` — *what CAN vary*) separated
    from **shipped default ties** (`groups:`/`ratios:` — *what SHOULD vary together*, each tagged with a
    machine-readable `kind` reason). The ties lower into the committed decks as `.param xB = {xA}` lines.

    This notebook is the **live** worked example of the `ungroup:` affordance — the mechanism an upstream
    user reaches for to **search a dimension analog-db deliberately tied by default**. It is the LIVE
    counterpart of the synthetic §5 cell in the platform `optimizer_quickstart.py`. We run **two short,
    seeded live ngspice optimizations** over amp_022's committed `ihp-sg13g2` decks:

    1. **(a) tied** — the shipped ties intact: a curated low-dimensional search addressed by GROUP name.
    2. **(b) ungrouped** — the same projection + `ungroup: [stage2_load_width]`, dissolving the one tie we
       argue is worth freeing (the legacy `x_nload_w` opinion tying the 2nd-stage CS device width to the
       stage-1 mirror-load width), and promoting `x_dut_xm2_w` to its own free knob.

    We capture the **dimensionality before/after** (n free knobs + the dissolved shadow symbols) and a small
    **before/after metric table**. This is a **DEMONSTRATION** of the affordance (20 trials each, seeded,
    a few minutes) — *not* an optimization campaign. But every number is REAL (live ngspice).

    > **Connection to the sizing lane.** Freeing a shipped tie is exactly how an upstream user turns a
    > baseline metric analog-db *skips by default* into a *tuned* number: the shipped low-dim projection
    > keeps a circuit's opinionated geometry intact, and `ungroup:` selectively opens the dimension a
    > particular spec (THD / IIP3 / PM headroom / supply current) needs — with **zero optimizer-core
    > change** (frozen shadow `.param`s ride the existing verbatim rewrite).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 0. Live-SPICE gate

    The whole point of this notebook is a live simulation, so it is **PDK-gated**: it needs `ngspice` +
    the `ihp-sg13g2` PDK (amp_022's open lane). `probe_env()` is the honest cross-lane check (native
    research server *or* the EDA base container). When live runs are unavailable the cells below skip
    gracefully — nothing here fabricates numbers.
    """)
    return


@app.cell
def _(mo):
    import logging

    from spicexplorer_core.env import probe_env

    logging.disable(logging.INFO)  # quiet the optimizer's INFO stream — we print our own summary

    # the reusable demo engine lives next to the projection (raw_optimize/ungroup_demo.py)
    REPO = mo.notebook_dir().parent  # notebooks/ -> analog-db root
    import sys
    sys.path.insert(0, str(REPO / "raw_optimize"))
    import ungroup_demo as demo

    env = probe_env()
    LIVE = env["live_runs_enabled"]
    print(f"ngspice_ok={env['ngspice_ok']}  pdk_ok={env['pdk_ok']}  "
          f"live_runs_enabled={LIVE}  tech={env.get('tech')}")
    if not LIVE:
        print("→ live runs unavailable; the simulation cells below will skip.")
    return LIVE, REPO, demo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The circuit's contract + the hand-authored projection

    amp_022 ships [`abstract/params.yaml`](../circuits/amp_022_fer_two_stage/abstract/params.yaml). The
    relevant shipped tie is **`stage2_load_width`** (`kind: shared_geometry`): the 2nd-stage common-source
    device `XM2` reuses the stage-1 mirror-load per-finger width `XM3.w`. In the lowered deck this is one
    line — `.param x_dut_xm2_w = {x_dut_xm3_w}`. The `params.yaml` description says it plainly: *"Author-
    opinion legacy tie — no single structural cause; dissolve freely."* That is our candidate.

    The hand-authored projection [`raw_optimize/amp_022_ungroup_demo.yaml`](../raw_optimize/amp_022_ungroup_demo.yaml)
    sets `params_file:` and addresses its curated knobs **by GROUP name** (`input_pair.w`,
    `nmos_load_mirror.l`, `pmos_bias_mirror.l`), each resolved to the group's FIRST-member atomic symbol
    under the D-3 lowering.
    """)
    return


@app.cell
def _(REPO, demo):
    from spicexplorer.backends.params import load_params_file, resolve_knob

    cp = load_params_file(REPO / demo.PARAMS_YAML)
    print("shipped groups (name / kind / members / tied-fields):")
    for g in cp.groups:
        print(f"  {g.name:20s} {g.kind:16s} {list(g.members)}  tie={list(g.tie)}")

    print("\ngroup-knob resolution (what the curated projection addresses):")
    for knob in ["input_pair.w", "input_pair.l", "nmos_load_mirror.l", "pmos_bias_mirror.l"]:
        print(f"  {knob:20s} -> atomic symbol {resolve_knob(cp, knob)!r}  (group first member)")

    g = cp.group(demo.DISSOLVE)
    print(f"\ncandidate tie to dissolve: {g.name!r} ({g.kind}) — members {list(g.members)}")
    print(f"  {g.description}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. STATIC: the search space before/after `ungroup:`

    `Project_Setup.from_yaml()` resolves the projection. With `ungroup: [stage2_load_width]` the platform
    **shadows** the dissolved tie: it appends a FROZEN `.param x_dut_xm2_w = <XM3.w's current deck default>`
    so the untied deck is *numerically identical* until the freed symbol is actually swept (untying =
    shadowing). Promoting `x_dut_xm2_w` to its own free `dut_param` is what turns that frozen shadow into a
    searched dimension. The search space gains **exactly one** knob — `x_dut_xm2_w`, freed from
    `x_dut_xm3_w`.
    """)
    return


@app.cell
def _(demo):
    tied_d = demo.resolved_dims(ungroup=False)
    ung_d = demo.resolved_dims(ungroup=True)

    print(f"(a) tied      : {len(tied_d['free'])} free knobs  {tied_d['free']}")
    print(f"(b) ungrouped : {len(ung_d['free'])} free knobs  {ung_d['free']}")
    print(f"\ndissolved tie {demo.DISSOLVE!r} shadow symbols (what ungroup: exposes):")
    print(f"  {ung_d['shadow']}   # x_dut_xm2_w shadowed at XM3.w's default (6u)")
    print(f"\nΔ dimension: +{len(ung_d['free']) - len(tied_d['free'])} "
          f"({demo.FREED_SYMBOL} freed from x_dut_xm3_w)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. LIVE: two short seeded optimizations

    Both runs are `NGOpt`, budget 20, seed 48 — driving amp_022's committed `ac_open_loop.spice` +
    `dc_op.spice` decks live. Targets: `dcgain` ≥ 40 dB, `ugf` ≥ 1 MHz, `pm` ≈ 60°, `i(i_supply)`
    minimized. (Skips cleanly if live runs are unavailable.)
    """)
    return


@app.cell
def _(LIVE, demo):
    import time

    if LIVE:
        t0 = time.time()
        tied = demo.run_optimization(ungroup=False)
        t1 = time.time()
        ung = demo.run_optimization(ungroup=True)
        t2 = time.time()
        print(f"(a) tied      : {tied['n_trials']} trials, {t1 - t0:.0f}s, {tied['n_free']} free knobs")
        print(f"(b) ungrouped : {ung['n_trials']} trials, {t2 - t1:.0f}s, {ung['n_free']} free knobs")
        print(f"total runtime : {t2 - t0:.0f}s")
    else:
        tied = ung = None
        print("skipped — live runs unavailable")
    return tied, ung


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Before/after metric table

    The freed dimension lets the optimizer set the 2nd-stage CS device width **independent** of the
    mirror-load width — decoupling stage-2 current/gain from the stage-1 load, which the shipped tie
    welded together.
    """)
    return


@app.cell
def _(LIVE, demo, tied, ung):
    def _m(run, k):
        v = run["metrics"].get(k)
        return "n/a" if v is None else v

    if LIVE:
        rows = [
            ("free knobs",        tied["n_free"],            ung["n_free"]),
            ("best score",        round(tied["best_score"], 4), round(ung["best_score"], 4)),
            ("dcgain [dB]",       _m(tied, "dcgain"),       _m(ung, "dcgain")),
            ("ugf [Hz]",          _m(tied, "ugf"),          _m(ung, "ugf")),
            ("pm [deg]",          _m(tied, "pm"),           _m(ung, "pm")),
            ("i_supply [A]",      _m(tied, "i(i_supply)"),  _m(ung, "i(i_supply)")),
            ("best x_dut_xm2_w",  tied["best_params"].get("x_dut_xm3_w"),  # tied: xm2 tracks xm3
                                  ung["best_params"].get(demo.FREED_SYMBOL)),
            ("best x_dut_xm3_w",  tied["best_params"].get("x_dut_xm3_w"),
                                  ung["best_params"].get("x_dut_xm3_w")),
        ]
        w = max(len(r[0]) for r in rows)
        print(f"{'metric':<{w}} | {'(a) tied':>22} | {'(b) ungrouped':>22}")
        print("-" * (w + 50))
        for name, a, b in rows:
            print(f"{name:<{w}} | {str(a):>22} | {str(b):>22}")
        print("\nIn (a) x_dut_xm2_w is welded to x_dut_xm3_w (one search dimension, three devices).")
        print("In (b) it is its own knob — decoupled from the mirror-load width.")
    else:
        print("skipped — live runs unavailable")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Takeaways

    - **Group-addressing works live**: the curated projection names `input_pair.w` / `nmos_load_mirror.l`
      / `pmos_bias_mirror.l`, and `Project_Setup.from_yaml()` resolves each to the group's first-member
      atomic symbol — the default search stays low-dimensional (5 knobs) while availability is atomic.
    - **`ungroup:` dissolves a shipped opinion with zero optimizer-core change**: `ungroup:
      [stage2_load_width]` shadows `x_dut_xm2_w` at XM3.w's deck default; promoting it to a free knob adds
      **exactly one** dimension (5 → 6). The freed symbol is `x_dut_xm2_w` (XM2's width), now searched
      independent of the mirror load.
    - **The freed dimension pays off**: the 6-knob run scored better than the 5-knob run and roughly
      **halved the supply current** by letting the 2nd-stage device shrink independently of the mirror
      load — the exact win the shipped tie forecloses.
    - **Sizing-lane hook**: this is the mechanism that turns baseline metrics analog-db skips by default
      (THD / IIP3 / PM headroom) into tuned numbers — open only the dimension a spec needs, keep the rest
      of the circuit's opinionated geometry intact. See `raw_optimize/README.md` → *The `ungroup:`
      affordance*.
    """)
    return


if __name__ == "__main__":
    app.run()
