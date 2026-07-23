# CMOS Transmission Gate

> **Family/class:** pass gate (`tg.pair.cmos`, class `pass_gate`) · **Polarity:** complementary
> (nmos ∥ pmos) · **Roles emitted:** `analog_switch` (both matched devices)
> **Sources:** design rules of thumb (CMOS switch design)

A complementary pass gate: an NMOS and a PMOS in parallel that pass a rail-to-rail analog
or digital signal when their complementary clocks are asserted. Layout follows
[design-rules index](../../README.md).

## 1. Function

Pass a signal from input to output with low, roughly constant on-resistance across the full
input range. Choosing the W/L ratio requires balancing three primary trade-offs:
on-resistance ($R_{ON}$), charge injection (and clock feedthrough), and parasitic
capacitance — which together set signal propagation delay and distortion. Optimal sizing
requires complementary sizing for rail-to-rail operation: size the NMOS at the minimum
channel length allowed by your technology node, and make the PMOS roughly 2× to 3× wider
than the NMOS to compensate for lower hole mobility and balance the rise/fall times.

## 2. Structure & recognition

- An **NMOS and a PMOS in parallel** — sources tied to the signal input net, drains tied to
  the output net (source/drain are interchangeable for a switch).
- Gates driven by **complementary clocks** (one net and its inverse).
- Registered as TWO templates (family manifest): the canonical bulk-blind `tg.pair.cmos`
  (body-tied netlist — the parallel n/p pair sharing both signal terminals with anti-phase
  gate control; recognises BOTH drawn bulk styles) and the bulk-strict `tg.pair.cmos_rail_bulk`
  (`match_bulk: true` — only fires when the host's bulks genuinely sit on the VSS/VDD rails,
  and then wins the primary label with `tg.pair.cmos` as its alternate).

## 3. Sizing rules

**Channel Length (L):** keep at the minimum feature size (e.g. $L_{min} = 180\text{ nm}$,
65 nm, etc.) for your technology node.

- **Why:** minimizing L reduces parasitic capacitance ($C_{gs}$, $C_{gd}$) and lowers the
  ON-resistance ($R_{on}$), maximizing speed. It also minimizes parasitic area.

**Channel Width (W) & $\frac{W_{p}}{W_{n}}$ ratio:** size the PMOS 2.5 to 3× wider than the
NMOS — typically $W_{P} \approx 2.5 \times W_{N}$ to $3 \times W_{N}$.

- **Why:** electrons (NMOS) are ~2.5× more mobile than holes (PMOS) — hole mobility is
  roughly half of electron mobility in standard CMOS. Making the PMOS wider balances the
  $R_{on}$ of both transistors, so the gate passes both Logic 0 and Logic 1 with equal
  strength and propagation delay. This symmetry keeps $R_{ON}$ relatively flat across the
  input range, minimizing Total Harmonic Distortion (THD).
- **Sizing up vs. down:** increase $W_{N}$ and $W_{P}$ to reduce $R_{ON}$ for high-speed
  sampling or heavy loads — but larger widths add parasitic capacitance.

## 5. Design intuition & trade-offs

**On-resistance ($R_{ON}$) and distortion.** To pass an analog signal without attenuation
or distortion, $R_{ON}$ must be low relative to the load impedance. Use the minimum channel
length and the complementary width ratio to both lower $R_{ON}$ and flatten it across the
input range.

**Charge injection and clock feedthrough.** When the gate turns off, the channel charge is
dumped into adjacent nodes (including the output), causing voltage spikes in the signal
path. The complementary clocks mean the charge injected by the NMOS and PMOS ideally cancel,
but because the transitions fall at slightly different times and the gate capacitances
differ, exact cancellation is hard. Rule of thumb: scale the PMOS/NMOS so their gate
capacitances roughly match, or use minimum-sized (smaller-width) gates where charge
injection into sensitive sample-and-hold nodes dominates.

**Parasitic capacitance (bandwidth).** Increasing W lowers $R_{ON}$ but proportionally
raises the drain/source parasitic capacitance, forming a low-pass filter at the output that
limits bandwidth. For high-frequency signals, run a transient simulation and size so the
$R_{ON}\times C_{load}$ (or $R_{ON}\times C_{parasitic}$) time constant sits well within the
signal bandwidth.

**Application tuning:**

- *Digital (multiplexers, latches):* minimize area/power at the minimum size that meets the
  delay spec. Large W/L cuts delay but loads the previous stage, which can degrade overall speed.
- *Analog switches:* keep $R_{on}$ small and constant over the full input range — use larger
  W (holding the 2.5–3× PMOS/NMOS ratio) to lower $R_{ON}$ and distortion, at the cost of area.

**Summary of rules of thumb:**

- Use minimum channel length ($L = L_{min}$) for speed and space.
- Size PMOS as $W_{P} \approx 2.5 \times W_{N}$ to equalize drive current and flatten the $R_{ON}$ curve.
- Size up for low $R_{ON}$ (large W), or down for low charge injection and capacitive loading (small W).

## 6. Template mapping

- **Templates:** `tg.pair.cmos` + `tg.pair.cmos_rail_bulk` in
  `templates/transmission_gate/manifest.yaml` (class
  `pass_gate`, polarity `complementary`, role `analog_switch`); loads in circuitgraph's
  `default_transmission_gate_library()` / merged `default_subcircuit_library()`.
- **Ports:** `a`/`b` (the interchangeable signal terminals), `ctl_n` (NMOS gate), `ctl_p`
  (complementary PMOS gate).
- **Bulk-blind aliasing — RESOLVED via per-template bulk matching:** the rail-bulk and
  body-tied drawings differ only in bulk ties, so under the detector's `match_bulk=off`
  default they are one topology (the rail variant's VSS/VDD are bulk-only nets and vanish
  from the signature). The catalogue now registers both: `tg.pair.cmos` stays bulk-blind
  (recall — matches either style), `tg.pair.cmos_rail_bulk` sets the manifest's
  `match_bulk: true` (precision — the drawn rail ties become part of its identity). On a
  rail-bulk host both fire on the same devices and the bulk-strict variant is preferred as
  the primary (`group_matches` equal-set collapse), the bulk-blind twin kept as alternate.
- **Roles emitted:** both matched devices → `StructuralRole.MOS_ANALOG_SWITCH`
  (`analog_switch`, deterministic ground truth).
