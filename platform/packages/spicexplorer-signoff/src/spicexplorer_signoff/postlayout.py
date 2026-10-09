"""Post-layout bench reuse: make an extracted netlist a drop-in for the schematic subckt.

The rule of the layout lane is that post-layout numbers come from the block's **own**
frozen benches, so the only thing this module does is netlist surgery:

- :func:`prep_pex_subckt` — the kpex/KLayout-extracted netlist uses primitive ``M`` cards
  (LVS convention); ngspice's IHP devices are *subcircuits*, so cards become ``XM…``
  (the subckt accepts ``w/l/as/ad/ps/pd``; with ``as/ad`` present the model's
  ``pre_layout`` junction estimate is bypassed). Optionally renames the subckt.
- :func:`extract_subckt` / :func:`splice_subckt` — pull ``.subckt NAME … .ends`` out of
  a text and replace the same-named block in a bench deck, checking pin lists agree.
- :func:`deltas` — pre/post scorecard diff with the same keys.
- :func:`score_c_budgets` / :func:`c_budget_table` — per-net extracted C against the layout
  brief's balanced / one-sided / differential budgets, and that table in Markdown.
- :func:`select_pex_netlist` — WHICH extracted netlist a scorecard measured, as a
  :class:`MeasuredNetlist` provenance record; stitched-preferred, record-within-dir, and
  loud (an exception) on a real ambiguity.
"""

from __future__ import annotations

import datetime
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .pex import _ELEM, _net, _num


def _read(x: str | Path) -> str:
    """Accept a path or netlist text (text = anything with a newline or that is not a file)."""
    if isinstance(x, Path):
        return x.read_text()
    if "\n" in x or len(x) > 4000:
        return x
    try:
        p = Path(x)
        return p.read_text() if p.is_file() else x
    except OSError:
        return x


def prep_pex_subckt(
    pex_netlist: str | Path,
    cell: str,
    *,
    rename: str | None = None,
    x_prefix: str = "X",
    strip_comments: bool = False,
) -> str:
    """Return the extracted subckt text with ``M``→``XM`` cards (and optional rename)."""
    text = _read(pex_netlist)
    out: list[str] = []
    prev_rewritten = False
    for line in text.splitlines():
        s = line.lstrip()
        if strip_comments and s.startswith("*"):
            continue
        if re.match(r"^[Mm]\S*\s", s):
            line = line[: len(line) - len(s)] + x_prefix + s
            prev_rewritten = True
        elif s.startswith("+") and prev_rewritten:
            pass
        else:
            prev_rewritten = False
        out.append(line)
    txt = "\n".join(out) + "\n"
    if rename and rename != cell:
        txt = re.sub(rf"(?im)^(\.subckt\s+){re.escape(cell)}\b", rf"\g<1>{rename}", txt)
        txt = re.sub(rf"(?im)^(\.ends\s+){re.escape(cell)}\b", rf"\g<1>{rename}", txt)
    return txt


def extract_subckt(text: str | Path, name: str) -> tuple[str, list[str]]:
    """(block text incl. .subckt/.ends lines, pin list) for subckt ``name``; KeyError if absent."""
    t = _read(text)
    m = re.search(rf"(?ims)^\.subckt\s+{re.escape(name)}\b([^\n]*)\n(.*?)^\.ends\b[^\n]*", t)
    if not m:
        raise KeyError(f"no .subckt {name} in text")
    header = m.group(1)
    # continuation lines of the header (+ ...) before the first element
    pins = [p for p in header.split() if "=" not in p]
    body = m.group(2)
    for line in body.splitlines():
        if line.lstrip().startswith("+"):
            pins += [p for p in line.lstrip()[1:].split() if "=" not in p]
        else:
            break
    return m.group(0), pins


def splice_subckt(
    deck: str | Path, replacement: str | Path, name: str, *, check_pins: bool = True
) -> str:
    """Replace ``.subckt name … .ends`` in ``deck`` with the block from ``replacement``."""
    d = _read(deck)
    old, old_pins = extract_subckt(d, name)
    new, new_pins = extract_subckt(replacement, name)
    if check_pins and [p.lower() for p in old_pins] != [p.lower() for p in new_pins]:
        raise ValueError(f"pin list mismatch for {name}: deck {old_pins} vs replacement {new_pins}")
    return d.replace(old, new.rstrip("\n"), 1)


