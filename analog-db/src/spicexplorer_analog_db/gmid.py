"""gm/ID lookup-table extraction (Phase 6 — gm/ID sizing reference).

Characterizes a single PDK MOS device across an ``(L × VGS × VDS × VSB)`` grid with an automated
ngspice sweep and writes a **pygmid-compatible** LUT (``.pkl``) into the DB at
``_shared/gmid/<pdk>/<device>__<corner>.pkl``. The LUT is the Boris Murmann gm/ID-kit convention
(arrays indexed ``(L,VGS,VDS,VSB)`` for ID/VT/GM/GMB/GDS + the C's + noise PSDs, plus the axis
grids), so ``pygmid.Lookup`` reads it for gm/ID sizing.

The characterization deck is cloned from Murmann's ``starter_files_open_source_tools`` decks (which
target exactly our three PDKs); this module *generates* them from the ``_shared/pdk/<pdk>.yaml``
``gmid`` block so every knob — the device + LV/HV variant, the corner (tt/ss/…), W, fingers, temp,
and the VGS/VDS/VSB/L ranges — is configurable. Two model families differ in their ngspice
operating-point probes + noise method: **BSIM4** (sky130, gf180mcu) and **PSP/OSDI** (ihp-sg13g2).

pygmid has no ngspice backend (its sweeper is Spectre-only); it is used here purely as the LUT
*reader*. This is a dev-time tool — the produced LUTs are committed; it is not on a runtime path.
"""

from __future__ import annotations

import json
import pickle
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from . import paths, pdks
from .bindings import (
    _SCALE_UM_PDKS,  # PDKs whose geometry is bare-µm (`.option scale=1u`); else 'u'
)

# ── model families ──────────────────────────────────────────────────────────────────────────
# How each family names the operating-point quantities + how its noise PSD is obtained. The
# capacitance reductions (intrinsic + overlap/junction, with the sign convention) follow the
# Murmann txt→mat builders. `noise`: 'ac' = BSIM4 needs a 1-Hz `.noise` (a CCVS mirrors Id) and the
# PSD is the squared onoise components; 'op' = PSP exposes sid/sfl directly at the operating point.
_FAMILY = {
    "bsim4": {
        "id": "id", "gmb": "gmbs", "noise": "ac", "finger": "nf",
        "overlap": ("cgdo", "cgso"), "junction": ("capbd", "capbs"),
    },
    "psp": {
        "id": "ids", "gmb": "gmb", "noise": "op", "finger": "ng",
        "overlap": ("cgdol", "cgsol"), "junction": ("cjd", "cjs"),
    },
}
# device op-point params saved on every device (besides id/gmb/noise, which are family-specific)
_BASE_PROBES = ["vth", "gm", "gds", "cgg", "cgs", "cgd", "cgb", "cdd", "css", "l"]


