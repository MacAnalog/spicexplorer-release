# spicexplorer-netlist2tf

A SpiceXplorer **leaf tool**: ingest a circuit netlist, replace each device with a small-signal
model, extract the **exact** symbolic transfer function between any two ports, and reduce it to the
compact, designer-readable hand-form by applying explicit, ordered, physically-motivated
assumptions — **each one individually recorded and numerically validated against the exact TF.**

That last stage is the reason the tool exists: lcapy and SLiCAP can build and normalize a symbolic
TF, but neither carries a *typed assumption with provenance and an error gate*. netlist2tf gives you
not just `H(s)`, but "`H(s) ≈ −gm·ro …` under these three named, error-bounded assumptions."

Depends on `spicexplorer-core` + `sympy` + `pydantic` + `numpy` **only** — never a peer tool, never
lcapy/SLiCAP at runtime. See the meta-repo `doc/plan_netlist2tf.md` (architecture, locked decisions)
and `doc/todo_netlist2tf.md` (phases).

## Status

**Shipped** — the tool is complete: all phases done & merged (P0–P9, incl. the post-R1 DM/CM
family: CMRR / PSRR / loop-gain). Phase-by-phase (`doc/todo_netlist2tf.md`):

- **P1 — ingestion + the one IR** ✅ — `ingest_netlist` / `from_file` / `from_string` map a
  `NetlistView` into the typed `Circuit2TF` (typed devices, role-classified nets, sympified params,
  round-trippable JSON).
- **P2 — small-signal models + registry** ✅ — `small_signal_model(ir, level)` replaces each device
  with stampable primitives (`VCCS`/`Conductance`/`Capacitor`/…) at a fidelity (`IDEAL`/
  `SOME_PARASITIC`/`FULL`); the MOSFET hybrid-pi is data, the ladder is primitive-selection, and
  `register_model` adds a device family without touching the MNA core.
- **P3 — MNA build + symbolic solve** ✅ — `build_system(ssir)` stamps the primitives into one nodal
  admittance matrix (AC grounds + DC-source shorts merged via union-find); `extract_tf(system, out, in)`
  augments a unit excitation at the port, solves by Cramer's rule, and returns the **exact** canonical
  `H(s)` (single-ended or differential), with a selective-numericization `subs` knob and a `solve_path`
  record. Verified against hand-derived RC / common-source / Miller-zero forms.
- **P4 — output forms + the single contract** ✅ — `describe_tf(raw, operating_point=)` parameterizes
  `H(s)` into DC gain / poles / zeros / Q / GBW / LaTeX inside the one Pydantic `TransferFunctionResult`
  (agent-structured fields + lazy designer `.as_sympy()`/`.latex` views); a numpy-only lambdify-at-jω
  helper (`numeric.frequency_response`) is the backbone for validation.
- **P5 — the simplification differentiator** ✅ — `simplify_tf(raw, assumptions, operating_point=)`
  reduces the exact `H(s)` by typed `Assumption`s (DOMINANCE / SMALLNESS / EQUALITY / BAND_LIMIT /
  POLE_SEPARATION) in a fixed phase order, each step numerically arbitrated and **validated against
  the exact TF** (a step that breaks tolerance is rolled back + flagged; a failing final gate returns
  the exact TF marked UNREDUCED). Every step is recorded in the audit ledger.
- **P6 — end-to-end + R1 bar** ✅ — `transfer_function(source, output, input, ...)` composes S1→S5
  into the one contract; deterministic tracked-fixture tests; a `slow` ngspice `.ac` cross-check
  (RC verified PDK-free; AnalogGym amplifier check PDK-gated, runs in the container).
- **P7 — derived analyses** ✅ — `open_loop_gain` / `input_impedance` / `output_impedance` are recipes
  over the same MNA solve (test-current injection + source-zeroing), each returning the standard
  contract with an `analysis` tag, so the simplification differentiator carries over for free.
  (PSRR / CMRR / loop-gain ride the post-R1 DM/CM engine.) `transimpedance(system, out, inject)`
  is the same solve driven by a **current** forced across a node pair — the `Z_T` a per-device
  noise or distortion budget needs, which a voltage-ratio `extract_tf` cannot express.
- **P8 — testbench ingestion** ✅ — *actual* netlists end to end: ingestion **flattens** resolvable
  `X…` subckt instances (internal nets/refs get a `_<inst>` postfix; `keep_opaque=`/`flatten=False`
  opt out), and the input port is **auto-detected from the testbench's AC source** when `input` is
  omitted (`detect_ac_input`). The committed `ota-improved_tb-ac.spice` (unity-gain buffer around
  the 20-T cascode OTA) solves with no manual `extra_grounds` and no explicit ports.
