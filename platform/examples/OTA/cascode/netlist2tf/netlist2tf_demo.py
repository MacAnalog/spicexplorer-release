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
    # netlist2tf — symbolic transfer functions with a *validated* simplification ledger

    `spicexplorer-netlist2tf` ingests a SPICE netlist, replaces each device with a small-signal
    model, extracts the **exact** symbolic transfer function between any two ports, and — the
    differentiator — **reduces it to the designer-readable hand-form** by applying explicit,
    ordered, physically-motivated assumptions, *each one numerically validated against the exact
    TF and recorded in an audit ledger*. You don't just get `H(s)`; you get
    "`H ≈ −gm/gm₂` under these named, error-bounded assumptions".

    **How to run:** from the platform root, `uv run marimo edit examples/OTA/cascode/netlist2tf/netlist2tf_demo.py`
    (a marimo notebook, on the platform venv). Everything here is deterministic and PDK-free — no simulator needed.

    Pipeline stages (each independently callable):
    `ingest_netlist → small_signal_model → build_system → extract_tf → simplify_tf → describe_tf`,
    or the one-liner `transfer_function(...)` that composes them all.
    """)
    return


@app.cell
def _():
    import sympy as sp
    from IPython.display import Math, display

    from spicexplorer_core import project_root
    from spicexplorer_netlist2tf import (
        # one-liner + staged API
        transfer_function, from_file, from_string,
        small_signal_model, build_system, extract_tf, simplify_tf, describe_tf,
        # assumptions (the differentiator)
        transconductance_dominates, neglect_cgd, matched_pair,
        # derived analyses (P7 base set + P9 DM/CM family)
        open_loop_gain, input_impedance, output_impedance,
        common_mode_gain, cmrr, psrr, loop_gain, asymptotic_gain,
        Fidelity,
    )

    sp.init_printing()

    def show(label, latex_str):
        # `label` is LaTeX math (pass a raw string if it contains backslash commands)
        display(Math(rf"{label} \quad {latex_str}"))

    return (
        Fidelity,
        build_system,
        cmrr,
        display,
        extract_tf,
        from_file,
        input_impedance,
        loop_gain,
        matched_pair,
        neglect_cgd,
        output_impedance,
        project_root,
        show,
        small_signal_model,
        sp,
        transconductance_dominates,
        transfer_function,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Quick start — an RC low-pass, one line

    `transfer_function` takes a netlist (path, raw SPICE text, `NetlistView`, or a pre-built IR),
    an output port and an input port, and returns one Pydantic contract
    (`TransferFunctionResult`) carrying the exact TF, the simplified TF, DC gain, poles, zeros,
    the assumption ledger, and the validation report.
    """)
    return


