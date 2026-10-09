"""End-to-end checks for a ported schematic cellview (``--netcheck`` / ``--simcheck``).

Both are *independent oracles* — neither reuses xvport's own net extractor:

* **netcheck** — "the port IS the same circuit": netlist the SOURCE ``.sch`` with headless
  xschem (SPICE dialect) and the BUILT cellview through Virtuoso's own netlister (spectre
  dialect, via the bridge's ``export_schematic_netlist``), then compare the two with
  spicexplorer-circuitgraph's labeled bipartite-graph isomorphism (device type + MOS
  polarity + pin-level wiring; instance/net names and sizing ignored, supply rails
  anchored). Both netlisters are third parties to the emitter under test. ``strict``
  (``--strict-netcheck``) adds the MODEL NAME to each device's label and compares
  ``w``/``l``/``m``/``nf`` by name and eng-normalized — what a SAME-KIT port needs, and what
  a cross-kit topology port must not ask for, since there the master and its sizing semantics
  change on purpose. Those per-device comparisons pair the two sides **by instance name**
  first (:func:`pair_components`), falling back to the recovered isomorphism only for names
  that do not correspond: a bench of parallel identical-topology branches has many valid
  isomorphisms, and one that pairs unlike devices turns their deliberate size difference into
  a sizing failure (#216). A fallback pair is labelled ``(paired by structure)`` in the
  message, so a reader can tell a *pairing* from a comparison.
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
    "pair_components",
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
        "xschem",
        "--rcfile",
        str(rc),
        "-n",
        "-q",
        "-x",
        "-o",
        str(out_dir),
        str(source),
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
    _reject_skipped_tokens(source, log)
    return netlist


_SKIPPING = "SKIPPING"


def _reject_skipped_tokens(source: Path, log: str) -> None:
    """Raise when xschem reports that it SKIPPED part of a schematic it nonetheless netlisted.

    xschem exits 0 after dropping a token it could not tokenize (an unescaped brace in an attribute
    value is the case that motivated this) and quietly falls back to the symbol template's default,
    so the netlist LOOKS fine while carrying a value the schematic never stated. Whenever xschem
    does say so, that has to be a loud failure rather than a silently wrong netlist.

    Caveat, measured on xschem 3.4.5: under ``-q`` (which this function needs — without it xschem
    waits on a display and never exits) the brace case prints NOTHING. So this guard is a net that
    catches whatever xschem chooses to report; it is not what makes the brace round trip correct.
    That is :func:`..emit._fmt_value`, which escapes the braces so nothing is skipped at all.
    """
    hits = [ln.strip() for ln in log.splitlines() if _SKIPPING in ln]
    if hits:
        raise RuntimeError(
            f"xschem -n skipped part of {source.name} and netlisted the rest anyway "
            f"(exit 0): {'; '.join(hits)[:400]}. The netlist is not the schematic — a dropped "
            f"attribute silently reverts to its symbol template default."
        )


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
    """A merged device table typing BOTH sides (IHP source models + the target kit cells)."""
    from spicexplorer_circuitgraph import pdk as cg_pdk

    return cg_pdk.Pdk(
        name="xvport-compare",
        devices=tuple(cg_pdk.IHP_SG13G2.devices) + tuple(cg_pdk.GENERIC_N65.devices),
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
            netlist_text = _re.sub(rf"(?<![\w-]){_re.escape(name)}(?![\w-])", clean, netlist_text)
    return netlist_text


#: Canonical sizing attribute -> the spellings either netlister may use for it, and the
#: value SPICE assumes when a side does not declare it at all (``None`` = no default, so a
#: one-sided declaration is itself the finding). The xschem source says ``ng``; Virtuoso's
#: spectre netlister says ``nf`` (its ``propMapping`` is ``m←simM, nf←fingers, w←wf``, and
#: ``wf`` is the per-finger CDF ``w`` multiplied back out — so both sides' ``w`` is the
#: device's TOTAL width and compares directly, which is exactly what makes a mis-declared
#: ``per_finger`` rule visible here).
SIZING_KEYS: dict[str, tuple[tuple[str, ...], str | None]] = {
    "w": (("w", "wf"), None),
    "l": (("l",), None),
    "m": (("m", "simm"), "1"),
    "nf": (("nf", "ng", "fingers"), "1"),
}

#: Relative tolerance for a sizing comparison — the 0.1 % the schematic-of-record gate uses.
SIZING_RTOL = 1e-3


def _graph_pair(source_netlist: Path, cellview_netlist: Path) -> tuple[Any, Any]:
    """Both sides as circuitgraph graphs, typed by the merged comparison PDK."""
    try:
        from spicexplorer_circuitgraph import CircuitGraph
    except ImportError as exc:
        raise CheckUnavailable(
            "spicexplorer-circuitgraph is not installed (the [e2e] extra)"
        ) from exc
    from spicexplorer_core.spice_engine import NetlistView

    # side A: xschem output (SPICE dialect) — raw text, so the subckt renames apply
    a_text = _sanitize_subckt_names(Path(source_netlist).read_text(encoding="utf-8"))
    a_view = NetlistView.from_string(a_text, dialect="auto")
    b_view = NetlistView.from_file(cellview_netlist, dialect="spectre")
    pdk = _comparison_pdk()
    return (
        CircuitGraph.from_netlist(a_view, name="a", pdk=pdk, on_unknown="skip"),
        CircuitGraph.from_netlist(b_view, name="b", pdk=pdk, on_unknown="skip"),
    )


def _name_key(name: str) -> str:
    """The form two netlisters spell the same instance in.

    Case-folded, and one leading ``X`` dropped: xschem gives a subcircuit-wrapped device the
    ``X`` SPICE card letter (``XM1``) that Virtuoso's spectre netlister does not write (``M1``)
    — the committed t-gate fixture is exactly that pair.
    """
    key = name.strip().lower()
    return key[1:] if len(key) > 1 and key.startswith("x") else key


def _by_name_key(names: Iterable[str]) -> dict[str, str]:
    """``_name_key`` -> instance name, dropping any key two instances on this side share.

    An ambiguous key (a sheet carrying both ``M1`` and ``XM1``) is no basis for a pairing, so
    those instances are left to the isomorphism instead.
    """
    index: dict[str, str] = {}
    for name in names:
        key = _name_key(name)
        index[key] = "" if key in index else name
    return {k: v for k, v in index.items() if v}


def pair_components(
    names_a: Iterable[str], names_b: Iterable[str], mapping: dict | None
) -> list[tuple[str, str, bool]]:
    """Pair the two sides' instances: BY NAME first, by isomorphism for the rest.

    Returns ``(a_name, b_name, by_name)`` triples, sorted by ``a_name``.

    A same-kit port carries the names it read from the sheet onto both sides, so the
    correspondence is *known* and does not have to be guessed. Guessing it is what produced
    a false sizing failure on a bench of parallel identical-topology branches (issue #216): a
    device-characterisation sheet whose branches differ only in size and model has many valid
    isomorphisms, ``compare_graphs`` returns one of them, and pairing ``MNHVT10`` against
    ``MNHVT15`` reports their (correct, deliberate) size difference as the finding. Name-keyed
    pairing is O(n), exact, and strictly *stronger*, because it also catches a renamed
    instance — which an isomorphism is designed to forgive.

    The isomorphism is still the fallback for names that do not correspond, which is what a
    cross-kit or renamed port needs; those pairs come back flagged ``by_name=False`` so the
    caller can say so rather than let a reader mistake a pairing for a comparison.
    """
    names_a, names_b = list(names_a), list(names_b)
    key_a, key_b = _by_name_key(names_a), _by_name_key(names_b)
    pairs: list[tuple[str, str, bool]] = []
    used_a: set[str] = set()
    used_b: set[str] = set()
    for key, a_name in key_a.items():
        b_name = key_b.get(key)
        if b_name is not None:
            pairs.append((a_name, b_name, True))
            used_a.add(a_name)
            used_b.add(b_name)
    free_b = {n for n in names_b if n not in used_b}
    for a_name in sorted(n for n in names_a if n not in used_a):
        b_name = (mapping or {}).get(a_name)
        if b_name not in free_b:
            # The isomorphism points at an instance a name already claimed. When exactly one
            # partner is left unclaimed it is the only one this instance can correspond to;
            # otherwise report the isomorphism's own answer rather than drop the instance.
            b_name = next(iter(free_b)) if len(free_b) == 1 else b_name
        if b_name is None:
            continue
        pairs.append((a_name, b_name, False))
        free_b.discard(b_name)
    return sorted(pairs)


def _lookup_size(params: dict, aliases: tuple[str, ...]) -> str | None:
    lowered = {str(k).strip().lower(): v for k, v in params.items()}
    for alias in aliases:
        if alias in lowered and str(lowered[alias]).strip() != "":
            return str(lowered[alias])
    return None


def sizing_differences(
    ga: Any, gb: Any, comparison: Any, *, rtol: float = SIZING_RTOL
) -> list[str]:
    """Per-device sizing diffs, over instances paired BY NAME first (see :func:`pair_components`).

    The isomorphism is the fallback, not the primary key: on a bench of parallel branches that
    differ only in size and model it has several valid answers, and the one it returns can pair
    unlike devices whose (deliberate) size difference then reads as the finding (#216). Every
    pair the fallback produced is labelled ``(paired by structure)`` in the message, so
    ``MNHVT10->MNHVT15`` cannot be mistaken for a device compared with itself.

    ``compare_graphs`` can be told to fold the whole parameter dict into the node label
    (``match_params``), but that is unusable against a real Virtuoso export: the two
    netlisters spell the finger count differently and the export carries a dozen
    CDF-derived geometry parameters (``ad``/``as``/``sa``/``sb``/…) the source never had, so
    the frozensets never agree and every device reads as a mismatch. This compares the four
    attributes a port is actually responsible for, by name, eng-normalized — which also
    yields a diff a human can act on (``M3: w 32.4747u vs 2.0297u``) instead of two opaque
    parameter sets.
    """
    from spicexplorer_core.eng import parse_value

    comps_a = {c.name: c for c in ga.get_components()}
    comps_b = {c.name: c for c in gb.get_components()}
    out: list[str] = []
    pairs = pair_components(comps_a, comps_b, getattr(comparison, "component_mapping", None))
    for a_name, b_name, by_name in pairs:
        ca, cb = comps_a.get(a_name), comps_b.get(b_name)
        if ca is None or cb is None:
            continue
        pair = f"{a_name}->{b_name}" + ("" if by_name else " (paired by structure)")
        for key, (aliases, default) in SIZING_KEYS.items():
            va = _lookup_size(getattr(ca, "params", {}) or {}, aliases)
            vb = _lookup_size(getattr(cb, "params", {}) or {}, aliases)
            if va is None and vb is None:
                continue
            if va is None or vb is None:
                if default is None:
                    side = "source" if va is None else "cellview"
                    out.append(f"{pair}: {key} not declared on the {side} side")
                    continue
                va, vb = (default if va is None else va), (default if vb is None else vb)
            try:
                fa, fb = float(parse_value(va)), float(parse_value(vb))
            except (TypeError, ValueError):
                if str(va).strip().lower() != str(vb).strip().lower():
                    out.append(f"{pair}: {key} {va} vs {vb}")
                continue
            scale = max(abs(fa), abs(fb))
            if scale and abs(fa - fb) > rtol * scale:
                out.append(f"{pair}: {key} {va} vs {vb}")
    return out


def netlists_graph_equivalent(
    source_netlist: Path, cellview_netlist: Path, *, strict: bool = False
) -> Any:
    """circuitgraph comparison of a SPICE source netlist vs a spectre cellview netlist.

    Returns the ``GraphComparison`` (truthy iff equivalent; ``.reason`` explains).

    ``strict`` additionally folds the MODEL NAME into each device's label. The default test
    is topological — device type, MOS polarity and pin-level wiring — which is the right
    question for a cross-kit TOPOLOGY port, where the master changes on purpose. It is the
    wrong question for a SAME-KIT port, where a device landing on the neighbouring threshold
    flavour is a defect this oracle would otherwise pass: same type, same polarity, same
    wiring. Sizing is judged separately by :func:`sizing_differences`.
    """
    # _graph_pair first: it is what turns a missing [e2e] extra into CheckUnavailable, which
    # every caller handles as SKIPPED. Importing above it would raise a bare ImportError.
    ga, gb = _graph_pair(source_netlist, cellview_netlist)
    from spicexplorer_circuitgraph import compare_graphs

    return compare_graphs(ga, gb, match_models=strict)


def netcheck(
    client: Any,
    lib: str,
    cell: str,
    source: Path,
    work_dir: Path,
    *,
    timeout: int = 180,
    strict: bool = False,
    dropped: Iterable[str] = (),
) -> CheckReport:
    """The netlist + graph-equivalence oracle for one built schematic cellview.

    ``strict`` also compares model names and declared parameters — see
    :func:`netlists_graph_equivalent`.

    ``dropped`` is the emitter's list of device instances the sheet has and the ``.il`` does
    NOT build (``EmitResult.dropped``). It has to be passed in because it is the one fact
    **neither** netlist carries: both sides of this comparison descend from the same source
    file, so an instance whose symbol did not resolve is absent from the cellview *and* from
    the xschem re-netlist, and the two agree about a circuit that is missing a component —
    the port that reported ``matched 4 components`` for a five-component comparator bench
    (#226). A non-empty ``dropped`` is therefore a FAILURE decided before either netlister
    runs, so it stands even where an unavailable oracle would have reported SKIPPED.
    """
    name = "netcheck (strict)" if strict else "netcheck"
    missing = sorted(dropped)
    if missing:
        return CheckReport(
            name,
            False,
            detail=(
                f"{len(missing)} instance(s) of the sheet were dropped at emit time and are "
                f"in neither netlist: {', '.join(missing)} — the built cellview is not this "
                "schematic, so an equivalence verdict on it would be meaningless"
            ),
        )
    try:
        src_netlist = xschem_source_netlist(source, Path(work_dir) / "source")
        cv_netlist = fetch_cellview_netlist(
            client, lib, cell, Path(work_dir) / "cellview", timeout=timeout
        )
        ga, gb = _graph_pair(src_netlist, cv_netlist)
        from spicexplorer_circuitgraph import compare_graphs

        comparison = compare_graphs(ga, gb, match_models=strict)
    except CheckUnavailable as exc:
        return CheckReport(name, True, skipped=str(exc))
    if not comparison:
        return CheckReport(name, False, detail=comparison.reason)
    if strict and comparison.rests_on_skipped:
        # The graphs agree on everything circuitgraph could TYPE and know nothing about the
        # rest, so an untyped kit would pass this gate without comparing a single device.
        # Tolerable for the default topological question; not for the gate a same-kit port
        # rests on. The fix is to type the kit's devices (a circuitgraph PDK table).
        skipped = ", ".join(sorted({*comparison.skipped_a, *comparison.skipped_b})[:6])
        return CheckReport(
            name,
            False,
            detail=f"verdict rests on untyped devices — nothing was compared for: {skipped}",
        )
    # Sizing is only meaningful once the isomorphism exists — it is what names the pairs.
    diffs = sizing_differences(ga, gb, comparison) if strict else []
    if diffs:
        shown = "; ".join(diffs[:6]) + (f" (+{len(diffs) - 6} more)" if len(diffs) > 6 else "")
        return CheckReport(name, False, detail=f"sizing differs — {shown}")
    return CheckReport(name, True, detail=comparison.reason)


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
        body = lines[starts[0] :]
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
            raise CheckUnavailable("no model file configured (--sim-models / XVPORT_SIM_MODELS)")
        if netlist_file is None or not Path(netlist_file).is_file():
            netlist_file = fetch_cellview_netlist(client, lib, cell, Path(work_dir) / "cellview")
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
