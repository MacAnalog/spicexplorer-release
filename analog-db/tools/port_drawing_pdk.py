#!/usr/bin/env python
"""Port an xschem drawing family from one PDK to another (schematic-level retarget).

Copies ``drawings/<family>/<src>/`` → ``drawings/<family>/<dst>/`` and rewrites every
PDK-specific component through a map declared in **``drawings/pdk-port-map.yaml``** (that
file documents the schema; adding a PDK pair is a YAML edit, not a code change):

* **device symbols** — ``symbols/nfet_06v0.sym`` → ``sg13g2_pr/sg13_hv_nmos.sym``, by
  flavour (gf180's voltage classes → IHP's lv/hv; the same slot where an lvt→lvt /
  hvt→hvt rule lives for a PDK pair that names flavours that way);
* **instance parameters** — key rename (``L``→``l``, ``W``→``w``, ``nf``→``ng``), drop of
  source-only keys (gf180's ``ad/as/pd/ps/nrd/nrs/sa/sb/sd`` are BSIM4-diffusion knobs the
  IHP PSP subckt computes itself), injection of target-required keys (``body``, ``b``), and
  a clamp of ``l``/``w`` to the target device's minimums;
* **model-library cards** — the ``.lib $::180MCU_MODELS/...`` lines inside testbench text;
* **intra-family symbol references** — ``<family>/gf180/foo.sym`` → ``<family>/ihp130/foo.sym``.

What this does NOT do (deliberately — these are design decisions, not translations):

* **re-size anything.** Geometry is carried over verbatim (only clamped up to the target's
  minimum). A gf180 0.7µ/0.3µ device is *legal* in IHP hv but is a different transistor;
  the ported drawing is a starting point for re-sizing, not a working circuit.
* **re-bias anything.** IHP hv tops out at 3.3 V vs gf180 06v0's 6 V, so supplies/refs above
  the target rail are REPORTED as warnings and left alone.
* **port ``simulation/*.spice``.** Those are exports of the source-PDK netlist; they are
  skipped and must be re-exported from xschem after the port.

Usage (from the analog-db root)::

    python tools/port_drawing_pdk.py drawings/ldo-005-ti-ldo-buffer-ref/gf180 --to ihp130
    python tools/port_drawing_pdk.py <src_dir> --to ihp130 --dry-run   # report only
    python tools/port_drawing_pdk.py <src_dir> --to ihp130 --force     # overwrite dest
    python tools/port_drawing_pdk.py <src_dir> --to ihp130 --map other-map.yaml

The map file is found by walking up from the source directory for ``pdk-port-map.yaml``
(so the one at the top of ``drawings/`` serves every family under it).

The footprint check (on whenever the PDKs are found under ``$PDK_ROOT``) verifies that each
mapped symbol pair has identical pin geometry, i.e. that the swap is drop-in and the existing
wires still land on the pins. A mismatch is reported per instance — the gf180 ``ppolyf_u_*``
resistors carry a third *bulk* pin that IHP's 2-pin ``r*`` symbols express as a ``body=``
parameter instead, so any wire on that pin is left dangling by the swap.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MAP_FILENAME = "pdk-port-map.yaml"


# ---------------------------------------------------------------------------- maps


@dataclass
class DeviceMap:
    """One source symbol → one target symbol, with the target's geometry floor."""

    sym: str  # target symbol path as xschem resolves it, e.g. "sg13g2_pr/sg13_hv_nmos.sym"
    model: str  # target `model=` value
    min_l: float = 0.0  # metres; the target device's minimum drawn length
    min_w: float = 0.0  # metres; total width (all fingers)
    sheet_res: float | None = None  # Ω/□ target — resistance-preserving `l` rescale
    src_sheet_res: float | None = None  # Ω/□ source; both needed or the rescale is skipped
    inject: dict[str, str] = field(default_factory=dict)  # attrs the target needs, source lacks


@dataclass
class PdkMap:
    src: str  # source PDK subdirectory name inside a family, e.g. "gf180"
    dst: str
    src_pdk: str
    dst_pdk: str
    src_symdir: str  # under $PDK_ROOT, for the footprint check
    dst_symdir: str
    devices: dict[str, DeviceMap]  # source symbol ref → target
    rename: dict[str, str] = field(default_factory=dict)  # attr key rename
    drop: tuple[str, ...] = ()  # attr keys to delete
    text_subs: tuple[tuple[str, str], ...] = ()  # (regex, replacement) over raw file text
    max_supply: float | None = None  # V; rails above this get a warning


def find_map_file(start: Path) -> Path | None:
    """Walk up from `start` for the map file — the one in drawings/ serves every family."""
    for d in [start, *start.parents]:
        if (d / MAP_FILENAME).is_file():
            return d / MAP_FILENAME
    return None


