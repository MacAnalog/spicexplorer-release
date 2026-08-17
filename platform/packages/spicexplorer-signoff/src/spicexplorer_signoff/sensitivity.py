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
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Sequence

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
