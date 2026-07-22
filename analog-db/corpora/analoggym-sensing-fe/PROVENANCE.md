# AnalogGym "Sensing Front End" corpus — provenance

Source material for the six **`kind: reference`** `sfe_*` circuits. Like the `ferrosim_*`
corpus (and unlike the verifiable `analoggym_*` LDOs), these are **not lowered to an open PDK
and not simulated** by this DB — they are proprietary-PDK Spectre/HSPICE decks, indexed for
reference/eval only. The harness runs the reference-only Tier-0 (schema + provenance +
deck-exists) and skips T1–T4.

## Upstream

**CODA-Team/AnalogGym** (`https://github.com/CODA-Team/AnalogGym`), BSD-3-Clause
(see [LICENSE.AnalogGym](LICENSE.AnalogGym)). The **"Sensing Front End"** category ships a
mix of sub-threshold voltage-reference / PTAT temperature-sensor cores and one readout
amplifier. A local snapshot lives in the meta-repo at
`external/AnalogGym-remainder/Sensing Front End/`.

> ⚠️ These designs target **proprietary TSMC PDKs** (0.18 µm BCD-HV `c018bcd_gen2_v1d6_usage.l`
> and 65 nm), using `nch_mac`/`pch_mac` devices. The PDK model libraries are **not** vendored;
> foundry include paths in the testbenches are stubbed as `${PDK_ROOT}/…` placeholders (D-9
> policy). No PDK model bytes are reproduced here.

## Imported circuits

| DB circuit | Upstream file(s) | Node | Testbench? |
|---|---|---|---|
| `sfe_reference_core_library` | `topology.txt` — 26 `front_end_*` reference/PTAT cores | 180 nm | — |
| `sfe_ptat_sensor_2t` | `PTAT_SENSOR` + `TB_2T_sensor_core.sp` | 180 nm | ✅ HSPICE (TC/LSB/Iq/line-sens/PSRR/noise) |
| `sfe_ptat_classic` | `ptat_classic` (PTAT_CLASSIC) | 180 nm | — |
| `sfe_ptat_65_classic` | `PTAT_65_classic1` | 65 nm | — |
| `sfe_ptat_sized_variants` | `spectre_ptat1..4` (ptat_1..4) | 180 nm | — |
| `sfe_smcnr_2stage_amp` | `SMCNR_SE_2st_AMP` + `TB_AC_/TB_TRAN_SMCNR_…sp` | 180 nm | ✅ HSPICE (gain/GBW/PM/CMRR/PSRR/Vos/slew, PVT) |

Each circuit's decks live under `circuits/<id>/spectre/<node>/netlist/{dut,tb}/` and are
indexed in the top-level [`catalog.json`](../../catalog.json). Only the `.scs` DUT decks are
indexed by the catalog; the HSPICE `.sp` testbenches sit beside them as provenance.

## Dialects & fidelity

The upstream folder mixes two netlist dialects:

- **Spectre** (`subckt … ends`, parenthesised nodes): `topology.txt`, `spectre_ptat*`,
  `PTAT_65_classic1` → copied **verbatim** to `dut/*.scs`.
- **HSPICE** (`.SUBCKT`, `xm…`, `.lib/.measure/.lstb/.check slew/.alter`): `PTAT_SENSOR`,
  `ptat_classic`, `SMCNR_SE_2st_AMP` and all three testbenches. For these three DUTs the
  verbatim original is preserved as `dut/<name>.orig.sp`, and a faithful Spectre rendering
  is authored as `dut/<name>.scs` (the catalog record). The testbenches are preserved
  verbatim as `tb/*.sp` (foundry `.lib` paths stubbed; the amp's `.include` repointed at the
  local `.orig.sp`).

  > These `.scs` renderings are an **interim shim** so each reference binding has the `.scs` DUT
  > that Tier-0 requires today. Once the platform gains first-class Spectre **and** HSPICE
  > `NetlistView` support, the DUT-of-record can point straight at the verbatim originals and the
  > renderings can be retired.

## Completeness & redundant copies (nothing left behind)

**Every one of the 17 upstream files is transferred verbatim** (the three testbenches modulo the
`${PDK_ROOT}` path stub above). The redundant copies are preserved too — filed under each binding's
`other/` bucket so they don't clutter the primary `dut/` list:

- `front_end_{11_6T,25_6T,31_3T,42_2_2015_REF}_schematic` — standalone single-cell exports,
  byte-identical to cells already inside `topology.txt` → `sfe_reference_core_library/…/other/`.
- `spectre_ptat6` — byte-identical duplicate of `spectre_ptat2` (both define `ptat_2`; no `ptat_5`
  exists) → `sfe_ptat_sized_variants/…/other/`.

Note: `topology.txt` itself defines `front_end_28_4T_schematic` **twice** (a bulk-connection
variant) — both are preserved verbatim inside `topology.scs`; the name collision is flagged in the
core-library circuit's README.

## What these are (not signal front-ends)

Despite the "Sensing Front End" label, the 33 cores are overwhelmingly **self-biased voltage
references and PTAT temperature-sensor cores** (2–7 stacked MOSFETs, using ZVT/HVT/substrate-tie
tricks; the upstream design notes are in Chinese and preserved verbatim). `SMCNR_SE_2st_AMP` is
the actual readout **amplifier** and is filed under `class: amplifier`.
