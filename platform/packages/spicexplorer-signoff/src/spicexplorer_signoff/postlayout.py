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
"""

from __future__ import annotations

import re
from pathlib import Path


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
