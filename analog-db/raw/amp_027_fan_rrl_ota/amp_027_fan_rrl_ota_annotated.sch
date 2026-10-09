v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_027_fan_rrl_ota} -860 -200 0 0 0.4 0.4 {}
C {devices/vsource_np.sym} -820 1040 0 0 {name=VB1 value="dc \{vb1\}" savecurrent=false}
C {devices/vsource_np.sym} -820 780 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -820 520 0 0 {name=VB3 value="dc \{vb3\}" savecurrent=false}
C {devices/vsource_np.sym} -820 260 0 0 {name=VB4 value="dc \{vb4\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 40 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -130 520 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_nmos_np.sym} 270 780 0 0 {name=M11 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -130 780 0 1 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 270 1040 0 0 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} -130 1040 0 1 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 40 520 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 580 520 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} 270 260 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -130 260 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 260 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 40 260 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 580 260 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} -480 260 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 800 260 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 270 520 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -820 170 -820 230 {}
N -820 290 -820 350 {}
N -820 430 -820 490 {}
N -820 550 -820 610 {}
N -820 690 -820 750 {}
N -820 810 -820 870 {}
N -820 950 -820 1010 {}
N -820 1070 -820 1130 {}
N -460 170 -460 230 {}
N -460 290 -460 320 {}
N -460 320 -460 350 {}
N -400 260 -400 354 {}
N -210 260 -210 354 {}
N -210 520 -210 614 {}
N -210 780 -210 874 {}
N -210 1040 -210 1134 {}
N -150 170 -150 230 {}
N -150 290 -150 350 {}
N -150 430 -150 490 {}
N -150 550 -150 750 {}
N -150 810 -150 1010 {}
N -150 1070 -150 1180 {}
N -110 520 -110 580 {}
N -80 1040 -80 1100 {}
N -10 -60 -10 0 {}
N -10 260 -10 640 {}
N 20 450 20 1100 {}
N 60 -140 60 -30 {}
N 60 30 60 90 {}
N 60 290 60 320 {}
N 60 430 60 490 {}
N 60 550 60 1180 {}
N 120 0 120 94 {}
N 120 200 120 230 {}
N 120 260 120 354 {}
N 120 520 120 614 {}
N 210 -60 210 0 {}
N 220 60 220 200 {}
N 280 -140 280 -30 {}
N 280 30 280 90 {}
N 290 170 290 230 {}
N 290 290 290 350 {}
N 290 430 290 490 {}
N 290 550 290 750 {}
N 290 810 290 1010 {}
N 290 1070 290 1180 {}
N 340 0 340 94 {}
N 350 260 350 354 {}
N 350 520 350 614 {}
N 350 780 350 874 {}
N 350 1040 350 1134 {}
N 600 200 600 230 {}
N 600 290 600 350 {}
N 600 430 600 490 {}
N 600 550 600 1180 {}
N 660 260 660 354 {}
N 660 520 660 614 {}
N 820 200 820 230 {}
N 820 290 820 350 {}
N 880 260 880 354 {}
N -880 -140 1275 -140 {}
N -10 -60 210 -60 {}
N -40 0 20 0 {}
N 60 0 120 0 {}
N 210 0 240 0 {}
N 280 0 340 0 {}
N 220 60 280 60 {}
N -460 200 120 200 {}
N 220 200 820 200 {}
N 60 230 120 230 {}
N -530 260 -500 260 {}
N -460 260 -400 260 {}
N -210 260 -150 260 {}
N -110 260 -80 260 {}
N -10 260 20 260 {}
N 60 260 120 260 {}
N 160 260 250 260 {}
N 290 260 350 260 {}
N 500 260 560 260 {}
N 600 260 660 260 {}
N 720 260 780 260 {}
N 820 260 880 260 {}
N -520 320 60 320 {}
N 20 450 60 450 {}
N -210 520 -150 520 {}
N -110 520 -80 520 {}
N 60 520 120 520 {}
N 190 520 250 520 {}
N 290 520 350 520 {}
N 500 520 560 520 {}
N 600 520 660 520 {}
N -10 640 290 640 {}
N -210 780 -150 780 {}
N -110 780 250 780 {}
N 290 780 350 780 {}
N -210 1040 -150 1040 {}
N -110 1040 250 1040 {}
N 290 1040 350 1040 {}
N -80 1100 20 1100 {}
N -880 1180 1275 1180 {}
C {devices/lab_wire.sym} 60 430 0 1 {name=l0 lab=cm_bias}
C {devices/lab_wire.sym} 600 350 2 0 {name=l1 lab=cm_bias}
C {devices/lab_wire.sym} 820 350 2 0 {name=l2 lab=cm_bias}
C {devices/lab_wire.sym} -460 350 2 0 {name=l3 lab=cm_sense}
C {devices/lab_wire.sym} 500 520 0 0 {name=l4 lab=cm_sense}
C {devices/lab_wire.sym} 600 430 0 1 {name=l5 lab=cm_sense}
C {devices/lab_wire.sym} -460 170 0 1 {name=l6 lab=cm_tail}
C {devices/lab_wire.sym} 280 90 2 0 {name=l7 lab=cm_tail}
C {devices/lab_wire.sym} 290 870 2 0 {name=l8 lab=csrc_n}
C {devices/lab_wire.sym} -150 870 2 0 {name=l9 lab=csrc_p}
C {devices/lab_wire.sym} 290 350 2 0 {name=l10 lab=d1n}
C {devices/lab_wire.sym} 290 430 0 1 {name=l11 lab=d1n}
C {devices/lab_wire.sym} -150 350 2 0 {name=l12 lab=d1p}
C {devices/lab_wire.sym} -150 430 0 1 {name=l13 lab=d1p}
C {devices/lab_wire.sym} -150 170 0 1 {name=l14 lab=tail}
C {devices/lab_wire.sym} 60 90 2 0 {name=l15 lab=tail}
C {devices/lab_wire.sym} 290 170 0 1 {name=l16 lab=tail}
C {devices/lab_wire.sym} -110 580 2 0 {name=l17 lab=vb1}
C {devices/lab_wire.sym} 190 520 0 0 {name=l18 lab=vb1}
C {devices/lab_wire.sym} -50 780 0 1 {name=l19 lab=vb2}
C {devices/lab_wire.sym} -40 0 0 0 {name=l20 lab=vb3}
C {devices/lab_wire.sym} 500 260 0 0 {name=l21 lab=vb4}
C {devices/lab_wire.sym} 720 260 0 0 {name=l22 lab=vb4}
C {devices/lab_wire.sym} -150 610 2 0 {name=l23 lab=voutp}
C {devices/lab_wire.sym} 120 94 2 0 {name=l24 lab=vdd}
C {devices/lab_wire.sym} -210 614 2 0 {name=l25 lab=vdd}
C {devices/lab_wire.sym} 350 354 2 0 {name=l26 lab=vdd}
C {devices/lab_wire.sym} -210 354 2 0 {name=l27 lab=vdd}
C {devices/lab_wire.sym} 340 94 2 0 {name=l28 lab=vdd}
C {devices/lab_wire.sym} 120 354 2 0 {name=l29 lab=vdd}
C {devices/lab_wire.sym} 660 354 2 0 {name=l30 lab=vdd}
C {devices/lab_wire.sym} -400 354 2 0 {name=l31 lab=vdd}
C {devices/lab_wire.sym} 880 354 2 0 {name=l32 lab=vdd}
C {devices/lab_wire.sym} 350 614 2 0 {name=l33 lab=vdd}
C {devices/lab_wire.sym} 350 874 2 0 {name=l34 lab=vss}
C {devices/lab_wire.sym} -210 874 2 0 {name=l35 lab=vss}
C {devices/lab_wire.sym} 350 1134 2 0 {name=l36 lab=vss}
C {devices/lab_wire.sym} -210 1134 2 0 {name=l37 lab=vss}
C {devices/lab_wire.sym} 120 614 2 0 {name=l38 lab=vss}
C {devices/lab_wire.sym} 660 614 2 0 {name=l39 lab=vss}
C {devices/lab_wire.sym} -820 950 0 1 {name=l40 lab=vb1}
C {devices/lab_wire.sym} -820 1130 2 0 {name=l41 lab=vss}
C {devices/lab_wire.sym} -820 870 2 0 {name=l42 lab=vss}
C {devices/lab_wire.sym} -820 610 2 0 {name=l43 lab=vss}
C {devices/lab_wire.sym} -820 350 2 0 {name=l44 lab=vss}
C {devices/lab_wire.sym} -820 690 0 1 {name=l45 lab=vb2}
C {devices/lab_wire.sym} -820 430 0 1 {name=l46 lab=vb3}
C {devices/lab_wire.sym} -820 170 0 1 {name=l47 lab=vb4}
C {devices/ipin.sym} -80 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} 160 260 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -880 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -880 1180 0 0 {name=p3 lab=vss}
C {devices/opin.sym} -530 260 0 0 {name=p4 lab=voutp}
C {devices/opin.sym} 290 580 0 0 {name=p5 lab=voutn}
B 8 -610 442 750 1118 {fill=0}
T {NMOS Simple Current Mirror (2 outputs)} -610 424 0 0 0.3 0.3 {layer=8}
B 10 -610 182 726 598 {fill=0}
T {PMOS Cascode Differential Pair Differential Pair} -610 164 0 0 0.3 0.3 {layer=10}
B 12 -30 182 1036 338 {fill=0}
T {PMOS Differential Pair} -30 164 0 0 0.3 0.3 {layer=12}
B 21 -30 182 1256 338 {fill=0}
T {PMOS Differential Pair} -30 140 0 0 0.3 0.3 {layer=21}
B 15 -550 182 1036 338 {fill=0}
T {PMOS Differential Pair} -550 164 0 0 0.3 0.3 {layer=15}
B 13 -550 182 1256 338 {fill=0}
T {PMOS Differential Pair} -550 140 0 0 0.3 0.3 {layer=13}
B 18 -564 204 704 316 {fill=0 dash=4}
T {PMOS Differential Pair} -564 114 0 0 0.3 0.3 {layer=18}
