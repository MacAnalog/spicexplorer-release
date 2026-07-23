"""End-to-end checks for a ported schematic cellview (``--netcheck`` / ``--simcheck``).

Both are *independent oracles* — neither reuses xvport's own net extractor:

* **netcheck** — "the port IS the same circuit": netlist the SOURCE ``.sch`` with headless
  xschem (SPICE dialect) and the BUILT cellview through Virtuoso's own netlister (spectre
  dialect, via the bridge's ``export_schematic_netlist``), then compare the two with
  spicexplorer-circuitgraph's labeled bipartite-graph isomorphism (device type + MOS
  polarity + pin-level wiring; instance/net names and sizing ignored, supply rails
  anchored). Both netlisters are third parties to the emitter under test.
* **simcheck** — "the port SIMULATES in the target PDK": wrap the same exported cellview
  netlist in a minimal smoke deck — the operator-supplied model include plus every
  interface net tied to ground through a large resistor, so the topology check passes on a
  bare (source-less) subcircuit — and run it through Spectre via the bridge. Proves the
  netlist parses, every device binds to a kit model with its CDF-derived parameters, and
  the DC operating point solves. Model file/section are never committed: they come from
  ``--sim-models``/``--sim-section`` or ``XVPORT_SIM_MODELS``/``XVPORT_SIM_SECTION``.

A check that *cannot run* (missing xschem, bridge, circuitgraph, or model config) reports
``SKIPPED`` with the reason and does not fail the port; a check that runs and finds a
difference fails loudly.

Cross-package note: importing ``spicexplorer_circuitgraph`` here is a DELIBERATE
exception to the "peer leaf tools never import each other" rule — lazy and
optional (the ``[e2e]`` extra), mirroring the lazy ``virtuoso_bridge`` pattern; the port
pipeline itself never needs it.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "CheckReport",
    "CheckUnavailable",
    "compose_smoke_deck",
    "extract_design_section",
    "fetch_cellview_netlist",
    "netcheck",
    "netlists_graph_equivalent",
    "simcheck",
    "xschem_source_netlist",
]

_TIE_RESISTANCE = "1G"


class CheckUnavailable(RuntimeError):
    """A check cannot run in this environment — reported as SKIPPED, never as a failure."""


@dataclass
class CheckReport:
    """Outcome of one end-to-end check."""

    name: str
    ok: bool
    skipped: str | None = None
    detail: str = ""

    def summary(self) -> str:
        if self.skipped:
            return f"{self.name} SKIPPED — {self.skipped}"
        state = "OK" if self.ok else "FAILED"
        return f"{self.name} {state}" + (f": {self.detail}" if self.detail else "")


# --- source side: headless xschem netlist -------------------------------------------


def xschem_source_netlist(source: Path, out_dir: Path, *, timeout: int = 120) -> Path:
    """Netlist ``source`` with headless xschem (``-n``) into ``out_dir``; return the file.

    Symbol resolution mirrors :func:`..render.render`: an rcfile seeding the Tcl
    ``XSCHEM_LIBRARY_PATH`` with the source's own directory first, then the vendored
    default search paths.
    """
    if shutil.which("xschem") is None:
        raise CheckUnavailable("xschem is not on PATH")
    from ..render import write_xschemrc
    from ..sym_library import default_search_paths

    source = Path(source).resolve()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # grandparent too: corpus drawings reference sibling projects relative to the
    # drawings root (`ccia-02-…/transmission_gate_pair.sym`) — same roots as symlib
    entries: list[str] = [str(source.parent), str(source.parent.parent)]
    for root in default_search_paths():
        entries.append(str(root))
        # bare symrefs (`ipin.sym`, corpus-common) resolve only against the generic
        # devices dir itself, not its parent — mirror the container's two-entry layout
        devices = root / "devices"
        if devices.is_dir():
            entries.append(str(devices))
    library_path = os.pathsep.join(dict.fromkeys(entries))  # de-dup, order-preserving
    rc = write_xschemrc(out_dir, library_path)
    env = os.environ.copy()
    env["XSCHEM_LIBRARY_PATH"] = library_path
    cmd = [
        "xschem", "--rcfile", str(rc), "-n", "-q", "-x",
        "-o", str(out_dir), str(source),
    ]
    try:
        proc = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=timeout, cwd=str(out_dir)
        )
        log = (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        raise CheckUnavailable(f"xschem -n timed out after {timeout}s") from None
    netlist = out_dir / f"{source.stem}.spice"
    if not netlist.is_file():
        raise CheckUnavailable(f"xschem -n produced no netlist: {log.strip()[:400]}")
    return netlist


# --- built side: Virtuoso's own netlister (via the bridge) ---------------------------


def fetch_cellview_netlist(
    client: Any, lib: str, cell: str, out_dir: Path, *, timeout: int = 180
) -> Path:
    """Netlist ``lib/cell`` with Virtuoso's netlister and download the package locally.

    Wraps the bridge's ``export_schematic_netlist`` (OCEAN ``simulator → design →
    createNetlist``); returns the local simulator input file.
    """
    try:
        from virtuoso_bridge.virtuoso.schematic.netlist import export_schematic_netlist
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise CheckUnavailable("virtuoso-bridge is not installed") from exc
    result = export_schematic_netlist(client, lib, cell, out_dir, timeout=timeout)
    return Path(result["input_file"])


# --- netcheck: graph equivalence ------------------------------------------------------


def _comparison_pdk() -> Any:
    """A merged device table typing BOTH sides (IHP source models + FOUNDRYN65 kit cells)."""
    from spicexplorer_circuitgraph import pdk as cg_pdk

    return cg_pdk.Pdk(
        name="xvport-compare",
        devices=tuple(cg_pdk.IHP_SG13G2.devices) + tuple(cg_pdk.FOUNDRY_N65.devices),
    )


def _sanitize_subckt_names(netlist_text: str) -> str:
    """Rename every ``.subckt`` definition (and its references) to its Virtuoso-legal form.

    xschem cell names may carry hyphens (``chopper-diff``); the port sanitizes them into
    the cellview name (``chopper_diff``), so the source netlist must be renamed the same
    way before the graphs are compared — a subckt instance's definition name is part of
    its component identity.
    """
    import re as _re

    from .emit_il import _sanitize

    names = set(_re.findall(r"^\s*\.subckt\s+(\S+)", netlist_text, _re.MULTILINE | _re.I))
    for name in names:
        clean = _sanitize(name, prefix="cell")
        if clean != name:
            netlist_text = _re.sub(
                rf"(?<![\w-]){_re.escape(name)}(?![\w-])", clean, netlist_text
            )
    return netlist_text


def netlists_graph_equivalent(source_netlist: Path, cellview_netlist: Path) -> Any:
    """circuitgraph comparison of a SPICE source netlist vs a spectre cellview netlist.

    Returns the ``GraphComparison`` (truthy iff equivalent; ``.reason`` explains).
    """
    try:
        from spicexplorer_circuitgraph import compare_netlists
    except ImportError as exc:
        raise CheckUnavailable(
            "spicexplorer-circuitgraph is not installed (the [e2e] extra)"
        ) from exc
    from spicexplorer_core.spice_engine import NetlistView

    # side A: xschem output (SPICE dialect) — raw text, so the subckt renames apply;
    # compare_netlists coerces a multi-line str into a graph itself
    a = _sanitize_subckt_names(Path(source_netlist).read_text(encoding="utf-8"))
    b = NetlistView.from_file(cellview_netlist, dialect="spectre")
    return compare_netlists(a, b, pdk=_comparison_pdk(), on_unknown="skip")


def netcheck(
    client: Any, lib: str, cell: str, source: Path, work_dir: Path, *, timeout: int = 180
) -> CheckReport:
    """The netlist + graph-equivalence oracle for one built schematic cellview."""
    try:
        src_netlist = xschem_source_netlist(source, Path(work_dir) / "source")
        cv_netlist = fetch_cellview_netlist(
            client, lib, cell, Path(work_dir) / "cellview", timeout=timeout
        )
        comparison = netlists_graph_equivalent(src_netlist, cv_netlist)
    except CheckUnavailable as exc:
        return CheckReport("netcheck", True, skipped=str(exc))
    return CheckReport("netcheck", bool(comparison), detail=comparison.reason)


# --- simcheck: it simulates in the target PDK ----------------------------------------


def extract_design_section(netlist_text: str) -> str:
    """The DESIGN SECTION of a Virtuoso ``createNetlist`` export — instances/subckts only.

    ``createNetlist`` bakes the ADE session's model setup into the header as absolute
    kit-path ``include`` lines (foundry NDA data — never repeat, embed, or commit those)
    and appends simulator/option/info statements after the design. This keeps everything
    from the first ``// Library name:`` block up to ``simulatorOptions``; the smoke deck
    then supplies its OWN operator-configured model include. Falls back to
    "every line that is not an include/lang/options/info statement" when the markers are
    absent (a foreign netlist format).
    """
    lines = netlist_text.splitlines()
    starts = [i for i, ln in enumerate(lines) if ln.startswith("// Library name:")]
    if starts:
        body = lines[starts[0]:]
        for j, ln in enumerate(body):
            if ln.startswith(("simulatorOptions", "saveOptions")):
                body = body[:j]
                break
        return "\n".join(body).rstrip() + "\n"
    kept = [
        ln
        for ln in lines
        if not ln.lstrip().startswith(
            ("include", "simulator lang", "simulatorOptions", "saveOptions", "global ")
        )
        and " info what=" not in ln
    ]
    return "\n".join(kept).rstrip() + "\n"


def compose_smoke_deck(
    netlist_file: Path,
    ports: Iterable[str],
    models: str,
    section: str | None,
    out_file: Path,
    params: dict[str, str] | None = None,
) -> Path:
    """A minimal spectre deck around an exported cellview netlist: models + a DC op.

    Only the netlist's *design section* is embedded (see :func:`extract_design_section` —
    the export's own kit include lines are dropped; the operator's ``models`` include is
    the single model source). Every interface net is tied to ground through ``1G`` so the
    (source-less) subcircuit passes the topology check and the operating point solves —
    the goal is *does every device bind to a kit model and evaluate*, not a meaningful
    bias point.
    """
    design = extract_design_section(Path(netlist_file).read_text(encoding="utf-8"))
    lines = [
        "// xvport simcheck smoke deck (generated — do not commit; model path is operator-local)",
        "simulator lang=spectre",
        "global 0",
        f'include "{models}"' + (f" section={section}" if section else ""),
    ]
    if params:
        # values for the drawing's symbolic placeholders (--sim-param name=val)
        lines.append("parameters " + " ".join(f"{k}={v}" for k, v in sorted(params.items())))
    lines.append(design.rstrip())
    for i, net in enumerate(sorted(set(ports))):
        lines.append(f"xvtie{i} ({net} 0) resistor r={_TIE_RESISTANCE}")
    lines.append("xvportOp dc")
    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_file


def simcheck(
    client: Any,
    lib: str,
    cell: str,
    ports: Iterable[str],
    work_dir: Path,
    *,
    models: str | None,
    section: str | None,
    env_file: str | Path | None = None,
    params: dict[str, str] | None = None,
    netlist_file: Path | None = None,
    timeout: int = 600,
) -> CheckReport:
    """Run the smoke deck for ``lib/cell`` through Spectre.

    ``env_file`` is the reliable local-vs-remote profile pin: the bridge's
    ``from_env`` discovers a ``.env`` and may silently
    flip a local-mode run to SSH; registering an explicit file wins over discovery.
    """
    try:
        if not models:
            raise CheckUnavailable(
                "no model file configured (--sim-models / XVPORT_SIM_MODELS)"
            )
        if netlist_file is None or not Path(netlist_file).is_file():
            netlist_file = fetch_cellview_netlist(
                client, lib, cell, Path(work_dir) / "cellview"
            )
        try:
            from virtuoso_bridge import SpectreSimulator
            from virtuoso_bridge.env import set_runtime_env_file
        except ImportError as exc:  # pragma: no cover - environment-specific
            raise CheckUnavailable("virtuoso-bridge is not installed") from exc
        deck = compose_smoke_deck(
            netlist_file,
            ports,
            models,
            section,
            Path(work_dir) / f"{cell}_smoke.spectre",
            params=params,
        )
        if env_file is not None:
            set_runtime_env_file(env_file)
        sim = SpectreSimulator.from_env(work_dir=Path(work_dir) / "sim", timeout=timeout)
    except CheckUnavailable as exc:
        return CheckReport("simcheck", True, skipped=str(exc))
    result = sim.run_simulation(deck, {})
    status = getattr(result, "status", None)
    ok = getattr(status, "value", str(status)).lower() in {"success", "ok"}
    if ok:
        detail = "spectre dc operating point solved"
    else:
        errors = "; ".join(getattr(result, "errors", None) or [])
        detail = (errors or f"spectre failed (status={status})")[:400]
    return CheckReport("simcheck", ok, detail=detail)
