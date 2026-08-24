# Publication schematics

Hand-placed, figure-quality xschem schematics for the eight amplifier DUTs of the
spicexplorer-tcas-2026 study. **AUTHORED artifacts** — unlike `raw/<id>/<id>.sch`
(which `analog-db generate` rewrites from the lowered netlist with automated
placement), these are drawn for human readers and are NOT touched by the generator.

## Provenance and verification

Each `.sch` was drawn against its circuit's committed lowered netlist
`raw/<id>/ihp-sg13g2/_dut.spice` and gated on netlist equivalence before landing:
the schematic was netlisted headlessly (`xschem -x -q -n -s`) and compared
device-for-device — device type, pin-to-net connectivity (up to a consistent
bijection on nets the drawing wires directly instead of labelling), and W/L/m/value
expressions verbatim. All eight pass with zero missing/extra devices. The drawing is
a *projection* of the committed netlist, not a second source of truth: if a netlist
changes, re-verify its figure.

Known, deliberate deltas against `_dut.spice` (electrically no-ops):

- `ng=1` on MOS devices and `m=1` on R/C where `_dut.spice` omits them — the xschem
  symbol `format` strings cannot omit these; both are the PDK model defaults.
- Some `**.subckt` header port *orders* differ from `_dut.spice` (sets are
  identical). These files are figures; do not instantiate them positionally.
- Internal nets keep the committed netlist's names (including ugly ones like
  `net013`) so the figures stay mechanically checkable against the netlist.
  Rename cosmetic labels downstream (e.g. in a LaTeX redraw), not here.

Reading notes encoded in the figures themselves: amp_011 and amp_012 are
single-ended-output amplifiers (`vout` is the only output port; `VOUTP`/`VOUTN` are
internal mirror-load nodes), and amp_012 contains a matched replica branch
(M2/M61/M13/M18) whose mid node intentionally drives no gate.

## Rendering

The committed `.svg` files are rendered with the light palette and cropped to
content. To re-render, use an `xschemrc` that puts the PDK and platform symbol
libraries on the path and selects the light scheme:

```tcl
set XSCHEM_LIBRARY_PATH {}
append XSCHEM_LIBRARY_PATH {:$PDK_ROOT/ihp-sg13g2/libs.tech/xschem}
append XSCHEM_LIBRARY_PATH {:<spicexplorer-platform>/docker/pdk/ihp-sg13g2/libs.tech/xschem}
append XSCHEM_LIBRARY_PATH {:<spicexplorer-platform>/docker/xschem_library}
append XSCHEM_LIBRARY_PATH {:<this repo>/drawings}
set dark_colorscheme 0
```

then `xschem --rcfile <rc> -x -q -b --svg --plotfile out.svg <id>.sch`. xschem
exports a fixed 1000×700 canvas; crop the SVG viewBox to content afterwards.
Symbol families in use: PDK `sg13g2_pr/sg13_lv_{n,p}mos.sym` (prints W/L parameter
text on canvas — amp_024) and the platform's `devices/sg13_lv_*_np.sym` wrappers
(byte-identical pins/format, no parameter text — the denser DUTs).
