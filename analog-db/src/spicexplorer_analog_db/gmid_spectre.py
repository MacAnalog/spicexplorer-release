"""Native-Spectre gm/ID LUT extraction — the licensed-kit lane of Phase 6.

:mod:`spicexplorer_analog_db.gmid` characterizes the *open* PDKs through ngspice;
Spectre-routed PDKs (``sim_engine: spectre`` in ``_shared/pdk/<pdk>.yaml``, e.g. FOUNDRY-n65)
deliberately opt out of that flow. This module is the missing lane: it sweeps the PDK's two
core MOS flavours over an ``(L × VGS × VDS × VSB)`` grid with **plain headless Spectre** — no
Virtuoso/OCEAN session — and writes **pygmid-compatible** LUT ``.pkl``s + ``.manifest.json``
sidecars, one pair per corner.

Everything is configured by the registry's ``gmid`` block (CLI flags override)::

    gmid:
      family: bsim4
      engine: spectre                  # routes `analog-db gmid-extract-spectre`
      corners: [tt]
      width_um: 5                      # characterization finger width (µm)
      temp_k: 300.15
      sweep:
        vgs: [0, 0.025, 1.5]           # (start, step, stop) V — 25 mV validated vs live op dumps
        vds: [0, 0.025, 1.8]
        vsb: [0, 0.1, 1.0]             # stored magnitudes; the deck mirrors signs per polarity
        length_um: [0.06, …, 10.0]
      out_root: ~/.spicexplorer/gmid   # licensed kit ⇒ LUTs live OUT-OF-REPO by default
      simulator:                       # optional runtime knobs for the Spectre fan-out
        workers: 12                    # parallel Spectre jobs (one job per (L, VSB) pair)
        timeout_s: 1200                # per-job wall clock

Speed: one Spectre process per (L, VSB) pair only — the nested ``sweep { dc }`` solves the
whole VGS×VDS plane (both polarities instantiated side by side, biases mirrored) inside a
single invocation, so per-process overhead is paid ``nL·nVSB`` times, not once per bias point
(17 L × 11 VSB × 61 × 73 × 2 devices ≈ 1.7 M op-points in ~10 min at 12 workers).

NDA posture (licensed kits): the deck references only the operator's *neutral* wrapper
(``$SPICEXPLORER_<PDK>_MODEL_ROOT/<corners.lib_file>`` + a generic section name) — no kit path
or kit section appears in repo or output; Spectre logs stay in the scratch dir and are never
echoed. Committing licensed-kit LUTs is an owner decision, not this tool's — hence the
out-of-repo ``out_root`` default (mirroring the committed ``_shared/gmid/<pdk>/`` layout).

Correctness notes proven against live op dumps (see the analog-learning-journal spectre.md):

* **bsim4 splits gate current** — ``igd``/``igs`` are overlap/edge tunneling only; the channel
  component ``igcd``/``igcs`` is ~100× larger at 65 nm. The stored ``IGD``/``IGS`` are the
  folded TOTALS (igd+igcd / igs+igcs), so leak budgets (``∂(IGD+IGS)/∂VGS``) are honest.
* **Noise (STH/SFL) is intentionally omitted** — an absent key fails loud; zeros lie.
* The LUT is per-unit-width at ``width_um`` fingers; apply sizings with ~2–10 µm fingers and
  scale total W via ``m`` (narrow fingers deviate: 0.5 µm pch measured 2.2× off on gm/gds).
"""

from __future__ import annotations

import json
import os
import pickle
import re
import shlex
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np

from . import pdks
from .gmid import _axis_spec, _grid

