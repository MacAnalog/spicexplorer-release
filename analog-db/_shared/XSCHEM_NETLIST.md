> **[REFERENCE / STALE-FRAMING]** — xschem netlisting runbook. Parent plan: `doc/plan_examples_db.md` D-11/O-3. This doc was written for a macOS host (xschem absent); the EDA server (`srv-elamien`) has xschem 3.4.5 on PATH. The Docker command below remains the authoritative path for PDK-symbol resolution. The Phase-0 "gated" framing is superseded — the base image now vendors three PDKs and xschem. The `analog-db export-raw --svg` step uses xschem on the host or container automatically.

# xschem → SPICE netlisting (D-11)

> Plan `doc/plan_examples_db.md` D-11 / O-3 (**resolved: Docker**). xschem is a tracked,
> per-PDK netlist *source*: a topology may originate from a `.sch` (analog-circuit-design) or a
> flat netlist (AnalogGym); the abstract netlist is the common product. The host EDA server has
> xschem on PATH; the `api` container also has it. The verified command below remains the
> canonical way to resolve PDK symbols correctly.

## Prerequisite — confirmed present

`docker/Dockerfile.spice-base` installs **xschem** (Ubuntu universe, runtime stage, line ~109)
alongside ngspice + the IHP PDK. The container has `PDK_ROOT=/opt/pdk` (`ihp-sg13g2`) and the
PDK's xschem symbol library, which each circuit's `schematic/xschemrc` sources.

## The command (headless, batch) — VERIFIED live 2026-06-10

```bash
xschem -x -q -n -s -o <out_dir> <file>.sch
#  -x  no X / GUI       -q  quiet      -n  netlist (SPICE)
#  -s  spice netlist mode    -o  output directory
```

**Gotcha (confirmed):** the vendored PDK subset ships the xschem *symbol library*
(`/opt/pdk/ihp-sg13g2/libs.tech/xschem/sg13g2_pr/*.sym`) but **no PDK `xschemrc`**, so the
project-level `xschemrc` (which `source`s `$PDK_ROOT/$PDK/libs.tech/xschem/xschemrc`) fails and
every PDK symbol resolves "MISSING". Set the library path explicitly and bypass the repo
`xschemrc`:

```bash
# from spicexplorer-platform/ (Docker stack up; see verify-live-spice-in-docker)
tar -C examples/analog-db/circuits/amp_001_5t/pdk/ihp-sg13g2 -cf - schematic | \
  docker compose exec -T api bash -lc '
    d=$(mktemp -d) && tar -C $d -xf - && cd $d/schematic && rm -f xschemrc &&
    XSCHEM_LIBRARY_PATH=/opt/pdk/ihp-sg13g2/libs.tech/xschem:. \
      xschem -x -q -n -s -o . ota-5t.sch && cat ota-5t.spice'
```

Verified output: all 13 `XM*` devices of the IHP 5t implementation emitted with
`sg13_lv_nmos`/`sg13_lv_pmos` model names + `x_dut_*` design-variable symbols.

The product (`ota-5t.spice`) is the **per-PDK** netlist source: a `.sch` instantiates
PDK-specific devices, so the netlist is a property of the binding, not the abstract topology.
The canonical *visual* is the rendered `abstract/schematic.svg` (D-11).

## Status (Phase 0) — historical (see the top banner)

*(The "gated" framing below is superseded: the base image now vendors three PDKs and xschem, and
`analog-db export-raw --svg` runs xschem on the host or container automatically. Kept for
provenance.)*

- **Command + image prerequisite: confirmed** (xschem in the base image; flags from the
  Dockerfile; `PDK_ROOT`/symbol lib present).
- **Live run: (historical) gated.** Not executed *at the time of writing* — the host had no xschem
  and the Docker daemon was down. Run the block above in the `api` container to produce the
  `.spice`. The generator path SpiceXplorer actually relies on for `pdk/<pdk>/netlist.spice` is
  **circuitgraph lowering** (`analog-db generate`, PDK-free) — xschem netlisting is the *alternate*
  source for schematic-origin circuits.
