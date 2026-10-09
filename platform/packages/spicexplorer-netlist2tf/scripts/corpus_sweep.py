"""netlist2tf over every analog-db open-loop bench: one status row per deck (WP-50, ROAD-F4).

For each ``raw/<circuit>/<pdk>/ac_open_loop.spice`` of the analog-db corpus it ingests the deck,
builds the small-signal model at the default level (``SOME_PARASITIC``), checks that the MNA
system is solvable, and then runs ``transfer_function`` in a child process under a time limit.
No PDK and no simulator are needed. Each row gets one status:

* ``unsupported`` — ingestion failed, a device has no small-signal model, or the output net is
  missing. The transfer function is not attempted: it would omit that device.
* ``singular`` — :func:`check_solvable` refused the system; ``detail`` names the nets.
* ``timeout`` — the symbolic ``transfer_function`` did not finish within ``--timeout`` seconds.
* ``ok`` — it finished; ``detail`` gives the pole and zero counts.
* ``error`` — it raised anything else; ``detail`` gives the exception.

The ``ideal`` column is the same solvability check at ``Fidelity.IDEAL`` (no ``ro``): ``ok``, or
the nets the refusal names.

Ports: the output is ``vout`` to ground, or ``voutp``/``voutn`` on a fully differential bench;
the input is the bench's own stimulus (``detect_ac_input``): its one AC source, or its DM pair
(``Vinp vinp vcm ac 0.5`` / ``Vinn vinn vcm ac -0.5``).

``--subs`` adds a numeric column. The same ``transfer_function`` runs again with every symbol
bound before the determinant: a symbol that is a numeric ``.param`` of the deck takes that value,
and every other one the generic operating point of ``simplify._coarse_op`` (``gm_*`` 1 mS,
``ro_*`` 200 kΩ, ``gmb_*`` 0.2 mS, ``c*`` 10 fF, ``r*`` 10 kΩ, anything else 1). Its poles and
zeros are those of that generic bias, not of the design: the column says where the solve
finishes, and the symbolic column stays as it was.

Writes ``results/corpus_sweep.json`` and ``results/corpus_sweep.md`` beside this directory; the
Markdown table is generated from the JSON. Regenerate with::

    nice uv run python packages/spicexplorer-netlist2tf/scripts/corpus_sweep.py --jobs 2 --subs
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import subprocess
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from spicexplorer_netlist2tf import (
    Fidelity,
    build_system,
    detect_ac_input,
    from_file,
    small_signal_model,
    transfer_function,
)
from spicexplorer_netlist2tf.mna import SingularSystemError, _as_pair, _augment, check_solvable
from spicexplorer_netlist2tf.simplify import _coarse_op

_HERE = Path(__file__).resolve().parent
_RESULTS = _HERE.parent / "results"
_STATUSES = ("ok", "singular", "timeout", "unsupported", "error")


def _ports(ssir, system) -> tuple[tuple[str, str], tuple[str, str]]:  # noqa: ANN001
    """The bench's (output, input) port pair, by the rule in the module docstring."""
    nets = {n.lower() for n in system._parent}
    out = ("vout", "0") if "vout" in nets else ("voutp", "voutn")
    return out, detect_ac_input(ssir)  # a ValueError makes the row unsupported


def _solvable(system, inp: tuple[str, str]) -> str:  # noqa: ANN001
    """``ok``, or the nets a singular refusal names."""
    try:
        check_solvable(system, inp)
    except SingularSystemError as exc:
        return ", ".join(exc.nets)
    return "ok"


