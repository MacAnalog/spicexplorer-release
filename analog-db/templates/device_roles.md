# Current Source (`vccs`) & Resistor (`vcres`) — Level-0 Device Roles

> **Family/class:** device role (not a standalone template) · **Polarity:** nmos / pmos ·
> **Roles emitted:** the matcher labels these in context (`current_mirror`,
> `tail_current_source`, …) rather than as a distinct role
> **Sources:** Massier 2008 (eqs. 16–26)

The two Level-0 roles: a single transistor biased as a voltage-controlled current source
(saturation) or as a voltage-controlled resistor (triode). Every higher-level block is
built from transistors in one of these roles, so these rules are inherited throughout.
Layout follows [design-rules index](README.md).

## 1. Function

- **`vccs`** — deliver a constant, bias-set drain current (mirror legs, tail sources, active
  loads). Value set by bias point and geometry.
- **`vcres`** — behave as a switch or tunable resistor (e.g. the lower devices of a
  4-transistor mirror).

## 2. Structure & recognition

Single MOSFET; the *role* is inferred from context, not standalone topology:

- **`vccs`** — drain on a non-rail (signal) net, source on a supply rail or tail; typically
  a mirror output or tail device. The matcher flags it via the enclosing block (a device
  whose drain sits on a diff-pair `CM_tail` net becomes `tail_current_source`).
- **`vcres`** — appears inside cascode/triode mirrors as a device held in the linear region.
- Region (saturation vs. triode) is **bias-dependent**, so it can only be *predicted* from
  topology, never confirmed by connectivity alone.

## 3. Sizing rules

**`vccs` — saturation** (Massier eqs. 18–23). The relative drain-current variance (eq. 17)
grows with terms $\propto 1/(W L)$ (area matching / $1/f$ noise), $1/W^2$, $1/L^2$, and
$1/(v_{gs}-V_{th})$ — so robustness needs minimum width, length **and area** well above the
process minimums:

| Rule | Constraint | Purpose |
|---|---|---|
| **FE1** | $v_{ds} - (v_{gs} - V_{th}) \ge V_{sat_{min}}$ | Stay in saturation with margin |
| **FE2** | $v_{ds} \ge 0$ | Correct drain polarity |
| **FE3** | $v_{gs} - V_{th} \ge 0$ | Transistor on (inverted) |
| **RG1** | $w \cdot l \ge A_{min_{SAT}}$ | Minimum area — matching / $1/f$ noise |
| **RG2** | $w \ge W_{min_{SAT}}$ | Minimum width for robustness |
| **RG3** | $l \ge L_{min_{SAT}}$ | Minimum length for robustness |

**`vcres` — linear/triode** (Massier eqs. 24–26):

| Rule | Constraint | Purpose |
|---|---|---|
| **FE1** | $(v_{gs} - V_{th}) - v_{ds} \ge V_{lin_{min}}$ | Stay in the linear region with margin |
| **FE2** | $v_{ds} \ge 0$ | Correct drain polarity |
| **FE3** | $v_{gs} - V_{th} \ge 0$ | Transistor on (inverted) |

## 5. Design intuition & trade-offs

The electrical rules pin the operating region; the geometric rules trade area for matching
and noise. A current source's whole value is set by its bias point and geometry, making it
the block most sensitive to mismatch — size it well above the minimums when it sets a
critical current. For a **deep** ohmic `vcres` (small, constant $R_{on}$), make $V_{lin_{min}}$
large — keep $v_{ds}$ well below the overdrive.

## 6. Template mapping

No standalone `analog-db` template — these are roles carried by devices inside mirror,
diff-pair, and cascode templates. The closest emitted structural role is
`tail_current_source` (a rail-sourced `vccs` feeding a diff-pair tail).
