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
    # gm/ID sizing demo — from spec to W/L on a real PDK table

    The gm/ID method (Jespers & Murmann) sizes a transistor without square-law formulas or SPICE
    tweaking: choose an **inversion level** (gm/ID) and **channel length** per device, read everything
    else off the pre-characterized LUT, and de-normalize to width. This notebook walks the canonical
    flows on the committed sky130 table — it is also the experimentation surface that seeds the
    `spicexplorer-gmid` tool's API (meta-repo `doc/archive/plan_gmid_sizing.md`).

    Companion: `gmid_tables_tour.py` (where the tables come from, what's inside).
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

    PDK, DEVICE = "sky130", "sky130_fd_pr__nfet_01v8"
    nch = Lookup(str(paths.shared_root() / "gmid" / PDK / f"{DEVICE}__tt.pkl"))
    geom = pdks.load_registry(PDK)["geometry"]
    print(nch["INFO"], "| characterized at W =", nch["W"], "µm | W bounds:", geom["min_w"], "…", geom["max_w"])
    return DEVICE, PDK, geom, nch, np, pd, pdks, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The canonical 5-step flow

    Spec: an OTA input device for **fu = 10 MHz unity-gain bandwidth into CL = 2 pF**, mid-rail output
    (VDS ≈ 0.9 V), grounded source (VSB = 0).

    1. **gm from spec** — `gm = 2π · fu · CL`
    2. **pick L** — 0.5 µm (gain/matching over raw speed; the tour notebook shows the tradeoff)
    3. **pick gm/ID** — 15 S/A (moderate inversion, the usual starting compromise)
    4. **ID = gm / (gm/ID)**
    5. **W = ID / JD** with `JD = look_up('ID_W', GM_ID, VDS, VSB, L)`
    """)
    return


@app.cell
def _(nch, np, pd):
    fu, CL = 10e6, 2e-12
    gm_id, L, VDS, VSB = 15.0, 0.5, 0.9, 0.0

    gm = 2 * np.pi * fu * CL                                              # step 1
    ID = gm / gm_id                                                       # step 4
    JD = float(nch.look_up("ID_W", GM_ID=gm_id, VDS=VDS, VSB=VSB, L=L))   # step 5
    W = ID / JD

    VGS = float(nch.look_upVGS(GM_ID=gm_id, VDS=VDS, VSB=VSB, L=L))
    Av0 = float(nch.look_up("GM_GDS", GM_ID=gm_id, VDS=VDS, VSB=VSB, L=L))
    fT  = float(nch.look_up("GM_CGG", GM_ID=gm_id, VDS=VDS, VSB=VSB, L=L)) / (2 * np.pi)

    sized = {"gm (S)": gm, "ID (A)": ID, "JD (A/µm)": JD, "W (µm)": W, "L (µm)": L,
             "VGS (V)": VGS, "gm/gds": Av0, "fT (Hz)": fT}
    pd.Series(sized).to_frame("value").map("{:.4g}".format)
    return CL, JD, L, VDS, VGS, VSB, W, fT, fu, gm, gm_id


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Sanity gates before accepting a size** (the checklist of the library skill `gmid-sizing`;
    `spicexplorer-gmid` checks them as typed gates):
    - speed margin `fT / fu ≥ 10` (quasi-static validity at fu),
    - saturation margin `VDS > VDsat ≈ 2/(gm/ID)` with headroom,
    - W inside the PDK's manufacturable bounds.
    """)
    return


