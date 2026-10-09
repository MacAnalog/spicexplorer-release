"""xvport connectivity mode after #267: ``wires`` by default, and ``labels`` says what it drops.

The port must translate the sheet's placement AND its wiring. ``--mode labels`` did both
*electrically* — every terminal gets a labelled stub, the cellview netlists correctly — and
no gate in this tool can see that it drew no wire: ``--strict-netcheck``, the read-back and a
post-port re-simulation all pass on such a cellview. Only a person opening it can. So the
default is ``wires``, ``labels`` says so once per run, and the mode a call is given reaches
every cellview that call builds.

Everything here is OFFLINE: the ``.il`` text is the artifact under test. What Virtuoso makes
of it — a drawn wire, a stub from the *master's* pin centre, which label wins when two land
on one point — is FIXTURE-ONLY in this repo; no daemon runs in these tests.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from spicexplorer_netlist2xschem.virtuoso_export.cli import (
    _LABELS_NO_WIRES,
    _add_common,
    main,
)

FIXTURES = Path(__file__).parent / "fixtures" / "xvport"
SYM_DEVICES = Path(__file__).parent / "fixtures" / "sym" / "devices"

#: a real label stub call, not the `xvLabelTerm` procedure definition in the helper block
LABEL_CALL = 'xvLabelTerm(cv "'
PATCH_CALL = 'xvPatchTerm(cv "'


def _body(il: str) -> str:
    """The built cellview only — the helper procedures above it also call schCreateWire."""
    return il.split("let((cv)", 1)[1]


def _hierarchy(tmp_path: Path) -> Path:
    """The two-level corpus fixture: a top sheet over one ported child (.sch + .sym)."""
    for name in ("chopper-diff.sch", "transmission_gate_pair.sch", "transmission_gate_pair.sym"):
        shutil.copy(FIXTURES / name, tmp_path / name)
    return tmp_path / "chopper-diff.sch"


def test_mode_parses_as_wires_by_default():
    """The flag itself: no --mode on the command line means wires (#267)."""
    parser = argparse.ArgumentParser()
    _add_common(parser)
    argv = ["x.sch", "--lib", "LIBX"]
    assert parser.parse_args(argv).mode == "wires"
    assert parser.parse_args([*argv, "--mode", "labels"]).mode == "labels"


def test_default_port_emits_the_wires_path(tmp_path):
    """…and the emitted `.il` takes the wires path: drawn wires + patched pins, no stubs."""
    src = tmp_path / "mos_fingered.sch"
    shutil.copy(FIXTURES / "mos_fingered.sch", src)
    out = tmp_path / "out.il"
    assert main(["sch2cv", str(src), "--lib", "LIBX", "-o", str(out)]) == 0
    body = _body(out.read_text(encoding="utf-8"))
    assert "schCreateWire(cv " in body
    assert PATCH_CALL in body
    assert LABEL_CALL not in body

    lab = tmp_path / "lab.il"
    assert main(["sch2cv", str(src), "--lib", "LIBX", "--mode", "labels", "-o", str(lab)]) == 0
    lab_body = _body(lab.read_text(encoding="utf-8"))
    assert LABEL_CALL in lab_body
    assert "schCreateWire(cv " not in lab_body  # the mode that ports no wiring


def test_mode_reaches_every_dependency_build(tmp_path):
    """--mode propagates through --with-symbols: the CHILD is wired the way the call says.

    A hierarchy ported in one call must be ported one way. The journal case is a top cell
    built in the requested mode over children built in the default one — invisible to every
    check, because each child netlists correctly either way (#267).
    """
    src = _hierarchy(tmp_path)
    out = tmp_path / "out.il"
    assert main(["sch2cv", str(src), "--lib", "LIBX", "--with-symbols", "-o", str(out)]) == 0
    child = (tmp_path / "out.sch.transmission_gate_pair.il").read_text(encoding="utf-8")
    top = (tmp_path / "out.sch.chopper_diff.il").read_text(encoding="utf-8")
    for il in (child, top):
        assert PATCH_CALL in il and LABEL_CALL not in il

    out2 = tmp_path / "lab.il"
    assert (
        main(
            [
                "sch2cv",
                str(src),
                "--lib",
                "LIBX",
                "--with-symbols",
                "--mode",
                "labels",
                "-o",
                str(out2),
            ]
        )
        == 0
    )
    child2 = (tmp_path / "lab.sch.transmission_gate_pair.il").read_text(encoding="utf-8")
    top2 = (tmp_path / "lab.sch.chopper_diff.il").read_text(encoding="utf-8")
    for il in (child2, top2):
        assert LABEL_CALL in il and PATCH_CALL not in il


def test_labels_mode_warns_once_per_run_that_it_ports_no_wires(tmp_path, capsys):
    """One line per RUN, not per cellview — three builds, one warning; none by default."""
    src = _hierarchy(tmp_path)
    assert (
        main(
            [
                "sch2cv",
                str(src),
                "--lib",
                "LIBX",
                "--with-symbols",
                "--mode",
                "labels",
                "-o",
                str(tmp_path / "lab.il"),
            ]
        )
        == 0
    )
    err = capsys.readouterr().err
    assert err.count(_LABELS_NO_WIRES) == 1
    assert "--mode labels ports NO wires" in err

    assert (
        main(["sch2cv", str(src), "--lib", "LIBX", "--with-symbols", "-o", str(tmp_path / "w.il")])
        == 0
    )
    assert _LABELS_NO_WIRES not in capsys.readouterr().err


# --- three terminals on one straight run (the #267 refusal) ----------------------


def _one_run_load(tmp_path: Path) -> Path:
    """A device whose drain, source and bulk sit on ONE straight run, tied to one net.

    The shape a unit gate load / decoupling device has, drawn against a rail. The three
    pins sit in one column ON the instance's own axis — the master geometry a kit MOS has
    when its origin is not between them — so neither perpendicular is provably outward and
    #254's fan-out has nowhere to aim the two inner stubs.
    """
    (tmp_path / "devices").mkdir(exist_ok=True)
    (tmp_path / "devices" / "mos4_stack.sym").write_text(
        "v {xschem version=3.4.5 file_version=1.2\n}\nG {}\nK {type=nmos\n"
        'template="name=M1 model=nmos_a"}\nV {}\nS {}\nE {}\n'
        "B 5 -2.5 17.5 2.5 22.5 {name=d dir=inout}\n"
        "B 5 -2.5 47.5 2.5 52.5 {name=b dir=inout}\n"
        "B 5 -2.5 77.5 2.5 82.5 {name=s dir=inout}\n"
        "B 5 -32.5 47.5 -27.5 52.5 {name=g dir=in}\n",
        encoding="utf-8",
    )
    shutil.copy(SYM_DEVICES / "lab_wire.sym", tmp_path / "devices" / "lab_wire.sym")
    src = tmp_path / "unit_load.sch"
    src.write_text(
        "v {xschem version=3.4.5 file_version=1.2\n}\nG {}\nK {}\nV {}\nS {}\nE {}\n"
        "C {devices/mos4_stack.sym} 0 0 0 0 {name=M1 model=nmos_a}\n"
        "N 0 20 0 80 {}\n"
        "N 0 80 0 110 {}\n"
        "C {devices/lab_wire.sym} 0 110 0 0 {name=l1 lab=vss_a}\n"
        "N -60 50 -30 50 {}\n"
        "C {devices/lab_wire.sym} -60 50 0 0 {name=l2 lab=gate}\n",
        encoding="utf-8",
    )
    return src


def test_labels_mode_refuses_three_terminals_on_one_run(tmp_path, capsys):
    """REFUSED, naming the instance and its terminals — not a plausible wrong cellview.

    Two of the three stubs stay collinear whatever the fan-out does, so on the master their
    labels can land on one point and one wins: the terminals reach the database on an
    auto-named net that netcheck, the read-back and a re-simulation all call correct.
    """
    src = _one_run_load(tmp_path)
    out = tmp_path / "out.il"
    rc = main(
        ["sch2cv", str(src), "--lib", "LIBX", "--with-symbols", "--mode", "labels", "-o", str(out)]
    )
    assert rc == 2
    err = capsys.readouterr().err
    refusal = next(line for line in err.splitlines() if "one line" in line)
    assert "instance M1" in refusal
    for term in ("b", "d", "s"):
        assert f"{term}," in refusal or f"{term} draw" in refusal
    assert "--allow-collinear-labels" in refusal


def test_allow_collinear_labels_downgrades_the_refusal(tmp_path, capsys):
    """The escape hatch: a warning and a built `.il`, for a caller who checked net by net."""
    src = _one_run_load(tmp_path)
    out = tmp_path / "out.il"
    rc = main(
        [
            "sch2cv",
            str(src),
            "--lib",
            "LIBX",
            "--with-symbols",
            "--mode",
            "labels",
            "--allow-collinear-labels",
            "-o",
            str(out),
        ]
    )
    assert rc == 0
    err = capsys.readouterr().err
    assert [
        ln for ln in err.splitlines() if "one line" in ln and "[--allow-collinear-labels]" in ln
    ]
    built = (tmp_path / "out.sch.unit_load.il").read_text(encoding="utf-8")
    assert LABEL_CALL in built


def test_the_default_mode_ports_that_same_sheet(tmp_path):
    """…and the same sheet ports without the refusal in the default mode: it draws wires."""
    src = _one_run_load(tmp_path)
    out = tmp_path / "out.il"
    assert main(["sch2cv", str(src), "--lib", "LIBX", "--with-symbols", "-o", str(out)]) == 0
    body = _body((tmp_path / "out.sch.unit_load.il").read_text(encoding="utf-8"))
    assert "schCreateWire(cv " in body and PATCH_CALL in body
