"""Convert the wizard form payload into a `project_setup.yaml` string.

The wizard sends a JSON blob shaped to mirror the DSL in
`spicexplorer.core.domains.Project_Setup` so the mapping here is mostly a
1:1 walk. Empty / falsy optional fields are dropped to keep the emitted
YAML close to the hand-written examples.
"""
from __future__ import annotations

from typing import Any, Dict, List

import yaml


def _drop_empty(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v not in (None, "", [], {})}


def _coerce_number(value: Any) -> Any:
    """Keep engineering-suffix strings (e.g. '0.18u') as-is; coerce plain numerics."""
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            if any(c in s for c in (".", "e", "E")):
                return float(s)
            return int(s)
        except ValueError:
            return s  # likely "0.18u" or a constraint reference
    return value


def _build_dut_param(row: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "name": row["name"],
        "min_val": _coerce_number(row.get("min_val")),
        "max_val": _coerce_number(row.get("max_val")),
    }
    if row.get("is_integer"):
        out["is_integer"] = True
    if row.get("log_scale"):
        out["log_scale"] = True
    if row.get("freeze"):
        # Only `freeze: true` must be serialized (False is the dataclass default).
        # The prior `is False` check inverted this and silently dropped frozen params,
        # so a frozen DUT param was emitted without `freeze` and then swept as a free var.
        out["freeze"] = True
    if row.get("init") not in (None, ""):
        out["init"] = _coerce_number(row.get("init"))
    # `val` is the FROZEN operating point a param is pinned at (parameterize injects
    # param.val ?? param.init). Dropping it on round-trip un-pins a frozen param to its
    # init/netlist default — silently changing the optimized design (BUG-B15).
    if row.get("val") not in (None, ""):
        out["val"] = _coerce_number(row.get("val"))
    return _drop_empty(out)


def _build_tb_param(row: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "name": row["name"],
        "val": _coerce_number(row.get("val")),
    }
    if row.get("description"):
        out["description"] = row["description"]
    return _drop_empty(out)


def _build_testbench(tb: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "name": tb["name"],
        "params": [_build_tb_param(p) for p in tb.get("params", []) if p.get("name")],
        "netlist": tb.get("netlist", ""),
    }
    if tb.get("enable") is False:
        out["enable"] = False
    else:
        out["enable"] = True
    if tb.get("description"):
        out["description"] = tb["description"]
    return out


def _build_target_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "name": spec["name"],
        "testbench": spec["testbench"],
        "sim_type": spec.get("sim_type", "ac"),
        "goal": spec.get("goal", "exceed"),
        "target": _coerce_number(spec.get("target")),
    }
    for key in ("range", "tolerance", "weight"):
        v = spec.get(key)
        if v not in (None, ""):
            out[key] = _coerce_number(v)
    for key in ("error_type", "reward_type"):
        v = spec.get(key)
        if v:
            out[key] = v
    if spec.get("log_scale"):
        out["log_scale"] = True
    out["enable"] = spec.get("enable", True)
    if spec.get("description"):
        out["description"] = spec["description"]
    return out


def _build_optimizer(form: Dict[str, Any]) -> Dict[str, Any]:
    o = form.get("optimizer", {})
    targets = form.get("target_specs", [])
    out: Dict[str, Any] = {
        "type": o.get("type", "nevergrad"),
        "name": o.get("name", "LhsDE"),
        "budget": int(o.get("budget") or 200),
    }
    if o.get("random_seed") not in (None, ""):
        out["random_seed"] = int(o["random_seed"])
    if o.get("lin_min") not in (None, "") and o.get("lin_max") not in (None, ""):
        out["lin_variable_bounds"] = {
            "min": _coerce_number(o["lin_min"]),
            "max": _coerce_number(o["lin_max"]),
        }
    if o.get("log_min") not in (None, "") and o.get("log_max") not in (None, ""):
        out["log_variable_bounds"] = {
            "min": _coerce_number(o["log_min"]),
            "max": _coerce_number(o["log_max"]),
        }
    kwargs_rows = o.get("optimizer_kwargs") or []
    kwargs: Dict[str, Any] = {}
    for row in kwargs_rows:
        key = (row.get("key") or "").strip()
        if not key:
            continue
        raw_val = row.get("value")
        # Support bool literals and engineering numbers; fall back to string
        if isinstance(raw_val, str):
            lower = raw_val.strip().lower()
            if lower in ("true", "false"):
                kwargs[key] = lower == "true"
                continue
            if lower in ("none", "null", ""):
                kwargs[key] = None
                continue
        kwargs[key] = _coerce_number(raw_val)
    if kwargs:
        out["optimizer_kwargs"] = kwargs
    out["target_specs"] = [_build_target_spec(s) for s in targets if s.get("name")]
    return out


