"""The **save list**: a small YAML file that decides which signals a deck writes to its rawfile.

A deck that says ``.save all`` (or says nothing, which for many benches amounts to the same
thing) asks the simulator to store *every* node and branch it knows about. On a flat testbench
that is a few hundred vectors; on a parasitic-extracted netlist it is tens of thousands, and one
transient rawfile can run to gigabytes. Nothing downstream reads more than a handful of those
vectors — the scorecard measures a fixed set — so the storage is pure waste.

This module is the fix, and it is deliberately a **text transform, not a simulator feature**:

.. code-block:: yaml

    # save.yaml — signals to keep. Strings pass through to ngspice verbatim, wildcards included.
    version: 1
    default: [v(out)]                 # used when nothing more specific matches
    tran:    [v(out), i(vsup)]        # per analysis kind: op | dc | ac | tran | noise
    ac:      [v(out), v(fb)]
    benches:                          # per bench/label; wins over the analysis kind
      loop_ac: [v(out), v(fb), v(x.*)]
    # all: true                       # the explicit opt-in to "save everything"

:func:`apply_save_list_to_deck` **OVERRIDES** — it strips every ``.save`` / ``.probe`` card and
every ``save`` command inside a ``.control`` block, then emits the resolved list. It is never a
merge: a deck cannot quietly re-add a signal the list left out, and a list is therefore a
complete, reviewable statement of what a run costs on disk. When no entry applies (no bench
entry, no entry for the deck's analysis kind, no ``default``) the deck is returned **byte
identical** — an incomplete list degrades to today's behaviour rather than to an empty rawfile.

Both forms are emitted when the deck has a ``.control`` block: the ``.save`` card in the netlist
section *and* a ``save`` command as the first line inside ``.control`` (before the analysis
command, which is where ngspice requires it). Asking twice for the same set is harmless; asking
in only one of the two places is not reliably honoured across deck styles.

Layering: core, stdlib only (``yaml``, a core dependency, is imported lazily inside
:func:`load_save_list`, so importing this module does not import it). Nothing here knows
what a design, a PDK or a metric is.
"""

from __future__ import annotations

import dataclasses
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

__all__ = [
    "ANALYSIS_KINDS",
    "SaveList",
    "apply_save_list_to_deck",
    "deck_analyses",
    "load_save_list",
]

#: The analysis kinds a save list may key on, in emission order. Closed on purpose: a typo
#: (``transient``) fails at load time with its fix, not at read-the-rawfile time.
ANALYSIS_KINDS: tuple[str, ...] = ("op", "dc", "ac", "tran", "noise")

#: The single signal that means "everything" — ngspice's own spelling.
ALL = "all"

_TOP_KEYS = ("version", "all", "default", "benches", *ANALYSIS_KINDS)
_FIX = (
    "a save list is `{version, all, default, benches, " + ", ".join(ANALYSIS_KINDS) + "}`; "
    "each signal list is one or more non-blank strings, e.g. `tran: [v(out), i(vsup)]`"
)

_SAVE_CARD_RE = re.compile(r"^\s*\.(?:save|probe)\b", re.IGNORECASE)
_SAVE_CMD_RE = re.compile(r"^\s*(?:save|probe)\b", re.IGNORECASE)
_CONTROL_RE = re.compile(r"^\s*\.control\b", re.IGNORECASE)
_ENDC_RE = re.compile(r"^\s*\.endc\b", re.IGNORECASE)
_END_RE = re.compile(r"^\s*\.end\s*$", re.IGNORECASE)
_COMMENT_RE = re.compile(r"^\s*[*;]")
# A body card (`.tran …`) and a control command (`tran …`) name the same analysis; `op`/`dc`
# take no mandatory argument, so the word alone must match.
_BODY_KIND_RE = re.compile(rf"^\s*\.({'|'.join(ANALYSIS_KINDS)})\b", re.IGNORECASE)
_CTRL_KIND_RE = re.compile(rf"^\s*({'|'.join(ANALYSIS_KINDS)})\b", re.IGNORECASE)


def _bad(where: str, what: str, fix: str = _FIX) -> ValueError:
    return ValueError(f"{where}: {what}\n    FIX: {fix}")


def _signals(raw: Any, where: str, at: str) -> tuple[str, ...]:
    """One validated signal list. Empty is refused: dropping the key is how you say nothing."""
    if not isinstance(raw, (list, tuple)):
        raise _bad(where, f"{at} must be a list of signal names (got {raw!r})")
    if not raw:
        raise _bad(
            where,
            f"{at} is empty",
            "name at least one signal, or DROP the key — an empty list would mean "
            "'strip the deck's saves and put nothing back', which is never what a bench wants",
        )
    out: list[str] = []
    for s in raw:
        if not isinstance(s, str) or not s.strip():
            raise _bad(where, f"{at} contains {s!r}, which is not a non-blank string")
        if s.strip() not in out:
            out.append(s.strip())
    return tuple(out)


