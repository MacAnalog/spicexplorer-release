"""The measurements a schematic agent reads after a sheet is drawn (``report.py``, ``--report``).

The 40-block fixture of issue #243 (``fixtures/blockdiag/``) at its 360-unit hand floorplan is
measured under both routers; the numbers are the ones ``test_channel_routing.py`` counts from the
plan itself. The CLI writes the same data as JSON, and the ``.sch`` files are the same with or
without ``--report``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import (
    SymLibrary,
    analyze,
    build_sch,
    from_file,
    plan_connections,
    sheet_report,
)
from spicexplorer_netlist2xschem.cli import main
from spicexplorer_netlist2xschem.geometry import Transform
from spicexplorer_netlist2xschem.ingest import Device, DeviceKind, MosPolarity, N2XCircuit
from spicexplorer_netlist2xschem.mapping import align_pins, register_subckt_symbol, symref_for
from spicexplorer_netlist2xschem.wiring import PlacedDevice

FIXTURES = Path(__file__).parent / "fixtures"
BLOCKDIAG = FIXTURES / "blockdiag"
PDK = "report-fixture"  # a token of its own: the subckt symbol table is module-global
CELLS = [f"blk_{c}" for c in "abcdefghi"]
for _cell in CELLS:
    register_subckt_symbol(PDK, _cell, f"blockdiag/{_cell}.sym")

#: Lanes reserved per channel on the fixture at 360, channels asked for: ``v:0`` is left of the
#: first block column, ``h:0`` above the first block row.
LANES_AT_360 = {
    "h:0": 2,
    "h:1": 5,
    "h:2": 6,
    "h:3": 4,
    "h:4": 8,
    "h:5": 1,
    "v:0": 5,
    "v:1": 6,
    "v:2": 5,
    "v:3": 6,
    "v:4": 5,
    "v:5": 5,
    "v:6": 5,
    "v:7": 5,
    "v:8": 4,
}


@dataclass
class FixedPlacer:
    at: dict[str, Transform]

    def place(self, circuit, lib=None, *, hints=None) -> dict[str, Transform]:  # noqa: ARG002
        return dict(self.at)


@pytest.fixture
def lib() -> SymLibrary:
    return SymLibrary([FIXTURES / "sym", FIXTURES])


def _top() -> N2XCircuit:
    return from_file(BLOCKDIAG / "blockdiag_top.spice", into="xtop", name="blockdiag_top")


def _at_360(circuit: N2XCircuit) -> FixedPlacer:
    refs = sorted(d.ref for d in circuit.devices)
    return FixedPlacer({r: Transform((i % 8) * 360, (i // 8) * 360) for i, r in enumerate(refs)})


def test_the_default_report_says_what_the_per_route_planner_left_by_name(lib):
    """Issue #243's numbers, read from the report: 28 nets by name, ``rst`` in 18 pieces, each
    supply in 33 (the sheet rail reaches 8 taps; 32 taps cross another block's supply pin and are
    refused)."""
    circuit = _top()
    report = sheet_report(build_sch(circuit, pdk=PDK, lib=lib, placer=_at_360(circuit)))
    assert report["router"] == "per-route"
    assert report["nets_by_name_count"] == len(report["nets_by_name"]) == 28
    assert set(report["pieces"]) == set(report["nets_by_name"])
    assert (report["pieces"]["rst"], report["pieces"]["clk"]) == (18, 14)
    assert (report["pieces"]["vdd"], report["pieces"]["vss"]) == (33, 33)
    signal = [n for n in report["pieces"] if n not in ("vdd", "vss")]
    assert len(signal) == 26
    rail = {"rails": 1, "spines": 0, "taps": 8, "refused": 32}
    assert report["supply"] == {"vdd": rail, "vss": rail}
    assert (report["lanes"], report["unrouted"], report["parked_ports"]) == ({}, [], [])


def test_the_channel_report_counts_rails_taps_and_lanes(lib):
    """Asked for channels: nothing by name, one rail per block row (5), one spine and 40 taps per
    supply, none of the 92 supply wires refused, and the lanes reserved in each channel."""
    circuit = _top()
    doc = build_sch(circuit, pdk=PDK, lib=lib, placer=_at_360(circuit), router="channel")
    report = sheet_report(doc)
    assert report["router"] == "channel"
    assert (report["nets_by_name"], report["pieces"], report["unrouted"]) == ([], {}, [])
    rails = {"rails": 5, "spines": 1, "taps": 40, "refused": 0}
    assert report["supply"] == {"vdd": rails, "vss": rails}
    assert report["lanes"] == LANES_AT_360
    assert (report["devices"], report["labels"]) == (40, doc.label_count)
    json.dumps(report)  # JSON-ready as returned


def _pair(lib: SymLibrary, gap: int) -> tuple[N2XCircuit, list[PlacedDevice]]:
    devs = [
        Device(
            ref=f"XB{i}",
            kind=DeviceKind.SUBCKT,
            model="blk_a",
            polarity=MosPolarity.UNKNOWN,
            pins=("clk", "rst", "vin", "q", "vdd", "vss"),
            nets={
                "clk": "clk",
                "rst": "rst",
                "vin": f"n{i}",
                "q": f"n{i + 1}",
                "vdd": "vdd",
                "vss": "vss",
            },
            params={},
        )
        for i in range(2)
    ]
    circuit = N2XCircuit(
        "pair",
        tuple(devs),
        tuple(sorted({n for d in devs for n in d.nets.values()})),
        {"vdd": "VDD", "vss": "VSS"},
    )
    placed = []
    for i, d in enumerate(devs):
        sym = lib.load(symref_for(d, pdk=PDK) or "")
        assert sym is not None
        placed.append(
            PlacedDevice(
                d.ref,
                Transform(i * gap, 0),
                d.nets,
                align_pins(d, sym),
                is_block=True,
                body=sym.bbox,
            )
        )
    return circuit, placed


def test_a_lane_that_does_not_fit_is_reported_unrouted(lib):
    """Two blocks 280 apart, not moved apart first: the gap holds 2 of its 3 lanes and ``rst``,
    numbered last, is left to its name. The report names it unrouted and in 2 pieces."""
    circuit, placed = _pair(lib, 280)
    plan = plan_connections(
        placed, supply=circuit.supply, port_role=analyze(circuit).port_role, router="channel"
    )
    assert (plan.router, plan.unrouted, plan.by_name, plan.pieces) == (
        "channel",
        ["rst"],
        ["rst"],
        {"rst": 2},
    )
    assert plan.lanes[("v", 1)] == 3


def test_the_labels_mode_reports_every_terminal_as_its_own_piece(lib):
    circuit = _top()
    doc = build_sch(circuit, pdk=PDK, lib=lib, placer=_at_360(circuit), wiring="labels")
    report = sheet_report(doc)
    assert report["router"] == "labels" and report["nets_by_name_count"] == 45
    assert (report["pieces"]["clk"], report["pieces"]["rst"]) == (21, 19)  # clk/rst fan-out
    assert (report["supply"], report["lanes"]) == ({}, {})


# ---------------------------------------------------------------------------------- the CLI


def _flat(tmp_path: Path, name: str, *extra: str) -> list[str]:
    return [str(FIXTURES / "mixed_devices.spice"), "-o", str(tmp_path / name), *extra]


def test_the_cli_report_is_written_beside_an_unchanged_sheet(tmp_path, capsys):
    assert main(_flat(tmp_path, "plain.sch")) == 0
    report_path = tmp_path / "mixed.json"
    assert main(_flat(tmp_path, "reported.sch", "--report", str(report_path))) == 0
    assert (tmp_path / "plain.sch").read_bytes() == (tmp_path / "reported.sch").read_bytes()
    report = json.loads(report_path.read_text())
    assert report["router_asked"] == "per-route"
    (sheet,) = report["sheets"].values()
    assert sheet["router"] == "per-route"
    assert sheet["nets_by_name_count"] == len(sheet["nets_by_name"])
    assert "wrote " in capsys.readouterr().out


def test_the_cli_report_goes_to_stdout_with_a_dash(tmp_path, capsys):
    """``--report -``: standard output is the JSON alone; the usual messages go to stderr."""
    assert main(_flat(tmp_path, "x.sch", "--report", "-", "--router", "channel")) == 0
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert report["router_asked"] == "channel"
    assert report["sheets"]["mixed_devices"]["router"] == "per-route"  # a cell sheet, as asked
    assert "wrote " in captured.err


def test_the_cli_refuses_a_report_where_it_draws_no_flat_sheet(tmp_path, capsys):
    assert main(_flat(tmp_path, "x.sch", "--report", "-", "--hierarchical")) == 2
    assert "--report applies to the flat sheet or the --collapse sheets" in capsys.readouterr().err


def _collapse_args(tmp_path: Path, name: str, *extra: str) -> list[str]:
    cells = [f"--cell-symbol={c}={BLOCKDIAG / f'{c}.sym'}" for c in CELLS]
    return [
        str(BLOCKDIAG / "blockdiag_top.spice"),
        "--into",
        "xtop",
        "--name",
        "blockdiag_top",
        "--pdk",
        "generic",
        "-o",
        str(tmp_path / name / "top.sch"),
        *cells,
        "--collapse",
        "front=blk_a,blk_b",
        "--collapse",
        "mid=blk_c,blk_g,blk_d,blk_h",
        *extra,
    ]


def test_the_cli_reports_a_collapsed_hierarchy_and_its_check(tmp_path):
    report_path = tmp_path / "top.json"
    rc = main(_collapse_args(tmp_path, "a", "--router", "channel", "--report", str(report_path)))
    assert rc == 0
    report = json.loads(report_path.read_text())
    assert report["top_sheet"] == {"instances_before": 40, "instances_after": 6}
    assert {g: (len(v["slices"]), len(v["ports"])) for g, v in report["groups"].items()} == {
        "front": (16, 14),
        "mid": (20, 18),
    }
    assert report["groups"]["front"]["instance"] == "xfront"
    assert set(report["sheets"]) == {"blockdiag_top", "front", "mid"}
    assert {s["router"] for s in report["sheets"].values()} == {"channel"}
    assert all(s["nets_by_name"] == [] for s in report["sheets"].values())
    check = report["check"]
    assert (check["identical"], check["terminals"], check["nets"]) == (True, 233, 46)
    assert check["split"] == check["missing"] == check["extra"] == []


def test_the_cli_report_leaves_every_collapsed_file_unchanged(tmp_path):
    assert main(_collapse_args(tmp_path, "plain")) == 0
    assert main(_collapse_args(tmp_path, "reported", "--report", str(tmp_path / "r.json"))) == 0

    def files(root: Path) -> dict[str, bytes]:
        return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}

    assert files(tmp_path / "plain") == files(tmp_path / "reported")
