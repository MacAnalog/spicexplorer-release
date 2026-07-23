"""PVT corner primitives — process/voltage/temperature, made first-class.

These dataclasses make corners actually drive the SPICE simulation. They are
deliberately PDK-AGNOSTIC: core never interprets ``lib_file``/``section`` strings —
the spice engine emits them verbatim.

Moved out of the optimizer's DSL module (``core/domains.py``) so the spice engine
can reference ``Corner`` without importing the optimizer (it previously did so via
a TYPE_CHECKING import to dodge a cycle). Re-exported from
``spicexplorer.core.domains`` for backward compatibility.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from spicexplorer_core.eng import parse_value

# Logger name preserved from the original ``core/domains.py`` so existing log
# capture / assertions keyed on this name keep working.
logger = logging.getLogger("spicexplorer.designer_tools.domains")


# ---------- Multi-corner vocabulary ----------
# Canonical names + author-facing aliases for the two Phase-2 knobs. These live in
# CORE (data-only, no numpy) so YAML validation happens at load time; the numeric
# aggregation implementations live in the optimizer layer, keyed by the CANONICAL
# names below.

PVT_MODES = ("single", "multi")

#: canonical strategy -> what it does to the per-corner total scores
#:   sum  — add them ("add"):        favors average-case, can mask one failing corner
#:   mean — average them ("average"): like sum but budget-of-corners invariant
#:   min  — worst case ("worst_case"): classic PVT sign-off; robust but pessimistic
SCORE_AGGREGATION_STRATEGIES = ("sum", "mean", "min")

_SCORE_AGGREGATION_ALIASES = {
    "sum": "sum", "add": "sum", "total": "sum",
    "mean": "mean", "avg": "mean", "average": "mean",
    "min": "min", "worst": "min", "worst_case": "min", "worst-case": "min", "worstcase": "min",
}


def normalize_score_aggregation(name: str) -> str:
    """Map an author-facing aggregation alias to its canonical name; raise on unknown."""
    canonical = _SCORE_AGGREGATION_ALIASES.get(str(name).strip().lower())
    if canonical is None:
        raise ValueError(
            f"Unknown pvt.score_aggregation '{name}'. Use one of "
            f"{sorted(set(_SCORE_AGGREGATION_ALIASES))} "
            f"(canonical: {list(SCORE_AGGREGATION_STRATEGIES)})."
        )
    return canonical


def _normalize_pvt_block(proj: dict) -> None:
    """Desugar the raw `pvt:` YAML block in-place into the canonical `PVTConfig` shape.

    The author-facing YAML allows convenient sugar that does NOT map 1:1 onto the
    dataclasses; this expands it before dacite ever sees it:

      • `process_bundles:` (reusable named include lists) are inlined into each
        corner's `model_includes`, then dropped — they are sugar, not a retained field.
      • a corner's `process: <bundle>` reference is replaced by the bundle's
        `model_includes` (inline `model_includes:` is kept as-is for one-off corners).
      • a singular `supply: {node, value}` is widened to `supplies: [...]` so the schema
        extends to multi-rail designs without breaking.
      • numeric env fields (`temp`, supply `value`, `params` values) are coerced via
        `parse_value`, so engineering strings ("1V2" style "1.2", "900m") and ints work.

    No-op if `proj` has no `pvt` key. Raises ValueError on a dangling `process`
    bundle reference, on a corner carrying BOTH `process` and inline `model_includes`,
    or on a corner carrying BOTH a singular `supply` and a plural `supplies` — each
    ambiguity is refused rather than silently resolved.
    """
    pvt = proj.get("pvt")
    if not isinstance(pvt, dict):
        return

    bundles: Dict[str, list] = pvt.pop("process_bundles", None) or {}

    def _coerce_includes(raw_list) -> list:
        out = []
        for inc in raw_list or []:
            out.append({"lib_file": str(inc["lib_file"]), "section": str(inc["section"])})
        return out

    corners = pvt.get("corners") or []
    for corner in corners:
        # process bundle reference  →  concrete model_includes
        bundle_ref = corner.pop("process", None)
        if bundle_ref is not None and "model_includes" in corner:
            # Ambiguous: both an inline include list AND a process-bundle reference. Don't silently
            # drop `process` (BUG-B32) — refuse so the author picks one.
            raise ValueError(
                f"PVT corner '{corner.get('name', '?')}' specifies BOTH 'process: {bundle_ref}' and "
                f"an inline 'model_includes' — use one or the other."
            )
        if bundle_ref is not None and "model_includes" not in corner:
            if bundle_ref not in bundles:
                raise ValueError(
                    f"PVT corner '{corner.get('name', '?')}' references unknown process "
                    f"bundle '{bundle_ref}'. Defined bundles: {sorted(bundles)}."
                )
            corner["model_includes"] = _coerce_includes(bundles[bundle_ref])
        elif "model_includes" in corner:
            corner["model_includes"] = _coerce_includes(corner["model_includes"])

        # singular `supply` sugar  →  `supplies: [...]`
        single_supply = corner.pop("supply", None)
        if single_supply is not None and "supplies" in corner:
            # Ambiguous: both the singular sugar AND the plural canonical form. Don't
            # silently drop `supply` (mirrors the `process`/`model_includes` guard
            # above) — refuse so the author folds it into `supplies`.
            raise ValueError(
                f"PVT corner '{corner.get('name', '?')}' specifies BOTH a singular "
                f"'supply' and a plural 'supplies' — use one or the other "
                f"(fold the single rail into 'supplies')."
            )
        if single_supply is not None:
            corner["supplies"] = [single_supply]

        # numeric coercion (env)
        if "temp" in corner:
            corner["temp"] = float(parse_value(corner["temp"]))
        for s in corner.get("supplies", []) or []:
            if "value" in s:
                s["value"] = float(parse_value(s["value"]))
        if corner.get("params"):
            corner["params"] = {k: float(parse_value(v)) for k, v in corner["params"].items()}


# ---------- PVT Corner System ----------
# These dataclasses make process/voltage/temperature corners first-class so they
# actually drive the SPICE simulation. They are deliberately PDK-AGNOSTIC: core
# never interprets `lib_file`/`section` strings — the spice engine emits them verbatim.


@dataclass
class ModelInclude:
    """One generic model-library include: an opaque (file, section) pair.

    The spice engine emits this as `.lib <lib_file> <section>` (ngspice); core never
    enumerates valid files or sections. PDK-specific tokens (e.g. `cornerMOSlv.lib`,
    `mos_tt`) live only in the YAML, never in core.
    """
    lib_file: str
    section: str


@dataclass
class SupplyOverride:
    """A supply-rail override: the `.param` name to set and its value (volts)."""
    node: str
    value: float


@dataclass
class Corner:
    """A fully-resolved PVT corner: process model includes + environment.

    `model_includes` is always the expanded, ordered include list — a YAML
    `process: <bundle>` reference is resolved into this list at load time (see
    `_normalize_pvt_block`), so core only ever sees concrete includes.
    """
    name: str
    model_includes: List[ModelInclude] = field(default_factory=list)
    temp: float = 27.0
    supplies: List[SupplyOverride] = field(default_factory=list)
    params: Dict[str, float] = field(default_factory=dict)
    # Extra simulator `.options` cards (e.g. {"seed": 7} → `.options seed=7` for a
    # Monte Carlo sample's RNG). Engine-neutral names; each backend's apply_corner
    # decides the concrete emission.
    options: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class PVTConfig:
    """Top-level PVT configuration: a set of named corners + how they drive the run.

    Two modes:
      • ``mode: single`` (default) — the optimizer runs against the one
        ``active_corner``.
      • ``mode: multi`` — every trial runs the full
        {enabled testbenches} × {enabled corners} cross-product; the per-corner
        scores are collapsed into one scalar by ``score_aggregation``
        (``sum``/"add", ``mean``/"average", or ``min``/"worst_case").
    """
    active_corner: str
    corners: List[Corner] = field(default_factory=list)
    model_lib_root: Optional[str] = None
    mode: str = "single"
    score_aggregation: str = "mean"

    def __post_init__(self):
        # Reject duplicate corner names: `get()`/`get_active()` return the FIRST
        # match, so a duplicate silently shadows the later corner (and the UI's
        # corner picker would key React rows on a non-unique name). Fail loudly,
        # mirroring the dut_param uniqueness check in Project_Setup.__post_init__.
        names = [c.name for c in self.corners]
        dupes = sorted({n for n in names if names.count(n) > 1})
        if dupes:
            raise ValueError(
                f"Duplicate PVT corner name(s) {dupes}. "
                "Each PVT corner must have a unique name."
            )

        self.mode = str(self.mode).strip().lower()
        if self.mode not in PVT_MODES:
            raise ValueError(
                f"Unknown pvt.mode '{self.mode}'. Use one of {list(PVT_MODES)}."
            )
        # Normalize the aggregation alias eagerly so every consumer (optimizer,
        # API summary, wizard round-trip) only ever sees a canonical name.
        self.score_aggregation = normalize_score_aggregation(self.score_aggregation)

        if self.mode == "multi":
            self._validate_multi_corner_config()

    def _validate_multi_corner_config(self) -> None:
        """Fail-fast checks that only matter when every enabled corner runs per trial.

        1. At least one corner must be enabled — an empty sweep is a config error.
        2. Corner names must survive the checkpoint key flattening: fit_summary keys
           become ``<corner>::<spec>`` and are later flattened into dotted CSV/JSON
           columns, so ``::`` and ``.`` inside a corner name would corrupt parsing.
        3. Enabled corners must be SYMMETRIC — override the same library files,
           supply nodes, and extra params. Corners are applied to the SAME netlist
           editor back-to-back each trial, and `apply_corner` only replaces what the
           incoming corner itself references: a supply/param/lib present in corner A
           but absent from corner B would silently LEAK A's value into B's runs.
        """
        enabled = self.enabled_corners()
        if not enabled:
            raise ValueError(
                "pvt.mode is 'multi' but no corner is enabled — enable at least one "
                "corner or switch to mode: single."
            )

        # active_corner is still load-bearing in multi mode (single-corner manual
        # sims, UI corner picks, and the multi→single collapse all resolve it via
        # get_active()). In single mode it fails fast when the optimizer applies it,
        # but a multi run never calls get_active(), so an undefined active_corner
        # would lurk until a manual sim. Validate it at load instead.
        if self.get(self.active_corner) is None:
            raise ValueError(
                f"pvt.active_corner '{self.active_corner}' is not among the defined "
                f"corners {[c.name for c in self.corners]} — it is still used by "
                "single-corner manual sims / UI corner picks in multi mode."
            )

        # '.'/'::': corrupt the checkpoint key flattening; '/', '\\': corner names
        # become run-folder labels (run_<n>_<tb>__<corner>) in multi mode, and a
        # path separator silently nests the run dirs one level deeper per sim.
        bad_chars = ("::", ".", "/", "\\")
        bad_names = sorted(c.name for c in self.corners if any(ch in c.name for ch in bad_chars))
        if bad_names:
            raise ValueError(
                f"PVT corner name(s) {bad_names} contain one of {list(bad_chars)}, which "
                "corrupt the multi-corner checkpoint keys ('<corner>::<spec>' columns) "
                "or the per-corner run-folder labels. Rename the corner(s) (e.g. 'tt_27C_1V5')."
            )

        def _footprint(c: "Corner"):
            return (
                sorted({inc.lib_file.rsplit("/", 1)[-1] for inc in c.model_includes}),
                sorted({s.node for s in c.supplies}),
                sorted(c.params),
            )

        ref_name, ref_fp = enabled[0].name, _footprint(enabled[0])
        for c in enabled[1:]:
            fp = _footprint(c)
            if fp != ref_fp:
                raise ValueError(
                    f"pvt.mode 'multi' requires SYMMETRIC enabled corners, but corner "
                    f"'{c.name}' overrides (libs={fp[0]}, supplies={fp[1]}, params={fp[2]}) "
                    f"while corner '{ref_name}' overrides (libs={ref_fp[0]}, "
                    f"supplies={ref_fp[1]}, params={ref_fp[2]}). Corners are re-applied to "
                    "the same netlist per trial, so an override present in one corner but "
                    "missing from another silently leaks across corners — give every "
                    "enabled corner the same set of libs/supply nodes/param keys."
                )

    def get(self, name: str) -> Optional["Corner"]:
        for c in self.corners:
            if c.name == name:
                return c
        return None

    def get_active(self) -> "Corner":
        corner = self.get(self.active_corner)
        if corner is None:
            available = [c.name for c in self.corners]
            raise ValueError(
                f"active_corner '{self.active_corner}' not found among defined "
                f"corners {available}."
            )
        if not corner.enabled:
            # The author explicitly disabled this corner yet left it active — warn rather than
            # silently simulate against a corner excluded from enabled_corners() (BUG-B34).
            logger.warning(
                f"active_corner '{self.active_corner}' is marked enabled: false but is the "
                f"active corner — it will still drive the simulation."
            )
        return corner

    def enabled_corners(self) -> List["Corner"]:
        return [c for c in self.corners if c.enabled]

    def is_multi(self) -> bool:
        return self.mode == "multi"

    def corners_to_run(self) -> List["Corner"]:
        """The corners one evaluation must simulate: every enabled corner in multi
        mode, else just the active corner (single-corner behavior)."""
        if self.is_multi():
            enabled = self.enabled_corners()
            if not enabled:
                # Defensive re-check: `enabled` flags may have been mutated after
                # __post_init__ (e.g. by an API override).
                raise ValueError(
                    "pvt.mode is 'multi' but no corner is enabled — nothing to simulate."
                )
            return enabled
        return [self.get_active()]


# ---------- Monte Carlo sample corners ----------
#
# A Monte Carlo "sample" is just a corner: the base corner's process libs swapped
# to their statistical siblings (e.g. IHP's `mos_tt` → `mos_tt_mismatch`, whose
# model cards wrap device params in seed-driven agauss() draws) plus a unique RNG
# seed via `.options seed=<n>` (Corner.options). The existing multi-corner
# fan-out then runs/labels each sample like any corner (`run_<n>_<tb>__mc<i>`),
# so checkpoints, artifact naming, and the viewer need nothing new.

def _lib_sections(lib_path: str) -> set:
    """The section names a SPICE library file defines (`.lib <name>` single-token lines).

    Two-token `.lib <file> <section>` lines are include-REFERENCES, not definitions,
    and are excluded by the single-token match.
    """
    import re as _re

    sections: set = set()
    try:
        with open(lib_path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = _re.match(r"^\s*\.lib\s+(\S+)\s*$", line, _re.IGNORECASE)
                if m:
                    sections.add(m.group(1))
    except OSError:
        pass
    return sections


def _resolve_lib_file(lib_file: str, search_roots: List[str]) -> Optional[str]:
    """Find a corner's ``lib_file`` on disk: as-given, else by basename under the roots."""
    import os

    if os.path.isfile(lib_file):
        return lib_file
    basename = os.path.basename(lib_file)
    for root in search_roots:
        if not root or not os.path.isdir(root):
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            if basename in filenames:
                return os.path.join(dirpath, basename)
    return None


