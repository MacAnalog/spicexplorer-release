"""Import the `ferrosim` corpus into analog-db as ``kind: reference`` circuits (plan D-9).

Source: ``Arcadia-1/ferrosim`` (author **Token Zhang**, MIT), vendored via ``netlist-crawler``. These
are proprietary-PDK (TSMC 28/65 nm) Spectre decks — indexed for reference/eval, NOT lowered or
simulated. Each upstream family becomes one ``circuits/ferrosim_<name>/`` circuit whose upstream deck
layout is preserved **verbatim** under a ``spectre/<node>/`` reference binding (so relative ``include``
paths stay intact). Provenance is recorded once in ``corpora/ferrosim/`` + the repo ``NOTICE``.

Point ``--src`` at the ferrosim ``tests/`` directory (the one holding ``decks/``, ``va_demo/``,
``sc_sample/``). Idempotent: an already-imported circuit dir is skipped, never clobbered.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

PROVENANCE = {
    "source": "Arcadia-1/ferrosim (imported via netlist-crawler)",
    "designer": "Token Zhang",
    "license": "MIT",
}

# (id, class, display, src subdir rel to --src, node)  -- whole subtree -> one binding
_FAMILIES: list[tuple[str, str, str, str, str]] = [
    ("ferrosim_amp5t", "amplifier", "5-transistor diff-to-single amp (ferrosim)", "decks/amp5t", "28nm"),
    ("ferrosim_biquad", "filter", "High-speed OTA biquad filter (ferrosim)", "decks/biquad", "28nm"),
    ("ferrosim_comparator", "comparator", "StrongARM comparator + offset trim (ferrosim)", "decks/comparator", "28nm"),
    ("ferrosim_inbuf", "buffer", "Cascode input buffer (ferrosim)", "decks/inbuf", "28nm"),
    ("ferrosim_opamp", "opamp", "Fully-differential two-stage opamp (ferrosim)", "decks/opamp", "28nm"),
    ("ferrosim_refbuf", "reference", "Push-pull reference buffer (ferrosim)", "decks/refbuf", "28nm"),
    ("ferrosim_restrim", "trim", "16-step thermometer resistor trim (ferrosim)", "decks/restrim", "28nm"),
    ("ferrosim_sampling_bts", "sampler", "Bottom-plate bootstrapped sampler (ferrosim)", "decks/sampling_bts", "28nm"),
    ("ferrosim_sar", "adc", "11-bit SAR ADC, with-MOS variant (ferrosim)", "decks/sar", "28nm"),
    ("ferrosim_sc_counter", "digital", "Programmable 4-bit counter (ferrosim)", "decks/sc_counter", "28nm"),
    ("ferrosim_sc_ring", "oscillator", "LVT ring oscillator (ferrosim)", "decks/sc_ring", "28nm"),
]

# (id, class, display, base, [node labels])  -- flat ported decks decks/ported/<base>_<n>.scs
_PORTED: list[tuple[str, str, str, str, list[str]]] = [
    ("ferrosim_bandgap_core", "reference", "Bandgap core (ferrosim, ported from circuit-bench)", "bandgap_core", ["28", "65"]),
    ("ferrosim_bjt_cal", "characterization", "BJT calibration bench (ferrosim, ported)", "bjt_cal", ["28"]),
    ("ferrosim_common_source", "amplifier", "Common-source amp (ferrosim, ported)", "common_source", ["28", "65"]),
    ("ferrosim_differential_pair", "amplifier", "Differential pair (ferrosim, ported)", "differential_pair", ["28", "65"]),
    ("ferrosim_hyst_comparator", "comparator", "Hysteresis comparator (ferrosim, ported)", "hyst_comparator", ["28", "65"]),
    ("ferrosim_ldo", "ldo", "LDO regulator (ferrosim, ported)", "ldo", ["28", "65"]),
    ("ferrosim_lfsr8", "digital", "8-bit LFSR (ferrosim, ported)", "lfsr8", ["28"]),
    ("ferrosim_pga_16step", "amplifier", "16-step programmable-gain amp (ferrosim, ported)", "pga_16step", ["28"]),
    ("ferrosim_source_follower", "buffer", "Source follower (ferrosim, ported)", "source_follower", ["28", "65"]),
    ("ferrosim_two_stage_opamp", "opamp", "Two-stage opamp (ferrosim, ported)", "two_stage_opamp", ["28", "65"]),
]

# (id, class, display, [glob patterns rel to --src], node|None, binding_dir)
_FILES: list[tuple[str, str, str, list[str], str | None, str]] = [
    ("ferrosim_transistor_char", "characterization", "Transistor gm/Id, DIBL, Ron sweeps (ferrosim)", ["decks/transistor_char/*.scs"], "28nm", "spectre/28nm"),
    ("ferrosim_bsimbulk_iv", "characterization", "BSIM-Bulk NMOS/PMOS IV benches (ferrosim)", ["decks/bsimbulk/*.scs"], "28nm", "spectre/28nm"),
    ("ferrosim_cap_meas", "characterization", "Capacitance measurement bench (ferrosim)", ["decks/cap_meas.scs"], "28nm", "spectre/28nm"),
    ("ferrosim_sc_integrator", "filter", "Switched-cap integrator (ferrosim)", ["decks/sc_integrator.scs"], "28nm", "spectre/28nm"),
    ("ferrosim_ring5", "oscillator", "5-stage ring oscillator (ferrosim)", ["decks/ring5.scs"], "28nm", "spectre/28nm"),
    ("ferrosim_ldo_sample", "ldo", "LDO sample deck (ferrosim)", ["decks/ldo.scs"], "28nm", "spectre/28nm"),
    ("ferrosim_sc_sample", "sampler", "Switched-cap sample deck (ferrosim)", ["sc_sample/sc_sample.scs"], "28nm", "spectre/28nm"),
    ("ferrosim_va_demo", "demo", "Verilog-A primitive demos (ferrosim)", ["va_demo/*.scs"], None, "spectre/va"),
    ("ferrosim_va_decl_init", "demo", "Verilog-A declaration/init demo (ferrosim)", ["decks/va_decl_init.scs"], None, "spectre/va"),
]

_BANNER = (
    "# ★ SUPER-DSL manifest — kind: reference (plan D-9). Validated against "
    "_shared/schema/circuit.schema.json.\n"
    "# IMPORTED reference circuit: authored proprietary-PDK Spectre decks, NOT lowered or simulated "
    "in this DB.\n"
    "# The harness runs the reference-only T0 subset (schema + provenance + deck-exists) and skips "
    "T1-T4.\n"
    "# Source credited under `provenance` (see repo NOTICE + corpora/ferrosim/PROVENANCE.md).\n"
)


def _binding(node: str | None, dir_: str) -> dict[str, Any]:
    b: dict[str, Any] = {"tool": "spectre", "dir": dir_}
    if node:
        b["node"] = node
    return b


def _count_decks(cdir: Path) -> int:
    return sum(1 for _ in cdir.rglob("*.scs"))


def _write_manifest_and_readme(
    cdir: Path, cid: str, cls: str, display: str, references: list[dict[str, Any]]
) -> None:
    manifest = {
        "schema": "spicexplorer/circuit@1",
        "id": cid,
        "kind": "reference",
        "class": cls,
        "display_name": display,
        "provenance": dict(PROVENANCE),
        "references": references,
        "status": "reference",
    }
    body = yaml.dump(manifest, sort_keys=False, default_flow_style=False, width=100)
    (cdir / "circuit.yaml").write_text(_BANNER + body)

    bind_rows = "\n".join(
        f"| `{b['dir']}` | {b.get('tool', 'spectre')} | {b.get('node', '—')} |" for b in references
    )
    (cdir / "README.md").write_text(
        f"# {cid} — {display}\n\n"
        "**kind: reference** (plan D-9) — imported proprietary-PDK Spectre circuit. Indexed for "
        "reference/eval; **not lowered to an open PDK and not simulated here** (reference-only "
        "Tier-0, skips T1–T4).\n\n"
        "- **Source:** [`Arcadia-1/ferrosim`](https://github.com/Arcadia-1/ferrosim), imported via "
        "`netlist-crawler`. Author: **Token Zhang**. License: **MIT** "
        "(see repo `NOTICE` + [`../../corpora/ferrosim/PROVENANCE.md`](../../corpora/ferrosim/PROVENANCE.md)).\n"
        f"- **Class:** `{cls}` · **decks:** {_count_decks(cdir)} `.scs` file(s), upstream layout "
        "preserved verbatim.\n\n"
        "## Bindings\n\n"
        f"| Binding | Tool | Node |\n|---|---|---|\n{bind_rows}\n\n"
        "Proprietary-PDK includes are stubbed as `${PDK_ROOT}`/`${CADENCE_ROOT}` placeholders; open in "
        "a Spectre environment with the real PDK bound.\n"
    )


def import_all(src: Path, dest_circuits_root: Path) -> tuple[list[str], list[str]]:
    """Import every ferrosim family under ``src`` (the ferrosim ``tests/`` dir) into ``dest``.

    Returns ``(imported ids, skipped notes)``. Existing circuit dirs are skipped (never clobbered).
    """
    imported: list[str] = []
    skipped: list[str] = []

    # families: copy the whole subtree verbatim into one 28 nm binding
    for cid, cls, display, subdir, node in _FAMILIES:
        cdir = dest_circuits_root / cid
        srcdir = src / subdir
        if cdir.exists():
            skipped.append(f"{cid} (exists)")
            continue
        if not srcdir.is_dir():
            skipped.append(f"{cid} (source {subdir} missing)")
            continue
        shutil.copytree(srcdir, cdir / "spectre" / node)
        _write_manifest_and_readme(cdir, cid, cls, display, [_binding(node, f"spectre/{node}")])
        imported.append(cid)

    # ported: one flat deck per node at the binding root
    for cid, cls, display, base, nodes in _PORTED:
        cdir = dest_circuits_root / cid
        if cdir.exists():
            skipped.append(f"{cid} (exists)")
            continue
        refs: list[dict[str, Any]] = []
        for n in nodes:
            srcfile = src / "decks" / "ported" / f"{base}_{n}.scs"
            if not srcfile.is_file():
                continue
            node = f"{n}nm"
            bdir = cdir / "spectre" / node
            bdir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(srcfile, bdir / srcfile.name)
            refs.append(_binding(node, f"spectre/{node}"))
        if not refs:
            if cdir.exists():
                shutil.rmtree(cdir)
            skipped.append(f"{cid} (no source decks)")
            continue
        _write_manifest_and_readme(cdir, cid, cls, display, refs)
        imported.append(cid)

    # files: a set of loose decks into one binding dir
    for cid, cls, display, patterns, node, bdir_rel in _FILES:
        cdir = dest_circuits_root / cid
        if cdir.exists():
            skipped.append(f"{cid} (exists)")
            continue
        bdir = cdir / bdir_rel
        bdir.mkdir(parents=True, exist_ok=True)
        n_copied = 0
        for pat in patterns:
            for srcfile in sorted(src.glob(pat)):
                shutil.copy2(srcfile, bdir / srcfile.name)
                n_copied += 1
        if not n_copied:
            shutil.rmtree(cdir)
            skipped.append(f"{cid} (no source decks)")
            continue
        _write_manifest_and_readme(cdir, cid, cls, display, [_binding(node, bdir_rel)])
        imported.append(cid)

    return imported, skipped
