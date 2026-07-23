"""Generate a raw-targeting ``project_setup.yaml`` — the optimizer driven straight off the
committed ``raw/`` export decks (companion to the hand-authored ``raw_optimize/`` demos).

Unlike ``extends.generate_project_setup`` (which targets the hand-authored ``testbenches.legacy``
netlists and pulls ``target_specs`` from the datasheet's ``optimize`` blocks), this points the
optimizer at ``raw/<id>/<pdk>/<analysis>.spice`` and DERIVES the specs by parsing each deck's
``.control`` block for the vectors it writes. That keeps the config in sync with the decks and
works for any circuit with raw decks — including those whose datasheet carries no ``optimize``
projection (e.g. the LDOs).

Naming rule (see the ``raw_optimize/`` README): a ``meas`` result is saved bare; ngspice saves a
``let`` scalar type-prefixed — ``let i_supply = abs(i(Vdd))`` → ``i(i_supply)``,
``let vout_dc = v(vout)`` → ``v(vout_dc)`` — so a target-spec name matches what RawRead sees.

Goals/targets are design intent we won't invent, so only the whitelisted, well-characterised
template metrics in ``_SPEC_REGISTRY`` become specs; a deck vector outside it is skipped (and a
testbench with no scorable spec is dropped). Sizing knobs are searched over a bias-preserving band
around the committed default; passives / reference / integer counts are frozen so the operating
point (and any regulation target) stays well-defined.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

from . import export, model, paths

# --------------------------------------------------------------------------- metric intent

# base metric name (i()/v() stripped) → optimizer intent. A whitelist: a deck vector not listed
# here has no defensible default goal/target, so it is skipped rather than guessed.
_SPEC_REGISTRY: dict[str, dict[str, Any]] = {
    "dcgain":       {"goal": "exceed",   "target": 40,      "range": 40,      "tolerance": 1,      "reward_type": "log"},
    "ugf":          {"goal": "exceed",   "target": 1.0e6,   "range": 10.0e6,  "tolerance": 1.0e5,  "reward_type": "log"},
    "pm":           {"goal": "exact",    "target": 60,      "range": 45,      "tolerance": 10,     "reward_type": "none"},
    "i_supply":     {"goal": "minimize", "target": 1.0e-4,  "range": 1.0e-3,  "tolerance": 1.0e-6, "reward_type": "log"},
    "vout_dc":      {"goal": "exact",    "target": 1.2,     "range": 1.0,     "tolerance": 0.02,   "reward_type": "none"},
    "load_reg":     {"goal": "minimize", "target": 1.0e-2,  "range": 5.0e-2,  "tolerance": 1.0e-4, "reward_type": "log"},
    "line_reg":     {"goal": "minimize", "target": 5.0e-3,  "range": 5.0e-2,  "tolerance": 1.0e-4, "reward_type": "log"},
    "zout_peak_db": {"goal": "minimize", "target": 3,       "range": 20,      "tolerance": 0.5,    "reward_type": "log"},
    # rejection benches (unity-buffer residual → dB at 1 kHz; all saved bare)
    "cmrr_db":      {"goal": "exceed",   "target": 40,      "range": 40,      "tolerance": 2,      "reward_type": "log"},
    "psrr_vdd_db":  {"goal": "exceed",   "target": 40,      "range": 40,      "tolerance": 2,      "reward_type": "log"},
    "psrr_db":      {"goal": "exceed",   "target": 40,      "range": 40,      "tolerance": 2,      "reward_type": "log"},
    "psr_db":       {"goal": "exceed",   "target": 40,      "range": 40,      "tolerance": 2,      "reward_type": "log"},
    # distortion (in-deck coherent DFT; thd_db is negative-dB, so no log reward)
    "thd_pct":      {"goal": "minimize", "target": 1.0,     "range": 10.0,    "tolerance": 0.05,   "reward_type": "log"},
    "thd_db":       {"goal": "minimize", "target": -40,     "range": 40,      "tolerance": 1,      "reward_type": "none"},
    # integrated input/output-referred noise (ngspice `.noise` native totals — see _NATIVE_PRINT)
    "inoise_total": {"goal": "minimize", "target": 1.0e-4,  "range": 1.0e-3,  "tolerance": 1.0e-7, "reward_type": "log"},
    "onoise_total": {"goal": "minimize", "target": 1.0e-3,  "range": 1.0e-2,  "tolerance": 1.0e-6, "reward_type": "log"},
    # step response + closed-loop buffer benches
    "t_settle":     {"goal": "minimize", "target": 1.0e-6,  "range": 1.0e-5,  "tolerance": 1.0e-8, "reward_type": "log"},
    "gain_cl":      {"goal": "exact",    "target": 1.0,     "range": 0.5,     "tolerance": 0.05,   "reward_type": "none"},
    "bw_cl":        {"goal": "exceed",   "target": 1.0e6,   "range": 1.0e7,   "tolerance": 1.0e5,  "reward_type": "log"},
    # LDO dropout (dc sweep: vin at which vout reaches its target, minus vout)
    "v_dropout":    {"goal": "minimize", "target": 0.3,     "range": 1.0,     "tolerance": 0.01,   "reward_type": "log"},
}

# sizing-var units that are SEARCHED (continuous geometry / bias current); every other unit
# (integer counts, ohms, farads, volts) is frozen at its default to hold the operating point.
_SEARCH_UNITS = {"m", "a"}

_ENG = {"t": 1e12, "g": 1e9, "meg": 1e6, "k": 1e3, "": 1.0,
        "m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15}


def _eng(value: Any) -> float:
    """Parse an ngspice-style engineering string (``0.5u``, ``100k``, ``2n``, ``10Meg``) → float."""
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().lower()
    m = re.fullmatch(r"([+-]?[0-9.eE+-]+)\s*(meg|[tgkmunpf]?)", s)
    if not m:
        return float(s)  # a plain number in string form
    return float(m.group(1)) * _ENG[m.group(2)]


# --------------------------------------------------------------------------- deck parsing


def _control_block(deck_text: str) -> list[str]:
    lines = deck_text.splitlines()
    try:
        c = next(i for i, ln in enumerate(lines) if ln.strip().lower() == ".control")
        e = next(i for i, ln in enumerate(lines) if ln.strip().lower() == ".endc")
    except StopIteration:
        return []
    return lines[c + 1 : e]


_ANALYSIS_CMDS = ("ac", "dc", "tran", "noise", "op")
_NON_ANALYSIS = ("meas", "let", "print", "set", "write", "quit", "echo", "plot", "save", "remzerovec")

# Native analysis-output vectors a deck can ``print`` directly — no ``meas``, no ``let``. Keyed by
# sim_type → {printed name: the name RawRead sees in the written raw file}. The ngspice ``.noise``
# analysis emits ``inoise_total``/``onoise_total`` as VOLTAGE-typed vectors, so they land v()-wrapped
# (verified against a written rawfile). Any ``let`` derived from them (e.g. ``sqrt(onoise_total)``)
# inherits the voltage type and is likewise v()-wrapped — which ``_saved_name``'s RHS-scan can't see,
# so such derived lets are deliberately left out of the registry (``onoise_total`` already covers them).
_NATIVE_PRINT: dict[str, dict[str, str]] = {
    "noise": {"inoise_total": "v(inoise_total)", "onoise_total": "v(onoise_total)"},
}


def _analysis_type(control: list[str]) -> str | None:
    """The deck's analysis command → sim_type (``op``/``ac``/``dc``/``tran``/``noise``)."""
    for ln in control:
        s = ln.strip().lower()
        if not s or any(s.startswith(p) for p in _NON_ANALYSIS):
            continue
        head = s.split()[0]
        if head in _ANALYSIS_CMDS:
            return head
    return None


