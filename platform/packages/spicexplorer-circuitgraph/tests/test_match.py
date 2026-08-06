"""Functional-subcircuit detection — subgraph monomorphism + grouping + annotation.

Covers: template-library loading (manifest + the shipped catalogue), simple-mirror detection,
the array-sharing-a-reference case (multi-output grouping), subsumption (simple inside cascode),
equal-set alternates, the supply / polarity / bulk match knobs, role annotation, and an
integration check against the real example OTAs.
"""

from __future__ import annotations

import logging
import re
import textwrap
from pathlib import Path

import pytest
import yaml
from spicexplorer_circuitgraph import (
    CircuitGraph,
    MatchOptions,
    SubcircuitTemplate,
    TemplateLibrary,
    annotate_subcircuits,
    default_current_mirror_library,
    default_subcircuit_library,
    find_subcircuits,
    graphs_equivalent,
    group_matches,
    netlists_equivalent,
)
from spicexplorer_circuitgraph.model.nodes import (
    DETERMINISTIC_ROLES,
    RESIDUE_ROLES,
    StructuralRole,
)
from spicexplorer_core.spice_engine import NetlistView

# --- inline template netlists (NMOS sink referenced to VSS, PMOS source to VDD) ------------------
SIMPLE_NMOS = """\
** simple nmos current mirror
XM1 iin iin VSS VSS sg13_lv_nmos w=0.15u l=0.13u
XM2 iout iin VSS VSS sg13_lv_nmos w=0.15u l=0.13u
.end
"""

SIMPLE_PMOS = """\
** simple pmos current mirror
XM1 iout iin VDD VDD sg13_lv_pmos w=0.15u l=0.13u
XM2 iin iin VDD VDD sg13_lv_pmos w=0.15u l=0.13u
.end
"""

CASCODE_NMOS = """\
** cascode nmos current mirror
XM1 net2 net1 VSS VSS sg13_lv_nmos
XM2 net1 net1 VSS VSS sg13_lv_nmos
XM3 iout iin net1 VSS sg13_lv_nmos
XM4 iin iin net2 VSS sg13_lv_nmos
.end
"""

# A clean cascode whose INTERNAL node `mid` (template net2: drain of the bottom device, source of the
# cascode device) is also loaded by a stray cap — so `mid` carries a device beyond the template's.
# Under plain monomorphism this still reads as a cascode (false positive); match_internal_exact
# rejects it because the internal node is no longer private to the sub-circuit. `mid` ↔ template net2,
# `g1` ↔ net1; the cap can never fill a MOS slot, it only raises mid's degree from 2 to 3.
CASCODE_NMOS_TAPPED_INTERNAL = """\
** cascode nmos current mirror with a parasitic cap on the internal cascode node
XM1 mid g1 VSS VSS sg13_lv_nmos
XM2 g1 g1 VSS VSS sg13_lv_nmos
XM3 iout iin g1 VSS sg13_lv_nmos
XM4 iin iin mid VSS sg13_lv_nmos
C1 mid VSS 10f
.end
"""

# A tail-biased NMOS differential pair (the `CM_tail` shared-source dependent template). Every net is
# a declared port — the pair has no private internal node — so internal-exactness never constrains it.
DIFF_PAIR_NMOS = """\
** nmos differential pair (tail on CM_tail)
XM1 drain_p vinp CM_tail VSS sg13_lv_nmos
XM2 drain_n vinn CM_tail VSS sg13_lv_nmos
.end
"""


def _g(netlist: str, name: str = "host") -> CircuitGraph:
    # spicelib requires the first line to be a title/comment — prepend one.
    text = "* test netlist\n" + textwrap.dedent(netlist)
    return CircuitGraph.from_netlist(NetlistView.from_string(text), name=name)


def _write_template(tmp_path, name: str, netlist: str) -> Path:
    p = tmp_path / f"{name}.spice"
    p.write_text(textwrap.dedent(netlist))
    return p


def _simple_lib(tmp_path) -> TemplateLibrary:
    """A two-template library (simple nmos + simple pmos) authored on disk."""
    nmos = _write_template(tmp_path, "simple_nmos", SIMPLE_NMOS)
    pmos = _write_template(tmp_path, "simple_pmos", SIMPLE_PMOS)
    return TemplateLibrary(
        [
            SubcircuitTemplate(
                id="cm.nmos.simple",
                netlist_path=nmos,
                mirror_class="simple",
                polarity="nmos",
                ports={"supply": "VSS", "ref_in": "iin", "out": "iout"},
            ),
            SubcircuitTemplate(
                id="cm.pmos.simple",
                netlist_path=pmos,
                mirror_class="simple",
                polarity="pmos",
                ports={"supply": "VDD", "ref_in": "iin", "out": "iout"},
            ),
        ],
        family="current_mirror",
    )


def _cascode_only_lib(tmp_path) -> TemplateLibrary:
    """A single-template library (cascode nmos only) — isolates internal-node behavior."""
    casc = _write_template(tmp_path, "cascode_nmos", CASCODE_NMOS)
    return TemplateLibrary(
        [
            SubcircuitTemplate(
                id="cm.nmos.cascode", netlist_path=casc, mirror_class="cascode", polarity="nmos",
                ports={"supply": "VSS", "ref_in": "iin", "out": "iout"},
            )
        ]
    )


def _diffpair_lib(tmp_path) -> TemplateLibrary:
    """A simple NMOS mirror (independent) + an NMOS differential pair anchored to a mirror output."""
    mirror = _write_template(tmp_path, "simple_nmos", SIMPLE_NMOS)
    pair = _write_template(tmp_path, "diff_pair_nmos", DIFF_PAIR_NMOS)
    return TemplateLibrary(
        [
            SubcircuitTemplate(
                id="cm.nmos.simple", netlist_path=mirror, mirror_class="simple", polarity="nmos",
                family="current_mirror",
                ports={"supply": "VSS", "ref_in": "iin", "out": "iout"},
            ),
            SubcircuitTemplate(
                id="dp.nmos.simple", netlist_path=pair, mirror_class="differential_pair",
                polarity="nmos", family="differential_pair",
                ports={
                    "supply": "VSS", "in_p": "vinp", "in_n": "vinn",
                    "CM_tail": "CM_tail", "out_n": "drain_n", "out_p": "drain_p",
                },
            ),
        ]
    )


