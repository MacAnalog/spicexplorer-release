#!/usr/bin/env python3
"""PEX + pre/post-layout simulation for the PAM-4 driver layout DUTs.

Pipeline per DUT (lsb | msb | pam4):

  1. pre-layout : ngspice .op/.ac on ``out/dut_<d>_sim.spice`` (the layout's
     device set on the PDK models — rsil / cap_cmim / npn13G2 — no wiring)
  2. kpex       : klayout-pex 2.5D extraction of ``out/dut_<d>.gds`` against
     the LVS reference (mode CC by default, RC optional)
  3. post-layout: the kpex netlist converted to ngspice X-cards, same bench
  4. metrics    : LF S21, f3dB, worst S11 <= 32 GHz, P(vcc) — pre vs post

The testbench mirrors ``../testbenches/driver_lib.py`` tb_ac (power-wave
S21 = 2*Vout/Vsrc into 50 ohm/side, S11 via Zin), adapted to the layout DUT
port convention (tails + sub are ports; ideal VCCS tails live in the bench).

    uv run python pex_sim.py --dut all                   # -> out/pex_report.yaml
    uv run python pex_sim.py --dut pam4 --mode RC --skip-pex   # reuse existing PEX
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
# driver_lib.py is vendored alongside this module in the analog-db layout entry
# (upstream it lived in ../testbenches/). Import it from HERE so the subtree is
# self-contained under circuits/<id>/pdk/<pdk>/layout-<NNN>-<slug>/.
sys.path.insert(0, HERE)
from driver_lib import Z0, hbt_lib_line, run_deck  # noqa: E402

# kpex executable and the KLayout >= 0.30 binary its LVS step drives
# (needs Ruby >= 2.6). Resolved from PATH; override via env KPEX /
# KPEX_KLAYOUT_EXE when they live elsewhere (see README "EDA tool setup").
KPEX = os.environ.get("KPEX") or shutil.which("kpex")
KPEX_KLAYOUT = os.environ.get("KPEX_KLAYOUT_EXE") or shutil.which("klayout")

VCC, VCASC, VCM, TAIL_MA = 4.0, 3.25, 1.9, 16.0
BIASES = {"vcc": VCC, "vcasc": VCASC, "vcmb": VCM, "tail_ma": TAIL_MA}

DUT_INPUTS = {"lsb": ["inp", "inn"], "msb": ["inp", "inn"],
              "pam4": ["lsbp", "lsbn", "msbp", "msbn"]}
DUT_TAILS = {"lsb": ["tail"], "msb": ["tail0", "tail1"],
             "pam4": ["tlsb0", "tmsb0", "tmsb1"]}


# ------------------------------------------------------------- pex netlist
def parse_subckt_ports(path: str) -> tuple[str, list[str]]:
    txt = open(path).read()
    # join continuation lines
    txt = re.sub(r"\n\+\s*", " ", txt)
    m = re.search(r"^\.subckt\s+(\S+)\s+(.*)$", txt,
                  re.IGNORECASE | re.MULTILINE)
    if not m:
        raise ValueError(f"no .subckt in {path}")
    return m.group(1), m.group(2).split()


def convert_pex_netlist(pex_path: str, out_path: str) -> tuple[str, list[str]]:
    """kpex output -> ngspice-runnable subckt: Q/R/C device cards become
    X-cards on the PDK subckt models; parasitic R/C cards pass through."""
    raw = open(pex_path).read()
    raw = re.sub(r"\n\+\s*", " ", raw)          # join continuations
    name, ports = None, []
    sub_net = "sub"
    lines_out: list[str] = []
    for line in raw.splitlines():
        ls = line.strip()
        low = ls.lower()
        if low.startswith(".subckt"):
            toks = ls.split()
            name, ports = toks[1], toks[2:]
            if "sub" not in [t.lower() for t in ports]:
                sub_net = "0"
            lines_out.append(ls)
            continue
        if low.startswith(".ends"):
            lines_out.append(ls)
            continue
        if not ls or ls.startswith("*"):
            lines_out.append(ls)
            continue
        ls = ls.replace("VSUBS", sub_net)   # parasitic substrate node
        toks = ls.split()
        el = toks[0]
        if el.upper().startswith("Q") and "npn13g2" in low:
            # Q$1 c b e s npn13G2 we=0.07 le=0.9 Nx=3 m=1 -> X.. Nx=3
            nets = toks[1:5]
            kv = dict(t.split("=", 1) for t in toks[6:] if "=" in t)
            nx = int(float(kv.get("Nx", 1))) * int(float(kv.get("m", 1)))
            lines_out.append(
                f"X{el.replace('$', '_')} {' '.join(nets)} npn13G2 Nx={nx}")
        elif el.upper().startswith("R") and " rsil " in f" {low} ":
            # R$5 n1 n2 sub <w> rsil l=<l> ps=0 b=0 m=1 (dims in um, no unit)
            nets = toks[1:4]
            w_um = toks[4]
            kv = dict(t.split("=", 1) for t in toks[6:] if "=" in t)
            lines_out.append(
                f"X{el.replace('$', '_')} {' '.join(nets)} rsil "
                f"w={w_um}u l={kv.get('l', '0.5')}u m={kv.get('m', '1')}")
        elif el.upper().startswith("C") and "cap_cmim" in low:
            nets = toks[1:3]
            kv = dict(t.split("=", 1) for t in toks[5:] if "=" in t)
            lines_out.append(
                f"X{el.replace('$', '_')} {' '.join(nets)} cap_cmim "
                f"w={kv.get('w', '1')}u l={kv.get('l', '1')}u")
        else:
            lines_out.append(ls)   # parasitic R/C card or comment
    _reinsert_caps(lines_out, pex_path)
    with open(out_path, "w") as f:
        f.write("\n".join(lines_out) + "\n")
    assert name is not None
    return name, ports


def _reinsert_caps(lines_out: list[str], pex_path: str) -> None:
    """Re-add the intentional Cdeg cap_cmim devices dropped by the MIM-less
    kpex run. Each cap bridges the two emitter nets of one cell — found as
    the two RE rsil devices (widest rsil) sharing a common (tail) net."""
    dut = re.search(r"pam4drv_(\w+?)_lay", pex_path).group(1)
    sim = open(os.path.join(OUT, f"dut_{dut}_sim.spice")).read()
    cap_m = re.findall(r"^XCdeg\S*\s+\S+\s+\S+\s+cap_cmim\s+(w=\S+)\s+(l=\S+)",
                       sim, re.MULTILINE)
    rew_m = re.findall(r"^XRRE\S+\s+\S+\s+\S+\s+\S+\s+rsil\s+w=(\S+?)u",
                       sim, re.MULTILINE)
    if not cap_m or not rew_m:
        return
    w_arg, l_arg = cap_m[0]
    re_w = float(rew_m[0])
    res = []
    for line in lines_out:
        m = re.match(r"X\S+\s+(\S+)\s+(\S+)\s+\S+\s+rsil\s+w=(\S+?)u", line)
        if m and abs(float(m.group(3)) - re_w) < 1e-6:
            res.append([m.group(1), m.group(2)])
    used = set()
    k = 0
    for i in range(len(res)):
        if i in used:
            continue
        for j in range(i + 1, len(res)):
            if j in used:
                continue
            shared = set(res[i]) & set(res[j])
            if len(shared) == 1:
                (sn,) = shared
                ea = next(n for n in res[i] if n != sn)
                eb = next(n for n in res[j] if n != sn)
                idx = max(ii for ii, ll in enumerate(lines_out)
                          if ll.lower().startswith(".ends"))
                lines_out.insert(
                    idx, f"XCdeg_r{k} {ea} {eb} cap_cmim {w_arg} {l_arg}")
                used.update((i, j))
                k += 1
                break


def wrap_layout_dut(dut: str, subckt_path: str) -> str:
    """Adapter: wrap a converted layout netlist (convert_pex_netlist output,
    or a dut_<d>_sim.spice) in the SCHEMATIC DUT port convention, so every
    testbench in ../testbenches/driver_lib.py runs on it unmodified via
    their `dut_ref=` argument.

    Maps the bias ports to per-tail 1 mA/V VCCS (as inside the schematic
    DUT), grounds the substrate port, and appends the resistor/cap corner
    libs the layout devices need.
    """
    name, ports = parse_subckt_ports(subckt_path)
    if dut == "pam4":
        outer = "lsbp lsbn msbp msbn outp outn vcc vcasc vcmb blsb bmsb"
        gmap = {"tlsb0": "blsb", "tmsb0": "bmsb", "tmsb1": "bmsb"}
    else:
        outer = "inp inn outp outn vcc vcasc vcmb bias"
        gmap = {t: "bias" for t in DUT_TAILS[dut]}
    lines = [f"* post-layout adapter: {name} -> pam4drv_{dut} schematic ports",
             f".subckt pam4drv_{dut} {outer}",
             f"Xlay {' '.join(ports)} {name}"]
    for tail, bias in gmap.items():
        lines.append(f"G{tail} {tail} 0 {bias} 0 1m")
    lines.append("Vsub sub 0 DC 0")
    lines.append(f".ends pam4drv_{dut}")
    lines.append(f'.include "{os.path.abspath(subckt_path)}"')
    lines.append('.lib "cornerRES.lib" res_typ')
    lines.append('.lib "cornerCAP.lib" cap_typ')
    return "\n".join(lines) + "\n"


# kpex's ihp-sg13g2 process tables have no entry for the MIM cap layer
# (`cmim_top` is `<TODO>` -> KeyError in the 2.5D extractor). Workaround:
# extract on a GDS copy with the MIM device layers stripped (the plates stay
# as plain Metal5/TopMetal1, so their coupling is still extracted) and
# re-insert the intentional cap as a device afterwards.
MIM_LAYERS = [(36, 0), (129, 0), (69, 0)]   # MIM, Vmim, MemCap


def _strip_mim(gds_in: str, gds_out: str) -> None:
    import klayout.db as kdb
    ly = kdb.Layout()
    ly.read(gds_in)
    for (l, d) in MIM_LAYERS:
        idx = ly.find_layer(l, d)
        if idx is not None:
            ly.delete_layer(idx)
    ly.write(gds_out)


def run_kpex(dut: str, mode: str = "CC") -> str:
    cell = f"pam4drv_{dut}_lay"
    out_dir = os.path.join(OUT, "pex", dut)
    os.makedirs(out_dir, exist_ok=True)
    gds = os.path.join(out_dir, f"dut_{dut}_nomim.gds")
    _strip_mim(os.path.join(OUT, f"dut_{dut}.gds"), gds)
    # kpex flavour schematic (3-node rsil) minus the now-absent cap devices
    schem = os.path.join(out_dir, f"dut_{dut}_kpex_nomim.spice")
    with open(os.path.join(OUT, f"dut_{dut}_kpex.spice")) as f:
        lines = [l for l in f
                 if not (l.startswith("C") and "cap_cmim" in l)]
    with open(schem, "w") as f:
        f.writelines(lines)
    if not KPEX:
        raise RuntimeError("kpex not found — install klayout-pex or set KPEX "
                           "(see README 'EDA tool setup')")
    env = dict(os.environ)
    if KPEX_KLAYOUT:
        env.setdefault("KPEX_KLAYOUT_EXE", KPEX_KLAYOUT)
    if "PDK_ROOT" not in env:
        raise RuntimeError("PDK_ROOT is not set (the directory containing "
                           "ihp-sg13g2)")
    cmd = [KPEX, "--pdk", "ihp-sg13g2", "--gds", gds, "--cell", cell,
           "--schematic", schem, "--2.5D", "--mode", mode,
           "--out_dir", out_dir]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    spice = os.path.join(out_dir, f"dut_{dut}_nomim__{cell}",
                         f"{cell}_k25d_pex_netlist.spice")
    if r.returncode != 0 or not os.path.exists(spice):
        raise RuntimeError(f"kpex failed for {dut}:\n" +
                           (r.stdout + r.stderr)[-3000:])
    return spice


# ------------------------------------------------------------- testbench
def tb_ac_layout(dut: str, subckt_path: str, subckt_name: str,
                 ports: list[str], *, drive: str = "msb",
                 corner: str = "tt", out_csv: str = "ac.csv",
                 biases: dict | None = None) -> str:
    """.op + .ac S21/S11 bench around a layout DUT subckt (any port order).

    ``biases`` overrides {vcc, vcasc, vcmb, tail_ma} — the electrical
    operating-point knobs for the sizing loop."""
    b = dict(BIASES, **(biases or {}))
    tails = DUT_TAILS[dut]
    groups = ["lsb", "msb"] if dut == "pam4" else ["in"]
    if dut != "pam4":
        drive = "in"
    lines = [f"* layout TB[{dut}] .op/.ac drive={drive}",
             f'.include "{subckt_path}"',
             f"Vcc vcc 0 DC {b['vcc']:g}",
             f"Vcasc vcasc 0 DC {b['vcasc']:g}",
             f"Vcmb vcmb 0 DC {b['vcmb']:g}",
             f"Vbias bias 0 DC {b['tail_ma']:g}",
             "Vsub sub 0 DC 0"]
    for t in tails:
        lines.append(f"G{t} {t} 0 bias 0 1m")
    lines.append(f"Rlp outp vcc {Z0:g}")
    lines.append(f"Rln outn vcc {Z0:g}")
    for g in groups:
        tp, tn = (f"{g}p", f"{g}n") if dut == "pam4" else ("inp", "inn")
        acp = " AC 0.5" if g == drive else ""
        acn = " AC -0.5" if g == drive else ""
        lines.append(f"Vs{g}p s{g}p 0 DC {b['vcmb']:g}{acp}")
        lines.append(f"Vs{g}n s{g}n 0 DC {b['vcmb']:g}{acn}")
        lines.append(f"Rs{g}p s{g}p {tp} {Z0:g}")
        lines.append(f"Rs{g}n s{g}n {tn} {Z0:g}")
    rp, rn = ((f"{drive}p", f"{drive}n") if dut == "pam4"
              else ("inp", "inn"))
    lines.append(f"X0 {' '.join(ports)} {subckt_name}")
    lines.append(hbt_lib_line(corner))
    lines.append('.lib "cornerRES.lib" res_typ')
    lines.append('.lib "cornerCAP.lib" cap_typ')
    lines.append(".options gmin=1e-12 reltol=1e-3")
    lines.append(".control")
    lines.append("op")
    lines.append("print v(outp) v(outn) i(Vcc)")
    lines.append("ac dec 20 1e8 1e11")
    lines.append("let vodiff = v(outp)-v(outn)")
    lines.append(f"let vidiff = v({rp})-v({rn})")
    lines.append("let s21db = db(2*vodiff)")
    lines.append(f"let zin = vidiff*{2 * Z0:g}/(1-vidiff)")
    lines.append(f"let s11db = db((zin-{2 * Z0:g})/(zin+{2 * Z0:g}))")
    lines.append(f"wrdata {out_csv} s21db s11db")
    lines.append(".endc")
    lines.append(".GLOBAL GND")
    lines.append(".end")
    return "\n".join(lines) + "\n"


def ac_metrics(dut: str, subckt_path: str, *, drive: str = "msb",
               label: str = "", biases: dict | None = None) -> dict:
    name, ports = parse_subckt_ports(subckt_path)
    deck = tb_ac_layout(dut, subckt_path, name, ports, drive=drive,
                        biases=biases)
    out, log = run_deck(deck, ["ac.csv"], timeout_s=600.0)
    data = out["ac.csv"]
    if data is None:
        raise RuntimeError(f"AC failed [{label} {dut} {drive}]:\n" + log[-2500:])
    f = data[:, 0]
    s21 = data[:, 1]
    s11 = data[:, 3]
    lf = float(s21[np.argmin(np.abs(f - 1e9))])
    thr = lf - 3.0
    above = s21 >= thr
    f3 = float(f[-1])
    for i in range(len(f) - 1):
        if above[i] and not above[i + 1]:
            f3 = float(np.interp(thr, [s21[i + 1], s21[i]],
                                 [f[i + 1], f[i]]))
            break
    m32 = f <= 32e9
    s11w = float(s11[m32].max())
    mi = re.search(r"i\(vcc\)\s*=\s*([-\d.e+]+)", log, re.IGNORECASE)
    vcc_v = dict(BIASES, **(biases or {}))["vcc"]
    p_mw = abs(float(mi.group(1))) * vcc_v * 1e3 if mi else float("nan")
    return {"s21_lf_db": round(lf, 3), "f3db_ghz": round(f3 / 1e9, 2),
            "s11_worst_db": round(s11w, 2), "power_mw": round(p_mw, 2)}


# ------------------------------------------------------------- main
def characterize(dut: str, *, mode: str = "CC", skip_pex: bool = False,
                 corner: str = "tt", biases: dict | None = None) -> dict:
    drives = ["lsb", "msb"] if dut == "pam4" else ["in"]
    pre_path = os.path.join(OUT, f"dut_{dut}_sim.spice")
    res: dict = {"dut": dut, "pex_mode": mode, "pre": {}, "post": {}}
    for drv in drives:
        res["pre"][drv] = ac_metrics(dut, pre_path, drive=drv, label="pre",
                                     biases=biases)
    pex_raw = os.path.join(OUT, "pex", dut,
                           f"dut_{dut}__pam4drv_{dut}_lay",
                           f"pam4drv_{dut}_lay_k25d_pex_netlist.spice")
    if not skip_pex or not os.path.exists(pex_raw):
        pex_raw = run_kpex(dut, mode)
    post_path = os.path.join(OUT, "pex", f"dut_{dut}_post.spice")
    convert_pex_netlist(pex_raw, post_path)
    for drv in drives:
        res["post"][drv] = ac_metrics(dut, post_path, drive=drv,
                                      label="post", biases=biases)
    res["delta"] = {
        drv: {k: round(res["post"][drv][k] - res["pre"][drv][k], 3)
              for k in res["pre"][drv]}
        for drv in drives}
    n_par = sum(1 for l in open(post_path)
                if l.startswith("C") or l.startswith("R"))
    res["n_parasitics"] = n_par
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description="PEX + pre/post AC comparison")
    ap.add_argument("--dut", default="all",
                    choices=["lsb", "msb", "pam4", "all"])
    ap.add_argument("--mode", default="CC", choices=["CC", "RC", "R"])
    ap.add_argument("--skip-pex", action="store_true",
                    help="reuse an existing kpex netlist")
    a = ap.parse_args()
    duts = ["lsb", "msb", "pam4"] if a.dut == "all" else [a.dut]
    report = {}
    for d in duts:
        r = characterize(d, mode=a.mode, skip_pex=a.skip_pex)
        report[d] = r
        for drv in r["pre"]:
            pre, post, dl = r["pre"][drv], r["post"][drv], r["delta"][drv]
            print(f"[{d}:{drv}] S21 {pre['s21_lf_db']} -> "
                  f"{post['s21_lf_db']} dB (d={dl['s21_lf_db']}); "
                  f"BW {pre['f3db_ghz']} -> {post['f3db_ghz']} GHz "
                  f"(d={dl['f3db_ghz']}); S11 {pre['s11_worst_db']} -> "
                  f"{post['s11_worst_db']} dB; "
                  f"P {pre['power_mw']} -> {post['power_mw']} mW")
    out_yaml = os.path.join(OUT, "pex_report.yaml")
    try:
        import yaml
        with open(out_yaml, "w") as f:
            yaml.safe_dump(report, f, sort_keys=False)
    except ImportError:
        out_yaml = out_yaml.replace(".yaml", ".json")
        with open(out_yaml, "w") as f:
            json.dump(report, f, indent=2)
    print(f"report: {out_yaml}")


if __name__ == "__main__":
    main()
