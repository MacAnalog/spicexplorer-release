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
    # spicexplorer-core quickstart

    `spicexplorer-core` is the platform kernel every other package builds on: the **ngspice engine
    wrapper** (`spice_engine`), **netlist introspection** (`NetlistView`), **engineering-string
    parsing** (`eng`), **PVT corner primitives** (`pvt`), **environment detection** (`env`), and
    **workspace root anchoring** (`paths`). Everything here is PDK-free; the one simulation cell
    needs only `ngspice` on PATH (no PDK).
    """)
    return


@app.cell
def _():
    from spicexplorer_core.env import probe_env

    env = probe_env()
    print(f"ngspice: {env['ngspice_ok']} ({env['ngspice_path']})")
    print(f"PDK    : {env['pdk_ok']} — {env['pdk_detail']}")
    print(f"live PDK runs enabled: {env['live_runs_enabled']}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Engineering strings — `parse_value`

    SPICE-style values parse to floats. The multipliers are **case-sensitive**: `m` = milli,
    `M` = mega (a classic silent-corruption trap this function refuses to guess about).
    """)
    return


@app.cell
def _():
    from spicexplorer_core.eng import parse_value

    for s in ["0.18u", "50f", "1.2k", "2M", "3m", "1.8", "inf"]:
        print(f"  parse_value({s!r:8}) = {parse_value(s):.4g}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Workspace anchoring — `project_root()`

    One root-resolution seam for the whole platform (the `.spicexplorer-root` sentinel, or the
    `$SPICEXPLORER_ROOT` override in containers) — never a depth-sensitive `parents[N]` walk.
    """)
    return


@app.cell
def _():
    from spicexplorer_core import project_root

    root = project_root()
    print(root)
    print("examples:", [p.name for p in (root / "examples").iterdir() if p.is_dir()][:5])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Netlist introspection — `NetlistView`

    Parse a netlist (file or string) and walk its structure without any simulator. This is the
    ingestion seam circuitgraph and netlist2tf both build on. The fixture below has a
    **hyphenated subckt name** (`ota-5t`) — a real-world xschem artifact `NetlistView` resolves.
    """)
    return


@app.cell
def _(mo):
    from pathlib import Path

    from spicexplorer_core.spice_engine import NetlistView

    view = NetlistView.from_file(mo.notebook_dir() / "../tests/fixtures/ota-5t_tb-ac.spice")
    print("components:", view.get_components())
    print("nodes     :", view.get_all_nodes())
    print("params    :", dict(list(view.get_parameters().items())[:4]))
    return Path, view


@app.cell
def _(view):
    # step INTO a subckt instance (resolves the hyphenated `ota-5t` definition)
    inner = view.get_subcircuit("XOTA")
    print("XOTA ports   :", view.get_subcircuit_ports("XOTA"))
    print("XOTA devices :", inner.get_components())
    print(
        "M1 wired to  :",
        inner.get_component_nodes("XM1")
        if "XM1" in inner.get_components()
        else inner.get_component_nodes(inner.get_components()[0]),
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## PVT primitives — `Corner` / `PVTConfig`

    Corners are plain typed data: ordered model includes, a temperature, supply/param overrides.
    Core never interprets PDK specifics — `NGSpice_Wrapper.apply_corner(corner)` later mutates a
    netlist with exactly these directives (idempotently).
    """)
    return


@app.cell
def _():
    from spicexplorer_core.pvt import Corner, ModelInclude, PVTConfig, SupplyOverride

    cfg = PVTConfig(
        active_corner="ss_hot",
        corners=[
            Corner(
                name="tt",
                temp=27.0,
                supplies=[SupplyOverride("VDD", 1.8)],
                model_includes=[ModelInclude("cornerMOSlv.lib", "mos_tt")],
            ),
            Corner(
                name="ss_hot",
                temp=85.0,
                supplies=[SupplyOverride("VDD", 1.62)],
                model_includes=[ModelInclude("cornerMOSlv.lib", "mos_ss")],
            ),
        ],
    )
    c = cfg.get_active()
    print(f"active corner: {c.name} | T={c.temp}°C | {c.supplies[0].node}={c.supplies[0].value}V")
    print(f".lib lines   : {[f'{m.lib_file} {m.section}' for m in c.model_includes]}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Run a simulation — `NGSpice_Wrapper` (needs ngspice, no PDK)

    The engine wrapper runs a netlist file and hands back parsed vectors (`spicelib` rawfiles →
    numpy). A PDK-free RC low-pass demonstrates the full loop: write → run → extract → plot.

    > ⚠️ **Gotcha:** the wrapper **deletes and re-creates `output_folder`** on construction —
    > always give it its own disposable directory, never the directory holding your netlist.
    """)
    return