@dataclass
class GmidConfig:
    """One gm/ID characterization run (a single device + corner over an L×VGS×VDS×VSB grid)."""

    pdk: str
    device: str                       # the exact PDK model, e.g. nfet_03v3 / sky130_fd_pr__pfet_01v8
    family: str                       # 'bsim4' | 'psp'
    probe: str                        # the inner op-probe instance, e.g. "m.xm1.m{device}" / "n.xm1.n{device}"
    corner: str = "tt"
    polarity: str = "n"               # 'n' | 'p' (pmos sweeps negative biases)
    width_um: float = 5.0
    nfing: int = 1
    temp_k: float = 300.0
    vgs: tuple[float, float, float] = (0.0, 0.025, 1.8)   # (start, step, stop)
    vds: tuple[float, float, float] = (0.0, 0.025, 1.8)
    vsb: tuple[float, float, float] = (0.0, -0.2, -0.4)
    length_um: list[float] = field(default_factory=lambda: [0.15, 0.3, 0.5, 1.0, 2.0])
    info: str = ""
    corner_override: dict[str, Any] = field(default_factory=dict)  # variant corner-lib/section override

    @property
    def probe_inst(self) -> str:
        return self.probe.format(device=self.device)

    @classmethod
    def from_registry(cls, pdk: str, device: str | None = None, corner: str = "tt",
                      **overrides: Any) -> GmidConfig:
        """Build a config from the PDK registry's ``gmid`` defaults (with optional overrides)."""
        reg = pdks.load_registry(pdk)
        g = reg.get("gmid")
        if not g:
            raise ValueError(f"{pdk}: no `gmid` block in _shared/pdk/{pdk}.yaml")
        device = str(device or g["device"])
        polarity = "p" if re.search(r"pfet|pmos", device, re.I) else "n"
        # A non-core variant (HV/IO) may keep its models in a different corner lib (ihp HV →
        # cornerMOShv.lib) or different per-corner sections (gf180 6V → nfet_06v0_t); the first
        # `gmid.variants` entry whose `match` regex hits the device supplies that corner override.
        override: dict[str, Any] = {}
        for v in g.get("variants", []):
            if re.search(v["match"], device):
                override = dict(v.get("corners", {}))
                break
        sw = g.get("sweep", {})
        cfg = cls(
            pdk=pdk, device=device, family=g["family"], probe=g["probe"], corner=corner,
            polarity=polarity, width_um=float(g.get("width_um", 5.0)),
            nfing=int(g.get("nfing", 1)), temp_k=float(g.get("temp_k", 300.0)),
            vgs=tuple(sw.get("vgs", (0.0, 0.025, 1.8))),
            vds=tuple(sw.get("vds", (0.0, 0.025, 1.8))),
            vsb=tuple(sw.get("vsb", (0.0, -0.2, -0.4))),
            length_um=list(sw.get("length_um", [0.15, 0.3, 0.5, 1.0, 2.0])),
            info=g.get("info", f"{pdk} {device} {corner}"),
            corner_override=override,
        )
        for k, v in overrides.items():
            setattr(cfg, k, v)
        return cfg


def registry_corners(pdk: str) -> list[str]:
    """The corner set registered for a PDK's gm/ID extraction (``gmid.corners``, default ``['tt']``).

    Lets a PDK declare *which* corners to characterize (e.g. ``[tt, ss, ff]``) so they can be
    extracted in one ``--corner all`` sweep instead of one manual run each.
    """
    g = pdks.load_registry(pdk).get("gmid", {})
    return [str(c) for c in g.get("corners", ["tt"])]


def _grid(start: float, step: float, stop: float) -> np.ndarray:
    """The ngspice ``compose … start= stop= step=`` grid (inclusive, same point count)."""
    n = int(round((stop - start) / step)) + 1
    return start + step * np.arange(n)


def axes(cfg: GmidConfig) -> dict[str, np.ndarray]:
    """The four LUT axis vectors (µm for L; positive VSB)."""
    return {
        "L": np.array(cfg.length_um, dtype=float),
        "VGS": _grid(*cfg.vgs),
        "VDS": _grid(*cfg.vds),
        "VSB": np.abs(_grid(*cfg.vsb)),   # stored positive (the deck sweeps vb negative)
    }


def _fmt_um(value: float, pdk: str) -> str:
    """A geometry literal in the PDK's convention: bare microns (sky130) vs explicit 'u' (ihp/gf180)."""
    txt = f"{value:g}"
    return txt if pdk in _SCALE_UM_PDKS else f"{txt}u"


def _corner_lines(registry: dict[str, Any], corner: str, override: dict[str, Any] | None = None) -> str:
    """The ``.lib``/``.include`` lines selecting ``corner`` (mirrors the binding's corners.yaml).

    ``override`` (a device-variant's ``gmid.variants[*].corners``) is shallow-merged over the PDK's
    default ``corners`` block, so an HV/IO device can swap the corner ``lib_file`` (ihp) or the
    ``per_corner`` section set (gf180) while inheriting everything else.
    """
    c = {**registry["corners"], **(override or {})}
    lib = c["lib_file"]
    lines: list[str] = []
    if "per_corner" in c:
        if corner not in c["per_corner"]:
            raise ValueError(f"corner {corner!r} not available for this device (have {sorted(c['per_corner'])})")
        lines += [f".include {inc}" for inc in c.get("includes", [])]
        lines += [f".lib {lib} {s}" for s in c.get("pre_sections", [])]
        lines += [f".lib {lib} {s}" for s in c["per_corner"][corner]]
        lines += [f".lib {lib} {s}" for s in c.get("post_sections", [])]
    else:
        section = next((s for s in c["sections"] if s in (corner, f"mos_{corner}")), None)
        if section is None:
            raise ValueError(f"corner {corner!r} not in {c['sections']}")
        lines.append(f".lib {lib} {section}")
    return "\n".join(lines)


