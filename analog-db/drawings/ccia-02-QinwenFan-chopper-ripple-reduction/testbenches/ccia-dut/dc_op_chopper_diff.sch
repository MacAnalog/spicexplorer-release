v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {ia/dc_op_chopper_diff -- DC operating point, chopper clocks HELD transparent} 52.5 -1402.5 0 0 0.4 0.4 {}
N 1035 -705 1035 -635 {
lab=clk_chop}
N 1055 -705 1055 -605 {
lab=clk_chop_not}
N 1105 -705 1105 -575 {
lab=clk_chop}
N 1125 -705 1125 -555 {
lab=clk_chop_not}
N 1172.5 -705 1172.5 -520 {
lab=clk_chop}
N 1192.5 -705 1192.5 -490 {
lab=clk_chop_not}
N 1245 -705 1245 -455 {
lab=clk_chop}
N 1265 -705 1265 -425 {
lab=clk_chop_not}
N 1315 -705 1315 -577.5 {
lab=clk_chop}
N 1335 -705 1335 -610 {
lab=clk_chop_not}
N 1400 -830 1455 -830 {
lab=clk_phi_1}
N 1400 -810 1455 -810 {
lab=clk_phi_2}
N 935 -865 995 -865 {
lab=vref}
N 935 -865 935 -825 {
lab=vref}
N 805 -900 995 -900 {
lab=vinp}
N 805 -900 805 -855 {
lab=vinp}
N 665 -920 995 -920 {
lab=vinn}
N 665 -920 665 -905 {
lab=vinn}
C {ccia-02-QinwenFan-chopper-ripple-reduction/ccia-dut-chopper-w-positive-feedback-rrl.sym} 1015 -725 0 0 {name=XDUT}
C {devices/lab_wire.sym} 1050 -1005 0 0 {name=l1 sig_type=std_logic lab=vdd}
C {devices/lab_wire.sym} 1070 -1005 0 0 {name=l2 sig_type=std_logic lab=vss}
C {devices/lab_wire.sym} 1035 -635 0 0 {name=l3 sig_type=std_logic lab=clk_chop}
C {devices/lab_wire.sym} 1055 -605 0 0 {name=l4 sig_type=std_logic lab=clk_chop_not}
C {devices/lab_wire.sym} 1105 -575 0 0 {name=l5 sig_type=std_logic lab=clk_chop}
C {devices/lab_wire.sym} 1125 -555 0 0 {name=l6 sig_type=std_logic lab=clk_chop_not}
C {devices/lab_wire.sym} 1172.5 -520 0 0 {name=l7 sig_type=std_logic lab=clk_chop}
C {devices/lab_wire.sym} 1192.5 -490 0 0 {name=l8 sig_type=std_logic lab=clk_chop_not}
C {devices/lab_wire.sym} 1245 -455 0 0 {name=l9 sig_type=std_logic lab=clk_chop}
C {devices/lab_wire.sym} 1265 -425 0 0 {name=l10 sig_type=std_logic lab=clk_chop_not}
C {devices/lab_wire.sym} 1315 -577.5 0 0 {name=l11 sig_type=std_logic lab=clk_chop}
C {devices/lab_wire.sym} 1335 -610 0 0 {name=l12 sig_type=std_logic lab=clk_chop_not}
C {devices/lab_wire.sym} 1455 -830 0 1 {name=l13 sig_type=std_logic lab=clk_phi_1}
C {devices/lab_wire.sym} 1455 -810 0 1 {name=l14 sig_type=std_logic lab=clk_phi_2}
C {devices/vsource.sym} 1665 -90 0 0 {name=Vdd value="dc \{VDD\}" savecurrent=true}
C {devices/lab_wire.sym} 1665 -120 0 0 {name=l15 sig_type=std_logic lab=vdd}
C {devices/gnd.sym} 1665 -60 0 0 {name=g16 lab=0}
C {devices/vsource.sym} 1765 -90 0 0 {name=Vss value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 1765 -120 0 0 {name=l17 sig_type=std_logic lab=vss}
C {devices/gnd.sym} 1765 -60 0 0 {name=g18 lab=0}
C {devices/vsource.sym} 95 -190 0 0 {name=Vchop_a value="dc \{VDD\}" savecurrent=true}
C {devices/lab_wire.sym} 95 -220 0 0 {name=l19 sig_type=std_logic lab=clk_chop}
C {devices/gnd.sym} 95 -160 0 0 {name=g20 lab=0}
C {devices/vsource.sym} 95 -310 0 0 {name=Vchop_b value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 95 -340 0 0 {name=l21 sig_type=std_logic lab=clk_chop_not}
C {devices/gnd.sym} 95 -280 0 0 {name=g22 lab=0}
C {devices/vsource.sym} 100 -575 0 0 {name=Vphi1 value="dc \{VDD\}" savecurrent=true}
C {devices/lab_wire.sym} 100 -605 0 0 {name=l35 sig_type=std_logic lab=clk_phi_1}
C {devices/gnd.sym} 100 -545 0 0 {name=g36 lab=0}
C {devices/vsource.sym} 100 -475 0 0 {name=Vphi2 value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 100 -505 0 0 {name=l37 sig_type=std_logic lab=clk_phi_2}
C {devices/gnd.sym} 100 -445 0 0 {name=g38 lab=0}
C {devices/vsource.sym} 535 -825 0 0 {name=Vcm value="dc \{VCM\}" savecurrent=true}
C {devices/lab_wire.sym} 535 -855 0 0 {name=l39 sig_type=std_logic lab=vcm}
C {devices/gnd.sym} 535 -795 0 0 {name=g40 lab=0}
C {devices/vsource.sym} 935 -795 0 0 {name=Vref value="dc \{VCM\}" savecurrent=true}
C {devices/lab_wire.sym} 935 -825 0 0 {name=l41 sig_type=std_logic lab=vref}
C {devices/gnd.sym} 935 -765 0 0 {name=g42 lab=0}
C {devices/lab_wire.sym} 995 -865 0 0 {name=l43 sig_type=std_logic lab=vref}
C {devices/vsource.sym} 805 -825 0 0 {name=Vinp value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 805 -855 0 0 {name=l44 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 805 -795 0 0 {name=l45 sig_type=std_logic lab=vcm}
C {devices/lab_wire.sym} 995 -900 0 0 {name=l46 sig_type=std_logic lab=vinp}
C {devices/vsource.sym} 665 -875 0 0 {name=Vinn value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 665 -905 0 0 {name=l47 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 665 -845 0 0 {name=l48 sig_type=std_logic lab=vcm}
C {devices/lab_wire.sym} 995 -920 0 0 {name=l49 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 1400 -900 0 0 {name=l50 sig_type=std_logic lab=voutp}
C {devices/lab_wire.sym} 1400 -920 0 0 {name=l51 sig_type=std_logic lab=voutn}
C {devices/code.sym} 50 -1315 0 0 {name=PARAMS_BENCH
only_toplevel=true
value="
* TESTBENCH dc_op_chopper_diff -- DUT ccia-dut-chopper-w-positive-feedback-rrl
* produces: i_supply, vos, vocm
* recorded baseline: i_supply 219.4951 uA | vos 7.720941e-06 V | vocm 0.6096373 V (ia_004)
* bench bindings (circuits/ia_004_fan_chopper_rrl/analyses/)
.param VDD=1.2
.param VCM=0.6
"}
C {devices/code.sym} 50 -1140 0 0 {name=PARAMS_TOP
only_toplevel=true
value="
* CCIA top level -- ccia-dut-chopper-w-positive-feedback-rrl.sch
* source: circuits/ia_004_fan_chopper_rrl/pdk/ihp-sg13g2/sizing.yaml
.param x_dut_cin1_main_value=16p  x_dut_cfb1_main_value=0.8p
.param x_dut_rb1_main_value=10Meg
* Cpf has no ia_004 knob (that composite drops the PF chopper); this drawing
* keeps it, so take ia_003_fan_chopper_pf's authored value.
.param x_dut_cpf1_main_value=0.8p
.param vb1_main=0.5 vb2_main=0.75 vb3_main=0.45 vb4_main=0.55
"}
C {devices/code.sym} 210 -1320 0 0 {name=PARAMS_CORE_OPAMP
only_toplevel=true
value="
* CCIA core opamp -- two-stage-opamp-core[-w-stage-breakout].sch
* (= circuits/amp_026_fan_chopper_ota, namespaced _MAIN in the composite)
.param x_dut_xm1_main_w=20u x_dut_xm1_main_l=1u
.param x_dut_xm2_main_w=20u x_dut_xm2_main_l=0.5u
.param x_dut_xm3_main_w=20u x_dut_xm3_main_l=0.5u
.param x_dut_xm4_main_w=4.7u x_dut_xm4_main_l=1u
.param x_dut_xm5_main_w=4.7u x_dut_xm5_main_l=1u
.param x_dut_xm6_main_w=10u x_dut_xm6_main_l=1u
.param x_dut_xm7_main_w=10u x_dut_xm7_main_l=1u
.param x_dut_xm8_main_w=6.2u x_dut_xm8_main_l=1u
.param x_dut_xm9_main_w=6.2u x_dut_xm9_main_l=1u
.param x_dut_xm10_main_w=10u x_dut_xm10_main_l=0.3u
.param x_dut_xm11_main_w=10u x_dut_xm11_main_l=0.3u
.param x_dut_xm12_main_w=5u x_dut_xm12_main_l=0.3u
.param x_dut_xm13_main_w=5u x_dut_xm13_main_l=0.3u
.param x_dut_xm14_main_w=6u x_dut_xm14_main_l=0.5u
.param x_dut_xm15_main_w=6u x_dut_xm15_main_l=0.5u
* Miller compensation cap
.param x_dut_cm1_main_value=1p
"}
C {devices/code.sym} 215 -1140 0 0 {name=PARAMS_RRL_SC
only_toplevel=true
value="
* RRL switched-capacitor network -- rrl-switched-capa-integrator.sch
* (= circuits/sup_003_rrl_sc_integrator, namespaced _RRL)
.param x_dut_cs1_rrl_value=1p  x_dut_caz1_rrl_value=1p  x_dut_cint1_rrl_value=4p
.param vb1_rrl=0.45 vb2_rrl=0.75 vb3_rrl=0.55 vcmfb_rrl=0.6
* behavioural compensation cell (shared/ideal/ideal-amp-fully-diff.sch).
* gm_val is ia_004's parent override (10u, not sup_003's own 100u): at the
* registry 5 kHz default the un-scaled Gm makes the discrete-time RRL loop
* gain > 1 and the clocked transient diverges.
.param gm_val=10u rout_val=10Meg cout_val=100f
.param rin_val=1T cin_val=10f
"}
C {devices/code.sym} 370 -1140 0 0 {name=PARAMS_RRL_OPAMP
only_toplevel=true
value="
* RRL integrator opamp -- integrator-switchcap-opamp.sch
* (= circuits/amp_027_fan_rrl_ota, namespaced _OPAMP_RRL)
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
* Switches -- shared/transmission_gate_pair.sch, used by EVERY chopper
* (in/fb/out/pf/rrl) and by the RRL's SC switches.
* Held at the PDK geometry floor and deliberately NOT sized yet.
.param tg_n_w=0.18u tg_n_l=0.13u
.param tg_p_w=0.18u tg_p_l=0.13u
"}
C {devices/code.sym} 1812.5 -527.5 0 0 {name=COMMANDS
only_toplevel=true
value="
.control
  save all
  set filetype=binary
  op
  let i_supply = abs(i(Vdd))
  let vos = v(voutp) - v(voutn)
  let vocm = (v(voutp) + v(voutn))/2
  print i_supply vos vocm
  * op has a single data row, so there is nothing to graph - dump the bias
  * point instead. `show` is the interactive companion to these prints.
  print v(voutp) v(voutn) v(vinp) v(vinn) v(vref)
  write dc_op_chopper_diff.raw
.endc
"}
C {devices/code.sym} 565 -1140 0 0 {name=MODELS
only_toplevel=true
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.temp 27
"}
C {devices/launcher.sym} 1895 -240 0 0 {name=h_run
descr="Simulate + load waves"
tclcommand="xschem netlist; simulate [list xschem raw_read $netlist_dir/[file tail [file rootname [xschem get current_name]]].raw op]"
}
C {devices/launcher.sym} 1895 -300 0 0 {name=h_load
descr="Load waves"
tclcommand="xschem raw_read $netlist_dir/[file tail [file rootname [xschem get current_name]]].raw op"
}
C {devices/title.sym} 190 -80 0 0 {name=l6 author="Copyright 2026 MacAnalog Research Group"}
