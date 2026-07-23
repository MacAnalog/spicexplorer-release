# Current Mirror (`cm` / family `current_mirror`)

> **Family/class:** `current_mirror` · **Polarity:** nmos (sink) / pmos (source) ·
> **Roles emitted:** `current_mirror`, `current_mirror_reference`, `cascode_device`
> **Sources:** Massier 2008 (eqs. 27–44) · Aggarwal 2016 (Figs. 1, 9–14, Tables 1–7) · GENIE-ASI (`CM`)

A current mirror produces a constant, geometry-set ratio between two (or more) branch
currents. This note covers the whole CMOS mirror family — the simple mirror, its
higher-order variants, the Aggarwal detection catalog, and how each maps to an `analog-db`
template class. Layout follows the house style in
[design-rules index](../../README.md).

## 1. Function

Hold a constant ratio between the two drain currents (gate currents ≈ 0), Massier eq. 27:

$$\frac{i_{d_2}}{i_{d_1}} = \frac{w_2 / l_2}{w_1 / l_1}.$$

Ideal behavior needs the output current independent of output voltage (high $r_{out}$) and
low input compliance. Aggarwal eq. 1 gives the simple mirror's small-signal figures:
$r_{in} = 1/g_{m1}$, $r_{out} = r_{o2} = 1/(\lambda i_{D2})$, $\omega_0 \approx g_{m1}/(C_{gs1}+C_{gs2})$.

## 2. Structure & recognition

The matcher keys on a **shared-gate, shared-source group** of same-polarity MOSFETs
containing at least one **diode-connected reference** (drain = gate on the supply rail),
plus one or more output copies. Distinguishing cues per variant (§4). Reference recovery:
the on-rail diode is the `current_mirror_reference`; a device with source on an internal
net (not the rail) is a `cascode_device`.

- **Ports** (template): `supply`, `ref_in`, `out`, optionally `ref_in2` (2nd bias diode)
  and `bias` (external gate bias for diodeless variants).
- **Diode-connection** shows up as two parallel gate/drain edges — no explicit flag.
- **Bulk is ignored** in detection, so a mirror is found whether the body ties to the rail
  or a separate well (**caveat:** this hides *bulk-driven* mirrors — see §4).

## 3. Sizing rules

Both transistors act as `vccs` (saturation) and inherit those rules — see
[device roles (vccs/vcres)](../../device_roles.md).
Simple-mirror rules (Massier eqs. 28–30):

| Rule | Constraint | Purpose |
|---|---|---|
| **FG** | $l_1 = l_2$ | Equal length → no systematic channel-length-modulation mismatch |
| **FE** | $\lvert v_{ds_2} - v_{ds_1}\rvert \le \Delta V_{ds_{max}(cm)}$ | Equal $v_{ds}$ → suppress ratio error from $\lambda$ |
| **RE** | $v_{gs_{1,2}} - V_{th_{1,2}} \ge V_{gs_{min}}$ | Large overdrive → robust to local mismatch |

Higher-order variants add rules on top (all inherit the simple-mirror rules):

| Variant | Added rules (Massier) | Note |
|---|---|---|
| Cascode (`CCM`) | $w_{ls(1)}=w_{cm(1)}$, $w_{ls(2)}=w_{cm(2)}$ (eqs. 39–40) | Level-shifter widths pinned to mirror widths |
| 4-transistor (`4TCM`) | $w_{vrI(1)}=w_{vrI(2)}$, $w_{cml(1)}=w_{cml(2)}$, $\lvert v_{ds_{vrI}}-v_{ds_{cml}}\rvert \le V_{ds_{max}(4TCM)}$ (eqs. 41–43) | Lower $v_{ds}$ drop; lower devices are `vcres` |
| Wide-swing cascode (`WSCCM`) | own rules (not from sub-modules); or take over `CCM` rules | Drop across left devices $= v_{gs}$ (one, not two) |
| Wilson (`WCM`) | `cm` rules with driving/driven **reversed**; ratio $i_2/i_1 = w_{cm(1)}/w_{cm(2)}$ (eq. 44) | 3rd (cascode) device is a `vccs` |
| Improved Wilson (`IWCM`) | same as `CCM` | Adds diode to fix Wilson's $v_{ds}$ mismatch |

