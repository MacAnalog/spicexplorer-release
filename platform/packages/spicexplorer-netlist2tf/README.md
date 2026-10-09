# spicexplorer-netlist2tf

A SpiceXplorer **leaf tool**: ingest a circuit netlist, replace each device with a small-signal
model, extract the **exact** symbolic transfer function between any two ports, and reduce it to the
compact, designer-readable hand-form by applying explicit, ordered, physically-motivated
assumptions — **each one individually recorded and numerically validated against the exact TF.**

That last stage is the reason the tool exists: lcapy and SLiCAP can build and normalize a symbolic
TF, but neither carries a *typed assumption with provenance and an error gate*. netlist2tf gives you
not just `H(s)`, but "`H(s) ≈ −gm·ro …` under these three named, error-bounded assumptions."

Depends on `spicexplorer-core` + `sympy` + `pydantic` + `numpy` **only** — never a peer tool, never
lcapy/SLiCAP at runtime. See the meta-repo `doc/archive/plan_netlist2tf.md` (architecture, locked decisions)
and `doc/archive/todo_netlist2tf.md` (phases).

## Status

**Shipped** — all phases are merged (P0–P9, incl. the post-R1 DM/CM family: CMRR / PSRR /
loop-gain). Known limits, each reported rather than hidden:

- `dominant_pole()` (POLE_SEPARATION) factors a 2nd-order denominator only; on any other order
  the step is a NO_OP. The factored form repeats the denominator's `s⁰` and `s¹` coefficients,
  so it reads more easily than the exact TF but is not shorter. The step is arbitrated like
  DOMINANCE: when `c1²/(c0·c2) < ratio_floor` at the operating point (a pole spacing under ~98x at
  the default floor of 100), or with a NaN coefficient, it is `REJECTED_NUMERICS`; an applied step
  records the spacing in `numeric_ratio`.
- Validation runs at one operating point over 1 Hz–1 GHz; there is no multi-corner sweep. An
  applied `inband(f_hi)` (BAND_LIMIT) step narrows the sweep to 1 Hz–`f_hi` for itself, for every
  later step and for the final gate, and `validation.freq_hz_max` records the top of the band
  checked. Above `f_hi` the simplified TF is not checked.
- BJTs, diodes and the controlled sources other than a linear `G` card (`E`/`F`/`H`, and a
  behavioural, `poly`, `table` or `m=` form of `G`) have no small-signal model. They are left out
  of the MNA and listed in `unmodelled` on the result.
- The symbolic solve of the analog-db amplifier benches still does not finish past the 5T OTA
  (9 unknowns and up time out at 60 s; `results/corpus_sweep.md`). With every symbol bound
  (`subs=`) the same benches solve in about a second, and `poles_zeros` is the numeric path for
  a bench without an inductor.
- `operating_point_from` is checked live against ngspice with the IHP PSP devices; for Spectre
  only its key shape is tested, so a Spectre model whose parameter names differ from the table
  below leaves that role in `unmapped`.

Phase-by-phase (`doc/archive/todo_netlist2tf.md`):

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
  POLE_SEPARATION) in a fixed phase order, DOMINANCE and POLE_SEPARATION steps numerically arbitrated, each step **validated against
  the exact TF** (a step that breaks tolerance is rolled back + flagged; a failing final gate returns
  the exact TF marked UNREDUCED). Every step is recorded in the audit ledger.
- **P6 — end-to-end + R1 bar** ✅ — `transfer_function(source, output, input, ...)` composes S1→S5
  into the one contract; deterministic tracked-fixture tests; a `slow` ngspice `.ac` cross-check
  (RC verified PDK-free; the OD-8 OTA acceptance runs only where the PDK is installed: the
  committed IHP 5T OTA bench, opened into an open loop and solved at FULL fidelity from ngspice's
  own PSP operating point mapped by `operating_point_from`, matches the simulator's DC gain to
  6e-5 dB, its −3 dB point to 0.3 % and its UGF to 1.8 %; re-run live 2026-10-05).
- **P7 — derived analyses** ✅ — `open_loop_gain` / `input_impedance` / `output_impedance` are recipes
  over the same MNA solve (test-current injection + source-zeroing), each returning the standard
  contract with an `analysis` tag, so the simplification differentiator carries over for free.
  (PSRR / CMRR / loop-gain ride the post-R1 DM/CM engine.) `transimpedance(system, out, inject)`
  is the same solve driven by a **current** forced across a node pair — the `Z_T` a per-device
  noise or distortion budget needs, which a voltage-ratio `extract_tf` cannot express.