def _probe_params(cfg: GmidConfig) -> list[str]:
    """The full ``@inst[param]`` list to save for this family (op-point + caps + family extras)."""
    fam = _FAMILY[cfg.family]
    params = [fam["id"], fam["gmb"], *_BASE_PROBES, *fam["overlap"], *fam["junction"]]
    if fam["noise"] == "op":
        params += ["sid", "sfl"]
    return params


def build_deck(cfg: GmidConfig, registry: dict[str, Any]) -> tuple[str, str]:
    """The ngspice characterization deck + the txt filename it writes (`wrdata`)."""
    fam = _FAMILY[cfg.family]
    sgn = -1.0 if cfg.polarity == "p" else 1.0
    inst = cfg.probe_inst
    txt = f"gmid_{cfg.pdk}_{cfg.device}_{cfg.corner}.txt".replace("-", "_")

    w = _fmt_um(cfg.width_um, cfg.pdk)
    l0 = _fmt_um(cfg.length_um[0], cfg.pdk)
    l_values = " ".join(_fmt_um(v, cfg.pdk) for v in cfg.length_um)
    # bias grids: pmos sweeps the negatives of the n-grids (start/stop scaled by sgn)
    # cfg.vsb is the BULK-voltage sweep for an nmos (e.g. (0, -0.2, -0.4) → VSB 0/0.2/0.4); a pmos
    # mirrors all three biases to the opposite sign. The stored VSB axis is |vb| (see axes()).
    def z(v: float) -> float:
        return 0.0 if v == 0 else v  # normalize -0.0 → 0.0 (pmos sgn flip) for clean deck literals
    vg0, vgs_step, vg1 = (z(sgn * cfg.vgs[0]), sgn * cfg.vgs[1], sgn * cfg.vgs[2])
    vd0, vds_step, vd1 = (z(sgn * cfg.vds[0]), sgn * cfg.vds[1], sgn * cfg.vds[2])
    vb0, vsb_step, vb1 = (z(sgn * cfg.vsb[0]), sgn * cfg.vsb[1], sgn * cfg.vsb[2])

    # XM1 port order: sky130/gf180 = (d g 0 b); ihp PSP = (0 g d b) — keep each PDK's verified order.
    port_line = ("0 g d b" if cfg.family == "psp" else "d g 0 b")
    save_lines = "\n".join(f".save @{inst}[{p}]" for p in _probe_params(cfg))
    save_lines += "\n" + "\n".join(f".save @v{n}[dc]" for n in ("g", "d", "b"))
    save_lines += "\n.save g d b n"
    if fam["noise"] == "ac":
        noise_analysis = ".noise v(n) vg lin 1 1 1 1"
        save_lines += f"\n.save onoise.{inst}.id\n.save onoise.{inst}.1overf"
        wr = f"wrdata {txt} noise1.all"
    else:
        noise_analysis = ".op"
        wr = f"wrdata {txt} all"
    temp_c = cfg.temp_k - 273.15

    deck = f"""** gm/ID characterization — {cfg.pdk} {cfg.device} @{cfg.corner} (analog-db gmid-extract)
vg g 0 DC {vg0:g} AC 1
vd d 0 {vd0:g}
vb b 0 0
Hn n 0 vd 1
XM1 {port_line} {cfg.device} L={{lx}} W={{wx}} {fam["finger"]}={cfg.nfing} m=1
.param wx={w} lx={l0}
{noise_analysis}
.control
option numdgt = 7
set wr_singlescale
set wr_vecnames
compose l_vec values {l_values}
compose vg_vec start={vg0:g} stop={vg1 + vgs_step / 2:g} step={vgs_step:g}
compose vd_vec start={vd0:g} stop={vd1 + vds_step / 2:g} step={vds_step:g}
compose vb_vec start={vb0:g} stop={vb1 + vsb_step / 2:g} step={vsb_step:g}
foreach var1 $&l_vec
  alterparam lx=$var1
  reset
  foreach var2 $&vg_vec
    alter vg $var2
    foreach var3 $&vd_vec
      alter vd $var3
      foreach var4 $&vb_vec
        alter vb $var4
        run
        {wr}
        destroy all
        set appendwrite
        unset set wr_vecnames
      end
    end
  end
end
unset appendwrite
.endc
.options TEMP={temp_c:g} TNOM=27
{_corner_lines(registry, cfg.corner, cfg.corner_override)}
{save_lines}
.end
"""
    return deck, txt


