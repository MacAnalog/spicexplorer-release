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
    # spicexplorer-netlist2tf quickstart

    **Netlist in → symbolic transfer function out**, with simplification you can audit: every
    textbook-style reduction is a declared assumption, numerically validated against the exact
    solve, and rolled back if it breaks tolerance. This is the concise tour; the deep walkthrough
    is `examples/OTA/cascode/netlist2tf/netlist2tf_demo.py`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## One line: an RC low-pass
    """)
    return


@app.cell
def _():
    from spicexplorer_netlist2tf import transfer_function

    res = transfer_function(
        "* rc\nV1 in 0 dc 0 ac 1\nR1 in out 1k\nC1 out 0 100p\n.end",
        output=("out", "0"),
        input=("in", "0"),
    )
    print("H(s) =", res.tf_exact_expr)
    print("pole:", res.poles[0].expr, f"→ {res.poles[0].frequency_hz / 1e6:.2f} MHz")  # pyright: ignore[reportOptionalOperand] -- the RC values are numeric, so the pole frequency is set
    return (transfer_function,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The signature move: simplify to the hand-form, audited

    A diode-loaded common-source stage. The exact TF is messy; asserting *gm₂ dominates its own
    ro* collapses it to the textbook −gm₁/gm₂ — and the **ledger** records exactly what was
    dropped, at what numeric ratio, validated against the exact TF.
    """)
    return


@app.cell
def _():
    from spicexplorer_netlist2tf import (
        build_system,
        extract_tf,
        from_string,
        simplify_tf,
        small_signal_model,
        transconductance_dominates,
    )

    ir = from_string("* diode-loaded CS\nM1 out in 0 0 nmos\nM2 out out vdd vdd pmos\n.end")
    raw = extract_tf(build_system(small_signal_model(ir)), ("out", "0"), ("in", "0"))
    res_simplified = simplify_tf(
        raw,
        transconductance_dominates("M2"),
        operating_point={"gm_m1": 1e-3, "gm_m2": 1e-3, "ro_m1": 2e5, "ro_m2": 2e5},
    )
    print("exact     :", raw.expr)
    print("simplified:", res_simplified.expr)
    print("validated :", res_simplified.validation.passed)  # pyright: ignore[reportOptionalMemberAccess] -- an operating_point is given, so simplify_tf validates
    for step in res_simplified.ledger:
        print(f"  ledger: {step.name} → {step.status}, dropped {step.dropped_terms}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Numbers + Bode — the same result, numerically parameterized

    Passing an `operating_point` unlocks numeric DC gain, pole/zero coordinates, and a
    Bode-able callable.
    """)
    return


@app.cell
def _(transfer_function):
    import matplotlib.pyplot as plt
    import numpy as np
    from spicexplorer_netlist2tf.numeric import frequency_response, log_sweep

    op = {"gm_m1": 1e-3, "ro_m1": 2e5, "gm_m2": 1e-3, "ro_m2": 2e5}
    cs = transfer_function(
        "* CS with load cap\nM1 out in 0 0 nmos\nM2 out out vdd vdd pmos\nCL out 0 1p\n.end",
        output=("out", "0"),
        input=("in", "0"),
        operating_point=op,
    )
    print(f"DC gain = {cs.dc_gain.value:.3f}  ({cs.dc_gain.expr})")
    for p in cs.poles:
        print(f"pole at {p.frequency_hz / 1e6:.1f} MHz   ({p.expr})")

    f = log_sweep(1e3, 1e10, points_per_decade=20)
    H = frequency_response(cs.as_sympy_exact(), op, f)
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.semilogx(f, 20 * np.log10(np.abs(H)))
    ax.set_xlabel("Hz")
    ax.set_ylabel("|H| dB")
    ax.grid(alpha=0.3, which="both")
    plt.tight_layout()
    fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Derived analyses — the same solve, different questions

    `open_loop_gain`, `input_impedance`, `output_impedance`, and the DM/CM family
    (`common_mode_gain`, `cmrr`, `psrr`, `loop_gain`, `asymptotic_gain`) all return the same
    `TransferFunctionResult` contract.
    """)
    return


@app.cell
def _():
    from spicexplorer_netlist2tf import output_impedance

    zout = output_impedance(
        "* diode-loaded CS\nM1 out in 0 0 nmos\nM2 out out vdd vdd pmos\n.end",
        port=("out", "0"),
        zero_input=("in", "0"),
    )
    print("Z_out =", zout.tf_exact_expr, "   (analysis:", zout.analysis + ")")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Real testbenches ingest directly

    A full AC testbench (DUT as a subckt instance, an `ac 1` stimulus) flattens automatically;
    `input=None` auto-detects the drive from the AC source.
    """)
    return


@app.cell
def _(mo, transfer_function):
    tb = transfer_function(
        mo.notebook_dir() / "../tests/fixtures/ota-5t_tb-ac.spice",
        output=("v_out", "0"),
        input=None,  # auto-detect from `Vin … ac 1`
    )
    print("analysis:", tb.analysis, "| solved symbols:", len(tb.tf_exact_expr), "chars of exact TF")
    print("DC gain (symbolic):", tb.dc_gain.expr[:90], "…")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Where to go next

    - The **full demo** (`examples/OTA/cascode/netlist2tf/netlist2tf_demo.py`): 5T OTA with
      matched pairs, selective numericization, CMRR/PSRR/loop-gain, advisory mode.
    - It cross-checks the **analog-db** sims (the symbolic-vs-sim gate in `analog-db run --crosscheck`).
    - The contract (`TransferFunctionResult`) is the seam future REST/MCP surfaces wrap.
    """)
    return


if __name__ == "__main__":
    app.run()
