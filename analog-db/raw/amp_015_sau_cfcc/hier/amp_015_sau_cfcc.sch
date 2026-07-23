v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_015_sau_cfcc} -1220 -580 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -960 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_improved_high_swing_cascode_1.sym} -440 0 0 0 {name=xcm_nmos_improved_high_swing_cascode_1}
C {blocks/cm_nmos_simple_1.sym} 80 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_2.sym} 520 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/dp_pmos_simple_1.sym} 960 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -550 380 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/isource_np.sym} -1180 380 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/sg13_lv_pmos_np.sym} -110 -380 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 110 -380 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -330 380 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} -110 380 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} 110 380 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_nmos_np.sym} 330 380 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 550 380 0 0 {name=M23 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
N -850 -80 -810 -80 {}
C {devices/lab_wire.sym} -810 -80 0 1 {name=l0 lab=DM_1}
N -850 -40 -810 -40 {}
C {devices/lab_wire.sym} -810 -40 0 1 {name=l1 lab=VB3}
N -850 0 -810 0 {}
C {devices/lab_wire.sym} -810 0 0 1 {name=l2 lab=VB4}
N -850 40 -810 40 {}
C {devices/lab_wire.sym} -810 40 0 1 {name=l3 lab=net013}
N -850 80 -810 80 {}
C {devices/lab_wire.sym} -810 80 0 1 {name=l4 lab=net31}
N -960 -140 -960 -180 {}
C {devices/lab_wire.sym} -960 -180 0 1 {name=l5 lab=vdd}
N -250 -40 -210 -40 {}
C {devices/lab_wire.sym} -210 -40 0 1 {name=l6 lab=DM_1}
N -250 0 -210 0 {}
C {devices/lab_wire.sym} -210 0 0 1 {name=l7 lab=VB3}
N -250 40 -210 40 {}
C {devices/lab_wire.sym} -210 40 0 1 {name=l8 lab=VB4}
N -440 100 -440 140 {}
C {devices/lab_wire.sym} -440 140 2 0 {name=l9 lab=vss}
N 190 -20 230 -20 {}
C {devices/lab_wire.sym} 230 -20 0 1 {name=l10 lab=net043}
N 190 20 230 20 {}
C {devices/lab_wire.sym} 230 20 0 1 {name=l11 lab=net049}
N 80 80 80 120 {}
C {devices/lab_wire.sym} 80 120 2 0 {name=l12 lab=vss}
N 630 -40 670 -40 {}
C {devices/lab_wire.sym} 670 -40 0 1 {name=l13 lab=VOUTN}
N 630 0 670 0 {}
C {devices/lab_wire.sym} 670 0 0 1 {name=l14 lab=net049}
N 630 40 670 40 {}
C {devices/lab_wire.sym} 670 40 0 1 {name=l15 lab=net050}
N 520 -100 520 -140 {}
C {devices/lab_wire.sym} 520 -140 0 1 {name=l16 lab=vdd}
N 850 -20 810 -20 {}
C {devices/lab_wire.sym} 810 -20 0 0 {name=l17 lab=VINN}
N 850 20 810 20 {}
C {devices/lab_wire.sym} 810 20 0 0 {name=l18 lab=VINP}
N 1070 -40 1110 -40 {}
C {devices/lab_wire.sym} 1110 -40 0 1 {name=l19 lab=DM_2}
N 1070 0 1110 0 {}
C {devices/lab_wire.sym} 1110 0 0 1 {name=l20 lab=net063}
N 1070 40 1110 40 {}
C {devices/lab_wire.sym} 1110 40 0 1 {name=l21 lab=net31}
N -550 350 -550 310 {}
C {devices/lab_wire.sym} -550 310 0 1 {name=l22 lab=net063}
N -550 410 -550 450 {}
C {devices/lab_wire.sym} -550 450 2 0 {name=l23 lab=VOUT}
N -1180 350 -1180 310 {}
C {devices/lab_wire.sym} -1180 310 0 1 {name=l24 lab=net013}
N -1180 410 -1180 450 {}
C {devices/lab_wire.sym} -1180 450 2 0 {name=l25 lab=vss}
N -90 -350 -90 -310 {}
C {devices/lab_wire.sym} -90 -310 2 0 {name=l26 lab=net043}
N -130 -380 -170 -380 {}
C {devices/lab_wire.sym} -170 -380 0 0 {name=l27 lab=net050}
N -90 -410 -90 -450 {}
C {devices/lab_wire.sym} -90 -450 0 1 {name=l28 lab=vdd}
N -90 -380 -50 -380 {}
C {devices/lab_wire.sym} -50 -380 0 1 {name=l29 lab=vdd}
N 130 -350 130 -310 {}
C {devices/lab_wire.sym} 130 -310 2 0 {name=l30 lab=VOUT}
N 90 -380 50 -380 {}
C {devices/lab_wire.sym} 50 -380 0 0 {name=l31 lab=net050}
N 130 -410 130 -450 {}
C {devices/lab_wire.sym} 130 -450 0 1 {name=l32 lab=vdd}
N 130 -380 170 -380 {}
C {devices/lab_wire.sym} 170 -380 0 1 {name=l33 lab=vdd}
N -310 350 -310 310 {}
C {devices/lab_wire.sym} -310 310 0 1 {name=l34 lab=VOUTN}
N -350 380 -390 380 {}
C {devices/lab_wire.sym} -390 380 0 0 {name=l35 lab=VB3}
N -310 410 -310 450 {}
C {devices/lab_wire.sym} -310 450 2 0 {name=l36 lab=DM_2}
N -310 380 -270 380 {}
C {devices/lab_wire.sym} -270 380 0 1 {name=l37 lab=vss}
N -90 350 -90 310 {}
C {devices/lab_wire.sym} -90 310 0 1 {name=l38 lab=net050}
N -130 380 -170 380 {}
C {devices/lab_wire.sym} -170 380 0 0 {name=l39 lab=VB3}
N -90 410 -90 450 {}
C {devices/lab_wire.sym} -90 450 2 0 {name=l40 lab=net063}
N -90 380 -50 380 {}
C {devices/lab_wire.sym} -50 380 0 1 {name=l41 lab=vss}
N 130 350 130 310 {}
C {devices/lab_wire.sym} 130 310 0 1 {name=l42 lab=DM_2}
N 90 380 50 380 {}
C {devices/lab_wire.sym} 50 380 0 0 {name=l43 lab=VB4}
N 130 410 130 450 {}
C {devices/lab_wire.sym} 130 450 2 0 {name=l44 lab=vss}
N 130 380 170 380 {}
C {devices/lab_wire.sym} 170 380 0 1 {name=l45 lab=vss}
N 350 350 350 310 {}
C {devices/lab_wire.sym} 350 310 0 1 {name=l46 lab=net063}
N 310 380 270 380 {}
C {devices/lab_wire.sym} 270 380 0 0 {name=l47 lab=VB4}
N 350 410 350 450 {}
C {devices/lab_wire.sym} 350 450 2 0 {name=l48 lab=vss}
N 350 380 390 380 {}
C {devices/lab_wire.sym} 390 380 0 1 {name=l49 lab=vss}
N 570 350 570 310 {}
C {devices/lab_wire.sym} 570 310 0 1 {name=l50 lab=VOUT}
N 530 380 490 380 {}
C {devices/lab_wire.sym} 490 380 0 0 {name=l51 lab=net049}
N 570 410 570 450 {}
C {devices/lab_wire.sym} 570 450 2 0 {name=l52 lab=vss}
N 570 380 610 380 {}
C {devices/lab_wire.sym} 610 380 0 1 {name=l53 lab=vss}