def _two_mirror_diffpair_lib(tmp_path, dp_tail_sources: list[str]) -> TemplateLibrary:
    """Simple + cascode NMOS mirrors + an NMOS diff pair with a configurable ``tail_sources`` list.

    Both mirror ids exist in the library, so the allow-list selects *which known mirror* may anchor
    the pair (no unknown-id warning) — the tail in :data:`OTA_5T_NMOS_INPUT` lands on the *simple*
    mirror's output.
    """
    mirror = _write_template(tmp_path, "simple_nmos", SIMPLE_NMOS)
    casc = _write_template(tmp_path, "cascode_nmos", CASCODE_NMOS)
    pair = _write_template(tmp_path, "diff_pair_nmos", DIFF_PAIR_NMOS)
    return TemplateLibrary(
        [
            SubcircuitTemplate(
                id="cm.nmos.simple", netlist_path=mirror, mirror_class="simple", polarity="nmos",
                family="current_mirror", ports={"supply": "VSS", "ref_in": "iin", "out": "iout"},
            ),
            SubcircuitTemplate(
                id="cm.nmos.cascode", netlist_path=casc, mirror_class="cascode", polarity="nmos",
                family="current_mirror", ports={"supply": "VSS", "ref_in": "iin", "out": "iout"},
            ),
            SubcircuitTemplate(
                id="dp.nmos.simple", netlist_path=pair, mirror_class="differential_pair",
                polarity="nmos", family="differential_pair", tail_sources=dp_tail_sources,
                ports={
                    "supply": "VSS", "in_p": "vinp", "in_n": "vinn",
                    "CM_tail": "CM_tail", "out_n": "drain_n", "out_p": "drain_p",
                },
            ),
        ]
    )


# A 5T-OTA NMOS core: input pair (XM1/XM2) tail-biased by an NMOS mirror (diode XM6 → output XM5,
# whose drain IS the tail), with a PMOS active-load mirror on top.
OTA_5T_NMOS_INPUT = """\
XM1 outm vinp tail vss sg13_lv_nmos
XM2 vout vinn tail vss sg13_lv_nmos
XM3 outm outm vdd vdd sg13_lv_pmos
XM4 vout outm vdd vdd sg13_lv_pmos
XM5 tail ibias vss vss sg13_lv_nmos
XM6 ibias ibias vss vss sg13_lv_nmos
.end
"""


def _cascode_lib(tmp_path) -> TemplateLibrary:
    nmos = _write_template(tmp_path, "simple_nmos", SIMPLE_NMOS)
    casc = _write_template(tmp_path, "cascode_nmos", CASCODE_NMOS)
    return TemplateLibrary(
        [
            SubcircuitTemplate(
                id="cm.nmos.simple", netlist_path=nmos, mirror_class="simple", polarity="nmos",
                ports={"supply": "VSS", "ref_in": "iin", "out": "iout"},
            ),
            SubcircuitTemplate(
                id="cm.nmos.cascode", netlist_path=casc, mirror_class="cascode", polarity="nmos",
                ports={"supply": "VSS", "ref_in": "iin", "out": "iout"},
            ),
        ]
    )


# ------------------------------------------------------------------------------------------------
# Template library
# ------------------------------------------------------------------------------------------------
def test_template_library_from_disk(tmp_path):
    lib = _simple_lib(tmp_path)
    assert len(lib) == 2
    t = lib.get("cm.nmos.simple")
    assert t.polarity == "nmos"
    assert t.ports["supply"] == "VSS"
    assert t.graph.component_count == 2  # builds the graph from the netlist
    assert lib.filter(polarity="pmos")[0].id == "cm.pmos.simple"


def test_template_library_rejects_duplicate_ids(tmp_path):
    nmos = _write_template(tmp_path, "simple_nmos", SIMPLE_NMOS)
    dup = SubcircuitTemplate(id="x", netlist_path=nmos)
    with pytest.raises(ValueError, match="duplicate template id"):
        TemplateLibrary([dup, SubcircuitTemplate(id="x", netlist_path=nmos)])


def test_from_manifest(tmp_path):
    _write_template(tmp_path, "simple_nmos", SIMPLE_NMOS)
    (tmp_path / "manifest.yaml").write_text(
        textwrap.dedent(
            """\
            schema: spicexplorer/subcircuit-template-library@1
            family: current_mirror
            templates:
              - id: cm.nmos.simple
                class: simple
                polarity: nmos
                netlist: simple_nmos.spice
                ports: {supply: VSS, ref_in: iin, out: iout}
            """
        )
    )
    lib = TemplateLibrary.from_manifest(tmp_path / "manifest.yaml")
    assert [t.id for t in lib] == ["cm.nmos.simple"]
    assert lib.get("cm.nmos.simple").netlist_path.name == "simple_nmos.spice"
    # both DR-3 / match_bulk manifest extensions are optional — absent keys default off/empty
    assert lib.get("cm.nmos.simple").match_bulk is False
    assert lib.get("cm.nmos.simple").rules_paths == ()


def test_from_manifest_parses_match_bulk_and_rules(tmp_path):
    _write_template(tmp_path, "simple_nmos", SIMPLE_NMOS)
    (tmp_path / "rules").mkdir()
    (tmp_path / "rules" / "current_mirror.md").write_text("# rules\n")
    (tmp_path / "manifest.yaml").write_text(
        textwrap.dedent(
            """\
            schema: spicexplorer/subcircuit-template-library@1
            family: current_mirror
            rules:
              - path: rules/current_mirror.md
                title: "CM sizing + detection"
            templates:
              - id: cm.nmos.simple
                class: simple
                polarity: nmos
                netlist: simple_nmos.spice
                match_bulk: true
                ports: {supply: VSS, ref_in: iin, out: iout}
            """
        )
    )
    t = TemplateLibrary.from_manifest(tmp_path / "manifest.yaml").get("cm.nmos.simple")
    assert t.match_bulk is True
    # the manifest-level rules block rides on every template of the family, resolved absolute
    assert t.rules_paths == ((tmp_path / "rules" / "current_mirror.md").resolve(),)


# ------------------------------------------------------------------------------------------------
# Core detection
# ------------------------------------------------------------------------------------------------
def test_simple_nmos_detected(tmp_path):
    # 5T-OTA-like core: NMOS tail mirror (M5 copy / M6 diode) + PMOS load mirror (M3 diode / M4).
    host = _g(
        """\
        XM1 outm vinp tail vss sg13_lv_nmos
        XM2 vout vinn tail vss sg13_lv_nmos
        XM3 outm outm vdd vdd sg13_lv_pmos
        XM4 vout outm vdd vdd sg13_lv_pmos
        XM5 tail ibias vss vss sg13_lv_nmos
        XM6 ibias ibias vss vss sg13_lv_nmos
        .end
        """
    )
    groups = group_matches(find_subcircuits(host, _simple_lib(tmp_path)))
    by_pol = {g.polarity: g for g in groups}
    assert set(by_pol) == {"nmos", "pmos"}
    assert by_pol["nmos"].reference_device == "XM6"  # the diode
    assert by_pol["nmos"].output_devices == ("XM5",)
    assert by_pol["pmos"].reference_device == "XM3"
    assert by_pol["pmos"].output_devices == ("XM4",)


