"""AnalogGym → analog-db importer (plan Phase 5).

Normalizes a CODA-Team AnalogGym amplifier (``Amplifier/spice_netlist/<Name>`` +
``Amplifier/design_variables/<Name>``) into a DB circuit directory:

  abstract/netlist.spice   AUTHORED-equivalent: PDK-neutral (sky130 device → nmos/pmos tokens),
                           canonical ports (gnda→vss, vdda→vdd), flat form (subckt markers
                           commented, top-level .end). The role-encoded design-variable symbols
                           (``MOSFET_..._gm1_PMOS`` etc.) + their arithmetic (``m='4*...'``) are
                           preserved verbatim — circuitgraph ingests + lowers them.
  pdk/sky130/{devices.map,sizing,corners}.yaml
  circuit.yaml             class/compensation/stages/ports/provenance from the folder name +
                           the analoggym-amplifiers skill mapping (BSD-3-Clause).
  datasheet.yaml           extract-only metrics (benchmark specs, skill §6) + conditions
                           (cload/vcm/ibias) read from design_variables. No symbolic (3-stage
                           netlist2tf ingest is deferred).

This is a dev-time tool (the produced circuit dirs are committed); it is not on any runtime path.
Provenance/classification is data-driven from ``_PAPER`` below (the skill's acronym→source table).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

# compensation acronym -> source paper (analoggym-amplifiers skill §4 / paper-benchmarks.md)
_PAPER: dict[str, str] = {
    "SMC": "Fan, Mishra, Sanchez-Sinencio, IEEE JSSC 40(3):584-592, 2005",
    "NMCF": "Leung & Mok, IEEE TCAS-I 48(9):1041-1056, 2001",
    "NMCNR": "Leung & Mok, IEEE TCAS-I 48(9):1041-1056, 2001",
    "DFCFC1": "Leung & Mok, IEEE TCAS-I 48(9):1041-1056, 2001",
    "DFCFC2": "Leung & Mok, IEEE TCAS-I 48(9):1041-1056, 2001",
    "AFFC": "H. Lee & P.K.T. Mok, IEEE JSSC 38(3):511-520, 2003",
    "RAFFC": "Grasso, Palumbo, Pennisi, IEEE TCAS-I 54(7):1459-1470, 2007",
    "ACBC": "X. Peng & W. Sansen, IEEE JSSC 39(11):2074-2079, 2004",
    "IAC": "Peng, Sansen, Hou, Wang, Wu, IEEE JSSC 46(2):445-451, 2011",
    "TCFC": "X. Peng & W. Sansen, IEEE JSSC 40(7):1514-1520, 2005",
    "CFCC": "S.S. Chong & P.K. Chan, IEEE JSSC 47(9):2227-2234, 2012",
    "CLIA": "M. Tan & W.-H. Ki, IEEE JSSC 50(2):440-449, 2015",
    "DACFC": "Song Guo & Hoi Lee, IEEE JSSC 46(2):452-464, 2011",
    "AZC": "Qu, Singh, Lee, Son, Cho, IEEE JSSC 52(2):517-527, 2017",
    "LEC": "Qu, Im, Kim, Cho, ISSCC 2014, pp. 290-291",
    "PFC": "J. Ramos & M. Steyaert, CICC 2002, pp. 333-336",
    "AZ": "Yan, Mak, Law, Martins, Maloberti, IEEE JSSC 50(10):2353-2366, 2015",
}

# AnalogGym single-objective benchmark specs (skill §6 / Eq. 5), restricted to metrics the
# universal/amplifier templates actually produce — extract-only, each `extract.meas` matches a
# template output (no symbolic: 3-stage param-arithmetic isn't netlist2tf-ingestible yet; the
# dedicated CMRR/PSRR/vos benches are deferred with their fragments).
_BENCHMARK_METRICS: dict[str, dict[str, Any]] = {
    "dc_gain_db": {"display": "DC open-loop gain", "unit": "dB", "analysis": "ac_open_loop",
                   "extract": {"meas": "dcgain"}, "spec": {"min": 100, "unit": "dB"}},
    "ugf_hz": {"display": "Unity-gain frequency", "unit": "Hz", "analysis": "ac_open_loop",
               "extract": {"meas": "ugf"}, "spec": {"min": "any", "unit": "Hz"}},
    "pm_deg": {"display": "Phase margin", "unit": "deg", "analysis": "ac_open_loop",
               "extract": {"meas": "pm"}, "spec": {"min": 45, "max": 90, "unit": "deg"}},
    "vn_in": {"display": "Input-referred noise", "unit": "V/sqrt(Hz)", "analysis": "noise",
              "extract": {"meas": "inoise_total"}, "spec": {"max": "any"}},
    "i_supply": {"display": "Supply current", "unit": "A", "analysis": "dc_op",
                 "extract": {"meas": "i_supply"}, "spec": {"max": "any"}},
    "t_settle": {"display": "Settling time", "unit": "s", "analysis": "tran_step",
                 "extract": {"meas": "t_settle"}, "spec": {"max": 1.0e-6, "unit": "s"}},
}
_ANALYSES = ["ac_open_loop", "dc_op", "noise", "tran_step"]

# Folders that import + schema/assembly-validate but don't yet load cleanly in ngspice (sim-gated
# stragglers). Marked status: incomplete + excluded from the sim tiers/baselines until fixed.
_SIM_INCOMPLETE = {
    "Tan_CLIA_Pin_3": "ngspice load error (model resolution) — under investigation",
}

# design-variable name prefixes → role (sizing knob vs operating condition)
_COND_EXACT = {"CLOAD": "cload", "VCM": "vcm"}


def parse_folder(name: str) -> dict[str, Any]:
    """`Leung_NMCNR_Pin_3` → {author, compensation, stages}. Raises on an unexpected shape."""
    m = re.fullmatch(r"(?P<author>[A-Za-z0-9]+)_(?P<comp>[A-Za-z0-9]+)_Pin_(?P<stages>\d+)", name)
    if not m:
        raise ValueError(f"unexpected AnalogGym folder name: {name!r}")
    return {"author": m["author"], "compensation": m["comp"], "stages": int(m["stages"])}


def _read_design_variables(path: Path) -> dict[str, str]:
    """Flatten the ``.PARAM`` continuation block into {NAME: value}."""
    text = path.read_text()
    body = re.sub(r"(?im)^\s*\.param\b", " ", text)         # drop the .PARAM keyword
    body = re.sub(r"(?m)^\s*\+", " ", body)                  # join continuation lines
    out: dict[str, str] = {}
    for tok in body.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def neutralize_netlist(raw: str, circuit_id: str) -> str:
    """sky130 device names → nmos/pmos; gnda/vdda → vss/vdd; subckt markers commented; +.end."""
    s = raw
    s = s.replace("sky130_fd_pr__pfet_01v8", "pmos").replace("sky130_fd_pr__nfet_01v8", "nmos")
    s = re.sub(r"(?i)\bgnda\b", "vss", s)
    s = re.sub(r"(?i)\bvdda\b", "vdd", s)
    lines = []
    for ln in s.splitlines():
        st = ln.strip().lower()
        if st.startswith(".subckt") or st.startswith(".ends"):
            lines.append("**" + ln)
        elif st and not st.startswith("*"):
            lines.append(ln)
        elif st.startswith("*"):
            lines.append(ln)
    header = (
        f"** {circuit_id} — AnalogGym import, PDK-neutral abstract (plan Phase 5).\n"
        "** sky130 device tokens → nmos/pmos; ports gnda→vss, vdda→vdd; role-encoded\n"
        "** design-variable symbols (MOSFET_*_<role>_<type>) + their arithmetic preserved.\n"
        "** Source: CODA-Team/AnalogGym (BSD-3-Clause). Subckt port order: vss vdd vinn vinp vout.\n"
    )
    return header + "\n".join(lines) + "\n.end\n"


def _split_design_vars(dvars: dict[str, str]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """(sizing variables, conditions). MOSFET_*/CAPACITOR_*/RESISTOR_* are knobs;
    CLOAD/VCM/CURRENT_*_BIAS are conditions."""
    knobs: list[dict[str, Any]] = []
    conds: dict[str, str] = {}
    for name, val in dvars.items():
        up = name.upper()
        if up in _COND_EXACT:
            conds[_COND_EXACT[up]] = val            # CLOAD/VCM are testbench-level conditions
        else:
            # everything else (MOSFET_*, CAPACITOR_*, RESISTOR_*, CURRENT_*_BIAS) is referenced
            # by the DUT netlist → a sizing knob that MUST be injected as a .param at assembly.
            knobs.append({"name": name, "default": val})
        if up.endswith("_BIAS") or up.startswith("CURRENT_"):
            conds["ibias"] = val                    # also surface as a datasheet condition
    return sorted(knobs, key=lambda k: k["name"]), conds


def _resolve_cid(folder: str, dest_circuits_root: Path) -> str:
    """The circuit id for an upstream folder — stable across re-imports (plan_scoreboard D-1/D-3).

    An already-registered circuit is matched by its provenance aliases (the upstream folder name,
    or the pre-accession legacy id ``folder.lower()``) and keeps its id. A fresh import allocates
    the next amplifier accession, slugged from the folder minus the ``_pin_3`` port-convention
    suffix."""
    legacy = folder.lower()
    if dest_circuits_root.is_dir():
        for cy in sorted(dest_circuits_root.glob("*/circuit.yaml")):
            doc = yaml.safe_load(cy.read_text()) or {}
            aliases = set((doc.get("provenance") or {}).get("aliases") or [])
            if doc.get("id") == legacy or folder in aliases or legacy in aliases:
                return str(doc["id"])
    from ..model import class_id_code, next_accession

    slug = legacy[: -len("_pin_3")] if legacy.endswith("_pin_3") else legacy
    code = class_id_code("amplifier") or "amp"
    return f"{code}_{next_accession(code, dest_circuits_root):03d}_{slug}"


def import_circuit(src_amplifier_dir: Path, folder: str, dest_circuits_root: Path) -> Path:
    """Import one AnalogGym amplifier folder into ``<dest>/<id>/``; return the circuit dir.

    Raises ``ValueError`` if the netlist is missing/empty (e.g. Qu_LEC) — the caller marks it
    incomplete rather than importing a guess.
    """
    netlist_path = src_amplifier_dir / "spice_netlist" / folder
    dvars_path = src_amplifier_dir / "design_variables" / folder
    raw = netlist_path.read_text() if netlist_path.is_file() else ""
    if ".subckt" not in raw.lower():
        raise ValueError(f"{folder}: ngspice netlist missing or empty (no .subckt)")

    meta = parse_folder(folder)
    cid = _resolve_cid(folder, dest_circuits_root)
    cdir = dest_circuits_root / cid
    (cdir / "abstract").mkdir(parents=True, exist_ok=True)
    (cdir / "pdk" / "sky130").mkdir(parents=True, exist_ok=True)
    (cdir / "analyses").mkdir(parents=True, exist_ok=True)

    # --- abstract netlist ---
    (cdir / "abstract" / "netlist.spice").write_text(neutralize_netlist(raw, cid))

    # --- sizing + conditions ---
    dvars = _read_design_variables(dvars_path) if dvars_path.is_file() else {}
    knobs, conds = _split_design_vars(dvars)
    sizing = {"schema": "spicexplorer/sizing@1", "pdk": "sky130", "variables": knobs}
    (cdir / "pdk" / "sky130" / "sizing.yaml").write_text(
        "# AnalogGym design variables (role-encoded). W/L in um, M integer; the netlist scales\n"
        "# them (e.g. m='4*<M>'). Defaults are the committed AnalogGym values.\n"
        + yaml.safe_dump(sizing, sort_keys=False, width=100))
    (cdir / "pdk" / "sky130" / "devices.map.yaml").write_text(
        "pdk: sky130\ndevices:\n  nmos: {model: sky130_fd_pr__nfet_01v8}\n"
        "  pmos: {model: sky130_fd_pr__pfet_01v8}\n")
    (cdir / "pdk" / "sky130" / "corners.yaml").write_text(
        "# sky130 corner libs are out-of-repo (D-6); AnalogGym vendors them under its PDK/.\n"
        "pdk: sky130\ncorners:\n  tt: [{lib_file: sky130.lib.spice, section: tt}]\n"
        "  ss: [{lib_file: sky130.lib.spice, section: ss}]\n"
        "  ff: [{lib_file: sky130.lib.spice, section: ff}]\ndefault_corner: tt\n")

    # --- circuit.yaml ---
    comp = meta["compensation"]
    manifest = {
        "schema": "spicexplorer/circuit@1",
        "id": cid,
        "class": "amplifier",
        "display_name": f"{meta['stages']}-stage OTA — {comp} compensation ({meta['author']})",
        "compensation": comp,
        "stages": meta["stages"],
        "ports": ["vss", "vdd", "vinn", "vinp", "vout"],   # = AnalogGym subckt order, normalized
        "provenance": {
            "source": "AnalogGym",
            # the upstream folder + the pre-accession legacy id — the re-import match keys
            "aliases": [folder] + ([folder.lower()] if folder.lower() != cid else []),
            "paper": _PAPER.get(comp, f"see analoggym-amplifiers skill ({comp})"),
            "license": "BSD-3-Clause",
        },
        "artifacts": {
            "abstract_netlist": "abstract/netlist.spice",
            "graph": "abstract/topology.cgraph.json",
            "datasheet": "datasheet.yaml",
        },
        "pdks": ["sky130"],
        "analyses": list(_ANALYSES),
        "status": "incomplete" if folder in _SIM_INCOMPLETE else "draft",
    }
    if folder in _SIM_INCOMPLETE:
        manifest["provenance"]["note"] = _SIM_INCOMPLETE[folder]
    (cdir / "circuit.yaml").write_text(
        "# SUPER-DSL manifest — AnalogGym import (plan Phase 5).\n"
        + yaml.safe_dump(manifest, sort_keys=False, width=100))

    # --- datasheet.yaml (extract-only; conditions from design_variables) ---
    supply = "1.8"  # AnalogGym shipped TB / README rail (skill gotcha 1)
    dconds: dict[str, Any] = {"supply": {"unit": "V", "typical": float(_eng(supply))},
                              "corner": {"typical": "tt"}, "temp": {"unit": "degC", "typical": 27}}
    if "cload" in conds:
        dconds["cload"] = {"unit": "F", "typical": _eng(conds["cload"])}
    if "vcm" in conds:
        dconds["vcm"] = {"unit": "V", "typical": _eng(conds["vcm"])}
    if "ibias" in conds:
        dconds["ibias"] = {"unit": "A", "typical": _eng(conds["ibias"])}
    datasheet = {"schema": "spicexplorer/datasheet@1", "default_conditions": dconds,
                 "metrics": _BENCHMARK_METRICS}
    (cdir / "datasheet.yaml").write_text(
        "# Datasheet — AnalogGym single-objective benchmark specs (skill §6 / Eq. 5), extract-only.\n"
        "# Conditions (cload/vcm/ibias) read from the AnalogGym design_variables.\n"
        + yaml.safe_dump(datasheet, sort_keys=False, width=100))

    # --- analysis bindings (the AnalogGym amps self-bias via an internal I0 source — no ibias
    #     port; the bias_wrap flag is an advisory hint for the wrapped open-loop template, deferred) ---
    vcm = conds.get("vcm", "0.3")
    cl = conds.get("cload", "100p")
    # ac_open_loop uses the bias-wrap template (enabled — the headline sim). dc_op/noise/tran_step
    # are scaffolded but `enabled: false`: the self-biased 3-stage amps need bias-aware variants of
    # those benches (the direct-drive universal templates won't bias them) — deferred. Tier 2 still
    # assembles all four; the runner/sim tiers skip the disabled ones.
    bindings = {
        "ac_open_loop": ("ac_open_loop_biaswrap", True,
                         "Open-loop AC gain/phase via the AnalogGym bias-wrap (Lfb/Cin).",
                         "[dc_gain_db, ugf_hz, pm_deg]",
                         f"{{VDD: {supply}, VCM: {vcm}, CL: {cl}, FSTART: 0.1, FSTOP: 1G, PPD: 50}}"),
        "dc_op": ("dc_op", False, "DC operating point (bias-aware variant deferred).", "[i_supply]",
                  f"{{VDD: {supply}, VCM: {vcm}}}"),
        "noise": ("noise", False, "Input-referred noise (bias-aware variant deferred).", "[vn_in]",
                  f"{{VDD: {supply}, VCM: {vcm}, CL: {cl}, FSTART: 1k, FSTOP: 1G, PPD: 50}}"),
        "tran_step": ("tran_step", False, "Step settling (bias-aware variant deferred).", "[t_settle]",
                      f"{{VDD: {supply}, VCM: {vcm}, CL: {cl}, VSTEP: 0.2, VTOL: 2m, "
                      f"TSTART: 1u, TSTEP: 10n, TSTOP: 200u}}"),
    }
    for aid, (template, enabled, desc, produces, params) in bindings.items():
        (cdir / "analyses" / f"{aid}.yaml").write_text(
            f"# AnalogGym analysis binding ({aid}).\n"
            f"schema: spicexplorer/analysis@1\nid: {aid}\ntemplate: {template}\n"
            f"description: \"{desc}\"\nenabled: {str(enabled).lower()}\n"
            f"params: {params}\nflags: []\nproduces: {produces}\n")

    (cdir / "README.md").write_text(
        f"# {cid} — {meta['stages']}-stage OTA, {comp} compensation\n\n"
        f"Imported from CODA-Team/AnalogGym `Amplifier/.../{folder}` (BSD-3-Clause) by "
        "`analog-db import-analoggym`. Compensation scheme + source: "
        f"{_PAPER.get(comp, comp)}.\n\n"
        "- `abstract/netlist.spice` — PDK-neutral (sky130→nmos/pmos), canonical ports, role-encoded\n"
        "  design-variable symbols preserved.\n"
        "- `pdk/sky130/sizing.yaml` — the AnalogGym design variables (W/L/M + compensation passives).\n"
        "- `datasheet.yaml` — extract-only benchmark specs (skill §6); per-topology CLoad from the\n"
        "  AnalogGym design_variables. Sim/symbolic deferred (needs the AnalogGym sky130 PDK).\n")
    return cdir


def _eng(s: str) -> float:
    """Parse an eng-suffixed value (10p, 60u, 300m, 1.8) to float."""
    s = s.strip()
    mult = {"f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3,
            "k": 1e3, "meg": 1e6, "g": 1e9}
    low = s.lower()
    for suf in ("meg", "f", "p", "n", "u", "m", "k", "g"):
        if low.endswith(suf):
            try:
                return float(low[: -len(suf)]) * mult[suf]
            except ValueError:
                break
    return float(s)


def import_all(src_amplifier_dir: Path, dest_circuits_root: Path) -> tuple[list[str], list[str]]:
    """Import every amplifier under ``spice_netlist/``. Returns (imported_ids, skipped_folders)."""
    nl_dir = src_amplifier_dir / "spice_netlist"
    imported, skipped = [], []
    for f in sorted(nl_dir.iterdir()):
        if not f.is_file():
            continue
        try:
            cdir = import_circuit(src_amplifier_dir, f.name, dest_circuits_root)
            imported.append(cdir.name)
        except (ValueError, OSError) as exc:
            skipped.append(f"{f.name}: {exc}")
    return imported, skipped
