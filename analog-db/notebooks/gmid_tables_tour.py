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
    # gm/ID lookup-table tour — the committed tri-PDK LUTs

    The analog-db ships **pre-computed gm/ID lookup tables** (Phase 6a): each PDK's core nmos is
    characterized over an `(L × VGS × VDS × VSB)` grid with an automated ngspice testbench and stored as
    a **pygmid-compatible `.pkl`** at `_shared/gmid/<pdk>/<device>__<corner>.pkl`. This notebook is the
    LUT layer's test/experimentation surface: load the tables, inspect them, and reproduce the canonical
    gm/ID design curves — including a **cross-PDK comparison** you can't get from any single-technology kit.

    - Generation: `analog-db gmid-extract --pdk <pdk>` (docs: `_shared/GMID.md`) — corner, LV/HV device
      variant, and the full grid are configurable.
    - Reader: [`pygmid`](https://github.com/dreoilin/pygmid) (`Lookup`), the Python port of the
      book's MATLAB kit ([Jespers & Murmann](https://github.com/bmurmann/Book-on-gm-ID-design)).
    - Worked sizing patterns: [iic-jku/analog-circuit-design](https://github.com/iic-jku/analog-circuit-design);
      the sizing flow itself is the companion notebook `gmid_sizing_demo.py`.
    """)
    return


@app.cell
def _():
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from pygmid import Lookup

    from spicexplorer_analog_db import paths, pdks

    plt.rcParams["figure.figsize"] = (11, 3.6)

    GMID_ROOT = paths.shared_root() / "gmid"
    luts = {p.parent.name: Lookup(str(p)) for p in sorted(GMID_ROOT.glob("*/*.pkl"))}
    print("committed LUTs:")
    for _pdk, _lk in luts.items():
        print(f"  {_pdk:12} {_lk['INFO']}")
    return luts, np, pd, pdks, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What's inside a table

    A flat dict: four **axis vectors** (`L` in µm, `VGS`/`VDS`/`VSB` in V) and 4-D arrays indexed
    `[L, VGS, VDS, VSB]` — DC operating point (`ID VT GM GMB GDS`), capacitances (`CGG CGS CGD CGB CDD
    CSS`), and noise PSDs (`STH SFL`) — plus the characterization header (`CORNER TEMP W NFING`).
    Everything below derives from these arrays.
    """)
    return


@app.cell
def _(luts, pd):
    _rows = []
    for _pdk, _lk in luts.items():
        _rows.append({
            "pdk": _pdk, "corner": _lk["CORNER"], "T (K)": _lk["TEMP"], "W (µm)": _lk["W"],
            "L grid (µm)": f"{_lk['L'][0]:g}…{_lk['L'][-1]:g} ({len(_lk['L'])} pts)",
            "VGS": f"0…{_lk['VGS'][-1]:g} ({len(_lk['VGS'])} pts)",
            "VDS": f"0…{_lk['VDS'][-1]:g} ({len(_lk['VDS'])} pts)",
            "VSB pts": len(_lk["VSB"]),
        })
    pd.DataFrame(_rows).set_index("pdk")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The canonical design curves

    **gm/ID vs VGS** — the transconductance-efficiency curve. Weak inversion plateaus near
    ~25–30 S/A, strong inversion falls toward a few S/A; this is the knob the whole methodology
    turns. (Curves at mid-rail VDS, VSB = 0.)
    """)
    return


@app.cell
def _(luts, np, plt):
    _fig, _axes = plt.subplots(1, len(luts), sharey=True)
    for _ax, (_pdk, _lk) in zip(np.atleast_1d(_axes), luts.items()):
        _vds_i = len(_lk["VDS"]) // 2
        for _li in [0, len(_lk["L"]) // 2, len(_lk["L"]) - 1]:
            _gm, _idd = _lk["GM"][_li, :, _vds_i, 0], _lk["ID"][_li, :, _vds_i, 0]
            with np.errstate(divide="ignore", invalid="ignore"):
                _eff = np.where(_idd > 0, _gm / _idd, np.nan)
            _ax.plot(_lk["VGS"], _eff, label=f"L={_lk['L'][_li]:g}µm")
        _ax.set_title(_pdk); _ax.set_xlabel("VGS (V)"); _ax.grid(alpha=0.3); _ax.legend(fontsize=8)
    np.atleast_1d(_axes)[0].set_ylabel("gm/ID (S/A)")
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **gm/ID vs current density JD = ID/W** — the master sizing chart: pick gm/ID, read JD, and width
    follows from `W = ID / JD`. Longer channels shift the curve left (less current per µm at the same
    efficiency).
    """)
    return