def test_array_shares_reference(tmp_path):
    # One diode reference (XM0) feeding THREE copies — the array-of-mirrors case.
    host = _g(
        """\
        XM0 iref iref vss vss sg13_lv_nmos
        XM1 o1 iref vss vss sg13_lv_nmos
        XM2 o2 iref vss vss sg13_lv_nmos
        XM3 o3 iref vss vss sg13_lv_nmos
        .end
        """
    )
    raw = find_subcircuits(host, _simple_lib(tmp_path))
    assert len(raw) == 3  # three distinct embeddings, all reusing XM0
    assert all(m.reference_device == "XM0" for m in raw)

    groups = group_matches(raw)
    assert len(groups) == 1  # collapsed into one multi-output mirror
    grp = groups[0]
    assert grp.reference_device == "XM0"
    assert grp.output_devices == ("XM1", "XM2", "XM3")
    assert set(grp.devices) == {"XM0", "XM1", "XM2", "XM3"}


def test_lone_diode_is_not_a_mirror(tmp_path):
    # A diode whose gate feeds only a cascode source (no sibling sharing the rail) → no simple match.
    host = _g(
        """\
        XM0 iref iref vss vss sg13_lv_nmos
        XM1 out iref iref vss sg13_lv_nmos
        .end
        """
    )
    assert find_subcircuits(host, _simple_lib(tmp_path)) == []


# ------------------------------------------------------------------------------------------------
# Resolution — subsumption + alternates
# ------------------------------------------------------------------------------------------------
def test_cascode_subsumes_simple(tmp_path):
    host = _g(CASCODE_NMOS)
    groups = group_matches(find_subcircuits(host, _cascode_lib(tmp_path)))
    assert len(groups) == 1
    grp = groups[0]
    assert grp.mirror_class == "cascode"
    assert set(grp.devices) == {"XM1", "XM2", "XM3", "XM4"}
    # the inner simple pair is reported as subsumed, not as a separate mirror
    assert any(s.template_id == "cm.nmos.simple" for s in grp.subsumed)


def test_equal_set_collision_becomes_alternate(tmp_path):
    # Two templates that are the SAME topology over the same devices → one primary + one alternate.
    casc = _write_template(tmp_path, "a", CASCODE_NMOS)
    casc2 = _write_template(tmp_path, "b", CASCODE_NMOS)
    lib = TemplateLibrary(
        [
            SubcircuitTemplate(id="cm.nmos.cascode", netlist_path=casc, mirror_class="cascode",
                               polarity="nmos", ports={"supply": "VSS", "ref_in": "iin", "out": "iout"}),
            SubcircuitTemplate(id="cm.nmos.improved_wilson", netlist_path=casc2,
                               mirror_class="improved_wilson", polarity="nmos",
                               ports={"supply": "VSS", "ref_in": "iin", "out": "iout"}),
        ]
    )
    groups = group_matches(find_subcircuits(_g(CASCODE_NMOS), lib))
    assert len(groups) == 1
    assert groups[0].mirror_class == "cascode"  # canonical wins
    assert [a.template_id for a in groups[0].alternates] == ["cm.nmos.improved_wilson"]


# ------------------------------------------------------------------------------------------------
# Match knobs: supply / polarity / bulk
# ------------------------------------------------------------------------------------------------
def test_supply_anchoring_requires_named_rail(tmp_path):
    # The shared source is a SIGNAL net, not a supply rail.
    host = _g(
        """\
        XM1 iin iin shared body sg13_lv_nmos
        XM2 iout iin shared body sg13_lv_nmos
        .end
        """
    )
    lib = _simple_lib(tmp_path)
    # default match_supply=True: the template's VSS rail can't land on a signal net → no match
    assert find_subcircuits(host, lib) == []
    # match_supply=False: rails no longer anchored → the structure matches
    assert len(find_subcircuits(host, lib, match_supply=False)) == 1


def test_polarity_default_vs_agnostic(tmp_path):
    # A PMOS mirror must NOT match the NMOS template by default, but does when polarity is ignored.
    pmos_host = _g(
        """\
        XM1 iout iin vdd vdd sg13_lv_pmos
        XM2 iin iin vdd vdd sg13_lv_pmos
        .end
        """
    )
    nmos_only = TemplateLibrary(
        [
            SubcircuitTemplate(
                id="cm.nmos.simple",
                netlist_path=_write_template(tmp_path, "simple_nmos", SIMPLE_NMOS),
                mirror_class="simple", polarity="nmos",
                ports={"supply": "VSS", "ref_in": "iin", "out": "iout"},
            )
        ]
    )
    assert find_subcircuits(pmos_host, nmos_only) == []
    # provisioned polarity-agnostic search (also drop supply anchoring so VSS↔vdd is allowed)
    assert len(
        find_subcircuits(pmos_host, nmos_only, match_polarity=False, match_supply=False)
    ) == 1


def test_bulk_ignored_by_default(tmp_path):
    # Bulk on a separate body net (not the rail).
    host = _g(
        """\
        XM1 iin iin vss body sg13_lv_nmos
        XM2 iout iin vss body sg13_lv_nmos
        .end
        """
    )
    lib = _simple_lib(tmp_path)
    assert len(find_subcircuits(host, lib)) == 1  # default match_bulk=False → found
    assert find_subcircuits(host, lib, match_bulk=True) == []  # strict bulk → body net breaks it


def test_options_override(tmp_path):
    host = _g(SIMPLE_NMOS)
    opts = MatchOptions(match_supply=True, match_polarity=True, match_bulk=True)
    assert len(find_subcircuits(host, _simple_lib(tmp_path), options=opts)) == 1


# ------------------------------------------------------------------------------------------------
# Match knob: internal-node exactness (private internal nodes must not pick up extra host devices)
# ------------------------------------------------------------------------------------------------
def test_internal_exact_rejects_tapped_internal_node(tmp_path):
    # A cascode whose internal cascode node carries a stray cap. Plain monomorphism calls it a
    # cascode (wrong topology); the default (match_internal_exact=True) must reject it.
    host = _g(CASCODE_NMOS_TAPPED_INTERNAL)
    lib = _cascode_only_lib(tmp_path)
    # loose monomorphism: false positive (internal node not checked)
    assert len(find_subcircuits(host, lib, match_internal_exact=False)) == 1
    assert find_subcircuits(host, lib) == []  # default is strict → rejected


def test_internal_exact_keeps_clean_cascode(tmp_path):
    # Positive control: a clean cascode (internal nodes private) still matches under the strict flag.
    host = _g(CASCODE_NMOS)
    lib = _cascode_only_lib(tmp_path)
    assert len(find_subcircuits(host, lib, match_internal_exact=True)) == 1


def test_internal_exact_leaves_ports_free(tmp_path):
    # Ports are the sub-circuit's interface — they MUST stay free to fan out even under the strict
    # flag. The shared diode/gate node (ref_in port) here feeds three copies; all three still match.
    host = _g(
        """\
        XM0 iref iref vss vss sg13_lv_nmos
        XM1 o1 iref vss vss sg13_lv_nmos
        XM2 o2 iref vss vss sg13_lv_nmos
        XM3 o3 iref vss vss sg13_lv_nmos
        .end
        """
    )
    raw = find_subcircuits(host, _simple_lib(tmp_path), match_internal_exact=True)
    assert len(raw) == 3
    assert all(m.reference_device == "XM0" for m in raw)


