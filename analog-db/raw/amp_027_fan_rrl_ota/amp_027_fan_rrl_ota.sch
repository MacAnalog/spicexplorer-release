v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_027_fan_rrl_ota} -860 -200 0 0 0.4 0.4 {}
C {devices/vsource_np.sym} -820 1040 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -820 780 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -820 520 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -820 260 0 0 {name=VB4 value="dc {vb4}"}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -170 520 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_nmos_np.sym} 190 780 0 0 {name=M11 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -170 780 0 1 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 190 1040 0 0 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} -170 1040 0 1 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 0 520 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 500 520 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} 190 260 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -170 260 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 180 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 0 260 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 500 260 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} -480 260 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 680 260 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 190 520 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -820 170 -820 230 {}
N -820 290 -820 350 {}
N -820 430 -820 490 {}
N -820 550 -820 610 {}
N -820 690 -820 750 {}
N -820 810 -820 870 {}
N -820 950 -820 1010 {}
N -820 1070 -820 1130 {}
N -460 170 -460 230 {}
N -460 290 -460 350 {}
N -400 260 -400 354 {}
N -250 260 -250 354 {}
N -250 520 -250 614 {}
N -250 780 -250 874 {}
N -250 1040 -250 1134 {}
N -190 170 -190 230 {}
N -190 290 -190 350 {}
N -190 430 -190 490 {}
N -190 550 -190 750 {}
N -190 810 -190 1010 {}
N -190 1070 -190 1180 {}
N -150 260 -150 320 {}
N -150 520 -150 580 {}
N -20 200 -20 260 {}
N -20 450 -20 520 {}
N 20 -140 20 -30 {}
N 20 30 20 90 {}
N 20 170 20 230 {}
N 20 290 20 350 {}
N 20 430 20 490 {}
N 20 550 20 610 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 80 520 80 614 {}
N 160 -60 160 0 {}
N 170 200 170 260 {}
N 170 460 170 520 {}
N 200 -140 200 -30 {}
N 200 30 200 90 {}
N 210 170 210 230 {}
N 210 290 210 350 {}
N 210 430 210 490 {}
N 210 550 210 750 {}
N 210 810 210 1010 {}
N 210 1070 210 1180 {}
N 260 0 260 94 {}
N 270 260 270 354 {}
N 270 520 270 614 {}
N 270 780 270 874 {}
N 270 1040 270 1134 {}
N 520 170 520 230 {}
N 520 290 520 350 {}
N 520 430 520 490 {}
N 520 550 520 1180 {}
N 580 260 580 354 {}
N 580 520 580 614 {}
N 700 200 700 230 {}
N 700 290 700 350 {}
N 760 260 760 354 {}
N -880 -140 890 -140 {}
N -80 0 -20 0 {}
N 20 0 80 0 {}
N 130 0 160 0 {}
N 200 0 260 0 {}
N 520 200 700 200 {}
N -560 260 -500 260 {}
N -460 260 -400 260 {}
N -250 260 -190 260 {}
N -150 260 -120 260 {}
N -50 260 -20 260 {}
N 20 260 80 260 {}
N 140 260 170 260 {}
N 210 260 270 260 {}
N 420 260 480 260 {}
N 520 260 580 260 {}
N 630 260 660 260 {}
N 700 260 760 260 {}
N -20 450 20 450 {}
N -250 520 -190 520 {}
N -150 520 -120 520 {}
N 20 520 80 520 {}
N 140 520 170 520 {}
N 210 520 270 520 {}
N 420 520 480 520 {}
N 520 520 580 520 {}
N -250 780 -190 780 {}
N -150 780 170 780 {}
N 210 780 270 780 {}
N -250 1040 -190 1040 {}
N -150 1040 170 1040 {}
N 210 1040 270 1040 {}
N -880 1180 890 1180 {}
C {devices/lab_wire.sym} -880 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -880 1180 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -90 1040 0 1 {name=l2 lab=cm_bias}
C {devices/lab_wire.sym} 20 430 0 1 {name=l3 lab=cm_bias}
C {devices/lab_wire.sym} 520 350 2 0 {name=l4 lab=cm_bias}
C {devices/lab_wire.sym} 700 350 2 0 {name=l5 lab=cm_bias}
C {devices/lab_wire.sym} -460 350 2 0 {name=l6 lab=cm_sense}
C {devices/lab_wire.sym} 20 350 2 0 {name=l7 lab=cm_sense}
C {devices/lab_wire.sym} 420 520 0 0 {name=l8 lab=cm_sense}
C {devices/lab_wire.sym} 520 430 0 1 {name=l9 lab=cm_sense}
C {devices/lab_wire.sym} -460 170 0 1 {name=l10 lab=cm_tail}
C {devices/lab_wire.sym} 20 170 0 1 {name=l11 lab=cm_tail}
C {devices/lab_wire.sym} 200 90 2 0 {name=l12 lab=cm_tail}
C {devices/lab_wire.sym} 520 170 0 1 {name=l13 lab=cm_tail}
C {devices/lab_wire.sym} 210 870 2 0 {name=l14 lab=csrc_n}
C {devices/lab_wire.sym} -190 870 2 0 {name=l15 lab=csrc_p}
C {devices/lab_wire.sym} 210 350 2 0 {name=l16 lab=d1n}
C {devices/lab_wire.sym} 210 430 0 1 {name=l17 lab=d1n}
C {devices/lab_wire.sym} -190 350 2 0 {name=l18 lab=d1p}
C {devices/lab_wire.sym} -190 430 0 1 {name=l19 lab=d1p}
C {devices/lab_wire.sym} -190 170 0 1 {name=l20 lab=tail}
C {devices/lab_wire.sym} 20 90 2 0 {name=l21 lab=tail}
C {devices/lab_wire.sym} 210 170 0 1 {name=l22 lab=tail}
C {devices/lab_wire.sym} -150 580 2 0 {name=l23 lab=vb1}
C {devices/lab_wire.sym} 170 460 0 1 {name=l24 lab=vb1}
C {devices/lab_wire.sym} -90 780 0 1 {name=l25 lab=vb2}
C {devices/lab_wire.sym} -80 0 0 0 {name=l26 lab=vb3}
C {devices/lab_wire.sym} 160 -60 0 1 {name=l27 lab=vb3}
C {devices/lab_wire.sym} 420 260 0 0 {name=l28 lab=vb4}
C {devices/lab_wire.sym} 660 260 0 0 {name=l29 lab=vb4}
C {devices/lab_wire.sym} -150 320 2 0 {name=l30 lab=vinn}
C {devices/lab_wire.sym} 170 200 0 1 {name=l31 lab=vinp}
C {devices/lab_wire.sym} -20 200 0 1 {name=l32 lab=voutn}
C {devices/lab_wire.sym} 210 610 2 0 {name=l33 lab=voutn}
C {devices/lab_wire.sym} -560 260 0 0 {name=l34 lab=voutp}
C {devices/lab_wire.sym} -190 610 2 0 {name=l35 lab=voutp}
C {devices/lab_wire.sym} 80 94 2 0 {name=l36 lab=vdd}
C {devices/lab_wire.sym} -250 614 2 0 {name=l37 lab=vdd}
C {devices/lab_wire.sym} 270 354 2 0 {name=l38 lab=vdd}
C {devices/lab_wire.sym} -250 354 2 0 {name=l39 lab=vdd}
C {devices/lab_wire.sym} 260 94 2 0 {name=l40 lab=vdd}
C {devices/lab_wire.sym} 80 354 2 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} 580 354 2 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} -400 354 2 0 {name=l43 lab=vdd}
C {devices/lab_wire.sym} 760 354 2 0 {name=l44 lab=vdd}
C {devices/lab_wire.sym} 270 614 2 0 {name=l45 lab=vdd}
C {devices/lab_wire.sym} 270 874 2 0 {name=l46 lab=vss}
C {devices/lab_wire.sym} -250 874 2 0 {name=l47 lab=vss}
C {devices/lab_wire.sym} 270 1134 2 0 {name=l48 lab=vss}
C {devices/lab_wire.sym} -250 1134 2 0 {name=l49 lab=vss}
C {devices/lab_wire.sym} 80 614 2 0 {name=l50 lab=vss}
C {devices/lab_wire.sym} 580 614 2 0 {name=l51 lab=vss}
C {devices/lab_wire.sym} -820 950 0 1 {name=l52 lab=vb1}
C {devices/lab_wire.sym} -820 1130 2 0 {name=l53 lab=vss}
C {devices/lab_wire.sym} -820 870 2 0 {name=l54 lab=vss}
C {devices/lab_wire.sym} -820 610 2 0 {name=l55 lab=vss}
C {devices/lab_wire.sym} -820 350 2 0 {name=l56 lab=vss}
C {devices/lab_wire.sym} -820 690 0 1 {name=l57 lab=vb2}
C {devices/lab_wire.sym} -820 430 0 1 {name=l58 lab=vb3}
C {devices/lab_wire.sym} -820 170 0 1 {name=l59 lab=vb4}
C {devices/lab_wire.sym} 20 610 2 0 {name=l60 lab=vss}
C {devices/ipin.sym} -1020 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -1020 380 0 0 {name=p1 lab=vinp}
C {devices/opin.sym} 1030 260 0 0 {name=p2 lab=voutp}
C {devices/opin.sym} 1030 380 0 0 {name=p3 lab=voutn}