def _build_tech_spec(form: Dict[str, Any]) -> Dict[str, Any]:
    tech = form.get("tech", {})
    constraints_in: List[Dict[str, Any]] = tech.get("constraints", [])
    constraints: Dict[str, Any] = {}
    for row in constraints_in:
        key = (row.get("key") or "").strip()
        if not key:
            continue
        constraints[key] = _coerce_number(row.get("value"))
    return {
        "name": tech.get("name", ""),
        "constraints": constraints,
    }


def _build_pvt_block(form: Dict[str, Any]) -> Dict[str, Any] | None:
    """Emit the new `pvt:` block (Phase 1) from the wizard's pvt config.

    Corners are written with inline `model_includes` (the wizard skips the
    `process_bundles` sugar). Returns None when no corner is defined, so no `pvt:`
    block is emitted and the netlist's own hardcoded corner stays in effect.
    """
    pvt = form.get("pvt") or {}
    corners_out: List[Dict[str, Any]] = []
    for c in pvt.get("corners") or []:
        name = (c.get("name") or "").strip()
        if not name:
            continue
        corner: Dict[str, Any] = {"name": name}
        includes = [
            {"lib_file": (inc.get("lib_file") or "").strip(), "section": (inc.get("section") or "").strip()}
            for inc in (c.get("includes") or [])
            if (inc.get("lib_file") or "").strip() and (inc.get("section") or "").strip()
        ]
        if includes:
            corner["model_includes"] = includes
        if c.get("temp") not in (None, ""):
            corner["temp"] = _coerce_number(c.get("temp"))
        node = (c.get("supply_node") or "").strip()
        rails: List[Dict[str, Any]] = []
        if node and c.get("supply_value") not in (None, ""):
            rails.append({"node": node, "value": _coerce_number(c.get("supply_value"))})
        # Re-emit any carried rails 2..N so a multi-rail corner survives the round-trip
        # instead of being silently collapsed to its first rail (BUG-A6 / WIZ-4).
        for s in (c.get("extra_supplies") or []):
            n = (s.get("node") or "").strip()
            if n and s.get("value") not in (None, ""):
                rails.append({"node": n, "value": _coerce_number(s.get("value"))})
        if len(rails) == 1:
            corner["supply"] = rails[0]
        elif len(rails) > 1:
            corner["supplies"] = rails
        # Carry per-corner extra `.param` overrides so they survive the round-trip instead of
        # reverting to the netlist defaults after a wizard Save (BUG-B40).
        params = c.get("params") or {}
        if isinstance(params, dict) and params:
            corner["params"] = {k: _coerce_number(v) for k, v in params.items()}
        corner["enabled"] = bool(c.get("enabled", True))
        corners_out.append(corner)

    if not corners_out:
        return None
    active = (pvt.get("active_corner") or "").strip() or corners_out[0]["name"]
    block: Dict[str, Any] = {"active_corner": active, "corners": corners_out}
    # Multi-corner (Phase 2) knobs must survive the round-trip, or a wizard Save
    # silently reverts a project to single-corner behavior. Emit only non-default
    # values so single-corner YAMLs stay uncluttered.
    mode = (pvt.get("mode") or "").strip().lower()
    if mode and mode != "single":
        block["mode"] = mode
    agg = (pvt.get("score_aggregation") or "").strip().lower()
    if agg and agg != "mean":
        block["score_aggregation"] = agg
    # model_lib_root is load-bearing — apply_corner() prepends it to each include's
    # lib_file — so it must survive the wizard round-trip instead of being dropped.
    raw_root = pvt.get("model_lib_root")
    root = raw_root.strip() if isinstance(raw_root, str) else raw_root
    if root:
        block["model_lib_root"] = root
    return block


