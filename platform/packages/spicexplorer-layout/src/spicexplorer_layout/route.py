"""A generator's per-net obstacle map and column allocator — no gdsfactory, so it is testable.

Two shorts a generator can draw that verification will not catch for you:

* **A stub through a neighbour's bar.** Reaching a terminal's channel track means a column plus a
  short stub at the terminal's y to bridge the x-shift. Two overlapping same-layer shapes merge
  into one legal polygon, so a stub that walks through a neighbour's gate bar is a short **DRC
  cannot see** — only LVS catches it, and only if some sizing point happens to produce the
  collision. A generator that is DRC- and LVS-clean at every committed sizing may still be one
  optimizer step away from it.
* **A column through drawn metal nobody registered.** An obstacle map that only knows about the
  columns the router itself allocated is blind to the plain rectangles the power path drew, and
  a column of one net merges into another. It is also blind in the other direction: refusing a
  Metal3 column because a *Metal2* rectangle is under it forces a hard-coded layer hop that has
  nothing to do with the geometry.

So the map is **layer-aware**: every vertical carries its layer, and :meth:`ObstacleMap.claim_box`
records an arbitrary drawn rectangle on a named layer, whatever drew it.

Every clearance is a rule of the process, so :class:`ObstacleMap` takes a
:class:`~spicexplorer_core.tech.RoutingRules` from the tech config and holds no literal of its
own. A generator derives its builder from this class, so the code under test is the code that
draws.

    from spicexplorer_core.tech import Tech
    from spicexplorer_layout.route import ObstacleMap

    class Builder(ObstacleMap):
        def __init__(self):
            super().__init__(Tech.builtin("ihp-sg13g2").routing_rules())
"""

from __future__ import annotations

from spicexplorer_core.tech import RoutingRules, Tech

__all__ = ["ObstacleMap"]