# ── pygmid reduction convention (pygmid.sweep.config coefficient matrices) ──────────────────
# stored LUT param ← signed sum of Spectre op-point params; `odd` entries flip sign for the
# p-device (its biases are swept negative, so odd quantities come back negative).
_OP_PARAMS = [
    "ids", "vth", "igd", "igs", "igcd", "igcs", "gm", "gmbs", "gds",
    "cgg", "cgs", "csg", "cgd", "cdg", "cgb", "cdd", "css", "cjd", "cjs",
]
_REDUCE: dict[str, list[tuple[str, float, bool]]] = {  # out ← [(op_param, coeff, odd)]
    "ID":  [("ids", 1.0, True)],
    "VT":  [("vth", 1.0, True)],
    # TOTAL gate currents: fold the bsim4 channel components in (igd/igs alone are ~100× low)
    "IGD": [("igd", 1.0, True), ("igcd", 1.0, True)],
    "IGS": [("igs", 1.0, True), ("igcs", 1.0, True)],
    "GM":  [("gm", 1.0, False)],
    "GMB": [("gmbs", 1.0, False)],
    "GDS": [("gds", 1.0, False)],
    "CGG": [("cgg", 1.0, False)],
    "CGS": [("cgs", -1.0, False)],
    "CSG": [("csg", -1.0, False)],
    "CGD": [("cgd", -1.0, False)],
    "CDG": [("cdg", -1.0, False)],
    "CGB": [("cgb", -1.0, False)],
    "CDD": [("cdd", 1.0, False), ("cjd", 1.0, False)],
    "CSS": [("css", 1.0, False), ("cjs", 1.0, False)],
}


@dataclass
class SpectreGmidConfig:
    """One Spectre gm/ID characterization run (both polarities, one corner)."""

    pdk: str
    nmos: str
    pmos: str
    lib_file: str                              # neutral operator wrapper (corners.lib_file)
    corner: str = "tt"
    width_um: float = 5.0
    nfing: int = 1
    temp_k: float = 300.15
    vgs: tuple[float, float, float] = (0.0, 0.025, 1.5)
    vds: tuple[float, float, float] = (0.0, 0.025, 1.8)
    vsb: tuple[float, float, float] = (0.0, 0.1, 1.0)   # magnitudes (deck mirrors signs)
    length_um: list[float] = field(default_factory=lambda: [0.06, 0.13, 0.25, 0.5, 1.0, 2.0])
    info: str = ""
    out_root: Path = field(default_factory=lambda: Path.home() / ".spicexplorer" / "gmid")
    workers: int = 8                           # gmid.simulator.workers — parallel Spectre jobs
    timeout_s: int = 1200                      # gmid.simulator.timeout_s — per-job wall clock

    @classmethod
    def from_registry(cls, pdk: str, corner: str = "tt", **overrides: Any) -> SpectreGmidConfig:
        """Build a config from the PDK registry's ``gmid`` block (+ optional overrides)."""
        reg = pdks.load_registry(pdk)
        g = reg.get("gmid")
        if not g:
            raise ValueError(f"{pdk}: no `gmid` block in _shared/pdk/{pdk}.yaml")
        if g.get("engine", reg.get("sim_engine")) != "spectre":
            raise ValueError(
                f"{pdk}: gmid engine is not 'spectre' — use `analog-db gmid-extract` (ngspice)"
            )
        if corner not in reg["corners"]["sections"]:
            raise ValueError(f"corner {corner!r} not in registry sections {reg['corners']['sections']}")
        sw = g.get("sweep", {})
        sim = g.get("simulator", {}) or {}
        cfg = cls(
            pdk=pdk,
            nmos=str(reg["devices"]["nmos"]["core"]),
            pmos=str(reg["devices"]["pmos"]["core"]),
            lib_file=str(reg["corners"]["lib_file"]),
            corner=corner,
            width_um=float(g.get("width_um", 5.0)),
            nfing=int(g.get("nfing", 1)),
            temp_k=float(g.get("temp_k", 300.15)),
            vgs=tuple(sw.get("vgs", (0.0, 0.025, 1.5))),
            vds=tuple(sw.get("vds", (0.0, 0.025, 1.8))),
            vsb=tuple(sw.get("vsb", (0.0, 0.1, 1.0))),
            length_um=[float(x) for x in sw.get("length_um", [0.06, 0.13, 0.25, 0.5, 1.0, 2.0])],
            info=str(g.get("info", f"{pdk} core pair, native Spectre")),
            out_root=Path(str(g.get("out_root", "~/.spicexplorer/gmid"))).expanduser(),
            workers=int(sim.get("workers", 8)),
            timeout_s=int(sim.get("timeout_s", 1200)),
        )
        for k, v in overrides.items():
            if v is not None:
                setattr(cfg, k, Path(v).expanduser() if k == "out_root" else v)
        return cfg

    @property
    def registered_corners(self) -> list[str]:
        return [str(c) for c in pdks.load_registry(self.pdk).get("gmid", {}).get("corners", ["tt"])]


