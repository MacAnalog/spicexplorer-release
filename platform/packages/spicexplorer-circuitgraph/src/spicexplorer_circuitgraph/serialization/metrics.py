"""Comparative harness: render a graph through every strategy and capture deterministic metrics.

The metrics are a deterministic proxy for downstream LLM utility — token budget (cheaper is better,
all else equal) and coverage (does the view actually name every component/net?). The real
"which representation does the LLM reason about best?" judgement plugs into downstream
role-detection accuracy experiments; this harness produces the comparable, reproducible
numbers those experiments rank against.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .base import Serializer, all_strategies

if TYPE_CHECKING:
    from ..graph import CircuitGraph

# A SPICE net/component name is word chars plus the symbols nets may contain (e.g. ``vin+``,
# ``vin-``, ``vdd!``). Tokenizing on this and testing *set membership* avoids the substring
# false-positives of ``name in text`` (``net1`` matching inside ``net12``; ``0`` inside ``R10``).
_NAME_TOKEN = re.compile(r"[\w!+-]+")


def _name_tokens(text: str) -> set[str]:
    return set(_NAME_TOKEN.findall(text))


@dataclass(frozen=True)
class StrategyMetrics:
    """Deterministic metrics for one strategy on one graph."""

    name: str
    kind: str
    char_count: int
    token_estimate: int  # ~chars/4 (rough GPT-style heuristic)
    component_coverage: float  # fraction of component names present in the rendered output
    net_coverage: float  # fraction of net names present in the rendered output


def _as_text(rendered: dict | str) -> str:
    return rendered if isinstance(rendered, str) else json.dumps(rendered, sort_keys=True)


def evaluate_strategy(
    graph: CircuitGraph, serializer: Serializer, *, include_params: bool = False
) -> StrategyMetrics:
    """Metrics for a single strategy. Coverage is token-set membership (deterministic)."""
    text = _as_text(serializer.render(graph, include_params=include_params))
    tokens = _name_tokens(text)
    comps = [c.name for c in graph.get_components(sort=False)]
    nets = [n.name for n in graph.get_nets(sort=False)]
    comp_cov = sum(1 for name in comps if name in tokens) / len(comps) if comps else 1.0
    net_cov = sum(1 for name in nets if name in tokens) / len(nets) if nets else 1.0
    return StrategyMetrics(
        name=serializer.name,
        kind=serializer.kind,
        char_count=len(text),
        token_estimate=len(text) // 4,
        component_coverage=round(comp_cov, 4),
        net_coverage=round(net_cov, 4),
    )


def evaluate_strategies(
    graph: CircuitGraph, *, include_params: bool = False
) -> list[StrategyMetrics]:
    """Metrics for every registered strategy, in name order (auto-includes newly-registered ones)."""
    return [evaluate_strategy(graph, s, include_params=include_params) for s in all_strategies()]