@app.cell
def _(show, transfer_function):
    rc = transfer_function(
        "* rc\nR1 in out R\nC1 out 0 C\n.end",
        output=("out", "0"),
        input=("in", "0"),
        operating_point={"r": 1e3, "c": 159.155e-9},   # enables numeric pole/gain coordinates
    )

    show("H(s) =", rc.tf_exact_latex)
    print("DC gain :", rc.dc_gain.expr, "=", rc.dc_gain.value)
    print("pole    :", rc.poles[0].expr, f"->  f3dB = {rc.poles[0].frequency_hz:,.1f} Hz")
    print("solve   :", rc.solve_path, "| analysis:", rc.analysis)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Exact symbolic amplifier TFs

    A common-source stage at `SOME_PARASITIC` fidelity (gm + ro) gives the textbook
    `Av = −gm·(ro ∥ RL)` exactly. Raising fidelity to `FULL` adds `gmb` and the four device
    capacitances — and the Miller cap `Cgd` produces the famous right-half-plane zero at
    `s = +gm/Cgd`, straight out of the math.
    """)
    return


@app.cell
def _(Fidelity, show, sp, transfer_function):
    CS = "* common source\nM1 out in 0 0 nmos\nRL out 0 RL\n.end"

    lo = transfer_function(CS, ("out", "0"), ("in", "0"))                      # gm + ro
    hi = transfer_function(CS, ("out", "0"), ("in", "0"), level=Fidelity.FULL) # + caps + gmb

    show(r"A_v\;(\text{some-parasitic}) =", lo.tf_exact_latex)
    show(r"A_v\;(\text{full}) =", hi.tf_exact_latex)

    # the RHP zero: the numerator vanishes at s = gm/Cgd
    num = sp.fraction(hi.as_sympy_exact())[0]
    _gm, cgd, s = sp.symbols("gm_m1 cgd_m1 s")
    print("numerator at s = +gm/Cgd:", sp.simplify(num.subs(s, _gm / cgd)), " (RHP zero confirmed)")
    return (CS,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. The differentiator — simplification you can audit

    A diode-loaded common-source stage. The exact gain is
    `−gm₁·ro₁·ro₂ / (gm₂·ro₁·ro₂ + ro₁ + ro₂)`; every textbook *says* "assume `gm₂ ≫ go` and
    read `−gm₁/gm₂`" — netlist2tf makes that step **explicit, numerically arbitrated, and
    validated**:

    * the `DOMINANCE` kernel only drops a term if the operating point really supports it
      (`|dominant| ≥ 100×|dropped|`, the 40 dB floor);
    * every applied step is re-checked against the **exact** TF over 1 Hz–1 GHz (1 Hz–`f_hi`
      after an `inband(f_hi)` step); a step that breaks the 5 % error budget is **rolled back and
      flagged**;
    * the whole story lands in the ledger (`assumptions_applied`).
    """)
    return


@app.cell
def _(display, show, transconductance_dominates, transfer_function):
    import pandas as pd

    DIODE = "* diode-loaded cs\nM1 out in 0 0 nmos\nM2 out out vdd vdd pmos\n.end"
    op_diode = {"gm_m1": 1e-3, "gm_m2": 1e-3, "ro_m1": 2e5, "ro_m2": 2e5}

    res = transfer_function(DIODE, ("out", "0"), ("in", "0"),
                            assumptions=[transconductance_dominates("M2")],
                            operating_point=op_diode)

    show("H_{exact} =", res.tf_exact_latex)
    show("H_{simplified} =", res.tf_simplified_latex)

    ledger = pd.DataFrame([{
        "assumption": a.name, "kind": a.kind, "status": a.status,
        "dropped": ", ".join(a.dropped_terms), "ratio": a.numeric_ratio,
        "step error": a.relative_error,
    } for a in res.assumptions_applied])
    display(ledger)

    v = res.validation
    print(f"validated over {v.freq_hz_min:g}–{v.freq_hz_max:g} Hz:  "
          f"max rel. error = {v.max_relative_error:.2e}  ->  passed = {v.passed}")
    return (DIODE,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### …and it refuses to lie

    Same `neglect_cgd` assumption, two operating points. With a tiny overlap cap the reduction
    validates; with a large one the dropped cap shapes the in-band response, the incremental gate
    catches it, and the step is **rejected and rolled back** — the result returns to the exact TF
    rather than shipping a wrong-but-pretty formula.
    """)
    return


@app.cell
def _(CS, Fidelity, neglect_cgd, transfer_function):
    small_cgd = {"gm_m1": 1e-3, "ro_m1": 2e5, "rl": 1e4,
                 "cgs_m1": 1e-14, "cgd_m1": 1e-16, "cdb_m1": 1e-16, "csb_m1": 1e-16}
    large_cgd = small_cgd | {"cgd_m1": 1e-12}

    for tag, op_ in (("small Cgd", small_cgd), ("LARGE Cgd", large_cgd)):
        r = transfer_function(CS, ("out", "0"), ("in", "0"), level=Fidelity.FULL,
                              assumptions=[neglect_cgd("M1")], operating_point=op_)
        step = r.assumptions_applied[0]
        print(f"{tag:9s} -> {step.status:20s} step error = {step.relative_error:.3%}   "
              f"simplified == exact: {r.tf_simplified_expr == r.tf_exact_expr}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. A 5-transistor OTA core — differential input, matched pairs, Bode

    The classic diff-pair + mirror-load core. The input is a true differential pair of
    high-impedance gates (`("vinp", "vinn")`); `matched_pair` folds the mirror devices'
    symbols together (a lossless EQUALITY rewrite), shrinking the expression before anything
    is dropped.
    """)
    return


