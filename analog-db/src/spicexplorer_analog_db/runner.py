"""The native analysis runner.

Runs ``analyses × pdk × corner`` through ngspice batch and records provenance-stamped
scoreboard entries at ``circuits/<id>/scoreboard/<pdk>/<design_id>.json``. PDK-gated:
needs ngspice AND the PDK's corner libs on the ngspice sourcepath. Two execution modes:

  - local:  ``ngspice -b`` on this machine's PATH.
  - docker: pipe each netlist into ``docker compose exec -T <service> ngspice`` from the host —
    no dependence on the (possibly stale) repo copy baked into the image.
"""

from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from spicexplorer_core.spice_engine.deck_prep import plan_slim_swap

try:
    from spicexplorer_core.spice_engine.sim_log import parse_measures
except ImportError as _exc:  # pragma: no cover - exercised by the merge-order test
    raise ImportError(
        "spicexplorer_core.spice_engine.sim_log is missing. analog-db re-exports its "
        "`parse_measures` instead of keeping a third private copy of the ngspice scalar-scrape "
        "rules; the module lands on spicexplorer-platform with PR #129 "
        "(branch `feat/harness-spec-v2`). MERGE ORDER: platform #129 must merge and the "
        "meta-repo submodule pointer be re-pinned BEFORE this analog-db branch."
    ) from _exc

from .assemble import assemble
from .model import Circuit


def _prepare_native_deck(netlist: str, pdk_dir: Path, spec: dict) -> str:
    """Native-lane deck fixes the container doesn't need (the container vendors the PDK on the deck
    path; the host resolves libs via the ``.spiceinit`` sourcepath instead):

    1. **Slim corner-lib swap** — replace a full binned corner lib (sky130's ~480k-line
       ``.lib sky130.lib.spice <corner>``) with its generated slim lib (byte-identical models,
       ~50-90x faster parse) when :func:`plan_slim_swap` finds one covering the deck's devices.
    2. **Absolute section-less includes** — ngspice's ``.include`` (unlike ``.lib``) does NOT search
       the sourcepath, so a bare ``.include <file>`` of a corner file that lives in the PDK model
       dir (e.g. gf180's ``design.ngspice``) fails natively. Rewrite it to the resolved absolute path.
    """
    lines = netlist.splitlines()

    plan = plan_slim_swap(lines, device_scan_lines=lines)
    if plan is not None:
        strip_full = re.compile(plan.full_lib_strip, re.IGNORECASE)
        strip_slim = re.compile(plan.slim_lib_strip, re.IGNORECASE)
        slim_cards = [f".lib {plan.slim_lib} {sec}" for sec in plan.sections]
        out: list[str] = []
        injected = False
        for ln in lines:
            if strip_full.match(ln) or strip_slim.match(ln):
                if not injected:  # swap the first full-lib line for the slim cards; drop the rest
                    out.extend(slim_cards)
                    injected = True
                continue
            out.append(ln)
        lines = out

    search = [pdk_dir / spec["model_subdir"]] + [
        pdk_dir / p for p in spec.get("extra_sourcepath", [])
    ]

    def _resolve_include(ln: str) -> str:
        m = re.match(r"^(\s*\.inc(?:lude)?\s+)(\S+)(.*)$", ln, re.IGNORECASE)
        if not m:
            return ln
        token = m.group(2).strip('"')
        if "/" in token or os.path.isabs(token):
            return ln  # already a path — leave it
        for d in search:
            cand = d / token
            if cand.is_file():
                return f"{m.group(1)}{cand}{m.group(3)}"
        return ln

    return "\n".join(_resolve_include(ln) for ln in lines) + "\n"


class SpiceRunner(Protocol):
    def __call__(self, netlist: str, /) -> str: ...


def local_runner(netlist: str) -> str:
    """Run ``ngspice -b`` in a temp dir; return combined stdout+stderr."""
    with tempfile.TemporaryDirectory(prefix="analogdb_run_") as td:
        f = Path(td) / "cell.spice"
        f.write_text(netlist)
        proc = subprocess.run(
            ["ngspice", "-b", f.name], cwd=td, capture_output=True, text=True, timeout=300
        )
    return proc.stdout + proc.stderr


