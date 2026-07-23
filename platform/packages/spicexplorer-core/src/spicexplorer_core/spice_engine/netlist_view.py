"""NetlistView — read-only topology introspection over a SPICE netlist.

This is the single seam through which higher layers (e.g. the ``spicexplorer-circuitgraph``
tool) read a netlist's *structure* — its nets, components, and subcircuits. It wraps
spicelib's ``SpiceEditor``/``SpiceCircuit`` and is the **only** place in the suite above the
engine that names spicelib types, so callers never ``import spicelib`` themselves.

Unlike :class:`~spicexplorer_core.spice_engine.spicelib.NGSpice_Wrapper`, constructing a
``NetlistView`` is **parse-only**: it needs neither ngspice nor a PDK, so it works on any host
(including a PDK-less Mac). Use ``NGSpice_Wrapper`` when you actually need to simulate.

All accessors are single-level (they do not descend into nested subcircuits). To walk a
hierarchy, step into a subckt instance with :meth:`get_subcircuit`, which returns another
``NetlistView`` over the referenced definition.
"""

from __future__ import annotations

import logging
import re
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from spicelib import SpiceEditor

from .dialects import Directive, NetlistDialect, ParsedDeck, detect_dialect, get_reader

if TYPE_CHECKING:
    from spicelib.editor.spice_editor import SpiceCircuit

__all__ = ["NetlistView", "NetlistViewLike"]

logger = logging.getLogger(__name__)


@runtime_checkable
class NetlistViewLike(Protocol):
    """The topology-accessor surface consumers (e.g. circuitgraph) read a netlist through.

    :class:`NetlistView` satisfies this structurally; a future native dialect parser (or an
    OA-backed view) can drop in by implementing the same ten accessors — consumers should type
    against this Protocol, not the concrete class.
    """

    def get_all_nodes(self) -> list[str]: ...
    def get_components(self, prefixes: str = "*") -> list[str]: ...
    def get_component_nodes(self, reference: str) -> list[str]: ...
    def get_component_value(self, reference: str) -> str: ...
    def get_component_parameters(self, reference: str) -> dict: ...
    def get_parameters(self) -> dict[str, str]: ...
    def get_subcircuit_names(self) -> list[str]: ...
    def get_subcircuit_named(self, name: str) -> "NetlistViewLike | None": ...
    def get_subcircuit(self, instance_name: str) -> "NetlistViewLike": ...
    def get_subcircuit_ports(self, instance_name: str) -> list[str] | None: ...


def _read_text_tolerant(path: Path) -> str:
    """Read netlist text for sniffing/normalizing (utf-8 first, latin-1 fallback)."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")

# `.SUBCKT <name> <port> <port> … [params…]` — capture the tokens after the name.
_SUBCKT_HEADER = re.compile(r"^\s*\.subckt\s+\S+\s+(?P<ports>.*)$", re.IGNORECASE)


def _parse_subckt_ports(circuit: "SpiceCircuit") -> list[str] | None:
    """Extract the ordered port names from a subcircuit's ``.SUBCKT`` header line."""
    for line in circuit.netlist:
        if not isinstance(line, str):
            continue  # nested SpiceCircuit / control block — not the header
        m = _SUBCKT_HEADER.match(line)
        if m:
            ports: list[str] = []
            for tok in m.group("ports").split():
                if "=" in tok or tok.lower().rstrip(":") == "params":
                    break  # reached the parameter section
                ports.append(tok)
            return ports
    return None