@app.cell
def _(matched_pair, show, transfer_function):
    OTA = '''* 5T OTA core (diff pair + mirror load, ideal tail)
    M1 outn vinp tail 0 nmos
    M2 outp vinn tail 0 nmos
    M3 outn outn vdd vdd pmos
    M4 outp outn vdd vdd pmos
    Itail tail 0 dc ib
    .end
    '''

    op_ota = ({f"gm_m{i}": 1e-3 for i in (1, 2, 3, 4)} | {f"ro_m{i}": 1e5 for i in (1, 2, 3, 4)})

    ota = transfer_function(OTA, ("outp", "0"), ("vinp", "vinn"),
                            assumptions=[matched_pair("M1", "M2"), matched_pair("M3", "M4")],
                            operating_point=op_ota)

    show(r"A_{dm \to se} =", ota.tf_simplified_latex)
    print("conv_type:", ota.conv_type, "| DC gain =", f"{ota.dc_gain.value:.1f}",
          f"({20 * __import__('math').log10(abs(ota.dc_gain.value)):.1f} dB)")
    print("validation passed:", ota.validation.passed)
    return OTA, op_ota


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    At `FULL` fidelity the device caps create real poles. A 4-transistor amp with the full cap set
    is past the fully-symbolic ceiling (measured in the P3 benchmark), so we use the
    **selective-numericization** lever: `subs=` numericizes everything before the determinant —
    fast — and the contract records `solve_path="selectively_numericized"` so the result never
    overstates how symbolic it is.
    """)
    return


@app.cell
def _(Fidelity, OTA, op_ota, transfer_function):
    import numpy as np
    import matplotlib.pyplot as plt
    from spicexplorer_netlist2tf.numeric import frequency_response, log_sweep

    _subs = (op_ota
            | {f"{c}_m{i}": 2e-14 for i in (1, 2, 3, 4) for c in ("cgs", "cgd", "cdb", "csb")}
            | {f"gmb_m{i}": 2e-4 for i in (1, 2, 3, 4)})

    full = transfer_function(OTA, ("outp", "0"), ("vinp", "vinn"),
                             level=Fidelity.FULL, subs=_subs, operating_point=_subs)
    print("solve_path:", full.solve_path, "| poles:",
          [f"{p.frequency_hz:,.0f} Hz" for p in full.poles if p.frequency_hz])

    freqs = log_sweep(1e3, 1e12, points_per_decade=15)
    H = frequency_response(full.as_sympy_exact(), {}, freqs)   # already numeric after subs

    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.semilogx(freqs, 20 * np.log10(np.abs(H)))
    for p in full.poles:
        if p.frequency_hz and 1e3 < p.frequency_hz < 1e12:
            ax.axvline(p.frequency_hz, ls="--", lw=0.8, color="tab:red", alpha=0.6)
    ax.set_xlabel("frequency (Hz)"); ax.set_ylabel("|H| (dB)")
    ax.set_title("5T OTA core, FULL fidelity — poles from the symbolic solve (dashed)")
    ax.grid(True, which="both", alpha=0.3)
    plt.tight_layout(); plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The real committed fixture — `ota-improved.spice` (this directory's cascode OTA)

    Now the actual IHP `sg13g2` cascode OTA netlist tracked in this repo
    (`examples/OTA/cascode/ihp-sg13g2/spice/ota-improved.spice`): 20 MOSFETs + 4 bias/measure
    V-sources, with symbolic `.param` geometry. Stage 1 ingests it into the typed IR; the rails
    classify as AC grounds; the DC bias sources become AC shorts automatically.

    One physical subtlety: the netlist's enable input `d_ena` is a *DC control pin* — at the bare
    DUT level nothing drives it, so the small-signal system is singular. Tying it to AC ground via
    `build_system(extra_grounds=...)` (the source-zeroing primitive) models exactly what the
    testbench's DC enable source does, and the system solves.
    """)
    return