class ObstacleMap:
    """Everything a later stub or column must not run into, plus the column allocator."""

    def __init__(self, rules: RoutingRules | Tech | str | None = None):
        if isinstance(rules, RoutingRules):
            self.rules = rules
        else:
            self.rules = Tech.resolve(rules).routing_rules()
        #: ``[net, y0, y1, x0, x1]`` on the stub layer.
        self.stub_rows: list[list] = []
        #: ``(net, x, y0, y1, layer)``.
        self.verticals: list[tuple[str, float, float, float, str]] = []
        #: ``(layer, net, x0, y0, x1, y1)`` — any drawn rectangle a later column must not cross.
        self.boxes: list[tuple[str, str, float, float, float, float]] = []

    def snap(self, v: float) -> float:
        return self.rules.snap(v)

    # ------------------------------------------------------------------ claims ----
    def claim_stub_row(
        self, net: str, y: float, x0: float, x1: float, height: float | None = None
    ) -> None:
        """A horizontal run of ``net`` on the stub layer, centred on ``y``."""
        h = self.rules.stub_width_um if height is None else height
        self.stub_rows.append(
            [
                net,
                self.snap(y - h / 2),
                self.snap(y + h / 2),
                self.snap(min(x0, x1)),
                self.snap(max(x0, x1)),
            ]
        )

    def claim_stub_box(self, net: str, x0: float, y0: float, x1: float, y1: float) -> None:
        """A rectangle of ``net`` on the stub layer, given by its corners."""
        self.stub_rows.append(
            [
                net,
                self.snap(min(y0, y1)),
                self.snap(max(y0, y1)),
                self.snap(min(x0, x1)),
                self.snap(max(x0, x1)),
            ]
        )

    def claim_box(self, layer: str, net: str, x0: float, y0: float, x1: float, y1: float) -> None:
        """Record a drawn rectangle on ``layer`` so no foreign column may cross it."""
        self.boxes.append(
            (
                layer,
                net,
                self.snap(min(x0, x1)),
                self.snap(min(y0, y1)),
                self.snap(max(x0, x1)),
                self.snap(max(y0, y1)),
            )
        )

    def claim_vertical(self, net: str, x: float, y0: float, y1: float, layer: str = "") -> None:
        self.verticals.append(
            (
                net,
                self.snap(x),
                self.snap(min(y0, y1)),
                self.snap(max(y0, y1)),
                layer or self.rules.route_layer,
            )
        )

    def retag(self, old: str, new: str) -> None:
        """Rename a net everywhere it was claimed (two nets merged after a topology change)."""
        for r in self.stub_rows:
            if r[0] == old:
                r[0] = new
        self.boxes = [(lay, new if n == old else n, *rest) for lay, n, *rest in self.boxes]
        self.verticals = [(new if v[0] == old else v[0], *v[1:]) for v in self.verticals]

    # -------------------------------------------------------------- the checks ----
    def stub_clear(
        self,
        net: str,
        y: float,
        xa: float,
        xb: float,
        cx: float | None = None,
        cy: float | None = None,
    ) -> bool:
        """Would a stub of ``net`` at ``y`` from ``xa`` to ``xb`` touch another net's stub metal?

        ``cx``/``cy`` default to the clearance the stub and its via pad need in this process.
        """
        cx = self.rules.stub_clear_x_um if cx is None else cx
        cy = self.rules.stub_clear_y_um if cy is None else cy
        w = self.rules.stub_width_um
        lo, hi = min(xa, xb) - cx, max(xa, xb) + cx
        ylo, yhi = y - w / 2 - cy, y + w / 2 + cy
        for n, y0, y1, x0, x1 in self.stub_rows:
            if n == net or y1 < ylo or y0 > yhi or x1 < lo or x0 > hi:
                continue
            return False
        return True

    def column_free(self, net: str, x: float, lo: float, hi: float, layer: str = "") -> bool:
        """Is a vertical of ``net`` on ``layer`` over ``[lo, hi]`` clear of every foreign
        obstacle **on that layer** — other routed columns and every rectangle
        :meth:`claim_box` recorded?"""
        layer = layer or self.rules.route_layer
        pitch = self.rules.column_pitch_um
        for v in self.verticals:
            if v[4] != layer:
                continue
            dx = abs(v[1] - x)
            if dx >= pitch - 1e-6:
                continue
            if v[0] == net and dx < 1e-6:
                continue  # the net's own column on the same x is a merge, not a neighbour
            if v[3] < lo - pitch or v[2] > hi + pitch:
                continue
            # Two columns of the SAME net closer than the pad pitch are not a short, but their
            # via pads still abut and their cuts land inside the cut-spacing rule. The pitch is
            # a geometric rule, so it applies to the net's own columns too.
            return False
        pad = pitch / 2
        for lay, n, x0, y0, x1, y1 in self.boxes:
            if n == net or lay != layer:
                continue
            if x < x0 - pad + 1e-6 or x > x1 + pad - 1e-6:
                continue
            if hi < y0 - pad + 1e-6 or lo > y1 + pad - 1e-6:
                continue
            return False
        return True

    def alloc(
        self,
        net: str,
        x: float,
        y0: float,
        y1: float,
        step: float | None = None,
        tries: int = 80,
        layer: str = "",
        hint: str = "",
    ) -> float:
        """First x from ``x`` in ``step`` increments whose column over ``[y0, y1]`` is free AND
        whose stub crosses nobody.

        The search goes in the preferred direction FIRST and then the other one: a column that is
        free of foreign metal but whose stub would cross a neighbour's bar is not usable, so the
        walk has to be able to turn round instead of marching into the neighbour.

        ``hint`` names the caller's own knobs in the refusal, since which parameter widens the
        gap is a property of the generator, not of the map.
        """
        step = self.rules.column_pitch_um if step is None else step
        layer = layer or self.rules.route_layer
        lo, hi = min(y0, y1), max(y0, y1)
        for k in range(tries):
            for s in (step, -step) if k else (step,):
                xx = self.snap(x + k * s)
                if self.column_free(net, xx, lo, hi, layer) and self.stub_clear(net, y0, x, xx):
                    return xx
        raise AssertionError(
            f"no free {layer} column for {net!r} near x={x} after {tries} tries "
            f"({hint or 'widen the device or group gap'})"
        )
