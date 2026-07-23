# Pseudo-Resistor (`pseudo_resistor`)

> **Family/class:** `pseudo_resistor` (new — not in Massier/Aggarwal) · **Polarity:** pmos
> (default; nmos needs an isolated p-well) · **Roles emitted:** `pseudo_resistor` (all matched
> devices of a registered cell)
> **Sources:** Guglielmi, Toso, Zanetto, Sciortino, Mesri, Sampietro, Ferrari —
> "High-Value Tunable Pseudo-Resistors Design," *IEEE JSSC* 55(8), 2020, pp. 2094–2105.
> **Status:** PARTIAL — the four Fig-3 series-symmetric cells (§4.2, `pr.series.*`) are drawn,
> netlisted, and registered in the family manifest; the other 12 §4 topologies (single-cell,
> parallel, extensions, `fvg.*` generators) are still to be drawn.

A pseudo-resistor mimics a very-high-value resistor (MΩ–TΩ) with one or a few subthreshold
MOSFETs, occupying far less area than a physical resistor and avoiding its distributed-RC
frequency/noise penalty. Used to bias high-sensitivity, low-noise transimpedance amplifiers
(TIAs) and to handle dc leakage in capacitive-feedback front ends. Layout follows the house
style in [design-rules index](../../README.md).

## 1. Function

Provide a high, tunable equivalent resistance in a compact, low-noise, (ideally) symmetric
2-terminal element. Around $V_{AB}=0$ the device sits in **deep subthreshold**, the parasitic
well diode is off, and the small-signal resistance is set by the subthreshold transfer
(eqs. 1–3):

$$I_{SD} = I_{SD0}\,e^{V_{SG}/(nV_{th})}\left[1 - e^{-V_{SD}/V_{th}}\right], \qquad
r_{eq0}\big|_{V_{AB}=0} = \frac{V_{th}}{I_{SD0}}.$$

**Tuning:** a floating-voltage generator sets $V_{SG}=V_{Gen}$, giving (eqs. 4–5):

$$r_{eq,T} = \frac{1}{4 n \mu C_{OX} V_{th}}\left(\frac{L}{W}\right)
e^{(|V_T| - V_{Gen})/(nV_{th})}.$$

Resistance rises with $L/W$ and falls **exponentially** with $V_{Gen}$. Reported range:
tunable **20 MΩ – 20 GΩ**; final design $R_{eq}\approx300$ MΩ at $I_B=2$ nA.

## 2. Structure & recognition

> ⚠️ **Detection is genuinely hard for this block** — capture these signatures when the
> schematics land, then finalize.

- **Single-cell transdiode** is literally a **diode-connected MOSFET** (gate tied to drain)
  → it collides structurally with GENIE-ASI's `MosfetDiode` / a mirror reference. The
  distinguishing cues are *not* purely gate/drain topology:
  - **Isolated / own floating well** — the bulk is **not** tied to a supply rail. This is
    exactly the case the current-mirror matcher misses with `match_bulk=off`; pseudo-resistor
    detection likely **needs `match_bulk=on`** (cross-ref
    [current mirrors](../../current_mirror/rules/current_mirror.md) §4 bulk-driven caveat).
  - **Both terminals are signal nodes** (A, B) — neither is a supply rail; the device sits in
    a high-impedance bias/feedback path, not a mirror leg.
  - Operates in subthreshold (bias-dependent — predictable, not confirmable from topology).
- **Tunable cell** adds a **floating-voltage generator** driving the gate (gate is neither
  drain- nor rail-tied but driven by a `VGen` net) — a strong discriminator vs. a plain diode.
- **Symmetric multi-cell** cells have an **anti-series / anti-parallel MOSFET pair** with gates
  commoned to the generator net and drains/sources cross-connected — a distinctive two-device
  signature worth its own template.
- **Proposed roles (TBD):** `pseudo_resistor`, `pseudo_resistor_cell`,
  `floating_voltage_generator` (companion bias sub-block).

## 3. Sizing / design rules

Design guidelines extracted from the paper (technology constants: $n$ sub-threshold slope,
$\mu$, $C_{OX}$, $V_{th}=kT/q$, $V_T$ threshold):