def axes(cfg: SpectreGmidConfig) -> dict[str, np.ndarray]:
    """The four LUT axis vectors (µm for L; VSB stored positive)."""
    return {
        "L": np.array(cfg.length_um, dtype=float),
        "VGS": _grid(*cfg.vgs),
        "VDS": _grid(*cfg.vds),
        "VSB": _grid(*cfg.vsb),
    }


# ── environment (operator-supplied, never committed) ────────────────────────────────────────

def model_root(cfg: SpectreGmidConfig) -> Path:
    """The neutral wrapper directory: ``$SPICEXPLORER_<PDK>_MODEL_ROOT`` (dashes → underscores)."""
    var = f"SPICEXPLORER_{cfg.pdk.replace('-', '_').upper()}_MODEL_ROOT"
    return Path(os.environ.get(var, str(Path.home() / ".spicexplorer" / "models")))


def _load_env_file(path: Path) -> dict[str, str]:
    """Parse a simple KEY=VALUE env file (the virtuoso-bridge local.env). Values never printed."""
    out: dict[str, str] = {}
    if path.is_file():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def spectre_invocation() -> tuple[str, str | None]:
    """(spectre binary, cadence cshrc) from the env / the bridge's local.env file."""
    env_file = Path(os.environ.get("SPICEXPLORER_VB_ENV_FILE",
                                   str(Path.home() / ".virtuoso-bridge" / "local.env")))
    env = _load_env_file(env_file)
    spectre_bin = os.environ.get("VB_SPECTRE_BIN") or env.get("VB_SPECTRE_BIN") or "spectre"
    cshrc = os.environ.get("VB_CADENCE_CSHRC") or env.get("VB_CADENCE_CSHRC") or None
    return spectre_bin, cshrc


# ── deck / run / parse ──────────────────────────────────────────────────────────────────────

def build_deck(cfg: SpectreGmidConfig, l_um: float, vsb: float) -> str:
    """One characterization deck: both polarities, ``sweep VDS { dc VGS }`` at fixed (L, VSB)."""
    ax = axes(cfg)
    vgs, vds = ax["VGS"], ax["VDS"]
    saves = " ".join(f"XM{p}:{q}" for p in ("N", "P") for q in _OP_PARAMS)
    vg0, vg1, vgstep = vgs[0], vgs[-1], vgs[1] - vgs[0]
    vd0, vd1, vdstep = vds[0], vds[-1], vds[1] - vds[0]
    temp_c = cfg.temp_k - 273.15
    return f"""// gm/ID characterization — {cfg.nmos}+{cfg.pmos} @{cfg.corner} L={l_um}u VSB={vsb} (analog-db gmid-extract-spectre)
simulator lang=spectre
include "{model_root(cfg) / cfg.lib_file}" section={cfg.corner}
parameters gs={vg0:g} ds={vd0:g} sb={vsb:g} lx={l_um:g}e-6 wx={cfg.width_um:g}e-6
vdsn (vdn 0) vsource dc=ds
vgsn (vgn 0) vsource dc=gs
vbsn (vbn 0) vsource dc=-sb
vdsp (vdp 0) vsource dc=-ds
vgsp (vgp 0) vsource dc=-gs
vbsp (vbp 0) vsource dc=sb
XMN (vdn vgn 0 vbn) {cfg.nmos} l=lx w=wx m=1
XMP (vdp vgp 0 vbp) {cfg.pmos} l=lx w=wx m=1
simulatorOptions options gmin=1e-13 reltol=1e-4 vabstol=1e-6 iabstol=1e-10 temp={temp_c:g} tnom=27
save {saves}
sweepvds sweep param=ds start={vd0:g} stop={vd1:g} step={vdstep:g} {{
sweepvgs dc param=gs start={vg0:g} stop={vg1:g} step={vgstep:g}
}}
"""