def _clean_col(name: str) -> str:
    """ngspice vector name → a bare key: ``@…[gm]``→gm, ``@vg[dc]``→vg, ``onoise.….1overf``→n_1f."""
    name = name.strip()
    m = re.fullmatch(r"@v([gdb])\[dc\]", name)
    if m:
        return "v" + m.group(1)
    m = re.fullmatch(r"@[^\[]+\[([a-z0-9]+)\]", name)
    if m:
        return m.group(1)
    if name.startswith("onoise"):
        return "n_1f" if "1overf" in name else ("n_id" if name.endswith(".id") else "n_" + name.rsplit(".", 1)[-1])
    return name


def parse_lut(text: str, cfg: GmidConfig) -> dict[str, Any]:
    """Parse the ``wrdata`` output into the pygmid LUT dict (reshape + cap/noise reduction).

    Columns are read **positionally** (the noise deck emits a duplicate ``frequency`` column, so
    keying by name would collide). The VGS/VDS/VSB axes are derived from the swept-bias readback
    columns (robust to ngspice's float-boundary endpoint handling); L comes from the config (the
    ``compose … values`` grid has no float drift). Rows are in foreach order ``(L,VGS,VDS,VSB)``.
    """
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise ValueError(f"{cfg.pdk}/{cfg.device}: empty sweep output")
    cleaned = [_clean_col(h) for h in lines[0].split()]
    rows = [r.split() for r in lines[1:] if len(r.split()) == len(cleaned)]
    if len(rows) != len(lines) - 1:
        # a malformed (truncated/overlong) row silently dropped here could still reshape into a
        # consistent-but-WRONG grid — corruption must be loud
        raise ValueError(
            f"{cfg.pdk}/{cfg.device}: {len(lines) - 1 - len(rows)} malformed wrdata row(s) "
            f"(wrong column count) — the sweep output is corrupt"
        )

    def col(name: str) -> np.ndarray:
        idx = cleaned.index(name)  # first occurrence (positional; dodges the duplicate 'frequency')
        out = np.array([float(r[idx]) for r in rows], dtype=float)
        if not np.all(np.isfinite(out)):
            # NaN/inf here would poison every pygmid interpolation downstream, silently
            raise ValueError(
                f"{cfg.pdk}/{cfg.device}: non-finite value(s) in column {name!r} "
                f"(non-converged bias point?) — refuse to build a poisoned LUT"
            )
        return out

    # Store ALL bias axes as positive magnitudes (the Murmann/pygmid convention: a pmos table uses
    # the same positive gm/ID, VGS, VDS as an nmos so one sizing flow serves both). A pmos deck
    # sweeps the biases negative; taking |·| here (a) flips them positive AND (b) re-aligns the axes
    # with the foreach-ordered arrays — `np.unique` sorts ASCENDING, and |sweep| is ascending in
    # foreach order for pmos too (0 → 1.8), whereas the raw negative sweep (0 → -1.8) would sort
    # reversed and mislabel every pmos slice. For nmos this is a no-op (biases already ≥ 0).
    VGS, VDS, VSB = (np.unique(np.abs(col(c))) for c in ("vg", "vd", "vb"))
    nV, nD, nB = len(VGS), len(VDS), len(VSB)
    nrows = len(rows)
    if nV * nD * nB == 0 or nrows % (nV * nD * nB) != 0:
        raise ValueError(
            f"{cfg.pdk}/{cfg.device}: {nrows} bias rows not divisible by VGS×VDS×VSB="
            f"{nV}×{nD}×{nB} (a non-converged point dropped a row?)"
        )
    nL = nrows // (nV * nD * nB)
    L = np.array(cfg.length_um[:nL], dtype=float)
    dims = [nL, nV, nD, nB]

    def arr(name: str) -> np.ndarray:
        return np.reshape(col(name), dims)  # foreach order = (L, VGS, VDS, VSB)

    fam = _FAMILY[cfg.family]
    ov_d, ov_s = (arr(o) for o in fam["overlap"])      # gate-drain / gate-source overlap
    jn_d, jn_s = (arr(j) for j in fam["junction"])     # drain / source junction
    sign = 1.0 if cfg.family == "psp" else -1.0        # BSIM intrinsic cgd/cgs are negative
    lut: dict[str, Any] = {
        "INFO": cfg.info, "CORNER": cfg.corner.upper(), "TEMP": float(cfg.temp_k),
        "NFING": int(cfg.nfing), "W": float(cfg.width_um),
        "L": L, "VGS": VGS, "VDS": VDS, "VSB": VSB,
        "ID": arr(fam["id"]), "VT": arr("vth"), "GM": arr("gm"),
        "GMB": arr(fam["gmb"]), "GDS": arr("gds"),
        "CGG": arr("cgg") + ov_d + ov_s,
        "CGB": -arr("cgb"),
        "CGD": sign * arr("cgd") + ov_d,
        "CGS": sign * arr("cgs") + ov_s,
        "CDD": arr("cdd") + jn_d + ov_d,
        "CSS": arr("css") + jn_s + ov_s,
    }
    if fam["noise"] == "ac":
        lut["STH"] = arr("n_id") ** 2
        lut["SFL"] = arr("n_1f") ** 2
    else:
        lut["STH"] = arr("sid")
        lut["SFL"] = arr("sfl")
    return lut