@app.cell
def _():
    import shutil

    NGSPICE_OK = shutil.which("ngspice") is not None
    print("ngspice on PATH:", NGSPICE_OK, "" if NGSPICE_OK else "→ the next cell will skip")
    return (NGSPICE_OK,)


@app.cell
def _(NGSPICE_OK, Path, mo):
    if not NGSPICE_OK:
        print("SKIPPED — install ngspice to run this cell.")
    else:
        import tempfile

        import matplotlib.pyplot as plt
        import numpy as np
        from spicexplorer_core.spice_engine import Ngspice_Plot_Type, NGSpice_Wrapper

        work = Path(tempfile.mkdtemp(prefix="core_quickstart_"))
        deck = work / "rc.cir"
        deck.write_text("""* RC low-pass (fc = 1/(2*pi*R*C) ~ 1.59 MHz) — spicelib wants a `*` title line
    V1 in 0 dc 0 ac 1
    R1 in out 1k
    C1 out 0 100p
    .ac dec 20 1k 1G
    .end
    """)
        # output_folder gets wiped by the wrapper — keep it separate from the netlist's dir
        w = NGSpice_Wrapper(netlist_filename=deck, testbench_name="rc", output_folder=work / "runs")
        raw, log, _ = w.run_and_wait()
        freq = w.extract_wave("frequency", Ngspice_Plot_Type.AC, is_real=True)
        vout = w.extract_wave("v(out)", Ngspice_Plot_Type.AC)

        fig, ax = plt.subplots(figsize=(7, 3.2))
        ax.semilogx(freq, 20 * np.log10(np.abs(vout)))
        ax.axvline(1 / (2 * np.pi * 1e3 * 100e-12), color="r", ls=":", label="analytic fc")
        ax.axhline(-3, color="gray", ls=":", lw=0.8)
        ax.set_xlabel("Hz")
        ax.set_ylabel("|H| (dB)")
        ax.grid(alpha=0.3, which="both")
        ax.legend()
        plt.tight_layout()
        fc_idx = int(np.argmin(np.abs(20 * np.log10(np.abs(vout)) + 3.0)))
        print(f"-3 dB at ~{freq[fc_idx] / 1e6:.2f} MHz (analytic 1.59 MHz)")
        mo.output.append(fig)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Where to go next

    - **circuitgraph** (`packages/spicexplorer-circuitgraph/notebooks/`) — netlist ↔ typed graph,
      serialization for LLMs, cross-PDK retargeting.
    - **netlist2tf** (`packages/spicexplorer-netlist2tf/notebooks/`) — netlist → symbolic transfer
      function with auditable simplification.
    - **optimizer** — the scannable YAML-DSL → engines → analog-db guide
      (`packages/spicexplorer/notebooks/optimizer_quickstart.py`; the classic per-example
      scripts live in `examples/OTA/*/sizing/`).
    - **PVT in anger**: `apply_corner()` drives real corner sims in the optimizer
      (platform `doc/archive/PVT_plan.md`).
    """)
    return


if __name__ == "__main__":
    app.run()