_SI = {"a": 1e-18, "f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "meg": 1e6}


def _val(tok: str) -> float:
    m = re.match(r"^([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)(meg|[afpnumk])?$", tok, re.I)
    if not m:
        raise ValueError(f"bad number {tok!r}")
    return float(m.group(1)) * _SI.get((m.group(2) or "").lower(), 1.0)


def to_lvs_reference(
    subckt: str | Path,
    name: str,
    *,
    cell: str | None = None,
    mos_re: str = r"_(n|p)mos$",
    cap_models: tuple[str, ...] = ("cap_cmim", "rfcmim"),
    combine_m: bool = True,
) -> str:
    """Translate an ngspice-style subckt (IHP devices as ``X`` subckt calls) into the flat
    ``M`` / ``C`` card netlist the KLayout LVS deck reads.

    - ``x<n> d g s b <mos> w= l= [ng=] [m=]`` → ``M<n> d g s b <mos> w=<w·m> l=<l>``. The
      layout draws ``ng`` fingers × ``m`` instances that the LVS combiner merges into one
      device of the summed width, so the reference carries the total width and no ``ng``/``m``
      (``combine_m=False`` keeps ``m=`` instead).
    - ``x<n> a b cap_cmim w= l= m=`` → ``C<n> a b cap_cmim w= l= m=`` (the deck compares
      w/l, m as a secondary parameter after combining parallel units).
    - other cards and the ``.subckt`` header pass through; ``cell`` renames the subckt (the
      LVS topcell must equal the schematic subckt name).
    """
    block, _ = extract_subckt(_read(subckt), name)
    out: list[str] = []
    for line in block.splitlines():
        s = line.strip()
        toks = s.split()
        if not toks or s.startswith(("*", "+", ".")):
            if cell and s.lower().startswith(".subckt"):
                toks[1] = cell
                line = " ".join(toks)
            elif cell and s.lower().startswith(".ends"):
                line = f".ends {cell}"
            out.append(line)
            continue
        if toks[0][0].lower() == "x":
            params = {k.lower(): v for k, v in (t.split("=", 1) for t in toks if "=" in t)}
            plain = [t for t in toks if "=" not in t]
            model = plain[-1]
            if re.search(mos_re, model, re.I) and len(plain) == 6:
                w = _val(params["w"]) * (int(float(params.get("m", "1"))) if combine_m else 1)
                card = f"M{plain[0][1:]} {' '.join(plain[1:5])} {model} w={w * 1e6:.6g}u l={_val(params['l']) * 1e6:.6g}u"
                if not combine_m and "m" in params:
                    card += f" m={params['m']}"
                out.append(card)
                continue
            if model in cap_models and len(plain) in (4, 5):
                extra = " ".join(f"{k}={params[k]}" for k in ("w", "l", "m") if k in params)
                out.append(f"C{plain[0][1:]} {' '.join(plain[1:-1])} {model} {extra}".rstrip())
                continue
        out.append(line)
    return "\n".join(out) + "\n"


def deltas(pre: dict[str, float], post: dict[str, float]) -> dict[str, dict[str, float | None]]:
    """{key: {pre, post, delta, rel}} over the keys present in both scorecards."""
    out: dict[str, dict[str, float | None]] = {}
    for k in pre:
        if k in post and isinstance(pre[k], (int, float)) and isinstance(post[k], (int, float)):
            d = float(post[k]) - float(pre[k])
            out[k] = {
                "pre": float(pre[k]),
                "post": float(post[k]),
                "delta": d,
                "rel": (d / abs(float(pre[k]))) if pre[k] else None,
            }
    return out


# ------------------------------------------------------ per-net C against the layout brief ----


def _load_json(x: Mapping[str, Any] | str | Path) -> Mapping[str, Any]:
    return x if isinstance(x, Mapping) else json.loads(Path(x).read_text())


def _twins(brief: Mapping[str, Any]) -> dict[str, str]:
    """net -> its other half: a net's own ``twin``, else ``structure.mirror_pairs``; both ways."""
    pairs: dict[str, str] = {}
    for pair in (brief.get("structure") or {}).get("mirror_pairs") or []:
        if len(pair) == 2:
            pairs.setdefault(pair[0], pair[1])
            pairs.setdefault(pair[1], pair[0])
    twin: dict[str, str] = {}
    for n in brief.get("nets") or []:
        t = n.get("twin") or pairs.get(n["name"])
        if t:
            twin[n["name"]] = t
    for net, t in list(twin.items()):
        twin.setdefault(t, net)
    return twin


def _c_dont_care(brief: Mapping[str, Any]) -> set[str]:
    """``dont_care`` as a list of names (every budget), or ``{"capacitance": [...], ...}``."""
    dc = brief.get("dont_care")
    if isinstance(dc, Mapping):
        dc = dc.get("capacitance")
    return {str(x) for x in dc} if isinstance(dc, (list, tuple)) else set()


def score_c_budgets(
    pex_text: str | Path,
    brief: Mapping[str, Any] | str | Path,
    *,
    exclude: str | Iterable[str] = (),
) -> list[dict[str, Any]]:
    """One row per ``brief["nets"]`` entry: its extracted C [fF] against the brief's budgets.

    The brief states three budgets per net because they are three different perturbations, so
    the extraction is split the same way (``bal + diff`` is the net's whole
    :func:`~spicexplorer_signoff.pex.summarize_parasitics` sum):

    * ``bal_ff`` (budget ``budget_c_ff``) — balanced: C from the net to every partner but its
      twin. Couplings to other signal nets count here too, so this column is the conservative one.
    * ``asym_ff`` (``budget_c_asym_ff``) — one-sided: ``|bal(net) - bal(twin)|``.
    * ``diff_ff`` (``budget_c_diff_ff``) — differential: only the C drawn between the twins.

    The twin is the net's ``twin``, else its ``structure.mirror_pairs`` partner; without one the
    one-sided and differential columns are ``None``. ``pex_text`` is the extracted netlist or its
    path, ``brief`` the parsed ``brief.json`` or its path.

    ``exclude`` is one or more regular expressions matched (case-insensitively) at the start of a
    C card's NAME: the intentional capacitors a flow splices back into the extracted subckt are
    design devices, not parasitics, and are named by the caller, never by value. Self-loop cards
    are skipped, as in :func:`~spicexplorer_signoff.pex.scan_parasitics`.

    ``*_ok`` is ``None``, never a pass, when there is no budget, when the net is a capacitance
    don't-care (``dont_care`` as a list, or its ``capacitance`` list), or when the net is named
    nowhere in the extraction (``found`` False: a renamed net would otherwise sum to 0 fF and pass).
    """
    text = _read(pex_text)
    b = _load_json(brief)
    pats = [re.compile(p, re.I) for p in ([exclude] if isinstance(exclude, str) else exclude)]
    present: set[str] = set()
    cards: list[tuple[str, str, float]] = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("*"):
            continue
        present.update(_net(t) for t in s.split() if "=" not in t)
        m = _ELEM.match(s)
        if not m or m.group(1).upper() != "C":
            continue
        a, c, v = _net(m.group(2)), _net(m.group(3)), _num(m.group(4))
        if v is None or a == c or any(p.match(s.split()[0]) for p in pats):
            continue
        cards.append((a, c, v * 1e15))

    twin, dont_care = _twins(b), _c_dont_care(b)

    def bal(net: str) -> float:
        t = twin.get(net)
        return sum(v for a, c, v in cards if net in (a, c) and t not in (a, c))

    def dif(net: str, t: str) -> float:
        return sum(v for a, c, v in cards if {a, c} == {net, t})

    rows: list[dict[str, Any]] = []
    for n in b.get("nets") or []:
        name = n["name"]
        t = twin.get(name)
        found = name in present
        pair = found and t is not None and t in present
        r: dict[str, Any] = {
            "net": name,
            "twin": t,
            "dont_care": name in dont_care,
            "found": found,
            "bal_ff": bal(name) if found else None,
            "bal_twin_ff": bal(t) if pair and t else None,
            "asym_ff": abs(bal(name) - bal(t)) if pair and t else None,
            "diff_ff": dif(name, t) if pair and t else None,
            "budget_bal_ff": n.get("budget_c_ff"),
            "budget_asym_ff": n.get("budget_c_asym_ff"),
            "budget_diff_ff": n.get("budget_c_diff_ff"),
        }
        for k in ("bal", "asym", "diff"):
            limit, got = r[f"budget_{k}_ff"], r[f"{k}_ff"]
            if r["dont_care"] or limit is None or got is None:
                r[f"{k}_ok"] = None
            else:
                r[f"{k}_ok"] = bool(got <= limit)
        rows.append(r)
    return rows


def c_budget_table(rows: list[dict[str, Any]]) -> str:
    """:func:`score_c_budgets` rows as a Markdown table: each measured column beside its budget.

    A budget cell reads ``ok`` / ``**OVER**``, ``unchecked`` (no measured value to hold against
    it), ``no bound`` (measured, no budget) or ``don't care``. Name the PEX mode and halo in the
    text around it: two extractions compare only at one halo.
    """

    def val(x: float | None) -> str:
        return "-" if x is None else f"{x:.2f}"

    def bud(limit: float | None, got: float | None, ok: bool | None, dont_care: bool) -> str:
        if limit is None:
            return "-" if got is None else "don't care" if dont_care else "no bound"
        if dont_care:
            return f"{limit:.2f} (don't care)"
        return f"{limit:.2f} " + {True: "ok", False: "**OVER**", None: "unchecked"}[ok]

    out = [
        "| net | twin | balanced C [fF] | budget | one-sided C [fF] | budget "
        "| differential C [fF] | budget |",
        "|---|---|---:|---|---:|---|---:|---|",
    ]
    for r in rows:
        cells = [f"`{r['net']}`", f"`{r['twin']}`" if r["twin"] else "-"]
        for k in ("bal", "asym", "diff"):
            got = r[f"{k}_ff"]
            shown = "not in extraction" if k == "bal" and not r["found"] else val(got)
            cells += [shown, bud(r[f"budget_{k}_ff"], got, r[f"{k}_ok"], r["dont_care"])]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


# --------------------------------------------------------------- which netlist was measured ----


@dataclass(frozen=True)
class MeasuredNetlist:
    """WHICH extracted netlist a scorecard measured, and how that was decided.

    A post-layout scorecard is only as good as its answer to "extracted from what?". Record
    this beside the numbers: ``path`` is the file, ``kind`` is ``"stitched"`` or ``"raw"``, and
    ``how`` says which rule chose it (``"explicit"`` / ``"record"`` / ``"directory"``).
    """

    path: Path
    kind: str
    how: str
    note: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "pex_netlist": str(self.path),
            "pex_netlist_kind": self.kind,
            "pex_netlist_how": self.how,
            **({"pex_netlist_note": self.note} if self.note else {}),
        }