@app.cell
def _(VDS, W, fT, fu, geom, gm_id):
    vdsat = 2.0 / gm_id
    w_min, w_max = float(geom["min_w"].rstrip("u")), float(geom["max_w"].rstrip("u"))
    gates = {
        f"fT/fu = {fT/fu:.0f} ≥ 10": fT / fu >= 10,
        f"VDS {VDS} > VDsat≈{vdsat:.2f} (+0.1 margin)": VDS > vdsat + 0.1,
        f"{w_min} ≤ W={W:.2f}µm ≤ {w_max}": w_min <= W <= w_max,
    }
    for g, _ok in gates.items():
        print(("PASS  " if _ok else "FAIL  ") + g)
    assert all(gates.values())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## When gm/ID is NOT the knob: the current-density (JD-first) flow

    In weak inversion the gm/ID curve plateaus (~25–30 S/A), so many densities map to nearly the same
    efficiency — gm/ID no longer pins the design. Choose **JD first**, look up the resulting gm/ID,
    then proceed as usual.
    """)
    return


@app.cell
def _(L, VDS, nch, np):
    # read gm/ID vs JD straight off the table arrays (interpolating on the monotonic region)
    li = int(np.argmin(np.abs(nch["L"] - L)))
    vi = int(np.argmin(np.abs(nch["VDS"] - VDS)))
    idd, gmv = nch["ID"][li, :, vi, 0], nch["GM"][li, :, vi, 0]
    _ok = idd > 1e-12
    jd_v, eff_v = idd[_ok] / nch["W"], gmv[_ok] / idd[_ok]

    JD_target = 5e-8                                                       # 50 nA/µm — deep weak inversion
    gm_id_wi = float(np.interp(JD_target, jd_v, eff_v))                    # jd_v is increasing in VGS
    ID_wi = 1e-6                                                           # 1 µA budget
    print(f"JD = {JD_target:.1e} A/µm → gm/ID = {gm_id_wi:.1f} S/A → "
          f"W = {ID_wi/JD_target:.1f} µm for ID = {ID_wi*1e6:.0f} µA, gm = {gm_id_wi*ID_wi*1e6:.1f} µS")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Self-loading: iterate when the device loads its own output

    When the drain capacitance `Cdd = W · CDD_W` is comparable to CL, size against `CL + Cdd` and
    iterate — converges in a few rounds.
    """)
    return


@app.cell
def _(CL, JD, L, VDS, VSB, W, fu, gm_id, nch, np):
    W_it, Cdd = W, 0.0
    for i in range(8):
        gm_i = 2 * np.pi * fu * (CL + Cdd)
        W_new = (gm_i / gm_id) / JD
        Cdd = W_new * float(nch.look_up("CDD_W", GM_ID=gm_id, VDS=VDS, VSB=VSB, L=L))
        print(f"iter {i}: W = {W_new:6.3f} µm   Cdd = {Cdd*1e15:6.2f} fF")
        if abs(W_new - W_it) < 1e-3:
            break
        W_it = W_new
    print(f"converged: W = {W_it:.3f} µm (vs {W:.3f} µm ignoring self-loading)")
    return (W_it,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Design-space sweep — the agent's default move

    When specs are intertwined (gain AND speed AND power), don't point-design: sweep gm/ID × L, build
    the tradeoff arrays, then pick the corner that meets everything with margin. (`look_up` vectorizes
    over GM_ID; loop L explicitly — pygmid keeps L scalar per call.)
    """)
    return


@app.cell
def _(VDS, VSB, fu, gm, nch, np, plt):
    gmid_v = np.linspace(5, 25, 41)
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
    for Lx in [nch["L"][0], 0.5, 1.0, 2.0]:
        JDv = np.asarray(nch.look_up("ID_W", GM_ID=gmid_v, VDS=VDS, VSB=VSB, L=Lx))
        Avv = np.asarray(nch.look_up("GM_GDS", GM_ID=gmid_v, VDS=VDS, VSB=VSB, L=Lx))
        fTv = np.asarray(nch.look_up("GM_CGG", GM_ID=gmid_v, VDS=VDS, VSB=VSB, L=Lx)) / (2 * np.pi)
        Wv = (gm / gmid_v) / JDv
        ax1.semilogy(gmid_v, Wv, label=f"L={Lx:g}")
        ax2.plot(gmid_v, Avv, label=f"L={Lx:g}")
        ax3.semilogy(gmid_v, fTv / fu, label=f"L={Lx:g}")
    ax3.axhline(10, color="r", ls=":", label="fT/fu = 10 gate")
    for ax, yl in [(ax1, "W (µm) for the spec gm"), (ax2, "intrinsic gain gm/gds"), (ax3, "fT / fu")]:
        ax.set_xlabel("gm/ID (S/A)"); ax.set_ylabel(yl); ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=7)
    plt.tight_layout()
    fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Passives: R → squares, C → area

    The compensation network needs the same treatment — the measured tt constants come from the PDK
    registry (`passives.models`, see the tour notebook).
    """)
    return


