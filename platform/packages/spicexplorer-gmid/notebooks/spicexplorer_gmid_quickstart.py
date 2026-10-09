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
    # spicexplorer-gmid quickstart

    Size a transistor from a gm/ID lookup table (LUT): pick gm/ID and L, read the current
    density, V<sub>GS</sub>, intrinsic gain and f<sub>T</sub> off the table, and scale to a width.
    This notebook runs the sizing flow of `spicexplorer_gmid` (`load_lut` / `search_luts`,
    `DeviceTable.at`, `gm_id_band`, `sweep`, `size_for_gm`, `size_for_current_density`, the
    finger-width gate, `size_resistor` / `size_capacitor`) on the four committed tables, all at
    the typical corner, 300 K and a 5 µm characterization finger. `LUTRegistry`, `look_up`,
    `gm_id_for_jd` and `from_lut_dict` are in the package README, not here.

    | PDK | device | table |
    |---|---|---|
    | sky130 | 1.8 V core NMOS | `sky130_fd_pr__nfet_01v8__tt.pkl` |
    | sky130 | 1.8 V core PMOS | `sky130_fd_pr__pfet_01v8__tt.pkl` |
    | ihp-sg13g2 | 1.5 V lv NMOS | `sg13_lv_nmos__tt.pkl` |
    | ihp-sg13g2 | 1.5 V lv PMOS | `sg13_lv_pmos__tt.pkl` |

    It imports `spicexplorer_gmid` and nothing else from the platform; in particular not
    `spicexplorer_analog_db`, which the shared venv does not install. `load_lut` finds the tables
    by name (next section). No simulator runs.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Where the tables are: `default_roots`, `search_luts`

    `load_lut(pdk, device)` searches a fixed list of directories, first match wins:
    `$SPICEXPLORER_GMID_ROOTS`, `~/.spicexplorer/gmid`, the shared installation under `$SX_ROOT`,
    and the platform checkout's `examples/analog-db/_shared/gmid`. `search_luts()` lists every
    table those directories hold, one manifest per table, with the grid it was characterized on.
    """)
    return


@app.cell
def _():
    import math

    import numpy as np
    from matplotlib.figure import Figure
    from spicexplorer_gmid import (
        GeometryBounds,
        OutOfGridError,
        default_roots,
        finger_width_set,
        load_lut,
        search_luts,
        size_capacitor,
        size_for_current_density,
        size_for_gm,
        size_resistor,
    )

    DEVICES = [
        ("sky130", "sky130_fd_pr__nfet_01v8"),
        ("sky130", "sky130_fd_pr__pfet_01v8"),
        ("ihp-sg13g2", "sg13_lv_nmos"),
        ("ihp-sg13g2", "sg13_lv_pmos"),
    ]
    print("search order:")
    for _root in default_roots():
        print(
            f"  {'found  ' if _root.is_dir() else 'absent '} {_root.name}/ in {_root.parent.name}/"
        )
    manifests = {(m.pdk, m.device): m for m in search_luts() if m.corner == "tt"}
    missing = [d for d in DEVICES if d not in manifests]
    assert not missing, f"not reachable by load_lut: {missing}"
    print(f"\n{'pdk':11s} {'device':24s} {'L grid / um':>13s} {'VDS grid / V':>13s} {'T / K':>6s}")
    for _pdk, _dev in DEVICES:
        _m = manifests[(_pdk, _dev)]
        _L, _vds = _m.dimensions["L_um"], _m.dimensions["VDS_V"]
        print(
            f"{_pdk:11s} {_dev:24s} {_L.min:5.2f} .. {_L.max:4.2f} "
            f"{_vds.min:5.2f} .. {_vds.max:4.2f} {_m.conditions.temp_k:6.1f}"
        )
    return (
        DEVICES,
        Figure,
        GeometryBounds,
        OutOfGridError,
        finger_width_set,
        load_lut,
        math,
        np,
        size_capacitor,
        size_for_current_density,
        size_for_gm,
        size_resistor,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. An operating point: `DeviceTable.at`

    `load_lut` returns a `DeviceTable`. `at(gm_id, L, vds, vsb=0)` interpolates everything but
    those four coordinates. The table below reads each device at gm/ID = 12 V<sup>-1</sup>,
    L = 0.5 µm and |V<sub>DS</sub>| = 0.6 V. PMOS tables store |I<sub>D</sub>| and |V<sub>SB</sub>|,
    so the same positive numbers are passed for both polarities.
    """)
    return