class NetlistView:
    """Read-only view of a netlist's topology (nodes, components, subcircuits).

    Prefer the :meth:`from_file` / :meth:`from_string` constructors. The bare constructor
    wraps an already-parsed spicelib circuit and is used internally by :meth:`get_subcircuit`.
    """

    def __init__(self, circuit: "SpiceEditor | SpiceCircuit") -> None:
        self._circuit = circuit
        # Dialect metadata — populated by the constructors for foreign-dialect sources and
        # propagated on step-in; the classic SPICE path keeps these defaults.
        self._dialect: NetlistDialect = NetlistDialect.SPICE
        self._directives: tuple[Directive, ...] = ()
        self._name_map: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------
    @classmethod
    def from_file(
        cls, netlist_file: str | Path, *, dialect: "NetlistDialect | str" = "auto"
    ) -> "NetlistView":
        """Parse a netlist file (``.cir`` / ``.net`` / ``.sp`` / ``.spice`` / ``.scs``) into a view.

        ``dialect`` selects the source syntax: ``"auto"`` (default) sniffs via
        :func:`~spicexplorer_core.spice_engine.dialects.detect_dialect`; ``"spice"``/``"ngspice"``
        is the native spicelib path (unchanged, byte-identical behavior); ``"spectre"``/``"hspice"``
        route through the dialect normalizer first. On the dialect path, ``include``/``.lib``
        statements are **never resolved** — they are preserved on :attr:`directives`.
        """
        path = Path(netlist_file)
        if dialect == "auto":
            resolved = (
                NetlistDialect.SPECTRE
                if path.suffix.lower() == ".scs"
                else detect_dialect(_read_text_tolerant(path), path.name)
            )
        else:
            resolved = NetlistDialect.coerce(dialect)
        if resolved is NetlistDialect.SPICE:
            return cls(SpiceEditor(netlist_file=str(path)))
        return cls._from_deck(get_reader(resolved).read(_read_text_tolerant(path)), source=str(path))

    @classmethod
    def from_string(
        cls, netlist: str, *, dialect: "NetlistDialect | str" = "spice"
    ) -> "NetlistView":
        """Parse raw netlist text into a view (``dialect="auto"`` sniffs the text).

        For self-contained netlists: ``.lib``/``.include`` directives are **not** resolved
        relative to any source directory here (there is none). The text is parsed eagerly, so
        topology accessors work without the backing file.
        """
        resolved = (
            detect_dialect(netlist) if dialect == "auto" else NetlistDialect.coerce(dialect)
        )
        if resolved is not NetlistDialect.SPICE:
            return cls._from_deck(get_reader(resolved).read(netlist), source="<string>")
        with tempfile.NamedTemporaryFile("w", suffix=".cir", delete=False, encoding="utf-8") as fh:
            fh.write(netlist)
            tmp_path = Path(fh.name)
        try:
            return cls(SpiceEditor(netlist_file=str(tmp_path)))
        finally:
            tmp_path.unlink(missing_ok=True)

    @classmethod
    def _from_deck(cls, deck: ParsedDeck, *, source: str) -> "NetlistView":
        """Build a view over a dialect reader's canonical text, carrying its metadata."""
        for warning in deck.warnings:
            logger.warning("%s [%s]: %s", deck.dialect.value, source, warning)
        view = cls.from_string(deck.canonical_text)  # canonical text is native SPICE
        view._dialect = deck.dialect
        view._directives = deck.directives
        view._name_map = dict(deck.name_map)
        return view

    # ------------------------------------------------------------------
    # Dialect metadata
    # ------------------------------------------------------------------
    @property
    def dialect(self) -> NetlistDialect:
        """The source dialect this view was parsed from (``SPICE`` for the classic path)."""
        return self._dialect

    @property
    def directives(self) -> tuple[Directive, ...]:
        """Non-structural source statements (analyses, options, includes, models) preserved
        verbatim by the dialect reader — empty on the classic SPICE path."""
        return self._directives

    def original_name(self, reference: str) -> str:
        """The source-netlist instance name behind a (possibly prefix-conformed) canonical ref.

        Identity for the classic SPICE path and for refs the reader did not rename.
        """
        return self._name_map.get(reference.upper(), reference)

    def _propagate_metadata(self, child: "NetlistView") -> "NetlistView":
        child._dialect = self._dialect
        child._directives = self._directives
        child._name_map = self._name_map
        return child

    # ------------------------------------------------------------------
    # Topology accessors (delegate to spicelib, single-level)
    # ------------------------------------------------------------------
    def get_all_nodes(self) -> list[str]:
        """All net (node) names at this level."""
        return self._circuit.get_all_nodes()

    def get_components(self, prefixes: str = "*") -> list[str]:
        """Component reference designators at this level (does not descend into subckts)."""
        return self._circuit.get_components(prefixes)

    def get_component_nodes(self, reference: str) -> list[str]:
        """The nets a component is wired to, in spicelib's pin order."""
        return self._circuit.get_component_nodes(reference)

    def get_component_value(self, reference: str) -> str:
        """The component's value/model token (e.g. a MOSFET's model name)."""
        return self._circuit.get_component_value(reference)

    def get_component_parameters(self, reference: str) -> dict:
        """The component's ``k=v`` parameters (spicelib also includes a ``'Value'`` key)."""
        return self._circuit.get_component_parameters(reference)

    def get_parameters(self) -> dict[str, str]:
        """The global ``.param`` definitions visible at this level, as ``{name: value_string}``.

        Values are returned verbatim (engineering strings like ``"50f"`` or symbolic references);
        callers parse them. spicelib upper-cases parameter names, so a consumer matching these
        against device-card references should normalize case.
        """
        return {name: self._circuit.get_parameter(name) for name in self._circuit.get_all_parameter_names()}

    def get_subcircuit_names(self) -> list[str]:
        """Names of ``.subckt`` definitions present at this level."""
        return self._circuit.get_subcircuit_names()

    def get_subcircuit_named(self, name: str) -> "NetlistView | None":
        """The definition of a ``.subckt`` by name, as a view (``None`` if not found)."""
        sub = self._circuit.get_subcircuit_named(name)
        return None if sub is None else self._propagate_metadata(NetlistView(sub))

    def _definition_for_truncated_name(self, referenced: str) -> "SpiceCircuit | None":
        """Work around spicelib's subckt-name regex (``[\\w.]+`` — no hyphen): a definition
        ``.subckt ota-improved …`` is registered under the truncated name ``ota``, so an instance
        referencing ``ota-improved`` can't be resolved directly. Match the referenced name against
        the registered names by truncated-prefix (longest wins)."""
        names = self._circuit.get_subcircuit_names()
        if referenced in names:
            return self._circuit.get_subcircuit_named(referenced)
        candidates = [
            n for n in names
            if len(n) < len(referenced)
            and referenced.startswith(n)
            and not (referenced[len(n)].isalnum() or referenced[len(n)] == "_")
        ]
        if not candidates:
            return None
        return self._circuit.get_subcircuit_named(max(candidates, key=len))

    def get_subcircuit(self, instance_name: str) -> "NetlistView":
        """Step into an ``X…`` subckt *instance*: return its definition as a new view.

        Supports spicelib's ``parent:child`` instance paths and lookup of definitions inside
        ``.lib``/``.include`` files. A definition whose name spicelib truncated (hyphenated
        names like ``ota-improved``) is resolved by truncated-prefix fallback.
        """
        try:
            return self._propagate_metadata(NetlistView(self._circuit.get_subcircuit(instance_name)))
        except Exception:
            if ":" not in instance_name:  # fallback is single-level only
                referenced = str(self._circuit.get_component_value(instance_name))
                sub = self._definition_for_truncated_name(referenced)
                if sub is not None:
                    return self._propagate_metadata(NetlistView(sub))
            raise

    def get_subcircuit_ports(self, instance_name: str) -> list[str] | None:
        """Formal ``.SUBCKT``-header port names of the subckt an ``X…`` instance references.

        The returned ports line up positionally with :meth:`get_component_nodes` for the same
        instance. Returns ``None`` when the definition can't be resolved (e.g. a definition in
        an unresolved library), so callers can fall back to positional port labels.
        """
        try:
            sub = self.get_subcircuit(instance_name)._circuit
        except Exception:
            return None
        return _parse_subckt_ports(sub)