def _saved_name(name: str, rhs: str) -> str:
    """The name RawRead will see for a ``let <name> = <rhs>`` scalar: ngspice types it from the
    expression — a current expression → ``i(name)``, a voltage expression → ``v(name)``, anything
    else (arithmetic of dimensionless ``meas`` results, dB math) stays bare."""
    if re.search(r"\bi\s*\(", rhs, re.IGNORECASE):
        return f"i({name})"
    if re.search(r"\bv(?:db|p|dbm)?\s*\(", rhs, re.IGNORECASE):
        return f"v({name})"
    return name


def parse_deck_metrics(deck_text: str) -> list[tuple[str, str]]:
    """``[(saved_vector_name, sim_type), …]`` for the scorable scalars a raw deck writes.

    Collects every ``meas`` result plus every ``let`` scalar named in a ``print``, applies the
    ngspice naming rule, and keeps only whitelisted metrics (``_SPEC_REGISTRY``). Order-preserving,
    de-duplicated by name.
    """
    control = _control_block(deck_text)
    atype = _analysis_type(control)
    lets: dict[str, str] = {}
    printed: list[str] = []
    ordered: list[tuple[str, str]] = []
    seen: set[str] = set()

    def _add(saved: str, sim: str) -> None:
        base = re.sub(r"^[iv]\((.*)\)$", r"\1", saved)
        if base in _SPEC_REGISTRY and saved not in seen:
            seen.add(saved)
            ordered.append((saved, sim))

    for ln in control:
        s = ln.strip()
        m = re.match(r"(?i)meas\s+(ac|dc|tran|op|noise|sp)\s+(\w+)", s)
        if m:
            _add(m.group(2), m.group(1).lower())
            continue
        m = re.match(r"(?i)let\s+(\w+)\s*=\s*(.+)", s)
        if m:
            lets[m.group(1)] = m.group(2)
            continue
        m = re.match(r"(?i)print\s+(.+)", s)
        if m:
            printed += [tok for tok in re.split(r"\s+", m.group(1)) if re.fullmatch(r"\w+", tok)]
    for name in printed:
        if atype is None:
            continue
        if name in lets:
            _add(_saved_name(name, lets[name]), atype)
        elif name in _NATIVE_PRINT.get(atype, {}):
            _add(_NATIVE_PRINT[atype][name], atype)  # native totals: no let, hardcoded saved name
    return ordered