@app.cell
def _(PDK, np, pdks):
    pas = pdks.load_registry(PDK)["passives"]["models"]
    sheet = pas["sky130_fd_pr__res_high_po"]["sheet_res"]        # Ω/□
    dens = pas["sky130_fd_pr__cap_mim_m3_1"]["area_cap"]         # F/µm²

    Rz, Cc = 10e3, 1e-12                                         # a typical Miller pair
    w_r = 1.0                                                    # µm resistor width
    print(f"Rz = {Rz/1e3:.0f} kΩ @ {sheet} Ω/□ → {Rz/sheet:.1f} squares → L = {Rz/sheet*w_r:.1f} µm at W = {w_r} µm")
    print(f"Cc = {Cc*1e12:.0f} pF @ {dens*1e15:.2f} fF/µm² → {Cc/dens:.0f} µm² → {np.sqrt(Cc/dens):.1f} µm square")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Close the loop in SPICE (PDK-gated)

    The method's discipline: **always back-annotate**. Put the sized W/L at the predicted VGS into an
    ngspice `.op` on the real models and compare ID and gm against the table's prediction — a few
    percent is expected; more means a wrong table/corner, wrong VDS/VSB assumption, or a device out of
    saturation.
    """)
    return


@app.cell
def _(PDK):
    # PDK-gated cells: real simulation needs ngspice + the sky130 PDK, either on this host
    # (ngspice on PATH, the PDK's models under $PDK_ROOT; tried first) or in the EDA base image
    # (ngspice + the three PDKs).
    # Build it once in spicexplorer-platform:  docker compose --profile base build spice-base
    # (probe with a real `docker run` — `docker image inspect` can false-negative under the
    #  containerd image store)
    import shutil
    import subprocess

    def base_image_available(image: str = "spicexplorer-spice-base:local") -> bool:
        if shutil.which("docker") is None:
            return False
        return subprocess.run(["docker", "run", "--rm", image, "true"],
                              capture_output=True, timeout=120).returncode == 0

    from spicexplorer_analog_db.runner import native_pdk_available

    NATIVE_OK = native_pdk_available(PDK)  # ngspice on PATH + the PDK under $PDK_ROOT
    PDK_OK = NATIVE_OK or base_image_available()  # the image is probed only when the host lacks either
    LANE = "this host (native ngspice)" if NATIVE_OK else "the EDA base image" if PDK_OK else "none"
    print("simulation lane:", LANE, "" if PDK_OK else "→ the simulation cells below will skip (everything else runs PDK-free)")
    return NATIVE_OK, PDK_OK


@app.cell
def _(DEVICE, JD, L, NATIVE_OK, PDK, PDK_OK, VDS, VGS, W_it, gm_id, mo, pd):
    if not PDK_OK:
        print("SKIPPED — needs ngspice + the PDK on this host, or the EDA base image, to run the back-annotation check.")
    else:
        from spicexplorer_analog_db import gmid as gx
        deck = f"""** gm/ID back-annotation check (sized device at the predicted bias)
    vg g 0 {VGS:.4f}
    vd d 0 {VDS}
    vb b 0 0
    XM1 d g 0 b {DEVICE} L={L:g} W={W_it:.3f} nf=1 m=1
    .op
    .control
    set wr_vecnames
    set wr_singlescale
    run
    wrdata opcheck.txt @m.xm1.m{DEVICE}[id] @m.xm1.m{DEVICE}[gm]
    .endc
    .lib sky130.lib.spice tt
    .end
    """
        out = (gx.native_deck_runner(PDK) if NATIVE_OK else gx.base_image_deck_runner())(deck, "opcheck.txt")
        vals = out.splitlines()[1].split()
        id_sim, gm_sim = float(vals[1]), float(vals[2])
        ID_pred = JD * W_it                      # the table's prediction at the final (self-loading) W
        gm_pred = gm_id * ID_pred
        cmp = pd.DataFrame({
            "predicted (table)": [ID_pred, gm_pred, gm_id],
            "simulated (.op)": [id_sim, gm_sim, gm_sim / id_sim],
        }, index=["ID (A)", "gm (S)", "gm/ID (S/A)"])
        cmp["Δ%"] = 100 * (cmp["simulated (.op)"] / cmp["predicted (table)"] - 1)
        mo.output.append(mo.ui.table(cmp, format_mapping={"predicted (table)": "{:.4g}", "simulated (.op)": "{:.4g}", "Δ%": "{:+.1f}"}))
        assert abs(gm_sim / id_sim / gm_id - 1) < 0.05, "gm/ID off by >5% — check table/corner/bias"
        print("back-annotation agrees — the sizing holds on the real models.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What's next

    - The typed tool: `packages/spicexplorer-gmid` wraps these flows as `DeviceTable` /
      `size_for_gm` / `size_for_current_density` with the sanity gates as checks;
      its README describes the API (the plan behind it is archived in the meta-repo `doc/archive/`).
    - Its first consumer: re-sizing the analog-db cascodes (`amp_004_folded_cascode`,
      `amp_018_telescopic_cascode`) into the sky130/gf180 model envelope.
    - Methodology depth (recipes, biasing, PVT, verification tolerances): the library skill
      `gmid-sizing` (the agent kit's `.claude/skills/gmid-sizing/`) and the source textbook.
    """)
    return


if __name__ == "__main__":
    app.run()