@app.cell
def _(luts, np, plt):
    _fig, _axes = plt.subplots(1, len(luts), sharey=True)
    for _ax, (_pdk, _lk) in zip(np.atleast_1d(_axes), luts.items()):
        _vds_i = len(_lk["VDS"]) // 2
        for _li in [0, len(_lk["L"]) // 2, len(_lk["L"]) - 1]:
            _gm, _idd = _lk["GM"][_li, :, _vds_i, 0], _lk["ID"][_li, :, _vds_i, 0]
            with np.errstate(divide="ignore", invalid="ignore"):
                _eff = np.where(_idd > 0, _gm / _idd, np.nan)
            _ax.semilogx(_idd / _lk["W"], _eff, label=f"L={_lk['L'][_li]:g}µm")
        _ax.set_title(_pdk); _ax.set_xlabel("JD = ID/W (A/µm)"); _ax.grid(alpha=0.3, which="both"); _ax.legend(fontsize=8)
    np.atleast_1d(_axes)[0].set_ylabel("gm/ID (S/A)")
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The two tradeoff curves** — transit frequency `fT = gm/(2π·CGG)` (speed) and intrinsic gain
    `gm/gds` (accuracy) against gm/ID. Together they frame every sizing compromise: low gm/ID buys
    speed, high gm/ID buys efficiency/swing, long L buys gain at the cost of fT.
    """)
    return


@app.cell
def _(luts, np, plt):
    _fig, (ax1, ax2) = plt.subplots(1, 2)
    for _pdk, _lk in luts.items():
        _vds_i = len(_lk["VDS"]) // 2
        for _li, ls in [(0, "-"), (len(_lk["L"]) - 1, "--")]:
            _gm, _idd = _lk["GM"][_li, :, _vds_i, 0], _lk["ID"][_li, :, _vds_i, 0]
            cgg, gds = _lk["CGG"][_li, :, _vds_i, 0], _lk["GDS"][_li, :, _vds_i, 0]
            with np.errstate(divide="ignore", invalid="ignore"):
                _eff = np.where(_idd > 0, _gm / _idd, np.nan)
                ft = np.where(cgg > 0, _gm / (2 * np.pi * cgg), np.nan)
                av = np.where(gds > 0, _gm / gds, np.nan)
            lbl = f"{_pdk} L={_lk['L'][_li]:g}"
            ax1.semilogy(_eff, ft, ls, label=lbl, alpha=0.8)
            ax2.plot(_eff, av, ls, label=lbl, alpha=0.8)
    ax1.set_xlabel("gm/ID (S/A)"); ax1.set_ylabel("fT (Hz)"); ax1.grid(alpha=0.3, which="both")
    ax2.set_xlabel("gm/ID (S/A)"); ax2.set_ylabel("intrinsic gain gm/gds"); ax2.grid(alpha=0.3)
    ax1.legend(fontsize=7); ax2.legend(fontsize=7)
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cross-PDK comparison at matched L

    All three L-grids contain **0.5 µm** — a direct apples-to-apples overlay of the three
    technologies' efficiency-vs-density tradeoff (something the single-PDK book kits can't show).
    """)
    return