def lut_path_for(pdk: str, device: str, corner: str = "tt") -> Path:
    """The committed-LUT path for a (pdk, device, corner) — no GmidConfig needed."""
    return paths.shared_root() / "gmid" / pdk / f"{device}__{corner}.pkl"


def lut_path(cfg: GmidConfig) -> Path:
    return lut_path_for(cfg.pdk, cfg.device, cfg.corner)


def write_lut(cfg: GmidConfig, lut: dict[str, Any]) -> Path:
    out = lut_path(cfg)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as fh:
        pickle.dump(lut, fh)
    return out


# ── LUT manifest (the registry record beside each .pkl) ───────────────────────────────────────
# A `<device>__<corner>.manifest.json` sidecar makes a LUT self-describing: the exact run
# dimensions (L/VGS/VDS/VSB grids + W/nfing/temp), the corner, and the EXACT model resolution (the
# `.lib`/`.include` lines that pulled the model card) — plus provenance. The `.pkl` holds the data;
# the manifest holds what it is and how it was made. Read both via `manifest()` + `lut()`.


def _axis_spec(values: Any) -> dict[str, Any]:
    """Describe a stored axis vector: n, min, max, and either a uniform `step` or explicit `values`."""
    v = np.asarray(values, dtype=float)
    spec: dict[str, Any] = {"n": int(v.size), "min": float(v.min()), "max": float(v.max())}
    if v.size >= 2:
        steps = np.diff(v)
        if np.allclose(steps, steps[0], rtol=1e-6, atol=0.0):
            spec["step"] = float(round(steps[0], 6))
        else:
            spec["values"] = [float(round(x, 6)) for x in v]  # non-uniform (e.g. the L grid)
    return spec