def test_internal_exact_threads_through_annotate(tmp_path):
    host = _g(CASCODE_NMOS_TAPPED_INTERNAL)
    groups = annotate_subcircuits(host, _cascode_only_lib(tmp_path), match_internal_exact=True)
    assert groups == []


# ------------------------------------------------------------------------------------------------
# Dependent (anchored) templates: the differential pair + its `CM_tail` current-mirror dependency
# ------------------------------------------------------------------------------------------------
def test_diff_pair_detected_when_tail_on_mirror_output(tmp_path):
    # The pair's shared tail IS the NMOS mirror's output net → the pair is admitted.
    groups = group_matches(find_subcircuits(_g(OTA_5T_NMOS_INPUT), _diffpair_lib(tmp_path)))
    by_fam = {g.family: g for g in groups}
    assert "differential_pair" in by_fam
    dp = by_fam["differential_pair"]
    assert set(dp.devices) == {"XM1", "XM2"}
    assert dp.ports["CM_tail"] == "tail"  # anchored on the mirror output
    # the tail mirror itself is still reported independently
    cm = next(g for g in groups if g.family == "current_mirror" and g.polarity == "nmos")
    assert cm.output_devices == ("XM5",) and cm.ports["out"] == "tail"


def test_diff_pair_rejected_when_tail_not_a_mirror_output(tmp_path):
    # Same pair, but the tail is tied straight to VSS through a resistor — no biasing mirror, so the
    # `CM_tail` dependency is unmet and the pair must NOT be reported (two common-source devices ≠ pair).
    host = _g(
        """\
        XM1 outm vinp tail vss sg13_lv_nmos
        XM2 vout vinn tail vss sg13_lv_nmos
        XM3 outm outm vdd vdd sg13_lv_pmos
        XM4 vout outm vdd vdd sg13_lv_pmos
        RT tail vss 1k
        .end
        """
    )
    groups = group_matches(find_subcircuits(host, _diffpair_lib(tmp_path)))
    assert all(g.family != "differential_pair" for g in groups)


def test_diff_pair_needs_distinct_gates_not_a_mirror(tmp_path):
    # A simple current mirror (shared gate) must never be mis-read as a differential pair: the pair's
    # two gate nets are distinct, so monomorphism cannot fold them onto the mirror's single gate.
    host = _g(
        """\
        XM5 tail ibias vss vss sg13_lv_nmos
        XM6 ibias ibias vss vss sg13_lv_nmos
        XMa o1 tail vss vss sg13_lv_nmos
        XMb o2 tail vss vss sg13_lv_nmos
        .end
        """
    )
    # XMa/XMb share gate `tail` (a mirror output) — even though tail is a valid anchor, they are a
    # mirror, not a pair (no two distinct input gates).
    groups = group_matches(find_subcircuits(host, _diffpair_lib(tmp_path)))
    assert all(g.family != "differential_pair" for g in groups)


def test_diff_pair_roles_assigned(tmp_path):
    host = _g(OTA_5T_NMOS_INPUT)
    annotate_subcircuits(host, _diffpair_lib(tmp_path))
    roles = {c.name: c.structural_role for c in host.get_components()}
    assert roles["XM1"] == StructuralRole.MOS_DIFFERENTIAL_PAIR
    assert roles["XM2"] == StructuralRole.MOS_DIFFERENTIAL_PAIR
    # XM5 is the mirror output that *biases the pair's tail* (its drain is the pair's common-source
    # node) — so it earns the more specific tail-current-source role rather than the generic mirror
    # output label. XM6, the diode reference that sets the bias, stays distinctly tagged so a
    # sizer/LLM can tell which device the bias current is solved from.
    assert roles["XM5"] == StructuralRole.MOS_TAIL_CURRENT_SOURCE
    assert roles["XM6"] == StructuralRole.MOS_CURRENT_MIRROR_REFERENCE
    # every deterministically-written role is in the documented DETERMINISTIC_ROLES partition.
    assert {r for r in roles.values() if r is not None} <= DETERMINISTIC_ROLES


def test_role_partition_is_total_and_disjoint():
    # The deterministic/residue partition is the contract the LLM annotation layer keys off:
    # together with the UNKNOWN sentinel they cover every role exactly once, with no overlap.
    assert DETERMINISTIC_ROLES.isdisjoint(RESIDUE_ROLES)
    assert DETERMINISTIC_ROLES | RESIDUE_ROLES | {StructuralRole.UNKNOWN} == set(StructuralRole)
    # the five roles the matcher writes are exactly the deterministic side.
    assert StructuralRole.MOS_TAIL_CURRENT_SOURCE in DETERMINISTIC_ROLES
    assert StructuralRole.UNKNOWN not in RESIDUE_ROLES


PAIR_UNBIASED_TAIL = """\
** nmos pair whose tail is fed by a device sourced off an INTERNAL node, not a rail → no tail bias
XM1 outm vinp tail vss sg13_lv_nmos
XM2 vout vinn tail vss sg13_lv_nmos
XM3 outm outm vdd vdd sg13_lv_pmos
XM4 vout outm vdd vdd sg13_lv_pmos
XM5 tail ibias smid vss sg13_lv_nmos
XM6 smid ibias vss vss sg13_lv_nmos
.end
"""


def _pair_only_lib(tmp_path) -> TemplateLibrary:
    """Just the NMOS differential-pair template — no mirror template to anchor to."""
    pair = _write_template(tmp_path, "diff_pair_nmos", DIFF_PAIR_NMOS)
    return TemplateLibrary(
        [
            SubcircuitTemplate(
                id="dp.nmos.simple", netlist_path=pair, mirror_class="differential_pair",
                polarity="nmos", family="differential_pair",
                ports={
                    "supply": "VSS", "in_p": "vinp", "in_n": "vinn",
                    "CM_tail": "CM_tail", "out_n": "drain_n", "out_p": "drain_p",
                },
            )
        ]
    )


def test_diff_pair_recovered_from_physical_tail_source(tmp_path):
    # Even with ONLY the diff-pair template loaded (no mirror to anchor to), the pair is recovered when
    # a real current source biases its tail: the 5T OTA's tail sits on XM5 (drain=tail, source on the
    # VSS rail), so the externally-biased-tail fallback in `_admit_anchored` admits the pair — this is
    # what lets real amps whose tail mirror is not a recognised template still report their input pair.
    groups = group_matches(find_subcircuits(_g(OTA_5T_NMOS_INPUT), _pair_only_lib(tmp_path)))
    assert any(g.family == "differential_pair" for g in groups)


def test_diff_pair_dropped_without_a_tail_current_source(tmp_path):
    # The fallback is not a free pass: two common-source devices sharing a tail that NO rail-sourced
    # device drives (XM5 feeds the tail but is itself sourced off the internal `smid`, not a rail) are
    # rejected — no tail current source means it is not a differential pair.
    assert find_subcircuits(_g(PAIR_UNBIASED_TAIL), _pair_only_lib(tmp_path)) == []


