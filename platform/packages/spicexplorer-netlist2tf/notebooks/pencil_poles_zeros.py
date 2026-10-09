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
    # Poles and zeros from the MNA pencil

    `describe_tf` reports poles and zeros the textbook way: expand `H(s)` into numerator and
    denominator polynomials, hand the coefficients to `numpy.roots`. That is exact, and it is the
    right default because it also works when the coefficients are still **symbolic**.

    Its limit is the symbolic determinant behind `H(s)`, whose cost grows with the node count
    (section 3 times it). This notebook compares it with `poles_zeros`, which reads the roots
    straight off the MNA pencil, on circuits small enough to run here in a second: accuracy on
    a wide-range RC ladder, then cost, then what `poles_zeros` returns and refuses.

    **The idea in one line.** Every primitive the stamp emits is a conductance, a VCCS or `s·C`,
    so the assembled matrix is *exactly* affine in `s`:

    $$Y(s) = G + s\,C$$

    and the poles are the finite generalized eigenvalues of the pencil $(G, C)$ — a matrix
    problem. No determinant and no polynomial is ever formed.
    """)
    return


@app.cell
def _():
    from spicexplorer_netlist2tf import (
        Fidelity,
        build_system,
        describe_tf,
        extract_tf,
        from_string,
        poles_zeros,
        small_signal_model,
    )

    def system(net, level=Fidelity.FULL):
        """netlist text -> assembled MNA system"""
        return build_system(small_signal_model(from_string(net, name="demo"), level=level))

    return (
        Fidelity,
        describe_tf,
        extract_tf,
        from_string,
        poles_zeros,
        small_signal_model,
        system,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. On a small circuit, both paths agree

    A single RC. The pole must land at $-1/RC = -10^6$ rad/s.
    """)
    return


@app.cell
def _(describe_tf, extract_tf, poles_zeros, system):
    rc = system("r1 vin vout 1e3\nc1 vout 0 1e-9\n.end")

    sym = describe_tf(extract_tf(rc, ("vout", "0"), ("vin", "0")))
    pen = poles_zeros(rc, ("vout", "0"), ("vin", "0"))

    print(f"describe_tf : {sym.poles[0].value_real:+.6e} rad/s")
    print(f"poles_zeros : {pen.poles[0].value_real:+.6e} rad/s")
    print(f"exact -1/RC : {-1 / (1e3 * 1e-9):+.6e} rad/s")
    print(f"\ndc gain {pen.dc_gain:.6f}, {pen.n_states} state")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Same answer. On circuits this size `describe_tf` is the better tool — it gives you the
    symbolic form as well. Section 2 checks the two paths on coefficients that span 24 decades;
    section 3 shows where the symbolic path stops.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Coefficients that span 24 decades

    An RC ladder whose sections step the impedance up by three decades each (1 kΩ with 1 nF,
    up to 1 TΩ with 1 aF). The denominator's coefficients span 1e24.

    Before ingestion kept netlist numbers exact (audit LEAF-F06), this example showed
    `numpy.roots` returning numbers that were not roots: the coefficients had been computed in
    floating point and were wrong (4.12e27 where the exact value is 4.003002001e27). With exact
    coefficients, the test below finds both paths' roots at machine precision.
    """)
    return


@app.cell
def _(extract_tf, system):
    import numpy as np
    import sympy as sp
    from spicexplorer_netlist2tf.tf import S

    ladder = system(
        "\n".join(
            f"r{k} {'vin' if k == 0 else f'n{k}'} n{k + 1} {1e3 * 10 ** (3 * k):g}\n"
            f"c{k} n{k + 1} 0 {1e-9 / 10 ** (3 * k):g}"
            for k in range(4)
        )
        + "\n.end"
    )
    out, inp = ("n4", "0"), ("vin", "0")

    den = sp.Poly(sp.expand(sp.fraction(sp.together(extract_tf(ladder, out, inp).expr))[1]), S)
    coeffs = [complex(c) for c in den.all_coeffs()]
    mags = [abs(c) for c in coeffs if c != 0]
    print(f"denominator degree {den.degree()}, coefficients span {max(mags) / min(mags):.1e}")
    return coeffs, inp, ladder, np, out


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To judge the two answers we need a test that does not trust either of them. For a true
    root, $G + sC$ is singular, so its smallest singular value (relative to its largest) is ~0.
    That is a property of the *matrices*, independent of how the root was found.
    """)
    return