@dataclasses.dataclass(frozen=True)
class SaveList:
    """A parsed save list. Build it with :meth:`from_mapping` or :func:`load_save_list`.

    ``all=True`` is the explicit opt-in to a full rawfile and is mutually exclusive with any
    signal list — "save everything AND these three" is a contradiction worth failing on.
    """

    all: bool = False
    default: tuple[str, ...] = ()
    analyses: Mapping[str, tuple[str, ...]] = dataclasses.field(default_factory=dict)
    benches: Mapping[str, tuple[str, ...]] = dataclasses.field(default_factory=dict)
    version: int = 1

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any], where: str = "save list") -> SaveList:
        if not isinstance(raw, Mapping):
            raise _bad(where, f"a save list is a map (got {type(raw).__name__})")
        unknown = sorted(set(raw) - set(_TOP_KEYS))
        if unknown:
            raise _bad(where, f"unknown key(s) {unknown}")
        version = raw.get("version", 1)
        if not isinstance(version, int) or isinstance(version, bool) or version != 1:
            raise _bad(where, f"version must be 1 (got {version!r})", "version: 1")
        want_all = raw.get("all", False)
        if not isinstance(want_all, bool):
            raise _bad(where, f"all must be true|false (got {want_all!r})", "all: true")
        analyses = {k: _signals(raw[k], where, k) for k in ANALYSIS_KINDS if raw.get(k) is not None}
        default = (
            _signals(raw["default"], where, "default") if raw.get("default") is not None else ()
        )
        benches_raw = raw.get("benches") or {}
        if not isinstance(benches_raw, Mapping):
            raise _bad(
                where, f"benches must be a map of bench name -> signals (got {benches_raw!r})"
            )
        benches = {str(k): _signals(v, where, f"benches[{k}]") for k, v in benches_raw.items()}
        if want_all and (analyses or default or benches):
            raise _bad(
                where,
                "all: true is set alongside signal list(s) "
                f"{sorted([*analyses, *(['default'] if default else []), *benches])}",
                "`all: true` saves everything — drop it, or drop the lists; a save list is an "
                "override, so the two cannot both be in force",
            )
        return cls(
            all=want_all,
            default=default,
            analyses=analyses,
            benches=benches,
            version=version,
        )

    def resolve(
        self, bench: str | None = None, kinds: Iterable[str] = ()
    ) -> tuple[str, ...] | None:
        """The signals for one deck, or ``None`` when this list says nothing about it.

        Precedence: ``all`` > the bench's own entry > the union of the deck's analysis kinds
        (in :data:`ANALYSIS_KINDS` order) > ``default``.
        """
        if self.all:
            return (ALL,)
        if bench and bench in self.benches:
            return self.benches[bench]
        wanted = {k for k in kinds}
        merged: list[str] = []
        for kind in ANALYSIS_KINDS:
            if kind in wanted:
                for s in self.analyses.get(kind, ()):
                    if s not in merged:
                        merged.append(s)
        if merged:
            return tuple(merged)
        return self.default or None


def load_save_list(path: str | Path) -> SaveList:
    """Read a save-list YAML file. ``yaml`` is imported here, not at module import."""
    import yaml  # local: keeps `import spicexplorer_core.spice_engine` free of the YAML parser

    p = Path(path)
    raw = yaml.safe_load(p.read_text()) or {}
    return SaveList.from_mapping(raw, where=str(p))


def deck_analyses(deck: str) -> tuple[str, ...]:
    """The analysis kinds a deck runs, in :data:`ANALYSIS_KINDS` order.

    Reads BOTH the netlist body's ``.tran``/``.ac``/… cards and the commands inside a
    ``.control`` block (where an interactive deck actually names its analysis). Comment lines
    are ignored, and a control command is only recognised at the start of a line, so a device
    named ``vtran`` or a ``let`` expression mentioning ``ac`` cannot fake one.
    """
    found: set[str] = set()
    in_control = False
    for ln in deck.splitlines():
        if _COMMENT_RE.match(ln):
            continue
        if _CONTROL_RE.match(ln):
            in_control = True
            continue
        if _ENDC_RE.match(ln):
            in_control = False
            continue
        m = _CTRL_KIND_RE.match(ln) if in_control else _BODY_KIND_RE.match(ln)
        if m:
            found.add(m.group(1).lower())
    return tuple(k for k in ANALYSIS_KINDS if k in found)


def apply_save_list_to_deck(
    deck: str, save_list: SaveList | None, *, bench: str | None = None
) -> str:
    """Rewrite ``deck`` so its saved signals are exactly what ``save_list`` names.

    Returns the deck **unchanged** when ``save_list`` is ``None`` or resolves to nothing for
    this deck — the "flag absent = behaviour unchanged" contract, checked byte-for-byte.

    Otherwise: every ``.save``/``.probe`` card and every ``save``/``probe`` command inside a
    ``.control`` block is removed, then the resolved list is emitted as a ``.save`` card (before
    the first ``.control``, else before the final ``.end``) and — when the deck has a
    ``.control`` block — as a ``save`` command on its first line, ahead of the analysis command.
    Idempotent: applying the same list twice is a no-op.

    :param bench: the bench/label name used for the ``benches:`` lookup.
    """
    if save_list is None:
        return deck
    signals = save_list.resolve(bench=bench, kinds=deck_analyses(deck))
    if not signals:
        return deck
    joined = " ".join(signals)

    kept: list[str] = []
    in_control = False
    for ln in deck.splitlines():
        if _CONTROL_RE.match(ln):
            in_control = True
        elif _ENDC_RE.match(ln):
            in_control = False
        elif _COMMENT_RE.match(ln):
            pass
        elif _SAVE_CMD_RE.match(ln) if in_control else _SAVE_CARD_RE.match(ln):
            continue
        kept.append(ln)

    at = next((i for i, ln in enumerate(kept) if _CONTROL_RE.match(ln)), None)
    if at is None:
        at = next((i for i in range(len(kept) - 1, -1, -1) if _END_RE.match(kept[i])), len(kept))
        out = kept[:at] + [f".save {joined}"] + kept[at:]
    else:
        out = kept[:at] + [f".save {joined}", kept[at], f"save {joined}"] + kept[at + 1 :]
    return "\n".join(out) + ("\n" if deck.endswith("\n") else "")
