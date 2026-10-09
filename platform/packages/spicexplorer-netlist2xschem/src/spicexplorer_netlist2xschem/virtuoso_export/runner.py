"""Load emitted ``.il`` into a live Virtuoso and verify the built cellview.

This is the only module that talks to Cadence; ``virtuoso_bridge`` is imported lazily so the
rest of the package (parse → net-extract → emit) stays runnable with no bridge installed.

Verification reads the built schematic back with the bridge's ``read_schematic`` and
STRICT-diffs it against the emitter's expectation table: name-for-name binding equality
(no exemptions), full terminal *coverage* (every device terminal read back from the live
DB must be covered by an expectation — catches terminals the net extractor silently failed
to bind), and exact device-instance sets.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import Any

from .emit_il import EmitResult
from .symbols import SymbolEmitResult

__all__ = ["VerifyReport", "connect", "load_il", "verify_schematic", "verify_symbol"]

#: Our fallback copy of the bridge's CDF read filter — see ``cdf_param_filters.yaml`` and
#: ``doc/bridge_limits.md`` §8. The bridge ships the file in its source tree but not in its
#: wheel, so an installed bridge has no such file and its reader raises ``FileNotFoundError``.
FALLBACK_PARAM_FILTERS = Path(__file__).with_name("cdf_param_filters.yaml")


def _bridge():
    try:
        import virtuoso_bridge
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise RuntimeError(
            "virtuoso-bridge is not installed in this environment; "
            "install external/virtuoso-bridge-lite to use --run/--verify"
        ) from exc
    return virtuoso_bridge


def connect(*, host: str = "127.0.0.1", port: int | None = None, timeout: int = 30) -> Any:
    """A ``VirtuosoClient`` for the live CIW daemon.

    With an explicit ``port``, connect locally (no tunnel); otherwise fall back to the
    bridge's environment resolution (``VirtuosoClient.from_env``).
    """
    vb = _bridge()
    if port is not None:
        return vb.VirtuosoClient.local(host=host, port=port, timeout=timeout)
    return vb.VirtuosoClient.from_env(timeout=timeout)


_CV_OPEN = re.compile(r'dbOpenCellViewByType\(\s*"([^"]+)"\s+"([^"]+)"\s+"[^"]*"\s+"[^"]*"\s+"w"')
_AT_LINE = re.compile(r"at line (\d+)")


def _locate(path: Path, detail: str) -> str:
    """Turn ``… at line 3463`` into the source line and the cellview block it sits in.

    Virtuoso reports a ``load`` failure as a line number and nothing else — with a whole
    hierarchy in one file that names nothing at all (#236). The file is right here, so read
    the line out of it and name the cellview whose ``dbOpenCellViewByType(… "w")`` last
    opened above it.
    """
    m = _AT_LINE.search(detail)
    if m is None:
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:  # pragma: no cover - the file we just wrote
        return ""
    n = int(m.group(1))
    if not 1 <= n <= len(lines):
        return f" (line {n} is past the end of {path.name}: {len(lines)} lines)"
    where = ""
    for above in reversed(lines[:n]):
        cv = _CV_OPEN.search(above)
        if cv is not None:
            where = f" in the build of {cv.group(1)}/{cv.group(2)}"
            break
    return f" — {path.name}:{n}{where}: {lines[n - 1].strip()}"


def load_il(client: Any, path: str | Path, *, timeout: int = 120) -> None:
    """Load the ``.il`` file; raise with the SKILL error text on failure.

    The message names the file, and — when the daemon reported a line number — the line
    itself and the cellview build it belongs to.
    """
    result = client.load_il(path, timeout=timeout)
    errors = getattr(result, "errors", None)
    status = getattr(result, "status", None)
    ok = getattr(status, "value", str(status)).lower() in {"success", "ok"}
    if errors or not ok:
        detail = (
            "; ".join(errors or []) or f"status={status} output={getattr(result, 'output', '')}"
        )
        raise RuntimeError(f"xvport: load_il failed: {detail}{_locate(Path(path), detail)}")


@dataclass
class VerifyReport:
    """The result of diffing the built cellview against the emitter's expectations."""

    ok: bool
    missing_instances: list[str] = field(default_factory=list)
    extra_instances: list[str] = field(default_factory=list)
    binding_mismatches: list[str] = field(default_factory=list)
    uncovered_bindings: list[str] = field(default_factory=list)
    missing_ports: list[str] = field(default_factory=list)
    checked_bindings: int = 0

    def summary(self) -> str:
        if self.ok:
            return f"verify OK: {self.checked_bindings} terminal bindings match"
        parts = []
        if self.missing_instances:
            parts.append(f"missing instances: {', '.join(self.missing_instances)}")
        if self.extra_instances:
            parts.append(f"extra instances: {', '.join(self.extra_instances)}")
        if self.binding_mismatches:
            parts.append("binding mismatches: " + "; ".join(self.binding_mismatches))
        if self.uncovered_bindings:
            parts.append("uncovered terminals: " + "; ".join(self.uncovered_bindings))
        if self.missing_ports:
            parts.append(f"missing ports: {', '.join(self.missing_ports)}")
        return "verify FAILED — " + " | ".join(parts)


_PIN_MASTERS = {"ipin", "opin", "iopin"}


def _filters_path(bridge_yaml: Path, fallback: Path = FALLBACK_PARAM_FILTERS) -> Path | None:
    """The CDF read filter to hand ``read_schematic``: the bridge's own when it is installed,
    ours when it is not, ``None`` (= no filtering) when neither file exists.

    Pure and path-only so it is testable with no bridge and no daemon.
    """
    if bridge_yaml.is_file():
        return bridge_yaml
    if fallback.is_file():
        return fallback
    return None


def _bridge_reader() -> Any:
    """``read_schematic`` bound to a filter file that actually exists (see ``_filters_path``)."""
    from virtuoso_bridge.virtuoso.schematic import reader as bridge_reader

    chosen = _filters_path(Path(bridge_reader.__file__).with_name("cdf_param_filters.yaml"))
    return partial(bridge_reader.read_schematic, param_filters=chosen)


def verify_schematic(
    client: Any, lib: str, cell: str, expected: EmitResult, *, reader: Any = None
) -> VerifyReport:
    """Read ``lib/cell`` back and STRICT-diff it against ``expected``:

    * every expected ``(instance, terminal)`` binding must equal the readback net name —
      no exemptions (a port-name exemption here used to be able to mask a mis-bind onto
      a port's net);
    * coverage: every terminal of every *device* instance read back must be covered by an
      expectation (interface-pin instances are the ``basic`` lib and are skipped);
    * the device instance sets match exactly; every expected interface pin exists.

    ``reader`` defaults to the bridge's ``read_schematic`` — bound to a CDF filter file that
    exists on this install (the bridge's own when packaged, ours otherwise: the bridge's wheel
    omits it, and the reader's default path then raises ``FileNotFoundError`` after a correct
    port, see ``doc/bridge_limits.md`` §8). Tests inject an offline fake.
    """
    if reader is None:
        reader = _bridge_reader()
    data = reader(client, lib, cell, include_positions=False)
    report = VerifyReport(ok=True)

    insts = {i["name"]: i for i in data.get("instances", [])}
    device_insts = {
        name: idata
        for name, idata in insts.items()
        if idata.get("cell") not in _PIN_MASTERS and idata.get("lib") != "basic"
    }
    for name in expected.instances:
        if name not in device_insts:
            report.missing_instances.append(name)
    report.extra_instances = sorted(set(device_insts) - set(expected.instances))

    for (inst, term), net in sorted(expected.expected_bindings.items()):
        actual = (insts.get(inst, {}).get("terms") or {}).get(term)
        report.checked_bindings += 1
        if actual is None:
            report.binding_mismatches.append(f"{inst}.{term}: no binding read back")
        elif actual != net:
            report.binding_mismatches.append(f"{inst}.{term}: expected {net!r} got {actual!r}")

    for name, idata in sorted(device_insts.items()):
        for term, actual in sorted((idata.get("terms") or {}).items()):
            if (name, term) not in expected.expected_bindings:
                report.uncovered_bindings.append(f"{name}.{term} -> {actual!r} (no expectation)")

    pins = set(data.get("pins") or {})  # read_schematic returns a dict keyed by pin name
    for pin in expected.expected_ports:
        if pin not in pins:
            report.missing_ports.append(pin)

    report.ok = not (
        report.missing_instances
        or report.extra_instances
        or report.binding_mismatches
        or report.uncovered_bindings
        or report.missing_ports
    )
    return report


def verify_symbol(client: Any, lib: str, cell: str, expected: SymbolEmitResult) -> VerifyReport:
    """Read the symbol view back and compare terminal names + directions."""
    from virtuoso_bridge.virtuoso.symbol.reader import read_symbol_ports

    data = read_symbol_ports(client, lib, cell)
    report = VerifyReport(ok=True)
    actual = {t["name"]: t["direction"] for t in data.get("terms", [])}
    for name, direction in expected.terms.items():
        report.checked_bindings += 1
        if name not in actual:
            report.binding_mismatches.append(f"terminal {name}: missing")
        elif actual[name] != direction:
            report.binding_mismatches.append(
                f"terminal {name}: expected {direction!r} got {actual[name]!r}"
            )
    extra = set(actual) - set(expected.terms)
    if extra:
        report.binding_mismatches.append(f"unexpected terminals: {sorted(extra)}")
    report.ok = not report.binding_mismatches
    return report