@app.cell
def _(coeffs, inp, ladder, np, out, poles_zeros):
    from spicexplorer_netlist2tf.mna import _as_pair, _augment
    from spicexplorer_netlist2tf.pencil import _affine_split

    def residual(G, C, s):
        """sigma_min / sigma_max of (G + sC) — zero exactly at a root."""
        sv = np.linalg.svd(G + s * C, compute_uv=False)
        return float(sv[-1] / sv[0])

    A, _ = _augment(ladder, _as_pair(inp, ladder), "dm")
    G, C = _affine_split(A, None)

    pen_roots = [complex(p.value_real, p.value_imag) for p in poles_zeros(ladder, out, inp).poles]
    poly_roots = np.roots(coeffs)

    # a control: generic points that are certainly NOT roots, to show where "not a root" sits
    scale = float(np.median([abs(z) for z in pen_roots]))
    floor = float(
        np.median([residual(G, C, scale * z) for z in (0.37 + 0.93j, -1.7 + 0.41j, 0.11 - 2.3j)])
    )

    print(f"{'source':<26}{'worst residual':>16}")
    print(f"{'poles_zeros (pencil)':<26}{max(residual(G, C, z) for z in pen_roots):>16.2e}")
    print(f"{'np.roots (expanded)':<26}{max(residual(G, C, z) for z in poly_roots):>16.2e}")
    print(f"{'control: not roots':<26}{floor:>16.2e}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Both paths' residuals sit about ten decades below the control, so both sets of numbers are
    roots of the system: on exact coefficients the expanded polynomial is as accurate as the
    pencil here. The 4th-order 250 Hz filter (degree-15 denominator) that first motivated the
    pencil was not re-run with exact coefficients.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. The symbolic determinant does not finish

    `extract_tf` computes a symbolic determinant. At `Fidelity.FULL` a capacitance lands on
    nearly every branch, and cost climbs steeply with node count. On a 13-node differential cell
    with 16 transistors this runs for minutes and gives no indication in advance.

    `poles_zeros` never forms the determinant, so its cost is the eigen-solve — milliseconds at
    these sizes. Below, the growth of *both* is timed on circuits small enough to finish.
    """)
    return


@app.cell
def _(describe_tf, extract_tf, inp, poles_zeros, system):
    import time

    print(f"{'nodes':>6}{'extract_tf + describe_tf':>28}{'poles_zeros':>16}")
    for n in (2, 4, 6):
        net = (
            "\n".join(
                f"r{k} {'vin' if k == 0 else f'n{k}'} n{k + 1} 1e3\nc{k} n{k + 1} 0 1e-9"
                for k in range(n)
            )
            + "\n.end"
        )
        sysm, o = system(net), (f"n{n}", "0")

        t0 = time.perf_counter()
        describe_tf(extract_tf(sysm, o, inp))
        t_sym = time.perf_counter() - t0

        t0 = time.perf_counter()
        poles_zeros(sysm, o, inp)
        t_pen = time.perf_counter() - t0

        print(f"{n:>6}{t_sym:>27.3f}s{t_pen:>15.3f}s")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. What `poles_zeros` gives back

    A `PoleZeroResult`: roots sorted by $|s|$, each carrying the $f_0$ and $Q$ a designer reads
    off directly, with repeated roots folded into `multiplicity`.

    Poles and zeros are reported **as computed, not cross-cancelled** — a root appearing in both
    lists is a genuine pole–zero cancellation of the topology, and seeing it is usually why you
    looked.

    (Every `Q` below is exactly ½ because a network of resistors and capacitors alone can only
    have real poles. The `q` field earns its keep on active circuits — a filter with gain in the
    loop is where complex pairs, and a `Q` worth reading, come from.)
    """)
    return