# ------------------------------------------------------------------------------------------------
# Dependent templates: the `tail_sources` anchor allow-list
# ------------------------------------------------------------------------------------------------
def test_tail_sources_admits_listed_mirror(tmp_path):
    # The tail lands on the SIMPLE mirror's output, and the allow-list permits it → pair admitted.
    lib = _two_mirror_diffpair_lib(tmp_path, ["cm.nmos.simple"])
    groups = group_matches(find_subcircuits(_g(OTA_5T_NMOS_INPUT), lib))
    assert any(g.family == "differential_pair" for g in groups)


def test_tail_sources_rejects_unlisted_mirror(tmp_path):
    # The tail still lands on the simple mirror's output, but the allow-list only permits the cascode
    # mirror (a known template, so no typo warning) → the pair is NOT admitted on the wrong source.
    lib = _two_mirror_diffpair_lib(tmp_path, ["cm.nmos.cascode"])
    groups = group_matches(find_subcircuits(_g(OTA_5T_NMOS_INPUT), lib))
    assert all(g.family != "differential_pair" for g in groups)


def test_tail_sources_empty_accepts_any_mirror(tmp_path):
    # An empty allow-list keeps the looser default: any detected mirror output qualifies as an anchor.
    lib = _two_mirror_diffpair_lib(tmp_path, [])
    groups = group_matches(find_subcircuits(_g(OTA_5T_NMOS_INPUT), lib))
    assert any(g.family == "differential_pair" for g in groups)


def test_unknown_tail_source_warns(tmp_path, caplog):
    import logging

    lib = _two_mirror_diffpair_lib(tmp_path, ["cm.nmos.does_not_exist"])
    with caplog.at_level(logging.WARNING, logger="spicexplorer_circuitgraph.match"):
        find_subcircuits(_g(OTA_5T_NMOS_INPUT), lib)
    assert any("tail_sources not in the library" in r.message for r in caplog.records)


# ------------------------------------------------------------------------------------------------
# Match knob: external port isolation (no external device may bridge two non-supply template nets)
# ------------------------------------------------------------------------------------------------
# A simple NMOS mirror whose two NON-supply ports (ref_in `iin`, out `iout`) are shorted by a stray
# external resistor — an external device bridging two template pins.
MIRROR_BRIDGED_PORTS = """\
** simple nmos mirror with an external resistor bridging its two ports
XM1 iin iin vss vss sg13_lv_nmos
XM2 iout iin vss vss sg13_lv_nmos
RB iin iout 1k
.end
"""

# Same mirror, but the two ports fan out to DISTINCT external nodes (the legitimate case): each
# external resistor touches exactly one template port.
MIRROR_DISTINCT_LOADS = """\
** simple nmos mirror whose ports drive distinct external nodes
XM1 iin iin vss vss sg13_lv_nmos
XM2 iout iin vss vss sg13_lv_nmos
RR iin refx 1k
RL iout outx 1k
.end
"""


def test_external_isolated_rejects_port_bridge(tmp_path):
    host = _g(MIRROR_BRIDGED_PORTS)
    lib = _simple_lib(tmp_path)
    # default (isolation off): ports are free to fan out, so the bridged mirror still matches
    assert len(find_subcircuits(host, lib)) == 1
    # isolation on: the external RB bridges ref_in and out → rejected
    assert find_subcircuits(host, lib, match_external_isolated=True) == []


def test_external_isolated_keeps_distinct_port_loads(tmp_path):
    # Positive control: ports may still fan out under the flag, as long as no single external device
    # touches two of them.
    host = _g(MIRROR_DISTINCT_LOADS)
    lib = _simple_lib(tmp_path)
    assert len(find_subcircuits(host, lib, match_external_isolated=True)) == 1


def test_external_isolated_exempts_supply_rail(tmp_path):
    # Many external devices hang off the supply rail; that must never count as a bridge. Here a stray
    # device ties iout to VSS — but VSS is a supply rail, so only `iout` is a template port touched.
    host = _g(
        """\
        XM1 iin iin vss vss sg13_lv_nmos
        XM2 iout iin vss vss sg13_lv_nmos
        RL iout vss 1k
        .end
        """
    )
    lib = _simple_lib(tmp_path)
    assert len(find_subcircuits(host, lib, match_external_isolated=True)) == 1


def test_external_isolated_breaks_active_loaded_pair(tmp_path):
    # Documents why the flag is OFF by default: in a 5T OTA the active-load device XM4 gates off one
    # diff-pair drain and lands on the other, bridging both output ports — so isolation rejects the
    # otherwise-valid pair, while the (un-bridged) mirrors survive.
    host = _g(OTA_5T_NMOS_INPUT)
    lib = _diffpair_lib(tmp_path)
    assert any(
        g.family == "differential_pair" for g in group_matches(find_subcircuits(host, lib))
    )
    strict = group_matches(find_subcircuits(host, lib, match_external_isolated=True))
    assert all(g.family != "differential_pair" for g in strict)
    assert any(g.family == "current_mirror" for g in strict)  # the mirrors are still found


# ------------------------------------------------------------------------------------------------
# Match knob: per-template bulk matching (SubcircuitTemplate.match_bulk / manifest `match_bulk: true`)
# ------------------------------------------------------------------------------------------------
# A transmission-gate pair in its two drawn bulk styles. Bulk-blind they are the SAME topology (the
# rail variant's VSS/VDD are bulk-only nets and vanish from the signature); with bulk edges kept they
# split apart — exactly the ambiguity per-template `match_bulk` exists to resolve.
TG_BODY_TIED = """\
** cmos transmission gate, bulks tied back to the channel ports
XM1 port_A vctl port_B port_B sg13_lv_nmos
XM2 port_B vctl_not port_A port_A sg13_lv_pmos
.end
"""

TG_RAIL_BULK = """\
** cmos transmission gate, bulks tied to the supply rails
XM1 port_A vctl port_B VSS sg13_lv_nmos
XM2 port_B vctl_not port_A VDD sg13_lv_pmos
.end
"""

_TG_PORTS = {"a": "port_A", "b": "port_B", "ctl_n": "vctl", "ctl_p": "vctl_not"}


def _tg_split_lib(tmp_path) -> TemplateLibrary:
    """The bulk-blind canonical TG template + the bulk-strict rail-tied variant."""
    blind = _write_template(tmp_path, "tg_body_tied", TG_BODY_TIED)
    rail = _write_template(tmp_path, "tg_rail_bulk", TG_RAIL_BULK)
    return TemplateLibrary(
        [
            SubcircuitTemplate(
                id="tg.pair.cmos", netlist_path=blind, mirror_class="pass_gate",
                polarity="complementary", family="transmission_gate", ports=dict(_TG_PORTS),
            ),
            SubcircuitTemplate(
                id="tg.pair.cmos_rail_bulk", netlist_path=rail, mirror_class="pass_gate",
                polarity="complementary", family="transmission_gate", ports=dict(_TG_PORTS),
                match_bulk=True,
            ),
        ]
    )