@app.cell
def _(luts, np, plt):
    _fig, _ax = plt.subplots(figsize=(7, 4.2))
    for _pdk, _lk in luts.items():
        _li = int(np.argmin(np.abs(_lk["L"] - 0.5)))
        _vds_i = len(_lk["VDS"]) // 2
        _gm, _idd = _lk["GM"][_li, :, _vds_i, 0], _lk["ID"][_li, :, _vds_i, 0]
        with np.errstate(divide="ignore", invalid="ignore"):
            _eff = np.where(_idd > 0, _gm / _idd, np.nan)
        _ax.semilogx(_idd / _lk["W"], _eff, label=f"{_pdk} (L={_lk['L'][_li]:g}µm, VDS={_lk['VDS'][_vds_i]:g}V)")
    _ax.set_xlabel("JD = ID/W (A/µm)"); _ax.set_ylabel("gm/ID (S/A)")
    _ax.set_title("Three PDKs, one chart — core nmos @ tt, L = 0.5 µm")
    _ax.grid(alpha=0.3, which="both"); _ax.legend()
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## pygmid lookups (the sizing API the tables serve)

    `Lookup` interpolates the grid: raw quantities vs a bias (`GM` at a VGS), **ratio-vs-ratio** mode
    (`ID_W` at a target `GM_ID` — the sizing workhorse), and the inverse `look_upVGS`. Note: pass
    **scalar L** (loop for L sweeps — vectorization is over GM_ID/VGS).
    """)
    return


@app.cell
def _(luts, np, pd):
    nch = luts["sky130"]
    gm_id = np.array([5, 10, 15, 20, 25])
    jd = nch.look_up("ID_W", GM_ID=gm_id, VDS=0.9, VSB=0, L=0.5)     # A/µm at each efficiency
    vgs10 = float(nch.look_upVGS(GM_ID=10, VDS=0.9, VSB=0, L=0.5))   # bias for gm/ID = 10
    ft10 = float(nch.look_up("GM_CGG", GM_ID=10, VDS=0.9, VSB=0, L=0.5)) / (2 * np.pi)
    pd.DataFrame({"gm/ID (S/A)": gm_id, "JD (A/µm)": np.asarray(jd)}).set_index("gm/ID (S/A)").T \
        .map("{:.3e}".format)
    return ft10, vgs10


@app.cell
def _(ft10, vgs10):
    print(f"at gm/ID=10, L=0.5µm, VDS=0.9V:  VGS = {vgs10:.3f} V,  fT = {ft10/1e9:.2f} GHz")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## PDK passives (the other half of sizing)

    Sizing also needs to turn a target R into squares and a target C into MIM area. The measured tt
    constants live in each PDK registry (`_shared/pdk/<pdk>.yaml` → `passives.models`).
    """)
    return


@app.cell
def _(luts, pd, pdks):
    _rows = []
    for _pdk in luts:
        reg = pdks.load_registry(_pdk)
        for model, info in (reg.get("passives", {}).get("models", {}) or {}).items():
            _rows.append({"pdk": _pdk, "model": model, "kind": info["kind"],
                         "sheet_res (Ω/□)": info.get("sheet_res", ""),
                         "area_cap (F/µm²)": info.get("area_cap", "")})
    pd.DataFrame(_rows).set_index(["pdk", "model"])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Regenerating / extending the tables

    Needs the EDA base image (`docker compose --profile base build spice-base` in spicexplorer-platform):

    ```bash
    analog-db gmid-extract --pdk sky130                                  # re-write the committed LUT
    analog-db gmid-extract --pdk sky130 --device sky130_fd_pr__pfet_01v8 # add the pmos
    analog-db gmid-extract --pdk ihp-sg13g2 --device sg13_hv_nmos        # HV variant (corner lib auto-swaps)
    analog-db gmid-extract --pdk gf180mcu --corner ss --vgs 0,0.025,3.3  # corner + finer grid
    ```

    Every knob (device incl. LV/HV variant, corner, grids, W, fingers, temperature) is configurable —
    see `_shared/GMID.md`. **What's next:** `gmid_sizing_demo.py` applies these tables to actual
    device sizing; the typed `spicexplorer-gmid` platform tool grows out of these patterns
    (meta-repo `doc/archive/plan_gmid_sizing.md`).
    """)
    return


if __name__ == "__main__":
    app.run()
