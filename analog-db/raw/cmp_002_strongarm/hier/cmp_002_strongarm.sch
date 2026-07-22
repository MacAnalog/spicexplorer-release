v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmp_002_strongarm} -590 -540 0 0 0.4 0.4 {}
C {blocks/dp_nmos_simple_1.sym} -440 0 0 0 {name=xdp_nmos_simple_1}
C {blocks/inv_cmos_stack_1.sym} 0 0 0 0 {name=xinv_cmos_stack_1}
C {blocks/inv_cmos_stack_2.sym} 440 0 0 0 {name=xinv_cmos_stack_2}
C {devices/sg13_lv_nmos_np.sym} -220 340 0 0 {name=MLEM model=sg13_lv_nmos spiceprefix=X w=x_dut_xmlem_w l=x_dut_xmlem_l m=x_dut_xmlem_m}
C {devices/sg13_lv_nmos_np.sym} 0 340 0 0 {name=MLEP model=sg13_lv_nmos spiceprefix=X w=x_dut_xmlep_w l=x_dut_xmlep_l m=x_dut_xmlep_m}
C {devices/sg13_lv_pmos_np.sym} -550 -340 0 0 {name=MLUM model=sg13_lv_pmos spiceprefix=X w=x_dut_xmlum_w l=x_dut_xmlum_l m=x_dut_xmlum_m}
C {devices/sg13_lv_pmos_np.sym} -330 -340 0 0 {name=MLUP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmlup_w l=x_dut_xmlup_l m=x_dut_xmlup_m}
C {devices/sg13_lv_pmos_np.sym} -110 -340 0 0 {name=MPC1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpc1_w l=x_dut_xmpc1_l m=x_dut_xmpc1_m}
C {devices/sg13_lv_pmos_np.sym} 110 -340 0 0 {name=MPC2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpc2_w l=x_dut_xmpc2_l m=x_dut_xmpc2_m}
C {devices/sg13_lv_pmos_np.sym} 330 -340 0 0 {name=MPC3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpc3_w l=x_dut_xmpc3_l m=x_dut_xmpc3_m}
C {devices/sg13_lv_pmos_np.sym} 550 -340 0 0 {name=MPC4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpc4_w l=x_dut_xmpc4_l m=x_dut_xmpc4_m}
C {devices/sg13_lv_nmos_np.sym} 220 340 0 0 {name=MTAIL model=sg13_lv_nmos spiceprefix=X w=x_dut_xmtail_w l=x_dut_xmtail_l m=x_dut_xmtail_m}
N -550 -20 -590 -20 {}
C {devices/lab_wire.sym} -590 -20 0 0 {name=l0 lab=vinn}
N -550 20 -590 20 {}
C {devices/lab_wire.sym} -590 20 0 0 {name=l1 lab=vinp}
N -330 -40 -290 -40 {}
C {devices/lab_wire.sym} -290 -40 0 1 {name=l2 lab=sn}
N -330 0 -290 0 {}
C {devices/lab_wire.sym} -290 0 0 1 {name=l3 lab=sp}
N -330 40 -290 40 {}
C {devices/lab_wire.sym} -290 40 0 1 {name=l4 lab=tail}
N -440 100 -440 140 {}
C {devices/lab_wire.sym} -440 140 2 0 {name=l5 lab=vss}
N -110 0 -150 0 {}
C {devices/lab_wire.sym} -150 0 0 0 {name=l6 lab=lm}
N 110 0 150 0 {}
C {devices/lab_wire.sym} 150 0 0 1 {name=l7 lab=voutp}
N 0 -80 0 -120 {}
C {devices/lab_wire.sym} 0 -120 0 1 {name=l8 lab=vdd}
N 0 80 0 120 {}
C {devices/lab_wire.sym} 0 120 2 0 {name=l9 lab=vss}
N 330 0 290 0 {}
C {devices/lab_wire.sym} 290 0 0 0 {name=l10 lab=lp}
N 550 0 590 0 {}
C {devices/lab_wire.sym} 590 0 0 1 {name=l11 lab=voutn}
N 440 -80 440 -120 {}
C {devices/lab_wire.sym} 440 -120 0 1 {name=l12 lab=vdd}
N 440 80 440 120 {}
C {devices/lab_wire.sym} 440 120 2 0 {name=l13 lab=vss}
N -200 310 -200 270 {}
C {devices/lab_wire.sym} -200 270 0 1 {name=l14 lab=lm}
N -240 340 -280 340 {}
C {devices/lab_wire.sym} -280 340 0 0 {name=l15 lab=lp}
N -200 370 -200 410 {}
C {devices/lab_wire.sym} -200 410 2 0 {name=l16 lab=sn}
N -200 340 -160 340 {}
C {devices/lab_wire.sym} -160 340 0 1 {name=l17 lab=vss}
N 20 310 20 270 {}
C {devices/lab_wire.sym} 20 270 0 1 {name=l18 lab=lp}
N -20 340 -60 340 {}
C {devices/lab_wire.sym} -60 340 0 0 {name=l19 lab=lm}
N 20 370 20 410 {}
C {devices/lab_wire.sym} 20 410 2 0 {name=l20 lab=sp}
N 20 340 60 340 {}
C {devices/lab_wire.sym} 60 340 0 1 {name=l21 lab=vss}
N -530 -310 -530 -270 {}
C {devices/lab_wire.sym} -530 -270 2 0 {name=l22 lab=lm}
N -570 -340 -610 -340 {}
C {devices/lab_wire.sym} -610 -340 0 0 {name=l23 lab=lp}
N -530 -370 -530 -410 {}
C {devices/lab_wire.sym} -530 -410 0 1 {name=l24 lab=vdd}
N -530 -340 -490 -340 {}
C {devices/lab_wire.sym} -490 -340 0 1 {name=l25 lab=vdd}
N -310 -310 -310 -270 {}
C {devices/lab_wire.sym} -310 -270 2 0 {name=l26 lab=lp}
N -350 -340 -390 -340 {}
C {devices/lab_wire.sym} -390 -340 0 0 {name=l27 lab=lm}
N -310 -370 -310 -410 {}
C {devices/lab_wire.sym} -310 -410 0 1 {name=l28 lab=vdd}
N -310 -340 -270 -340 {}
C {devices/lab_wire.sym} -270 -340 0 1 {name=l29 lab=vdd}
N -90 -310 -90 -270 {}
C {devices/lab_wire.sym} -90 -270 2 0 {name=l30 lab=sp}
N -130 -340 -170 -340 {}
C {devices/lab_wire.sym} -170 -340 0 0 {name=l31 lab=clk}
N -90 -370 -90 -410 {}
C {devices/lab_wire.sym} -90 -410 0 1 {name=l32 lab=vdd}
N -90 -340 -50 -340 {}
C {devices/lab_wire.sym} -50 -340 0 1 {name=l33 lab=vdd}
N 130 -310 130 -270 {}
C {devices/lab_wire.sym} 130 -270 2 0 {name=l34 lab=sn}
N 90 -340 50 -340 {}
C {devices/lab_wire.sym} 50 -340 0 0 {name=l35 lab=clk}
N 130 -370 130 -410 {}
C {devices/lab_wire.sym} 130 -410 0 1 {name=l36 lab=vdd}
N 130 -340 170 -340 {}
C {devices/lab_wire.sym} 170 -340 0 1 {name=l37 lab=vdd}
N 350 -310 350 -270 {}
C {devices/lab_wire.sym} 350 -270 2 0 {name=l38 lab=lp}
N 310 -340 270 -340 {}
C {devices/lab_wire.sym} 270 -340 0 0 {name=l39 lab=clk}
N 350 -370 350 -410 {}
C {devices/lab_wire.sym} 350 -410 0 1 {name=l40 lab=vdd}
N 350 -340 390 -340 {}
C {devices/lab_wire.sym} 390 -340 0 1 {name=l41 lab=vdd}
N 570 -310 570 -270 {}
C {devices/lab_wire.sym} 570 -270 2 0 {name=l42 lab=lm}
N 530 -340 490 -340 {}
C {devices/lab_wire.sym} 490 -340 0 0 {name=l43 lab=clk}
N 570 -370 570 -410 {}
C {devices/lab_wire.sym} 570 -410 0 1 {name=l44 lab=vdd}
N 570 -340 610 -340 {}
C {devices/lab_wire.sym} 610 -340 0 1 {name=l45 lab=vdd}
N 240 310 240 270 {}
C {devices/lab_wire.sym} 240 270 0 1 {name=l46 lab=tail}
N 200 340 160 340 {}
C {devices/lab_wire.sym} 160 340 0 0 {name=l47 lab=clk}
N 240 370 240 410 {}
C {devices/lab_wire.sym} 240 410 2 0 {name=l48 lab=vss}
N 240 340 280 340 {}
C {devices/lab_wire.sym} 280 340 0 1 {name=l49 lab=vss}