def build_manifest(
    cfg: GmidConfig,
    lut: dict[str, Any],
    registry: dict[str, Any] | None = None,
    *,
    ngspice: str | None = None,
    extracted_at: str | None = None,
) -> dict[str, Any]:
    """Assemble a LUT manifest (run dimensions + exact model resolution + provenance).

    Conditions (W/temp/nfing/corner) are read from the LUT's own header so the manifest stays true
    to the committed data even when rebuilt; the model `.lib`/`.include` lines come from the
    registry corner block (+ any device-variant override).
    """
    if registry is None:
        registry = pdks.load_registry(cfg.pdk)
    corner_lines = _corner_lines(registry, cfg.corner, cfg.corner_override).splitlines()
    scalars, axes_keys = {"INFO", "CORNER", "TEMP", "NFING", "W"}, {"L", "VGS", "VDS", "VSB"}
    params = [k for k in lut if k not in scalars and k not in axes_keys]
    return {
        "schema": "spicexplorer/gmid-lut@1",
        "pdk": cfg.pdk,
        "device": cfg.device,
        "model_family": cfg.family,
        "polarity": cfg.polarity,
        "corner": str(lut.get("CORNER", cfg.corner)).lower(),
        "model": {
            "corner_lines": corner_lines,  # the EXACT lines that resolved the model card
            "variant_override": cfg.corner_override or None,
            "info": str(lut.get("INFO", cfg.info)),
        },
        "conditions": {
            "temp_k": float(lut.get("TEMP", cfg.temp_k)),
            "width_um": float(lut.get("W", cfg.width_um)),
            "nfing": int(lut.get("NFING", cfg.nfing)),
        },
        "dimensions": {  # the run dimensions (stored positive magnitudes; VSB/pmos are |·|)
            "L_um": _axis_spec(lut["L"]),
            "VGS_V": _axis_spec(lut["VGS"]),
            "VDS_V": _axis_spec(lut["VDS"]),
            "VSB_V": {**_axis_spec(lut["VSB"]), "stored": "magnitude"},
        },
        "params": params,
        "lut_file": f"{cfg.device}__{cfg.corner}.pkl",
        "provenance": {"tool": "analog-db gmid-extract", "ngspice": ngspice, "extracted_at": extracted_at},
    }


def manifest_path_for(pdk: str, device: str, corner: str = "tt") -> Path:
    return paths.shared_root() / "gmid" / pdk / f"{device}__{corner}.manifest.json"


def write_manifest(
    cfg: GmidConfig,
    lut: dict[str, Any],
    registry: dict[str, Any] | None = None,
    *,
    ngspice: str | None = None,
    extracted_at: str | None = None,
) -> Path:
    out = manifest_path_for(cfg.pdk, cfg.device, cfg.corner)
    out.parent.mkdir(parents=True, exist_ok=True)
    man = build_manifest(cfg, lut, registry, ngspice=ngspice, extracted_at=extracted_at)
    out.write_text(json.dumps(man, indent=2) + "\n")
    return out


def manifest(pdk: str, device: str | None = None, corner: str = "tt") -> dict[str, Any]:
    """Read a committed LUT's manifest (run dimensions + exact model + provenance).

    ``device`` defaults to the registry ``gmid.device``. Pairs with :func:`lut` (the data): clear
    ``FileNotFoundError`` listing the regen command when the manifest isn't committed.
    """
    if device is None:
        device = pdks.load_registry(pdk).get("gmid", {}).get("device")
        if device is None:
            raise ValueError(f"{pdk}: no `gmid.device` default in the registry — pass device=")
    p = manifest_path_for(pdk, device, corner)
    if not p.is_file():
        raise FileNotFoundError(
            f"no manifest '{p.name}' under _shared/gmid/{pdk}/ — regenerate it with "
            f"`analog-db gmid-extract --pdk {pdk} --device {device}"
            + (f" --corner {corner}" if corner != "tt" else "") + "`"
        )
    return json.loads(p.read_text())


def list_luts(pdk: str | None = None) -> list[dict[str, Any]]:
    """Catalog the committed gm/ID LUTs — one row per ``.pkl`` (pdk, device, corner, files).

    The DB user's entry point: enumerate what's available, then `manifest()`/`lut()` for the detail.
    """
    root = paths.shared_root() / "gmid"
    if not root.is_dir():
        return []
    pdk_dirs = [root / pdk] if pdk else sorted(d for d in root.iterdir() if d.is_dir())
    rows: list[dict[str, Any]] = []
    for d in pdk_dirs:
        if not d.is_dir():
            continue
        for pkl in sorted(d.glob("*.pkl")):
            device, _, corner = pkl.stem.rpartition("__")
            man = d / f"{pkl.stem}.manifest.json"
            rows.append(
                {
                    "pdk": d.name,
                    "device": device,
                    "corner": corner,
                    "lut_file": str(pkl.relative_to(root)),
                    "manifest": str(man.relative_to(root)) if man.is_file() else None,
                }
            )
    return rows


