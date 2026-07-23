"""Symbol resolution for porting: xschem-faithful search behavior.

xschem resolves a symbol reference against each library search path, and — unlike the strict
:class:`~spicexplorer_netlist2xschem.sym_library.SymLibrary` join — a schematic moved out of
its original tree still opens because the *basename* is found next to the ``.sch`` or on the
path. Porting must reproduce that: corpus files reference siblings with their original
directory prefix (``ccia-02-…/transmission_gate_pair.sym``).
"""

from __future__ import annotations

from pathlib import Path

from ..sym_library import Symbol, SymLibrary, default_search_paths

__all__ = ["PortingSymLibrary", "symlib_for_source"]


class PortingSymLibrary(SymLibrary):
    """A :class:`SymLibrary` that additionally resolves a symref by its basename."""

    def resolve(self, symref: str) -> Path | None:
        found = super().resolve(symref)
        if found is not None:
            return found
        base = symref.rsplit("/", 1)[-1]
        if base != symref:
            return super().resolve(base)
        return None

    def load(self, symref: str) -> Symbol | None:  # cache under the full symref
        return super().load(symref)


def symlib_for_source(source: Path) -> PortingSymLibrary:
    """A library rooted at the source file's directory, then the vendored trees.

    The source's *grandparent* is searched too: corpus drawings reference sibling-project
    symbols relative to the drawings root (``ccia-01-…/ideal-amp-fully-diff.sym``). Each
    root's ``devices/`` subdir is appended as well, so bare generic references
    (``ipin.sym``) resolve the way xschem's default library path does.
    """
    roots = [source.parent, source.parent.parent, *default_search_paths()]
    extra = [r / "devices" for r in roots if (r / "devices").is_dir()]
    return PortingSymLibrary(search_paths=roots + extra)
