"""Pre-run ngspice deck preparation — PDK slim-corner-lib swap + noise solver guard.

Kept OUT of the general ``NGSpice_Wrapper`` so PDK-specific knowledge lives in ONE place
and adding a PDK is a registry entry, not a wrapper edit. Two independent concerns:

**Slim corner-lib swap (per-PDK, data-driven).** A full binned corner lib — e.g. sky130's
``.lib sky130.lib.spice <corner>`` (~480k expanded lines) — is re-parsed by ngspice on every
fresh process (~59 s, 99 % CPU-bound; the actual solve is <0.1 s). A *generated* slim lib
(see ``examples/analog-db/tools/make_sky130_slim_lib.py``) includes ONLY the device families a
deck uses → byte-identical models, ~1 s parse. :data:`SLIM_LIB_SPECS` lists the PDKs this
applies to; :func:`plan_slim_swap` picks the matching spec off the deck's own ``.lib`` line and
returns a :class:`SlimSwapPlan` (or ``None`` → keep the full lib). Every uncertainty fails
SAFE (keep the full lib): the slim lib absent on ``$PDK_ROOT``, an uncovered device family, a
``.lib`` section the slim lib doesn't define, or a deck whose devices can't be fully scanned
(an ``.include`` of circuit content, or no visible devices). **Add a PDK by appending a
:class:`SlimLibSpec`** — no wrapper change.

**Noise solver guard (PDK-agnostic).** ngspice's KLU direct solver cannot run ``.noise`` — it
errors and returns an empty ``inoise``/``onoise`` vector; ``.option sparse`` selects the solver
that can. :func:`noise_needs_sparse` detects a noise deck so the caller forces sparse.

Env toggles: per-spec ``spec.env_var`` (e.g. ``SPICEXPLORER_SKY130_SLIM_LIB``) or the global
``SPICEXPLORER_SLIM_LIB`` — ``auto`` (default) | ``off``/``0`` | ``<name-or-path>`` (force a
lib); and ``SPICEXPLORER_NGSPICE_NOISE_SPARSE=0`` to disable the noise guard.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_FALSEY = {"", "0", "off", "false", "no"}
_TRUTHY_AUTO = {"auto", "1", "on", "true", "yes"}


def _env_off(name: str, default: str = "1") -> bool:
    """True when env var ``name`` reads as disabled."""
    return os.environ.get(name, default).strip().lower() in _FALSEY


# ---------------------------------------------------------------------------------------
# Slim corner-lib swap
# ---------------------------------------------------------------------------------------
@dataclass(frozen=True)
class SlimLibSpec:
    """How to slim ONE PDK's corner lib (all fields are plain data — no wrapper coupling).

    :param name: PDK id (for logging), e.g. ``"sky130"``.
    :param pdk_subdirs: ``$PDK_ROOT`` subdirs to look under for the generated slim lib —
        e.g. ``("sky130A", "sky130")`` covers the volare/ciel and vendored-docker layouts.
    :param full_lib: basename of the stock full corner lib (``sky130.lib.spice``).
    :param slim_lib: basename of the generated slim lib (``sky130_slim.lib.spice``).
    :param device_prefix: model-name stem that identifies an instanced device
        (``sky130_fd_pr__``); a *bare* device ref has the same ``__`` count as the prefix.
    :param env_var: per-PDK toggle name (falls back to the global ``SPICEXPLORER_SLIM_LIB``).
    """

    name: str
    pdk_subdirs: tuple[str, ...]
    full_lib: str
    slim_lib: str
    device_prefix: str
    env_var: str

    @property
    def full_lib_re(self) -> re.Pattern[str]:
        return re.compile(rf"^\s*\.lib\s+\S*{re.escape(self.full_lib)}\s+(\S+)", re.IGNORECASE)

    @property
    def full_lib_strip(self) -> str:
        return rf"^\s*\.lib\s+\S*{re.escape(self.full_lib)}\s+\S+"

    @property
    def device_re(self) -> re.Pattern[str]:
        return re.compile(rf"{re.escape(self.device_prefix)}[A-Za-z0-9_]+")

    def setting(self) -> str:
        """The active toggle: per-spec env var, else the global, else ``auto``."""
        return (os.environ.get(self.env_var) or os.environ.get("SPICEXPLORER_SLIM_LIB") or "auto").strip()


# The PDKs the slim-lib swap applies to. Append a SlimLibSpec to support another PDK
# (e.g. gf180mcu) — nothing else changes. sky130 is the only binned-BSIM4 PDK measured to
# need it so far (IHP is compiled-OSDI PSP + a tiny corner lib; not worth slimming).
SLIM_LIB_SPECS: list[SlimLibSpec] = [
    SlimLibSpec(
        name="sky130",
        pdk_subdirs=("sky130A", "sky130"),
        full_lib="sky130.lib.spice",
        slim_lib="sky130_slim.lib.spice",
        device_prefix="sky130_fd_pr__",
        env_var="SPICEXPLORER_SKY130_SLIM_LIB",
    ),
]

# a circuit `.include`/`.inc` (NOT `.lib`) pulls in content the editor does NOT expand, so its
# devices can't be scanned → the coverage gate would fail open. Treat such a deck as unscannable.
_INCLUDE_RE = re.compile(r"^\s*\.inc(?:lude)?\b", re.IGNORECASE)


@dataclass(frozen=True)
class SlimSwapPlan:
    """The result of :func:`plan_slim_swap` — what the caller strips and re-adds.

    ``slim_lib`` is the reference the caller writes into the deck: the ABSOLUTE resolved path
    of the generated lib for the ``auto`` case (the lib lives in the PDK's ``corners/`` subdir,
    which is off ngspice's sourcepath — a bare basename wouldn't resolve), or the operator's
    verbatim string when they force one via env. ``full_lib_strip``/``slim_lib_strip`` are
    regexes the caller uses to remove the deck's current full ``.lib`` lines AND any prior slim
    ``.lib`` line (the latter keeps multi-corner PVT — one editor re-used across corners — from
    ACCUMULATING sections; both match by basename with a ``\\S*`` path prefix, so an absolute
    path is stripped fine). Then it adds ``.lib <slim_lib> <section>`` for each section.
    """

    slim_lib: str
    sections: list[str]
    full_lib_strip: str
    slim_lib_strip: str


def _slim_strip_pattern(slim_name: str) -> str:
    """Regex matching a ``.lib <slim_name> <section>`` line (any path prefix), for stripping."""
    return rf"^\s*\.lib\s+\S*{re.escape(Path(slim_name).name)}\s+\S+"


def _slim_lib_file(spec: SlimLibSpec) -> Path | None:
    """Locate the generated slim lib for ``spec`` via ``$PDK_ROOT`` (checks each layout)."""
    root = os.environ.get("PDK_ROOT")
    if not root:
        return None
    for sub in spec.pdk_subdirs:
        cand = Path(root) / sub / "libs.tech" / "ngspice" / "corners" / spec.slim_lib
        if cand.is_file():
            return cand
    return None


def _slim_lib_info(slim_path: Path, spec: SlimLibSpec) -> tuple[set[str], set[str]] | None:
    """Parse a generated slim lib → (covered device families, defined ``.lib`` sections)."""
    try:
        text = slim_path.read_text(errors="ignore")
    except OSError:
        return None
    m = re.search(r"Families:\s*(.+?)\.", text[:2000])
    if not m:
        return None
    families = {f"{spec.device_prefix}{f.strip()}" for f in m.group(1).split(",") if f.strip()}
    sections = set(re.findall(r"(?im)^\s*\.lib\s+(\S+)\s*$", text))
    if not families or not sections:
        return None
    return families, sections


def _scan_devices(lines: "list[Any]", spec: SlimLibSpec) -> set[str]:
    """Bare ``<prefix><family>`` device model refs on non-comment lines."""
    devs: set[str] = set()
    for ln in lines:
        if isinstance(ln, str) and ln.lstrip()[:1] != "*":
            devs.update(spec.device_re.findall(ln))
    return devs


def _plan_for_spec(
    spec: SlimLibSpec, netlist_lines: "list[Any]", device_scan_lines: "list[Any] | None"
) -> SlimSwapPlan | None:
    setting = spec.setting()
    if setting.lower() in _FALSEY:
        return None

    sections: list[str] = []
    has_include = False
    for ln in netlist_lines:
        if not isinstance(ln, str):
            continue
        m = spec.full_lib_re.match(ln)
        if m:
            sections.append(m.group(1))
        if _INCLUDE_RE.match(ln):
            has_include = True
    if not sections:
        return None  # this PDK's full lib isn't selected in the deck

    def _plan(slim_name: str) -> SlimSwapPlan:
        return SlimSwapPlan(slim_name, sections, spec.full_lib_strip, _slim_strip_pattern(slim_name))

    if setting.lower() not in _TRUTHY_AUTO:
        return _plan(setting)  # explicit lib named by the operator — trust it

    if has_include:
        return None  # unscannable `.include`d content → can't verify coverage → keep full lib

    slim = _slim_lib_file(spec)
    if slim is None:
        return None  # generator not run here → keep full lib (safe)
    info = _slim_lib_info(slim, spec)
    if info is None:
        return None
    covered_families, defined_sections = info
    if not set(sections).issubset(defined_sections):
        return None  # deck selects a section the slim lib doesn't define → keep full lib
    # scan devices from the raw deck text (has the .subckt body); fall back to the editor lines
    devices = _scan_devices(device_scan_lines if device_scan_lines is not None else netlist_lines, spec)
    # a bare device model ref has the same `__` count as the prefix; extra `__` = a model param
    depth = spec.device_prefix.count("__")
    used = {d for d in devices if d.count("__") == depth}
    if not used or not used.issubset(covered_families):
        return None  # no verifiable devices, or an uncovered family → keep full lib (safe)
    # Emit the ABSOLUTE resolved path, NOT the bare basename: the generator drops the slim lib
    # in the PDK's corners/ subdir, which is NOT on ngspice's sourcepath (only the ngspice root,
    # where the stock sky130.lib.spice lives, is) — so `.lib sky130_slim.lib.spice <c>` fails with
    # "Could not find library file". The absolute path always resolves, and the slim lib's own
    # verbatim `.include`s resolve relative to its (corners/) dir regardless. Verified in-container.
    return _plan(str(slim))


def plan_slim_swap(
    netlist_lines: "list[Any]", device_scan_lines: "list[Any] | None" = None
) -> SlimSwapPlan | None:
    """Decide whether to swap a full PDK corner lib for its slim one; ``None`` = keep full.

    Pure/​side-effect-free (unit-testable without a live ngspice). ``netlist_lines`` gives the
    CURRENT ``.lib``/``.include`` cards (the editor, reflecting any ``apply_corner`` swap).
    ``device_scan_lines`` (default: ``netlist_lines``) is scanned for device model refs — pass
    the raw deck TEXT here, because ``SpiceEditor`` stores a ``.subckt`` DUT body opaquely, so
    its device instances are invisible in ``editor.netlist``. Tries every registered
    :data:`SLIM_LIB_SPECS`; the first whose full lib the deck selects wins.
    """
    for spec in SLIM_LIB_SPECS:
        plan = _plan_for_spec(spec, netlist_lines, device_scan_lines)
        if plan is not None:
            return plan
    return None


# ---------------------------------------------------------------------------------------
# Noise solver guard (PDK-agnostic)
# ---------------------------------------------------------------------------------------
_NOISE_ANALYSIS_RE = re.compile(r"^\s*(?:\.noise|noise)\s+\S+", re.IGNORECASE)
_SOLVER_OPTION_RE = re.compile(r"^\s*\.options?\b.*\b(?:sparse|klu)\b", re.IGNORECASE)


def noise_needs_sparse(
    editor_lines: "list[Any]", deck_lines: "list[str]", testbench_name: str
) -> bool:
    """True if the deck runs a noise analysis and no solver option is set yet.

    ngspice KLU can't run ``.noise``; the caller should add ``.option sparse`` when this is
    True. Detects the ``noise`` command from the deck TEXT (it lives in a ``.control`` block
    the editor hides), the editor lines, or a ``noise`` testbench name. Disabled by
    ``$SPICEXPLORER_NGSPICE_NOISE_SPARSE=0``.
    """
    if _env_off("SPICEXPLORER_NGSPICE_NOISE_SPARSE"):
        return False
    ed = [ln for ln in editor_lines if isinstance(ln, str)]
    if any(_SOLVER_OPTION_RE.match(ln) for ln in ed):
        return False
    return (
        "noise" in testbench_name.lower()
        or any(_NOISE_ANALYSIS_RE.match(ln) for ln in deck_lines)
        or any(_NOISE_ANALYSIS_RE.match(ln) for ln in ed)
    )