## 4. Variants — detection catalog (Aggarwal 2016)

Aggarwal enumerates ~30 CM topologies; below are the **CMOS, structurally-detectable**
ones, with the connectivity signature the matcher can key on and the `analog-db` `class`
status. "GAP" = pure-MOS and templateable now; "NEEDS …" = requires a matcher capability
change.

| Topology (Aggarwal Fig.) | Devices | Structural signature (detection) | Distinguishing cue | Non-MOS | `analog-db` class |
|---|---|---|---|---|---|
| Simple (1a) | 2T | diode ref + output, shared gate/source | baseline | — | `simple` ✓ |
| Cascode (1d) | 4T | two stacked pairs; cascode source on internal net | no Wilson feedback edge | — | `cascode` ✓ |
| Wilson (1b) | 3T | output-branch drain → reference gate **feedback edge** | the feedback edge | — | `wilson` ✓ |
| Improved Wilson (1c) | 4T | Wilson + added input-branch diode | extra diode vs Wilson | — | `improved_wilson` ✓ |
| High-swing cascode (9a) | 4T | cascode + **2nd on-rail bias diode** (M4 ¼ aspect) | `ref_in2` present | — | `high_swing_cascode` ✓ |
| Improved high-swing (9c) | 5T | high-swing + extra bias device | 5th device | — | `improved_high_swing_cascode` ✓ |
| Self-biased high-swing (9d) | 4T + R | bias set by resistor across input branch | **R node** in group | R | `selfbiased_high_swing_cascode` ✓ |
| Low-voltage cascode (9b) | 4T | **no on-rail diode**; cascode gates from external bias | reference-less (`bias` port) | — | `low_voltage_cascode` ✓ |
| Self-biased wide-swing (integrated bias) | 11T | self-contained; integrated opposite-polarity bias mirror spanning both rails | single `ref_in`, spans rails | — | `wide_swing` ✓ |
| Self-cascode composite (11c) | 2T | series stack, gates tied to bias; M1 in triode; acts as one long device | 2 stacked, **not** a copy pair | — | **GAP** |
| FVF CM (10b) | 5T | flipped-voltage-follower loop (M5 regulates input node) | FVF feedback loop | — | **GAP** |
| Regulated / gain-boosted cascode (11b) | 4T (+$I_B$ src) | cascode + common-source feedback device (M4) sensing output | CS feedback device | — | **GAP** (pure-MOS form) |
| Triode-region simple (9j) | 3T | extra diode bias `Mb1` forces input M1 into triode | added input-branch bias diode | — | **GAP** |
| Triode-region cascode (9k) | 5T | M3/M4 triode active resistors + bias `M5` | triode active-resistor devices | — | **GAP** |
| Level-shifted simple/cascode (9g,h) | 3–5T | constant-$v_{gs}$ level-shift device between drain & gate of ref (breaks diode) | reference-less like low-voltage | — | **GAP** |
| Active / active-feedback / super-cascode (10a, 11a, 11e) | var | embeds an explicit **amplifier** sub-block | gain block present | — | **NEEDS** hierarchical amp template |
| Bulk-driven simple/cascode (13c,d) | 2/4T | **signal on bulk**, gate tied to rail | bulk is the input | — | **NEEDS** `match_bulk=on` |
| FGMOS simple/cascode (13a,b) | 2/4T | floating-gate, multiple control gates | multi-gate device | — | **NEEDS** FGMOS device model |
| Compensation R/C/L (12a,d; 11d) | 2–4T + R/C/L | simple/cascode + passive between ref gates or gate–source | passive present | R/C/L | passive-annotated **sub-variant** |

### Discriminator ladder (aligned to the matcher's `_CLASS_SPECIFICITY`)

