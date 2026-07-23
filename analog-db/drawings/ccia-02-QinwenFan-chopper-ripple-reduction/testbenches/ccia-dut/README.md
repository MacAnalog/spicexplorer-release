# ccia-02 testbenches (xschem)

Hand-runnable xschem testbenches for the **RRL-connected CCIA**
(`ccia-dut-chopper-w-positive-feedback-rrl.sch`).

> **No AC benches here.** Plain `.ac` linearizes around a frozen DC operating point with
> the choppers/SC switches stuck in one state, so it is *not* the real (time-varying)
> response of a chopper/switched-cap circuit. The `ac_closed_loop_chopper_diff`,
> `ac_zin_chopper_diff`, `ac_cm_reg` and `ac_cm_reg_cmfb` benches were **removed** for that
> reason. The correct analyses are **transient** (native/ngspice, below) or **PSS+PAC**
> (Spectre — as `circuits/ia_002`/`ia_003` already use: `pac_gain`/`pac_zin`/`pnoise_chopped`).
> Block-level AC on the *continuous* opamps (`amp_026` core, `amp_027` RRL integrator opamp)
> is still valid and lives under the sibling block-bench dirs.

Each `.sch` carries its `.param` set split **one block per level of the DUT hierarchy**,
so a block can be re-sized without hunting through a single wall of params:

| code block | drives |
|---|---|
| `PARAMS_BENCH` | the analysis bindings (`VDD`, `VCM`, `CL`, `FCHOP`, …) |
| `PARAMS_TOP` | `ccia-dut-chopper-w-positive-feedback-rrl.sch` — Cin/Cfb/Cpf/Rb, `vb<n>_main` |
| `PARAMS_CORE_OPAMP` | `two-stage-opamp-core[-w-stage-breakout].sch` (= `amp_026`) |
| `PARAMS_RRL_OPAMP` | `integrator-switchcap-opamp.sch` (= `amp_027`) |
| `PARAMS_RRL_SC` | `rrl-switched-capa-integrator.sch` (= `sup_003`) + the behavioural Gm cell |
| `PARAMS_SWITCH` | `../../shared/transmission_gate_pair.sch` — every chopper + SC switch |
| `COMMANDS` | `.control` — the analysis + its `.meas` set |
| `MODELS` | IHP corner libs + `.temp` |

## Layout convention

All follow the hand-placed layout of `tran_zin_chopped.sch`:

- **DUT** centre-right at `(1015,-725)`.
- **Pin labelling**: the `lab_wire` sits *at* the DUT pin, with a wire stub running out
  to its source. Connection is by net **name** — the wires are visual aids, so a few
  units of gap between a stub and a pin is harmless.
- **Clock pins** drop vertically out of the DUT bottom to staggered depths (30 units
  apart) so the labels don't collide.
- **Clock sources** run along the bottom in a row (in / out / pf / fb, left to right),
  each complement stacked above its mate; the SC phases sit at mid-left.
- **`.param` blocks** form a right-hand column, one per DUT hierarchy level.
- **`COMMANDS`** top-left, **`MODELS`** bottom-centre, **launcher** bottom-right.
- **Graph boxes** span the top band between the COMMANDS block and `PARAMS_BENCH`.

## Waveform plotting

Three mechanisms, all driven off the same `.raw`:

1. **Schematic graph boxes** (`B 2 … {flags=graph …}`), auto-populated by the
   **Simulate + load waves** launcher. That launcher is
   `xschem netlist; simulate [list xschem raw_read <raw> <type>]` — `simulate` takes a
   callback that fires when the run finishes, so one click netlists, simulates, and
   fills the graphs. A second **Load waves** launcher re-reads an existing `.raw`
   without re-simulating.
2. **`hardcopy … .svg`** in `.control` — renders without a display, so this is the one
   that works under `ngspice -b`. Each bench drops `<bench>_<what>.svg` next to the raw.
3. **`plot`** in `.control`, for an interactive ngspice session.

> **`plot` cannot work in batch.** `ngspice -b` answers
> `command 'plot' is not available during batch simulation, ignored!` and suggests
> Gnuplot (not installed here). That warning is expected and harmless — it is why
> `hardcopy` is there alongside it. To get `plot` windows, run the deck interactively
> (`ngspice <bench>.spice`, no `-b`), or just use the graph boxes.

Every derived trace is materialised as a *named vector* in `.control` (`let gdb =
db(vodm)`, `let izp = i(vzp)`, …) and graphed by plain name. xschem needs an RPN
expression like `vodm db20()` wrapped in escaped quotes inside `node="…"`; naming the
vector instead sidesteps that entirely and makes the same trace available to `plot`.