# --------------------------------------------------------------------------- dut params


def _sig(x: float, n: int = 3) -> float:
    """Round to ``n`` significant figures (tidies float-division noise in the emitted bounds)."""
    if x == 0:
        return 0.0
    from math import floor, log10

    return round(x, -int(floor(log10(abs(x)))) + (n - 1))


def _band(default: float, lo: float | None, hi: float | None, factor: float = 2.0) -> tuple[float, float]:
    """A bias-preserving search band centred on ``default`` (``[default/factor, default*factor]``),
    clamped to the sizing var's own ``[min, max]`` when given."""
    a, b = default / factor, default * factor
    if lo is not None:
        a = max(a, lo)
    if hi is not None:
        b = min(b, hi)
    return _sig(a), _sig(b)


def _search_var(var: dict[str, Any]) -> bool:
    """Search this sizing knob (transistor geometry / bias current) or freeze it (integer counts,
    passives, references)? Uses the ``unit`` when the sizing var carries one (the in-repo circuits),
    else falls back to name tokens (the AnalogGym imports ship no ``unit``)."""
    if var.get("is_integer"):
        return False
    unit = str(var.get("unit", "")).lower()
    if unit:
        return unit in _SEARCH_UNITS  # m (geometry) / a (current); ohm/f/v/count → freeze
    name = var["name"].lower()
    if re.search(r"(^|_)m(_|$)", name):                                   # device-count multiplier
        return False
    if re.search(r"(^|_)(w|l)(_|$)", name) or "width" in name or "length" in name:
        return True                                                      # W / L geometry
    if "current" in name or re.search(r"(^|_)i(_|bias|tail|$)", name):
        return True                                                      # bias current
    return False                                                          # caps / res / refs / unknown


def _dut_params(sizing: dict[str, Any]) -> list[dict[str, Any]]:
    params: list[dict[str, Any]] = []
    for var in sizing.get("variables", []):
        name = var["name"]
        default = var.get("default")
        if default is None or not _search_var(var):
            params.append({"name": name, "freeze": True, "val": _eng(default) if default is not None else 0})
            continue
        lo, hi = _band(
            _eng(default),
            _eng(var["min"]) if var.get("min") is not None else None,
            _eng(var["max"]) if var.get("max") is not None else None,
        )
        params.append({"name": name, "min_val": lo, "max_val": hi})
    return params


# --------------------------------------------------------------------------- generation