def run_deck(deck_path: Path, *, spectre_bin: str, cshrc: str | None, timeout: int) -> Path:
    """Run one deck (bridge-style invocation); return the psfascii raw dir.

    NDA: on failure only the return code + log *path* are surfaced — Spectre output resolves
    the kit path and must never be echoed.
    """
    raw = deck_path.with_suffix(".raw")
    log = deck_path.with_suffix(".log")
    argv = [spectre_bin, "-64", str(deck_path), "+escchars", "+log", str(log),
            "-format", "psfascii", "-raw", str(raw), "-maxw", "5", "-maxn", "5"]
    cmd = (["csh", "-fc", f"source {shlex.quote(cshrc)}; exec "
            + " ".join(shlex.quote(a) for a in argv)] if cshrc else argv)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          cwd=str(deck_path.parent))
    if proc.returncode != 0 or not raw.is_dir():
        raise RuntimeError(f"spectre failed (rc={proc.returncode}) for {deck_path.name}; see {log}")
    return raw


def parse_job(raw: Path, n_vgs: int, n_vds: int) -> dict[str, np.ndarray]:
    """Read the ``sweepvds-*_sweepvgs.dc`` PSFs → ``{'XMN:ids': (n_vgs, n_vds), …}``.

    Fail-loud: missing slices, short vectors, or non-finite values abort the LUT (a silently
    dropped row would reshape into a consistent-but-WRONG grid).
    """
    from psf_utils import PSF

    files = sorted(raw.glob("sweepvds-*_sweepvgs.dc"),
                   key=lambda p: int(re.search(r"-(\d+)_", p.name).group(1)))  # numeric, not lexical
    if len(files) != n_vds:
        raise RuntimeError(f"{raw}: expected {n_vds} vds slices, found {len(files)}")
    out = {f"XM{p}:{q}": np.zeros((n_vgs, n_vds)) for p in ("N", "P") for q in _OP_PARAMS}
    for k, f in enumerate(files):
        psf = PSF(str(f))
        for sig in psf.all_signals():
            if sig.name in out:
                vec = np.asarray(sig.ordinate, dtype=float).reshape(-1)
                if vec.size != n_vgs:
                    raise RuntimeError(f"{f.name}:{sig.name}: {vec.size} pts != n_vgs {n_vgs}")
                out[sig.name][:, k] = vec
    for name, arr in out.items():
        if not np.all(np.isfinite(arr)):
            raise RuntimeError(f"{raw}: non-finite {name} — refuse to build a poisoned LUT")
    return out


def assemble(cfg: SpectreGmidConfig, jobs: dict[tuple[int, int], dict[str, np.ndarray]],
             pol: str) -> dict[str, Any]:
    """Fold per-(L,VSB) job dicts into one pygmid LUT dict for one polarity."""
    ax = axes(cfg)
    inst = "XMN" if pol == "n" else "XMP"
    dims = (len(ax["L"]), len(ax["VGS"]), len(ax["VDS"]), len(ax["VSB"]))
    lut: dict[str, Any] = {
        "INFO": cfg.info, "CORNER": cfg.corner.upper(), "TEMP": float(cfg.temp_k),
        "NFING": int(cfg.nfing), "W": float(cfg.width_um),
        "L": ax["L"].copy(), "VGS": ax["VGS"].copy(), "VDS": ax["VDS"].copy(),
        "VSB": ax["VSB"].copy(),
    }
    for out, terms in _REDUCE.items():
        arr = np.zeros(dims)
        for i, j in jobs:
            arr[i, :, :, j] = sum(
                c * (-1.0 if (odd and pol == "p") else 1.0) * jobs[i, j][f"{inst}:{q}"]
                for q, c, odd in terms
            )
        lut[out] = arr
    return lut


