"""Typed loaders over the on-disk database (the registry walker).

Thin, dependency-light readers: YAML in, plain dict/dataclass out. The schema validation
lives in ``schema.py``; this module just locates and parses.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from . import paths

# Verifiable-circuit accession id: <class id_code>_<nnn>_<slug>, where the
# number is append-only (allocated max+1, never renumbered or reused). Reference circuits instead
# keep corpus-scoped ids, e.g. ferrosim_<name>.
ACCESSION_RE = re.compile(r"^(?P<code>[a-z]+)_(?P<num>[0-9]{3})_(?P<slug>[a-z0-9][a-z0-9_]*)$")
REFERENCE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")

# A CLOCKED circuit exposes a chopper / switched-capacitor clock as a port (clk_*/phi*). Its
# switches toggle, so a FROZEN-operating-point small-signal analysis (.ac / .noise) does not
# represent it — the correct in-operation benches are transient (native ngspice) or PSS/PAC/
# pnoise (Spectre). Enforced by the assemble() guard + the verify Tier-0 xref check.
_CLOCK_PORT_RE = re.compile(r"^(clk|phi)([_0-9]|$)", re.IGNORECASE)

# Frozen-OP small-signal analysis ids: the ``.ac``-based family (``ac_*`` + cmrr/psrr/stb) and
# the ``.noise``-based family (``noise*``). These are the analyses that are INVALID on a clocked
# circuit. PSS/PAC ids (``pac_*``, ``pnoise_*``) are the periodic replacements and are allowed.
_FROZEN_SS_ANALYSIS_NAMES = frozenset(
    {
        "cmrr_vcm",
        "cmrr_vcm_selfbias",
        "psrr",
        "psrr_vdd",
        "psrr_vdd_selfbias",
        "psrr_vss",
        "stb",
        "noise",
        "noise_diff",
        "noise_biaswrap_ibias",
    }
)


def is_frozen_smallsignal_analysis(analysis_id: str) -> bool:
    """True iff ``analysis_id`` names a frozen-operating-point small-signal analysis (``.ac`` /
    ``.noise`` family). Such an analysis is physically invalid on a clocked (chopper /
    switched-cap) circuit — use a transient bench or PSS/PAC/pnoise instead."""
    a = str(analysis_id)
    return a.startswith("ac_") or a in _FROZEN_SS_ANALYSIS_NAMES


def parse_accession(circuit_id: str) -> tuple[str, int, str] | None:
    """``(code, number, slug)`` if the id is a valid accession id, else ``None``."""
    m = ACCESSION_RE.match(circuit_id)
    return (m["code"], int(m["num"]), m["slug"]) if m else None


def class_id_code(class_id: str) -> str | None:
    """The class's accession-id prefix (``id_code`` in its metrics.yaml), if declared."""
    try:
        return load_class(class_id).get("id_code")
    except FileNotFoundError:
        return None


def next_accession(code: str, root: Path | None = None) -> int:
    """The next free accession number for ``code`` — max over the registry + 1 (gaps stay gaps)."""
    root = root if root is not None else paths.circuits_root()
    taken = [
        acc[1]
        for p in (root.iterdir() if root.is_dir() else ())
        if (acc := parse_accession(p.name)) and acc[0] == code
    ]
    return max(taken, default=0) + 1


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open() as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping, got {type(data).__name__}")
    return data