def _geom(spec: dict, key: str) -> float:
    """Geometry from YAML: '0.45u' or a plain number in metres."""
    raw = spec.get(key, 0)
    if isinstance(raw, (int, float)):
        return float(raw)
    v = parse_eng(str(raw))
    if v is None:
        raise ValueError(f"{key}={raw!r} is not a length")
    return v


def load_maps(path: Path) -> dict[tuple[str, str], PdkMap]:
    """Parse the YAML map file into {(src_dir, dst_dir): PdkMap}, failing loudly on typos."""
    doc = yaml.safe_load(path.read_text()) or {}
    out: dict[tuple[str, str], PdkMap] = {}
    for i, entry in enumerate(doc.get("maps") or []):
        try:
            devices = {}
            for sym, spec in (entry["devices"] or {}).items():
                devices[sym] = DeviceMap(
                    sym=spec["sym"],
                    model=spec["model"],
                    min_l=_geom(spec, "min_l"),
                    min_w=_geom(spec, "min_w"),
                    sheet_res=spec.get("sheet_res"),
                    src_sheet_res=spec.get("src_sheet_res"),
                    inject={k: str(v) for k, v in (spec.get("inject") or {}).items()},
                )
            pm = PdkMap(
                src=entry["src"],
                dst=entry["dst"],
                src_pdk=entry.get("src_pdk", entry["src"]),
                dst_pdk=entry.get("dst_pdk", entry["dst"]),
                src_symdir=entry.get("src_symdir", ""),
                dst_symdir=entry.get("dst_symdir", ""),
                devices=devices,
                rename=dict(entry.get("rename") or {}),
                drop=tuple(entry.get("drop") or ()),
                text_subs=tuple((s["pattern"], s["repl"]) for s in (entry.get("text_subs") or [])),
                max_supply=entry.get("max_supply"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise SystemExit(f"error: {path}: maps[{i}] is malformed ({exc})") from exc
        out[(pm.src, pm.dst)] = pm
    return out


# ------------------------------------------------------------------- xschem parsing

_SUFFIX = {"f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "meg": 1e6, "g": 1e9}
_NUM = re.compile(r"^\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*(meg|[fpnumkgKM]?)\s*$")


def parse_eng(s: str) -> float | None:
    """'0.70u' | '1e-6' → metres. None when the value is an expression we must not touch."""
    m = _NUM.match(s)
    if not m:
        return None
    num, suf = m.group(1), m.group(2)
    if not suf:
        return float(num)
    return float(num) * _SUFFIX.get(suf.lower() if suf != "M" else "meg", 1.0)


def fmt_eng(v: float) -> str:
    """Metres → the micron form the drawings use ('0.45u')."""
    return f"{v * 1e6:g}u"


def read_braced(text: str, i: int) -> tuple[str, int]:
    """`text[i]` is '{'. Return (inner, index just past the matching '}'), honouring \\{ \\}."""
    assert text[i] == "{"
    depth, j = 0, i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1 : j], j + 1
        j += 1
    raise ValueError(f"unbalanced braces starting at offset {i}")


def parse_attrs(s: str) -> list[tuple[str, str]]:
    """'name=M1\\nl=0.7u\\nad="\\'expr\\'"' → ordered [(key, value)] with quoting preserved."""
    out: list[tuple[str, str]] = []
    i, n = 0, len(s)
    while i < n:
        while i < n and s[i] in " \t\r\n":
            i += 1
        if i >= n:
            break
        k0 = i
        while i < n and s[i] not in "= \t\r\n":
            i += 1
        key = s[k0:i]
        if i < n and s[i] == "=":
            i += 1
            if i < n and s[i] == '"':  # quoted: run to the closing quote, newlines included
                v0 = i
                i += 1
                while i < n and s[i] != '"':
                    i += 2 if s[i] == "\\" else 1
                i = min(i + 1, n)
                val = s[v0:i]
            else:
                v0 = i
                while i < n and s[i] not in " \t\r\n":
                    i += 1
                val = s[v0:i]
        else:
            val = ""
        out.append((key, val))
    return out


def format_attrs(pairs: list[tuple[str, str]]) -> str:
    """xschem's own layout: 'name=X' first line, one attr per line, trailing newline."""
    return "\n".join(f"{k}={v}" if v != "" else k for k, v in pairs) + "\n"


def iter_components(text: str):
    """Yield (start, end, symref, middle, attrs) for every `C {sym} x y r f {attrs}` card."""
    for m in re.finditer(r"^C\s*\{", text, re.M):
        start = m.start()
        sym, i = read_braced(text, m.end() - 1)
        j = text.find("{", i)
        if j < 0:
            continue
        middle = text[i:j]
        if "\n" in middle.strip():  # not this card's attr block
            continue
        attrs, end = read_braced(text, j)
        yield start, end, sym, middle, attrs


def pin_signature(sym_path: Path) -> list[tuple[str, str, str]] | None:
    """(name, x, y) per pin box, for the drop-in footprint check. None if unreadable."""
    try:
        text = sym_path.read_text(errors="replace")
    except OSError:
        return None
    pins = []
    for m in re.finditer(r"^B\s+5\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\{([^}]*)\}", text, re.M):
        x0, y0, x1, y1, attrs = m.groups()
        name = dict(parse_attrs(attrs)).get("name", "?")
        cx = (float(x0) + float(x1)) / 2
        cy = (float(y0) + float(y1)) / 2
        pins.append((name, f"{cx:g}", f"{cy:g}"))
    return pins


# ------------------------------------------------------------------------- porting


class Report:
    def __init__(self) -> None:
        self.swaps: list[str] = []
        self.clamps: list[str] = []
        self.warnings: list[str] = []
        self.skipped: list[str] = []


def port_instance(
    attrs: str, dev: DeviceMap, pm: PdkMap, where: str, rep: Report, keep_resistance: bool
) -> str:
    pairs = parse_attrs(attrs)
    name = dict(pairs).get("name", "?")
    out: list[tuple[str, str]] = []

    for key, val in pairs:
        if key in pm.drop:
            continue
        if key == "model":
            out.append(("model", dev.model))
            continue
        out.append((pm.rename.get(key, key), val))

    d = dict(out)
    # Resistors: preserve R = Rsheet * l / w by rescaling l for the target's sheet resistance.
    if keep_resistance and dev.sheet_res and dev.src_sheet_res:
        lv = parse_eng(d.get("l", ""))
        if lv is not None and dev.src_sheet_res != dev.sheet_res:
            scaled = lv * dev.src_sheet_res / dev.sheet_res
            out = [(k, fmt_eng(scaled) if k == "l" else v) for k, v in out]
            rep.swaps.append(
                f"    {where}:{name}  l {d['l']} → {fmt_eng(scaled)} "
                f"(R held: {dev.src_sheet_res:g} → {dev.sheet_res:g} Ω/□)"
            )
            d = dict(out)

    # Clamp geometry up to the target device's floor (never silently — every clamp is reported).
    for key, floor in (("l", dev.min_l), ("w", dev.min_w)):
        if key not in d or floor <= 0:
            continue
        v = parse_eng(d[key])
        if v is None:
            rep.warnings.append(f"    {where}:{name}  {key}={d[key]} is an expression — left as-is, check by hand")
        elif v < floor:
            out = [(k, fmt_eng(floor) if k == key else val) for k, val in out]
            rep.clamps.append(f"    {where}:{name}  {key} {d[key]} → {fmt_eng(floor)} ({dev.model} minimum)")
    d = dict(out)

    for key, val in dev.inject.items():
        if key not in d:
            out.append((key, val))
    if "spiceprefix" not in d:
        out.append(("spiceprefix", "X"))

    return format_attrs(out)


def port_text(
    text: str, pm: PdkMap, family: str, src_dir: str, dst_dir: str, where: str, rep: Report,
    pdk_root: Path | None, keep_resistance: bool,
) -> str:
    out, cursor = [], 0
    for start, end, sym, middle, attrs in iter_components(text):
        dev = pm.devices.get(sym)
        if dev is None:
            continue
        name = dict(parse_attrs(attrs)).get("name", "?")
        if pdk_root is not None and pm.src_symdir and pm.dst_symdir:
            _check_footprint(sym, dev, pm, pdk_root, f"{where}:{name}", rep)
        new_attrs = port_instance(attrs, dev, pm, where, rep, keep_resistance)
        out.append(text[cursor:start])
        out.append(f"C {{{dev.sym}}}{middle}{{{new_attrs}}}")
        cursor = end
        rep.swaps.append(f"    {where}:{name}  {sym} → {dev.sym}")
    out.append(text[cursor:])
    ported = "".join(out)

    for pattern, repl in pm.text_subs:
        ported = re.sub(pattern, repl, ported, flags=re.M)
    ported = ported.replace(f"{family}/{src_dir}/", f"{family}/{dst_dir}/")

    _check_rails(ported, pm, where, rep)
    return ported


_FOOTPRINT_CACHE: dict[tuple[str, str], str] = {}


def _check_footprint(sym: str, dev: DeviceMap, pm: PdkMap, pdk_root: Path, where: str, rep: Report) -> None:
    key = (sym, dev.sym)
    if key in _FOOTPRINT_CACHE:
        msg = _FOOTPRINT_CACHE[key]
    else:
        a = pin_signature(pdk_root / pm.src_symdir / sym)
        b = pin_signature(pdk_root / pm.dst_symdir / dev.sym)
        if a is None or b is None:
            msg = f"footprint UNVERIFIED ({sym} → {dev.sym}): symbol not found under $PDK_ROOT"
        elif a == b:
            msg = ""
        else:
            only_src = [p for p in a if p not in b]
            only_dst = [p for p in b if p not in a]
            msg = (
                f"footprint MISMATCH {sym} → {dev.sym}: "
                f"source-only pins {[p[0] for p in only_src]}, target-only {[p[0] for p in only_dst]} "
                f"— wires on the dropped pin(s) are left dangling; fix by hand"
            )
        _FOOTPRINT_CACHE[key] = msg
    if msg:
        rep.warnings.append(f"    {where}  {msg}")


def _check_rails(text: str, pm: PdkMap, where: str, rep: Report) -> None:
    """Report supplies above the target's rail — a retarget can't re-bias a circuit for you."""
    if pm.max_supply is None:
        return
    for _s, _e, sym, _m, attrs in iter_components(text):
        if "vsource" not in sym:
            continue
        d = dict(parse_attrs(attrs))
        m = re.search(r"(?:dc\s+)?([\d.]+(?:[eE][+-]?\d+)?)", d.get("value", ""))
        if m and float(m.group(1)) > pm.max_supply:
            rep.warnings.append(
                f"    {where}:{d.get('name', '?')}  supply {m.group(1)} V > {pm.dst_pdk} rail "
                f"{pm.max_supply} V — re-bias needed"
            )


# ---------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path, help="source PDK dir, e.g. drawings/ldo-005-.../gf180")
    ap.add_argument("--to", required=True, help="target PDK dir name, e.g. ihp130")
    ap.add_argument("--dry-run", action="store_true", help="report only; write nothing")
    ap.add_argument("--force", action="store_true", help="overwrite a non-empty destination")
    ap.add_argument("--no-keep-resistance", action="store_true", help="carry resistor l/w over verbatim")
    ap.add_argument("--pdk-root", type=Path, default=os.environ.get("PDK_ROOT"), help="for the footprint check")
    ap.add_argument("--map", type=Path, help=f"map file (default: nearest {MAP_FILENAME} above <src>)")
    args = ap.parse_args()

    src = (args.src if args.src.is_absolute() else ROOT / args.src).resolve()
    if not src.is_dir():
        print(f"error: {src} is not a directory", file=sys.stderr)
        return 2
    src_dir, family_dir = src.name, src.parent

    map_file = args.map or find_map_file(src)
    if map_file is None:
        print(f"error: no {MAP_FILENAME} found at or above {src}", file=sys.stderr)
        return 2
    maps = load_maps(Path(map_file))
    key = (src_dir, args.to)
    if key not in maps:
        have = ", ".join(f"{a}→{b}" for a, b in sorted(maps)) or "(none)"
        print(f"error: {map_file} has no map for {src_dir} → {args.to}; it defines: {have}", file=sys.stderr)
        return 2
    pm = maps[key]
    dst = family_dir / args.to
    if dst.exists() and any(dst.iterdir()) and not (args.force or args.dry_run):
        print(f"error: {dst} is not empty (use --force)", file=sys.stderr)
        return 2

    pdk_root = Path(args.pdk_root) if args.pdk_root else None
    if pdk_root and not pdk_root.is_dir():
        print(f"note: $PDK_ROOT {pdk_root} not found — footprint check disabled")
        pdk_root = None

    rep = Report()
    print(f"port {family_dir.name}/{src_dir} → {family_dir.name}/{args.to}  "
          f"({pm.src_pdk} → {pm.dst_pdk}){'  [dry-run]' if args.dry_run else ''}")
    print(f"map: {map_file}\n")

    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        if "simulation" in rel.parts:  # source-PDK netlist exports — re-export after the port
            rep.skipped.append(f"    {rel}  (netlist export — re-export from xschem)")
            continue
        out_path = dst / rel
        if path.suffix in (".sch", ".sym"):
            ported = port_text(
                path.read_text(), pm, family_dir.name, src_dir, args.to, str(rel), rep,
                pdk_root, not args.no_keep_resistance,
            )
            if not args.dry_run:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(ported)
        elif not args.dry_run:  # pictures/, notes, … copied verbatim
            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, out_path)

    for title, rows in (
        ("swapped", rep.swaps), ("clamped to target minimums", rep.clamps),
        ("WARNINGS — need a human", rep.warnings), ("skipped", rep.skipped),
    ):
        if rows:
            print(f"  {title} ({len(rows)}):")
            print("\n".join(rows))
            print()

    print("next: open the ported drawings in xschem, re-size for the target device, "
          "re-bias to the target rail, then re-export simulation/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