def _prepare(db: Path, deck: Path) -> dict:
    """The row's static part, from ingest + model + MNA build (milliseconds per deck)."""
    circuit, pdk = deck.parent.parent.name, deck.parent.name
    row: dict = {
        "circuit": circuit,
        "pdk": pdk,
        "deck": str(deck.relative_to(db)),
        "status": "",
        "nodes": None,
        "devices": None,
        "output": "",
        "input": "",
        "ideal": "",
        "seconds": None,
        "detail": "",
        "subs_status": "",
        "subs_seconds": None,
        "subs_detail": "",
    }
    try:
        ir = from_file(deck)
    except Exception as exc:  # noqa: BLE001 — any ingest failure is this row's finding
        row.update(status="unsupported", detail=f"ingest: {type(exc).__name__}: {exc}")
        return row
    ssir = small_signal_model(ir)
    system = build_system(ssir)
    row["devices"] = len(ir.devices)
    try:
        out, inp = _ports(ssir, system)
    except ValueError as exc:
        row.update(status="unsupported", detail=f"input: {exc}")
        return row
    row.update(output=",".join(out), input=",".join(inp))
    try:
        _as_pair(out, system, "output")
        row["nodes"] = _augment(system, _as_pair(inp, system, "input"), "dm")[0].shape[0]
    except (KeyError, ValueError) as exc:
        row.update(status="unsupported", detail=f"ports: {exc}")
        return row
    ideal = small_signal_model(ir, level=Fidelity.IDEAL)
    row["ideal"] = _solvable(build_system(ideal), inp)
    if ssir.unmodelled:
        row.update(status="unsupported", detail="no model for " + ", ".join(ssir.unmodelled))
        return row
    refused = _solvable(system, inp)
    if refused != "ok":
        row.update(status="singular", detail=refused)
    return row