def build_project_dict(form: Dict[str, Any]) -> Dict[str, Any]:
    """Top-level mapping: returns the structure dumped as YAML."""
    project = form.get("project", {})
    body: Dict[str, Any] = {
        "name": project.get("name", "unnamed-project"),
        "description": project.get("description", ""),
        "simulator": project.get("simulator", "ngspice"),
        "save_sim": bool(project.get("save_sim", False)),
        "parallel_sim": bool(project.get("parallel_sim", True)),
        "ws_root": project.get("ws_root", ""),
        "netlist": project.get("netlist", ""),
        "outdir": project.get("outdir", "spice/temp_spice_out"),
        **({"schematic": project["schematic"]} if project.get("schematic") else {}),
        "tech_spec": _build_tech_spec(form),
        **({"pvt": _pvt_block} if (_pvt_block := _build_pvt_block(form)) else {}),
        "dut_params": [_build_dut_param(p) for p in form.get("dut_params", []) if p.get("name")],
        "testbenches": [_build_testbench(tb) for tb in form.get("testbenches", []) if tb.get("name")],
        "optimizer_config": _build_optimizer(form),
    }
    return {"project": body}


def generate_yaml(form: Dict[str, Any]) -> str:
    payload = build_project_dict(form)
    return yaml.safe_dump(payload, sort_keys=False, default_flow_style=False, indent=2)


# ---------------------------------------------------------------------------
# Inverse direction: existing YAML  →  WizardForm dict
# ---------------------------------------------------------------------------

def _str_or_blank(v: Any) -> str:
    if v is None:
        return ""
    return str(v)


def _bool(v: Any, default: bool = False) -> bool:
    if v is None:
        return default
    return bool(v)


def _pvt_block_to_form(raw_pvt: Any) -> Dict[str, Any]:
    """Convert a raw `pvt:` block (yaml.safe_load shape) into the wizard's pvt form.

    Reuses the canonical desugaring (`_normalize_pvt_block`) so a YAML using
    `process_bundles` / `process:` refs / singular `supply` flattens to the inline
    shape the wizard edits. The wizard models a single supply rail, so only the
    first supply is carried (multi-rail YAML is fully editable in the raw editor).
    """
    empty = {"active_corner": "", "corners": [], "model_lib_root": "", "mode": "single", "score_aggregation": "mean"}
    if not isinstance(raw_pvt, dict):
        return empty

    import copy

    from spicexplorer.core.domains import _normalize_pvt_block

    holder = {"pvt": copy.deepcopy(raw_pvt)}
    try:
        _normalize_pvt_block(holder)
    except Exception:
        return empty
    block = holder["pvt"]

    corners_out: List[Dict[str, Any]] = []
    for c in (block.get("corners") or []):
        supplies = c.get("supplies") or []
        first = supplies[0] if supplies else {}
        corners_out.append({
            "name": _str_or_blank(c.get("name")),
            "temp": _str_or_blank(c.get("temp")) or "27",
            "supply_node": _str_or_blank(first.get("node")) or "VDD",
            "supply_value": _str_or_blank(first.get("value")),
            # Carry rails 2..N losslessly (the wizard edits only the primary rail) so a
            # round-trip Save doesn't drop a multi-rail corner (BUG-A6 / WIZ-4).
            "extra_supplies": [
                {"node": _str_or_blank(s.get("node")), "value": _str_or_blank(s.get("value"))}
                for s in supplies[1:]
            ],
            "enabled": _bool(c.get("enabled"), True),
            "includes": [
                {"lib_file": _str_or_blank(m.get("lib_file")), "section": _str_or_blank(m.get("section"))}
                for m in (c.get("model_includes") or [])
            ],
            # Carry per-corner `.param` overrides so they round-trip (BUG-B40).
            "params": dict(c.get("params") or {}),
        })
    return {
        "active_corner": _str_or_blank(block.get("active_corner")),
        "corners": corners_out,
        # Carry model_lib_root through the round-trip (it survives _normalize_pvt_block
        # untouched); the wizard re-emits it via _build_pvt_block.
        "model_lib_root": _str_or_blank(block.get("model_lib_root")),
        # Multi-corner (Phase 2) knobs — defaulted so pre-Phase-2 YAMLs form-load
        # cleanly; _build_pvt_block re-emits non-default values.
        "mode": (_str_or_blank(block.get("mode")) or "single").lower(),
        "score_aggregation": (_str_or_blank(block.get("score_aggregation")) or "mean").lower(),
    }


