"""SG13G2 inductorless PAM-4 driver — DUT netlist builders, testbenches, extractors.

Port of the EIC-designer `lumped-broadband-driver` verified reference
(replication of Inac et al., EuMIC 2022) into the spicexplorer analog-db
drawings staging area. Differences from the EIC original:

* Standalone — no eic_designer import; the IHP SG13G2 PDK is resolved from
  ``$PDK_ROOT/$PDK``, falling back to ``~/local/pdks/ihp-sg13g2`` and the
  platform-vendored ``docker/pdk/ihp-sg13g2``.
* The driver is factored into three DUT subcircuits (LSB cell, MSB 2-cell
  bank, combined 2-bit DAC), each with its own testbench set. Tail currents
  are VCCS-driven from a bias port (1 mA/V) so one DUT netlist serves both
  the ramped-transient and the DC/AC testbenches.
* Both measurement methods are provided:
  - ``tran``: ramp-from-0 ``uic`` + single-tone probe + single-bin DFT
    (the EIC-validated method, required on ngspice-44 where the
    self-heating VBIC HBT fails .op/.ac — JPP-361);
  - ``ac``: direct .op/.ac (converges on ngspice-45 and matches the
    transient DFT to <0.1 dB; ~30x cheaper for a frequency sweep).

S21 is a differential 2-port power-wave gain with equal 50 ohm/side
(100 ohm differential) reference at both ports — the paper's VNA convention,
NOT the open-circuit voltage gain.

Device: npn13G2, pin order "c b e bn" (collector base emitter substrate).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

Z0 = 50.0  # per-side port reference impedance (100 ohm differential)

# --------------------------------------------------------------------------
# PDK resolution
# --------------------------------------------------------------------------

_CORNER_SECTION = {"tt": "hbt_typ", "fast": "hbt_bcs", "slow": "hbt_wcs"}


def models_dir() -> Path:
    """IHP SG13G2 ngspice model directory (must contain cornerHBT.lib)."""
    cands: list[Path] = []
    root = os.environ.get("PDK_ROOT")
    pdk = os.environ.get("PDK", "ihp-sg13g2")
    if root:
        cands.append(Path(root) / pdk)
    cands.append(Path.home() / "local" / "pdks" / "ihp-sg13g2")
    for up in Path(__file__).resolve().parents:
        vend = up / "docker" / "pdk" / "ihp-sg13g2"
        if vend.is_dir():
            cands.append(vend)
            break
    for c in cands:
        m = c / "libs.tech" / "ngspice" / "models"
        if (m / "cornerHBT.lib").is_file():
            return m
    raise FileNotFoundError(
        "IHP SG13G2 ngspice models not found. Set PDK_ROOT (and PDK) to an "
        f"IHP-Open-PDK install. Tried: {[str(c) for c in cands]}"
    )


def spiceinit_lines() -> list[str]:
    """.spiceinit content. ngbehavior=hsa is MANDATORY: without it the IHP
    models parse but the HBT conducts 0 current (silently)."""
    lines = [
        f"setcs sourcepath = ( $sourcepath {models_dir()} )",
        "set ngbehavior=hsa",
    ]
    # PDK resistors (rsil/rppd) are OSDI r3_cmc devices; preload the compiled
    # model when the PDK ships it (harmless for HBT-only decks).
    osdi = models_dir().parent / "osdi" / "r3_cmc.osdi"
    if osdi.is_file():
        lines.append(f"osdi {osdi}")
    return lines


def hbt_lib_line(corner: str = "tt") -> str:
    """Bare-name .lib line, resolved through the .spiceinit sourcepath."""
    return f'.lib "cornerHBT.lib" {_CORNER_SECTION[corner]}'


# --------------------------------------------------------------------------
# Parameters (defaults == EIC-verified nominal)
# --------------------------------------------------------------------------


@dataclass
class CellParams:
    """One differential cascode gain cell (one DAC weight unit)."""

    nx: int = 3                 # 3-finger HBTs
    tail_ma: float = 16.0       # tail current per cell (8 mA/device x 2)
    re_ohm: float = 2.5         # emitter degeneration per side (thesis R1/R2)
    cdeg_ff: float = 20.0       # bridging cap across emitters (HF peaking)
    rc_ohm: float = 50.0        # on-chip collector load per side (thesis R_C)
    rb_ohm: float = 50.0        # base termination per side (thesis R_B)
    vcasc: float = 3.25         # cascode base bias
    vcm_in: float = 1.9         # input common-mode bias


@dataclass
class DriverParams:
    vcc: float = 4.0
    cell: CellParams = field(default_factory=CellParams)
    n_lsb: int = 1
    n_msb: int = 2


# --------------------------------------------------------------------------
# DUT subcircuits
# --------------------------------------------------------------------------

# DUT registry: name -> (n_lsb, n_msb)
DUTS = {"lsb": (1, 0), "msb": (0, 2), "pam4": (1, 2)}


def _cell_body(prefix: str, inp: str, inn: str, tail: str, bias: str,
               p: CellParams) -> str:
    """One differential cascode cell. Tail sink is a VCCS (1 mA per volt on
    the bias port) so the same DUT works under ramped-tran and DC/AC drive."""
    nx = p.nx
    return f"""\