| # | Rule / relation | Purpose |
|---|---|---|
| PR1 | $r_{eq,T} \propto (L/W)\,e^{(|V_T|-V_{Gen})/(nV_{th})}$ (eq. 5) | Set resistance by $L/W$ and tune with $V_{Gen}$ |
| PR2 | Prefer **pMOS** (lower hole mobility → higher $R$, smaller device) | Reach high $R$ compactly |
| PR3 | Device in its **own floating well**; mandatory for nMOS, avoids/uses body effect | Symmetry, linearity, rail-independence |
| PR4 | Bias around $V_{AB}=0$, **deep subthreshold**; well diode off | High-$R$, low-current regime |
| PR5 | Parallel identical pair: $r_{eq}=r_{M1}\Vert r_{M2}=r_{eq,T}/2$ (eq. 6) | Symmetric cell |
| PR6 | **Series-cascade $N$ cells** to extend the linear range (Fig. 7) | Widen linear $V_{AB}$ span (tens→hundreds of mV) |
| PR7 | Resistive divider: $R_{eq}=(1+R_1/R_2)r_{eq}+R_1\cong N\,r_{eq}$, $N=1+R_1/R_2$ (eqs. 7–8) | Compact area-efficient high $R$ (one cell + divider) |
| PR8 | Mirror-biased generator: $R_{eq}=\dfrac{V_{th}}{2I_B}\dfrac{W_B}{W}N$ (eq. 15) | Link $R_{eq}$ to geometry + externally-tunable $I_B$ |

**Non-linearity is a design axis (not a defect):**
- **Sub-linear** cells (Fig. 3a,b) — current saturates; self-limit dc.
- **Super-linear** cells (Fig. 3c,d; parallel Fig. 5) — used in TIA feedback for **dynamic
  offset reduction** (super-linear $I$–$V$ raises average current with ac signal, pulling dc
  output back).

## 4. Variants — topology catalog & **schematics needed**

Each row is a candidate `analog-db` template. **⬜ = schematic to be drawn by owner.**
`req` column notes the resistance/linearity character.

### 4.1 Single-cell

| # | Proposed id | Devices | Structural signature | Fig | Notes | Sch |
|---|---|---|---|---|---|---|
| 1 | `pr.single.transdiode` | 1 pMOS | gate–drain shorted; own n-well; A, B signal nodes | 1a | Non-tunable, asymmetric baseline | ⬜ |
| 2 | `pr.single.tunable_gate_a` | 1 pMOS + `VGen` | generator between gate & node **A** | 2a | Body effect ⇒ better linearity for $V_{AB}>0$ | ⬜ |
| 3 | `pr.single.tunable_gate_b` | 1 pMOS + `VGen` | generator between gate & node **B** | 2b | Symmetric to #2; strongly asymmetric $I$–$V$ | ⬜ |

### 4.2 Series symmetric (2 mirrored cells)

| # | Proposed id | Wells | Generators | Linearity | Fig | Sch |
|---|---|---|---|---|---|---|
| 4 | `pr.series.indep_well_indep_gen` | 2 independent | 2 independent | sub-linear | 3a | ✅ registered |
| 5 | `pr.series.shared_well_gen` | shared | shared | sub-linear | 3b | ✅ registered |
| 6 | `pr.series.shared_well` | shared | independent | super-linear | 3c | ✅ registered |
| 7 | `pr.series.shared_gen` | independent | shared | super-linear | 3d | ✅ registered |

### 4.3 Parallel symmetric

| # | Proposed id | Devices | Signature | Fig | Notes | Sch |
|---|---|---|---|---|---|---|
| 8 | `pr.parallel.gen_anode` | 2 pMOS ∥ | generators at well-diode **anode**; no internal node | 5a | ★ **selected TIA topology** | ⬜ |
| 9 | `pr.parallel.gen_cathode` | 2 pMOS ∥ | generators at well-diode **cathode** | 5b | super-linear when diodes off | ⬜ |

### 4.4 Linearity extension & application

