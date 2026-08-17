"""spicexplorer-layout — parameterized layout generation as a library.

The **generator contract** (:mod:`gen`): a layout of record is a Python module exposing

    @dataclass(frozen=True) class LayoutParams: ...   # the optimizer knobs, with defaults
    def build(params: LayoutParams, sizing: dict | None = None) -> gdsfactory.Component

Everything else derives from that: :func:`load_generator` imports such a module from a
path, :class:`GdsBuilder` binds it into a ``params → GDS path`` callable (what
``spicexplorer_signoff.run_flow`` and an optimizer trial consume), :func:`build_gds`
writes the GDS deterministically and reports bbox / area / sha256, :func:`render_png`
draws it headless with the PDK layer colours. :mod:`patterns` holds matching-pattern
helpers (mirror pair, interdigitation / common-centroid orders, dummies) that generators
compose. :mod:`review` is the **layout-review DSL** (``layout-review/1``: findings with
geometry anchors, severity, effect, fix→knob) and its **annotated render**
(:func:`annotate` / :func:`annotate_crops`) — the reviewer's machine-readable + visual output.
:mod:`iterations` is the designer's **audit trail**: :func:`snapshot` per verification round
(generator copy + GDS + render + verdicts + "what it fixed" note → ``iterations.yaml``),
:func:`diff_png` before|after pictures with changed regions and DRC hits fixed/still/new,
:func:`iterations_table_md` for the report.
"""

from .gen import (
    GdsBuild,
    GdsBuilder,
    Generator,
    build_gds,
    load_generator,
    params_from_json,
    params_schema,
    render_png,
)
from .iterations import IterationEntry, diff_png, iterations_table_md, snapshot
from .patterns import common_centroid_order, interdigitate_order
from .review import Finding, Review, annotate, annotate_crops, dump_review, load_review, validate

__all__ = [
    "Finding",
    "Review",
    "annotate",
    "annotate_crops",
    "dump_review",
    "load_review",
    "validate",
    "IterationEntry",
    "diff_png",
    "iterations_table_md",
    "snapshot",
    "GdsBuild",
    "GdsBuilder",
    "Generator",
    "build_gds",
    "common_centroid_order",
    "interdigitate_order",
    "load_generator",
    "params_from_json",
    "params_schema",
    "render_png",
]
