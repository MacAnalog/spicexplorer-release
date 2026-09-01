"""The generator contract + the build step.

A generator module (``layout/<cell>/gen_<cell>.py`` in a block repo, or a registered
module) must expose ``LayoutParams`` (a frozen dataclass — every field is an optimizer
knob with a default; optionally a ``BOUNDS: dict[str, tuple[float, float]]`` giving the
legal range per knob) and ``build(params, sizing=None) -> gdsfactory.Component``. Sizes
LVS pins (W/L/m) come from ``sizing`` (the cell's ``design.json`` or equivalent), never
from ``LayoutParams``.
"""

from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, cast


@dataclass(frozen=True)
class Generator:
    """A loaded generator module: its ``LayoutParams`` type, ``build`` and knob bounds."""

    name: str
    module: ModuleType
    params_cls: Any  # the LayoutParams dataclass type
    bounds: dict[str, tuple[float, float]]
    source: str

    def default_params(self) -> Any:
        return self.params_cls()

    def build(self, params: Any = None, sizing: dict | None = None):
        import inspect

        params = params if params is not None else self.default_params()
        sig = inspect.signature(self.module.build)
        if sizing is not None and "sizing" in sig.parameters:
            return self.module.build(params, sizing=sizing)
        return self.module.build(params)


def load_generator(path_or_module: str | Path, name: str | None = None) -> Generator:
    """Import a generator from a file path (``gen_<cell>.py``) or a dotted module name."""
    p = Path(str(path_or_module))
    if p.suffix == ".py" and p.is_file():
        modname = name or p.stem
        spec = importlib.util.spec_from_file_location(modname, p)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        sys.modules[modname] = mod
        sys.path.insert(0, str(p.parent))
        spec.loader.exec_module(mod)
        source = str(p.resolve())
    else:
        mod = importlib.import_module(str(path_or_module))
        source = getattr(mod, "__file__", str(path_or_module)) or str(path_or_module)
    if not hasattr(mod, "LayoutParams") or not hasattr(mod, "build"):
        raise AttributeError(f"{source}: a generator must expose LayoutParams and build()")
    if not dataclasses.is_dataclass(mod.LayoutParams):
        raise TypeError(f"{source}: LayoutParams must be a dataclass")
    return Generator(
        name=name or getattr(mod, "CELL", p.stem),
        module=mod,
        params_cls=cast(Any, mod.LayoutParams),
        bounds=dict(getattr(mod, "BOUNDS", {})),
        source=source,
    )


def params_schema(gen: Generator) -> list[dict[str, Any]]:
    """[{name, default, type, lo, hi}] — what an optimizer or a UI needs to expose the knobs."""
    out = []
    for f in dataclasses.fields(gen.params_cls):
        lo, hi = gen.bounds.get(f.name, (None, None))
        default = f.default if f.default is not dataclasses.MISSING else None
        out.append(
            {
                "name": f.name,
                "default": default,
                "type": getattr(f.type, "__name__", str(f.type)),
                "lo": lo,
                "hi": hi,
            }
        )
    return out


def params_from_json(gen: Generator, text: str | dict | None) -> Any:
    """LayoutParams from a JSON string / dict of overrides (unknown keys are an error)."""
    if not text:
        return gen.default_params()
    d = json.loads(text) if isinstance(text, str) else dict(text)
    names = {f.name for f in dataclasses.fields(gen.params_cls)}
    unknown = set(d) - names
    if unknown:
        raise KeyError(f"unknown LayoutParams fields: {sorted(unknown)}")
    return gen.params_cls(**d)


@dataclass
class GdsBuild:
    gds: str
    cell: str
    params: dict[str, Any]
    bbox_um: tuple[float, float, float, float]  # left, bottom, right, top
    area_um2: float
    sha256: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def _bbox(comp) -> tuple[float, float, float, float]:
    b = comp.bbox() if callable(getattr(comp, "bbox", None)) else comp.bbox
    if hasattr(b, "left"):
        return (float(b.left), float(b.bottom), float(b.right), float(b.top))
    (x0, y0), (x1, y1) = b
    return (float(x0), float(y0), float(x1), float(y1))


def build_gds(
    gen: Generator,
    params: Any,
    out: str | Path,
    *,
    sizing: dict | None = None,
    cell: str | None = None,
) -> GdsBuild:
    """Build and write the GDS deterministically (same params → same bytes); report bbox/area/sha."""
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    comp = gen.build(params, sizing)
    if cell and getattr(comp, "name", None) != cell:
        try:
            comp.name = cell
        except Exception:
            pass
    # gdsfactory stamps a timestamp into GDS headers unless told otherwise
    try:
        comp.write_gds(str(out), with_metadata=False, timestamp=None)
    except TypeError:
        comp.write_gds(str(out))
    x0, y0, x1, y1 = _bbox(comp)
    return GdsBuild(
        gds=str(out),
        cell=getattr(comp, "name", cell or gen.name),
        params=dataclasses.asdict(cast(Any, params))
        if dataclasses.is_dataclass(params)
        else dict(params),
        bbox_um=(x0, y0, x1, y1),
        area_um2=(x1 - x0) * (y1 - y0),
        sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
    )