def docker_runner(service: str = "api") -> Callable[[str], str]:
    """A runner that executes ngspice inside the compose service, piping the netlist via stdin."""

    def _run(netlist: str) -> str:
        proc = subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "-T",
                service,
                "bash",
                "-lc",
                "d=$(mktemp -d) && cat > $d/cell.spice && cd $d && ngspice -b cell.spice 2>&1; rm -rf $d",
            ],
            input=netlist,
            capture_output=True,
            text=True,
            timeout=600,
        )
        return proc.stdout + proc.stderr

    return _run


def base_image_runner(image: str = "spicexplorer-spice-base:local") -> Callable[[str], str]:
    """A runner that pipes the netlist into a fresh ``docker run`` of the EDA base image.

    Image-independent (no running service / no api venv needed): the base image carries ngspice
    + both PDKs (ihp-sg13g2, sky130) + the .spiceinit sourcepath. This is how the host drives
    real PDK sims without rebuilding the api image.
    """

    def _run(netlist: str) -> str:
        proc = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-i",
                image,
                "bash",
                "-lc",
                "d=$(mktemp -d) && cat > $d/cell.spice && cd $d && ngspice -b cell.spice 2>&1",
            ],
            input=netlist,
            capture_output=True,
            text=True,
            timeout=600,
        )
        return proc.stdout + proc.stderr

    return _run


# --------------------------------------------------------------------------- native PDK sim
#
# Run ngspice on THIS host against a PDK installed under ``$PDK_ROOT`` — no container. Each of the
# three open PDKs needs its ngspice model dir on the sourcepath (and IHP its PSP OSDI modules); the
# committed decks reference the corner libs by bare filename (``.lib cornerMOSlv.lib mos_tt`` /
# ``.lib sky130.lib.spice tt`` / ``.lib sm141064.ngspice nfet_03v3_t``), so ngspice resolves them
# via ``sourcepath``. We write a per-PDK ``.spiceinit`` into the run's scratch dir (ngspice reads the
# CWD ``.spiceinit`` in preference to ``$HOME``'s), making the runner self-contained + PDK-correct
# regardless of the ambient shell config. This is the Tier-3 native sweep path.

# registry PDK name → on-disk ``$PDK_ROOT`` layout. dir candidates cover the ciel/volare install
# names (sky130A, gf180mcuD, …) that differ from the registry name; the first whose model dir exists
# wins. IHP keeps its BSIM/PSP models under models/ + needs the OSDI compiled devices loaded.
_NATIVE_PDK: dict[str, dict] = {
    "ihp-sg13g2": {
        "dirs": ["ihp-sg13g2"],
        "model_subdir": "libs.tech/ngspice/models",
        "extra_sourcepath": ["libs.ref/sg13g2_stdcell/spice"],
        "osdi": [
            "libs.tech/ngspice/osdi/psp103_nqs.osdi",
            "libs.tech/ngspice/osdi/r3_cmc.osdi",
            "libs.tech/ngspice/osdi/mosvar.osdi",
        ],
    },
    "sky130": {
        "dirs": ["sky130A", "sky130B", "sky130"],
        "model_subdir": "libs.tech/ngspice",
        "extra_sourcepath": [],
        "osdi": [],
    },
    "gf180mcu": {
        "dirs": ["gf180mcuD", "gf180mcuC", "gf180mcuB", "gf180mcuA", "gf180mcu"],
        "model_subdir": "libs.tech/ngspice",
        "extra_sourcepath": [],
        "osdi": [],
    },
}


def native_pdk_dir(pdk: str, pdk_root: str | None = None) -> Path | None:
    """Resolve the on-disk install dir for a registry PDK name under ``$PDK_ROOT`` (following the
    ciel symlinks), or ``None`` if that PDK's ngspice models aren't installed here."""
    root = pdk_root or os.environ.get("PDK_ROOT")
    spec = _NATIVE_PDK.get(pdk)
    if not root or not spec:
        return None
    base = Path(root)
    for d in spec["dirs"]:
        cand = base / d
        if (cand / spec["model_subdir"]).is_dir():
            return cand
    return None


