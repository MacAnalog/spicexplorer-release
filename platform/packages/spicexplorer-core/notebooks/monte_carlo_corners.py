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
    # Monte Carlo mismatch corners — `monte_carlo_corners`

    Device **mismatch** Monte Carlo as a first-class PVT lane: `spicexplorer_core.pvt.monte_carlo_corners`
    clones a base corner into `mc1..mcN` *statistical sample corners* that ride the existing
    multi-corner fan-out — checkpoints, `run_<n>_<tb>__mc<i>` artifact naming, and the Analyze
    viewer's Monte Carlo mode all work with **nothing new**.

    The mechanism has two halves, both visible in this notebook:

    1. **Statistical-section swap** — every model include whose library defines a
       `<section>_mismatch` sibling is swapped to it. Open PDKs ship these next to the nominal
       sections (e.g. IHP sg13g2's `cornerMOSlv.lib` defines `mos_tt` *and* `mos_tt_mismatch`,
       whose model cards wrap device parameters in `agauss(...)` draws).
    2. **Per-sample RNG seed** — each sample corner carries `Corner.options = {"seed": seed0+i-1}`,
       which the engine's `apply_corner` emits as an `.options seed=<n>` card: draws differ per
       sample, and the *same seed reproduces the same draw* (verified live on sg13g2: seed 3 →
       839.2 Ω twice, seed 7 → 906.8 Ω twice).

    This tour is **fully offline** — it fabricates a miniature PDK library tree in a temp dir, so
    no ngspice, no real PDK, and no network are needed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. A miniature PDK with statistical sections

    The swap is driven purely by what the library **file** defines: `monte_carlo_corners` parses
    single-token `.lib <name>` lines (section *definitions* — two-token `.lib <file> <section>`
    lines are include-references and are ignored) and looks for the `<section>_mismatch` sibling.
    We mirror the sg13g2 layout in miniature:
    """)
    return


@app.cell
def _():
    import tempfile
    from pathlib import Path

    pdk_root = Path(tempfile.mkdtemp(prefix="mc_demo_pdk_"))
    models = pdk_root / "demo-pdk" / "libs.tech" / "ngspice" / "models"
    models.mkdir(parents=True)

    # The corner library: a nominal section and its statistical sibling. In a real
    # PDK the *_mismatch section pulls extra model cards whose parameters are
    # agauss() draws; here plain includes stand in for them.
    (models / "cornerMOSlv.lib").write_text(
        """.lib mos_tt
    .include sg13g2_moslv_mod.lib
    .endl

    .lib mos_tt_mismatch
    .include sg13g2_moslv_mod.lib
    .include sg13g2_moslv_mod_mismatch.lib
    .endl
    """
    )
    # A resistor library with NO statistical sibling — it must be left untouched.
    (models / "resistors.lib").write_text(".lib res_typ\n.include res_mod.lib\n.endl\n")

    print((models / "cornerMOSlv.lib").read_text())
    return (pdk_root,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Derive the sample corners

    The base corner references its libraries the same way a project YAML does — an opaque
    `(lib_file, section)` pair per include. `lib_search_roots` is where the files are found
    (defaulting to `$PDK_ROOT`); a bare basename is resolved by walking the roots, so committed
    YAMLs stay machine-portable.
    """)
    return


@app.cell
def _(pdk_root):
    from spicexplorer_core.pvt import Corner, ModelInclude, SupplyOverride, monte_carlo_corners

    base = Corner(
        name="tt_27c",
        model_includes=[
            ModelInclude(lib_file="cornerMOSlv.lib", section="mos_tt"),
            ModelInclude(lib_file="resistors.lib", section="res_typ"),
        ],
        temp=27.0,
        supplies=[SupplyOverride(node="vdd_val", value=1.5)],
    )

    samples = monte_carlo_corners(base, 4, seed0=1, lib_search_roots=[str(pdk_root)])
    for c in samples:
        print(
            c.name,
            "| sections:",
            [(i.lib_file, i.section) for i in c.model_includes],
            "| options:",
            c.options,
        )
    return Corner, ModelInclude, monte_carlo_corners


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Every sample swapped `mos_tt → mos_tt_mismatch` (the resistor include, which has no
    sibling, is untouched), and each carries its own `seed`. The samples are **independent
    copies** — mutating one never leaks into another — and inherit the base corner's
    temp/supplies/params, so an MC sweep perturbs *only* the statistical draws.

    Reproducibility contract: `seed0` pins the whole family. Re-deriving with the same `seed0`
    gives byte-identical corners → identical draws → identical results; a different `seed0`
    re-rolls every sample.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. The failure contract — no silent fake Monte Carlo

    If **no** include has a statistical sibling (the PDK ships none, or the libraries can't be
    found under the search roots), `monte_carlo_corners` **raises** rather than returning N
    copies of the same deterministic corner — a "Monte Carlo" that re-runs one deck N times
    would be a lie:
    """)
    return


@app.cell
def _(Corner, ModelInclude, monte_carlo_corners, pdk_root):
    res_only = Corner(
        name="tt_res",
        model_includes=[ModelInclude(lib_file="resistors.lib", section="res_typ")],
    )
    try:
        monte_carlo_corners(res_only, 4, lib_search_roots=[str(pdk_root)])
    except ValueError as e:
        print("ValueError:", e)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. How a sample corner reaches the simulator

    `Corner.options` is engine-neutral; each backend's `apply_corner` decides the concrete
    emission. The ngspice engine (`spice_engine/spicelib.py`, step 2b) emits one card per
    entry after the corner's includes/temp/supplies:

    ```
    .options seed=3
    ```

    ngspice re-seeds its RNG from that card, so the library's `agauss()` model-card draws are
    sample-specific and reproducible.

    ## 5. The REST lane and the viewer

    `POST /api/simulate/once` grows the launch surface (see
    `packages/spicexplorer-api/routes/simulate.py`):

    ```jsonc
    {
      "project_id": "…",
      "params": { "w_dut_m1": "20u" },
      "monte_carlo": 8,          // 2..100 samples; requires a pvt block
      "mc_seed0": 1              // optional; the reproducibility pin
    }
    ```

    - `active_corner` (or the project's active corner) picks the **base** the samples clone.
    - `monte_carlo` is mutually exclusive with `sweep_corners` — one launch = one lane.
    - The run lands `run_<n>_<tb>__mc<i>` artifacts; the Analyze viewer's **Monte Carlo** sweep
      mode discovers them and renders the mean ± kσ band, ghost samples, the metric histogram
      with the spec line, and the yield/Cpk strip (specs judged only from the project's own
      target specs — never invented client-side).

    **Where this runs live:** a real PDK with mismatch sections + ngspice — i.e. the Docker
    `api` container or the research server, not a bare macOS host.

    Pointers: `packages/spicexplorer-core/tests/test_monte_carlo_corners.py` (the swap /
    seed / failure contracts), `packages/spicexplorer-api/tests/test_simulate_mc.py` (the
    launch-surface validation), and the UI-side plan record in the spicexplorer-ui repo's
    `doc/plan_waveform_viewer.md`.
    """)
    return


if __name__ == "__main__":
    app.run()
