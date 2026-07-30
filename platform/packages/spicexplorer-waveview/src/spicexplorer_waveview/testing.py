"""Synthetic result-artifact generators (no simulator needed).

Fast tests and demos need real *files* in both engines' formats without running SPICE:

* :func:`synth_ac_raw` / :func:`synth_tran_raw` — ngspice ``.raw`` files via spicelib's
  ``RawWrite`` (a single-pole transfer / a first-order step), with exact analytic
  figures of merit to assert against.
* :func:`synth_spectre_raw_dir` — a psfascii raw directory in the grammar Spectre 23.1
  actually emits (validated against a real ``-raw`` dir): swept AC/DC/tran/noise PSFs,
  a ``pss.fd.pss`` harmonic fd-PSF, an ``stb.stb`` loop gain, the non-swept ``dcOp.dc``
  op-point, and per-device ``*.info`` STRUCTs — plus a ``modelParameter.info`` decoy
  that loaders must SKIP (the NDA-guard contract).

Every generator returns the analytic ground truth so tests assert physics, not
snapshots.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

__all__ = ["synth_ac_raw", "synth_tran_raw", "synth_spectre_raw_dir", "write_ngspice_ascii_raw"]

# --- analytic prototypes ---------------------------------------------------------
A0 = 1000.0  # 60 dB
FPOLE = 1.0e3  # Hz


def _single_pole(freq: np.ndarray) -> np.ndarray:
    return A0 / (1.0 + 1j * freq / FPOLE)


def write_ngspice_ascii_raw(
    path: str | Path,
    plots: list[tuple[str, list[tuple[str, str]], list[np.ndarray]]],
) -> None:
    """Write an ngspice ASCII ``.raw`` file (the exact format ngspice emits).

    ``plots`` is a list of ``(plotname, variables, columns)`` where ``variables`` is
    ``[(name, kind), …]`` (kinds like ``frequency``/``voltage``/``time``) and
    ``columns`` one array per variable. Complex columns set ``Flags: complex`` and
    emit ``re,im`` pairs. Multiple plots concatenate — exactly how a deck with several
    analyses lands in one raw file.
    """
    chunks: list[str] = []
    for plotname, variables, columns in plots:
        cols = [np.asarray(c) for c in columns]
        is_complex = any(np.iscomplexobj(c) for c in cols)
        n = cols[0].size
        lines = [
            "Title: * synthetic (spicexplorer_waveview.testing)",
            "Date: Thu Jan  1 00:00:00 1970",
            "Command: ngspice-45, synthetic writer",  # spicelib sniffs the dialect from this line
            f"Plotname: {plotname}",
            f"Flags: {'complex' if is_complex else 'real'}",
            f"No. Variables: {len(variables)}",
            f"No. Points: {n}",
            "Variables:",
        ]
        for i, (name, kind) in enumerate(variables):
            lines.append(f"\t{i}\t{name}\t{kind}")
        lines.append("Values:")
        for i in range(n):
            for j, col in enumerate(cols):
                v = col[i]
                if is_complex:
                    val = f"{float(np.real(v)):.15e},{float(np.imag(v)):.15e}"
                else:
                    val = f"{float(np.real(v)):.15e}"
                lines.append(f" {i}\t{val}" if j == 0 else f"\t{val}")
        chunks.append("\n".join(lines))
    # a BLANK line separates consecutive plots (ngspice's own multi-plot framing —
    # without it spicelib's ascii reader spins forever looking for the next point)
    Path(path).write_text("\n\n".join(chunks) + "\n")


def synth_ac_raw(path: str | Path, n: int = 901) -> dict[str, Any]:
    """Write a single-pole AC ``.raw`` (ngspice ASCII format) → analytic truth dict."""
    freq = np.logspace(0, 9, n)
    h = _single_pole(freq)
    write_ngspice_ascii_raw(
        path,
        [("AC Analysis", [("frequency", "frequency"), ("v(vout)", "voltage")],
          [freq.astype(complex), h])],
    )
    return {
        "out": "v(vout)",
        "dcgain_db": 20.0 * np.log10(A0),
        "ugf_hz": A0 * FPOLE,  # single-pole GBW
        "pm_deg": 90.0,
        "f3db_hz": FPOLE,
        "n": n,
    }


def synth_tran_raw(path: str | Path, n: int = 2001, tau: float = 1e-6) -> dict[str, Any]:
    """Write a first-order step-response transient ``.raw`` → analytic truth dict."""
    t = np.linspace(0.0, 20.0 * tau, n)
    v = 1.0 - np.exp(-t / tau)
    write_ngspice_ascii_raw(
        path,
        [("Transient Analysis", [("time", "time"), ("v(vout)", "voltage")], [t, v])],
    )
    return {
        "out": "v(vout)",
        "t_settle_1pct": -np.log(0.01) * tau,  # 4.605·τ
        "slew_max": 1.0 / tau,  # dv/dt at t=0 (discrete estimate is slightly below)
        "tau": tau,
        "n": n,
    }


# --- psfascii writers --------------------------------------------------------------
def _psf_header(analysis_type: str, analysis_name: str) -> str:
    return (
        "HEADER\n"
        '"PSFversion" "1.00"\n'
        '"simulator" "spectre"\n'
        '"version" "23.1.0.509.isr9"\n'
        f'"analysis type" "{analysis_type}"\n'
        f'"analysis name" "{analysis_name}"\n'
    )


def _fmt(v: float) -> str:
    return f"{v:.15e}"


def _write_swept(
    path: Path,
    analysis_type: str,
    analysis_name: str,
    sweep_name: str,
    sweep_units: str,
    sweep: np.ndarray,
    signals: dict[str, np.ndarray],
    units: str = "V",
) -> None:
    """One swept psfascii PSF (complex signals emit ``(re im)`` pairs like Spectre)."""
    is_complex = any(np.iscomplexobj(a) for a in signals.values())
    kind = "COMPLEX DOUBLE" if is_complex else "FLOAT DOUBLE"
    lines = [_psf_header(analysis_type, analysis_name)]
    lines.append("TYPE")
    lines.append('"sweep" FLOAT DOUBLE PROP(\n"key" "sweep"\n)')
    lines.append(f'"V" {kind} PROP(\n"units" "{units}"\n"key" "node"\n)')
    lines.append("SWEEP")
    lines.append(f'"{sweep_name}" "sweep" PROP(\n"sweep_direction" 0\n"units" "{sweep_units}"\n)')
    lines.append("TRACE")
    for name in signals:
        lines.append(f'"{name}" "V"')
    lines.append("VALUE")
    for i, x in enumerate(np.asarray(sweep)):
        lines.append(f'"{sweep_name}" {_fmt(float(x))}')
        for name, arr in signals.items():
            v = np.asarray(arr)[i]
            if np.iscomplexobj(np.asarray(arr)):
                lines.append(f'"{name}" ({_fmt(float(np.real(v)))} {_fmt(float(np.imag(v)))})')
            else:
                lines.append(f'"{name}" {_fmt(float(v))}')
    lines.append("END")
    path.write_text("\n".join(lines) + "\n")


def _write_nonswept(path: Path, analysis_type: str, analysis_name: str, values: dict[str, float]) -> None:
    lines = [_psf_header(analysis_type, analysis_name)]
    lines.append("TYPE")
    lines.append('"V" FLOAT DOUBLE PROP(\n"units" "V"\n"key" "node"\n)')
    lines.append("VALUE")
    for name, v in values.items():
        lines.append(f'"{name}" "V" {_fmt(float(v))}')
    lines.append("END")
    path.write_text("\n".join(lines) + "\n")


def _write_info_struct(path: Path, struct_name: str, instances: dict[str, dict[str, float]]) -> None:
    members = list(next(iter(instances.values())).keys())
    lines = [_psf_header("info", path.stem)]
    lines.append("TYPE")
    lines.append(f'"{struct_name}" STRUCT(')
    for m in members:
        lines.append(f'"{m}" FLOAT DOUBLE PROP(\n"units" ""\n)')
    lines.append(") PROP(")
    lines.append('"key" "inst"')
    lines.append(")")
    lines.append("VALUE")
    for inst, params in instances.items():
        lines.append(f'"{inst}" "{struct_name}" (')
        for m in members:
            lines.append(_fmt(float(params[m])))
        lines.append(") PROP(")
        lines.append('"model" "synthetic"')
        lines.append(")")
    lines.append("END")
    path.write_text("\n".join(lines) + "\n")


def synth_spectre_raw_dir(root: str | Path) -> dict[str, Any]:
    """Write a full synthetic Spectre psfascii raw dir → analytic truth dict.

    Contents: ``ac.ac`` (single-pole complex transfer), ``dc.dc`` (buffer-connected
    ICMR sweep), ``tran.tran`` (first-order step), ``noise.noise`` (flicker+flat
    density), ``pss.fd.pss`` (harmonic phasors), ``stb.stb`` (loop gain),
    ``dcOp.dc`` (non-swept op values), ``finalTimeOP.info`` (device STRUCTs) and a
    ``modelParameter.info`` decoy that must never be loaded.
    """
    d = Path(root)
    d.mkdir(parents=True, exist_ok=True)

    freq = np.logspace(0, 9, 121)
    _write_swept(d / "ac.ac", "ac", "ac", "freq", "Hz", freq, {"vout": _single_pole(freq)})

    vin = np.linspace(0.0, 1.2, 121)
    vout = np.clip(vin, 0.2, 1.0)  # genuine tracking (vout follows vin, rail-pinned excluded): vin ∈ [0.2, 1.0]
    _write_swept(d / "dc.dc", "dc", "dc", "dc", "V", vin, {"vin": vin, "vout": vout})

    tau = 1e-6
    t = np.linspace(0.0, 20 * tau, 801)
    _write_swept(d / "tran.tran", "tran", "tran", "time", "s", t,
                 {"vout": 1.0 - np.exp(-t / tau)})

    fn = np.logspace(0, 6, 61)
    density = 1e-7 * np.sqrt(1.0 + 1e3 / fn)
    # a real Spectre noise PSF also carries the input→output `gain` transfer it used
    # for input-referral — snapshot's noise selection must keep the densities only
    _write_swept(d / "noise.noise", "noise", "noise", "freq", "Hz", fn,
                 {"out": density, "in": density / 10.0, "gain": np.full(fn.size, 10.0)},
                 units="V/sqrt(Hz)")

    fp = np.logspace(3, 7, 41)  # pnoise offset band (Spectre pnoise riding a PSS)
    pdensity = 2e-8 * np.sqrt(1.0 + 1e4 / fp)
    _write_swept(d / "pnoise.pnoise", "pnoise", "pnoise", "freq", "Hz", fp,
                 {"out": pdensity, "in": pdensity / 10.0}, units="V/sqrt(Hz)")

    f0 = 1e3
    hfreq = np.array([0.0, f0, 2 * f0, 3 * f0, 4 * f0, 5 * f0])
    harmonics = np.array([0.6 + 0j, 1.0 + 0j, 0.01j, 1e-3 + 0j, 1e-4j, 1e-5 + 0j])
    _write_swept(d / "pss.fd.pss", "pss", "pss", "freq", "Hz", hfreq, {"vout": harmonics})

    # periodic AC (pac riding the pss): the BASEBAND (harmonic 0) is the signal-band
    # transfer → `pac`; a non-baseband sideband → `pac_sb`; the metadata-only `pac.pac`
    # parent index must be SKIPPED by name, never parsed
    fpac = np.logspace(0, 3, 31)
    _write_swept(d / "pac.0.pac", "pac", "pac", "freq", "Hz", fpac,
                 {"vout": np.full(31, 20.0 + 0j)})
    _write_swept(d / "pac.3.pac", "pac", "pac", "freq", "Hz", fpac,
                 {"vout": np.full(31, 0.5 + 0j)})
    (d / "pac.pac").write_text("PSF pac parent index — types only, no node data\n")

    fstb = np.logspace(0, 8, 81)
    loopgain = 100.0 / (1.0 + 1j * fstb / FPOLE)
    _write_swept(d / "stb.stb", "stb", "stb", "freq", "Hz", fstb, {"loopGain": loopgain})
    # the margin sibling Spectre writes next to stb.stb: numeric margins + a STRING
    # verdict signal — loaders must keep the numbers and skip the text without failing
    (d / "stb.margin.stb").write_text(
        _psf_header("margin.stb", "stb")
        + 'TYPE\n"Deg" FLOAT DOUBLE PROP(\n"units" "Deg"\n)\n"stbstate" STRING *\n'
        + "VALUE\n"
        + f'"phaseMargin" "Deg" {_fmt(90.0)} PROP(\n"phaseMarginInfo" "synthetic"\n)\n'
        + '"stb_state" "stbstate" "The circuit is stable. Gain and phase margin are both found."\n'
        + "END\n"
    )

    _write_nonswept(d / "dcOp.dc", "dc", "dcOp",
                    {"VDD": 1.2, "VOUT": 0.6, "Vdd:p": -3.3e-4})

    _write_info_struct(
        d / "finalTimeOP.info",
        "bsim4",
        {
            "X0.M0": {"ids": 1e-4, "gm": 1e-3, "gds": 5e-5, "vth": 0.45, "cgg": 2e-15},
            "X0.M1": {"ids": 1e-4, "gm": 1.1e-3, "gds": 6e-5, "vth": 0.46, "cgg": 2.2e-15},
        },
    )
    # NDA-guard decoy: loaders must SKIP the ADE model-card dump entirely.
    _write_info_struct(d / "modelParameter.info", "modelcard", {"nch_model": {"poison": 12345.0}})
    # non-PSF siblings a real raw dir carries — must be ignored quietly
    (d / "logFile").write_text("not a psf\n")
    (d / "pss.fd.pss.cache").write_text("binary-ish cache\n")

    return {
        "ac_out": "vout",
        "dcgain_db": 20.0 * np.log10(A0),
        "ugf_hz": A0 * FPOLE,
        "f3db_hz": FPOLE,
        "icmr": (0.20, 1.00),  # rail-excluded true tracking band (icmr_band no longer counts rail coincidence)
        "vtrack": 0.05,
        "thd_pss": np.sqrt(0.01**2 + 1e-3**2 + 1e-4**2 + 1e-5**2) / 1.0,
        "hd2_db": -40.0,
        "hd3_db": -60.0,
        "loopgain_db": 40.0,
        "stb_ugf_hz": 100.0 * FPOLE,
        "i_supply": 3.3e-4,
        "noise_freq_signal": "out",
        "onoise_total": float(np.sqrt(np.trapezoid(density**2, fn))),
        "onoise_pnoise_total": float(np.sqrt(np.trapezoid(pdensity**2, fp))),
        "pnoise_spot_1e5": float(2e-8 * np.sqrt(1.0 + 1e4 / 1e5)),
        "tau": tau,
    }
