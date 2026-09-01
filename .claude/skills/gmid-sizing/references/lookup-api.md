# look_up / look_upVGS API reference

The lookup layer is `pygmid.Lookup` — `Lookup` is a class; `look_up` and
`look_upVGS` are **instance methods** on it (the aliases `lookup` / `lookupVGS`
also exist, still as methods, not free functions). It is the runtime
implementation of the book's `lookup.m` / `lookupVGS.m` (Appendix 2). For typed,
fail-loud sizing prefer the platform wrapper `spicexplorer_gmid.DeviceTable`
(`.load` / `.look_up` / `.at` / `.sweep`), which carries the same semantics over
the same `.pkl` tables. Load a table and bind it to `nch` / `pch`:

```python
from pygmid import Lookup
nch = Lookup('…/analog-db/_shared/gmid/sky130/sky130_fd_pr__nfet_01v8__tt.pkl')
```

The table is a dict-like structure with axis vectors `L`, `VGS`, `VDS`, `VSB`
(all monotonic, microns for L, volts otherwise) and 4-D arrays indexed
`[L, VGS, VDS, VSB]` for each stored parameter:

```
ID VT GM GMB GDS CGG CGS CGD CGB CDD CSS STH SFL
```

Header fields: `INFO`, `CORNER`, `TEMP`, `NFING`, `W` (characterization width,
microns). All ratios with `_W` in the name are per-micron of width.

## nch.look_up(outvar, **kwargs): three usage modes

**Mode 1, plain parameter at a bias point.**
`outvar` is a stored parameter name.
```python
nch.look_up('ID', VGS=0.5, VDS=0.8, L=0.13, VSB=0.1)
```

**Mode 2, ratio of two parameters at a bias point.**
`outvar` is `'A_B'`, computed as A/B after interpolating each.
```python
nch.look_up('GM_ID', VGS=0.5, VDS=0.8, L=0.13)   # gm/ID
nch.look_up('GM_CGG', ...)                        # omega_T = 2*pi*fT
nch.look_up('GM_GDS', ...)                        # intrinsic gain
nch.look_up('ID_W',   ...)                        # current density JD (A/um)
nch.look_up('CDD_W',  ...)                        # drain cap per width
```

**Mode 3, cross-lookup of one ratio against another.**
Pass the input ratio as a keyword. The function evaluates both ratios along the
full VGS grid at the given (L, VDS, VSB) and intersects.
```python
nch.look_up('GM_CGG', GM_ID=np.arange(5, 20.1, 0.1))
nch.look_up('ID_W',  GM_ID=15, VDS=0.6, L=0.13)
```

### Defaults when an axis is omitted (modes 1-3 and look_upVGS)

```
L   = min(data L vector)        # minimum characterized length
VGS = full VGS grid vector
VDS = max(VDS grid) / 2         # roughly VDD/2
VSB = 0
```
These defaults are convenient for exploration plots and dangerous for final
sizing. Always pass explicit values in the final computation.

### Interpolation rules

- All grid interpolation is multilinear (linear in every dimension). Higher
  order methods need continuous derivatives across all dimensions, which device
  tables do not guarantee.
- Only the final 1-D inversion in mode 3 (and in look_upVGS) uses pchip by
  default; override with `method='linear'`.
- Vector inputs broadcast; with two vector inputs the result is 2-D. To get a
  locus like VGS = VDS, take the diagonal of the 2-D result.

### Non-monotonicity handling (mode 3)

Ratio-vs-VGS curves can be non-monotonic, giving multiple intersections:

- `GM_ID` as X-variable: the curve has a spurious rise at very low VGS from
  second-order artifacts. The implementation keeps only points to the right of
  the GM_ID maximum (the weak-inversion branch artifact is discarded).
- `GM_CGG` / `GM_CGS` as X-variable: mobility degradation makes fT fall at
  high VGS. The implementation keeps only points to the left of the maximum.
- Any other ratio as X-variable: monotonicity is merely checked. On failure
  ("multiple curve intersections"), restrict the search range yourself:
  ```python
  nch.look_up('ID_W', GM_GDS=10, VGS=nch['VGS'][10:])
  ```

### Failure modes

- Requested ratio outside table range: warning + NaN (e.g. `GM_ID=50`).
  Suppress repeated warnings in loops with `warning=False`, but never ignore
  NaNs in results.
- Requests outside the (L, VGS, VDS, VSB) grid: do not extrapolate. Treat as
  an error and either re-grid the LUT or change the operating point.

## nch.look_upVGS(**kwargs): invert for VGS

Finds the VGS that yields a target inversion level or current density.

**Mode 1, source potential known.** Inputs: `GM_ID` (or `ID_W`) plus
`VDS`, `VSB`, `L`.
```python
nch.look_upVGS(GM_ID=10, VDS=0.6, VSB=0.1, L=0.13)
nch.look_upVGS(ID_W=1e-4, VDS=0.6, VSB=0.1, L=0.13)
```

**Mode 2, source floating (tail node of a diff pair, inner node of a cascode
stack).** Supply bulk-referenced `VDB` and `VGB` instead of VDS/VSB:
```python
nch.look_upVGS(GM_ID=10, VDB=0.6, VGB=1.0, L=0.13)
```
Internally, for each candidate VGS the source sits at VS = VGB - VGS, so
VSB = VGB - VGS and VDS = VDB - VGB + VGS; the GM_ID locus along that path is
inverted for VGS.

At most one input may be a vector; output is a column vector. Same GM_ID
non-monotonicity trim as mode 3 above. NaN + warning when the target exceeds
the table maximum.