There is deliberately **no `quit`** at the end of `.control` — it would tear down the
plot windows before they can be looked at. `write <file>.raw` still finalises the raw
without it (a *bare* `write` does not — that is the known ngspice trap).

`save` is an explicit per-bench list on the transients rather than `save all`: on the
8 ms / 200 ns run over this hierarchy `save all` writes a **338 MB** raw. The targeted
list brings that to ~20 MB (and `tran_zin_chopped` from 338 MB to 2.7 MB).

## Running one

```bash
export PDK_ROOT=$HOME/local/pdks PDK=ihp-sg13g2
cd drawings
xschem -n -s -q --rcfile "$PWD/xschemrc" -o <outdir> \
  ccia-02-QinwenFan-chopper-ripple-reduction/testbenches/<bench>.sch
cd <outdir> && ln -sf $PDK_ROOT/ihp-sg13g2/libs.tech/ngspice/models/* .
ngspice -b <bench>.spice
```

## The benches

| bench | template | produces |
|---|---|---|
| `dc_op_chopper_diff` | ia/dc_op_chopper_rrl | `i_supply` `vos` `vocm` |
| `tran_chopper_ripple_rrl` | ia/tran_chopper_ripple_rrl | `v_ripple_pp` `v_ripple0_pp` `gain_cl` `vos_residual` |
| `tran_zin_chopped` | ia/tran_zin_chopped | `zin_chop_ohm` |

(`gain_cl_db`/`bw_cl_hz`/`hpf_hz`/`zin_ohm` used to come from the removed AC benches —
they belong on the PSS+PAC/Spectre lane now, not native ngspice.)

`clk_CHrrl`/`clk_CHrrl_not` are labelled onto the **`clk_chout` nets**, matching
`ia_004`'s `composition.yaml` (`clk_ch_rrl: clk_chout`) — the RRL chopper rides the
output chopper's clock, so there is no separate source for it.

## Sizing — the drawings are parameterized

The drawings used to hardcode every device at `w=0.15u l=0.13u` and every cap at `1p`,
i.e. a min-size topology skeleton. Simulated as-drawn it gives **−31.6 dB** where the
entry records **+25.7 dB**. Param names match
`circuits/ia_004_fan_chopper_rrl/pdk/ihp-sg13g2/sizing.yaml`, with matched pairs resolved
through `abstract/params.yaml`'s tying groups, so each block's params block is a direct
transcription of the entry's sizing.

### Switches are at the PDK floor and NOT sized

`PARAMS_SWITCH` holds every chopper (in/fb/out/pf/rrl) and every RRL SC switch at
`w=0.18u l=0.13u` — the `_shared/pdk/ihp-sg13g2.yaml` `geometry.min_w`/`min_l`. This is a
deliberate "not sized yet" placeholder, and it is one edit to change.

Measured cost of the floor vs the corpus's authored `2u/0.13u`:

| bench | `w=2u` | `w=0.18u` (current) |
|---|---|---|
| `ac_closed_loop` (gm=0) `gain_cl_db` | 25.711 dB | 25.706 dB |
| `ac_closed_loop` (gm=0) `hpf_hz` | 32.433 Hz | 32.397 Hz |
| `tran_zin_chopped` | completes, 21.37 MΩ | **aborts at 2.7 µs** |
| `tran_chopper_ripple_rrl` | aborts at 1.000 ms | aborts at 2.7 µs |