def _testbenches_and_specs(
    circuit: model.Circuit, pdk: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Walk the circuit's committed raw decks; build one testbench per deck that yields ≥1 scorable
    spec, and the flattened target-spec list (spec.testbench = the deck/analysis id)."""
    vout_target = (
        circuit.datasheet().get("default_conditions", {}).get("vout", {}).get("typical")
    )
    tbs: list[dict[str, Any]] = []
    specs: list[dict[str, Any]] = []
    for aid in circuit.analyses:
        deck = export.deck_path(circuit, aid, pdk, "tt")
        if not deck.is_file():
            continue
        metrics = parse_deck_metrics(deck.read_text())
        if not metrics:
            continue
        rel = str(deck.relative_to(paths.db_root()))
        tbs.append({"name": aid, "params": [], "netlist": rel, "enable": True,
                    "description": f"raw deck: {aid}"})
        for saved, sim in metrics:
            base = re.sub(r"^[iv]\((.*)\)$", r"\1", saved)
            reg = _SPEC_REGISTRY[base]
            target = reg["target"]
            if base == "vout_dc" and vout_target is not None:
                target = float(vout_target)
            specs.append({
                "name": saved, "testbench": aid, "sim_type": sim, "goal": reg["goal"],
                "target": target, "range": reg["range"], "tolerance": reg["tolerance"],
                "weight": 1.0, "reward_type": reg["reward_type"], "enable": True,
            })
    return tbs, specs


def generate(circuit_id: str, pdk: str | None, out_dir: Path) -> str:
    """Render the raw-targeting ``project_setup.yaml`` text for one circuit (no filesystem writes)."""
    circuit = model.load_circuit(circuit_id)
    pdk = pdk or circuit.pdks[0]
    tbs, specs = _testbenches_and_specs(circuit, pdk)
    # i_supply (quiescent current) is a COST, not an objective: a config that can only score
    # i_supply would just shrink the bias into a degenerate point. Require at least one
    # performance objective (gain/bandwidth/regulation/…) — otherwise skip the circuit (its
    # performance metric isn't in _SPEC_REGISTRY yet; broadening the registry is the follow-up).
    def _base(name: str) -> str:
        return re.sub(r"^[iv]\((.*)\)$", r"\1", name)

    if not any(_base(s["name"]) != "i_supply" for s in specs):
        raise ValueError(
            f"{circuit_id}@{pdk}: only i_supply is scorable — no performance objective "
            "(add its metric to _SPEC_REGISTRY)"
        )

    db = paths.db_root()
    ws_root = os.path.relpath(db, out_dir)                                  # YAML dir → db root
    run_dir = os.path.relpath(out_dir / "_runs" / circuit_id, db)          # db root → run dir
    project = {
        "name": f"RAW-{circuit_id}",
        "description": f"Optimize {circuit_id} by driving its committed raw/ export decks ({pdk}).",
        "simulator": "ngspice",
        "save_sim": False,
        "parallel_sim": True,
        "ws_root": ws_root,
        "netlist": tbs[0]["netlist"],
        "outdir": run_dir,
        "tech_spec": {"name": pdk, "constraints": {}},
        "dut_params": _dut_params(circuit.sizing(pdk)),
        "testbenches": tbs,
        "optimizer_config": {
            "type": "nevergrad", "random_seed": 48, "budget": 15, "name": "NGOpt",
            "lin_variable_bounds": {"min": 0, "max": 100},
            "log_variable_bounds": {"min": 1, "max": 100},
            "target_specs": specs,
        },
    }
    header = (
        "# GENERATED by `analog-db export-raw-project` — DO NOT EDIT.\n"
        f"# Drives the committed raw/{circuit_id}/{pdk}/*.spice decks through the optimizer.\n"
        "# dut_params: sizing.yaml knobs (geometry/bias searched on a band around default; passives\n"
        "#   + integer counts frozen). target_specs: parsed from each deck's meas/let vectors.\n"
    )
    return header + yaml.safe_dump({"project": project}, sort_keys=False, width=100)


def write(circuit_id: str, pdk: str | None, out_dir: Path) -> Path:
    """Write ``<out_dir>/<circuit_id>.yaml``; returns the path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{circuit_id}.yaml"
    out.write_text(generate(circuit_id, pdk, out_dir))
    return out


# --------------------------------------------------------------------------- demo variant


def generate_demo(circuit_id: str, pdk: str | None = None) -> str:
    """Render a Studio DEMO ``project_setup.yaml`` for one circuit (no filesystem writes).

    Same raw-deck testbenches/specs as :func:`generate`, but shaped for the platform's
    "load a demo as a project" flow: ``ws_root`` pins the circuit's raw deck directory
    (so example seeding copies just the decks, not the whole DB), netlists are bare
    filenames, and the project is named from the catalog ``display_name`` + accession id.
    """
    circuit = model.load_circuit(circuit_id)
    pdk = pdk or circuit.pdks[0]
    tbs, specs = _testbenches_and_specs(circuit, pdk)

    def _base(name: str) -> str:
        return re.sub(r"^[iv]\((.*)\)$", r"\1", name)

    if not any(_base(s["name"]) != "i_supply" for s in specs):
        raise ValueError(
            f"{circuit_id}@{pdk}: only i_supply is scorable — no performance objective "
            "(add its metric to _SPEC_REGISTRY)"
        )
    for tb in tbs:
        tb["netlist"] = Path(tb["netlist"]).name  # relative to ws_root = the deck dir

    display = str(circuit.manifest.get("display_name", circuit_id))
    project = {
        "name": f"{display} · {circuit_id}",
        "description": f"analog-db {circuit_id} — optimizer demo on the committed {pdk} raw decks",
        "simulator": "ngspice",
        "save_sim": False,
        "parallel_sim": True,
        "ws_root": f"../../raw/{circuit_id}/{pdk}",
        "netlist": tbs[0]["netlist"],
        "outdir": "scratch",
        "tech_spec": {"name": pdk, "constraints": {}},
        "dut_params": _dut_params(circuit.sizing(pdk)),
        "testbenches": tbs,
        "optimizer_config": {
            "type": "nevergrad", "random_seed": 48, "budget": 15, "name": "NGOpt",
            "lin_variable_bounds": {"min": 0, "max": 100},
            "log_variable_bounds": {"min": 1, "max": 100},
            "target_specs": specs,
        },
    }
    # Vendored schematic assets: every committed .sch/.sym under the circuit dir
    # (pdk schematic/ + reference/ trees), YAML-dir-relative. The platform's
    # example seeding copies them into the project's xschem/ (structure kept so
    # sibling .sym refs resolve); `assets` is a top-level sibling of `project:`,
    # ignored by Project_Setup.from_yaml.
    sch_assets = sorted(
        p.relative_to(circuit.dir).as_posix()
        for pat in ("*.sch", "*.sym")
        for p in circuit.dir.rglob(pat)
        if p.is_file()
    )
    doc: dict[str, Any] = {"project": project}
    if sch_assets:
        doc["assets"] = {"xschem": sch_assets}

    header = (
        "# GENERATED by `analog-db export-raw-project --demo` — DO NOT EDIT.\n"
        f"# Studio demo entry: drives the committed raw/{circuit_id}/{pdk}/*.spice decks\n"
        "# through the optimizer. dut_params from sizing.yaml (geometry/bias searched on a\n"
        "# band around default); target_specs parsed from each deck's meas/let vectors.\n"
        "# assets.xschem: the circuit's committed schematics — seeded into the\n"
        "#   project's xschem/ dir when loaded as a demo.\n"
    )
    return header + yaml.safe_dump(doc, sort_keys=False, width=100, allow_unicode=True)


def write_demo(circuit_id: str, pdk: str | None = None) -> Path:
    """Write ``circuits/<id>/project_setup.yaml``; returns the path.

    Refuses when the circuit has an ``optimizer/projection.yaml`` — that circuit's
    ``project_setup.yaml`` belongs to the extends lane (``analog-db generate``).
    """
    circuit = model.load_circuit(circuit_id)
    if (circuit.dir / "optimizer" / "projection.yaml").is_file():
        raise ValueError(
            f"{circuit_id}: has optimizer/projection.yaml — its project_setup.yaml is "
            "owned by `analog-db generate` (the extends lane), not --demo"
        )
    out = circuit.dir / "project_setup.yaml"
    out.write_text(generate_demo(circuit_id, pdk))
    return out
