v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_026_fan_chopper_ota} -1210 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 265 520 0 0 {name=CM1 value='x_dut_cm1_value'}
C {devices/capa_np.sym} 515 520 0 0 {name=CM2 value='x_dut_cm2_value'}
C {devices/vsource_np.sym} -1170 780 0 0 {name=VB1 value="dc \{vb1\}" savecurrent=false}
C {devices/vsource_np.sym} -1170 520 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -1170 260 0 0 {name=VB3 value="dc \{vb3\}" savecurrent=false}
C {devices/vsource_np.sym} -1170 0 0 0 {name=VB4 value="dc \{vb4\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 265 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -380 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 990 260 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} 990 520 0 0 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} -380 520 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 95 260 0 1 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 525 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} -150 520 0 1 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} -605 520 0 1 {name=M17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 1215 520 0 0 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_pmos_np.sym} 765 520 0 0 {name=M19 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} 265 260 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1440 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_pmos_np.sym} 1670 520 0 0 {name=M21 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 75 520 0 1 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} -830 520 0 1 {name=M23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_pmos_np.sym} 1345 260 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} 265 780 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 515 780 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} -380 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 990 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 95 0 0 1 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 525 0 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1170 -90 -1170 -30 {}
N -1170 30 -1170 90 {}
N -1170 170 -1170 230 {}
N -1170 290 -1170 350 {}
N -1170 430 -1170 490 {}
N -1170 550 -1170 610 {}
N -1170 690 -1170 750 {}
N -1170 810 -1170 870 {}
N -910 520 -910 614 {}
N -850 460 -850 490 {}
N -850 550 -850 580 {}
N -810 -140 -810 520 {}
N -685 520 -685 614 {}
N -625 460 -625 490 {}
N -625 550 -625 610 {}
N -585 520 -585 920 {}
N -460 0 -460 94 {}
N -460 260 -460 354 {}
N -460 520 -460 614 {}
N -400 -140 -400 -30 {}
N -400 30 -400 230 {}
N -400 290 -400 460 {}
N -400 460 -400 490 {}
N -400 550 -400 610 {}
N -360 0 -360 60 {}
N -360 260 -360 320 {}
N -330 -60 -330 0 {}
N -230 520 -230 614 {}
N -170 460 -170 490 {}
N -170 550 -170 610 {}
N -130 -140 -130 520 {}
N -5 520 -5 614 {}
N 15 0 15 94 {}
N 15 260 15 354 {}
N 55 460 55 490 {}
N 75 -140 75 -30 {}
N 75 30 75 230 {}
N 75 290 75 920 {}
N 85 260 85 460 {}
N 95 520 95 920 {}
N 115 260 115 320 {}
N 115 550 115 580 {}
N 145 -60 145 0 {}
N 205 260 205 550 {}
N 215 -60 215 0 {}
N 215 780 215 840 {}
N 265 460 265 490 {}
N 265 550 265 610 {}
N 285 -140 285 -30 {}
N 285 30 285 200 {}
N 285 200 285 230 {}
N 285 290 285 750 {}
N 285 810 285 920 {}
N 315 460 315 580 {}
N 345 0 345 94 {}
N 345 260 345 354 {}
N 345 780 345 874 {}
N 465 780 465 840 {}
N 475 -60 475 0 {}
N 515 260 515 490 {}
N 515 550 515 610 {}
N 535 690 535 750 {}
N 535 810 535 920 {}
N 545 -140 545 -30 {}
N 545 30 545 60 {}
N 545 170 545 230 {}
N 545 290 545 920 {}
N 595 780 595 874 {}
N 605 0 605 94 {}
N 605 260 605 354 {}
N 745 520 745 920 {}
N 785 460 785 490 {}
N 785 550 785 610 {}
N 845 520 845 614 {}
N 970 -60 970 0 {}
N 1010 -140 1010 -30 {}
N 1010 30 1010 90 {}
N 1010 290 1010 460 {}
N 1010 460 1010 490 {}
N 1010 550 1010 610 {}
N 1070 60 1070 230 {}
N 1070 260 1070 354 {}
N 1070 520 1070 614 {}
N 1195 -140 1195 520 {}
N 1235 460 1235 490 {}
N 1235 550 1235 610 {}
N 1295 520 1295 614 {}
N 1365 200 1365 230 {}
N 1365 290 1365 350 {}
N 1420 520 1420 920 {}
N 1425 260 1425 354 {}
N 1460 460 1460 490 {}
N 1460 550 1460 580 {}
N 1520 520 1520 614 {}
N 1650 -140 1650 520 {}
N 1690 460 1690 490 {}
N 1690 550 1690 580 {}
N 1750 520 1750 614 {}
N -1330 -140 2170 -140 {}
N -330 -60 145 -60 {}
N 215 -60 475 -60 {}
N -460 0 -400 0 {}
N -360 0 -330 0 {}
N 15 0 75 0 {}
N 115 0 245 0 {}
N 285 0 345 0 {}
N 475 0 505 0 {}
N 545 0 605 0 {}
N 940 0 970 0 {}
N 1010 60 1070 60 {}
N 225 200 1365 200 {}
N 1010 230 1070 230 {}
N -460 260 -400 260 {}
N -360 260 -330 260 {}
N 15 260 75 260 {}
N 85 260 205 260 {}
N 215 260 245 260 {}
N 285 260 345 260 {}
N 445 260 515 260 {}
N 545 260 605 260 {}
N 940 260 970 260 {}
N 1010 260 1070 260 {}
N 1235 260 1325 260 {}
N 1365 260 1425 260 {}
N -850 460 55 460 {}
N 85 460 265 460 {}
N 315 460 515 460 {}
N 785 460 1690 460 {}
N -910 520 -850 520 {}
N -685 520 -625 520 {}
N -460 520 -400 520 {}
N -360 520 -300 520 {}
N -230 520 -170 520 {}
N -5 520 55 520 {}
N 785 520 845 520 {}
N 910 520 970 520 {}
N 1010 520 1070 520 {}
N 1235 520 1295 520 {}
N 1460 520 1520 520 {}
N 1690 520 1750 520 {}
N 55 550 205 550 {}
N -850 580 115 580 {}
N 315 580 1690 580 {}
N 185 780 245 780 {}
N 285 780 345 780 {}
N 465 780 495 780 {}
N 535 780 595 780 {}
N 215 840 465 840 {}
N -1330 920 2170 920 {}
C {devices/lab_wire.sym} -400 90 2 0 {name=l0 lab=casc_src_n}
C {devices/lab_wire.sym} 1010 90 2 0 {name=l1 lab=casc_src_p}
C {devices/lab_wire.sym} -400 610 2 0 {name=l2 lab=fold_n}
C {devices/lab_wire.sym} 535 690 0 1 {name=l3 lab=fold_n}
C {devices/lab_wire.sym} 1365 350 2 0 {name=l4 lab=fold_n}
C {devices/lab_wire.sym} 285 350 2 0 {name=l5 lab=fold_p}
C {devices/lab_wire.sym} 1010 610 2 0 {name=l6 lab=fold_p}
C {devices/lab_wire.sym} -625 610 2 0 {name=l7 lab=g2_n}
C {devices/lab_wire.sym} -170 610 2 0 {name=l8 lab=g2_n}
C {devices/lab_wire.sym} 445 260 0 0 {name=l9 lab=g2_n}
C {devices/lab_wire.sym} 115 320 2 0 {name=l10 lab=g2_p}
C {devices/lab_wire.sym} 785 610 2 0 {name=l11 lab=g2_p}
C {devices/lab_wire.sym} 1235 610 2 0 {name=l12 lab=g2_p}
C {devices/lab_wire.sym} -400 350 2 0 {name=l13 lab=out1_n}
C {devices/lab_wire.sym} 1010 350 2 0 {name=l14 lab=out1_p}
C {devices/lab_wire.sym} 285 90 2 0 {name=l15 lab=tail}
C {devices/lab_wire.sym} 185 780 0 0 {name=l16 lab=vb1}
C {devices/lab_wire.sym} -300 520 0 1 {name=l17 lab=vb2}
C {devices/lab_wire.sym} 910 520 0 0 {name=l18 lab=vb2}
C {devices/lab_wire.sym} -360 320 2 0 {name=l19 lab=vb3}
C {devices/lab_wire.sym} 970 260 0 0 {name=l20 lab=vb3}
C {devices/lab_wire.sym} -360 60 2 0 {name=l21 lab=vb4}
C {devices/lab_wire.sym} 970 -60 0 1 {name=l22 lab=vb4}
C {devices/lab_wire.sym} 515 610 2 0 {name=l23 lab=voutn}
C {devices/lab_wire.sym} 545 170 0 1 {name=l24 lab=voutn}
C {devices/lab_wire.sym} 265 610 2 0 {name=l25 lab=voutp}
C {devices/lab_wire.sym} 345 94 2 0 {name=l26 lab=vdd}
C {devices/lab_wire.sym} -460 354 2 0 {name=l27 lab=vdd}
C {devices/lab_wire.sym} 1070 354 2 0 {name=l28 lab=vdd}
C {devices/lab_wire.sym} -685 614 2 0 {name=l29 lab=vdd}
C {devices/lab_wire.sym} 845 614 2 0 {name=l30 lab=vdd}
C {devices/lab_wire.sym} 345 354 2 0 {name=l31 lab=vdd}
C {devices/lab_wire.sym} 1750 614 2 0 {name=l32 lab=vdd}
C {devices/lab_wire.sym} -910 614 2 0 {name=l33 lab=vdd}
C {devices/lab_wire.sym} 1425 354 2 0 {name=l34 lab=vdd}
C {devices/lab_wire.sym} -460 94 2 0 {name=l35 lab=vdd}
C {devices/lab_wire.sym} 1010 0 0 0 {name=l36 lab=vdd}
C {devices/lab_wire.sym} 15 94 2 0 {name=l37 lab=vdd}
C {devices/lab_wire.sym} 605 94 2 0 {name=l38 lab=vdd}
C {devices/lab_wire.sym} 1070 614 2 0 {name=l39 lab=vss}
C {devices/lab_wire.sym} -460 614 2 0 {name=l40 lab=vss}
C {devices/lab_wire.sym} 15 354 2 0 {name=l41 lab=vss}
C {devices/lab_wire.sym} 605 354 2 0 {name=l42 lab=vss}
C {devices/lab_wire.sym} -230 614 2 0 {name=l43 lab=vss}
C {devices/lab_wire.sym} 1295 614 2 0 {name=l44 lab=vss}
C {devices/lab_wire.sym} 1520 614 2 0 {name=l45 lab=vss}
C {devices/lab_wire.sym} -5 614 2 0 {name=l46 lab=vss}
C {devices/lab_wire.sym} 345 874 2 0 {name=l47 lab=vss}
C {devices/lab_wire.sym} 595 874 2 0 {name=l48 lab=vss}
C {devices/lab_wire.sym} -1170 690 0 1 {name=l49 lab=vb1}
C {devices/lab_wire.sym} -1170 870 2 0 {name=l50 lab=vss}
C {devices/lab_wire.sym} -1170 610 2 0 {name=l51 lab=vss}
C {devices/lab_wire.sym} -1170 350 2 0 {name=l52 lab=vss}
C {devices/lab_wire.sym} -1170 90 2 0 {name=l53 lab=vss}
C {devices/lab_wire.sym} -1170 430 0 1 {name=l54 lab=vb2}
C {devices/lab_wire.sym} -1170 170 0 1 {name=l55 lab=vb3}
C {devices/lab_wire.sym} -1170 -90 0 1 {name=l56 lab=vb4}
C {devices/ipin.sym} 215 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} 1235 260 0 0 {name=p1 lab=vinn}
C {devices/iopin.sym} -1330 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1330 920 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 75 60 0 0 {name=p4 lab=voutp}
C {devices/opin.sym} 545 60 0 0 {name=p5 lab=voutn}
B 8 195 182 1801 338 {fill=0}
T {PMOS Differential Pair} 195 164 0 0 0.3 0.3 {layer=8}
