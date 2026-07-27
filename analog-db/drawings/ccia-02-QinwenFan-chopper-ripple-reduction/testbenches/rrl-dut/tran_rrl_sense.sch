v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {support/tran_rrl_sense -- rrl-dut standalone bench (sup_003_rrl_sc_integrator)} 52.5 -1402.5 0 0 0.4 0.4 {}
B 2 1820 -925 2780 -765 {flags=graph
y1=-0.5
y2=0.5
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=0.002
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
dataset=-1
unitx=m
logx=0
logy=0
color="4"
node="vd"
rainbow=0}
B 2 1820 -755 2780 -595 {flags=graph
y1=0
y2=1.2
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=0.002
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
dataset=-1
unitx=m
logx=0
logy=0
color="4 5"
node="voutp voutn"
rainbow=0}
C {ccia-02-QinwenFan-chopper-ripple-reduction/rrl-switched-capa-integrator.sym} 1015 -725 0 0 {name=XDUT}
C {devices/lab_wire.sym} 995 -900 0 0 {name=l1 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 995 -860 0 0 {name=l2 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 1295 -900 0 0 {name=l3 sig_type=std_logic lab=voutp}
C {devices/lab_wire.sym} 1295 -860 0 0 {name=l4 sig_type=std_logic lab=voutn}
C {devices/lab_wire.sym} 1035 -705 0 0 {name=l5 sig_type=std_logic lab=clk_ch_rrl}
C {devices/lab_wire.sym} 1055 -705 0 0 {name=l6 sig_type=std_logic lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} 1235 -705 0 0 {name=l7 sig_type=std_logic lab=clk_phi_1}
C {devices/lab_wire.sym} 1255 -705 0 0 {name=l8 sig_type=std_logic lab=clk_phi_2}
C {devices/lab_wire.sym} 1050 -995 0 0 {name=l9 sig_type=std_logic lab=vdd}
C {devices/lab_wire.sym} 1070 -995 0 0 {name=l10 sig_type=std_logic lab=vss}
C {devices/vsource.sym} 965 -1290 0 0 {name=Vdd value="dc \{VDD\}" savecurrent=true}
C {devices/lab_wire.sym} 965 -1320 0 0 {name=l11 sig_type=std_logic lab=vdd}
C {devices/gnd.sym} 965 -1260 0 0 {name=g12 lab=0}
C {devices/vsource.sym} 1065 -1290 0 0 {name=Vss value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 1065 -1320 0 0 {name=l13 sig_type=std_logic lab=vss}
C {devices/gnd.sym} 1065 -1260 0 0 {name=g14 lab=0}
C {devices/vsource.sym} 535 -825 0 0 {name=Vcm value="dc \{VCM\}" savecurrent=true}
C {devices/lab_wire.sym} 535 -855 0 0 {name=l15 sig_type=std_logic lab=vcm}
C {devices/gnd.sym} 535 -795 0 0 {name=g16 lab=0}
C {devices/vsource.sym} 805 -825 0 0 {name=Vinp value="pulse(\{-VR/2\} \{VR/2\} 0 \{TEDGE\} \{TEDGE\} \{TCHOP/2-TEDGE\} \{TCHOP\})" savecurrent=true}
C {devices/lab_wire.sym} 805 -855 0 0 {name=l17 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 805 -795 0 0 {name=l18 sig_type=std_logic lab=vcm}
C {devices/vsource.sym} 665 -905 0 0 {name=Vinn value="pulse(\{VR/2\} \{-VR/2\} 0 \{TEDGE\} \{TEDGE\} \{TCHOP/2-TEDGE\} \{TCHOP\})" savecurrent=true}
C {devices/lab_wire.sym} 665 -935 0 0 {name=l19 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 665 -875 0 0 {name=l20 sig_type=std_logic lab=vcm}
C {devices/vsource.sym} 95 -190 0 0 {name=Vckr value="pulse(0 \{VDD\} 0 \{TEDGE\} \{TEDGE\} \{TCHOP/2-TEDGE\} \{TCHOP\})" savecurrent=true}
C {devices/lab_wire.sym} 95 -220 0 0 {name=l21 sig_type=std_logic lab=clk_ch_rrl}
C {devices/gnd.sym} 95 -160 0 0 {name=g22 lab=0}
C {devices/vsource.sym} 95 -310 0 0 {name=Vckrn value="pulse(\{VDD\} 0 0 \{TEDGE\} \{TEDGE\} \{TCHOP/2-TEDGE\} \{TCHOP\})" savecurrent=true}
C {devices/lab_wire.sym} 95 -340 0 0 {name=l23 sig_type=std_logic lab=clk_ch_rrl_not}
C {devices/gnd.sym} 95 -280 0 0 {name=g24 lab=0}
C {devices/vsource.sym} 475 -205 0 0 {name=Vphi1 value="pulse(0 \{VDD\} 0 \{TEDGE\} \{TEDGE\} \{TCHOP/4-TEDGE\} \{TCHOP/2\})" savecurrent=true}
C {devices/lab_wire.sym} 475 -235 0 0 {name=l25 sig_type=std_logic lab=clk_phi_1}
C {devices/gnd.sym} 475 -175 0 0 {name=g26 lab=0}
C {devices/vsource.sym} 475 -310 0 0 {name=Vphi2 value="pulse(\{VDD\} 0 0 \{TEDGE\} \{TEDGE\} \{TCHOP/4-TEDGE\} \{TCHOP/2\})" savecurrent=true}
C {devices/lab_wire.sym} 475 -340 0 0 {name=l27 sig_type=std_logic lab=clk_phi_2}
C {devices/gnd.sym} 475 -280 0 0 {name=g28 lab=0}
C {devices/code.sym} 50 -1315 0 0 {name=PARAMS_BENCH
only_toplevel=true
value="
* TESTBENCH tran_rrl_sense -- DUT rrl-dut (sup_003_rrl_sc_integrator)
* template support/tran_rrl_sense ; produces: ramp_rate, ripple_gain (V/s per V ripple; SIGN = RRL loop polarity)
* ripple-sensing demodulating SC integrator; biases live inside the block, so the bench drives only the ripple + clocks.
* bench conditions (mirror circuits/<id>/analyses/<id>.yaml params):
.param VDD=1.2
.param VCM=0.6
.param VR=2m
.param FCHOP=5k
.param TEDGE=100n
.param T1=0.6m
.param T2=1.8m
.param TSTEP=500n
.param TSTOP=2m
.param TMAX=200n
.param TCHOP=\{1/FCHOP\}
"}
C {devices/code.sym} 215 -1140 0 0 {name=PARAMS_RRL_SC
only_toplevel=true
value="
* RRL switched-capacitor network -- rrl-switched-capa-integrator.sch
* = circuits/sup_003_rrl_sc_integrator. The drawing has TWO amps: the REAL
* integrator-switchcap-opamp (x_opamp) as the SC virtual-ground amp, AND a
* behavioural ideal-amp-fully-diff (x1) as the output driver stage.
.param x_dut_cs1_rrl_value=1p  x_dut_caz1_rrl_value=1p  x_dut_cint1_rrl_value=4p
* internal bias sources (drawn inside the block): vb4 -> vcmfb_rrl is the
* CMFB reference into the opamp's DDA-CMFB.
.param vb1_rrl=0.45 vb2_rrl=0.75 vb3_rrl=0.55 vcmfb_rrl=0.6
* behavioural output amp (shared/ideal/ideal-amp-fully-diff.sch); sup_003's own
* gm_val=100u (NOT ia_004's 10u override) -- the standalone tran_rrl_sense window
* is short (T1..T2 < windup), so the un-scaled Gm is fine here.
.param gm_val=100u rout_val=10Meg cout_val=100f
.param rin_val=1T cin_val=10f
"}
C {devices/code.sym} 370 -1140 0 0 {name=PARAMS_RRL_OPAMP
only_toplevel=true
value="
* RRL integrator opamp -- integrator-switchcap-opamp.sch
* = circuits/sup_003 embedded opamp (telescopic + internal DDA-CMFB, ref = V_cmfb_ref/vb4)
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
C {devices/code.sym} 370 -1320 0 0 {name=PARAMS_SWITCH
only_toplevel=true
value="
* Chopper / SC transmission gates (shared/transmission_gate_pair.sch).
* PDK geometry floor, deliberately NOT sized yet (per owner).
.param tg_n_w=0.18u tg_n_l=0.13u
.param tg_p_w=0.18u tg_p_l=0.13u
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
  tran 500n 2m 0 200n
  let vd = v(voutp) - v(voutn)
  meas tran v1 FIND vd AT=0.6m
  meas tran v2 FIND vd AT=1.8m
  * ramp inside the linear window; denom = T2-T1 = 1.2 ms, VR = 2 mV
  let ramp_rate  = (v2 - v1)/1.2e-3
  let ripple_gain = ramp_rate/2e-3
  print ramp_rate ripple_gain
  write tran_rrl_sense.raw
  * --- waveform output: hardcopy=batch-safe SVG, plot=interactive ---
  hardcopy tran_rrl_sense_vd.svg vd
  hardcopy tran_rrl_sense_out.svg voutp voutn
  plot vd
  plot voutp voutn
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
