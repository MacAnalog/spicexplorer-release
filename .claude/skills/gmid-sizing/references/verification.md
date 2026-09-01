# SPICE verification of a gm/ID-sized design

Always close the loop. The methodology's promise is calculation-to-simulation
agreement within a few percent without tweaking; the verification step is what
proves it for a given design.

## 1. Back-annotate

Write the computed sizes and bias values into the netlist as parameters, never
hardcode. Emit a param file from the sizing script:

```
.param w1=41.7u l1=130n id1=419u
```

In this project, sizes flow into the example's `project_setup.yaml` /
netlist parameters the same way any optimizer candidate does; reuse that
plumbing instead of inventing a new injection path.

## 2. Operating-point run

Run a `.op` (or a DC sweep pinned at the intended bias) with device internal
parameters saved. ngspice control block sketch:

```
.control
op
* PSP/OSDI device parameter access; verify exact vector names with a
* single-device debug deck before scripting (names depend on model binding,
* e.g. @m.x<inst>.<model>[gm] vs @n.x<inst>.<osdi-instance>[gm])
print @m.xm1.msky[gm] @m.xm1.msky[gds] @m.xm1.msky[id] @m.xm1.msky[vgs]
.endc
```

For the IHP SG13G2 PSP models compiled via OSDI, the saveable parameter names
differ from builtin MOS levels. Mandatory first step on a new PDK: run one
single-transistor deck, `display` all vectors, and record the exact handles in
this file for reuse. This mirrors the book's debug-first advice for the table
generation flow.

## 3. Compare, with tolerances

| Quantity        | Source (calc)                  | Source (sim)        | Tolerance |
|-----------------|--------------------------------|---------------------|-----------|
| ID              | gm/(gm/ID)                     | .op device id       | 3%        |
| gm              | spec (e.g. 2*pi*fu*CL)         | .op device gm       | 3%        |
| gm/ID           | chosen                         | sim gm / sim id     | 3%        |
| VGS             | lookup_vgs                     | .op device vgs      | ~5 mV     |
| gds (or Av0)    | lookup GM_GDS                  | .op device gds      | 10%       |
| fT              | lookup GM_CGG / 2pi            | AC sim or cgg ratio | 10%       |
| fu, gain, noise | circuit-level lookup model     | AC/noise analysis   | 5-10%     |

gds and fT carry looser tolerances: both are sensitive to VDS error and layout
parasitics. ID, gm, VGS agreement is the primary pass/fail gate.

## 4. Diagnose disagreement (ordered)

1. Bias point mismatch: actual VDS/VSB in the circuit differs from the values
   used in the lookups. Read node voltages from the .op and re-run the lookups
   at the simulated bias; if agreement returns, fix the bias assumption.
2. Saturation: check VDS > ~2/(gm/ID). A device in triode invalidates the
   whole comparison.
3. Wrong table: corner/temperature of the LUT header vs simulation settings.
4. Grid violation: L or voltages outside the characterized table range
   (interpolation became extrapolation somewhere).
5. Geometry effects: W far from the characterized finger geometry. Per the
   layout-dependence appendix, parameter ratios are width-insensitive only if
   the finger width is preserved; partition W into fingers matching the LUT's
   characterization (header `W`/`NFING`), not into arbitrary finger widths.

## 5. Automation contract for agents

A verification run must produce a structured result, not prose:

```json
{
  "device": "M1", "pass": true,
  "calc": {"id": 4.19e-4, "gm": 6.28e-3, "gm_id": 15.0, "vgs": 0.468},
  "sim":  {"id": 4.23e-4, "gm": 6.31e-3, "gm_id": 14.9, "vgs": 0.470},
  "err_pct": {"id": 0.9, "gm": 0.5, "gm_id": 0.7},
  "saturation_ok": true
}
```

Fail the run on any gate violation and report the first diagnosis step that
explains it. Do not auto-tweak W or ID to force agreement; disagreement is
information about a wrong assumption, and the fix belongs upstream in the
sizing inputs.