def monte_carlo_corners(
    base: "Corner",
    samples: int,
    *,
    seed0: int = 1,
    mismatch_suffix: str = "_mismatch",
    lib_search_roots: Optional[List[str]] = None,
) -> List["Corner"]:
    """Clone ``base`` into ``mc1..mcN`` statistical sample corners.

    Every model include whose library defines a ``<section><mismatch_suffix>``
    sibling is swapped to it; each sample gets ``options["seed"] = seed0 + i`` so
    the library's agauss() draws differ per sample but stay reproducible per seed.
    Raises when NO include has a statistical sibling (the PDK ships none, or the
    lib files can't be found under ``lib_search_roots``) — a silent "Monte Carlo"
    that re-runs the identical deterministic deck N times would be a lie.
    """
    import os

    if samples < 2:
        raise ValueError(f"monte_carlo needs at least 2 samples (got {samples})")
    roots = lib_search_roots if lib_search_roots is not None else [os.environ.get("PDK_ROOT", "")]

    swapped_includes: List[ModelInclude] = []
    swapped_any = False
    for inc in base.model_includes:
        target = f"{inc.section}{mismatch_suffix}"
        path = _resolve_lib_file(inc.lib_file, roots)
        if path is not None and target in _lib_sections(path):
            swapped_includes.append(ModelInclude(lib_file=inc.lib_file, section=target))
            swapped_any = True
        else:
            swapped_includes.append(inc)
    if not swapped_any:
        raise ValueError(
            f"Monte Carlo: no '<section>{mismatch_suffix}' statistical sections found for "
            f"corner '{base.name}' (includes: "
            f"{[(i.lib_file, i.section) for i in base.model_includes]}; search roots: {roots}). "
            "The bound PDK ships no mismatch sections, or its model libraries were not found."
        )

    return [
        Corner(
            name=f"mc{i}",
            model_includes=list(swapped_includes),
            temp=base.temp,
            supplies=list(base.supplies),
            params=dict(base.params),
            options={**base.options, "seed": seed0 + i - 1},
            enabled=True,
        )
        for i in range(1, samples + 1)
    ]