def native_pdk_available(pdk: str, pdk_root: str | None = None) -> bool:
    """True iff ngspice is on PATH AND this PDK's ngspice models resolve under ``$PDK_ROOT`` —
    the gate for the native Tier-3 sim sweep (skips cleanly on a host missing ngspice or the PDK)."""
    return shutil.which("ngspice") is not None and native_pdk_dir(pdk, pdk_root) is not None


def _native_spiceinit(pdk_dir: Path, spec: dict) -> str:
    base = pdk_dir / spec["model_subdir"]
    sp = [str(base)] + [str(pdk_dir / p) for p in spec["extra_sourcepath"]]
    lines = [f"setcs sourcepath = ( $sourcepath {' '.join(sp)} )"]
    lines += [f"osdi '{pdk_dir / o}'" for o in spec["osdi"]]
    return "\n".join(lines) + "\n"


def native_pdk_runner(
    pdk: str, pdk_root: str | None = None, timeout: int = 300
) -> Callable[[str], str]:
    """A :class:`SpiceRunner` running ``ngspice -b`` natively with a per-PDK ``.spiceinit``
    (sourcepath + OSDI) dropped into each call's scratch dir, so a deck for ``pdk`` resolves its
    PDK libs with no container. Raises ``RuntimeError`` if the PDK isn't installed under
    ``$PDK_ROOT`` (guard with :func:`native_pdk_available`). Each call gets its own ``mktemp`` dir,
    so a thread pool can drive many cells concurrently without colliding."""
    pdk_dir = native_pdk_dir(pdk, pdk_root)
    spec = _NATIVE_PDK.get(pdk)
    if pdk_dir is None or spec is None:
        raise RuntimeError(
            f"native PDK {pdk!r} not installed under $PDK_ROOT={os.environ.get('PDK_ROOT')}"
        )
    init = _native_spiceinit(pdk_dir, spec)

    def _run(netlist: str) -> str:
        with tempfile.TemporaryDirectory(prefix="analogdb_native_") as td:
            Path(td, ".spiceinit").write_text(init)
            (Path(td) / "cell.spice").write_text(_prepare_native_deck(netlist, pdk_dir, spec))
            try:
                proc = subprocess.run(
                    ["ngspice", "-b", "cell.spice"],
                    cwd=td,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
            except subprocess.TimeoutExpired as exc:
                parts: list[str] = []
                for chunk in (exc.stdout, exc.stderr):
                    if chunk is None:
                        continue
                    parts.append(
                        chunk.decode("utf-8", "replace") if isinstance(chunk, bytes) else chunk
                    )
                return "".join(parts) + f"\nfatal: ngspice timed out after {timeout}s\n"
        return proc.stdout + proc.stderr

    return _run


def docker_exec_runner(container: str) -> Callable[[str], str]:
    """A runner that pipes the netlist into an ALREADY-RUNNING container via ``docker exec``.

    Much cheaper per call than :func:`base_image_runner` — that one pays a full container
    create/teardown (`docker run --rm`) on EVERY invocation, which dominates wall-clock when
    driving many decks in a loop (e.g. the T3 raw-deck sweep, ~200+ decks). Pair with
    :func:`start_detached_base_image`/:func:`stop_container` to start the base image ONCE and
    reuse it across every call; each call still runs in its own ``mktemp -d`` scratch dir so
    concurrent callers (e.g. a thread pool) don't collide.
    """

    def _run(netlist: str) -> str:
        proc = subprocess.run(
            [
                "docker",
                "exec",
                "-i",
                container,
                "bash",
                "-lc",
                "d=$(mktemp -d) && cat > $d/cell.spice && cd $d && ngspice -b cell.spice 2>&1; rm -rf $d",
            ],
            input=netlist,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return proc.stdout + proc.stderr

    return _run


def start_detached_base_image(
    image: str = "spicexplorer-spice-base:local", timeout: int = 60
) -> str | None:
    """Start ``image`` detached + self-removing, kept alive with ``sleep infinity``; return its
    container id for :func:`docker_exec_runner`, or ``None`` if docker/the image isn't
    available (never raises — callers fall back to :func:`base_image_runner`)."""
    try:
        proc = subprocess.run(
            ["docker", "run", "-d", "--rm", image, "sleep", "infinity"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None
    cid = proc.stdout.strip()
    return cid if proc.returncode == 0 and cid else None


def stop_container(container: str, timeout: int = 30) -> None:
    """Stop a container started by :func:`start_detached_base_image` (a ``--rm`` container
    auto-removes on stop). Best-effort — swallows errors so teardown never masks a test failure."""
    try:
        subprocess.run(["docker", "stop", container], capture_output=True, timeout=timeout)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass


# ngspice load-time (parse/library/topology) error markers — distinct from analysis-time
# failures (singular matrix, timestep). The Level-0 "no syntax error" gate keys on these.
_PARSE_ERR = re.compile(
    r"(could not find library|can't find|cannot find|unknown subckt|unknown model|"
    r"syntax error|error on line|premature|no such (parameter|vector)|unrecognized|"
    r"unable to find|too few|too many|fatal error in ngspice)",
    re.IGNORECASE,
)


def parse_errors_text(netlist: str, runner: SpiceRunner = local_runner) -> list[str]:
    """Level-0 on an arbitrary deck STRING (e.g. a committed ``raw/`` file): load it with the
    analysis replaced by a no-op ``quit`` so ngspice parses the deck + resolves the PDK libs WITHOUT
    running an analysis; return any load/syntax errors (empty = clean)."""
    probe = re.sub(r"\.control.*?\.endc", ".control\nquit\n.endc", netlist, flags=re.S | re.I)
    out = runner(probe)
    return [ln.strip() for ln in out.splitlines() if _PARSE_ERR.search(ln)]


def parse_errors(
    circuit: Circuit, analysis_id: str, pdk: str, corner: str, runner: SpiceRunner = local_runner
) -> list[str]:
    """Level-0 for one matrix cell: assemble it, then :func:`parse_errors_text`. Separates "the
    netlist is syntactically valid" from "the sim converges"."""
    return parse_errors_text(assemble(circuit, analysis_id, pdk, corner), runner)


# ``parse_measures`` is RE-EXPORTED (see the import at the top) from the one module that owns the
# simulator-log rules, ``spicexplorer_core.spice_engine.sim_log``. It used to be a third private
# copy of the ngspice scalar-scrape regexes, after the platform's and the waveform viewer's.
#
# The platform version is a strict SUPERSET of the copy that lived here — verified case by case in
# ``tests/test_parse_measures_reuse.py``. It additionally reads ngspice-45's
# ``meas tran <name> … failed!`` form (the copy here knew only the older ``<name> = failed`` line
# and silently missed the other), ``trig=``/``targ=`` delay tails, dotted names, and ``inf``/``nan``
# as non-finite floats. The name stays bound HERE because ``verify`` and the tests import it as
# ``runner.parse_measures``.
#
# ``run_text``'s own fatal scan below is deliberately NOT replaced by ``sim_log.fatal_lines``.
# The two CONTAINMENT gaps that used to justify this are now CLOSED (platform 2430bfc): both the
# lowercase ``fatal: ngspice timed out after …`` marker :func:`native_pdk_runner` emits above and
# every ``cannot open`` form are fatal to ``fatal_lines`` today, and on real ngspice logs the two
# agree. The scan stays for a different and stronger reason: ``fatal_lines`` is deliberately
# BROADER than this function's contract. It reports EVERY error-level line, including
# ``could not find a valid modelname`` (W out of the model bin), ``singular matrix``,
# ``no convergence``, ``timestep too small`` and ``doAnalyses: iteration limit reached`` — which
# this database classifies as RECORDED FLOORS (a degenerate baseline sizing), not dead runs; see
# TESTING.md §3 and ``tests/test_slow_sim.py::_LOAD_ERR``.
#
# Adopting it here would also undo the fix directly below: a deck that yields SOME finite measures
# alongside one of those lines would raise, ``run_circuit`` would mark the whole analysis
# ``sim_error``, and ``metric_values`` skips a non-``ok`` analysis — so every SIBLING metric would
# vanish from the scorecard, which scores more leniently than failing. Measured: 0 of 65 sampled
# committed decks (25 ihp-sg13g2 + 40 sky130/gf180mcu) currently pair finite measures with such a
# line, so the hazard is latent rather than active — but it is exactly the hazard `run_text`'s
# narrow, dead-run-only gate exists to avoid. ``fatal_lines`` remains the right rule for the
# viewer's log panel and for ``run_deck``, which classify lines rather than gate a recording.


class SimError(RuntimeError):
    pass


def run_text(
    netlist: str, label: str = "<netlist>", runner: SpiceRunner = local_runner
) -> dict[str, float]:
    """Simulate an arbitrary deck STRING (e.g. a committed ``raw/`` file) and return its measures.
    Raises ``SimError`` on a fatal error, no parseable measure, or a run in which NO measure came
    back finite; ``label`` tags the message.

    A single non-finite measure is NOT fatal. ngspice reports a failed ``.meas`` two ways at once —
    a ``-999`` sentinel and a ``… failed!`` line — and an overflowing ``let`` prints ``inf``/``nan``;
    either way that is ONE dead metric, not a dead run. Non-finite measures are kept as NaN so
    ``ppa.metric_values`` scores them ``{value: null, spec: fail}``, the honest verdict its docstring
    promises. Raising on the first NaN instead would set the whole analysis ``status: sim_error``,
    and ``metric_values`` skips a non-``ok`` analysis entirely — so every SIBLING metric of that
    analysis would vanish from the scorecard, and absence scores more leniently than failure."""
    output = runner(netlist)
    lowered = output.lower()
    if "fatal" in lowered or "simulation interrupted" in lowered or "cannot open" in lowered:
        raise SimError(f"{label}: ngspice error:\n{output[-2000:]}")
    measures, failed = parse_measures(output)
    if not measures:
        raise SimError(f"{label}: no measures parsed:\n{output[-2000:]}")
    # failed `.meas` names become NaN FIRST, so the "did anything survive?" gate sees the whole
    # picture (a `-999` sentinel must not count as a finite survivor).
    measures.update({name: float("nan") for name in failed})
    if not any(math.isfinite(v) for v in measures.values()):
        raise SimError(f"{label}: no finite measure (all {len(measures)} are NaN/inf)")
    return measures


def run_cell(
    circuit: Circuit, analysis_id: str, pdk: str, corner: str, runner: SpiceRunner = local_runner
) -> dict[str, float]:
    """Assemble + simulate one matrix cell; return its measures (raises ``SimError``)."""
    label = f"{circuit.id}/{analysis_id}@{pdk}/{corner}"
    return run_text(assemble(circuit, analysis_id, pdk, corner), label, runner)


def _ngspice_version(runner: SpiceRunner) -> str:
    out = runner("* version probe\n.control\nversion -s\nquit\n.endc\n.end\n")
    m = re.search(r"ngspice-([0-9.]+)", out)
    return m.group(1) if m else "unknown"


def run_circuit(
    circuit: Circuit, pdk: str, corner: str = "tt", runner: SpiceRunner = local_runner
) -> dict:
    """Run every declared analysis for one (pdk, corner); return the results document."""
    analyses: dict[str, dict] = {}
    for aid in circuit.analyses:
        if not circuit.analysis(aid).get("enabled", True):
            analyses[aid] = {"status": "disabled"}
            continue
        try:
            analyses[aid] = {
                "measures": run_cell(circuit, aid, pdk, corner, runner),
                "status": "ok",
            }
        except SimError as exc:
            analyses[aid] = {"status": "sim_error", "error": str(exc)[:500]}
    return {
        "schema": "spicexplorer/results@1",
        "circuit": circuit.id,
        "pdk": pdk,
        "corner": corner,
        "analyses": analyses,
        "provenance": {
            "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "ngspice": _ngspice_version(runner),
            "generator": "analog-db run",
        },
    }


def write_results(circuit: Circuit, results: dict) -> Path:
    """Record the run on the circuit's scoreboard: the current design point's entry gains this
    corner, and the first recorded design point per PDK is auto-named the baseline."""
    from .scoreboard import record

    return record(circuit, results)