* --- cell {prefix} ---
XQ1{prefix} c1{prefix} {inp} e1{prefix} 0 npn13G2 Nx={nx}
XQ2{prefix} c2{prefix} {inn} e2{prefix} 0 npn13G2 Nx={nx}
XQ3{prefix} outp vcasc c1{prefix} 0 npn13G2 Nx={nx}
XQ4{prefix} outn vcasc c2{prefix} 0 npn13G2 Nx={nx}
RE1{prefix} e1{prefix} {tail} {p.re_ohm:g}
RE2{prefix} e2{prefix} {tail} {p.re_ohm:g}
Cdeg{prefix} e1{prefix} e2{prefix} {p.cdeg_ff:g}f
Gtail{prefix} {tail} 0 {bias} 0 1m
"""


def dut_subckt(dut: str, dp: DriverParams | None = None) -> tuple[str, str, list[str]]:
    """Build the DUT .subckt. Returns (subckt_name, netlist_text, port_list).

    Ports:
      lsb/msb : inp inn outp outn vcc vcasc vcmb bias
      pam4    : lsbp lsbn msbp msbn outp outn vcc vcasc vcmb blsb bmsb

    bias/blsb/bmsb: tail-current control, 1 mA per volt (16 V -> 16 mA/cell).
    vcmb: input-termination common-mode reference node (R_B per side).
    On-chip collector loads R_C (per side, to vcc) are part of the DUT.
    Tail current sources are ideal (VCCS) — block-level model fidelity,
    as in the EIC reference (no bias mirrors, no pad parasitics).
    """
    dp = dp or DriverParams()
    p = dp.cell
    n_lsb, n_msb = DUTS[dut]
    name = f"pam4drv_{dut}"
    if dut == "pam4":
        ports = ["lsbp", "lsbn", "msbp", "msbn", "outp", "outn",
                 "vcc", "vcasc", "vcmb", "blsb", "bmsb"]
    else:
        ports = ["inp", "inn", "outp", "outn", "vcc", "vcasc", "vcmb", "bias"]

    lines = [f"* DUT: {name} — {n_lsb} LSB cell(s) + {n_msb} MSB cell(s), "
             f"npn13G2 Nx={p.nx}",
             f".subckt {name} " + " ".join(ports)]
    cells = []
    for i in range(n_lsb):
        inp, inn = ("lsbp", "lsbn") if dut == "pam4" else ("inp", "inn")
        bias = "blsb" if dut == "pam4" else "bias"
        cells.append((f"L{i}", inp, inn, f"tlsb{i}", bias))
    for i in range(n_msb):
        inp, inn = ("msbp", "msbn") if dut == "pam4" else ("inp", "inn")
        bias = "bmsb" if dut == "pam4" else "bias"
        cells.append((f"M{i}", inp, inn, f"tmsb{i}", bias))
    for prefix, inp, inn, tail, bias in cells:
        lines.append(_cell_body(prefix, inp, inn, tail, bias, p))
    # Shared on-chip collector loads.
    lines.append(f"Rcp outp vcc {p.rc_ohm:g}")
    lines.append(f"Rcn outn vcc {p.rc_ohm:g}")
    # Input termination R_B per side to the CM reference.
    inports = [("lsbp", "lsbn"), ("msbp", "msbn")] if dut == "pam4" \
        else [("inp", "inn")]
    for ip, in_ in inports:
        lines.append(f"Rb{ip} {ip} vcmb {p.rb_ohm:g}")
        lines.append(f"Rb{in_} {in_} vcmb {p.rb_ohm:g}")
    lines.append(f".ends {name}")
    return name, "\n".join(lines) + "\n", ports


def _dut_input_ports(dut: str, drive: str) -> tuple[str, str]:
    """Testbench node names wired to the driven DUT input pair."""
    if dut == "pam4":
        return (f"{drive}p", f"{drive}n")
    return ("inp", "inn")


def _tb_dut_instance(dut: str, dp: DriverParams) -> str:
    """XDUT line for a testbench (testbench nodes mirror the port names)."""
    name = f"pam4drv_{dut}"
    if dut == "pam4":
        return (f"XDUT lsbp lsbn msbp msbn outp outn vcc vcasc vcmb "
                f"blsb bmsb {name}")
    return f"XDUT inp inn outp outn vcc vcasc vcmb bias {name}"


# --------------------------------------------------------------------------
# Testbench decks
# --------------------------------------------------------------------------
# `dut_ref` is what goes into the deck for the DUT definition: either the
# full subckt text (self-contained deck, used for temp-dir runs) or an
# ".include ../dut/dut_<name>.spice" line (dumped static decks).


def _bias_sources_tran(dut: str, dp: DriverParams, ramp_ns: float) -> list[str]:
    """Supply/bias sources, ramped from 0 (uic-friendly)."""
    p = dp.cell
    lines = [f"Vcc vcc 0 PWL(0 0 {ramp_ns:g}n {dp.vcc:g})",
             f"Vcasc vcasc 0 PWL(0 0 {ramp_ns:g}n {p.vcasc:g})",
             f"Vcmb vcmb 0 PWL(0 0 {ramp_ns:g}n {p.vcm_in:g})"]
    if dut == "pam4":
        lines.append(f"Vblsb blsb 0 PWL(0 0 {ramp_ns:g}n {p.tail_ma:g})")
        lines.append(f"Vbmsb bmsb 0 PWL(0 0 {ramp_ns:g}n {p.tail_ma:g})")
    else:
        lines.append(f"Vbias bias 0 PWL(0 0 {ramp_ns:g}n {p.tail_ma:g})")
    return lines


def _bias_sources_dc(dut: str, dp: DriverParams) -> list[str]:
    p = dp.cell
    lines = [f"Vcc vcc 0 DC {dp.vcc:g}",
             f"Vcasc vcasc 0 DC {p.vcasc:g}",
             f"Vcmb vcmb 0 DC {p.vcm_in:g}"]
    if dut == "pam4":
        lines.append(f"Vblsb blsb 0 DC {p.tail_ma:g}")
        lines.append(f"Vbmsb bmsb 0 DC {p.tail_ma:g}")
    else:
        lines.append(f"Vbias bias 0 DC {p.tail_ma:g}")
    return lines


def _input_ports(dut: str) -> list[str]:
    return ["lsb", "msb"] if dut == "pam4" else ["in"]


def _tb_output_load(dp: DriverParams) -> list[str]:
    """VNA output reference: 50 ohm/side to VCC (AC ground)."""
    return [f"Rlp outp vcc {Z0:g}", f"Rln outn vcc {Z0:g}"]


def tb_sparam(dut: str, dut_ref: str, *, f_hz: float, drive: str = "msb",
              dp: DriverParams | None = None, corner: str = "tt",
              vac_mv: float = 2.0, ramp_ns: float = 8.0,
              settle_periods: float = 6.0, window_periods: float = 20.0,
              pts_per_period: int = 60,
              out_csv: str = "ss.csv") -> tuple[str, float, float]:
    """Transient sine-probe S-parameter testbench (EIC-validated method).

    Drives one input port differentially through 50 ohm/side sources; the
    other port (pam4 DUT only) idles at CM. drive='both' excites LSB+MSB in
    phase (large-signal swing testbench). Returns (deck, win0_ns, win1_ns).
    """
    dp = dp or DriverParams()
    p = dp.cell
    if dut != "pam4":
        drive = "in"
    period_ns = 1e9 / f_hz
    sine_start = ramp_ns + 1.0
    win0 = sine_start + settle_periods * period_ns
    win1 = win0 + window_periods * period_ns
    dt_ns = period_ns / pts_per_period
    amp = vac_mv * 1e-3 / 2.0

    lines = [f"* TB[{dut}] S-param tone probe f={f_hz:g} drive={drive}"]
    lines += _bias_sources_tran(dut, dp, ramp_ns)
    lines.append(_tb_dut_instance(dut, dp))
    lines += _tb_output_load(dp)
    for port in _input_ports(dut):
        if drive == "both" or port == drive:
            lines.append(f"Vs{port}p s{port}p 0 "
                         f"SIN({p.vcm_in:g} {amp:g} {f_hz:g} {sine_start:g}n)")
            lines.append(f"Vs{port}n s{port}n 0 "
                         f"SIN({p.vcm_in:g} {-amp:g} {f_hz:g} {sine_start:g}n)")
        else:
            lines.append(f"Vs{port}p s{port}p 0 PWL(0 0 {ramp_ns:g}n {p.vcm_in:g})")
            lines.append(f"Vs{port}n s{port}n 0 PWL(0 0 {ramp_ns:g}n {p.vcm_in:g})")
        tp, tn = _dut_input_ports(dut, port) if dut == "pam4" else ("inp", "inn")
        lines.append(f"Rs{port}p s{port}p {tp} {Z0:g}")
        lines.append(f"Rs{port}n s{port}n {tn} {Z0:g}")
    ref = drive if drive != "both" else ("msb" if dut == "pam4" else "in")
    rp, rn = _dut_input_ports(dut, ref) if dut == "pam4" else ("inp", "inn")
    lines.append(dut_ref)
    lines.append(hbt_lib_line(corner))
    lines.append(".options gmin=1e-12 reltol=1e-3")
    lines.append(".control")
    lines.append(f"tran {dt_ns:g}n {win1:g}n uic")
    lines.append(f"wrdata {out_csv} v(outp)-v(outn) "
                 f"v({rp})-v({rn}) v(s{ref}p)-v(s{ref}n)")
    lines.append(".endc")
    lines.append(".GLOBAL GND")
    lines.append(".end")
    return "\n".join(lines) + "\n", win0, win1


def tb_s22(dut: str, dut_ref: str, *, f_hz: float,
           dp: DriverParams | None = None, corner: str = "tt",
           vac_mv: float = 4.0, ramp_ns: float = 8.0,
           settle_periods: float = 6.0, window_periods: float = 20.0,
           pts_per_period: int = 60,
           out_csv: str = "s22.csv") -> tuple[str, float, float]:
    """Output-reflection testbench: inputs idle at CM, differential tone
    injected into OUT+/- through 50 ohm/side referenced to VCC."""
    dp = dp or DriverParams()
    p = dp.cell
    period_ns = 1e9 / f_hz
    sine_start = ramp_ns + 1.0
    win0 = sine_start + settle_periods * period_ns
    win1 = win0 + window_periods * period_ns
    dt_ns = period_ns / pts_per_period
    amp = vac_mv * 1e-3 / 2.0

    lines = [f"* TB[{dut}] S22 probe f={f_hz:g}"]
    lines += _bias_sources_tran(dut, dp, ramp_ns)
    lines.append(_tb_dut_instance(dut, dp))
    for port in _input_ports(dut):
        lines.append(f"Vs{port}p s{port}p 0 PWL(0 0 {ramp_ns:g}n {p.vcm_in:g})")
        lines.append(f"Vs{port}n s{port}n 0 PWL(0 0 {ramp_ns:g}n {p.vcm_in:g})")
        tp, tn = _dut_input_ports(dut, port) if dut == "pam4" else ("inp", "inn")
        lines.append(f"Rs{port}p s{port}p {tp} {Z0:g}")
        lines.append(f"Rs{port}n s{port}n {tn} {Z0:g}")
    # Output probe source rides on VCC (AC ground). No extra Rl load: the
    # probe's 50 ohm/side is the VNA reference termination.
    lines.append(f"Vsop sop 0 SIN({dp.vcc:g} {amp:g} {f_hz:g} {sine_start:g}n)")
    lines.append(f"Vson son 0 SIN({dp.vcc:g} {-amp:g} {f_hz:g} {sine_start:g}n)")
    lines.append(f"Rsop sop outp {Z0:g}")
    lines.append(f"Rson son outn {Z0:g}")
    lines.append(dut_ref)
    lines.append(hbt_lib_line(corner))
    lines.append(".options gmin=1e-12 reltol=1e-3")
    lines.append(".control")
    lines.append(f"tran {dt_ns:g}n {win1:g}n uic")
    lines.append(f"wrdata {out_csv} v(outp)-v(outn) v(sop)-v(son)")
    lines.append(".endc")
    lines.append(".GLOBAL GND")
    lines.append(".end")
    return "\n".join(lines) + "\n", win0, win1


def tb_bias(dut: str, dut_ref: str, *, dp: DriverParams | None = None,
            corner: str = "tt", ramp_ns: float = 8.0, hold_ns: float = 6.0,
            probes: list[str] | None = None,
            out_csv: str = "bias.csv") -> tuple[str, float, float]:
    """Ramp to bias and hold; record output/internal node voltages + I(VCC).

    Internal DUT nodes are probed with dotted subckt access (xdut.<node>).
    Probes the first cell of each flavor present in the DUT by default;
    pass `probes` to override (post-layout netlists have different
    internal node names, so only port-level probes are portable there).
    """
    dp = dp or DriverParams()
    p = dp.cell
    t_end = ramp_ns + hold_ns
    hold0 = ramp_ns + hold_ns * 0.5
    n_lsb, n_msb = DUTS[dut]

    lines = [f"* TB[{dut}] bias point (ramp and hold)"]
    lines += _bias_sources_tran(dut, dp, ramp_ns)
    lines.append(_tb_dut_instance(dut, dp))
    lines += _tb_output_load(dp)
    for port in _input_ports(dut):
        lines.append(f"Vs{port}p s{port}p 0 PWL(0 0 {ramp_ns:g}n {p.vcm_in:g})")
        lines.append(f"Vs{port}n s{port}n 0 PWL(0 0 {ramp_ns:g}n {p.vcm_in:g})")
        tp, tn = _dut_input_ports(dut, port) if dut == "pam4" else ("inp", "inn")
        lines.append(f"Rs{port}p s{port}p {tp} {Z0:g}")
        lines.append(f"Rs{port}n s{port}n {tn} {Z0:g}")
    if probes is None:
        probes = ["v(outp)"]
        if n_lsb:
            probes += ["v(xdut.c1L0)", "v(xdut.e1L0)", "v(xdut.tlsb0)"]
        if n_msb:
            probes += ["v(xdut.c1M0)", "v(xdut.e1M0)", "v(xdut.tmsb0)"]
        probes.append("i(Vcc)")
    lines.append(dut_ref)
    lines.append(hbt_lib_line(corner))
    lines.append(".options gmin=1e-12 reltol=1e-3")
    lines.append(".control")
    lines.append(f"tran {t_end/600.0:g}n {t_end:g}n uic")
    lines.append("wrdata " + out_csv + " " + " ".join(probes))
    lines.append(".endc")
    lines.append(".GLOBAL GND")
    lines.append(".end")
    return "\n".join(lines) + "\n", hold0, t_end


def tb_ac(dut: str, dut_ref: str, *, drive: str = "msb",
          dp: DriverParams | None = None, corner: str = "tt",
          f_start_hz: float = 1e8, f_stop_hz: float = 1e11,
          pts_per_dec: int = 20,
          out_csv: str = "ac.csv") -> str:
    """.op + .ac S21/S11 sweep testbench (ngspice-45; full sweep in one run).

    In-deck power-wave math: S21 = 2*Vout/Vsrc with Vsrc = 1 V differential
    AC EMF; S11 from Zin = Vin/Iin, Iin = (Vsrc-Vin)/(2*Z0). Both written to
    out_csv as dB vs frequency.
    """
    dp = dp or DriverParams()
    if dut != "pam4":
        drive = "in"
    lines = [f"* TB[{dut}] .op/.ac S21+S11 sweep drive={drive} (ngspice-45)"]
    lines += _bias_sources_dc(dut, dp)
    lines.append(_tb_dut_instance(dut, dp))
    lines += _tb_output_load(dp)
    p = dp.cell
    for port in _input_ports(dut):
        acp = " AC 0.5" if (port == drive) else ""
        acn = " AC -0.5" if (port == drive) else ""
        lines.append(f"Vs{port}p s{port}p 0 DC {p.vcm_in:g}{acp}")
        lines.append(f"Vs{port}n s{port}n 0 DC {p.vcm_in:g}{acn}")
        tp, tn = _dut_input_ports(dut, port) if dut == "pam4" else ("inp", "inn")
        lines.append(f"Rs{port}p s{port}p {tp} {Z0:g}")
        lines.append(f"Rs{port}n s{port}n {tn} {Z0:g}")
    rp, rn = _dut_input_ports(dut, drive) if dut == "pam4" else ("inp", "inn")
    lines.append(dut_ref)
    lines.append(hbt_lib_line(corner))
    lines.append(".options gmin=1e-12 reltol=1e-3")
    lines.append(".control")
    lines.append("op")
    lines.append("print v(outp) v(outn) i(Vcc)")
    lines.append(f"ac dec {pts_per_dec} {f_start_hz:g} {f_stop_hz:g}")
    lines.append("let vodiff = v(outp)-v(outn)")
    lines.append(f"let vidiff = v({rp})-v({rn})")
    lines.append("let s21db = db(2*vodiff)")
    lines.append(f"let zin = vidiff*{2*Z0:g}/(1-vidiff)")
    lines.append(f"let s11db = db((zin-{2*Z0:g})/(zin+{2*Z0:g}))")
    lines.append(f"wrdata {out_csv} s21db s11db")
    lines.append(".endc")
    lines.append(".GLOBAL GND")
    lines.append(".end")
    return "\n".join(lines) + "\n"


def tb_ac_s22(dut: str, dut_ref: str, *, dp: DriverParams | None = None,
              corner: str = "tt", f_start_hz: float = 1e8,
              f_stop_hz: float = 1e11, pts_per_dec: int = 20,
              out_csv: str = "acs22.csv") -> str:
    """.op + .ac S22 sweep: inputs at CM, unit differential AC EMF into the
    output through 50 ohm/side referenced to VCC."""
    dp = dp or DriverParams()
    p = dp.cell
    lines = [f"* TB[{dut}] .op/.ac S22 sweep (ngspice-45)"]
    lines += _bias_sources_dc(dut, dp)
    lines.append(_tb_dut_instance(dut, dp))
    for port in _input_ports(dut):
        lines.append(f"Vs{port}p s{port}p 0 DC {p.vcm_in:g}")
        lines.append(f"Vs{port}n s{port}n 0 DC {p.vcm_in:g}")
        tp, tn = _dut_input_ports(dut, port) if dut == "pam4" else ("inp", "inn")
        lines.append(f"Rs{port}p s{port}p {tp} {Z0:g}")
        lines.append(f"Rs{port}n s{port}n {tn} {Z0:g}")
    lines.append(f"Vsop sop 0 DC {dp.vcc:g} AC 0.5")
    lines.append(f"Vson son 0 DC {dp.vcc:g} AC -0.5")
    lines.append(f"Rsop sop outp {Z0:g}")
    lines.append(f"Rson son outn {Z0:g}")
    lines.append(dut_ref)
    lines.append(hbt_lib_line(corner))
    lines.append(".options gmin=1e-12 reltol=1e-3")
    lines.append(".control")
    lines.append("op")
    lines.append(f"ac dec {pts_per_dec} {f_start_hz:g} {f_stop_hz:g}")
    lines.append("let vodiff = v(outp)-v(outn)")
    lines.append(f"let zout = vodiff*{2*Z0:g}/(1-vodiff)")
    lines.append(f"let s22db = db((zout-{2*Z0:g})/(zout+{2*Z0:g}))")
    lines.append(f"wrdata {out_csv} s22db")
    lines.append(".endc")
    lines.append(".GLOBAL GND")
    lines.append(".end")
    return "\n".join(lines) + "\n"


def tb_dc(dut: str, dut_ref: str, *, drive: str = "both",
          vd_max_mv: float = 500.0, step_mv: float = 5.0,
          other_mv: float = 0.0, dp: DriverParams | None = None,
          corner: str = "tt", out_csv: str = "dc.csv") -> str:
    """.dc transfer sweep: differential source EMF vd on the driven port(s)
    through 50 ohm/side, output into the VNA 50 ohm/side load (ngspice-45;
    the self-heating HBT converges in .dc — see README / JPP-361 note).

    drive='both' sweeps LSB+MSB together (large-signal swing curve);
    drive='msb'|'lsb' sweeps one port with the other held at a differential
    EMF of `other_mv` (pam4 DUT: the 4 sweep endpoints are the DAC levels).
    Port-level only, so it runs unmodified on post-layout netlists.
    """
    dp = dp or DriverParams()
    p = dp.cell
    lines = [f"* TB[{dut}] .dc transfer sweep drive={drive} other={other_mv:g}mV"]
    lines += _bias_sources_dc(dut, dp)
    lines.append(_tb_dut_instance(dut, dp))
    lines += _tb_output_load(dp)
    lines.append("Vd d 0 DC 0")
    if dut != "pam4":
        drive = "in"
    for port in _input_ports(dut):
        tp, tn = _dut_input_ports(dut, port) if dut == "pam4" else ("inp", "inn")
        if drive == "both" or port == drive:
            lines.append(f"Bs{port}p s{port}p 0 V = {p.vcm_in:g} + 0.5*v(d)")
            lines.append(f"Bs{port}n s{port}n 0 V = {p.vcm_in:g} - 0.5*v(d)")
        else:
            off = other_mv * 1e-3 / 2.0
            lines.append(f"Vs{port}p s{port}p 0 DC {p.vcm_in + off:g}")
            lines.append(f"Vs{port}n s{port}n 0 DC {p.vcm_in - off:g}")
        lines.append(f"Rs{port}p s{port}p {tp} {Z0:g}")
        lines.append(f"Rs{port}n s{port}n {tn} {Z0:g}")
    lines.append(dut_ref)
    lines.append(hbt_lib_line(corner))
    lines.append(".options gmin=1e-12 reltol=1e-3")
    lines.append(".control")
    vm = vd_max_mv * 1e-3
    lines.append(f"dc Vd {-vm:g} {vm:g} {step_mv*1e-3:g}")
    lines.append(f"wrdata {out_csv} v(outp)-v(outn) i(Vcc)")
    lines.append(".endc")
    lines.append(".GLOBAL GND")
    lines.append(".end")
    return "\n".join(lines) + "\n"


def _nrz_pwl(name: str, node: str, ref: str, bits, *, baud_hz: float,
             vcm: float, swing: float, t0_ns: float, tr_ps: float) -> str:
    """A PWL NRZ source at vcm +/- swing/2 per bit (EIC original)."""
    T = 1e9 / baud_hz
    tr = tr_ps * 1e-3
    pts = [f"0 {vcm + (swing/2 if bits[0] else -swing/2):g}"]
    t = t0_ns
    for b in bits:
        lvl = vcm + (swing / 2 if b else -swing / 2)
        pts.append(f"{t:g}n {pts[-1].split()[-1]}")
        pts.append(f"{t + tr:g}n {lvl:g}")
        t += T
    return f"{name} {node} {ref} PWL({' '.join(pts)})"


def tb_eye(dut_ref: str, *, msb_bits, lsb_bits, dp: DriverParams | None = None,
           corner: str = "tt", baud_hz: float = 48e9, vswing_mv: float = 200.0,
           ramp_ns: float = 8.0, tr_ps: float = 4.0,
           out_csv: str = "eye.csv") -> tuple[str, float, float]:
    """48 GBaud PAM-4 eye testbench (pam4 DUT only): independent MSB/LSB NRZ
    streams summed into PAM-4 at OUT+/-."""
    dp = dp or DriverParams()
    p = dp.cell
    T_ns = 1e9 / baud_hz
    data_start = ramp_ns + 2.0
    t_end = data_start + len(msb_bits) * T_ns + 1.0
    lines = [f"* TB[pam4] {baud_hz/1e9:g} GBaud PAM-4 eye"]
    lines += _bias_sources_tran("pam4", dp, ramp_ns)
    lines.append(_tb_dut_instance("pam4", dp))
    lines += _tb_output_load(dp)
    sw = vswing_mv * 1e-3
    for port, bits in (("msb", msb_bits), ("lsb", lsb_bits)):
        lines.append(_nrz_pwl(f"Vs{port}p", f"s{port}p", "0", bits,
                              baud_hz=baud_hz, vcm=p.vcm_in, swing=sw,
                              t0_ns=data_start, tr_ps=tr_ps))
        lines.append(_nrz_pwl(f"Vs{port}n", f"s{port}n", "0",
                              [1 - b for b in bits],
                              baud_hz=baud_hz, vcm=p.vcm_in, swing=sw,
                              t0_ns=data_start, tr_ps=tr_ps))
        lines.append(f"Rs{port}p s{port}p {port}p {Z0:g}")
        lines.append(f"Rs{port}n s{port}n {port}n {Z0:g}")
    lines.append(dut_ref)
    lines.append(hbt_lib_line(corner))
    lines.append(".options gmin=1e-12 reltol=1e-3")
    lines.append(".control")
    lines.append(f"tran {T_ns/40.0:g}n {t_end:g}n uic")
    lines.append(f"wrdata {out_csv} v(outp)-v(outn)")
    lines.append(".endc")
    lines.append(".GLOBAL GND")
    lines.append(".end")
    return "\n".join(lines) + "\n", data_start, t_end


# --------------------------------------------------------------------------
# Execution + extraction
# --------------------------------------------------------------------------


def run_deck(deck: str, out_files: list[str], *, timeout_s: float = 300.0
             ) -> tuple[dict[str, np.ndarray | None], str]:
    """Run a deck in a temp dir (with the required .spiceinit); load wrdata
    outputs. Returns ({filename: array-or-None}, ngspice log)."""
    if shutil.which("ngspice") is None:
        raise FileNotFoundError("ngspice not on PATH")
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / ".spiceinit").write_text("\n".join(spiceinit_lines()) + "\n")
        (d / "deck.spice").write_text(deck)
        proc = subprocess.run(["ngspice", "-b", "deck.spice"], cwd=d,
                              capture_output=True, text=True,
                              timeout=timeout_s)
        out: dict[str, np.ndarray | None] = {}
        for f in out_files:
            fp = d / f
            out[f] = np.loadtxt(fp) if fp.exists() else None
    return out, proc.stdout + proc.stderr


def _dft_bin(t: np.ndarray, x: np.ndarray, f_hz: float) -> complex:
    """Single-frequency phasor of x(t) at f_hz (least-squares cos/sin
    projection, robust to a non-integer number of periods)."""
    w = 2 * np.pi * f_hz
    c = np.cos(w * t)
    s = np.sin(w * t)
    n = len(t)
    a = 2.0 / n * np.dot(x, c)
    b = 2.0 / n * np.dot(x, s)
    return complex(a, -b)


def _resolve_dut_ref(dut: str, dp: DriverParams,
                     dut_ref: str | None) -> str:
    """Schematic subckt text by default; pass `dut_ref` (e.g. from
    layout/pex_sim.wrap_layout_dut) to run the same bench on a post-layout
    netlist."""
    if dut_ref is not None:
        return dut_ref
    _, sub, _ = dut_subckt(dut, dp)
    return sub


def run_sparam(dut: str, *, f_hz: float, drive: str = "msb",
               dp: DriverParams | None = None, dut_ref: str | None = None,
               timeout_s: float = 240.0, **kw) -> dict[str, float]:
    """One transient tone-probe point -> S21(dB), S11(dB), phase, Vpp."""
    dp = dp or DriverParams()
    sub = _resolve_dut_ref(dut, dp, dut_ref)
    deck, w0, w1 = tb_sparam(dut, sub, f_hz=f_hz, drive=drive, dp=dp, **kw)
    out, log = run_deck(deck, ["ss.csv"], timeout_s=timeout_s)
    data = out["ss.csv"]
    if data is None:
        return {"ok": 0.0, "log": log}  # type: ignore[dict-item]
    t = data[:, 0]
    m = (t >= w0 * 1e-9) & (t <= w1 * 1e-9)
    t, vout, vin, vsrc = t[m], data[m, 1], data[m, 3], data[m, 5]
    Vout = _dft_bin(t, vout, f_hz)
    Vin = _dft_bin(t, vin, f_hz)
    Vsrc = _dft_bin(t, vsrc, f_hz)
    s21 = 2.0 * Vout / Vsrc
    iin = (Vsrc - Vin) / (2.0 * Z0)
    zin = Vin / iin if abs(iin) > 0 else complex(1e9)
    s11 = (zin - 2.0 * Z0) / (zin + 2.0 * Z0)
    return {
        "ok": 1.0,
        "f_ghz": f_hz / 1e9,
        "s21_db": 20.0 * np.log10(abs(s21)),
        "s21_phase_deg": float(np.angle(s21, deg=True)),
        "s11_db": 20.0 * np.log10(abs(s11)),
        "vout_pp_mv": float(2 * abs(Vout) * 1e3),
        "vin_pp_mv": float(2 * abs(Vin) * 1e3),
    }


def run_s22(dut: str, *, f_hz: float, dp: DriverParams | None = None,
            dut_ref: str | None = None, timeout_s: float = 240.0,
            **kw) -> dict[str, float]:
    """One transient output-reflection point -> S22(dB)."""
    dp = dp or DriverParams()
    sub = _resolve_dut_ref(dut, dp, dut_ref)
    deck, w0, w1 = tb_s22(dut, sub, f_hz=f_hz, dp=dp, **kw)
    out, log = run_deck(deck, ["s22.csv"], timeout_s=timeout_s)
    data = out["s22.csv"]
    if data is None:
        return {"ok": 0.0, "log": log}  # type: ignore[dict-item]
    t = data[:, 0]
    m = (t >= w0 * 1e-9) & (t <= w1 * 1e-9)
    t, vout, vsrc = t[m], data[m, 1], data[m, 3]
    Vout = _dft_bin(t, vout, f_hz)
    Vsrc = _dft_bin(t, vsrc, f_hz)
    iin = (Vsrc - Vout) / (2.0 * Z0)
    zout = Vout / iin if abs(iin) > 0 else complex(1e9)
    s22 = (zout - 2.0 * Z0) / (zout + 2.0 * Z0)
    return {"ok": 1.0, "f_ghz": f_hz / 1e9,
            "s22_db": 20.0 * np.log10(abs(s22))}


def run_bias(dut: str, *, dp: DriverParams | None = None,
             dut_ref: str | None = None, timeout_s: float = 120.0,
             **kw) -> dict[str, float]:
    """Bias testbench -> averaged node voltages, per-device V_CE, power.

    Uses the default (schematic) internal-node probes; for post-layout
    netlists build the deck via tb_bias(..., probes=[...]) instead."""
    dp = dp or DriverParams()
    sub = _resolve_dut_ref(dut, dp, dut_ref)
    deck, hold0, _ = tb_bias(dut, sub, dp=dp, **kw)
    out, log = run_deck(deck, ["bias.csv"], timeout_s=timeout_s)
    data = out["bias.csv"]
    if data is None:
        return {"ok": 0.0, "log": log}  # type: ignore[dict-item]
    n_lsb, n_msb = DUTS[dut]
    names = ["outp"]
    if n_lsb:
        names += ["c1L", "e1L", "tL"]
    if n_msb:
        names += ["c1M", "e1M", "tM"]
    names.append("icc")
    t = data[:, 0]
    m = t >= hold0 * 1e-9
    av = {k: float(np.mean(data[m, 1 + 2 * i])) for i, k in enumerate(names)}
    icc = abs(av["icc"])
    res: dict[str, float] = {"ok": 1.0, "outp_v": av["outp"],
                             "i_supply_ma": icc * 1e3,
                             "power_mw": icc * dp.vcc * 1e3}
    if n_lsb:
        res["vce_q1_lsb"] = av["c1L"] - av["e1L"]
        res["vce_q3_lsb"] = av["outp"] - av["c1L"]
        res["tail_lsb_v"] = av["tL"]
    if n_msb:
        res["vce_q1_msb"] = av["c1M"] - av["e1M"]
        res["vce_q3_msb"] = av["outp"] - av["c1M"]
        res["tail_msb_v"] = av["tM"]
    return res


def run_ac(dut: str, *, drive: str = "msb", dp: DriverParams | None = None,
           dut_ref: str | None = None, timeout_s: float = 240.0,
           **kw) -> dict[str, object]:
    """Full .op/.ac sweep -> arrays f_ghz, s21_db, s11_db (ngspice-45)."""
    dp = dp or DriverParams()
    sub = _resolve_dut_ref(dut, dp, dut_ref)
    deck = tb_ac(dut, sub, drive=drive, dp=dp, **kw)
    out, log = run_deck(deck, ["ac.csv"], timeout_s=timeout_s)
    data = out["ac.csv"]
    if data is None:
        return {"ok": 0.0, "log": log}
    return {"ok": 1.0, "f_ghz": data[:, 0] / 1e9,
            "s21_db": data[:, 1], "s11_db": data[:, 3]}


def run_ac_s22(dut: str, *, dp: DriverParams | None = None,
               dut_ref: str | None = None, timeout_s: float = 240.0,
               **kw) -> dict[str, object]:
    """Full .op/.ac S22 sweep -> arrays f_ghz, s22_db (ngspice-45)."""
    dp = dp or DriverParams()
    sub = _resolve_dut_ref(dut, dp, dut_ref)
    deck = tb_ac_s22(dut, sub, dp=dp, **kw)
    out, log = run_deck(deck, ["acs22.csv"], timeout_s=timeout_s)
    data = out["acs22.csv"]
    if data is None:
        return {"ok": 0.0, "log": log}
    return {"ok": 1.0, "f_ghz": data[:, 0] / 1e9, "s22_db": data[:, 1]}


def run_dc(dut: str, *, drive: str = "both", dp: DriverParams | None = None,
           dut_ref: str | None = None, timeout_s: float = 240.0,
           **kw) -> dict[str, object]:
    """.dc transfer sweep -> arrays vd_v (source EMF, diff), vout_diff_v,
    i_vcc_a (ngspice-45)."""
    dp = dp or DriverParams()
    sub = _resolve_dut_ref(dut, dp, dut_ref)
    deck = tb_dc(dut, sub, drive=drive, dp=dp, **kw)
    out, log = run_deck(deck, ["dc.csv"], timeout_s=timeout_s)
    data = out["dc.csv"]
    if data is None:
        return {"ok": 0.0, "log": log}
    return {"ok": 1.0, "vd_v": data[:, 0], "vout_diff_v": data[:, 1],
            "i_vcc_a": data[:, 3]}


def run_eye(*, msb_bits, lsb_bits, dp: DriverParams | None = None,
            dut_ref: str | None = None, baud_hz: float = 48e9,
            timeout_s: float = 600.0, **kw):
    """PAM-4 eye transient -> (t[s], vout_diff[V], data_start_ns, baud, log)."""
    dp = dp or DriverParams()
    sub = _resolve_dut_ref("pam4", dp, dut_ref)
    deck, t0, _ = tb_eye(sub, msb_bits=msb_bits, lsb_bits=lsb_bits, dp=dp,
                         baud_hz=baud_hz, **kw)
    out, log = run_deck(deck, ["eye.csv"], timeout_s=timeout_s)
    data = out["eye.csv"]
    if data is None:
        return None, None, t0, baud_hz, log
    return data[:, 0], data[:, 1], t0, baud_hz, ""