def base_image_deck_runner(image: str = "spicexplorer-spice-base:local"):
    """A ``(deck, txt) -> txt-contents`` runner: pipe the deck into a fresh ``docker run`` of the EDA
    base image, run ngspice, and ``cat`` the ``wrdata`` file back (the LUT data is in that file, not
    on stdout). The base image carries all three PDKs on the sourcepath."""
    import subprocess

    def _run(deck: str, txt: str) -> str:
        cmd = [
            "docker", "run", "--rm", "-i", image, "bash", "-lc",
            f"d=$(mktemp -d) && cat > $d/cell.spice && cd $d && ngspice -b cell.spice >/dev/null 2>&1; "
            f"cat $d/{txt} 2>/dev/null",
        ]
        return subprocess.run(cmd, input=deck, capture_output=True, text=True, timeout=3600).stdout

    return _run


def base_image_ngspice_version(image: str = "spicexplorer-spice-base:local") -> str | None:
    """The base image's ngspice version string (for manifest provenance); ``None`` if unavailable."""
    import re as _re
    import subprocess

    try:
        out = subprocess.run(
            ["docker", "run", "--rm", image, "ngspice", "--version"],
            capture_output=True, text=True, timeout=120,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    m = _re.search(r"ngspice(?:-| )(\d+)", out)
    return m.group(1) if m else (out.strip().splitlines()[0] if out.strip() else None)


def extract(cfg: GmidConfig, run: Any) -> dict[str, Any]:
    """Build the deck, run it via ``run(deck, txt) -> txt-contents``, and parse the LUT."""
    registry = pdks.load_registry(cfg.pdk)
    deck, txt = build_deck(cfg, registry)
    out = run(deck, txt)
    if not out.strip():
        raise RuntimeError(
            f"{cfg.pdk}/{cfg.device}@{cfg.corner}: ngspice produced no '{txt}' — the sweep failed "
            f"(check the corner libs resolve + the device biases up)."
        )
    return parse_lut(out, cfg)


def load_lut(path: Path | str):
    """Load a LUT *by path*: a ``pygmid.Lookup`` if pygmid is installed, else the raw dict.

    For the common case use :func:`lut` — ``lut(pdk, device, corner)`` resolves the path for you.
    """
    try:
        from pygmid import Lookup
        return Lookup(str(path))
    except ImportError:
        with Path(path).open("rb") as fh:
            return pickle.load(fh)


def lut(pdk: str, device: str | None = None, corner: str = "tt"):
    """One-step load of a committed gm/ID LUT — the common case (no GmidConfig / path surgery).

    ``device`` defaults to the PDK registry's ``gmid.device`` (the core device). Returns a
    ``pygmid.Lookup`` (or the raw dict without pygmid). Raises a **clear** ``FileNotFoundError`` that
    lists what *is* committed and the exact ``gmid-extract`` command when the LUT isn't committed —
    not every (pdk × device × corner) is (only the cores are committed; others are one extract away).
    """
    if device is None:
        device = pdks.load_registry(pdk).get("gmid", {}).get("device")
        if device is None:
            raise ValueError(f"{pdk}: no `gmid.device` default in the registry — pass device=")
    path = lut_path_for(pdk, device, corner)
    if not path.is_file():
        have = sorted(p.name for p in path.parent.glob("*.pkl")) if path.parent.is_dir() else []
        cmd = f"analog-db gmid-extract --pdk {pdk} --device {device}"
        if corner != "tt":
            cmd += f" --corner {corner}"
        raise FileNotFoundError(
            f"no committed LUT '{path.name}' under _shared/gmid/{pdk}/ "
            f"(committed there: {', '.join(have) or 'none'}). Extract it:\n    {cmd}"
        )
    return load_lut(path)
