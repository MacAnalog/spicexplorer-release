"""Layout-sensitivity injection — the primitive behind the layout *brief*.

Before layout exists, the schematic side measures how much parasitic / mismatch each net
or device can take: perturb the certified subckt, re-run the block's benches, read the
metric deltas. This module does the perturbation as **text on the subckt**; the
measurement is a caller-supplied callable (the campaign's own harness), so this package
never depends on any bench.

    def measure(subckt_text: str) -> dict[str, float]: ...   # e.g. {"fc_hz": 249.8, ...}
    table = sweep(core_sp, "lpf_core", measure, nets=[...], c_ff=(1, 10), pairs=[("vout_1","vout_2")])

Perturbations available: :func:`inject_caps` (C net→ref, balanced pair, one-sided),
:func:`inject_resistor` (series R on a net — the net is split at every element pin
occurrence), :func:`scale_param` (multiply a device parameter, e.g. ``w`` of one member
of a matched pair; ``add`` for additive shifts), :func:`inject_vsource` (a dc source in
series with one device pin — a ΔV_T on a gate when the model wrapper hard-codes
``delvto``, as IHP's ``sg13_hv_*`` do), :func:`inject_isource` (dc current into nodes —
the leakage / ESD-diode budget primitive). Everything is inserted just before the
subckt's ``.ends`` so the block stays a valid, same-pins drop-in.

On an **extracted** block the design's device names are gone, so :func:`find_mos_cards` locates
a device class by connectivity and :func:`inject_threshold_offset` applies a ΔV_T to every card
of it with the sign convention stated once. :func:`filter_caps` and :func:`insert_series_return`
are the two what-ifs an extraction invites: which parasitic capacitance actually costs the
metric, and what the return path the extraction did not model would cost.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from .postlayout import _read, extract_subckt

Measure = Callable[[str], dict[str, float]]


def _insert_before_ends(block: str, lines: Sequence[str]) -> str:
    m = re.search(r"(?im)^\.ends\b", block)
    if not m:
        raise ValueError("subckt block has no .ends")
    return block[: m.start()] + "\n".join(lines) + "\n" + block[m.start() :]


def inject_caps(
    subckt: str | Path, name: str, caps: Iterable[tuple[str, str, float]], *, prefix: str = "cinj"
) -> str:
    """Add ``C<prefix><i> a b <val F>`` lines to subckt ``name`` (whole text returned)."""
    text = _read(subckt)
    block, _ = extract_subckt(text, name)
    lines = [f"C{prefix}{i} {a} {b} {v:.6g}" for i, (a, b, v) in enumerate(caps)]
    return text.replace(block, _insert_before_ends(block, lines), 1)


def inject_resistor(
    subckt: str | Path,
    name: str,
    net: str,
    r_ohm: float,
    *,
    at_devices: Iterable[str] | None = None,
    new_net: str | None = None,
) -> str:
    """Split ``net`` and insert a series R: every element pin on ``net`` (or only the pins of
    ``at_devices``) is moved to ``new_net`` and ``R… net new_net r_ohm`` is added."""
    text = _read(subckt)
    block, _ = extract_subckt(text, name)
    new_net = new_net or f"{net}_r"
    devs = {d.lower() for d in at_devices} if at_devices else None
    out = []
    for line in block.splitlines():
        s = line.strip()
        if s and not s.startswith((".", "*", "+")):
            toks = line.split()
            if devs is None or toks[0].lower() in devs:
                toks = [new_net if t == net else t for t in toks[1:]]
                line = " ".join([line.split()[0]] + toks)
        out.append(line)
    nb = _insert_before_ends("\n".join(out), [f"Rinj_{net} {net} {new_net} {r_ohm:.6g}"])
    return text.replace(block, nb, 1)


def scale_param(
    subckt: str | Path, name: str, device: str, param: str, factor: float = 1.0, add: float = 0.0
) -> str:
    """Multiply (and/or add to) ``param=`` on the card of ``device`` inside subckt ``name``.
    Values may carry SI suffixes (``w=4u``); the result is written in plain SI (``4.4e-06``)."""
    text = _read(subckt)
    block, _ = extract_subckt(text, name)
    si = {"f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "meg": 1e6}
    lines = block.splitlines()
    for i, line in enumerate(lines):
        toks = line.split()
        if toks and toks[0].lower() == device.lower():

            def rep(m: re.Match[str]) -> str:
                v = float(m.group(2)) * si.get((m.group(3) or "").lower(), 1.0)
                return f"{m.group(1)}{v * factor + add:.6g}"

            new = re.sub(
                rf"(?i)\b({re.escape(param)}=)([-+]?\d*\.?\d+(?:e[-+]?\d+)?)(meg|[fpnumk])?\b",
                rep,
                line,
            )
            if new == line:
                raise KeyError(f"{param}= not found on device {device}")
            lines[i] = new
            break
    else:
        raise KeyError(f"device {device} not in subckt {name}")
    return text.replace(block, "\n".join(lines), 1)


def inject_vsource(
    subckt: str | Path,
    name: str,
    device: str,
    dv: float,
    *,
    pin: int | str = "g",
    pin_order: str = "dgsb",
) -> str:
    """Put a dc source ``dv`` (V) in series with one pin of ``device``: the pin's net is
    replaced by ``<net>_<device>_v`` on that card and ``V… <new> <net> dv`` added, i.e. the
    device sees net + dv. ``pin`` is a name in ``pin_order`` (default MOS d/g/s/b) or an index."""
    text = _read(subckt)
    block, _ = extract_subckt(text, name)
    idx = pin if isinstance(pin, int) else pin_order.index(pin.lower())
    lines = block.splitlines()
    for i, line in enumerate(lines):
        toks = line.split()
        if toks and toks[0].lower() == device.lower():
            net = toks[1 + idx]
            new = f"{net}_{device}_v"
            toks[1 + idx] = new
            lines[i] = " ".join(toks)
            nb = _insert_before_ends("\n".join(lines), [f"Vinj_{device} {new} {net} dc {dv:.6g}"])
            return text.replace(block, nb, 1)
    raise KeyError(f"device {device} not in subckt {name}")


def inject_isource(
    subckt: str | Path, name: str, nets: dict[str, float], *, ref: str = "0", prefix: str = "iinj"
) -> str:
    """Add ``I<prefix>_<net> <ref> <net> dc <A>`` per entry (positive = current INTO the net)."""
    text = _read(subckt)
    block, _ = extract_subckt(text, name)
    lines = [f"I{prefix}_{n} {ref} {n} dc {v:.6g}" for n, v in nets.items()]
    return text.replace(block, _insert_before_ends(block, lines), 1)


@dataclass
class SensRow:
    kind: str  # c_gnd | c_pair | c_onesided | c_balanced | r_series | i_leak | v_pin | param
    target: str  # net, "a|b" or device.param
    unit: str  # e.g. "1fF", "10fF", "1kOhm", "x1.01"
    metrics: dict[str, float]  # measured with the perturbation
    delta: dict[str, float]  # metrics - baseline
    per_unit: dict[str, float] = field(default_factory=dict)  # delta / unit magnitude

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "target": self.target,
            "unit": self.unit,
            "metrics": self.metrics,
            "delta": self.delta,
            "per_unit": self.per_unit,
        }


def sweep(
    subckt: str | Path,
    name: str,
    measure: Measure,
    *,
    nets: Sequence[str] = (),
    pairs: Sequence[tuple[str, str]] = (),
    c_ff: Sequence[float] = (1.0, 10.0),
    ref: str = "0",
    r_nets: Sequence[tuple[str, float]] = (),
    params: Sequence[tuple[str, str, float]] = (),
    i_nets: Sequence[tuple[str, float]] = (),
    v_pins: Sequence[tuple[str, str, float]] = (),
    baseline: dict[str, float] | None = None,
) -> tuple[dict[str, float], list[SensRow]]:
    """Run the injection matrix; returns (baseline metrics, rows). Rows are per perturbation;
    ``per_unit`` normalizes by fF / kΩ / pA / mV / fractional param change so budgets can be
    derived (budget = margin_fraction × margin / per_unit).

    For each ``pairs`` entry three cases run: ``c_pair`` (between the halves), ``c_onesided``
    (one half to ``ref``) and ``c_balanced`` (both halves to ``ref`` — what a symmetric layout
    produces). ``i_nets`` = (net, A) leakage into a node; ``v_pins`` = (device, pin, V) series
    source on a device pin (ΔV_T when the model wrapper hard-codes ``delvto``)."""
    text = _read(subckt)
    base = baseline or measure(text)
    rows: list[SensRow] = []

    def add(kind: str, target: str, unit: str, mag: float, perturbed: str) -> None:
        m = measure(perturbed)
        d = {k: m[k] - base[k] for k in m if k in base}
        rows.append(SensRow(kind, target, unit, m, d, {k: v / mag for k, v in d.items()}))

    for n in nets:
        for c in c_ff:
            add("c_gnd", n, f"{c:g}fF", c, inject_caps(text, name, [(n, ref, c * 1e-15)]))
    for a, b in pairs:
        for c in c_ff:
            add("c_pair", f"{a}|{b}", f"{c:g}fF", c, inject_caps(text, name, [(a, b, c * 1e-15)]))
            add(
                "c_onesided",
                f"{a}|{b}",
                f"{c:g}fF",
                c,
                inject_caps(text, name, [(a, ref, c * 1e-15)]),
            )
            add(
                "c_balanced",
                f"{a}|{b}",
                f"{c:g}fF",
                c,
                inject_caps(text, name, [(a, ref, c * 1e-15), (b, ref, c * 1e-15)]),
            )
    for n, r in r_nets:
        add("r_series", n, f"{r / 1e3:g}kOhm", r / 1e3, inject_resistor(text, name, n, r))
    for dev, par, fac in params:
        add("param", f"{dev}.{par}", f"x{fac:g}", fac - 1.0, scale_param(text, name, dev, par, fac))
    for n, amps in i_nets:
        add("i_leak", n, f"{amps * 1e12:g}pA", amps * 1e12, inject_isource(text, name, {n: amps}))
    for dev, pin, volts in v_pins:
        add(
            "v_pin",
            f"{dev}.{pin}",
            f"{volts * 1e3:g}mV",
            volts * 1e3,
            inject_vsource(text, name, dev, volts, pin=pin),
        )
    return base, rows


# ------------------------------------------------------- working on an EXTRACTED block ----
# An extraction carries no design-device names: every MOS is `XMn_<k>`, every parasitic a
# `Cext_`/`Rext_`. What IS labelled is the nets, because a generator names them after the
# certified netlist -- so a design device is found by its connectivity, not by its name.

_C_CARD = re.compile(r"^(C\S*)\s+(\S+)\s+(\S+)\s+(\S+)\s*$")


def find_mos_cards(
    block: str | Path,
    *,
    family: str,
    drain: str,
    gate: str,
    source: str,
    prefix: str = "XM",
) -> list[str]:
    """Names of every extracted MOS card matching ``(model family, d, g, s)``.

    ``family`` is matched as a model-name SUFFIX (``"nmos"`` matches ``sg13_lv_nmos``), so the
    caller names the device class, not one PDK's model string. A design device drawn as several
    half-width cards returns several names — assert the count you expect: a class whose member
    count silently changed is a re-certification the injection did not follow.
    """
    out: list[str] = []
    for ln in _read(block).splitlines():
        t = ln.split()
        if len(t) < 6 or not t[0].upper().startswith(prefix.upper()):
            continue
        if not t[5].lower().endswith(family.lower()):
            continue
        if (t[1], t[2], t[3]) == (drain, gate, source):
            out.append(t[0])
    return out


def inject_threshold_offset(
    subckt: str | Path, name: str, cards: Sequence[str], dvt_v: float, *, pin: str = "g"
) -> str:
    """A threshold-voltage offset of ``+dvt_v`` on every card of one design device.

    :func:`inject_vsource` makes the device see ``net + dv`` on the chosen pin, so a threshold
    INCREASE of ``dvt`` is a gate source of ``-dvt``. Getting that sign backwards is a mismatch
    study that reports the safe direction as the dangerous one, so it lives here once rather
    than in each caller.
    """
    text = _read(subckt)
    for c in cards:
        text = inject_vsource(text, name, c, -dvt_v, pin=pin)
    return text


def filter_caps(
    block: str, *, keep: Iterable[str] = (), drop: Iterable[str] = (), prefix: str = "Cext"
) -> tuple[str, int, int]:
    """Delete extracted coupling/ground capacitors, for a what-if. ``(text, kept, dropped)``.

    ``keep`` keeps only the cards touching one of those nets; ``drop`` keeps everything except
    those; give neither and nothing changes. Nothing else in the block moves, so the difference
    between two runs is exactly the capacitance named — this is how "the parasitics on THIS net
    move the metric by X" is measured rather than asserted. Only cards whose name starts with
    ``prefix`` are considered, so re-inserted devices (``X`` calls) always survive.
    """
    kk, dd = {n for n in keep if n}, {n for n in drop if n}
    out, gone, left = [], 0, 0
    for ln in block.splitlines():
        m = _C_CARD.match(ln.strip())
        if m and m.group(1).lower().startswith(prefix.lower()):
            nets = {m.group(2), m.group(3)}
            hit = bool(nets & kk) if kk else not (nets & dd)
            if not hit:
                gone += 1
                continue
            left += 1
        out.append(ln)
    return "\n".join(out) + "\n", left, gone


def insert_series_return(
    block: str, net: str, ohm: float, *, kelvin: Iterable[str] = ()
) -> tuple[str, int]:
    """Put a series resistance in the block's own ``net`` return path. ``(text, cards_moved)``.

    A capacitance-only extraction carries no wire resistance at all, so every metric it produces
    is measured with an IDEAL return. This renames ``net`` to ``<net>_ret`` on every card inside
    the block except the ``.subckt`` header and the Kelvin-returned devices named in ``kelvin``
    (whose own strap reaches the pin), and adds one resistor ``<net>_ret -> <net>``. ``ohm`` is
    therefore the COMMON series element — the quantity a return-path budget is written on; the
    per-device spread beyond it is a separate, much smaller term.
    """
    keep = {k.strip().upper() for k in kelvin if k.strip()}
    ret = f"{net}_ret"
    out, touched = [], 0
    for ln in block.splitlines():
        t = ln.split()
        s = ln.lstrip()
        if t and not s.startswith("*") and not s.startswith(".") and t[0].upper() not in keep:
            if net in t[1:]:
                ln = " ".join([t[0]] + [ret if x == net else x for x in t[1:]])
                touched += 1
        out.append(ln)
    text = "\n".join(out)
    i = text.lower().rindex(".ends")
    return text[:i] + f"R{net}ret {ret} {net} {ohm:g}\n" + text[i:] + "\n", touched