- **The numeric pencil path** ✅ — `poles_zeros(system, out, in)` reads the poles and zeros
  straight off the MNA pencil instead of rooting an expanded polynomial. `describe_tf` remains
  the default (it is exact, and it works symbolically), but its `numpy.roots` path degrades
  quietly on circuits that are merely medium-sized: the symbolic determinant may not finish,
  and a denominator whose coefficients span tens of decades loses its low-frequency roots to
  floating-point cancellation. Since every primitive stamps a conductance, a VCCS or `s·C`,
  `Y(s) = G + s·C` **exactly**, so the poles are the finite generalized eigenvalues of
  `(G, C)` — no polynomial, nothing to cancel. numpy-only (shift-and-invert, no scipy);
  checked against a QZ reference on a 13-node differential filter to 3.2e-14. Returns the
  Pydantic `PoleZeroResult`; refuses inductors (`1/(sL)` is not affine in `s`) with a message
  that says so.
- **Dropped devices are inspectable** ✅ — `SmallSignalIR.unmodelled` lists the refs no
  registered model could expand. Those branches are absent from the MNA, so an `H(s)` built
  over them is silently missing part of the circuit; assert on the field rather than scraping
  the (long-standing) Stage-2 log warning.

### One-liner

```python
from spicexplorer_netlist2tf import transfer_function

res = transfer_function(
    "ota.spice",                    # path | SPICE text | NetlistView | Circuit2TF
    output=("vout", "0"),
    input=("vinp", "vinn"),         # diff input inferred from the pair
    assumptions="ideal",            # opt into the validated reduction (default "full" = exact)
    operating_point={"gm_m1": 1e-3, "ro_m1": 1e5, ...},   # enables the validation gate + numbers
)
res.tf_simplified_expr            # the readable hand-form
res.dc_gain.value, res.poles      # numeric parameterization
res.validation.passed             # validated against the exact TF
```

```python
from spicexplorer_netlist2tf import (from_string, small_signal_model, build_system, extract_tf,
                                      simplify_tf, transconductance_dominates)
ir = from_string("* diode-loaded CS\nM1 out in 0 0 nmos\nM2 out out vdd vdd pmos\n.end")
raw = extract_tf(build_system(small_signal_model(ir)), ("out","0"), ("in","0"))
res = simplify_tf(raw, transconductance_dominates("M2"),
                  operating_point={"gm_m1":1e-3,"gm_m2":1e-3,"ro_m1":2e5,"ro_m2":2e5})
res.expr                # -gm_m1/gm_m2   — the textbook hand-form
res.validation.passed   # True — validated against the exact TF over 1 Hz–1 GHz
[(r.name, r.status, r.dropped_terms) for r in res.ledger]   # the auditable assumption ledger
```

```python
from spicexplorer_netlist2tf import from_string, small_signal_model, build_system, extract_tf, Fidelity
ir = from_string("* cs\nM1 out in 0 0 nmos\nRL out 0 RL\n.end")
raw = extract_tf(build_system(small_signal_model(ir, level=Fidelity.SOME_PARASITIC)), ("out","0"), ("in","0"))
raw.expr           # -gm_m1*rl*ro_m1/(rl + ro_m1)   — exact Av = -gm·(ro∥RL)
```

## Quickstart

```python
from spicexplorer_core.spice_engine import NetlistView
from spicexplorer_netlist2tf import from_file, ingest_netlist

# A flat DUT netlist (paths here are relative to the platform repo root):
ir = from_file("examples/OTA/cascode/ihp-sg13g2/spice/ota-improved.spice")
ir.device("XM1").kind            # DeviceKind.NMOS
ir.device("XM1").params["w"]     # symbolic geometry: Symbol('x_dut_m1m2_w')
ir.ac_ground_nets                # ('vdd', 'vss') — both rails are AC grounds

# Or step into a subckt definition and ingest that level:
view = NetlistView.from_file("ota_tb.spice").get_subcircuit_named("ota")
ir = ingest_netlist(view, name="ota", ports={"in": ("vinp", "vinn"), "out": ("vout", "0")})

ir.to_dict()                     # round-trippable JSON front-end (Circuit2TF.from_dict)
```

## Notebooks

[`notebooks/netlist2tf_quickstart.ipynb`](notebooks/netlist2tf_quickstart.ipynb) — an
executed, end-to-end walkthrough: ingest a netlist → small-signal model → exact `H(s)` → the
describe stage (DC gain / poles / zeros), including the differential/common-mode family
(CMRR / PSRR / loop-gain).

[`notebooks/pencil_poles_zeros.ipynb`](notebooks/pencil_poles_zeros.ipynb) — when the
symbolic path stops being the right tool: the two ways `describe_tf`'s expanded-coefficient
rooting degrades, the same circuits solved with `poles_zeros`, a residual test proving the
pencil's roots really are roots, and the `unmodelled` guard.

## Tests

```bash
uv run pytest packages/spicexplorer-netlist2tf/tests -v
```