def test_match_bulk_template_splits_rail_host(tmp_path):
    # On a RAIL-BULK host both templates fire on the same device pair; the bulk-strict variant is
    # the more specific claim, so it wins the primary and the bulk-blind twin rides as alternate.
    lib = _tg_split_lib(tmp_path)
    matches = find_subcircuits(_g(TG_RAIL_BULK), lib)
    assert {m.template_id for m in matches} == {"tg.pair.cmos", "tg.pair.cmos_rail_bulk"}
    by_id = {m.template_id: m for m in matches}
    assert by_id["tg.pair.cmos"].match_bulk is False  # matched bulk-blind
    assert by_id["tg.pair.cmos_rail_bulk"].match_bulk is True  # matched with bulk edges kept
    (grp,) = group_matches(matches)
    assert grp.template_id == "tg.pair.cmos_rail_bulk"
    assert [a.template_id for a in grp.alternates] == ["tg.pair.cmos"]
    assert set(grp.ports) == {"a", "b", "ctl_n", "ctl_p"}


def test_match_bulk_template_rejects_body_tied_host(tmp_path):
    # On a BODY-TIED host only the bulk-blind canonical template fires: the rail variant's bulk
    # edges (NMOS→VSS-class, PMOS→VDD-class) have no image, so there is no ambiguity to resolve.
    lib = _tg_split_lib(tmp_path)
    (grp,) = group_matches(find_subcircuits(_g(TG_BODY_TIED), lib))
    assert grp.template_id == "tg.pair.cmos"
    assert grp.alternates == ()


def test_match_bulk_flag_is_one_way(tmp_path):
    # A global bulk-strict run stays strict for every template — the per-template flag can only ADD
    # the bulk constraint, never relax a requested one. Bulk-strict, the body-tied netlist no longer
    # matches the rail-bulk host at all (their bulk wirings genuinely differ).
    lib = _tg_split_lib(tmp_path)
    matches = find_subcircuits(_g(TG_RAIL_BULK), lib, match_bulk=True)
    assert {m.template_id for m in matches} == {"tg.pair.cmos_rail_bulk"}
    assert all(m.match_bulk for m in matches)


def test_match_bulk_templates_self_match(tmp_path):
    # (a) each variant still finds itself in its own netlist.
    lib = _tg_split_lib(tmp_path)
    for netlist, tid in ((TG_BODY_TIED, "tg.pair.cmos"), (TG_RAIL_BULK, "tg.pair.cmos_rail_bulk")):
        (grp,) = group_matches(find_subcircuits(_g(netlist), lib))
        assert grp.template_id == tid


# ------------------------------------------------------------------------------------------------
# Annotation
# ------------------------------------------------------------------------------------------------
def test_annotate_writes_overlay_and_roles(tmp_path):
    host = _g(CASCODE_NMOS)
    groups = annotate_subcircuits(host, _cascode_lib(tmp_path))
    assert host.subcircuit_matches == groups
    roles = {c.name: c.structural_role for c in host.get_components()}
    # base pair sits on the rail → current-mirror; the stacked cascode devices → cascode device.
    # The diode reference (XM2) is tagged distinctly from its output copy (XM1).
    assert roles["XM2"] == StructuralRole.MOS_CURRENT_MIRROR_REFERENCE  # diode on VSS — the reference
    assert roles["XM1"] == StructuralRole.MOS_CURRENT_MIRROR  # mirror output dev on VSS
    assert roles["XM3"] == StructuralRole.MOS_CASCODE_DEVICE  # source on internal net1
    assert roles["XM4"] == StructuralRole.MOS_CASCODE_DEVICE  # source on internal net2


def test_annotate_can_skip_roles(tmp_path):
    host = _g(SIMPLE_NMOS)
    annotate_subcircuits(host, _simple_lib(tmp_path), set_roles=False)
    assert all(c.structural_role is None for c in host.get_components())
    assert len(host.subcircuit_matches) == 1


# ------------------------------------------------------------------------------------------------
# Integration — the real shipped catalogue against the example OTAs
# ------------------------------------------------------------------------------------------------
def _example_netlist(rel: str):
    from spicexplorer_core import project_root

    p = project_root() / rel
    return p if p.exists() else None


@pytest.fixture()
def cm_library():
    try:
        return default_current_mirror_library()
    except FileNotFoundError:
        pytest.skip("current-mirror template catalogue not present (packaged install without examples)")


def test_real_library_has_expected_templates(cm_library):
    ids = {t.id for t in cm_library}
    assert {"cm.nmos.simple", "cm.nmos.cascode", "cm.nmos.wilson", "cm.pmos.simple"} <= ids
    # PMOS current sources now ship the full cascode family (twins of the NMOS sinks), not just
    # simple + wilson — so a gate-biased PMOS cascode load no longer goes undetected.
    assert {
        "cm.pmos.cascode",
        "cm.pmos.high_swing_cascode",
        "cm.pmos.improved_high_swing_cascode",
        "cm.pmos.low_voltage_cascode",
        "cm.pmos.selfbiased_high_swing_cascode",
        "cm.pmos.improved_wilson",
    } <= ids
    assert len(ids) == len(cm_library)  # ids unique


def test_real_folded_cascode_multi_output(cm_library):
    path = _example_netlist("examples/analog-db/circuits/amp_004_folded_cascode/abstract/netlist.spice")
    if path is None:
        pytest.skip("folded_cascode example netlist not present")
    g = CircuitGraph.from_netlist(NetlistView.from_file(path), name="folded_cascode")
    groups = annotate_subcircuits(g, cm_library)
    by = {(grp.polarity, grp.reference_device): grp for grp in groups}
    # PMOS bias mirror: diode XM11 feeds tail (XM0) and nbias (XM12)
    assert ("pmos", "XM11") in by
    assert set(by["pmos", "XM11"].output_devices) == {"XM0", "XM12"}
    # NMOS folding mirror: diode XM13 feeds foldp (XM3) and foldn (XM4)
    assert ("nmos", "XM13") in by
    assert set(by["nmos", "XM13"].output_devices) == {"XM3", "XM4"}


def test_real_5t_ota(cm_library):
    path = _example_netlist("examples/analog-db/circuits/amp_001_5t/abstract/netlist.spice")
    if path is None:
        pytest.skip("amp_001_5t example netlist not present")
    g = CircuitGraph.from_netlist(NetlistView.from_file(path), name="amp_001_5t")
    groups = {grp.polarity: grp for grp in annotate_subcircuits(g, cm_library)}
    assert groups["nmos"].reference_device == "XM6"  # tail mirror
    assert groups["pmos"].reference_device == "XM3"  # active load


@pytest.fixture()
def subckt_library():
    try:
        return default_subcircuit_library()
    except FileNotFoundError:
        pytest.skip("subcircuit template catalogue not present (packaged install without examples)")


def test_real_subcircuit_library_includes_diff_pairs(subckt_library):
    ids = {t.id for t in subckt_library}
    assert {"cm.nmos.simple", "dp.nmos.simple", "dp.pmos.simple"} <= ids


