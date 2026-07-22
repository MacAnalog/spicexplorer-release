# AnalogGym reference snapshots — unimported amplifiers

Original schematic snapshots of [AnalogGym](https://github.com/CODA-Team/AnalogGym) amplifiers
whose topology is **not** in this DB, kept here for reference. The snapshots for the amplifiers we
*did* import live with their circuit at `circuits/<id>/reference/<Alias>.png` (and are indexed in
`catalog.json` under each circuit's `schematic.reference`).

| Snapshot | Why it's here, not under `circuits/` |
|---|---|
| `Qu_LEC_Pin_3.png` | Upstream netlist is missing/empty, so the importer skips it (`importers/analoggym.py`). |
| `Cascode_Miller_Pin_2.png` | A 2-stage (`Pin_2`) Miller-compensated amp; not part of the imported 3-stage (`Pin_3`) corpus. |

If either topology is later imported as a DB circuit, move its snapshot to
`circuits/<id>/reference/` and register it under that circuit's `artifacts.reference_schematic`.
