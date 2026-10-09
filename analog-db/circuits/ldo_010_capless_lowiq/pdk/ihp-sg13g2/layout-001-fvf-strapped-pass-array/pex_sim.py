"""The post-layout scorecard: the entry's OWN benches, re-run on the extracted netlist.

The rule of the layout lane is that post-layout numbers come from the same bench definitions as
the pre-layout ones, so nothing here measures anything new — it only makes the kpex-extracted
subcircuit a drop-in replacement for the assembled ``.subckt ldo_010_capless_lowiq vdd vout vss``:

1. ``prep_pex_subckt`` (platform) rewrites the extractor's primitive ``M`` cards as ``XM`` — the
   IHP ngspice devices are subcircuits — and renames the block from the DRAWN cell name to the
   accession id the benches instantiate.
2. ``ngspice_cards`` turns kpex's 3-node ``rhigh`` primitives into ``XR`` subckt calls and renames
   its ``$nn`` anonymous nets (``$`` opens a comment in SPICE).
3. Every labelled net is a pin of the extracted block; ``VREF`` and the loop-break marker ``VLP``
   are sources, not drawn devices. Both go BACK INSIDE the block and the header is narrowed to the
   schematic's three pins, so ``vref``/``lp_brk``/``fb``/… become internal nodes exactly as in the
   schematic. kpex's substrate node ``VSUBS`` is tied to ``vss``.
4. The three MIM capacitors are re-attached by name: kpex cannot extract ``cap_cmim``, so their
   plates are stripped from the GDS before extraction. **What this costs is stated, not hidden:**
   the MIM bottom plate's (Metal5) coupling to the neighbourhood IS extracted, the top plate's is
   not.

Then the entry's own machinery does the rest — ``assemble()`` renders each of the 13 analyses at
the sizing of record, ``splice_subckt`` swaps the DUT, ``runner.run_text`` simulates, and
``ppa.metric_values`` scores the datasheet's metrics against their specs. There is no second
measurement path: the pre-layout column this run prints beside the post-layout one is the very
same code with the swap left out.

    analog-db layout run --circuit ldo_010_capless_lowiq --step pex -- --netlist <extracted>

**Vendored** from an agent-first design repo @ ``40cad45`` (``layout/postlayout.py``). The
netlist surgery below (``REINSERT``, ``ngspice_cards``, ``floor_zero_r``, ``pex_subckt``, the
what-ifs, ``select_pex_netlist``) is that file's, unchanged apart from the rename in (1) and the
paths; the driver is new, because the source repo drives its own ``ldo`` package's benches and
this entry drives analog-db's.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

from spicexplorer_analog_db import model, ppa, runner
from spicexplorer_analog_db.assemble import assemble

#: The DRAWN cell — the GDS top cell, and the name the extractor writes into its `.subckt`.
CELL = "ldo_ihp_capless"
#: The analog-db accession the benches instantiate. The extracted block is RENAMED to this on the
#: way in (`prep_pex_subckt(..., rename=)`); the drawn cell keeps its own name, which is what
#: every signed-off layout artefact — REVIEW.yaml, SIGNOFF.md, the LVS run — refers to.
CIRCUIT = "ldo_010_capless_lowiq"
PDK = "ihp-sg13g2"
HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

# The devices the layout does not carry, re-inserted inside the extracted block. Values stay
# symbolic: the deck's own `.param` block (from sizing.yaml) binds them, so the post-layout deck
# and the pre-layout deck are the same sizing point by construction.
REINSERT = """VREF vref vss dc {vref_val}
* kpex hangs every extracted ground capacitance on a substrate node VSUBS that is NOT in the
* subckt pin list; the p-substrate is at vss through the layout's own ptap ring, so tie it (a 0 V
* source rather than a rename, so the substrate branch stays visible to a reviewer). Without this
* the operating point is singular at `xdut.vsubs`.
VSUBSTIE VSUBS vss dc 0
VLP lp_brk vout dc 0
XCFF lp_brk fb cap_cmim w=c_ff_w l=c_ff_w
XCC ea_out ea_o1 cap_cmim w=c_comp_w l=c_comp_w
XCOUT vout vss cap_cmim w=c_out_w l=c_out_w m=c_out_m"""


# kpex writes an extracted poly resistor as a THREE-node primitive card,
#   ``R$36 lp_brk \\$37 vss 0.5 rhigh l=85 ps=0 b=0 m=1``   (w and l in um, no suffix)
# but ngspice's IHP ``rhigh`` is a 3-terminal SUBCIRCUIT (``.subckt rhigh 1 2 bn``), so the card
# has to become an ``XR`` call or ngspice reports ``unknown parameter (vss)`` -- it is trying to
# read the third node as the resistance. Journal: doc/journal/kpex-cards-are-not-ngspice-cards.md.
_RES_CARD = re.compile(
    r"^(R\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s+([-+.\d eE]+?)\s+(rhigh|rppd|rsil)\s*(.*)$", re.I)
_L_PARAM = re.compile(r"\bl\s*=\s*([-+.\deE]+)", re.I)


# The 2.5D R mesh anchors a named net on its `[Pin]` node with a **zero-ohm** resistor -- the
# stitcher means "merge these two nodes".  ngspice does not merge: it clamps the value to 1e-12
# ohm and puts a 1e12 S entry into a conductance matrix whose signal entries are ~1e-5 S, and the
# direct solve then returns an operating point that is not a solution of the network.  It is not
# a convergence failure -- it converges, silently, to the wrong answer, and it does so with both
# SPARSE and KLU and with a `.nodeset` seeded from the correct solution.  Measured on the LDO's
# feedback divider, sixteen IDENTICAL 126 kOhm segments in series between vout and vss:
#
#     two 0-ohm ties present   fb = 9.99 mV   (top half drops 186.25 mV/segment, bottom 1.25)
#     the same two at 1e-3     fb = 599.7 mV  (uniform 75 mV/segment, vout 1.1995 V, Iq 33.77 uA)
#
# The first row violates KCL at `fb` by 1.5 uA with no path to carry it, and it survives the
# resistors being replaced by ideal linear ones -- so it is arithmetic, not a model.  A finite
# floor is the smallest honest repair: 1 mOhm against a mesh whose own segments are 0.2-20 ohm
# adds at most a nanovolt, and unlike a node merge it leaves the netlist's shape (and every node
# name a reviewer might probe) intact.
R_FLOOR = 1e-3
_R_MESH = re.compile(r"^(R\S*)\s+(\S+)\s+(\S+)\s+([-+.\deE]+)\s*(.*)$")


def floor_zero_r(txt: str) -> tuple[str, int]:
    """Give every zero-valued mesh resistor a finite value; return the text and the count."""
    out, n = [], 0
    for ln in txt.splitlines():
        m = _R_MESH.match(ln)
        if m and m.group(1).lower().startswith("rext"):
            try:
                v = float(m.group(4))
            except ValueError:
                out.append(ln); continue
            if v == 0.0:
                n += 1
                ln = f"{m.group(1)} {m.group(2)} {m.group(3)} {R_FLOOR:g}" + (
                    f" {m.group(5)}" if m.group(5) else "")
        out.append(ln)
    return "\n".join(out) + ("\n" if txt.endswith("\n") else ""), n


def ngspice_cards(txt: str) -> str:
    """kpex element cards -> cards ngspice can read."""
    out = []
    for ln in txt.splitlines():
        s = ln.strip()
        m = _RES_CARD.match(s)
        if m:
            name, n1, n2, n3, w, model, rest = m.groups()
            lm = _L_PARAM.search(rest)
            length = f"{float(lm.group(1)):g}u" if lm else "1u"
            rest = _L_PARAM.sub("", rest).strip()
            keep = " ".join(p for p in rest.split() if p.split("=")[0].lower() in ("m",))
            ln = f"X{name} {n1} {n2} {n3} {model} w={float(w):g}u l={length}" + (f" {keep}" if keep else "")
        out.append(ln)
    # `$` opens an in-line comment in SPICE, so the extractor's anonymous nets (`\$21`) must be
    # renamed before ngspice ever sees them.
    return re.sub(r"\\?\$(\w+)", r"n_\1", "\n".join(out)) + "\n"


def pex_subckt(pex_netlist: Path) -> str:
    """The extracted block, made pin-compatible with the schematic subckt."""
    from spicexplorer_signoff.postlayout import prep_pex_subckt

    raw = Path(pex_netlist).read_text()
    # An already-prepared block (`asbuilt/core_pex.sp`, `extracted_subckt.spice`) is NOT an
    # extractor output: preparing it twice re-inserts VREF/VSUBSTIE/VLP and the three MIM cards
    # a second time and every bench fails at the operating point.  Say so instead of doing it.
    if "VSUBSTIE" in raw:
        raise SystemExit(f"{pex_netlist} is already a prepared block (it carries VSUBSTIE) — "
                         "point --netlist at the extractor's own output, or read it directly")
    txt = ngspice_cards(prep_pex_subckt(pex_netlist, CELL, rename=CIRCUIT))
    txt, n_zero = floor_zero_r(txt)
    if n_zero:
        print(f"pex: {n_zero} zero-ohm mesh tie(s) floored at {R_FLOOR:g} Ohm", flush=True)
    # The header spills onto `+` continuation lines: every labelled net becomes a pin, so the
    # extracted block has ~15 of them where the schematic subckt has three.
    m = re.search(rf"(?im)^\.subckt\s+{CIRCUIT}\b[^\n]*\n(?:\+[^\n]*\n)*", txt)
    if not m:
        raise SystemExit(f"no .subckt {CELL} in {pex_netlist}")
    head = m.group(0)
    pins = [w for w in re.sub(r"(?m)^\+", " ", head).split()[2:] if "=" not in w]
    missing = {"vdd", "vout", "vss"} - {p.lower() for p in pins}
    if missing:
        raise SystemExit(f"extracted subckt is missing pin(s) {sorted(missing)}: {pins}")
    # Narrow the header to the schematic's three pins; every other labelled net (vref, lp_brk,
    # fb, ea_out ...) becomes an internal node again, which is what the benches expect.
    txt = txt[: m.start()] + f".subckt {CIRCUIT} vdd vout vss\n" + REINSERT + "\n" + txt[m.end():]
    return txt


_C_CARD = re.compile(r"^(C\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s*$")


def filter_caps(block: str, keep: str = "", drop: str = "") -> tuple[str, int, int]:
    """Delete extracted coupling/ground capacitors, for a what-if.

    ``keep`` (comma list) keeps only the `Cext_` cards that touch one of those nets; ``drop``
    keeps everything except those.  Nothing else in the block changes, so the difference between
    two runs is exactly the capacitance named — this is how "the `gate` parasitics alone move S7
    by X" is measured rather than asserted (review-003 F3).  The re-inserted MIM cards are `X`
    calls, not `C` cards, so they always survive."""
    kk = {n for n in keep.split(",") if n}
    dd = {n for n in drop.split(",") if n}
    out, gone, left = [], 0, 0
    for ln in block.splitlines():
        m = _C_CARD.match(ln.strip())
        if m and m.group(1).lower().startswith("cext"):
            nets = {m.group(2), m.group(3)}
            hit = bool(nets & kk) if kk else not (nets & dd)
            if not hit:
                gone += 1
                continue
            left += 1
        out.append(ln)
    return "\n".join(out) + "\n", left, gone


def insert_vss_return(block: str, ohm: float, kelvin: str = "XCOUT") -> tuple[str, int]:
    """What-if: put the drawn `vss` return resistance in circuit (review-004 **F9**).

    The extraction is CC, so it carries no wire resistance at all: the committed `psrr_1k` is
    measured with an IDEAL ground return. This renames `vss` to `vss_ret` on every card inside
    the block except the subckt header and the Kelvin-returned devices (`XCOUT`, whose bottom
    plate has its own strap to the pin — PLAN A10), and adds one resistor `vss_ret -> vss`.
    `ohm` is therefore the COMMON series element, the quantity F9 says the budget should be
    written on; the per-device spread beyond it is a separate, much smaller term.
    """
    keep = {k.strip().upper() for k in kelvin.split(",") if k.strip()}
    out, touched = [], 0
    for ln in block.splitlines():
        t = ln.split()
        if (t and not ln.lstrip().startswith("*") and not ln.lstrip().startswith(".")
                and t[0].upper() not in keep and "vss" in t[1:]):
            ln = " ".join([t[0]] + ["vss_ret" if x == "vss" else x for x in t[1:]])
            touched += 1
        out.append(ln)
    txt = "\n".join(out)
    i = txt.lower().rindex(".ends")
    return txt[:i] + f"Rvssret vss_ret vss {ohm:g}\n" + txt[i:] + "\n", touched



def select_pex_netlist(pex_dir, explicit: str | None = None,
                       record: str | None = None) -> tuple[Path, str]:
    """`(path, "raw"|"stitched")` — WHICH extracted netlist the benches measure.

    review-004 **F27**. For an RC/R run the platform writes two files side by side:

    * ``<cell>_k25d_pex_netlist.spice`` — kpex's own output, whose resistor mesh is an
      electrical island (no card joins a mesh node to a device pin), and
    * ``<cell>_k25d_pex_netlist_stitched.spice`` — the repaired one, which is what
      ``PexResult.netlist_path`` names.

    The old rule here was ``rglob("*_pex_netlist.spice")`` + "exactly one match". The stitched
    name does not match that pattern, so with both files present the glob found exactly one,
    reported no ambiguity, and measured the netlist the extractor did **not** name — a scorecard
    from the unstitched file, silently. Hence: an explicit path wins, else the PEX stage's own
    record (`signoff.json` → `pex.netlist`), else the directory — and if the directory holds both
    kinds and nobody said which, this raises instead of choosing.
    """
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            raise SystemExit(f"--netlist {p} does not exist")
        return p, ("stitched" if p.name.endswith("_stitched.spice") else "raw")
    if record:
        rp = Path(record)
        if rp.is_file():
            named = ((json.loads(rp.read_text()).get("pex") or {}).get("netlist"))
            if named and Path(named).is_file():
                p = Path(named)
                # The record is only evidence about the directory it belongs to. A run dir that
                # holds a CC stage AND an RC stage has ONE signoff.json, whose `pex.netlist` is
                # whichever stage wrote last -- so honouring it while the caller asked for the
                # other stage's directory measures the wrong extraction and says the right name
                # (review-005: `--pex .../pex_rc --record .../signoff.json` silently scored the
                # CC netlist). If they disagree, the explicit directory wins and says so.
                if Path(pex_dir).resolve() in p.resolve().parents:
                    return p, ("stitched" if p.name.endswith("_stitched.spice") else "raw")
                print(f"note: {rp} names {p}, which is not under the requested {pex_dir}; "
                      "reading the directory instead", flush=True)
    pex_dir = Path(pex_dir)
    stitched = sorted(pex_dir.rglob("*_pex_netlist_stitched.spice"))
    raw = sorted(pex_dir.rglob("*_pex_netlist.spice"))   # does NOT match the stitched name
    hits = [(p, "stitched") for p in stitched] + [(p, "raw") for p in raw]
    if not hits:
        raise SystemExit(f"no kpex netlist under {pex_dir} — run layout/signoff.py first")
    # One RC run leaves a matched PAIR: `<stem>.spice` and `<stem>_stitched.spice`.  The stitched
    # one is the netlist `PexResult.netlist_path` names and the only one whose mesh is in the
    # circuit, so the pair is not an ambiguity — it is answered, loudly.  Anything else (two runs
    # under one directory) is an ambiguity and stops.
    if len(stitched) == 1 and len(raw) == 1 and raw[0].stem + "_stitched" == stitched[0].stem:
        print(f"note: {pex_dir} holds an RC pair; measuring the STITCHED netlist "
              f"({stitched[0].name}) — the raw one's resistor mesh is not in the circuit. "
              "Pass --netlist to override.", flush=True)
        return stitched[0], "stitched"
    if len(hits) > 1:
        raise SystemExit(
            f"{len(hits)} extracted netlists under {pex_dir} (stitched: {len(stitched)}, "
            "raw: {}); name the one THIS scorecard measures with --netlist:\n  ".format(len(raw))
            + "\n  ".join(f"{p} [{k}] ({datetime.datetime.fromtimestamp(p.stat().st_mtime)})"
                          for p, k in hits))
    return hits[0]


def recorded_pex_dir() -> str:
    """The directory of the extraction behind the committed row of record.

    ``out/pex/rc_netlist.sha256`` carries the digest and the mesh census of that netlist but not
    the netlist: a ~5 000-card extractor output is a rawfile, and rawfiles are not committed. Its
    first non-comment line names the file, so a re-run on the SAME extraction needs no arguments
    while a re-extraction is an explicit ``--pex``/``--netlist``. The path is recorded
    ``$SX_SCRATCH``-relative (no user's home in a committed file), so it is expanded here."""
    digest = OUT / "pex" / "rc_netlist.sha256"
    if digest.is_file():
        for ln in digest.read_text().splitlines():
            if ln.startswith("# netlist:"):
                p = Path(os.path.expandvars(ln.split(":", 1)[1].strip()))
                if p.is_file():
                    return str(p.parent)
    raise SystemExit(
        "no extracted netlist to measure: the recorded one "
        f"({digest}) is not on this machine. Re-extract with\n"
        "  analog-db layout run --circuit ldo_010_capless_lowiq --step signoff -- "
        "--stages pex --pex-mode RC\n"
        "then pass its directory with --pex.")



# --------------------------------------------------------------------- the claim it reproduces --
# `out/scorecard_post_rc.json` is the SIGNED post-layout row of record, carried over from the
# source repo, whose scorer names and units are its own (millivolts, microamps, kilohertz). This
# map is the only place the two vocabularies meet: analog-db metric -> (source column, scale from
# the source's unit to the datasheet's SI unit). A metric absent from the map is simply not
# compared; a metric present but missing from the file is reported as such.
CLAIM_MAP: dict[str, tuple[str, float]] = {
    "v_out":            ("v_out_v",           1.0),
    "i_q":              ("i_q_ua",            1e-6),
    "load_reg":         ("load_reg_mv",       1e-3),
    "line_reg":         ("line_reg_mv",       1e-3),
    "v_dropout":        ("v_dropout_mv",      1e-3),
    "psrr_vdd_db":      ("psrr_1k_db",        1.0),
    "v_undershoot":     ("v_undershoot_mv",   1e-3),
    "pm_loop_deg":      ("pm_loop_deg",       1.0),
    "loopgain_db":      ("loopgain_db",       1.0),
    "ugf_loop_hz":      ("ugf_loop_khz",      1e3),
    "gm_loop_db":       ("gm_loop_db",        1.0),
    "ms_peak_db":       ("ms_peak_db",        1.0),
    "tloop_ph_dc_deg":  ("tloop_ph_dc_deg",   1.0),
    "zout_peak_db":     ("zout_peak_db",      1.0),
    "t_transient":      ("t_transient_us",    1e-6),
    "v_line_pp":        ("v_line_pp_mv",      1e-3),
    "vn_out_rms":       ("vn_out_urms",       1e-6),
    # Measured by the `psrr_1m` bench and carried in the source scorecard, but NOT a metric of
    # the `ldo` class datasheet, so `ppa.metric_values` does not produce it: the comparison prints
    # the claim with no measurement beside it rather than dropping the row and hiding the gap.
    "psrr_1m_db":       ("psrr_1m_db",        1.0),
}


def run_benches(circuit, decks: dict[str, str], corner: str) -> dict:
    """Simulate each assembled deck; return the ``analyses`` block ``ppa.metric_values`` reads."""
    spice = runner.native_pdk_runner(PDK)
    out: dict[str, dict] = {}
    for aid, deck in decks.items():
        try:
            out[aid] = {"status": "ok",
                        "measures": runner.run_text(deck, f"{circuit.id}/{aid}@{PDK}/{corner}",
                                                    spice)}
            print(f"    {aid}: ok", flush=True)
        except runner.SimError as exc:
            out[aid] = {"status": "sim_error", "measures": {}, "error": str(exc)[:400]}
            print(f"    {aid}: SIM ERROR — {str(exc)[:160]}", flush=True)
    return out


def compare_to_claim(rows: dict, claim_path: Path) -> list[dict]:
    """Every mapped metric against the committed row of record, in the datasheet's own units."""
    if not claim_path.is_file():
        return []
    claim = (json.loads(claim_path.read_text()).get("post") or {})
    table = []
    for metric, (col, scale) in sorted(CLAIM_MAP.items()):
        got = (rows.get(metric) or {}).get("value")
        if col not in claim:
            table.append({"metric": metric, "claim": None, "measured": got, "rel": None,
                          "note": f"{col} absent from the claim"})
            continue
        want = float(claim[col]) * scale
        rel = None if got is None else (
            abs(got - want) / abs(want) if want else abs(got - want))
        table.append({"metric": metric, "claim": want, "measured": got, "rel": rel})
    return table


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pex", default=None,
                    help="directory holding the extracted netlist (default: the one the recorded "
                         "row of record names, see out/pex/rc_netlist.sha256)")
    ap.add_argument("--netlist", default=None,
                    help="the extracted netlist to measure (review-004 F27); wins over --pex")
    ap.add_argument("--record", default=None, help="signoff.json naming the netlist")
    ap.add_argument("--corner", default="tt")
    ap.add_argument("--out-dir", default=None,
                    help="where the scorecard goes (a what-if must NOT overwrite the record)")
    ap.add_argument("--claim", default=str(OUT / "scorecard_post_rc.json"),
                    help="the committed row this run is compared against")
    ap.add_argument("--no-pre", action="store_true",
                    help="skip the pre-layout control column (it is the entry's own scoreboard "
                         "row and is reproduced by `analog-db run`)")
    ap.add_argument("--keep-c", default="", help="what-if: keep only the extracted C on these nets")
    ap.add_argument("--drop-c", default="", help="what-if: drop the extracted C on these nets")
    ap.add_argument("--no-c", action="store_true", help="what-if: drop every extracted C")
    ap.add_argument("--vss-r", type=float, default=None,
                    help="what-if: insert the drawn vss return resistance (Ohm) between the "
                         "internal ground and the pin, XCOUT excepted (review-004 F9)")
    a = ap.parse_args()

    whatif = bool(a.keep_c or a.drop_c or a.no_c or a.vss_r is not None)
    out_dir = Path(a.out_dir) if a.out_dir else OUT / "pex"
    if whatif and a.out_dir is None:
        raise SystemExit("a what-if run needs --out-dir: it must not overwrite the record")
    out_dir.mkdir(parents=True, exist_ok=True)

    if a.netlist:
        netlist, kind = select_pex_netlist(".", explicit=a.netlist)
    else:
        pex_dir = a.pex or recorded_pex_dir()
        netlist, kind = select_pex_netlist(pex_dir, record=a.record)
    print(f"pex netlist: {netlist} [{kind}]", flush=True)
    block = pex_subckt(netlist)
    if a.keep_c or a.drop_c or a.no_c:
        block, left, gone = filter_caps(block, "__none__" if a.no_c else a.keep_c, a.drop_c)
        print(f"what-if: kept {left} extracted C card(s), dropped {gone}", flush=True)
    if a.vss_r is not None:
        block, n = insert_vss_return(block, a.vss_r)
        print(f"what-if: {a.vss_r} Ohm vss return, {n} card(s) moved off the pin", flush=True)
    (out_dir / "extracted_subckt.spice").write_text(block)

    from spicexplorer_signoff.postlayout import splice_subckt

    circuit = model.load_circuit(CIRCUIT)
    benches = [b for b in circuit.analyses if circuit.analysis(b).get("enabled", True)]
    pre_decks = {b: assemble(circuit, b, PDK, a.corner) for b in benches}
    post_decks = {b: splice_subckt(pre_decks[b], block, CIRCUIT, check_pins=False)
                  for b in benches}

    doc: dict = {"schema": "spicexplorer/results@1", "circuit": CIRCUIT, "pdk": PDK,
                 "corner": a.corner, "pex_netlist": str(netlist), "pex_netlist_kind": kind}
    if not (whatif or a.no_pre):
        print("pre-layout:", flush=True)
        pre_an = run_benches(circuit, pre_decks, a.corner)
        doc["pre"] = ppa.metric_values(circuit, pre_an)
        doc["pre_bench_status"] = {b: r["status"] for b, r in sorted(pre_an.items())}
    print("post-layout:", flush=True)
    post_an = run_benches(circuit, post_decks, a.corner)
    doc["post"] = ppa.metric_values(circuit, post_an)
    doc["post_measures"] = {b: r["measures"] for b, r in sorted(post_an.items())}
    doc["bench_status"] = {b: r["status"] for b, r in sorted(post_an.items())}
    doc["post_violations"] = sorted(k for k, v in doc["post"].items() if v["spec"] == "fail")
    if whatif:
        doc["whatif"] = {"keep_c": a.keep_c, "drop_c": a.drop_c, "no_c": a.no_c,
                         "vss_r": a.vss_r}
    else:
        doc["vs_claim"] = compare_to_claim(doc["post"], Path(a.claim))
        doc["claim"] = str(Path(a.claim))

    (out_dir / "scorecard.json").write_text(json.dumps(doc, indent=1, sort_keys=False) + "\n")
    print(f"\n  {len(doc['bench_status'])} benches, "
          f"{sum(1 for s in doc['bench_status'].values() if s == 'ok')} ok; "
          f"{len(doc['post_violations'])} spec violation(s)"
          + (f": {doc['post_violations']}" if doc["post_violations"] else ""))
    worst = [r for r in doc.get("vs_claim", []) if r.get("rel") is not None]
    if worst:
        w = max(worst, key=lambda r: r["rel"])
        print(f"  vs the committed row of record: {len(worst)} metric(s) compared, "
              f"worst relative difference {w['rel']:.3g} on {w['metric']}")
    print("  wrote", out_dir / "scorecard.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