@app.cell
def _(DEVICES, load_lut):
    tables = {dev: load_lut(pdk, dev) for pdk, dev in DEVICES}
    BIAS = dict(L=0.5, vds=0.6)
    print(f"{'device':24s} {'VGS / V':>8s} {'JD / (uA/um)':>13s} {'gm/gds':>7s} {'fT / GHz':>9s}")
    for _dev, _t in tables.items():
        _op = _t.at(gm_id=12, **BIAS)
        print(f"{_dev:24s} {_op.vgs:8.3f} {_op.jd * 1e6:13.3f} {_op.av0:7.1f} {_op.ft / 1e9:9.2f}")
    return BIAS, tables


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. The reachable gm/ID band: `gm_id_band`

    gm/ID rises towards weak inversion, peaks, then falls as the device turns off, and pygmid
    inverts only the branch above the peak's V<sub>GS</sub>. `gm_id_band(L, vds)` returns that
    branch as `(lo, hi, vgs_peak)`. `at`, `sweep` and the sizing calls raise `OutOfGridError`
    outside it, with the band in the message, instead of returning an extrapolated value.
    """)
    return


@app.cell
def _(BIAS, OutOfGridError, tables):
    bands = {}
    print(f"{'device':24s} {'lo / V^-1':>10s} {'hi / V^-1':>10s} {'VGS at peak / V':>16s}")
    for _dev, _t in tables.items():
        bands[_dev] = _t.gm_id_band(**BIAS)
        _lo, _hi, _vp = bands[_dev]
        print(f"{_dev:24s} {_lo:10.2f} {_hi:10.2f} {_vp:16.3f}")

    _dev = "sky130_fd_pr__nfet_01v8"
    try:
        tables[_dev].at(gm_id=1.2 * bands[_dev][1], **BIAS)
    except OutOfGridError as exc:
        print(f"\n{_dev} at 1.2 x the peak: OutOfGridError: {str(exc)[:150]} ...")
    return (bands,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The trade-off curves: `sweep`

    `sweep(gm_id=(lo, hi), L, vds)` returns arrays over gm/ID. The figure plots f<sub>T</sub> and
    the intrinsic gain gm/g<sub>ds</sub> from gm/ID = 5 to 20 V<sup>-1</sup>, inside every band
    of section 3, at L = 0.5 µm and |V<sub>DS</sub>| = 0.6 V: the speed given up for efficiency,
    per device.
    """)
    return


