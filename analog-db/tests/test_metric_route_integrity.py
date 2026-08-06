"""Corpus-wide integrity gate: every DECLARED metric must have a REACHABLE recipe.

A datasheet ``metrics:`` entry is a promise that the corpus can produce a number. Three
separate defects have now shipped where that promise was unbacked, and all three had the
same shape and the same silence:

* ``inoise_total`` — the closed-lane ``noise`` bench hardcoded ``iprobe=VINP``, an instance
  the self-biased (``noise_biaswrap*``) testbench templates do not contain. Spectre referred
  the noise to nothing; 19 tsmc-n65 amplifiers recorded no input-referred density at all.
* ``vos`` — declared by 10 tsmc-n65 amplifiers, never registered in the core measurement
  table, and with no calculator row on the ``dc_op`` bench. ``KeyError``.
* ``ugf_loop`` / ``gm_loop`` — every amplifier datasheet spells the loop measures the way the
  ngspice ``stb`` template emits them, but the class calculator row was keyed ``gm_loop_db``
  (the datasheet METRIC id, not its ``meas``) and ``ugf_loop`` had no row at all. ``KeyError``
  on all 32 tsmc-n65 baselines.

The failure is silent BY CONSTRUCTION. The read raises, ``CircuitRun.evaluate`` degrades that
one metric to NaN, the recorder drops the key, the entry still says ``status: ok``, and the
metrics block simply lacks it. A NaN scan cannot see it — the key is ABSENT, not NaN — and the
paper prints a blank cell. Nothing between the datasheet and the table ever asked whether a
declared metric had a recipe at all.

This module asks. It is fully OFFLINE — no simulator, no PDK, no bridge — because the question
is one of NAME RESOLUTION, and every name involved is committed:

    datasheet metric -> analysis id -> analyses/<id>.yaml -> template
                                    -> _shared/pdk/<pdk>.yaml sim_engine
        ngspice lane   the `meas` name is EMITTED by the routed class testbench template
                       (runner.parse_measures scrapes the ngspice log; a name the deck never
                       prints is a name the corpus can never record)
        spectre lane   the `meas` name is a calculator ROW NAME on the class bench entry for
                       that analysis (the OCEAN Tier-2 route, which wins when present), or a
                       name the core Tier-1 measurement registry defines (the fallback) —
                       and when it falls back, the registry recipe's KIND must match a result
                       the bench actually composes. A name that resolves onto the wrong kind
                       of result fails identically to one that does not resolve at all: the
                       read raises, the key vanishes, the cell goes blank.

``_KNOWN_GAPS`` freezes the violations that exist TODAY, with a reason each. The test asserts
EXACT equality against it, so it fails both ways: a new declared-but-unreachable metric fails,
and a gap that gets closed fails until its entry is deleted. Cataloguing, not hiding — the
entries are the tracker.

Layering: imports ``spicexplorer_core`` (the kernel, below this repo) and corpus YAML only —
never ``spicexplorer`` (the adapter above it). Everything the adapter knows that matters here
is derivable from the committed data.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml
from spicexplorer_core.measurements import registry as _registry

from spicexplorer_analog_db import model, paths

# ---------------------------------------------------------------- corpus readers

#: ngspice publishes a scalar as ``name = value`` on stdout, and ``runner.parse_measures``
#: scrapes exactly that. Two statements put a name there: an interpolating ``meas`` (whose
#: echo carries the name) and ``print`` of a scalar vector. A bare ``let`` does NOT — it
#: defines a vector nobody writes to the log — which is why ``let`` is deliberately absent
#: from these patterns.
_MEAS_STMT = re.compile(r"^\s*\.?meas(?:ure)?\s+\w+\s+([A-Za-z_]\w*)", re.IGNORECASE)
_PRINT_STMT = re.compile(r"^\s*print\s+(.*)$", re.IGNORECASE)

#: a top-level deck instance line: the name in column 0 (``.control`` bodies are indented,
#: dot-cards start with ``.``, comments with ``*``).
_INSTANCE = re.compile(r"^([A-Za-z]\w*)\s+\S")

#: Spectre analysis-template args whose VALUE names a deck INSTANCE (not a net, not a number).
#: A wrong name here is the ``inoise_total`` defect: Spectre resolves nothing and the analysis
#: still reports ok.
_INSTANCE_ARGS = ("IPROBE", "PROBE", "DEV")

#: ``analog_db._spectre_context``: the noise iprobe follows the template VARIANT, because the
#: closed-lane deck is a translation of the ngspice template. Mirrored here (as DATA, from the
#: template name) so this repo does not import the adapter.
_NOISE_IPROBE = {True: "VAC", False: "VINP"}

#: ``CircuitRun._measure_metric``: ngspice has no PSS, so the closed lane runs a native ``pss``
#: on the thd/iip3 benches and the registry recipe is swapped for its harmonic-phasor twin.
_SPECTRE_PSS_SWAP = {
    "thd": "thd_pss", "thd_pct": "thd_pss_pct", "thd_db": "thd_pss_db",
    "iip3": "iip3_pss", "iip3_dbv": "iip3_pss_dbv", "im3_dbc": "im3_pss_dbc",
}

#: calculator rows gated on context keys that ``_spectre_context`` sets ONLY for a
#: fully-differential DUT. A gated row is skipped, not rendered against the wrong nets.
_FD_ONLY_CONTEXT = {"CM_OUTP", "CM_OUTN"}

#: ``_shared/engines/spectre/analyses.yaml`` template -> the engine-neutral analysis string the
#: registry addresses its result by (``kind_default_analysis()``). The bench's ``analyses:``
#: list therefore says which KINDS of result a Tier-1 fallback can possibly read.
_TEMPLATE_RESULT = {
    "dc_op": "op", "ac": "ac", "dc_sweep": "dc", "dc_sweep_down": "dc", "temp_sweep": "dc",
    "dc_param_points": "dc",
    "noise": "noise", "tran": "tran", "pss": "pss", "stb": "stb", "pac": "pac",
    "pnoise": "pnoise",
}


def _emitted_measures(template: Path) -> set[str]:
    """The scalar names the ngspice deck writes to its log (lowercased, as the parser reads)."""
    names: set[str] = set()
    for line in template.read_text().splitlines():
        stmt = _MEAS_STMT.match(line)
        if stmt:
            names.add(stmt.group(1).lower())
            continue
        printed = _PRINT_STMT.match(line)
        if printed:
            names.update(tok.lower() for tok in re.split(r"[\s,]+", printed.group(1).strip()) if tok)
    return names


def _deck_instances(template: Path) -> set[str]:
    """The top-level instance names the ngspice deck defines (lowercased)."""
    return {
        m.group(1).lower()
        for m in (_INSTANCE.match(line) for line in template.read_text().splitlines())
        if m
    }


def _pdk_engine(pdk: str) -> str:
    doc = yaml.safe_load((paths.shared_root() / "pdk" / f"{pdk}.yaml").read_text()) or {}
    return str(doc.get("sim_engine", "ngspice"))


def _bench_map(class_id: str) -> dict | None:
    """``{analysis id: bench}`` from the class Spectre bench map; None when the class has none."""
    path = paths.classes_root() / class_id / "spectre-benches.yaml"
    if not path.is_file():
        return None
    return (yaml.safe_load(path.read_text()) or {}).get("benches") or {}


def _is_differential(circuit) -> bool:
    """Mirror ``analog_db.differential_output``: a voutp/voutn pair and no vout."""
    ports = {str(p).lower() for p in circuit.ports}
    return "voutp" in ports and "voutn" in ports and "vout" not in ports


def _calculator_row_names(bench: dict, *, differential: bool) -> set[str]:
    """The row names this bench actually renders for this DUT (``requires:`` gating applied)."""
    names: set[str] = set()
    for row in bench.get("calculator") or []:
        needs = {str(n) for n in (row.get("requires") or [])}
        if needs & _FD_ONLY_CONTEXT and not differential:
            continue
        names.add(str(row.get("name", row.get("expr", ""))))
    return names


# ---------------------------------------------------------------- the gate


def _route_violations(circuit, pdk: str) -> set[str]:
    """``{"<metric>(meas=<name>): <reason>"}`` for one (circuit, pdk) binding."""
    engine = _pdk_engine(pdk)
    analyses = circuit.analysis_files()
    differential = _is_differential(circuit)
    bench_map = _bench_map(circuit.klass)
    table = _registry.measurement_table()
    kind_analysis = _registry.kind_default_analysis()
    out: set[str] = set()

    for name, spec in (circuit.datasheet().get("metrics") or {}).items():
        spec = spec or {}
        aid = spec.get("analysis")
        meas = (spec.get("extract") or {}).get("meas")
        # A metric with NEITHER is a spec-only / derived entry (`formula:`, paper targets a
        # frozen-switch .ac cannot measure) — it promises no measurement, so it owes none.
        if not aid and not meas:
            continue
        tag = f"{name}(meas={meas})"
        if not meas:
            out.add(f"{tag}: analysis {aid!r} declared but extract.meas is missing")
            continue
        if not aid:
            out.add(f"{tag}: extract.meas declared but no analysis to run it on")
            continue
        if aid not in analyses:
            out.add(f"{tag}: analysis {aid!r} has no circuits/<id>/analyses/{aid}.yaml")
            continue

        template_id = str((circuit.analysis(aid) or {}).get("template", aid))
        if engine != "spectre":
            template = model.resolve_template(circuit.klass, template_id)
            if template is None:
                out.add(f"{tag}: template {template_id!r} ({aid}) resolves to no file")
                continue
            if meas.lower() not in _emitted_measures(template):
                out.add(
                    f"{tag}: the {template_id!r} testbench template never prints it, so the "
                    f"ngspice log parser can never record it"
                )
            continue

        if bench_map is None:
            out.add(f"{tag}: class {circuit.klass!r} ships no spectre-benches.yaml")
            continue
        bench = bench_map.get(aid)
        if bench is None:
            out.add(f"{tag}: no {aid!r} bench entry in the {circuit.klass} spectre-benches.yaml")
            continue
        candidates = {meas}
        if aid in ("thd", "iip3") and meas in _SPECTRE_PSS_SWAP:
            candidates.add(_SPECTRE_PSS_SWAP[meas])
        rows = _calculator_row_names(bench, differential=differential)
        if candidates & rows:
            continue  # the OCEAN calculator route, which wins whenever a row exists
        fallback = next((m for m in sorted(candidates) if m in table), None)
        if fallback is None:
            out.add(
                f"{tag}: no calculator row on the {aid!r} bench and no core registry entry "
                f"(bench rows: {sorted(rows) or 'none'})"
            )
            continue
        # It falls back to Tier-1 — so the bench must actually COMPOSE the kind of result
        # that recipe reads. `gain_cl` is an AC transfer; asking for it off a clocked
        # transient bench resolves the NAME and then reads an `ac` result that the run never
        # produced.
        wants = str((spec.get("extract") or {}).get("analysis")
                    or kind_analysis.get(table[fallback][0], ""))
        composed = {_TEMPLATE_RESULT.get(str(e.get("template", ""))) for e in (bench.get("analyses") or [])}
        if wants and wants not in composed:
            out.add(
                f"{tag}: the registry recipe reads a {wants!r} result but the {aid!r} bench "
                f"composes {sorted(x for x in composed if x)}"
            )
    return out


def _bench_arg_violations(circuit, pdk: str) -> set[str]:
    """Spectre bench args that name a deck instance the routed template does not define."""
    if _pdk_engine(pdk) != "spectre":
        return set()
    bench_map = _bench_map(circuit.klass)
    if bench_map is None:
        return set()
    out: set[str] = set()
    for aid in circuit.analysis_files():
        bench = bench_map.get(aid)
        if not bench:
            continue
        template_id = str((circuit.analysis(aid) or {}).get("template", aid))
        template = model.resolve_template(circuit.klass, template_id)
        if template is None:
            continue
        instances = _deck_instances(template)
        for entry in bench.get("analyses") or []:
            for key, raw in (entry.get("args") or {}).items():
                if key not in _INSTANCE_ARGS:
                    continue
                value = str(raw)
                if value == "$NOISE_IPROBE":
                    value = _NOISE_IPROBE[template_id.startswith("noise_biaswrap")]
                elif value.startswith("$"):
                    continue  # a bench param, not an instance name
                if value.lower() not in instances:
                    out.add(
                        f"{aid}/{key}={value}: the {template_id!r} deck defines no such "
                        f"instance, so the closed lane probes nothing"
                    )
        # A single-injection loop probe cannot break an ANTIPHASE marker pair: half the loop
        # stays closed and Spectre returns a ~0 dB return ratio with no margins. Derived, not
        # hardcoded: compare the markers the routed deck defines against the ones the bench
        # actually probes.
        if aid == "stb":
            markers = {i for i in instances if i.startswith("viprb")}
            probed = {
                str((e.get("args") or {}).get("PROBE", "")).lower()
                for e in (bench.get("analyses") or [])
            }
            unprobed = markers - probed
            if markers and unprobed:
                out.add(
                    f"stb/PROBE: the {template_id!r} deck breaks the loop with "
                    f"{sorted(markers)} but the bench probes only {sorted(markers & probed)} — "
                    f"{sorted(unprobed)} keeps its half of the loop closed"
                )
    return out


# ---------------------------------------------------------------- the frozen gaps

#: MEASURED against the corpus as it stands. Each entry is an open defect, not an exemption:
#: delete it when the route is bound, and this module will tell you if you delete one early.
_KNOWN_GAPS: dict[tuple[str, str], set[str]] = {
    # (CLOSED 2026-08-05: `dc_cm_bias_sweep` now has an amplifier spectre-benches entry —
    # the `dc_param_points` 5-point parameter sweep + the cm_interior_pts calculator row —
    # so amp_029/amp_030/amp_034 all route on the closed lane. The old entry is deleted, as
    # this registry's contract demands.)
    #
    # The cmfb class has a tsmc-n65 BINDING but no Spectre bench map, so not one of its eight
    # measured metrics has a closed-lane route. Latent, not yet published: neither cell has a
    # tsmc-n65 scoreboard entry — the bindings have never been harvested. They would come back
    # empty on the day someone runs them.
    ("cmfb_001_ideal_rsense_servo", "tsmc-n65"): {
        f"{m}(meas={m}): class 'cmfb' ships no spectre-benches.yaml"
        for m in (
            "cmfb_slope", "gain_servo_db", "bw_servo_hz", "ugf_servo_hz",
            "vcmfb_nat", "step_delta_v", "ring_v", "t_cm_settle", "i_supply",
        )
    },
    # cmfb_002 is the same class-level gap, on a cell whose datasheet declares five more
    # measured metrics (the transistor-level 5T servo's sense range + actuator swing).
    # cmfb_003_5t_nmos_input is deliberately NOT listed: it binds gf180mcu/ihp-sg13g2/sky130
    # only (all ngspice), so it has no closed lane to be missing a bench map on — add it the
    # day it gains a tsmc-n65 binding.
    ("cmfb_002_5t_pmos_input", "tsmc-n65"): {
        f"{m}(meas={m}): class 'cmfb' ships no spectre-benches.yaml"
        for m in (
            "cmfb_slope", "gain_servo_db", "bw_servo_hz", "ugf_servo_hz",
            "vcmfb_nat", "vcmfb_min", "vcmfb_max", "sense_lo", "sense_hi", "r_sense_in",
            "step_delta_v", "ring_v", "t_cm_settle", "i_supply",
        )
    },
    # The clocked ia transient benches carry NO calculator rows (their figures are in-deck
    # ngspice `.control` maths that Spectre never executes) and their names are not registry
    # recipes either. All three are absent from ia_002's tsmc-n65 entry.
    ("ia_002_fan_chopper_simple", "tsmc-n65"): {
        "v_ripple_pp(meas=v_ripple_pp): no calculator row on the 'tran_chopper_ripple' bench "
        "and no core registry entry (bench rows: none)",
        "vos_residual(meas=vos_residual): no calculator row on the 'tran_chopper_ripple' bench "
        "and no core registry entry (bench rows: none)",
        "zin_chop_ohm(meas=zin_chop_ohm): no calculator row on the 'tran_zin_chopped' bench "
        "and no core registry entry (bench rows: none)",
        # resolves by NAME and then reads nothing: `gain_cl` is the AC closed-loop transfer,
        # but this bench is the clocked transient whose in-deck window arithmetic Spectre
        # never runs. Absent from ia_002's tsmc-n65 entry, present on its ngspice rows.
        "gain_cl(meas=gain_cl): the registry recipe reads a 'ac' result but the "
        "'tran_chopper_ripple' bench composes ['op', 'tran']",
    },
}

#: The single-probe `stb` bench against the antiphase `stb_diff` deck (8 fully-differential
#: amplifiers on tsmc-n65). The adapter now REFUSES this composition rather than publish the
#: ~0 dB return ratio it used to, so all four loop metrics on these cells are unreachable on
#: the closed lane until a `diffstbprobe` is emitted across the marker pair.
_STB_DIFF_GAP = (
    "stb/PROBE: the 'stb_diff' deck breaks the loop with ['viprb', 'viprbm'] but the bench "
    "probes only ['viprb'] — ['viprbm'] keeps its half of the loop closed"
)
_KNOWN_ARG_GAPS: dict[tuple[str, str], set[str]] = {
    (cid, "tsmc-n65"): {_STB_DIFF_GAP}
    # amp_020 (deleted) is no longer iterated by _bindings(). amp_029 IS iterated again: it is
    # `published: false` (de-published), not `kind: reference`, so it stays a verifiable FD
    # binding that hits the same single-probe gap as its siblings.
    for cid in (
        "amp_023_fer_fd2s", "amp_025_hsu_classab_ota",
        "amp_026_fan_chopper_ota", "amp_027_fan_rrl_ota",
        "amp_029_two_stage_miller_comp",
        "amp_030_miller_cmfb_composite", "amp_031_srmc_core_cmfb",
        "amp_034_fan_chopper_cmfb",
    )
}


def _bindings():
    for cid in model.list_circuit_ids():
        circuit = model.load_circuit(cid)
        if circuit.is_reference_only:
            continue
        for pdk_dir in sorted((circuit.dir / "pdk").glob("*")):
            if pdk_dir.is_dir() and (paths.shared_root() / "pdk" / f"{pdk_dir.name}.yaml").is_file():
                yield circuit, pdk_dir.name


_CASES = list(_bindings())
_IDS = [f"{c.id}@{pdk}" for c, pdk in _CASES]


@pytest.mark.parametrize(("circuit", "pdk"), _CASES, ids=_IDS)
def test_declared_metric_resolves_to_a_recipe_the_routed_engine_can_compute(circuit, pdk):
    """A datasheet metric the routed engine cannot produce is a blank cell, not a number."""
    found = _route_violations(circuit, pdk)
    known = _KNOWN_GAPS.get((circuit.id, pdk), set())
    new = found - known
    closed = known - found
    assert not new, f"{circuit.id}@{pdk}: unreachable metric route — " + "; ".join(sorted(new))
    assert not closed, (
        f"{circuit.id}@{pdk}: _KNOWN_GAPS lists a route that now resolves — delete it: "
        + "; ".join(sorted(closed))
    )


@pytest.mark.parametrize(("circuit", "pdk"), _CASES, ids=_IDS)
def test_spectre_bench_probes_an_instance_the_routed_deck_actually_defines(circuit, pdk):
    """A probe/iprobe/sweep-device arg naming a nonexistent instance measures nothing, quietly."""
    found = _bench_arg_violations(circuit, pdk)
    known = _KNOWN_ARG_GAPS.get((circuit.id, pdk), set())
    new = found - known
    closed = known - found
    assert not new, f"{circuit.id}@{pdk}: bench probes nothing — " + "; ".join(sorted(new))
    assert not closed, (
        f"{circuit.id}@{pdk}: _KNOWN_ARG_GAPS lists a probe that now resolves — delete it: "
        + "; ".join(sorted(closed))
    )


def test_known_gap_registries_name_only_live_bindings():
    """A gap entry for a binding that no longer exists is rot — the gate would never see it."""
    live = {(c.id, pdk) for c, pdk in _CASES}
    stale = sorted((set(_KNOWN_GAPS) | set(_KNOWN_ARG_GAPS)) - live)
    assert stale == [], f"_KNOWN_GAPS names bindings that are not in the corpus: {stale}"
