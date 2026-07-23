# symbol-templates/ — fixed template symbols

Per the OTA-vs-opamp convention in ../README.md. **Owner decision (PR #37):
one-size-fits-all is NOT the goal — specialized cores keep their own bespoke
symbols with whatever bias/clock pins they need. These templates are WRAPPER
symbols**: the fixed face of a *biased* amplifier block (core + its bias
cells drawn inside a wrapper .sch), which is exactly the form the landed
circuits/ entries take (drawn Vb/ibias PORTS become internal knob sources —
instantiator-owns-bias, plan D3/D4) and the form the P4 composer instantiates.
Core symbol = free pinout; wrapper symbol = this contract.

**DRAWN 2026-07-16 by the owner** under `ota-fully-diff/`; **`ota-single-ended/`
added 2026-07-20**. Each family is base + 0b..4b bias-pin counts (fully-diff also
has a `_chop` variant per count adding `vctl vctl_not`), stamped by
`gen_symbols.py`.

## Pin order — matches the LANDED corpus (⚠ read before landing a block)

```
ota-fully-diff/     vinp vinn voutp voutn [vb1..vbN] [vctl vctl_not] vdd vss
ota-single-ended/   vdd vout vinp vinn   [vb1..vbN]                  vss
```

The class testbench templates bind `${PORT_LINE}` **POSITIONALLY** to
`circuit.yaml ports`, so symbol order and entry order must agree or the block is
silently mis-wired. Both families were re-cut **2026-07-20** to match the landed
corpus exactly, audited across `circuits/*/circuit.yaml`:

| corpus order | count | family |
|---|---|---|
| `[vinp, vinn, voutp, voutn, vdd, vss]` | 8 entries | `ota-fully-diff` |
| `[vdd, vout, vinp, vinn, ibias, vss]` | 3 entries | `ota-single-ended` |

Lowercase `vdd`/`vss` is the corpus norm (63 lowercase vs 2 uppercase). Extras
(bias, chopper) splice in immediately **before the trailing supply pin(s)**, which
is why `vb1` lands exactly where `ibias` sits in the landed single-ended entries.

**⚠ What changed and why.** Until 2026-07-20 the drawn fully-diff symbols were
`vinp vinn voutn voutp VSS VDD` — outputs swapped and supplies uppercase relative
to all 8 landed entries. That divergence was the documented "opposite-polarity
feedback" footgun. It was safe to re-cut because **no schematic instantiated the
templates yet** (verified by grep across the repo), so no landed entry's loop sign
was affected. Any block drawn from an older copy of these symbols must be
re-checked against the table above.

**⚠ Two competing ordering mechanisms.** xschem expands `@pinlist` in B-box
**file order** — *unless* the pins carry `sim_pinnumber`, which overrides it.
A symbol with `sim_pinnumber` will ignore any reordering of its B-boxes. These
templates deliberately carry **no** `sim_pinnumber`; keep it that way so file
order is the single source of truth. (This bit the ldo-005 `ref_amp.sym`
migration — the boxes moved, the numbers travelled with them, and the emitted
port order did not change.)

## Files

- `ota-fully-diff/ota_fully_diff_{0b..4b}.sym` — OTA wrapper, N bias pins.
- `ota-fully-diff/ota_fully_diff_{0b..4b}_chop.sym` — …+ `vctl vctl_not`.
- `ota-single-ended/ota_single_ended_{0b..4b}.sym` — single-ended wrapper, N bias pins.
- `gen_symbols.py` — stamps the variants from each family's hand-drawn base.

```bash
python gen_symbols.py                          # all families
python gen_symbols.py --family ota-single-ended
```

**Fixed 2026-07-20:** the generator had been unrunnable since the symbols were
moved into `ota-fully-diff/` — it looked for the base one directory up and threw
`FileNotFoundError`. That is why the previously-noted label nit (variants carrying
`T {@symname} 11 -26` while the base used `11 -16`) could never be resynced;
regenerating from the current bases cleared it.

## Still-placeholder faces

`ota_ideal.sym` (behavioral macromodel, knob names
gm_val/rout_val/cout_val/rin_val/cin_val — baselines in _shared/IDEAL_AMP.md) is
not drawn yet. Existing family symbols (two-stage-ota-core.sym,
two-stage-opamp-core.sym, integrator-switchcap-opamp.sym, ideal-amp-fully-diff.sym)
migrate to these on each block's next edit — no bulk retrofit required.
