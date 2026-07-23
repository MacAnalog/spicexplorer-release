v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {amplifier/tran_cm_kick -- rrl-integrator-opamp standalone bench (amp_027_fan_rrl_ota)} 52.5 -1402.5 0 0 0.4 0.4 {}
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
C {ccia-02-QinwenFan-chopper-ripple-reduction/integrator-switchcap-opamp.sym} 1015 -725 0 0 {name=XDUT}
C {devices/lab_wire.sym} 1105 -1005 0 0 {name=l1 sig_type=std_logic lab=vdd}
C {devices/lab_wire.sym} 1125 -1005 0 0 {name=l2 sig_type=std_logic lab=vss}
C {devices/lab_wire.sym} 995 -945 0 0 {name=l3 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 995 -905 0 0 {name=l4 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 1295 -900 0 0 {name=l5 sig_type=std_logic lab=voutp}
C {devices/lab_wire.sym} 1295 -945 0 0 {name=l6 sig_type=std_logic lab=voutn}
C {devices/lab_wire.sym} 995 -815 0 0 {name=l7 sig_type=std_logic lab=vb1}
C {devices/lab_wire.sym} 995 -830 0 0 {name=l8 sig_type=std_logic lab=vb2}
C {devices/lab_wire.sym} 995 -845 0 0 {name=l9 sig_type=std_logic lab=vb3}
C {devices/lab_wire.sym} 995 -860 0 0 {name=l10 sig_type=std_logic lab=vb4}
C {devices/vsource.sym} 965 -1290 0 0 {name=Vdd value="dc \{VDD\}" savecurrent=true}
C {devices/lab_wire.sym} 965 -1320 0 0 {name=l11 sig_type=std_logic lab=vdd}
C {devices/gnd.sym} 965 -1260 0 0 {name=g12 lab=0}
C {devices/vsource.sym} 1065 -1290 0 0 {name=Vss value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 1065 -1320 0 0 {name=l13 sig_type=std_logic lab=vss}
C {devices/gnd.sym} 1065 -1260 0 0 {name=g14 lab=0}
C {devices/vsource.sym} 150 -540 0 0 {name=Vb1 value="dc \{vb1\}" savecurrent=true}
C {devices/lab_wire.sym} 150 -570 0 0 {name=l15 sig_type=std_logic lab=vb1}
C {devices/gnd.sym} 150 -510 0 0 {name=g16 lab=0}
C {devices/vsource.sym} 150 -660 0 0 {name=Vb2 value="dc \{vb2\}" savecurrent=true}
C {devices/lab_wire.sym} 150 -690 0 0 {name=l17 sig_type=std_logic lab=vb2}
C {devices/gnd.sym} 150 -630 0 0 {name=g18 lab=0}
C {devices/vsource.sym} 150 -780 0 0 {name=Vb3 value="dc \{vb3\}" savecurrent=true}
C {devices/lab_wire.sym} 150 -810 0 0 {name=l19 sig_type=std_logic lab=vb3}
C {devices/gnd.sym} 150 -750 0 0 {name=g20 lab=0}
C {devices/vsource.sym} 150 -900 0 0 {name=V_cmfb_ref value="dc \{vb4\}" savecurrent=true}
C {devices/lab_wire.sym} 150 -930 0 0 {name=l21 sig_type=std_logic lab=vb4}
C {devices/gnd.sym} 150 -870 0 0 {name=g22 lab=0}
C {devices/vsource.sym} 535 -825 0 0 {name=Vcm value="dc \{VCM\}" savecurrent=true}
C {devices/lab_wire.sym} 535 -855 0 0 {name=l23 sig_type=std_logic lab=vcm}
C {devices/gnd.sym} 535 -795 0 0 {name=g24 lab=0}
C {devices/vsource.sym} 805 -825 0 0 {name=Vinp value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 805 -855 0 0 {name=l25 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 805 -795 0 0 {name=l26 sig_type=std_logic lab=vcm}
C {devices/vsource.sym} 665 -905 0 0 {name=Vinn value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 665 -935 0 0 {name=l27 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 665 -875 0 0 {name=l28 sig_type=std_logic lab=vcm}
C {devices/capa.sym} 1580 -860 0 0 {name=CLoadp m=1 value=\{CL\}}
C {devices/lab_wire.sym} 1580 -890 0 0 {name=l29 sig_type=std_logic lab=voutp}
C {devices/gnd.sym} 1580 -830 0 0 {name=g30 lab=0}
C {devices/capa.sym} 1680 -890 0 0 {name=CLoadn m=1 value=\{CL\}}
C {devices/lab_wire.sym} 1680 -920 0 0 {name=l31 sig_type=std_logic lab=voutn}
C {devices/gnd.sym} 1680 -860 0 0 {name=g32 lab=0}
C {devices/isource.sym} 1500 -660 0 0 {name=Icmp value="pulse(0 \{ICM/2\} \{TKICK\} 10n 10n \{TREL-TKICK\} 1)"}
C {devices/lab_wire.sym} 1500 -690 0 0 {name=l33 sig_type=std_logic lab=voutp}
C {devices/gnd.sym} 1500 -630 0 0 {name=g34 lab=0}
C {devices/isource.sym} 1620 -660 0 0 {name=Icmn value="pulse(0 \{ICM/2\} \{TKICK\} 10n 10n \{TREL-TKICK\} 1)"}
C {devices/lab_wire.sym} 1620 -690 0 0 {name=l35 sig_type=std_logic lab=voutn}
C {devices/gnd.sym} 1620 -630 0 0 {name=g36 lab=0}
C {devices/code.sym} 50 -1315 0 0 {name=PARAMS_BENCH
only_toplevel=true
value="
* TESTBENCH tran_cm_kick -- DUT rrl-integrator-opamp (amp_027_fan_rrl_ota)
* template amplifier/tran_cm_kick ; produces: cm_kick_v, cm_resid_v, t_cm_settle
* telescopic OTA with an internal DDA-CMFB; vb4 (pin V_cmfb_ref) is the output-CM reference -> ac_cm_reg / tran_cm_kick test that loop.
* bench conditions (mirror circuits/<id>/analyses/<id>.yaml params):
.param VDD=1.2
.param VCM=0.6
.param CL=50f
.param ICM=5u
.param TKICK=2u
.param TMID=5u
.param TREL=6u
.param TEND=19u
.param VTOL=2m
.param TSTEP=2n
.param TSTOP=20u
* external bias ports (block sizing.yaml defaults):
.param vb1=0.45
.param vb2=0.75
.param vb3=0.55
.param vb4=0.6
"}
C {devices/code.sym} 370 -1140 0 0 {name=PARAMS_RRL_OPAMP
only_toplevel=true
value="
* RRL integrator opamp -- integrator-switchcap-opamp.sch
* = circuits/amp_027_fan_rrl_ota (telescopic + internal DDA-CMFB, ref = V_cmfb_ref/vb4)
.param x_dut_xm1_opamp_rrl_w=20u x_dut_xm1_opamp_rrl_l=1u
.param x_dut_xm2_opamp_rrl_w=20u x_dut_xm2_opamp_rrl_l=0.5u
.param x_dut_xm3_opamp_rrl_w=20u x_dut_xm3_opamp_rrl_l=0.5u
.param x_dut_xm4_opamp_rrl_w=10u x_dut_xm4_opamp_rrl_l=1u
.param x_dut_xm5_opamp_rrl_w=4u x_dut_xm5_opamp_rrl_l=0.5u
.param x_dut_xm6_opamp_rrl_w=4u x_dut_xm6_opamp_rrl_l=0.5u
.param x_dut_xm7_opamp_rrl_w=4u x_dut_xm7_opamp_rrl_l=0.5u
.param x_dut_xm8_opamp_rrl_w=4u x_dut_xm8_opamp_rrl_l=0.5u
.param x_dut_xm9_opamp_rrl_w=10u x_dut_xm9_opamp_rrl_l=0.3u
.param x_dut_xm10_opamp_rrl_w=10u x_dut_xm10_opamp_rrl_l=0.3u
.param x_dut_xm11_opamp_rrl_w=5u x_dut_xm11_opamp_rrl_l=0.3u
.param x_dut_xm12_opamp_rrl_w=5u x_dut_xm12_opamp_rrl_l=0.3u
.param x_dut_xm13_opamp_rrl_w=6u x_dut_xm13_opamp_rrl_l=1u
.param x_dut_xm14_opamp_rrl_w=6u x_dut_xm14_opamp_rrl_l=1u
.param x_dut_xm15_opamp_rrl_w=2u x_dut_xm15_opamp_rrl_l=1u
.param x_dut_xm16_opamp_rrl_w=2u x_dut_xm16_opamp_rrl_l=1u
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
  set filetype=binary
  tran 2n 20u
  let vocm = (v(voutp)+v(voutn))/2
  meas tran vocm0   FIND vocm AT=1u
  meas tran vocm_mid FIND vocm AT=5u
  meas tran vocm_end FIND vocm AT=19u
  let cm_kick_v  = vocm_mid - vocm0
  let cm_resid_v = vocm_end - vocm0
  let verr = abs(vocm - vocm_end)
  meas tran tcross WHEN verr=2m FALL=LAST
  let t_cm_settle = tcross - 6u
  print cm_kick_v cm_resid_v t_cm_settle
  write tran_cm_kick.raw
  * --- waveform output: hardcopy=batch-safe SVG, plot=interactive ---
  hardcopy tran_cm_kick_vocm.svg vocm
  plot vocm
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