@app.cell
def _(poles_zeros, system):
    biquad = system(
        "r1 vin n1 1e3\ncf vin n1 1e-12\nc1 n1 0 1e-9\n"
        "r2 n1 vout 1e5\ncf2 n1 vout 1e-13\nc2 vout 0 1e-11\n.end"
    )
    res = poles_zeros(biquad, ("vout", "0"), ("vin", "0"))

    for kind, roots in (("pole", res.poles), ("zero", res.zeros)):
        for r in roots:
            q = f"{r.q:.4f}" if r.q is not None else "  -   "
            print(
                f"{kind}  f0 = {r.frequency_hz:12.3f} Hz   Q = {q}   multiplicity {r.multiplicity}"
            )
    print(f"\ndc gain {res.dc_gain:.6f}   n_states {res.n_states}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Two things it will refuse

    **An inductor.** `1/(sL)` is not affine in `s`, so the pencil split does not exist. Rather
    than silently mis-split the matrix, it says so and names the alternative.
    """)
    return


@app.cell
def _(poles_zeros, system):
    try:
        poles_zeros(system("r1 vin vout 1e3\nl1 vout 0 1e-3\n.end"), ("vout", "0"), ("vin", "0"))
    except NotImplementedError as exc:
        print(f"NotImplementedError: {exc}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Unbound symbols.** The pencil path is numeric. If the system is still symbolic, bind the
    values with `numeric_subs=` (or build the system with `subs=`) — the error names exactly what
    is missing rather than failing deeper in numpy.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. A related guard: devices that silently contribute nothing

    Not a pencil feature, but the same class of quiet wrongness. A device whose family has no
    registered model — an opaque subckt, a PDK primitive the ingest could not type — is skipped,
    so **its branches are absent from the MNA** and every `H(s)` built from that model is missing
    part of the circuit.

    Stage 2 logs a warning about this, but a log line is easy to lose in a busy run.
    `SmallSignalIR.unmodelled` makes it something you can assert on.
    """)
    return


@app.cell
def _(Fidelity, from_string, small_signal_model):
    ir = from_string(
        "xq1 vout vin 0 0 some_unknown_pdk_thing w=1u l=1u\nr1 vout 0 1e6\nc1 vout 0 1e-12\n.end",
        name="demo",
    )
    ssir = small_signal_model(ir, level=Fidelity.FULL)

    print("devices typed :", [(d.ref, d.kind.value) for d in ir.devices])
    print("unmodelled    :", ssir.unmodelled)

    # the guard worth putting in your own pipeline, shown here without aborting the notebook
    if ssir.unmodelled:
        print(f"\n-> would raise: model is missing {ssir.unmodelled}, so H(s) is incomplete")

    clean = small_signal_model(
        from_string("r1 vin vout 1e3\nc1 vout 0 1e-9\n.end", name="demo"), level=Fidelity.FULL
    )
    print("a fully-typed circuit:", clean.unmodelled, "-> nothing missing")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `XQ1` really is missing from the model, and this is what finding out early looks like —
    one field to check instead of hoping a log line was read.

    ---

    ## Summary

    | | `describe_tf` (expanded polynomial) | `poles_zeros` (MNA pencil) |
    |---|---|---|
    | symbolic coefficients | yes | no — numeric only |
    | small circuits | preferred (gives the closed form too) | agrees exactly |
    | coefficients spanning 1e24 (exact) | roots at machine precision | roots at machine precision |
    | many nodes at `Fidelity.FULL` | determinant may not finish | eigen-solve, milliseconds |
    | inductors | supported | refused, explicitly |

    Reach for `poles_zeros` when the symbolic determinant will not finish, and for
    `describe_tf` when you want the expression a human will read.
    """)
    return


if __name__ == "__main__":
    app.run()