def test_real_5t_ota_detects_diff_pair(subckt_library):
    # The full catalogue (mirrors + miscellaneous) finds the input pair anchored to the tail mirror.
    path = _example_netlist("examples/analog-db/circuits/amp_001_5t/abstract/netlist.spice")
    if path is None:
        pytest.skip("amp_001_5t example netlist not present")
    g = CircuitGraph.from_netlist(NetlistView.from_file(path), name="amp_001_5t")
    groups = annotate_subcircuits(g, subckt_library)
    dp = next((grp for grp in groups if grp.family == "differential_pair"), None)
    assert dp is not None
    assert set(dp.devices) == {"XM1", "XM2"}
    assert dp.ports["CM_tail"] == "tail"  # the tail mirror's output net
    roles = {c.name: c.structural_role for c in g.get_components()}
    assert roles["XM1"] == StructuralRole.MOS_DIFFERENTIAL_PAIR
    assert roles["XM2"] == StructuralRole.MOS_DIFFERENTIAL_PAIR


def _template_netlist(stem: str):
    return _example_netlist(
        f"examples/analog-db/templates/current_mirror/nmos_current_sink/simulation/{stem}.spice"
    )


def _pmos_template_netlist(stem: str):
    return _example_netlist(
        f"examples/analog-db/templates/current_mirror/pmos_current_source/simulation/{stem}.spice"
    )


# (template stem, manifest class) for the PMOS cascode family authored as twins of the NMOS sinks.
_PMOS_CASCODE_TWINS = [
    ("cascode_current_mirror", "cascode"),
    ("high_swing_cascode_current_mirror", "high_swing_cascode"),
    ("improved_high_swing_cascode_current_mirror", "improved_high_swing_cascode"),
    ("low_voltage_cascode_current_mirror", "low_voltage_cascode"),
    ("selfbiased_high_swing_cascode_current_mirror", "selfbiased_high_swing_cascode"),
    ("improved_wilson_current_mirror", "improved_wilson"),
]


@pytest.mark.parametrize(("stem", "mirror_class"), _PMOS_CASCODE_TWINS)
def test_pmos_cascode_template_is_polarity_twin_of_nmos(subckt_library, stem, mirror_class):
    """Each PMOS cascode template is the exact polarity-mirror of its NMOS sink (same topology,
    pmos for nmos, VDD for VSS) and self-detects under its own class with PMOS polarity."""
    npath, ppath = _template_netlist(stem), _pmos_template_netlist(stem)
    if npath is None or ppath is None:
        pytest.skip("current-mirror template netlists not present")
    gn = CircuitGraph.from_netlist(NetlistView.from_file(npath), name="nmos")
    gp = CircuitGraph.from_netlist(NetlistView.from_file(ppath), name="pmos")
    # Ignoring polarity + supply class, the NMOS sink and PMOS source are the same circuit.
    assert graphs_equivalent(gn, gp, match_polarity=False, match_supply=False)

    groups = annotate_subcircuits(gp, subckt_library)
    primary = next((g for g in groups if g.mirror_class == mirror_class), None)
    assert primary is not None, [g.mirror_class for g in groups]
    assert primary.polarity == "pmos"


def test_real_telescopic_detects_pmos_cascode(subckt_library):
    """Integration: the gate-biased PMOS cascode load of the telescopic OTA — invisible before the
    PMOS cascode twins existed — is now detected as a low-voltage cascode current source."""
    path = _example_netlist("examples/analog-db/circuits/amp_018_telescopic_cascode/abstract/netlist.spice")
    if path is None:
        pytest.skip("amp_018_telescopic_cascode example netlist not present")
    g = CircuitGraph.from_netlist(NetlistView.from_file(path), name="telescopic")
    groups = annotate_subcircuits(g, subckt_library)
    pmos_cascodes = [
        grp
        for grp in groups
        if grp.polarity == "pmos" and grp.family == "current_mirror" and grp.mirror_class != "simple"
    ]
    assert len(pmos_cascodes) == 1
    assert pmos_cascodes[0].mirror_class == "low_voltage_cascode"
    assert "XM4C" in pmos_cascodes[0].output_devices


def test_cascode_and_improved_wilson_are_distinguishable(subckt_library):
    """Regression: the cascode and improved-Wilson template netlists must be structurally
    distinct, so the matcher never reports one where the other belongs.

    They were once byte-identical — the improved-Wilson schematic was missing its distinguishing
    output→input feedback edge, so the two collided on the *same* device set and a
    ``_CLASS_SPECIFICITY`` tie-break had to demote one to an alternate. The schematic now encodes the
    feedback, so each resolves to its own class with no cross-class alternate."""
    casc = _template_netlist("cascode_current_mirror")
    wils = _template_netlist("improved_wilson_current_mirror")
    if casc is None or wils is None:
        pytest.skip("current-mirror template netlists not present")

    # 1. The two are no longer the same circuit up to renaming — the heart of the bug.
    assert not netlists_equivalent(str(casc), str(wils))

    # 2. Each host resolves to its OWN class as the single 4-device primary, with the other class
    #    NOT folded in as an equal-device-set alternate (no collision left for the tie-break to mask).
    def _four_device_primary(host):
        groups = group_matches(find_subcircuits(host, subckt_library))
        full = [g for g in groups if len(g.devices) == 4]
        assert len(full) == 1, [(g.template_id, g.devices) for g in groups]
        return full[0]

    gc = _four_device_primary(str(casc))
    assert gc.mirror_class == "cascode"
    assert "improved_wilson" not in {a.mirror_class for a in gc.alternates}

    gw = _four_device_primary(str(wils))
    assert gw.mirror_class == "improved_wilson"
    assert "cascode" not in {a.mirror_class for a in gw.alternates}


# ---------------------------------------------------------------------------
# Real shipped catalogue: pseudo-resistor + transmission-gate families
# ---------------------------------------------------------------------------
def test_real_subcircuit_library_includes_pr_and_tg(subckt_library):
    ids = {t.id for t in subckt_library}
    assert {
        "pr.series.indep_well_indep_gen",
        "pr.series.shared_well_gen",
        "pr.series.shared_well",
        "pr.series.shared_gen",
        "tg.pair.cmos",
    } <= ids


# (netlist stem, template id) for the four Guglielmi Fig-3 series pseudo-resistor cells. Bulk-blind
# (match_bulk=False) they stay pairwise distinct — they differ in which of D/G/S sits on the outer
# ports vs the shared middle node — so each host must resolve to EXACTLY its own template, with no
# cross-variant alternate.
_PR_SERIES_CELLS = [
    ("pseudo-resistor-a-independant-well-generator", "pr.series.indep_well_indep_gen"),
    ("pseudo-resistor-b-well-and-generator", "pr.series.shared_well_gen"),
    ("pseudo-resistor-c-well-only", "pr.series.shared_well"),
    ("pseudo-resistor-d-generator-only", "pr.series.shared_gen"),
]