- **P8 — testbench ingestion** ✅ — *actual* netlists end to end: ingestion **flattens** resolvable
  `X…` subckt instances (internal nets/refs get a `_<inst>` postfix; `keep_opaque=`/`flatten=False`
  opt out), and the input port is **auto-detected from the testbench's AC source** when `input` is
  omitted (`detect_ac_input`: the bench's one AC source, or a `±a` DM pair on one reference net,
  `Vinp vinp vcm ac 0.5` / `Vinn vinn vcm ac -0.5` → `("vinp", "vinn")`). The committed `ota-improved_tb-ac.spice` (unity-gain buffer around
  the 20-T cascode OTA) solves with no manual `extra_grounds` and no explicit ports.
- **The numeric pencil path** ✅ — `poles_zeros(system, out, in)` reads the poles and zeros
  straight off the MNA pencil instead of rooting an expanded polynomial. `describe_tf` remains
  the default (it is exact, and it works symbolically), but on circuits that are merely
  medium-sized its symbolic determinant may not finish. Since every primitive stamps a
  conductance, a VCCS or `s·C`, `Y(s) = G + s·C` **exactly**, so the poles are the finite
  generalized eigenvalues of `(G, C)` and no determinant is formed. Rooting the expanded
  coefficients is not the weak point once ingestion keeps them exact: on a 4-section RC ladder
  whose coefficients span 1e24, `numpy.roots` finds roots with a residual of 1.75e-22 and the
  pencil 2.79e-22 (the pencil notebook, section 2). numpy-only (shift-and-invert, no scipy);
  checked against a QZ reference on a 13-node differential filter to 3.2e-14. Returns the
  Pydantic `PoleZeroResult`; refuses inductors (`1/(sL)` is not affine in `s`) with a message
  that says so.
- **Dropped devices are inspectable** ✅ — `SmallSignalIR.unmodelled` lists the refs no
  registered model could expand. Those branches are absent from the MNA, so an `H(s)` built
  over them is silently missing part of the circuit; assert on the field rather than scraping
  the (long-standing) Stage-2 log warning.
- **A singular system names its nets** ✅ — before its symbolic determinant, `extract_tf` checks
  the driven system with `mna.check_solvable`: an exact rank at random values of the symbols,
  5 ms on a 26-node amplifier bench. A singular system raises `SingularSystemError` (a
  `ValueError`) with the nets in `.nets`: a net only MOS drains meet has no conductance at
  `Fidelity.IDEAL`, and a net only MOS gates meet has none below `Fidelity.FULL`.
- **analog-db corpus sweep** ✅ — `scripts/corpus_sweep.py` runs `transfer_function` over every
  analog-db `ac_open_loop` bench under a time limit and writes one status row per deck to
  `results/corpus_sweep.{json,md}`; `--subs` adds a numeric column, the same solve with every
  symbol bound to the deck's numeric `.param` values and otherwise `simplify._coarse_op`'s
  generic operating point (its poles are those of that generic bias, not of the design).
  `tests/test_n2tf_corpus_ingest.py` checks, without the symbolic solve, that every bench on
  every PDK models every device, names its own input and builds a solvable system.
- **`G` cards (VCCS)** ✅ — a linear `G n+ n- nc+ nc- value` card ingests as `DeviceKind.VCCS`
  (the value sympified like any other, `{gm_val}` → `gm_val`) and models as one `VCCS`
  primitive, so the CMFB servo of the fully differential benches is in their `H(s)`.
- **Numeric determinant** ✅ — a matrix whose only symbol is `s` (every device value bound) is
  solved over sympy's polynomial domain (`DomainMatrix`) instead of Berkowitz over generic
  expressions: the same exact rational function, 0.06 s on a 26-unknown bench that ran past
  300 s before.
- **Simulator operating point → symbols** ✅ — `operating_point_from(result, circuit)` maps an
  ngspice `.op` result or a Spectre oppoint dict onto the symbols the model minted (below).

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
from spicexplorer_netlist2tf import (
    from_string,
    small_signal_model,
    build_system,
    extract_tf,
    simplify_tf,
    transconductance_dominates,
)

ir = from_string("* diode-loaded CS\nM1 out in 0 0 nmos\nM2 out out vdd vdd pmos\n.end")
raw = extract_tf(build_system(small_signal_model(ir)), ("out", "0"), ("in", "0"))
res = simplify_tf(
    raw,
    transconductance_dominates("M2"),
    operating_point={"gm_m1": 1e-3, "gm_m2": 1e-3, "ro_m1": 2e5, "ro_m2": 2e5},
)
res.expr  # -gm_m1/gm_m2   — the textbook hand-form
res.validation.passed  # True — validated against the exact TF over 1 Hz–1 GHz
[(r.name, r.status, r.dropped_terms) for r in res.ledger]  # the auditable assumption ledger
```

```python
from spicexplorer_netlist2tf import (
    from_string,
    small_signal_model,
    build_system,
    extract_tf,
    Fidelity,
)