def project_dict_to_form(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a `yaml.safe_load`-style project dict into the wizard's form shape.

    String values (e.g. `0.18u`, constraint keys) are preserved verbatim so the
    round-trip generate→parse→generate is lossless for engineering-notation values.
    """
    p = data.get("project") or {}
    tech = p.get("tech_spec") or {}
    opt = p.get("optimizer_config") or {}

    constraints_dict: Dict[str, Any] = tech.get("constraints") or {}
    constraints = [{"key": k, "value": _str_or_blank(v)} for k, v in constraints_dict.items()]

    pvt_form = _pvt_block_to_form(p.get("pvt"))

    dut_rows = []
    for d in (p.get("dut_params") or []):
        dut_rows.append({
            "name": _str_or_blank(d.get("name")),
            "min_val": _str_or_blank(d.get("min_val")),
            "max_val": _str_or_blank(d.get("max_val")),
            "init": _str_or_blank(d.get("init")),
            "val": _str_or_blank(d.get("val")),  # frozen operating point — must round-trip (BUG-B15)
            "is_integer": _bool(d.get("is_integer"), False),
            "log_scale": _bool(d.get("log_scale"), False),
            # Project_Setup default: freeze=True if not specified — but wizard default is "tracked".
            # Preserve explicit value, default to False so loaded params are variable by default.
            "freeze": _bool(d.get("freeze"), False),
            "source": "manual",
        })

    tb_rows = []
    for tb in (p.get("testbenches") or []):
        params = []
        for tp in (tb.get("params") or []):
            params.append({
                "name": _str_or_blank(tp.get("name")),
                "val": _str_or_blank(tp.get("val")),
                "description": _str_or_blank(tp.get("description")),
                "source": "manual",
            })
        tb_rows.append({
            "name": _str_or_blank(tb.get("name")),
            "netlist": _str_or_blank(tb.get("netlist")),
            "enable": _bool(tb.get("enable"), True),
            "description": _str_or_blank(tb.get("description")),
            "params": params,
        })

    spec_rows = []
    for s in (opt.get("target_specs") or []):
        spec_rows.append({
            "name": _str_or_blank(s.get("name")),
            "testbench": _str_or_blank(s.get("testbench")),
            "sim_type": _str_or_blank(s.get("sim_type")) or "ac",
            "goal": _str_or_blank(s.get("goal")) or "exceed",
            "target": _str_or_blank(s.get("target")),
            "range": _str_or_blank(s.get("range")),
            "tolerance": _str_or_blank(s.get("tolerance")),
            "weight": _str_or_blank(s.get("weight")) or "1.0",
            "log_scale": _bool(s.get("log_scale"), False),
            "error_type": _str_or_blank(s.get("error_type")) or "relative-absolute",
            "reward_type": _str_or_blank(s.get("reward_type")) or "none",
            "enable": _bool(s.get("enable"), True),
            "description": _str_or_blank(s.get("description")),
        })

    lin = opt.get("lin_variable_bounds") or {}
    log = opt.get("log_variable_bounds") or {}
    optimizer_kwargs = opt.get("optimizer_kwargs") or {}

    optimizer = {
        "type": _str_or_blank(opt.get("type")) or "nevergrad",
        "name": _str_or_blank(opt.get("name")) or "LhsDE",
        "budget": _str_or_blank(opt.get("budget")) or "200",
        "random_seed": _str_or_blank(opt.get("random_seed")) or "42",
        "lin_min": _str_or_blank(lin.get("min")) or "0",
        "lin_max": _str_or_blank(lin.get("max")) or "100",
        "log_min": _str_or_blank(log.get("min")) or "1",
        "log_max": _str_or_blank(log.get("max")) or "100",
        # Free-form kwargs: serialised as a list of {key,value} pairs so the UI can edit them
        "optimizer_kwargs": [
            {"key": str(k), "value": _str_or_blank(v) if not isinstance(v, (dict, list)) else yaml.safe_dump(v).strip()}
            for k, v in optimizer_kwargs.items()
        ],
    }

    return {
        "project": {
            "name": _str_or_blank(p.get("name")),
            "description": _str_or_blank(p.get("description")),
            "simulator": _str_or_blank(p.get("simulator")) or "ngspice",
            "save_sim": _bool(p.get("save_sim"), False),
            "parallel_sim": _bool(p.get("parallel_sim"), True),
            "ws_root": _str_or_blank(p.get("ws_root")),
            "netlist": _str_or_blank(p.get("netlist")),
            "outdir": _str_or_blank(p.get("outdir")) or "spice/temp_spice_out",
            "schematic": _str_or_blank(p.get("schematic")),
        },
        "tech": {
            "name": _str_or_blank(tech.get("name")),
            "constraints": constraints,
        },
        "pvt": pvt_form,
        "dut_params": dut_rows,
        "testbenches": tb_rows,
        "target_specs": spec_rows,
        "optimizer": optimizer,
    }