def _child(row: dict, db: Path, timeout: float, subs: bool) -> tuple[str, float | None, str]:
    """One ``transfer_function`` for a prepared row in a child process: (status, seconds, detail)."""
    cmd = [
        sys.executable,
        __file__,
        "--one",
        str(db / row["deck"]),
        "--output",
        row["output"],
        "--input",
        row["input"],
        *(["--subs"] if subs else []),
    ]
    t0 = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "timeout", timeout, f"over {timeout:g} s"
    seconds = round(time.monotonic() - t0, 1)
    try:
        result = json.loads(proc.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        tail = (proc.stderr.strip().splitlines() or ["no output"])[-1]
        return "error", seconds, tail[:200]
    return result["status"], seconds, result["detail"]


def _solve(row: dict, db: Path, timeout: float, subs: bool = False) -> dict:
    """The symbolic transfer function for one prepared row, and with ``subs`` the numeric one."""
    if row["status"]:
        return row
    status, seconds, detail = _child(row, db, timeout, subs=False)
    row.update(status=status, seconds=seconds, detail=detail)
    if subs:
        status, seconds, detail = _child(row, db, timeout, subs=True)
        row.update(subs_status=status, subs_seconds=seconds, subs_detail=detail)
    return row


def generic_op(ir) -> dict[str, float]:  # noqa: ANN001 — a Circuit2TF
    """Every symbol of the default-level model bound: the deck's numeric ``.param`` values, then
    ``simplify._coarse_op`` for the rest (the ``--subs`` column)."""
    names = set(build_system(small_signal_model(ir)).free_symbols)
    op = {n: float(ir.params[n]) for n in names if n in ir.params and ir.params[n].is_number}
    op.update(_coarse_op(names - set(op)))
    return op


def _one(deck: Path, output: str, input_: str, subs: bool = False) -> None:
    """Child mode: one ``transfer_function``, one JSON line on stdout."""
    logging.disable(logging.WARNING)
    try:
        out_pos, out_neg = output.split(",")
        in_pos, in_neg = input_.split(",")
        ir = from_file(deck)
        values = generic_op(ir) if subs else None
        res = transfer_function(ir, (out_pos, out_neg), (in_pos, in_neg), subs=values)
    except SingularSystemError as exc:
        print(json.dumps({"status": "singular", "detail": ", ".join(exc.nets)}))
        return
    except Exception as exc:  # noqa: BLE001 — reported as this row's error
        print(json.dumps({"status": "error", "detail": f"{type(exc).__name__}: {exc}"[:200]}))
        return
    counts = ((len(res.poles), "pole"), (len(res.zeros), "zero"))
    detail = ", ".join(f"{n} {word}{'' if n == 1 else 's'}" for n, word in counts)
    if subs:
        # above 1 Hz: the benches' 1 TH / 1 TF DC-feedback pair puts a pole near 1e-14 Hz
        freqs = sorted(f for p in res.poles if (f := p.frequency_hz) and f > 1.0)
        if freqs:
            detail += f"; lowest pole above 1 Hz: {freqs[0]:.3g} Hz"
    print(json.dumps({"status": "ok", "detail": detail}))


def _db_commit(db: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(db), "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True
    )
    return proc.stdout.strip() or "unknown"


def _markdown(report: dict) -> str:
    rows = report["rows"]
    counts = Counter(r["status"] for r in rows)
    lines = [
        "# netlist2tf corpus sweep",
        "",
        "Generated by `packages/spicexplorer-netlist2tf/scripts/corpus_sweep.py` from "
        "`corpus_sweep.json`; do not edit by hand.",
        "",
        f"- analog-db commit `{report['analog_db']}`, {len(rows)} `ac_open_loop` decks, "
        f"level `{report['level']}`, time limit {report['timeout_s']:g} s per deck, "
        f"run {report['date']}.",
        "- Status counts: " + ", ".join(f"{s} {counts.get(s, 0)}" for s in _STATUSES) + ".",
        "- `nodes` is the size of the driven MNA system; `ideal` is the same solvability check "
        "at level `ideal` (no `ro`); on an `unsupported` row it ran without the unmodelled "
        "devices.",
    ]
    subs = bool(report.get("subs"))
    if subs:
        sc = Counter(r["subs_status"] for r in rows if r["subs_status"])
        lines += [
            "- `subs` columns: the same transfer function with every symbol bound before the "
            "determinant (the deck's numeric `.param` values, else `simplify._coarse_op`'s "
            "generic operating point). Its poles are those of that generic bias, not of the "
            "design. Status counts: " + ", ".join(f"{s} {sc.get(s, 0)}" for s in _STATUSES) + ".",
        ]
    head = "| circuit | pdk | status | nodes | devices | output | input | ideal | s | detail |"
    rule = "|---|---|---|---|---|---|---|---|---|---|"
    if subs:
        head += " subs | subs s | subs detail |"
        rule += "---|---|---|"
    lines += ["", head, rule]
    for r in rows:
        cells = [
            r["circuit"],
            r["pdk"],
            r["status"],
            r["nodes"],
            r["devices"],
            r["output"],
            r["input"],
            r["ideal"],
            r["seconds"],
            r["detail"],
        ]
        if subs:
            cells += [r["subs_status"], r["subs_seconds"], r["subs_detail"]]
        text = ["" if c is None else str(c).replace("|", "/") for c in cells]
        lines.append("| " + " | ".join(text) + " |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="netlist2tf over every analog-db open-loop bench")
    ap.add_argument(
        "--db",
        type=Path,
        default=None,
        help="analog-db root (default: <project root>/examples/analog-db)",
    )
    ap.add_argument("--timeout", type=float, default=60.0, help="seconds per transfer function")
    ap.add_argument("--jobs", type=int, default=2, help="transfer functions run at once")
    ap.add_argument("--out", type=Path, default=_RESULTS, help="directory for the json and md")
    ap.add_argument("--circuit", default="*", help="glob over circuit names (default: all)")
    ap.add_argument(
        "--subs",
        action="store_true",
        help="also solve with every symbol bound to a generic operating point (numeric column)",
    )
    ap.add_argument("--one", type=Path, help=argparse.SUPPRESS)
    ap.add_argument("--output", help=argparse.SUPPRESS)
    ap.add_argument("--input", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if args.one:
        _one(args.one, args.output, args.input, subs=args.subs)
        return 0

    logging.disable(logging.WARNING)
    if args.db is None:
        from spicexplorer_core import project_root

        args.db = project_root() / "examples/analog-db"
    db = args.db.resolve()
    decks = sorted(db.glob(f"raw/{args.circuit}/*/ac_open_loop.spice"))
    if not decks:
        print(f"no raw/*/*/ac_open_loop.spice under {db}", file=sys.stderr)
        return 2
    prepared = [_prepare(db, d) for d in decks]
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        rows = list(pool.map(lambda r: _solve(r, db, args.timeout, args.subs), prepared))
    report = {
        "analog_db": _db_commit(db),
        "level": Fidelity.SOME_PARASITIC.value,
        "timeout_s": args.timeout,
        "date": datetime.date.today().isoformat(),
        "subs": args.subs,
        "counts": dict(Counter(r["status"] for r in rows)),
        "subs_counts": dict(Counter(r["subs_status"] for r in rows if r["subs_status"])),
        "rows": rows,
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "corpus_sweep.json").write_text(json.dumps(report, indent=1) + "\n")
    (args.out / "corpus_sweep.md").write_text(_markdown(report))
    print(" ".join(f"{s}={report['counts'].get(s, 0)}" for s in _STATUSES))
    if args.subs:
        print("subs: " + " ".join(f"{s}={report['subs_counts'].get(s, 0)}" for s in _STATUSES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