So the floor is free for the frozen-clock AC/DC benches (<0.01 dB) but it makes the
**clocked** benches diverge ~370× sooner. Both abort on the same node
(`x_ccia_opamp.net1`, the core's PMOS tail) — the root cause is the missing CMFB below,
not the switch size, but bigger switches buy a lot more runway before it bites.

> `shared/transmission_gate_pair.sch` is shared with **ccia-01 and bio-afe**. Their
> testbenches will need `tg_n_w/tg_n_l/tg_p_w/tg_p_l` defined too.

## Verified against the recorded baseline

> **Caveat (kept as historical record):** the `gain_cl_db`, `hpf_hz`, `bw_cl_hz` and
> `zin_ohm` rows below were produced by the now-removed **frozen-switch AC** benches, which
> do not properly apply to this chopper (see the banner at the top). They need re-deriving
> via PSS+PAC before they can be trusted. The **`vocm`** (DC) and **`zin_chop_ohm`**
> (transient) rows stand. Note `circuits/ia_004`'s recorded baseline is itself AC-based and
> carries the same caveat — it should move to PAC like `ia_002`/`ia_003`.

With the RRL's behavioural gm cell nulled (`gm_val=0`), switches at the PDK floor:

| metric | this TB | recorded | Δ |
|---|---|---|---|
| `gain_cl_db` | 25.706 dB | 25.71322 (ia_004) | 0.007 dB |
| `peaking_db` | 0.070 dB | — (flat, as expected) | — |
| `hpf_hz` | 32.397 Hz | 32.44218 (ia_004) | 0.14 % |
| `bw_cl_hz` | 2.0809 MHz | 2.100179 (ia_003) | 0.9 % |
| `vocm` | 0.6096873 V | 0.6096373 (ia_004) | 8e-5 |
| `zin_ohm` † | 201.2 MΩ | 204.3625 (ia_004) | 1.5 % |
| `zin_chop_ohm` †‡ | 21.37 MΩ | 23.73692 M (ia_003) | 10 % |

† measured with `gm_val=10u` (the RRL affects these only as a load).
‡ at `w=2u`; does not complete at the PDK floor.

`bw_cl_hz` / `zin_chop_ohm` are compared against **ia_003**, not ia_004: this drawing is
*positive-feedback **+** RRL*, a combination no entry covers (ia_003 = PF only, ia_004 =
simple + RRL). `zin_chop_ohm` 21.4 MΩ against ia_002's 11.79 MΩ reproduces the documented
~2× PF Zin boost. `i_supply` (181.7 µA) sits between ia_003's 146.4 µA and ia_004's
219.5 µA, as it should.

## `tran_chopper_ripple_rrl` does not complete — the core has no CMFB

```
Timestep too small; time = 0.00460277, timestep = 2.5e-19:
  trouble with node "xdut.x_ccia_opamp.net1"      <- the core opamp's PMOS tail
tran simulation(s) aborted                         (~4.60 ms of 8 ms)
```

The bench now carries a **CM diagnostic** so this is a reported number rather than an
inference:

| measure | value |
|---|---|
| `vocm_min` | **0.0074 V** @ 405 µs |
| `vocm_max` | **1.1968 V** @ 4.52 ms |
| `vocm_a` (avg 3–4 ms) | 0.443 V (commanded: 0.6 V) |
| `vavga` (differential, 3–4 ms) | −2.4 nV |
| `v_ripple0_pp` | 2.31e-07 V |

The output common mode swings **rail to rail** while the differential output sits at
nanovolts. That is `DRAWING_REVIEW.md` §1's *"output common mode is BISTABLE under
clocking (a ~0.7 ms relaxation oscillation … flips vocm rail-to-rail)"* reproduced
directly.

**Do not read `v_ripple0_pp` = 0.23 µV as a good ripple result** — it is the signature of
a dead, railed output, not of a nulled ripple. `v_ripple_pp` / `vos_residual` need
window B (7–8 ms), which the run never reaches. All four figures need CMFB first — see
`CMFB_PLAN.md` next to this file.

### PF clock polarity matters more than it looks

Window A now completes (it did not before) because the PF chopper's two phases are wired
in the right order. Controlled A/B on the identical deck, swapping only `clk_chpf` /
`clk_chpf_not` on the `XDUT` line:

| PF phases | `tran_zin_chopped` |
|---|---|
| correct | aborts at **2.74 µs** |
| swapped | runs to **842.8 µs**, reports `zin_chop_ohm` 7.65 MΩ |

Inverting the PF path turns positive feedback into negative, which damps the un-CMFB'd
core and buys ~300× more runway — so a *swapped* build looks far healthier while being
wrong. The 7.65 MΩ it reports is below ia_002's no-PF 11.79 MΩ, which is the tell: a
working PF boost should push Zin *up* toward ia_003's 23.7 MΩ.

## Shape guard — why the AC numbers are now trustworthy

The ia closed-loop AC templates used to take `gain_cl_db` as `MAX` over the sweep, then
place the `−3 dB` corners around it. On a **peaked** response that reports the resonance
as "the gain" and puts `hpf_hz` up next to the peak. Fixed in
`_shared/classes/ia/testbench-templates/ac_closed_loop{_diff,_chopper_diff}.spice`:
the passband is read `FIND … AT=${FMID}` (defaulted to 1 kHz in `assemble.py`), and
`gain_peak_db` / `peaking_db` are emitted as the guard.

Flat responses are unaffected — re-running the entry benches after the change:

| circuit | `gain_cl_db` | recorded | `peaking_db` |
|---|---|---|---|
| ia_002 | 25.71312 | 25.71728 | **0.004 dB** (flat) |
| ia_003 | 25.71295 | 25.71720 | **0.004 dB** (flat) |
| ia_004 (phases now driven) | 22.691 | 25.71322 | **18.70 dB** (peaked) |

This drawing, same measurement: `peaking_db` **10.13 dB** with the RRL cell live,
**0.07 dB** with it nulled.