@dataclass(frozen=True)
class Circuit:
    """A circuit directory and its parsed manifest."""

    id: str
    dir: Path
    manifest: dict[str, Any]

    @property
    def klass(self) -> str:
        return self.manifest.get("class", "")

    @property
    def pdks(self) -> list[str]:
        return list(self.manifest.get("pdks", []))

    @property
    def analyses(self) -> list[str]:
        return list(self.manifest.get("analyses", []))

    @property
    def ports(self) -> list[str]:
        return [str(p) for p in (self.manifest.get("ports", []) or [])]

    @property
    def is_clocked(self) -> bool:
        """True iff any port is a chopper / switched-cap clock (``clk_*`` / ``phi*``). A clocked
        circuit's switches toggle, so a frozen-operating-point small-signal analysis (``.ac`` /
        ``.noise``) is invalid on it — see :func:`is_frozen_smallsignal_analysis`. This is the
        predicate the assemble() guard and the verify Tier-0 check key on."""
        return any(_CLOCK_PORT_RE.match(p) for p in self.ports)

    @property
    def status(self) -> str:
        return self.manifest.get("status", "draft")

    @property
    def references(self) -> list[dict[str, Any]]:
        """Reference bindings: foreign/proprietary decks, not lowered or run here."""
        return list(self.manifest.get("references", []))

    @property
    def kind(self) -> str:
        """``reference`` iff authored so, or (derived) a reference-only binding set; else ``verifiable``."""
        declared = self.manifest.get("kind")
        if declared:
            return str(declared)
        return "reference" if (self.references and not self.pdks) else "verifiable"

    @property
    def is_published(self) -> bool:
        """False iff the manifest DE-PUBLISHES this circuit (``published: false``).

        Orthogonal to :attr:`kind`. A de-published circuit is dropped from the generated
        scoreboard index / paper tabulation but stays fully verifiable: bindings, sizing, params
        and raw decks are still generated, drift-guarded and resolvable — which is what lets a
        composite keep composing a retired cell as its core block. ``kind: reference`` is NOT a
        de-publish marker: it means "imported foreign deck" (PDK-free, carries ``references``).
        """
        return bool(self.manifest.get("published", True))

    @property
    def is_reference_only(self) -> bool:
        """A pure reference circuit: reference bindings and no open-PDK (verifiable) bindings."""
        return self.kind == "reference" or (bool(self.references) and not self.pdks)

    def reference_dir(self, entry: dict[str, Any]) -> Path:
        """The binding directory for one ``references`` entry (relative ``dir`` resolved under the circuit)."""
        return self.dir / str(entry.get("dir", ""))

    def datasheet(self) -> dict[str, Any]:
        return _load_yaml(self.dir / "datasheet.yaml")

    def pdk_dir(self, pdk: str) -> Path:
        """The binding directory ``pdk/<pdk>/`` — raises with the available PDKs if it's not bound."""
        d = self.dir / "pdk" / pdk
        if not d.is_dir():
            root = self.dir / "pdk"
            have = sorted(p.name for p in root.iterdir() if p.is_dir()) if root.is_dir() else []
            raise FileNotFoundError(
                f"{self.id}: not bound to pdk {pdk!r} (have: {', '.join(have) or 'none'})"
            )
        return d

    def sizing(self, pdk: str) -> dict[str, Any]:
        return _load_yaml(self.pdk_dir(pdk) / "sizing.yaml")

    def netlist(self, pdk: str) -> Path:
        """Path to the PDK-bound lowered netlist (``.spice``) — parity with :meth:`sizing`.

        Returns a ``Path`` (the netlist is SPICE text, not YAML); read it or hand it to a tool. The
        PDK-neutral source is :meth:`abstract_netlist`.
        """
        p = self.pdk_dir(pdk) / "netlist.spice"
        if not p.is_file():
            raise FileNotFoundError(f"{self.id}: no netlist.spice under pdk/{pdk}/")
        return p

    def abstract_netlist(self) -> Path:
        """Path to the PDK-neutral abstract netlist (``abstract/netlist.spice``)."""
        p = self.dir / "abstract" / "netlist.spice"
        if not p.is_file():
            raise FileNotFoundError(f"{self.id}: no abstract/netlist.spice")
        return p

    def analysis_files(self) -> dict[str, Path]:
        d = self.dir / "analyses"
        if not d.is_dir():
            return {}
        return {p.stem: p for p in sorted(d.glob("*.yaml"))}

    def analysis(self, analysis_id: str) -> dict[str, Any]:
        return _load_yaml(self.dir / "analyses" / f"{analysis_id}.yaml")


def list_circuit_ids() -> list[str]:
    root = paths.circuits_root()
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if (p / "circuit.yaml").is_file())


def load_circuit(circuit_id: str) -> Circuit:
    cdir = paths.circuits_root() / circuit_id
    if not (cdir / "circuit.yaml").is_file():
        known = ", ".join(list_circuit_ids()[:8])
        raise KeyError(f"unknown circuit {circuit_id!r} — known ids start: {known}, …")
    manifest = _load_yaml(cdir / "circuit.yaml")
    return Circuit(id=circuit_id, dir=cdir, manifest=manifest)


def load_all_circuits() -> list[Circuit]:
    return [load_circuit(cid) for cid in list_circuit_ids()]


@lru_cache(maxsize=None)
def list_class_ids() -> tuple[str, ...]:
    root = paths.classes_root()
    if not root.is_dir():
        return ()
    return tuple(sorted(p.name for p in root.iterdir() if (p / "metrics.yaml").is_file()))


def load_class(class_id: str) -> dict[str, Any]:
    return _load_yaml(paths.classes_root() / class_id / "metrics.yaml")


def class_templates(class_id: str) -> list[str]:
    return list(load_class(class_id).get("templates", []))


def resolve_template(class_id: str, template_id: str) -> Path | None:
    """Resolve a template id: class-scoped first, then the universal set."""
    candidates = [
        paths.classes_root() / class_id / "testbench-templates" / f"{template_id}.spice",
        paths.shared_templates_root() / f"{template_id}.spice",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None