def _kind(p: Path) -> str:
    return "stitched" if p.name.endswith("_stitched.spice") else "raw"


def select_pex_netlist(
    pex_dir: str | Path,
    *,
    explicit: str | Path | None = None,
    record: str | Path | None = None,
    stitched_glob: str = "*_pex_netlist_stitched.spice",
    raw_glob: str = "*_pex_netlist.spice",
) -> MeasuredNetlist:
    """Pick the extracted netlist a post-layout scorecard measures, loudly.

    For an RC/R run the extractor's own output and the repaired one sit side by side:

    * ``<cell>_..._pex_netlist.spice`` — kpex's, whose resistor mesh is an electrical island
      (no card joins a mesh node to a device pin), and
    * ``<cell>_..._pex_netlist_stitched.spice`` — the one :attr:`PexResult.netlist_path` names,
      the only one whose mesh is in the circuit.

    A ``rglob("*_pex_netlist.spice")`` + "exactly one match" rule does **not** match the
    stitched name, so with both present it found exactly one file, reported no ambiguity, and
    silently measured the netlist the extractor did *not* name. Hence the order:

    1. ``explicit`` wins — the caller said which.
    2. ``record`` (a ``signoff.json`` whose ``pex.netlist`` names one) — but **only if that
       file is under ``pex_dir``**. A run dir holding a CC stage *and* an RC stage has ONE
       ``signoff.json``, whose ``pex.netlist`` is whichever stage wrote last; honouring it while
       the caller asked for the other stage's directory measures the wrong extraction and reports
       the right name. When they disagree the explicit directory wins, and says so.
    3. The directory. A matched RC **pair** (``<stem>.spice`` + ``<stem>_stitched.spice``) is not
       an ambiguity — it is answered, in favour of the stitched one, out loud. Anything else
       (two runs under one directory) raises rather than choosing.
    """
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            raise FileNotFoundError(f"the named extracted netlist {p} does not exist")
        return MeasuredNetlist(p, _kind(p), "explicit")

    pex_dir = Path(pex_dir)
    disagreed = ""
    if record and Path(record).is_file():
        named = (json.loads(Path(record).read_text()).get("pex") or {}).get("netlist")
        if named and Path(named).is_file():
            p = Path(named)
            if pex_dir.resolve() in p.resolve().parents:
                return MeasuredNetlist(p, _kind(p), "record")
            disagreed = (
                f"{record} names {p}, which is not under the requested {pex_dir}; "
                "reading the directory instead"
            )

    stitched = sorted(pex_dir.rglob(stitched_glob))
    raw = sorted(pex_dir.rglob(raw_glob))  # does NOT match the stitched name
    hits = [(p, "stitched") for p in stitched] + [(p, "raw") for p in raw]
    if not hits:
        raise FileNotFoundError(f"no extracted netlist under {pex_dir} — run the PEX stage first")
    if len(stitched) == 1 and len(raw) == 1 and raw[0].stem + "_stitched" == stitched[0].stem:
        note = (
            f"{pex_dir} holds an RC pair; measuring the STITCHED netlist ({stitched[0].name}) — "
            "the raw one's resistor mesh is not in the circuit. Name one explicitly to override."
        )
        return MeasuredNetlist(stitched[0], "stitched", "directory", f"{disagreed} {note}".strip())
    if len(hits) > 1:
        listing = "\n  ".join(
            f"{p} [{k}] ({datetime.datetime.fromtimestamp(p.stat().st_mtime)})" for p, k in hits
        )
        raise ValueError(
            f"{len(hits)} extracted netlists under {pex_dir} (stitched: {len(stitched)}, raw: "
            f"{len(raw)}); name the one THIS scorecard measures:\n  {listing}"
        )
    p, k = hits[0]
    return MeasuredNetlist(p, k, "directory", disagreed)