def extract(cfg: SpectreGmidConfig, *, scratch: Path | None = None,
            progress: Callable[[str], None] = print,
            lengths: list[float] | None = None) -> dict[str, dict[str, Any]]:
    """Run the full fan-out and return ``{'n': lut, 'p': lut}``.

    Parallelism = ``cfg.workers`` concurrent Spectre jobs (the ``gmid.simulator.workers`` YAML
    knob); one job per (L, VSB) pair. A failed job aborts the extraction (fail-loud).
    """
    if lengths is not None:
        cfg.length_um = list(lengths)
    ax = axes(cfg)
    spectre_bin, cshrc = spectre_invocation()
    work = Path(scratch) if scratch else Path(tempfile.mkdtemp(prefix="gmid_spectre_"))
    work.mkdir(parents=True, exist_ok=True)
    n_jobs = len(ax["L"]) * len(ax["VSB"])
    progress(f"{cfg.pdk}@{cfg.corner}: {len(ax['L'])} L × {len(ax['VSB'])} VSB = {n_jobs} spectre "
             f"jobs × {len(ax['VGS'])}×{len(ax['VDS'])} bias points × 2 devices "
             f"({cfg.workers} workers); scratch={work}")

    def one(i: int, j: int) -> tuple[int, int, dict[str, np.ndarray]]:
        deck = work / f"job_L{i}_B{j}.scs"
        deck.write_text(build_deck(cfg, float(ax["L"][i]), float(ax["VSB"][j])))
        raw = run_deck(deck, spectre_bin=spectre_bin, cshrc=cshrc, timeout=cfg.timeout_s)
        return i, j, parse_job(raw, len(ax["VGS"]), len(ax["VDS"]))

    t0 = time.time()
    jobs: dict[tuple[int, int], dict[str, np.ndarray]] = {}
    with ThreadPoolExecutor(max_workers=cfg.workers) as ex:
        futs = [ex.submit(one, i, j)
                for i in range(len(ax["L"])) for j in range(len(ax["VSB"]))]
        for n, fut in enumerate(as_completed(futs), 1):
            i, j, data = fut.result()
            jobs[i, j] = data
            if n % 10 == 0 or n == n_jobs:
                progress(f"  {n}/{n_jobs} jobs done ({time.time() - t0:.0f}s)")
    return {"n": assemble(cfg, jobs, "n"), "p": assemble(cfg, jobs, "p")}


# ── output (out-of-repo by default; committed _shared/gmid layout) ──────────────────────────

def device_for(cfg: SpectreGmidConfig, pol: str) -> str:
    return cfg.nmos if pol == "n" else cfg.pmos


def lut_path(cfg: SpectreGmidConfig, pol: str) -> Path:
    return cfg.out_root / cfg.pdk / f"{device_for(cfg, pol)}__{cfg.corner}.pkl"


def write_lut(cfg: SpectreGmidConfig, lut: dict[str, Any], pol: str) -> Path:
    out = lut_path(cfg, pol)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as fh:
        pickle.dump(lut, fh)
    return out


def build_manifest(cfg: SpectreGmidConfig, lut: dict[str, Any], pol: str,
                   *, extracted_at: str | None = None) -> dict[str, Any]:
    """The self-describing sidecar (same ``spicexplorer/gmid-lut@1`` schema as the open lane)."""
    scalars, axes_keys = {"INFO", "CORNER", "TEMP", "NFING", "W"}, {"L", "VGS", "VDS", "VSB"}
    return {
        "schema": "spicexplorer/gmid-lut@1",
        "pdk": cfg.pdk,
        "device": device_for(cfg, pol),
        "model_family": "bsim4",
        "polarity": pol,
        "corner": cfg.corner,
        "model": {
            # the EXACT include line, kit-neutral: wrapper filename + generic section only
            "corner_lines": [f'include "{cfg.lib_file}" section={cfg.corner}'],
            "variant_override": None,
            "info": cfg.info,
        },
        "conditions": {"temp_k": float(lut["TEMP"]), "width_um": float(lut["W"]),
                       "nfing": int(lut["NFING"])},
        "dimensions": {
            "L_um": _axis_spec(lut["L"]),
            "VGS_V": _axis_spec(lut["VGS"]),
            "VDS_V": _axis_spec(lut["VDS"]),
            "VSB_V": {**_axis_spec(lut["VSB"]), "stored": "magnitude"},
        },
        "params": [k for k in lut if k not in scalars and k not in axes_keys],
        "notes": "IGD/IGS are TOTAL gate currents (bsim4 igd+igcd / igs+igcs — the channel "
                 "component dominates ~100× at 65nm); noise (STH/SFL) not characterized — "
                 "keys omitted so lookups fail loud",
        "lut_file": lut_path(cfg, pol).name,
        "provenance": {"tool": "analog-db gmid-extract-spectre", "engine": "spectre",
                       "extracted_at": extracted_at},
    }


def write_manifest(cfg: SpectreGmidConfig, lut: dict[str, Any], pol: str,
                   *, extracted_at: str | None = None) -> Path:
    out = lut_path(cfg, pol).with_name(f"{device_for(cfg, pol)}__{cfg.corner}.manifest.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build_manifest(cfg, lut, pol, extracted_at=extracted_at),
                              indent=2) + "\n")
    return out
