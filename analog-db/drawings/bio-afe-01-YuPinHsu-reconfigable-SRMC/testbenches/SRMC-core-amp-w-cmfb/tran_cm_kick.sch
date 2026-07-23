v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {amplifier/tran_cm_kick -- SRMC-core-amp-w-cmfb standalone bench (amp_031_srmc_core_cmfb)} 52.5 -1402.5 0 0 0.4 0.4 {}
B 2 1820 -925 2780 -765 {flags=graph
y1=0.4
y2=0.8
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=2e-05
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
dataset=-1
unitx=u
logx=0
logy=0
color="4"
node="vocm"
rainbow=0}
C {bio-afe-01-YuPinHsu-reconfigable-SRMC/SRMC-core-amp-w-cmfb.sym} 1015 -725 0 0 {name=XDUT}
C {devices/lab_wire.sym} 995 -855 0 0 {name=l1 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 995 -835 0 0 {name=l2 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 1295 -755 0 0 {name=l3 sig_type=std_logic lab=voutp}
C {devices/lab_wire.sym} 1295 -775 0 0 {name=l4 sig_type=std_logic lab=voutn}
C {devices/lab_wire.sym} 1235 -885 0 0 {name=l5 sig_type=std_logic lab=vdd}
C {devices/lab_wire.sym} 1265 -885 0 0 {name=l6 sig_type=std_logic lab=vss}
C {devices/vsource.sym} 965 -1290 0 0 {name=Vdd value="dc \{VDD\}" savecurrent=true}
C {devices/lab_wire.sym} 965 -1320 0 0 {name=l7 sig_type=std_logic lab=vdd}
C {devices/gnd.sym} 965 -1260 0 0 {name=g8 lab=0}
C {devices/vsource.sym} 1065 -1290 0 0 {name=Vss value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 1065 -1320 0 0 {name=l9 sig_type=std_logic lab=vss}
C {devices/gnd.sym} 1065 -1260 0 0 {name=g10 lab=0}
C {devices/vsource.sym} 535 -825 0 0 {name=Vcm value="dc \{VCM\}" savecurrent=true}
C {devices/lab_wire.sym} 535 -855 0 0 {name=l11 sig_type=std_logic lab=vcm}
C {devices/gnd.sym} 535 -795 0 0 {name=g12 lab=0}
C {devices/vsource.sym} 805 -825 0 0 {name=Vinp value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 805 -855 0 0 {name=l13 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 805 -795 0 0 {name=l14 sig_type=std_logic lab=vcm}
C {devices/vsource.sym} 665 -905 0 0 {name=Vinn value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 665 -935 0 0 {name=l15 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 665 -875 0 0 {name=l16 sig_type=std_logic lab=vcm}
C {devices/capa.sym} 1580 -860 0 0 {name=CLoadp m=1 value=\{CL\}}
C {devices/lab_wire.sym} 1580 -890 0 0 {name=l17 sig_type=std_logic lab=voutp}
C {devices/gnd.sym} 1580 -830 0 0 {name=g18 lab=0}
C {devices/capa.sym} 1680 -890 0 0 {name=CLoadn m=1 value=\{CL\}}
C {devices/lab_wire.sym} 1680 -920 0 0 {name=l19 sig_type=std_logic lab=voutn}
C {devices/gnd.sym} 1680 -860 0 0 {name=g20 lab=0}
C {devices/isource.sym} 1500 -660 0 0 {name=Icmp value="pulse(0 \{ICM/2\} \{TKICK\} 10n 10n \{TREL-TKICK\} 1)"}
C {devices/lab_wire.sym} 1500 -690 0 0 {name=l21 sig_type=std_logic lab=voutp}
C {devices/gnd.sym} 1500 -630 0 0 {name=g22 lab=0}
C {devices/isource.sym} 1620 -660 0 0 {name=Icmn value="pulse(0 \{ICM/2\} \{TKICK\} 10n 10n \{TREL-TKICK\} 1)"}
C {devices/lab_wire.sym} 1620 -690 0 0 {name=l23 sig_type=std_logic lab=voutn}
C {devices/gnd.sym} 1620 -630 0 0 {name=g24 lab=0}
C {devices/code.sym} 50 -1315 0 0 {name=PARAMS_BENCH
only_toplevel=true
value="
* TESTBENCH tran_cm_kick -- DUT SRMC-core-amp-w-cmfb (amp_031_srmc_core_cmfb)
* template amplifier/tran_cm_kick ; produces: cm_kick_v, cm_resid_v, t_cm_settle
* SRMC filter core OTA + ideal-CMFB servo (cmfb-output-ideal-amp). Biases internal (V1/V2/V3). CONTINUOUS -> AC valid. Min-size as drawn.
* bench conditions:
.param VDD=1.2
.param VCM=0.6
.param CL=50f
.param ICM=5u
.param TKICK=2u
.param TREL=6u
.param TSTEP=2n
.param TSTOP=20u
* DUT global params (drawing cap/res + ideal-CMFB macromodel knobs):
.param Cc=1p Rz=10k Cin=16p Cf=0.8p Cu=1p gm_val=100u rout_val=10Meg rin_val=1T cin_val=10f cout_val=100f Rm=1Meg tg_n_w=0.18u tg_p_w=0.18u tg_n_l=0.13u tg_p_l=0.13u
"}
C {devices/code.sym} 565 -1140 0 0 {name=MODELS
only_toplevel=true
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.temp 27
"}
C {devices/code.sym} 1812 -527 0 0 {name=COMMANDS
only_toplevel=true
value="
.control
  save all
  set hcopydevtype=svg
  set filetype=ascii
  tran 2n 20u
  let vocm = (v(voutp)+v(voutn))/2
  meas tran vocm0   FIND vocm AT=1u
  meas tran vocm_mid FIND vocm AT=5u
  meas tran vocm_end FIND vocm AT=19u
  let cm_kick_v  = vocm_mid - vocm0
  let cm_resid_v = vocm_end - vocm0
  print cm_kick_v cm_resid_v
  write tran_cm_kick.raw
  hardcopy tran_cm_kick_vocm.svg vocm
.endc
"}
C {devices/launcher.sym} 1895 -240 0 0 {name=h_run
descr="Simulate + load waves"
tclcommand="xschem netlist; simulate [list xschem raw_read $netlist_dir/[file tail [file rootname [xschem get current_name]]].raw tran]"
}
C {devices/launcher.sym} 1895 -300 0 0 {name=h_load
descr="Load waves"
tclcommand="xschem raw_read $netlist_dir/[file tail [file rootname [xschem get current_name]]].raw tran"
}
C {devices/title.sym} 190 -80 0 0 {name=l6 author="Copyright 2026 MacAnalog Research Group"}