| # | Proposed id | Composition | Fig | Notes | Sch |
|---|---|---|---|---|---|
| 10 | `pr.series.cascade_n` | $N$ single cells in series ($N=1,2,4$) | 7 | Extend linear range | ⬜ |
| 11 | `pr.app.cell_with_divider` | 1 parallel cell (#8) + $R_1$, $R_2$ divider | 8 | $R_{eq}\cong N\,r_{eq}$; the compact TIA DC-handling network | ⬜ |

### 4.5 Floating-voltage generator (companion bias sub-block, $V_{Gen}=V_+-V_-$)

| # | Proposed id | Topology | Fig | Notes | Sch |
|---|---|---|---|---|---|
| 12 | `fvg.source_follower` | source follower | 12a | Simplest; process-sensitive, needs double well | ⬜ |
| 13 | `fvg.improved_source_follower` | improved source follower | 12b | $V_T$-compensated; needs double well | ⬜ |
| 14 | `fvg.buffered_transdiode` | op-amp-buffered transdiode | 12c | Accurate; area/power cost | ⬜ |
| 15 | `fvg.transdiode` | transdiode | 12d | Single generator; simple |  ⬜ |
| 16 | `fvg.matched_transdiode_pair` | 2 pMOS transdiodes + cascode current-mirror bias | 13 | ★ **proposed** matched, process-stable bias | ⬜ |

**16 schematics total** (11 pseudo-resistor cells + 5 floating-voltage generators). Highest
priority for the TIA use case: **#8 (`pr.parallel.gen_anode`)**, **#11
(`pr.app.cell_with_divider`)**, and **#16 (`fvg.matched_transdiode_pair`)** — that trio is the
paper's actual fabricated design.

## 5. Design intuition & trade-offs

- **Sub- vs super-linear** picks itself by application: super-linear (Fig. 3c/d, parallel
  Fig. 5) for TIA feedback where dynamic-offset reduction is wanted; sub-linear for
  self-limiting dc.
- **Series vs parallel:** series cells share/isolate wells & generators (Fig. 3). A shared
  **generator** (Fig. 3d, independent wells) loads an internal node but still reaches ≈100 kHz;
  shared-**well** structures (Fig. 3b,c) load the well and are limited to very low frequencies;
  fully independent well+generator (Fig. 3a) drives parasitic well capacitance from the outer
  pins → wider band, larger area. **Parallel (Fig. 5) has no internal node** → best for
  high-frequency symmetric operation (selected for the MHz-range TIA).
- **Process stability:** $R_{eq}$ depends **exponentially** on $V_{Gen}$ and $V_T$ ⇒ raw
  source-follower bias gives huge spread ($\sigma_\alpha\approx0.79$). The matched
  transdiode-pair generator (#16) cancels $V_T$ variation, tightening spread
  ($\sigma_\alpha\approx0.107$, $R_{eq}$ 200–500 MΩ).
- **Noise:** modeled as ideal $r_{eq}$ + current-noise PSD. Thermal-limited input noise is
  $4kT/R_{eq}$, **amplified by the divider factor $N$** (eq. 10) — so cascading cells beats
  the divider for noise, but the divider wins on area. Shot-limited: $2qI_{IN}$ (eq. 11).
  Advantage over a physical resistor: no distributed-RC → far lower high-frequency noise.

## 6. Template mapping

- **`analog-db` family:** `pseudo_resistor` (+ companion `floating_voltage_generator`) —
  registered at `templates/pseudo_resistor/manifest.yaml` (schema
  `spicexplorer/subcircuit-template-library@1`, provenance → Guglielmi 2020). The four §4.2
  series cells (`pr.series.*`, Fig. 3a–d) are drawn + registered and load in circuitgraph's
  `default_pseudo_resistor_library()` / merged `default_subcircuit_library()`.
- **Ports (registered):** `a`, `b` (the two resistor terminals, `port_A`/`port_B` in the
  netlists). `VGen` collapses out of the topology-only netlists (an ideal floating source ties
  gate to node); the isolated-well net is drawn but not matched (see below).
- **12 templates remain ⬜ pending schematics** (§4.1/4.3/4.4/4.5). Once drawn, capture the
  exact structural signature per §2 and add a manifest row each.
- **Matcher prerequisites — status:** the "neither terminal is a supply rail" rule comes FREE
  from `match_supply=on` (a template port net can never map to a host rail-class net). The
  **`match_bulk=on` isolated-well discriminator is LANDED**: every registered `pr.series.*`
  entry sets the manifest's per-template `match_bulk: true`, so its MOS bulk edges stay in the
  matcher's projection and a match asserts the drawn well wiring (bulk follows the source in
  all four cells; never a rail). The four cells were already pairwise distinct bulk-blind
  (their D/G/S port-vs-middle placements differ); the flag adds the well check on top.
  Single-cell transdiodes (§4.1) are UNBLOCKED by the same capability — draw them, register
  with `match_bulk: true`, and the isolated well separates them from a mirror reference.
- **Roles emitted:** every matched device → `StructuralRole.MOS_PSEUDO_RESISTOR`
  (`pseudo_resistor`, deterministic ground truth).
- **Owner action:** draw the remaining §4 schematics, then add a `templates:` row per topology to
  `templates/pseudo_resistor/manifest.yaml` (this note already lives in `pseudo_resistor/rules/`).
