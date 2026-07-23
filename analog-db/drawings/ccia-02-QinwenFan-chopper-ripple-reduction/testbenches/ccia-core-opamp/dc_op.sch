v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {amplifier/dc_op -- ccia-core-opamp standalone bench (amp_026_fan_chopper_ota)} 52.5 -1402.5 0 0 0.4 0.4 {}
C {ccia-02-QinwenFan-chopper-ripple-reduction/two-stage-opamp-core.sym} 1015 -725 0 0 {name=XDUT}
C {devices/lab_wire.sym} 1105 -1005 0 0 {name=l1 sig_type=std_logic lab=vdd}
C {devices/lab_wire.sym} 1125 -1005 0 0 {name=l2 sig_type=std_logic lab=vss}
C {devices/lab_wire.sym} 995 -905 0 0 {name=l3 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 995 -945 0 0 {name=l4 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 1295 -900 0 0 {name=l5 sig_type=std_logic lab=voutp}
C {devices/lab_wire.sym} 1295 -945 0 0 {name=l6 sig_type=std_logic lab=voutn}
C {devices/lab_wire.sym} 995 -815 0 0 {name=l7 sig_type=std_logic lab=vb1}
C {devices/lab_wire.sym} 995 -830 0 0 {name=l8 sig_type=std_logic lab=vb2}
C {devices/lab_wire.sym} 995 -845 0 0 {name=l9 sig_type=std_logic lab=vb3}
C {devices/lab_wire.sym} 995 -860 0 0 {name=l10 sig_type=std_logic lab=vb4}
C {devices/lab_wire.sym} 1035 -705 0 0 {name=l11 sig_type=std_logic lab=vdd}
C {devices/lab_wire.sym} 1055 -705 0 0 {name=l12 sig_type=std_logic lab=vss}
C {devices/vsource.sym} 965 -1290 0 0 {name=Vdd value="dc \{VDD\}" savecurrent=true}
C {devices/lab_wire.sym} 965 -1320 0 0 {name=l13 sig_type=std_logic lab=vdd}
C {devices/gnd.sym} 965 -1260 0 0 {name=g14 lab=0}
C {devices/vsource.sym} 1065 -1290 0 0 {name=Vss value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 1065 -1320 0 0 {name=l15 sig_type=std_logic lab=vss}
C {devices/gnd.sym} 1065 -1260 0 0 {name=g16 lab=0}
C {devices/vsource.sym} 150 -540 0 0 {name=Vb1 value="dc \{vb1\}" savecurrent=true}
C {devices/lab_wire.sym} 150 -570 0 0 {name=l17 sig_type=std_logic lab=vb1}
C {devices/gnd.sym} 150 -510 0 0 {name=g18 lab=0}
C {devices/vsource.sym} 150 -660 0 0 {name=Vb2 value="dc \{vb2\}" savecurrent=true}
C {devices/lab_wire.sym} 150 -690 0 0 {name=l19 sig_type=std_logic lab=vb2}
C {devices/gnd.sym} 150 -630 0 0 {name=g20 lab=0}
C {devices/vsource.sym} 150 -780 0 0 {name=Vb3 value="dc \{vb3\}" savecurrent=true}
C {devices/lab_wire.sym} 150 -810 0 0 {name=l21 sig_type=std_logic lab=vb3}
C {devices/gnd.sym} 150 -750 0 0 {name=g22 lab=0}
C {devices/vsource.sym} 150 -900 0 0 {name=Vb4 value="dc \{vb4\}" savecurrent=true}
C {devices/lab_wire.sym} 150 -930 0 0 {name=l23 sig_type=std_logic lab=vb4}
C {devices/gnd.sym} 150 -870 0 0 {name=g24 lab=0}
C {devices/vsource.sym} 535 -825 0 0 {name=Vcm value="dc \{VCM\}" savecurrent=true}
C {devices/lab_wire.sym} 535 -855 0 0 {name=l25 sig_type=std_logic lab=vcm}
C {devices/gnd.sym} 535 -795 0 0 {name=g26 lab=0}
C {devices/vsource.sym} 805 -825 0 0 {name=Vinp value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 805 -855 0 0 {name=l27 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 805 -795 0 0 {name=l28 sig_type=std_logic lab=vcm}
C {devices/vsource.sym} 665 -905 0 0 {name=Vinn value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 665 -935 0 0 {name=l29 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 665 -875 0 0 {name=l30 sig_type=std_logic lab=vcm}
C {devices/code.sym} 50 -1315 0 0 {name=PARAMS_BENCH
only_toplevel=true
value="
* TESTBENCH dc_op -- DUT ccia-core-opamp (amp_026_fan_chopper_ota)
* template amplifier/dc_op_diff ; produces: i_supply, vos, vocm
* two-stage OTA core with a statically-transparent output chopper; vctl->vdd, vctl_not->vss. NO CMFB (vocm ratio-set).
* bench conditions (mirror circuits/<id>/analyses/<id>.yaml params):
.param VDD=1.2
.param VCM=0.6
* external bias ports (block sizing.yaml defaults):
.param vb1=0.398118
.param vb2=0.65
.param vb3=0.45
.param vb4=0.55
"}
C {devices/code.sym} 210 -1320 0 0 {name=PARAMS_CORE_OPAMP
only_toplevel=true
value="
* CCIA core opamp (standalone) -- two-stage-opamp-core.sch
* = circuits/amp_026_fan_chopper_ota, own pdk/ihp-sg13g2/sizing.yaml defaults
* (no CMFB is drawn: vocm is set by device ratioing -- see dc_op vocm)
.param x_dut_xm1_main_w=20u x_dut_xm1_main_l=1u
.param x_dut_xm2_main_w=20u x_dut_xm2_main_l=0.5u
.param x_dut_xm3_main_w=20u x_dut_xm3_main_l=0.5u
.param x_dut_xm4_main_w=10u x_dut_xm4_main_l=1u
.param x_dut_xm5_main_w=10u x_dut_xm5_main_l=1u
.param x_dut_xm6_main_w=10u x_dut_xm6_main_l=1u
.param x_dut_xm7_main_w=10u x_dut_xm7_main_l=1u
.param x_dut_xm8_main_w=10u x_dut_xm8_main_l=1u
.param x_dut_xm9_main_w=10u x_dut_xm9_main_l=1u
.param x_dut_xm10_main_w=10u x_dut_xm10_main_l=0.3u
.param x_dut_xm11_main_w=10u x_dut_xm11_main_l=0.3u
.param x_dut_xm12_main_w=5u x_dut_xm12_main_l=0.3u
.param x_dut_xm13_main_w=5u x_dut_xm13_main_l=0.3u
.param x_dut_xm14_main_w=10u x_dut_xm14_main_l=0.25u
.param x_dut_xm15_main_w=10u x_dut_xm15_main_l=0.25u
.param x_dut_cm1_main_value=2p
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
  set filetype=binary
  op
  let i_supply = abs(i(Vdd))
  let vos  = v(voutp) - v(voutn)
  let vocm = (v(voutp) + v(voutn))/2
  print i_supply vos vocm
  print v(voutp) v(voutn) v(vinp) v(vinn)
  write dc_op.raw
.endc
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