@app.cell
def _(from_file, project_root):
    dut = project_root() / "examples/OTA/cascode/ihp-sg13g2/spice/ota-improved.spice"
    ir = from_file(dut, name="cascode-ota")

    print("devices:", len(ir.devices), "| nets:", len(ir.nets), "| AC grounds:", ir.ac_ground_nets)
    m1 = ir.device("XM1")
    print("XM1:", m1.kind.value, "D/G/S/B =", m1.nets, "| w =", m1.params["w"], "| l =", m1.params["l"])
    print("kept-symbolic geometry params:", len(ir.symbolic))
    return (ir,)


@app.cell
def _(Fidelity, build_system, extract_tf, ir, show, small_signal_model, sp):
    ssir = small_signal_model(ir, level=Fidelity.SOME_PARASITIC)
    print("small-signal primitives:", len(ssir.primitives),
          "| introduced symbols:", len(ssir.introduced_symbols))

    # Selective numericization: ball-park every small-signal value EXCEPT the input-pair gm.
    _subs = {n: (1e-3 if n.startswith("gm") else 2e5) for n in ssir.introduced_symbols}
    _subs.pop("gm_m1")

    system = build_system(ssir, subs=_subs, extra_grounds={"d_ena"})   # ground the DC enable pin
    raw = extract_tf(system, ("vout", "0"), ("vinp", "vinn"), numeric_subs=_subs)

    show("H(g_{m,M1}) =", sp.latex(sp.nsimplify(raw.expr, rational=False)))
    print("kept symbolic:", raw.kept_symbolic, "| solve_path:", raw.solve_path)

    import math
    _gm = sp.Symbol("gm_m1", positive=True)
    for g in (0.2e-3, 0.5e-3, 1e-3, 2e-3):
        av = float(raw.expr.subs(_gm, g))
        print(f"  gm_m1 = {g * 1e3:4.1f} mS  ->  Av = {av:8.1f}  ({20 * math.log10(abs(av)):5.1f} dB)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### …or just hand it the actual testbench

    `ota-improved_tb-ac.spice` is the real AC testbench: the DUT is an `X…` instance of the
    `ota-improved` subckt, the rails and the enable pin are driven by DC V-sources, and
    `Vin … dc V_CM ac 1` marks the input. Ingestion now **flattens** the instance (internal nets
    and refs get a `_xota` postfix, so the DUT's internal `net1` never collides with the
    testbench's `net1`), every pure-DC source becomes an AC short automatically — no
    `extra_grounds` needed — and the input port is **auto-detected from the AC source**, so the
    one-liner needs only the output. This testbench closes the loop (`vinn` is tied to `v_out`:
    a unity-gain buffer), so the closed-loop DC gain lands just under 1.
    """)
    return


@app.cell
def _(from_file, project_root, small_signal_model, transfer_function):
    tb = project_root() / "examples/OTA/cascode/ihp-sg13g2/spice/ota-improved_tb-ac.spice"

    tb_ir = from_file(tb)                              # subckt flatten is the default
    print("devices:", len(tb_ir.devices), "| e.g.", [d.ref for d in tb_ir.devices][1:5])

    tb_ssir = small_signal_model(tb_ir)
    nums = {n: (1e-3 if n.startswith("gm") else 2e5) for n in tb_ssir.introduced_symbols}
    nums |= {"cl": 50e-15}                             # the tb's load cap (.param CL=50f)

    buf = transfer_function(tb_ir, ("v_out", "0"), subs=nums, operating_point=nums)  # input: auto
    print("closed-loop DC gain:", f"{buf.dc_gain.value:.4f}", "(unity-gain buffer)")
    print("dominant pole:", [f"{p.frequency_hz:,.0f} Hz" for p in buf.poles
                             if p.frequency_hz and p.frequency_hz < 1e11])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Derived analyses — the same solve, more designer numbers

    Open-loop gain, input impedance, and output impedance are **recipes over the same MNA
    solve** (test-current injection + source-zeroing), so they return the same contract and the
    same validated-simplification machinery applies. `Z_out` of the common-source stage comes
    out as the textbook `ro ∥ RL`; the SOME_PARASITIC gate is correctly *infinite* impedance
    (a clean error suggesting FULL fidelity), and at FULL it is capacitive.
    """)
    return


@app.cell
def _(CS, Fidelity, input_impedance, output_impedance, show):
    zo = output_impedance(CS, ("out", "0"), zero_input=("in", "0"),
                          operating_point={"gm_m1": 1e-3, "ro_m1": 1e5, "rl": 1e5})
    show(r"Z_{out}(s) =", zo.tf_exact_latex)
    print("Z_out =", f"{zo.dc_gain.value:,.0f} Ω  (= ro ∥ RL = 50 kΩ)", "| analysis:", zo.analysis)

    zi = input_impedance(CS, ("in", "0"), level=Fidelity.FULL)
    show(r"Z_{in}(s)\;(\text{full}) =", zi.tf_exact_latex)

    try:
        input_impedance(CS, ("in", "0"))   # ideal gate at SOME_PARASITIC -> infinite
    except ValueError as e:
        print("SOME_PARASITIC gate:", str(e)[:90], "…")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### …and the DM/CM family rides the same solve

    `cmrr`, `psrr`, `loop_gain`, and `asymptotic_gain` are **two solves of one built system**
    (or one augmented solve split linearly in a probe's $g_m$), combined into a single symbolic
    ratio that the validated-simplification machinery then reduces as a whole. `CMRR` of a
    long-tailed pair comes out as the textbook $(1 + 2 g_m R_\text{tail})/2$; the loop gain $T(s)$
    of a shunt-feedback stage is the Blackman return ratio.
    """)
    return


@app.cell
def _(Fidelity, cmrr, loop_gain, show):
    # CMRR of a long-tailed pair (single-ended output): A_dm / A_cm.
    PAIR = '''* long-tailed pair — resistor loads, finite tail resistance
    M1 outp inp tail 0 nmos
    M2 outn inn tail 0 nmos
    RDP outp 0 rd
    RDN outn 0 rd
    RT tail 0 rt
    .end'''
    cm = cmrr(PAIR, ("outp", "0"), ("inp", "inn"), level=Fidelity.IDEAL,
              subs={"gm_m1": 1e-3, "gm_m2": 1e-3, "rd": 1e4, "rt": 5e4})
    print("CMRR =", f"{cm.dc_gain.value:.1f}", "(= (1 + 2·gm·rt)/2 = 50.5)",
          "| analysis:", cm.analysis, "| components:", list(cm.component_tfs))

    # Loop gain (Blackman return ratio) of a shunt-feedback common-source stage.
    FB = '''* shunt-feedback common-source
    M1 out ing 0 0 nmos
    Rf ing out rfb
    Rin ing 0 rin
    RD out 0 rd
    .end'''
    lg = loop_gain(FB, "M1", level=Fidelity.IDEAL)
    show(r"T(s) =", lg.tf_exact_latex)  # = gm·rin·rd / (rin + rd + rfb)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Advisory mode — ask the tool what it would assume

    With the default `assumptions="full"` nothing is dropped (the trustworthy default), but the
    engine still runs its numeric arbitration over the canonical candidate assumptions and
    returns the ones the operating point *supports* as `SUGGESTED` — so an agent (or you) can
    discover the safe reductions and re-call with them.
    """)
    return


@app.cell
def _(DIODE, op_ota, transfer_function):
    adv = transfer_function(DIODE, ("out", "0"), ("in", "0"), operating_point=op_ota)
    print("simplified == exact:", adv.tf_simplified_expr == adv.tf_exact_expr, "(nothing applied)\n")
    for a in adv.assumptions_applied:
        print(f"  {a.status:10s} {a.name:22s} would drop: {', '.join(a.dropped_terms)}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Where this goes next

    * **REST + MCP adapters** (api / orchestration layer) around this same
      `TransferFunctionResult`.
    * **Acceptance corpus** — curated example netlists (AnalogGym et al.) cross-checked against
      real `.ac` sims in the PDK container; a separate curation effort.

    Plan: `doc/archive/plan_netlist2tf.md` · tracker: `doc/archive/todo_netlist2tf.md` (meta-repo).
    """)
    return


if __name__ == "__main__":
    app.run()