@pytest.mark.parametrize(("stem", "template_id"), _PR_SERIES_CELLS)
def test_real_pseudo_resistor_cell_self_matches(subckt_library, stem, template_id):
    path = _example_netlist(
        f"examples/analog-db/templates/pseudo_resistor/simulation/{stem}.spice"
    )
    if path is None:
        pytest.skip("pseudo-resistor template netlists not present")
    g = CircuitGraph.from_netlist(NetlistView.from_file(str(path)), name=stem)
    groups = annotate_subcircuits(g, subckt_library)
    assert [grp.template_id for grp in groups] == [template_id]
    assert groups[0].family == "pseudo_resistor"
    assert not groups[0].alternates  # no cross-variant aliasing bulk-blind
    assert set(groups[0].ports) == {"a", "b"}
    roles = {c.name: c.structural_role for c in g.get_components()}
    assert roles == {
        "XM1": StructuralRole.MOS_PSEUDO_RESISTOR,
        "XM2": StructuralRole.MOS_PSEUDO_RESISTOR,
    }


@pytest.mark.parametrize(
    "stem",
    [
        # The canonical registered netlist (bulks tied back to the channel ports) …
        "transmission_gate_pair_body_tied",
        # … and the rail-bulk drawing: bulk-blind the SAME topology (its VSS/VDD are bulk-only
        # nets), so the one canonical template must recognise both bulk styles.
        "transmission_gate_pair",
    ],
)
def test_real_transmission_gate_matches_both_bulk_styles(subckt_library, stem):
    path = _example_netlist(
        f"examples/analog-db/templates/transmission_gate/simulation/{stem}.spice"
    )
    if path is None:
        pytest.skip("transmission-gate template netlists not present")
    g = CircuitGraph.from_netlist(NetlistView.from_file(str(path)), name=stem)
    groups = annotate_subcircuits(g, subckt_library)
    rail_variant_registered = "tg.pair.cmos_rail_bulk" in {t.id for t in subckt_library}
    if stem == "transmission_gate_pair" and rail_variant_registered:
        # Bulk-split catalogue: the bulk-strict rail variant wins the primary on the rail-bulk
        # drawing; the bulk-blind canonical template is kept as its alternate (still recognised).
        assert [grp.template_id for grp in groups] == ["tg.pair.cmos_rail_bulk"]
        assert [a.template_id for a in groups[0].alternates] == ["tg.pair.cmos"]
    else:
        # Body-tied drawing (any catalogue) / rail drawing under a pre-split catalogue: the
        # canonical bulk-blind template is the sole, unambiguous primary.
        assert [grp.template_id for grp in groups] == ["tg.pair.cmos"]
        assert groups[0].alternates == ()
    assert groups[0].family == "transmission_gate"
    assert groups[0].polarity == "complementary"
    assert set(groups[0].ports) == {"a", "b", "ctl_n", "ctl_p"}
    roles = {c.name: c.structural_role for c in g.get_components()}
    assert roles == {
        "XM1": StructuralRole.MOS_ANALOG_SWITCH,
        "XM2": StructuralRole.MOS_ANALOG_SWITCH,
    }


# ---------------------------------------------------------------------------
# DR-4 — the shipped catalogue's design-rule registrations are valid
# ---------------------------------------------------------------------------
# Backticked tokens on a rule doc's "Roles emitted" banner line — each must name a real
# StructuralRole, either by value (`current_mirror`) or by member (`StructuralRole.MOS_...`).
_BACKTICKED = re.compile(r"`([^`]+)`")


def _templates_root() -> Path | None:
    from spicexplorer_core import project_root

    root = project_root() / "examples/analog-db/templates"
    return root if root.is_dir() else None


def test_every_manifest_rules_path_resolves_and_claimed_roles_are_real():
    """Every family manifest's ``rules:`` paths resolve to files, and every role a rule doc
    claims to emit (its "Roles emitted" banner lines) is a real :class:`StructuralRole` member."""
    root = _templates_root()
    if root is None:
        pytest.skip("template catalogue not present (packaged install without examples)")
    manifests = sorted(root.glob("*/manifest.yaml"))
    assert manifests, "no family manifests found under templates/"
    valid_values = {r.value for r in StructuralRole}
    for manifest in manifests:
        data = yaml.safe_load(manifest.read_text()) or {}
        rules = data.get("rules") or []
        assert rules, f"{manifest}: family registers no design-rule docs (rules: block)"
        for entry in rules:
            doc = (manifest.parent / entry["path"]).resolve()
            assert doc.is_file(), f"{manifest}: rules path {entry['path']!r} does not resolve"
            for line in doc.read_text().splitlines():
                if "Roles emitted" not in line:
                    continue
                for token in _BACKTICKED.findall(line.split("Roles emitted", 1)[1]):
                    ok = token in valid_values or (
                        token.startswith("StructuralRole.")
                        and token.removeprefix("StructuralRole.") in StructuralRole.__members__
                    )
                    assert ok, f"{doc}: claimed emitted role {token!r} is not a StructuralRole"


def test_real_catalogue_templates_carry_their_family_rules(subckt_library):
    # The DR-3 surface: every shipped template points at its family's registered rule doc(s), so the
    # annotation exporter can emit `rules_ref` per detected block.
    missing = [t.id for t in subckt_library if not t.rules_paths]
    assert not missing, f"templates without family rules registration: {missing}"
    for t in subckt_library:
        for p in t.rules_paths:
            assert p.is_file()


def test_family_roles_are_deterministic_ground_truth():
    # The new family roles join the deterministic partition (the LLM layer must not override them).
    assert StructuralRole.MOS_PSEUDO_RESISTOR in DETERMINISTIC_ROLES
    assert StructuralRole.MOS_ANALOG_SWITCH in DETERMINISTIC_ROLES
    assert DETERMINISTIC_ROLES.isdisjoint(RESIDUE_ROLES)


def test_detection_over_an_incomplete_host_says_the_host_was_incomplete(caplog):
    """`find_subcircuits` builds the host graph internally and throws it away.

    With the default `on_unknown="skip"` a device it cannot model is dropped, so detection runs
    over a partial netlist — a template can only be found in, or ruled out of, the part that could
    be typed. The census has to reach the caller; nothing else can.
    """
    host = (
        "* mirror plus an unmodelable device\n"
        "M1 ref ref vss vss sg13_lv_nmos\n"
        "M2 out ref vss vss sg13_lv_nmos\n"
        "Q1 out ref vss npn\n"
        ".end\n"
    )
    with caplog.at_level(logging.WARNING, logger="spicexplorer_circuitgraph.match"):
        find_subcircuits(host)
    assert "invisible to subcircuit detection" in caplog.text and "Q1" in caplog.text


def test_a_fully_typed_host_is_not_flagged(caplog):
    host = (
        "* mirror\n"
        "M1 ref ref vss vss sg13_lv_nmos\n"
        "M2 out ref vss vss sg13_lv_nmos\n"
        ".end\n"
    )
    with caplog.at_level(logging.WARNING, logger="spicexplorer_circuitgraph.match"):
        find_subcircuits(host)
    assert "invisible to subcircuit detection" not in caplog.text
