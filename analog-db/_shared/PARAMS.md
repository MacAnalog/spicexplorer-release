# DUT parameterization — `spicexplorer/params@1`

The per-circuit `abstract/params.yaml` contract: the **atomic per-instance parameter inventory**
plus **declarative default tying**. Plan: meta `doc/plan_parameterization.md`. Schema:
[`schema/params.schema.json`](schema/params.schema.json) (validated at Tier 0 when the file is
present — adoption is per circuit, absence is not a failure until the P2 migration).

**Why:** today the sharing decisions (matched pairs, mirror L-sharing, frozen m-ratios) are baked
into the abstract netlist at authoring time. This layer separates *what CAN vary* (`devices:` —
a physical fact of the topology, exhaustive, GENERATED from `abstract/topology.cgraph.json`) from
*what SHOULD vary together* (`groups:` / `ratios:` — shipped defaults tagged with machine-readable
`kind` reasons, so an upstream user dissolves ties **by category** instead of re-authoring
netlists).

```yaml
schema: spicexplorer/params@1
devices:                      # atomic inventory — GENERATED, one row per instance
  XM1: {w: x_dut_xm1_w, l: x_dut_xm1_l, m: x_dut_xm1_m}
groups:                       # shipped DEFAULT tying — a recommendation, tagged with WHY
  - {name: input_pair,    kind: matched_pair,  members: [XM1, XM2], tie: [w, l, m]}
  - {name: nmos_mirror_l, kind: mirror_length, members: [XM3, XM4], tie: [l]}
ratios:                       # mirror gains: frozen constants, or integer knobs via is_integer
  - {param: m, ref: XM7, of: XM6, ratio: "17/3"}   # m(XM7) = m(XM6) × 17/3
```

## Settled design decisions (plan §4, locked in P0)

1. **Per-finger `(w, m)` is canonical.** The atomic pair is what the netlist says (and IHP PSP
   clips silently above ~10 µm total width); total-W is a *derived* convenience knob, never a
   stored field.
2. **Generation lives in this package** (`analog-db gen-params`, lands P1) — analog-db owns the
   artifact; the platform's circuitgraph is the structural detector. The P0 detection spike is
   `spicexplorer_analog_db.params` (pure functions over the committed cgraph JSON).
3. **Ties lower to `.param` lines referencing the FIRST member's atomic symbols** (P2):
   `.param x_dut_xm4_l = {x_dut_xm3_l}`. Group names stay a YAML-level concept and never appear
   in decks — fewer symbols, and *untying = shadowing* (an upstream project writing the atomic
   symbol directly overrides the tie for that symbol only). The optimizer wrapper needs zero
   changes (it already rewrites `.param` values verbatim).

4. **Non-MOS inventory rows echo the netlist's knob (P4).** ``devices:`` is mechanical
   ``x_dut_<id>_<field>`` for MOS geometry only; V/I bias sources and passives echo the free
   symbol the card already binds (``i_tail``, ``vref_val``, ``'c_comp'``, ``dc {…}`` forms —
   bias-branch values are already free params and stay first-class knobs; plan D-1 "the scheme
   is not geometry-only"). Passive values SHARED across instances were atomized + tied
   (``shared_geometry`` on the value field) by the P4 sweep; unique ones keep their names.

## `kind` vocabulary (@1)

| kind | meaning | typical `tie` |
|---|---|---|
| `matched_pair` | symmetric same-polarity pair (diff pair, mirror-load halves) | `[w, l, m]` |
| `mirror_length` | current-mirror members sharing L for ratio accuracy | `[l]` |
| `bias_chain` | devices tracking a bias branch | authored |
| `shared_geometry` | author-opinion sharing with no single structural cause (legacy global ties) | authored |

## Phasing

P0 (this slice): schema locked + §4 settled + structural detection spike (matched pairs +
mirrors on `amp_001_5t`). P1: `gen-params` generator + Tier-1 coherence checks (members exist /
electrically coherent with the claimed kind; detected-but-untied symmetry is a **warning**).
P2: lowering to `.param` tie blocks + numeric-parity acceptance on `amp_001_5t`. P3: platform
group/atomic resolution + `ungroup:`. P4 (DONE): `amp_022` opinionated migration + the
full-catalog atomic sweep (`tools/migrate_params.py`; numeric parity per circuit × PDK gated by
`tests/test_params_p4.py` against `tests/data/premigration_dut_geometry.json`). P5: docs.
`kind: reference` circuits are out of scope (no sizing contract).

## Provenance surfaces + regen flow

The inventory is visible without opening `params.yaml`, in three places:

- **Deck banner** — every committed deck carries a `** params: N free + M frozen knobs (sizing.yaml)
  · T tied · R ratio-derived (abstract/params.yaml)` line (full testbench decks add ` · K testbench
  params`). `free`/`frozen` are the `sizing.yaml` rows (`freeze:false`/`true`); `tied`/`ratio-derived`
  are the generated tie/ratio `.param` lines.
- **`catalog.json`** — a per-circuit `params` block (`devices` count, `groups` name→kind, `ratios`
  count, per-PDK `symbols` free/frozen/tied/ratio counts, and any `untied_symmetries`).
- **`analog-db verify --tier 1`** — a `params:inventory:<pdk>` info row echoing the banner counts,
  and a `params:untied_symmetry` **warning** (not a gate) for a detected-but-untied symmetry.

Both `params.yaml`'s `devices:` and the derived surfaces are GENERATED. After editing the AUTHORED
`groups:`/`ratios:` (or the topology), refresh with `analog-db gen-params --circuit <id> --write`
(it preserves the authored sections), then `analog-db generate --all` to relower the decks + rebuild
the catalog — the Tier-1 drift guard fails a stale commit. A worked walk-through (atomic symbols →
tie block → `sizing.yaml` free-symbol keying → banner) is in [`PDK_SIM.md`](PDK_SIM.md).
