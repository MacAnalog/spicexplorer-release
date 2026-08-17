# gm/ID LUT store — regenerable, out-of-repo

The gm/ID lookup tables are **not committed** (they are large regenerable artifacts, and the
Spectre-lane tables come from a licensed kit). The canonical store lives **out-of-repo** at
`gmid.out_root` (default `~/.spicexplorer/gmid/<pdk>/`), laid out
`<device>__<corner>[__<T>C].pkl` + `.manifest.json`.

## Rebuild

```bash
python tools/regen_gmid_luts.py                 # everything the environment can build
python tools/regen_gmid_luts.py --pdk sky130    # one PDK (all devices × corners)
python tools/regen_gmid_luts.py --open-only     # skip the licensed Spectre lane
```

- **Open PDKs** (sky130 / ihp-sg13g2 / gf180mcu) → native ngspice + `$PDK_ROOT` (per-L parallel).
- **Spectre-routed kits** → headless Spectre via the virtuoso-bridge (licensed kit; needs the operator wrapper
  `$SPICEXPLORER_SPECTRE_MODEL_ROOT/<corners.lib_file>` and the bridge `local.env`).

## Reading a LUT

```python
from spicexplorer_analog_db import gmid
nch = gmid.lut("ihp-sg13g2", "sg13_lv_nmos", "tt")   # resolves the out-of-repo store, then the
                                                     # legacy in-repo fallback; clear regen error if absent
```

or the typed leaf tool: `spicexplorer_gmid.DeviceTable.load(gmid.find_lut_path(pdk, device, corner))`.

## What gets built

Max-fidelity grid (25 mV VGS/VDS, ~11 VSB points to VDD/2, W = 5 µm), all 5 corners
`tt/ss/ff/sf/fs`, 27 °C:

| PDK | devices | lane |
|---|---|---|
| sky130 | `…nfet_01v8`, `…pfet_01v8` | ngspice |
| ihp-sg13g2 | `sg13_{lv,hv}_{nmos,pmos}` | ngspice |
| gf180mcu | `nfet_03v3`, `pfet_03v3` | ngspice |
| *(licensed Spectre kit)* | the kit's LVT/SVT/HVT core devices, per its registry `gmid.devices` block | Spectre |

Full details, grid rationale, and the pygmid LUT format: [`../GMID.md`](../GMID.md).