@app.cell
def _(BIAS, Figure, bands, tables):
    GM_ID_RANGE = (5.0, 20.0)
    for _dev, (_lo, _hi, _) in bands.items():
        assert _lo <= GM_ID_RANGE[0] and GM_ID_RANGE[1] <= _hi, f"{_dev}: sweep leaves its band"
    sweeps = {_dev: _t.sweep(gm_id=GM_ID_RANGE, **BIAS, n=31) for _dev, _t in tables.items()}

    fig = Figure(figsize=(9, 3.4), layout="constrained")
    ax_ft, ax_av = fig.subplots(1, 2)
    for _dev, _sw in sweeps.items():
        ax_ft.semilogy(_sw.gm_id, _sw.ft / 1e9, label=_dev)
        ax_av.plot(_sw.gm_id, _sw.av0, label=_dev)
    ax_ft.set(xlabel="gm/ID / V$^{-1}$", ylabel="fT / GHz", title="transit frequency")
    ax_av.set(xlabel="gm/ID / V$^{-1}$", ylabel="gm/gds", title="intrinsic gain")
    ax_av.legend(fontsize=7)
    fig.suptitle("tt, 300 K, L = 0.5 um, |VDS| = 0.6 V, VSB = 0")
    print(f"{'device':24s} {'fT at gm/ID=5 / GHz':>20s} {'fT at gm/ID=20 / GHz':>21s}")
    for _dev, _sw in sweeps.items():
        print(f"{_dev:24s} {_sw.ft[0] / 1e9:20.3f} {_sw.ft[-1] / 1e9:21.3f}")
    fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Size a device: `size_for_gm` and `size_for_current_density`

    **gm first.** A load C<sub>L</sub> = 1 pF at a unity-gain frequency of 50 MHz needs
    gm = 2π · 50 MHz · 1 pF. `size_for_gm` picks I<sub>D</sub> = gm / (gm/ID) and
    W = I<sub>D</sub> / J<sub>D</sub>; `wf_max` splits W into fingers no wider than 5 µm.

    **Current first.** `size_for_current_density` fixes I<sub>D</sub> = 20 µA at gm/ID = 15
    instead, the usual choice for a mirror or a bias device.

    Every `SizedDevice` carries its sanity gates (saturation headroom, intrinsic gain, f<sub>T</sub>,
    finger width, geometry bounds), and `passed` is true when no blocking gate fails.
    """)
    return


@app.cell
def _(BIAS, GeometryBounds, math, size_for_current_density, size_for_gm, tables):
    GM = 2 * math.pi * 50e6 * 1e-12
    BOUNDS = GeometryBounds(w_min=0.42, w_max=100.0, l_min=0.13)
    print(f"target gm = {GM * 1e3:.3f} mS\n")
    print(
        f"{'flow':8s} {'device':24s} {'ID / uA':>8s} {'W / um':>8s} {'nf':>3s} {'passed':>7s}  gates"
    )
    for _dev, _t in tables.items():
        for _flow, _d in (
            ("gm", size_for_gm(_t, gm=GM, gm_id=12, **BIAS, bounds=BOUNDS, wf_max=5.0)),
            (
                "current",
                size_for_current_density(_t, ID=20e-6, gm_id=15, **BIAS, bounds=BOUNDS, wf_max=5.0),
            ),
        ):
            _gates = ", ".join(f"{g.name}={g.status}" for g in _d.gates)
            print(
                f"{_flow:8s} {_dev:24s} {_d.ID * 1e6:8.2f} {_d.W:8.2f} {_d.nf:3d} {str(_d.passed):>7s}  {_gates}"
            )
    return (GM,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. The finger-width caveat: `finger_width_set` and the `finger_width` gate

    A table describes fingers at its own characterization width, `w_char` = 5 µm here; J<sub>D</sub>
    and the capacitances per µm move with the finger width itself. `finger_width_set` opens every
    finger width the roots hold for one device, and interpolates across them. The committed store
    holds only the 5 µm tables, so on it the set has one member.

    The `finger_width` gate compares the drawn W/nf with `w_char`. With `wf=` given, a finger under
    `w_char/2` or over `2·w_char` fails and vetoes `passed`. With neither `wf` nor `wf_max`, a
    finger outside that window is reported `unchecked` and does not veto: W/nf is then the total
    width the gm target asked for, not a finger choice. The cell shows the three states.
    """)
    return


@app.cell
def _(BIAS, GM, finger_width_set, size_for_gm, tables):
    _fs = finger_width_set("sky130", "sky130_fd_pr__nfet_01v8")
    print("sky130 nfet finger widths held:", _fs.finger_widths, "um")
    _t = tables["sky130_fd_pr__nfet_01v8"]
    for _label, _gm, _kw in (
        ("gm, wf=5", GM, dict(wf=5.0)),
        ("gm, wf=1", GM, dict(wf=1.0)),
        ("gm/5, no wf, no wf_max", GM / 5, {}),
    ):
        _d = size_for_gm(_t, gm=_gm, gm_id=12, **BIAS, **_kw)
        _g = next(g for g in _d.gates if g.name == "finger_width")
        print(
            f"{_label:24s} W/nf = {_d.W / _d.nf:5.2f} um  finger_width={_g.status:9s} passed={_d.passed}"
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Passives: `size_resistor`, `size_capacitor`

    Closed-form, from the PDK's sheet resistance [Ω/□] and area capacitance [F/µm²]. The two
    constants below are the sky130 `res_high_po` and `cap_mim_m3_1` values measured at the typical
    corner; pass the values of your PDK.
    """)
    return


@app.cell
def _(size_capacitor, size_resistor):
    _r = size_resistor(10e3, sheet_res=355, w_um=1.0)
    _c = size_capacitor(1e-12, area_cap=2.07e-15)
    print(f"10 kOhm at 355 Ohm/sq, W = 1 um: {_r.squares:.1f} squares, L = {_r.l_um:.1f} um")
    print(f"1 pF at 2.07 fF/um^2: {_c.area_um2:.0f} um^2")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Where to go next

    - `examples/notebooks/gmid_cascode_resizing.py` sizes the six device roles of a folded-cascode
      OTA (`amp_004_folded_cascode`, sky130) with these calls and writes a `sizing.yaml` fragment.
    - The package README covers `LUTRegistry`, the manifest sidecars and the extraction commands
      for tables that are not committed.
    """)
    return


if __name__ == "__main__":
    app.run()
