# Analog Building-Block Sizing & Detection Rules — Index

CMOS-only design notes, one per building block, that feed the **functional-block
detection** in `spicexplorer-circuitgraph` and the subcircuit **templates** in
`analog-db`. Each note pairs the *sizing rules* (geometry/bias constraints that define a
block's function) with the *structural signature* the graph matcher keys on. The notes
are **co-located with the templates they describe** — see **Repository layout** below.

## Sources

- **Massier, Graeb, Schlichtmann — "The Sizing Rules Method for CMOS and Bipolar Analog
  IC Synthesis," *IEEE TCAD*, 2008.** Generic sizing rules (eqs. 16–44) per building block.
  *(Bipolar rules exist in the paper but are out of scope here — CMOS only.)*
- **Aggarwal, Gupta, Gupta — "A comparative study of various current mirror
  configurations," *Microelectronics Journal* 53 (2016) 134–155.** The current-mirror
  topology catalog, structural discriminators, and performance ordering. *(Already cited
  in the `analog-db` CM manifest `provenance`.)*
- **Pham et al. — "GENIE-ASI," 2025.** Block taxonomy (HL1/2/3) and netlist recognition rules.
- **Guglielmi et al. — "High-Value Tunable Pseudo-Resistors Design," *IEEE JSSC* 55(8), 2020.**
  Pseudo-resistor cell taxonomy + floating-voltage-generator bias topologies.

## Repository layout

Each **functional-block family** is a directory under `templates/` with its own
`manifest.yaml` (the schematics/netlists the circuitgraph matcher overlays) and a
`rules/` subfolder holding that family's design note(s). The manifest **registers** its
notes under a `rules:` key (path + title + sources) so the rules travel with the
templates. Cross-cutting material — this index, plus the two *embedded-motif* primers
(**device roles**, **level shifter**) that no single family owns — lives at the library root.

```
templates/
├── README.md                     ← this index + house style + taxonomy
├── device_roles.md               ← Level-0 vccs/vcres primer (embedded in every block)
├── level_shifter.md              ← cascode sub-motif primer (embedded in cascode mirrors)
├── current_mirror/
│   ├── manifest.yaml             ← templates: … + rules: [rules/current_mirror.md]
│   ├── rules/current_mirror.md
│   └── {nmos_current_sink,pmos_current_source}/…   (.sch/.png + simulation/*.spice)
├── miscellaneous/
│   ├── manifest.yaml             ← rules: [rules/differential_pair.md, rules/cross_coupled_pair.md]
│   └── rules/{differential_pair,cross_coupled_pair}.md
├── transmission_gate/            ← 2 templates: bulk-blind tg.pair.cmos + rail-bulk tg.pair.cmos_rail_bulk (match_bulk)
│   ├── manifest.yaml             ← templates: … + rules: [rules/transmission_gate.md]
│   ├── rules/transmission_gate.md
│   └── *.sch + simulation/*.spice
└── pseudo_resistor/              ← partial: the 4 Fig-3 series cells (pr.series.*, match_bulk); 12 of §4 pending
    ├── manifest.yaml             ← templates: … + rules: [rules/pseudo_resistors.md]
    ├── rules/pseudo_resistors.md
    └── *.sch + simulation/*.spice
```

> The matcher reads **only** each manifest's `templates:` list; `rules:` is metadata for
> humans + LLM agents. A *rules-only* manifest (empty `templates:`) is skipped by the
> library API and never loaded by the matcher — it just reserves the family and tracks
> its note until schematics are drawn.

## House style — templated layout

**Every block note uses these numbered sections, in order:**

| # | Section | Contents |
|---|---|---|
| — | Title + metadata blockquote | Family/class · polarity · `StructuralRole` emitted · source refs |
| 1 | **Function** | What the block does; transfer relation |
| 2 | **Structure & recognition** | Topological signature the matcher keys on — device count/type, diode-connection, shared gate/source nets, stacking, non-MOS elements, ports |
| 3 | **Sizing rules** | FE/FG/RG/RE constraint table with equation references |
| 4 | **Variants** *(mirrors only; omit otherwise)* | Detection catalog + discriminator ladder |
| 5 | **Design intuition & trade-offs** | Why the rules hold; performance ordering |
| 6 | **Template mapping** | `analog-db` template `class` ids + detection status / gaps |

## Rule classification (Massier, Fig. 1)

Along two axes — **Function vs. Robustness** and **Geometric vs. Electrical**:

| Label | Concerns | Constrains | Example |
|---|---|---|---|
| **FG** | Function | Geometry ($W$, $L$) | $l_1 = l_2$ |
| **FE** | Function | Electrical ($v_{ds}$, $v_{gs}$) | $\lvert v_{ds_2} - v_{ds_1}\rvert \le \Delta V_{ds_{max}}$ |
| **RG** | Robustness | Geometry | $w \cdot l \ge A_{min}$ |
| **RE** | Robustness | Electrical | $v_{gs} - V_{th} \ge V_{gs_{min}}$ |

*Equalities* (e.g. $l_1=l_2$) reduce free parameters → faster optimization. *Inequalities*
keep devices in their intended region → must hold throughout sizing/centering. Higher-level
blocks inherit the rules of the sub-blocks they contain.

## How detection works (circuitgraph, for context)

The matcher runs **labeled subgraph monomorphism** (networkx VF2) of each template's
SPICE-subckt graph against the flattened host. What it keys on:

- **Device node:** type + `polarity` (nmos/pmos). `match_models`/`match_params` are **off**.
- **Edge token:** the **pin multiset** (gate/drain/source) between a device–net pair — this
  keeps gate distinct from drain/source. **Bulk is dropped** in detection (`match_bulk=off`) —
  unless a template opts back in with the manifest key `match_bulk: true` (per-template
  bulk-aware matching: that template's drawn bulk wiring becomes part of its identity; on an
  equal device set a bulk-strict match wins the primary over a bulk-blind one).
- **Diode-connection is topological:** drain and gate on one net ⇒ two parallel edges (no
  explicit flag).
- **Supply rails** are anchored by class (`match_supply=on`); **internal nets** must map to a
  private host net of equal degree (`match_internal_exact`).

**Deterministic structural roles emitted** (ground truth; the LLM layer must not override):
`current_mirror`, `current_mirror_reference`, `cascode_device`, `differential_pair`,
`tail_current_source`, `pseudo_resistor`, `analog_switch`.

## Hierarchy (Massier, Figs. 2–3) — CMOS

| Level | Blocks |
|---|---|
| **0** — device role | current source (`vccs`, saturation), resistor (`vcres`, triode) |
| **1** — transistor pair | simple current mirror (`cm`), level shifter (`ls`), differential pair (`dp`), cross-coupled pair (`cc`) |
| **2** — 3–4 transistors | cascode CM (`CCM`), 4-transistor CM (`4TCM`), wide-swing cascode CM (`WSCCM`), Wilson CM (`WCM`), improved Wilson CM (`IWCM`) |
| **3** — stage | differential stage (`DS`) |

> Lists only the **rule-bearing** CMOS blocks. Massier's Fig. 2 also contains helper pairs
> (vr I/II, `cml`, `cp`) on Level 1 and the current-mirror/level-shifter banks (CMB, LSB) on
> Level 2, which carry no standalone sizing rules of their own.

## GENIE-ASI recognition taxonomy (Table VII)

| Level | Blocks |
|---|---|
| **HL1** — device | `MosfetDiode`, `load_cap`, `compensation_cap` |
| **HL2** — structure | `DiffPair`, `CM`, `Inverter` |
| **HL3** — stage | `firstStage`, `secondStage`, `thirdStage`, `feedBack`, `loadPart`, `biasPart` |

## Technology-specific constants

Extracted **once per technology**, reused across blocks: $V_{sat_{min}}$, $V_{lin_{min}}$,
$A_{min}$, $W_{min}$, $L_{min}$, $V_{gs_{min}}$, $\Delta V_{ds_{max}}$, $\Delta V_{gs_{max}}$.

## Device model (Massier, eq. 16)

Shichman–Hodges, design parameters $W$, $L$:

$$
i_d =
\begin{cases}
0, & v_{gs} \le 0 \\[2pt]
K\frac{W}{L}\left[(v_{gs}-V_{th}) - \frac{v_{ds}}{2}\right]v_{ds}(1+\lambda v_{ds}), & 0 \le v_{ds} < v_{gs}-V_{th} \\[2pt]
\frac{1}{2}K\frac{W}{L}(v_{gs}-V_{th})^2 (1+\lambda v_{ds}), & v_{gs}-V_{th} \le v_{ds}
\end{cases}
$$

$K = \mu_{Si} C_{ox}$; $V_{th}$ threshold; $\lambda$ channel-length modulation. Gate current neglected.

## File index

**Shared primers (library root)** — embedded motifs no single family owns:

| Note | Blocks |
|---|---|
| [device roles](device_roles.md) | `vccs`, `vcres` (Level-0 roles) |
| [level shifter](level_shifter.md) | `ls` (cascode sub-motif) |

**Per-family notes** (`<family>/rules/`, registered in each `<family>/manifest.yaml`):

| Family dir | Note | Blocks | Detects as |
|---|---|---|---|
| `current_mirror/` | [current mirrors](current_mirror/rules/current_mirror.md) | `cm`, `CCM`, `4TCM`, `WSCCM`, `WCM`, `IWCM` + Aggarwal catalog | `current_mirror` |
| `miscellaneous/` | [differential pair](miscellaneous/rules/differential_pair.md) | `dp` (+ variants), differential stage `DS` | `differential_pair` |
| `miscellaneous/` | [cross-coupled pair](miscellaneous/rules/cross_coupled_pair.md) | `cc` | `cross_coupled` |
| `transmission_gate/` | [transmission gate](transmission_gate/rules/transmission_gate.md) | CMOS pass gate (`tg.pair.cmos` bulk-blind + `tg.pair.cmos_rail_bulk` bulk-strict) | `analog_switch` |
| `pseudo_resistor/` | [pseudo-resistors](pseudo_resistor/rules/pseudo_resistors.md) | series pseudo-resistor cells `pr.series.*` (Fig. 3a–d, bulk-strict `match_bulk: true`); 12 more §4 topologies + `fvg.*` generators pending | `pseudo_resistor` |
