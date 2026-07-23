# Level Shifter (`ls`)

> **Family/class:** cascode sub-motif (no standalone template) · **Polarity:** nmos / pmos ·
> **Roles emitted:** its devices surface as `cascode_device` inside a mirror
> **Sources:** Massier 2008 (eqs. 31–32)

The level shifter provides a **constant (equal) voltage difference between the two
transistors' source pins** — the element that lets a cascode present equal drain-source
voltages to the mirror below it. It appears inside the cascode mirror (`CCM`), improved
Wilson mirror (`IWCM`), and the upper devices of the 4-transistor mirror (`4TCM`). Layout
follows [design-rules index](README.md).

## 1. Function

Provide a constant differential voltage between — or equal voltages at — the two
transistors' source pins. Realizable with a single transistor (source follower, or
diode-connected), but as a pair it forces the fixed offset that equalizes a mirror's $v_{ds}$.

## 2. Structure & recognition

- Two same-polarity MOSFETs stacked above a mirror pair; each level-shifter device's
  **source sits on an internal net** (the mirror device's drain), not the supply rail.
- The matcher labels such a stacked device `cascode_device` — the level shifter is not
  recognized as an independent block but as the cascode devices of the enclosing mirror.
- In cascode templates its widths are **pinned to the mirror widths** (see `CCM`).

## 3. Sizing rules

Both transistors act as `vccs` (saturation) — see
[device roles (vccs/vcres)](device_roles.md).
Level-shifter rules (Massier eqs. 31–32):

| Rule | Constraint | Purpose |
|---|---|---|
| **FG** | $l_1 = l_2$ | Equal length → avoid systematic mismatch |
| **RE** | $v_{gs_{1,2}} - V_{th_{1,2}} \ge V_{gs_{min}}$ | Sufficient overdrive → robust to local mismatch |

## 5. Design intuition & trade-offs

The level shifter is the "voltage-matching" companion to the current mirror: where the
mirror forces equal *currents*, the level shifter forces a fixed *voltage* offset between
source pins. Because it almost always equalizes the $v_{ds}$ of the mirror below it, its
widths are typically pinned to the mirror's widths when folded into a cascode
(`CCM` rules, eqs. 39–40 in
[current mirrors](current_mirror/rules/current_mirror.md)).

## 6. Template mapping

No standalone `analog-db` template — the level shifter is embedded in the cascode /
high-swing / 4-transistor mirror templates, and its devices carry the `cascode_device`
structural role.
