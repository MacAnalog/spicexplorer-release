"""The native analysis runner.

Runs ``analyses × pdk × corner`` through ngspice batch and records provenance-stamped
scoreboard entries at ``circuits/<id>/scoreboard/<pdk>/<design_id>.json``. PDK-gated:
needs ngspice AND the PDK's corner libs on the ngspice sourcepath. Two execution modes:

  - local:  ``ngspice -b`` on this machine's PATH.
  - docker: pipe each netlist into ``docker compose exec -T <service> ngspice`` from the host —
    no dependence on the (possibly stale) repo copy baked into the image.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol

from spicexplorer_core.spice_engine.deck_prep import plan_slim_swap

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

    search = [pdk_dir / spec["model_subdir"]] + [pdk_dir / p for p in spec.get("extra_sourcepath", [])]

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

# ngspice meas/print output: "name              =  2.977862e+01"; MIN/MAX/PP/AVG
# measures append the location, e.g. "name = 4.8e-01 at=  4.34e-06" — accept it.
_MEASURE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)"
    r"(?:\s+(?:at|from|to)\s*=.*)?\s*$"
)
_FAILED = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*failed", re.IGNORECASE)


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
        raise RuntimeError(f"native PDK {pdk!r} not installed under $PDK_ROOT={os.environ.get('PDK_ROOT')}")
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


def parse_measures(output: str) -> tuple[dict[str, float], list[str]]:
    """(measures, failed-measure names) from ngspice batch output."""
    measures: dict[str, float] = {}
    failed: list[str] = []
    for line in output.splitlines():
        m = _MEASURE.match(line)
        if m:
            measures[m.group(1).lower()] = float(m.group(2))
            continue
        f = _FAILED.match(line)
        if f:
            failed.append(f.group(1).lower())
    return measures, failed


class SimError(RuntimeError):
    pass


def run_text(
    netlist: str, label: str = "<netlist>", runner: SpiceRunner = local_runner
) -> dict[str, float]:
    """Simulate an arbitrary deck STRING (e.g. a committed ``raw/`` file) and return its measures.
    Raises ``SimError`` on a fatal error, no parseable measures, or a NaN; ``label`` tags the message."""
    output = runner(netlist)
    lowered = output.lower()
    if "fatal" in lowered or "simulation interrupted" in lowered or "cannot open" in lowered:
        raise SimError(f"{label}: ngspice error:\n{output[-2000:]}")
    measures, failed = parse_measures(output)
    if not measures:
        raise SimError(f"{label}: no measures parsed:\n{output[-2000:]}")
    for name, value in measures.items():
        if value != value:  # NaN
            raise SimError(f"{label}: {name} is NaN")
    if failed:
        measures.update({name: float("nan") for name in failed})
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
