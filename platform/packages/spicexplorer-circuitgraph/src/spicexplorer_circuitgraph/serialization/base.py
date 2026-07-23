"""Serializer interface + a name-keyed registry.

A *strategy* turns a :class:`~spicexplorer_circuitgraph.graph.CircuitGraph` into one LLM-facing
representation (a JSON ``dict`` or a text ``str``). Which representation an LLM reasons about best
is an open research question, so the views are pluggable and comparable rather than baked in.

Adding a strategy is a one-file change: define a ``Serializer`` subclass and decorate it with
``@register``. It is then reachable by name via :func:`serialize` / :func:`get_strategy` and is
automatically picked up by the comparison harness.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from ..graph import CircuitGraph

Rendered = dict | str
Kind = Literal["json", "text"]


class Serializer(ABC):
    """Render a graph into one named view. Subclasses set ``name``/``kind`` and implement render."""

    name: str
    kind: Kind

    @abstractmethod
    def render(
        self,
        graph: CircuitGraph,
        *,
        include_params: bool = False,
        include_body: bool = False,
        include_spice_model: bool = True,
    ) -> Rendered:
        """Serialize ``graph``.

        ``include_params`` is honored by views that show device params. ``include_body`` (default
        ``False``) adds each MOSFET's ``BULK`` terminal back into the connection lists — off by
        default because the body tie rarely affects topology and just clutters the description; the
        lossless round-trip lives in :class:`~spicexplorer_circuitgraph.contract.CircuitGraphDoc`.
        ``include_spice_model`` (default ``True``) shows the foundry model name; pass ``False`` for
        an NDA-safe view that omits it by construction. A strategy
        that adds keyword arguments in future should accept ``**_`` for forward compatibility.
        """


_REGISTRY: dict[str, Serializer] = {}


def register(cls: type[Serializer]) -> type[Serializer]:
    """Class decorator: instantiate and register a strategy under its ``name``.

    Re-registering the *same* class (e.g. an ``importlib.reload`` in a notebook) replaces the entry;
    a *different* class claiming a taken name is a genuine collision and raises.
    """
    instance = cls()
    if not getattr(instance, "name", None):
        raise ValueError(f"{cls.__name__} must define a non-empty 'name'")
    if getattr(instance, "kind", None) not in ("json", "text"):
        raise ValueError(f"{cls.__name__} must set kind to 'json' or 'text'")
    existing = _REGISTRY.get(instance.name)
    if existing is not None and type(existing).__qualname__ != cls.__qualname__:
        raise ValueError(f"duplicate serializer name {instance.name!r} ({cls.__qualname__})")
    _REGISTRY[instance.name] = instance
    return cls


def unregister(name: str) -> None:
    """Remove a strategy from the registry (no-op if absent). For teardown / live re-registration."""
    _REGISTRY.pop(name, None)


def get_strategy(name: str) -> Serializer:
    """Look up a registered strategy by name (raises ``KeyError`` with the known names)."""
    try:
        return _REGISTRY[name]
    except KeyError:
        raise KeyError(f"unknown serializer {name!r}; registered: {list_strategies()}") from None


def list_strategies() -> list[str]:
    """Names of all registered strategies, sorted."""
    return sorted(_REGISTRY)


def all_strategies() -> list[Serializer]:
    """All registered strategy instances, in name order."""
    return [_REGISTRY[name] for name in list_strategies()]


def serialize(
    graph: CircuitGraph,
    strategy: str,
    *,
    include_params: bool = False,
    include_body: bool = False,
    include_spice_model: bool = True,
) -> Any:
    """Render ``graph`` through the named ``strategy``.

    Returns ``Any`` because the concrete shape (a JSON ``dict`` or a text ``str``) is selected by a
    runtime strategy name — the caller knows which it asked for. Each strategy's ``render`` is itself
    precisely typed as :data:`Rendered`. ``include_body`` (default ``False``) keeps MOSFET ``BULK``
    terminals out of the description; pass ``True`` to include them. ``include_spice_model`` (default
    ``True``) shows the foundry model name; ``include_params=False, include_spice_model=False`` is the
    NDA-safe projection for a cloud-LLM payload.
    """
    return get_strategy(strategy).render(
        graph,
        include_params=include_params,
        include_body=include_body,
        include_spice_model=include_spice_model,
    )
