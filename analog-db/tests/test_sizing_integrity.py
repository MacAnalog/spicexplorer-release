"""Corpus-wide integrity gates on the committed sizing defaults.

These exist because a bulk defaults-writer once shipped values that were never
simulable as authored — an exponent-stripped bias current (``1e-7`` -> ``979217``
A), a width-in-metres written into a frozen multiplier (``1`` -> ``1.17e-05``),
a 65 µF Miller cap (``0.5p`` -> ``6.5e-05``). Each one still *ran*: ngspice
solved the broken circuit, the harness recorded plausible-looking numbers, and
the scoreboard baseline (hence the paper table) quoted them. Nothing in the
pipeline objected, because every check downstream of the knob trusts the knob.

A default outside its own declared ``[min, max]`` is the cheap, universal
signature of that whole class, so it is gated here corpus-wide.
"""

from __future__ import annotations

import pytest
import yaml

from spicexplorer_analog_db import model

_SUFFIX = {"a": 1e-18, "f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "meg": 1e6, "g": 1e9}


def _si(value) -> float | None:
    """SPICE scalar -> float; None when the value is a symbol/expression."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    for suffix, scale in sorted(_SUFFIX.items(), key=lambda kv: -len(kv[0])):
        if text.lower().endswith(suffix):
            try:
                return float(text[: -len(suffix)]) * scale
            except ValueError:
                return None
    try:
        return float(text)
    except ValueError:
        return None


def _bindings():
    for cid in model.list_circuit_ids():
        circuit = model.load_circuit(cid)
        if circuit.is_reference_only:
            continue
        for pdk_dir in sorted((circuit.dir / "pdk").glob("*")):
            sizing = pdk_dir / "sizing.yaml"
            if sizing.is_file():
                yield cid, pdk_dir.name, sizing


_CASES = list(_bindings())
_IDS = [f"{cid}@{pdk}" for cid, pdk, _ in _CASES]


@pytest.mark.parametrize(("cid", "pdk", "path"), _CASES, ids=_IDS)
def test_committed_default_is_inside_its_own_bounds(cid, pdk, path):
    """The shipped default must be a point the search space actually contains."""
    doc = yaml.safe_load(path.read_text())
    offenders = []
    for var in doc.get("variables") or []:
        lo, hi, default = _si(var.get("min")), _si(var.get("max")), _si(var.get("default"))
        if None in (lo, hi, default):
            continue
        if not lo <= default <= hi:
            offenders.append(f"{var['name']}={var.get('default')} outside [{var.get('min')}, {var.get('max')}]")
    assert offenders == [], f"{cid}@{pdk}: " + "; ".join(offenders)


# NOT gated here: "geometry default below the PDK registry's min_w/min_l". The
# registry floors are the binding generator's clamp targets, not process rules,
# and measurably disagree with the models — ihp-sg13g2 registers min_w=0.18u
# while the sg13g2 model card itself carries wmin=0.15e-6, so four hand-authored
# cells at 0.15u/0.178u would fail a gate that is really testing the registry.
# Reconcile the registry against the model cards before asserting on it.


# --------------------------------------------------- baseline vs the sizing the repo ships
def _si_or_str(value):
    v = _si(value)
    return v if v is not None else str(value)


@pytest.mark.parametrize(("cid", "pdk", "path"), _CASES, ids=_IDS)
def test_baseline_is_the_entry_measured_at_the_committed_sizing(cid, pdk, path):
    """The named baseline must be an entry recorded AT the committed defaults.

    This is the invariant that makes a published number mean anything: the table quotes the
    baseline, and the repo ships the defaults, so if they disagree the paper reports a design
    point nobody can reproduce. Measured 2026-08-04: amp_004_folded_cascode@tsmc-n65 shipped a
    repaired sizing (cascode gate biases moved back inside the 1.2 V rail) and a matching entry
    existed at +51.2 dB, but the pointer still named the pre-repair entry, so the table printed
    -6.5 dB. Nothing else in the pipeline compares those two things.

    Entries recorded at OTHER sizings are legitimate history and are not touched; only the
    baseline is constrained.
    """
    from spicexplorer_analog_db import scoreboard

    circuit = model.load_circuit(cid)
    base = scoreboard.baselines(circuit).get(pdk)
    if base is None:
        pytest.skip(f"{cid}@{pdk}: no baseline named")
    committed = {v["name"]: v.get("default")
                 for v in (yaml.safe_load(path.read_text()).get("variables") or [])}

    def matches(entry) -> bool:
        sizing = (entry.get("parameters") or {}).get("sizing") or {}
        shared = [k for k in sizing if k in committed]
        return bool(shared) and all(
            _si_or_str(sizing[k]) == pytest.approx(_si_or_str(committed[k]), rel=1e-4)
            if isinstance(_si_or_str(sizing[k]), float) and isinstance(_si_or_str(committed[k]), float)
            else _si_or_str(sizing[k]) == _si_or_str(committed[k])
            for k in shared)

    entries = scoreboard.load_entries(circuit, pdk)
    named = next((e for e in entries if e.get("design_id") == base), None)
    assert named is not None, f"{cid}@{pdk}: baseline {base} names no recorded entry"
    if matches(named):
        return
    better = [e["design_id"] for e in entries if matches(e)]
    assert not better, (
        f"{cid}@{pdk}: baseline {base} was NOT measured at the committed sizing, but "
        f"{better} was — the table would quote a design point the repo does not ship")
    pytest.skip(f"{cid}@{pdk}: no entry matches the committed sizing (needs a re-run, not a re-point)")