1. **Count** same-polarity MOS sharing gate & source.
2. **Find the diode reference** (drain = gate on the supply rail). *None* → externally biased
   (`low_voltage_cascode`) or level-shifted/triode (diode broken by an inserted device).
3. **Wilson feedback edge?** (output-branch drain → reference/output-device gate) → `wilson`;
   an extra input-branch diode → `improved_wilson`. Otherwise cascode family.
4. **Second on-rail bias diode** (`ref_in2`)? → `high_swing_cascode` → `improved_high_swing_cascode`.
5. **Passive in the group:** R → `selfbiased_high_swing_cascode` / compensation; C or L → compensation sub-variant.
6. **Embedded gain block** (device/sub-block whose gate senses in/out in feedback) → regulated / active-feedback / FVF *(needs hierarchy)*.
7. **Signal on bulk, gate on rail** → bulk-driven *(needs `match_bulk`)*.
8. **Multiple control gates** per device → FGMOS.

Matcher tie-break when two templates hit the **same** device set (preferred first):
`improved_high_swing_cascode` > `selfbiased_high_swing_cascode` > `high_swing_cascode` >
`cascode` > `improved_wilson` > `low_voltage_cascode` > `wilson` > `simple`. (`cascode` over
`improved_wilson` is only a defensive default — on a real host the Wilson feedback edge
separates them cleanly.) `wide_swing` is not in the specificity list, so it sorts last on a tie.

## 5. Design intuition & trade-offs

Stating cascode/level-shifter constraints as **absolute width equalities** (not ratios)
drops the free-parameter count from 4→2 — the optimizer converges faster. The Wilson/cascode
families buy output resistance by adding devices, at the cost of headroom and, for
Wilson/improved-Wilson, a real zero before the dominant pole that peaks the response.

**Performance ordering (post-detection annotation — NOT a detection input; Aggarwal Tables 1–7):**

- **Accuracy (PER):** simple (very poor) < Wilson (poor) < cascode ≈ improved-Wilson ≈
  regulated cascode (very good) < compact-all-cascode (excellent, Table 7).
- **Output resistance:** simple ($\sim$200 k) ≪ cascode ≈ improved-Wilson ($\sim$14 M) <
  regulated cascode ($\sim$830 M) < super-cascode ($\sim$15 G). Self-cascode is only
  $\sim$5 M — near cascode, not in this top tier.
- **Output compliance:** cascode $\approx 2V_{DS,sat}+V_T$ (higher) vs. wide-swing /
  low-voltage / self-biased $\approx 2V_{DS,sat}$ (lower); simple $\approx V_{DS,sat}$.
- **Bandwidth:** enhanced topologies add parasitic $C$ → lower BW; Wilson/improved-Wilson
  peak (cascode does not); R/C/L compensation recovers it.

Once a class is detected, attach the relevant row as characterization metadata — this is
where the study's performance data belongs, feeding the LLM/semantic layer, never the matcher.

## 6. Template mapping

- **Manifest:** `examples/analog-db/templates/current_mirror/manifest.yaml`
  (`family: current_mirror`, schema `spicexplorer/subcircuit-template-library@1`); provenance
  already cites Aggarwal 2016.
- **Present (9 classes × {nmos sink, pmos source} = 18 templates):** `simple`, `cascode`,
  `wilson`, `improved_wilson`, `high_swing_cascode`, `improved_high_swing_cascode`,
  `low_voltage_cascode`, `selfbiased_high_swing_cascode`, `wide_swing`.
- **Naming note:** the 4-transistor double cascode is spelled `cascode` (there is no
  `4-transistor` label); Massier's `WSCCM` maps to the 4T `high_swing_cascode`, distinct from
  the 11T integrated-bias `wide_swing`.
- **Templateable gaps (pure-MOS):** `self_cascode`, `fvf`, `regulated_cascode`,
  `triode_simple`, `triode_cascode`, `level_shifted_{simple,cascode}`.
- **Blocked on matcher capability:** amplifier-containing families (hierarchical amp
  sub-template), bulk-driven (`match_bulk`), FGMOS (device model), multi-$V_T$
  (`match_models`/`match_params`).
