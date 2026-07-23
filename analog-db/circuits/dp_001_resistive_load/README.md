# dp_001_resistive_load — resistively-loaded NMOS differential pair (current-mirror tail)

**Promoted** from the `ferrosim_differential_pair` reference entry (Arcadia-1/ferrosim, MIT). Class
`diff_pair` (new). Ports `vdd voutp voutn vinp vinn ibias vss`.

NMOS input pair (XMP/XMN) with ideal-resistor loads (RP/RN) and an NMOS current-mirror tail
(XMR reference ← external `ibias`; XMT tail). The upstream deck uses a plain resistor tail; the
promotion swaps in a mirror tail so the pair is **mirror-anchored** and `find_subcircuits` reports
both the pair and its mirror (a resistor-tailed pair is not flagged — the diff-pair template is
tail-anchored on a detected mirror).

- **Open-PDK bindings:** `ihp-sg13g2`, `sky130` (shared 1.5 V supply — a per-PDK `analysis_params`
  override is blocked by `sizing.schema.json`).
- `gf180mcu` binding added via `analog-db add-binding --from ihp-sg13g2` (untuned transfer; T3/T4 sim-smoke passes).
- **Analyses:** `dc_op` (tail current + output CM), `gain_dc` (differential DC gain).
- **Reference bindings:** original FOUNDRY-28nm + 65nm ferrosim decks under `spectre/{28nm,65nm}/`.
- **Structure:** `find_subcircuits` → `dp.nmos.simple` (XMP/XMN, tail mirror-biased) +
  `cm.nmos.simple` (XMR → XMT).

## Measured (tt, native ngspice-45, 1.5 V, Ibias 20 µA)

| metric | ihp-sg13g2 | sky130 |
|--------|-----------|--------|
| gain_dc (\|d(voutp−voutn)/d(vid)\|) | 5.3 V/V | 3.4 V/V |
| v_ocm | 1.23 V | 1.34 V |
| i_supply (tail + Ibias) | 45 µA | 35 µA |

Modest gain (bare pair, gm·R_load). Regenerate: `analog-db generate --circuit dp_001_resistive_load`.