class GdsBuilder:
    """``params → GDS path`` callable for ``spicexplorer_signoff.run_flow`` / optimizer trials.

    Runs the generator **in a subprocess** by default (gdsfactory caches components by
    name+params inside one interpreter, and PDK activation is process-global — the two
    classic ways to rebuild yesterday's layout), writing to ``out_dir/<cell>.gds``.
    ``inproc=True`` skips the subprocess for tight loops that manage the cache themselves.
    """

    def __init__(
        self,
        gen_path: str | Path,
        out_dir: str | Path,
        *,
        cell: str | None = None,
        sizing_json: str | Path | None = None,
        inproc: bool = False,
        python: str | None = None,
    ):
        self.gen_path = str(Path(gen_path).resolve())
        self.out_dir = Path(out_dir).resolve()
        self.cell = cell
        self.sizing_json = str(sizing_json) if sizing_json else None
        self.inproc = inproc
        self.python = python or sys.executable
        self.last: GdsBuild | None = None

    def __call__(self, params: Any) -> Path:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        pdict = (
            dataclasses.asdict(cast(Any, params))
            if dataclasses.is_dataclass(params)
            else dict(params or {})
        )
        if self.inproc:
            gen = load_generator(self.gen_path)
            sizing = json.loads(Path(self.sizing_json).read_text()) if self.sizing_json else None
            out = self.out_dir / f"{self.cell or gen.name}.gds"
            self.last = build_gds(gen, gen.params_cls(**pdict), out, sizing=sizing, cell=self.cell)
            return out
        import subprocess

        # the generator side may live in another interpreter (e.g. a conda env that has
        # gdsfactory + the node PDK) — this package's src is pure-stdlib, so expose it via
        # PYTHONPATH instead of requiring an install there.
        env = dict(os.environ)
        src = str(Path(__file__).resolve().parents[1])
        env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
        cmd = [
            self.python,
            "-m",
            "spicexplorer_layout.cli",
            "build",
            self.gen_path,
            "--out-dir",
            str(self.out_dir),
            "--params",
            json.dumps(pdict),
            "--json",
        ]
        if self.cell:
            cmd += ["--cell", self.cell]
        if self.sizing_json:
            cmd += ["--sizing", self.sizing_json]
        # cwd = the (per-build) out_dir: PDK PyCells may drop scratch files in cwd
        # (ihp-gdsfactory's npn13G2 writes+removes `temp.gds`), which collides when several
        # optimizer islands / builds share the launcher's cwd.
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(self.out_dir))
        if r.returncode != 0:
            raise RuntimeError(f"generator failed ({r.returncode}):\n{r.stderr[-3000:]}")
        # the JSON record is the LAST line the CLI prints, but the generator side (gdsfactory /
        # kfactory / the PDK) may append its own stdout noise — take the last line that parses
        # as the build record rather than trusting the very last line.
        d = None
        for line in reversed(r.stdout.strip().splitlines()):
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    cand = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(cand, dict) and "gds" in cand and "bbox_um" in cand:
                    d = cand
                    break
        if d is None:
            raise RuntimeError(f"generator produced no build record on stdout:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}")
        d["bbox_um"] = tuple(d["bbox_um"])
        self.last = GdsBuild(**d)
        return Path(self.last.gds)


def pdk_lyp(pdk: str) -> Path | None:
    """Layer-properties file of an installed PDK: the single ``*.lyp`` under
    ``$PDK_ROOT/<pdk>/libs.tech/klayout/tech/`` (no per-PDK name table)."""
    root = Path(os.environ.get("PDK_ROOT", os.path.expanduser("~/local/pdks")))
    hits = sorted((root / pdk / "libs.tech" / "klayout" / "tech").glob("*.lyp"))
    return hits[0] if hits else None


def render_png(
    gds: str | Path,
    png: str | Path,
    *,
    lyp: str | Path | None = None,
    size: tuple[int, int] = (1600, 1200),
    pdk: str = "ihp-sg13g2",
) -> Path:
    """Headless render with the PDK layer colours (needs the ``klayout`` python module)."""
    import klayout.lay as klay  # optional dep

    if lyp is None:
        lyp = pdk_lyp(pdk) or Path("")
    lv = klay.LayoutView()
    lv.load_layout(str(gds), 0)  # type: ignore[call-overload]  (path, add_cellview)
    if Path(lyp).is_file():
        lv.load_layer_props(str(lyp))
    lv.max_hier_levels = 20
    lv.zoom_fit()
    lv.save_image(str(png), *size)
    return Path(png)