ir = from_string("* cs\nM1 out in 0 0 nmos\nRL out 0 RL\n.end")
raw = extract_tf(
    build_system(small_signal_model(ir, level=Fidelity.SOME_PARASITIC)), ("out", "0"), ("in", "0")
)
raw.expr  # -gm_m1*rl*ro_m1/(rl + ro_m1)   — exact Av = -gm·(ro∥RL)
```

### A simulator operating point

`transfer_function(..., operating_point=...)` and `build_system(..., subs=...)` want values keyed
by the symbols the model mints: `gm_m1`, `ro_m1`, and for a device flattened out of a subckt a
name carrying the instance (`XM1` in `xota` → `gm_m1_xota`). `operating_point_from` builds that
dict from what the simulator reports, reading the names from the model's own symbol table:

```python
from spicexplorer_netlist2tf import (
    Fidelity,
    build_system,
    from_file,
    operating_point_from,
    poles_zeros,
    small_signal_model,
)

ir = from_file("ota_open_loop.spice")
ssir = small_signal_model(ir, level=Fidelity.FULL)
# or read_oppoint_info(run_dir) from Spectre
values, unmapped = operating_point_from(ngspice_op, ssir)
assert not unmapped  # nothing is defaulted
pz = poles_zeros(
    build_system(ssir, subs=values), ("v_out", "0"), ("v_in", "0"), numeric_subs=values
)
```

- **Keys:** ngspice device vectors (`@m1[gm]`, `@m.xota.m1[gds]`, `@n.xota.xm1.nsg13_lv_nmos[gm]`
  through a PDK's subckt wrapper) or Spectre's `<instance path>:<param>` (`xota.xm1:gm`,
  `xota.xm1.m0:gm`), case-insensitive; any other key is ignored.
- **Roles:** `gm` ← `gm`; `ro` ← `1/gds` (a non-positive `gds` stays unmapped); `gmb` ← `gmb`
  or `gmbs`; `cgs` ← `cgs + cgsol`, `cgd` ← `cgd + cgdol` (PSP's intrinsic caps exclude the
  overlap); `cdb` ← `cjd` or `capbd`, `csb` ← `cjs` or `capbs` (junctions, never PSP's
  trans-capacitances `cdb`/`csb`).
- **Deck parameters:** a symbol that is a numeric global `.param` (`CL`) takes the deck's value;
  `params=False` turns that off.
- **Returns** `(values, unmapped)`: every symbol it filled, and the sorted names of the model's
  free symbols it could not. The OD-8 acceptance test uses it as its only mapping.

## Quickstart

```python
from spicexplorer_core.spice_engine import NetlistView
from spicexplorer_netlist2tf import from_file, ingest_netlist

# A flat DUT netlist (paths here are relative to the platform repo root):
ir = from_file("examples/OTA/cascode/ihp-sg13g2/spice/ota-improved.spice")
ir.device("XM1").kind  # DeviceKind.NMOS
ir.device("XM1").params["w"]  # symbolic geometry: Symbol('x_dut_m1m2_w')
ir.ac_ground_nets  # ('vdd', 'vss') — both rails are AC grounds

# Or step into a subckt definition and ingest that level:
view = NetlistView.from_file("ota_tb.spice").get_subcircuit_named("ota")
ir = ingest_netlist(view, name="ota", ports={"in": ("vinp", "vinn"), "out": ("vout", "0")})

ir.to_dict()  # round-trippable JSON front-end (Circuit2TF.from_dict)
```

## Notebooks

Each is a marimo notebook: open it with
`uv run marimo edit packages/spicexplorer-netlist2tf/notebooks/<name>.py`, or run all its cells
from that folder with `uv run python <name>.py`. Neither needs ngspice or a PDK.

[`notebooks/netlist2tf_quickstart.py`](notebooks/netlist2tf_quickstart.py) — an
end-to-end walkthrough: ingest a netlist → small-signal model → exact `H(s)` → the
describe stage (DC gain / poles / zeros), including the differential/common-mode family
(CMRR / PSRR / loop-gain).

[`notebooks/pencil_poles_zeros.py`](notebooks/pencil_poles_zeros.py) — when the
symbolic path stops being the right tool: a residual test of both paths' roots on an RC ladder
whose coefficients span 1e24 (both are roots), the cost of the symbolic determinant against the
pencil's as the node count grows, and the `unmodelled` guard.

## Tests

```bash
uv run pytest packages/spicexplorer-netlist2tf/tests -v
```
