v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_026_fan_chopper_ota} -1210 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 110 520 0 0 {name=CM1 value='x_dut_cm1_value'}
C {devices/capa_np.sym} 325 520 0 0 {name=CM2 value='x_dut_cm2_value'}
C {devices/vsource_np.sym} -1170 780 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -1170 520 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -1170 260 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -1170 0 0 0 {name=VB4 value="dc {vb4}"}
C {devices/sg13_lv_pmos_np.sym} 110 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -455 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 725 260 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} 725 520 0 0 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} -455 520 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} -60 260 0 1 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 335 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} -265 520 0 1 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} -640 520 0 1 {name=M17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 910 520 0 0 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_pmos_np.sym} 535 520 0 0 {name=M19 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} 110 260 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1100 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_pmos_np.sym} 1290 520 0 0 {name=M21 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} -80 520 0 1 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} -830 520 0 1 {name=M23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_pmos_np.sym} 1040 260 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} 110 780 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 325 780 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} -455 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 725 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} -60 0 0 1 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 335 0 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
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
N -850 550 -850 610 {}
N -810 -140 -810 520 {}
N -720 520 -720 614 {}
N -660 460 -660 490 {}
N -660 550 -660 610 {}
N -620 520 -620 920 {}
N -535 0 -535 94 {}
N -535 260 -535 354 {}
N -535 520 -535 614 {}
N -475 -140 -475 -30 {}
N -475 30 -475 230 {}
N -475 290 -475 490 {}
N -475 550 -475 610 {}
N -435 520 -435 580 {}
N -345 520 -345 614 {}
N -285 460 -285 490 {}
N -285 550 -285 610 {}
N -245 -140 -245 520 {}
N -160 520 -160 614 {}
N -140 0 -140 94 {}
N -140 260 -140 354 {}
N -100 460 -100 490 {}
N -100 550 -100 610 {}
N -80 -140 -80 -30 {}
N -80 30 -80 230 {}
N -80 290 -80 920 {}
N -60 520 -60 920 {}
N -40 0 -40 60 {}
N -40 260 -40 320 {}
N 110 260 110 490 {}
N 110 550 110 610 {}
N 130 -140 130 -30 {}
N 130 30 130 230 {}
N 130 290 130 750 {}
N 130 810 130 920 {}
N 190 0 190 94 {}
N 190 260 190 354 {}
N 190 780 190 874 {}
N 305 720 305 780 {}
N 315 -60 315 0 {}
N 315 200 315 260 {}
N 325 260 325 490 {}
N 325 550 325 610 {}
N 345 690 345 750 {}
N 345 810 345 920 {}
N 355 -140 355 -30 {}
N 355 30 355 90 {}
N 355 170 355 230 {}
N 355 290 355 350 {}
N 405 780 405 874 {}
N 415 0 415 94 {}
N 415 260 415 354 {}
N 515 520 515 920 {}
N 555 460 555 490 {}
N 555 550 555 610 {}
N 615 520 615 614 {}
N 745 -140 745 -30 {}
N 745 30 745 90 {}
N 745 170 745 230 {}
N 745 290 745 490 {}
N 745 550 745 610 {}
N 805 0 805 94 {}
N 805 260 805 354 {}
N 805 520 805 614 {}
N 890 -140 890 520 {}
N 930 460 930 490 {}
N 930 550 930 610 {}
N 990 520 990 614 {}
N 1020 200 1020 260 {}
N 1060 170 1060 230 {}
N 1060 290 1060 720 {}
N 1080 520 1080 920 {}
N 1120 260 1120 354 {}
N 1120 460 1120 490 {}
N 1120 550 1120 610 {}
N 1180 520 1180 614 {}
N 1270 -140 1270 520 {}
N 1310 460 1310 490 {}
N 1310 550 1310 580 {}
N 1370 520 1370 614 {}
N -1230 -140 1505 -140 {}
N -535 0 -475 0 {}
N -435 0 -375 0 {}
N -140 0 -80 0 {}
N -40 0 90 0 {}
N 130 0 190 0 {}
N 285 0 315 0 {}
N 355 0 415 0 {}
N 645 0 705 0 {}
N 745 0 805 0 {}
N -80 200 110 200 {}
N -535 260 -475 260 {}
N -435 260 -375 260 {}
N -140 260 -80 260 {}
N -40 260 -10 260 {}
N 60 260 90 260 {}
N 130 260 190 260 {}
N 285 260 325 260 {}
N 355 260 415 260 {}
N 645 260 705 260 {}
N 745 260 805 260 {}
N 990 260 1020 260 {}
N 1060 260 1120 260 {}
N -850 460 -100 460 {}
N 555 460 1310 460 {}
N -910 520 -850 520 {}
N -720 520 -660 520 {}
N -535 520 -475 520 {}
N -435 520 -405 520 {}
N -345 520 -285 520 {}
N -160 520 -100 520 {}
N 555 520 615 520 {}
N 675 520 705 520 {}
N 745 520 805 520 {}
N 930 520 990 520 {}
N 1120 520 1180 520 {}
N 1310 520 1370 520 {}
N 1120 580 1310 580 {}
N 30 780 90 780 {}
N 130 780 190 780 {}
N 275 780 305 780 {}
N 345 780 405 780 {}
N -1230 920 1505 920 {}
C {devices/lab_wire.sym} -1230 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1230 920 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -475 90 2 0 {name=l2 lab=casc_src_n}
C {devices/lab_wire.sym} 745 90 2 0 {name=l3 lab=casc_src_p}
C {devices/lab_wire.sym} 745 170 0 1 {name=l4 lab=casc_src_p}
C {devices/lab_wire.sym} -475 610 2 0 {name=l5 lab=fold_n}
C {devices/lab_wire.sym} 345 690 0 1 {name=l6 lab=fold_n}
C {devices/lab_wire.sym} 1060 350 2 0 {name=l7 lab=fold_n}
C {devices/lab_wire.sym} 130 350 2 0 {name=l8 lab=fold_p}
C {devices/lab_wire.sym} 745 610 2 0 {name=l9 lab=fold_p}
C {devices/lab_wire.sym} -660 610 2 0 {name=l10 lab=g2_n}
C {devices/lab_wire.sym} -285 610 2 0 {name=l11 lab=g2_n}
C {devices/lab_wire.sym} 315 200 0 1 {name=l12 lab=g2_n}
C {devices/lab_wire.sym} 1120 610 2 0 {name=l13 lab=g2_n}
C {devices/lab_wire.sym} -850 610 2 0 {name=l14 lab=g2_p}
C {devices/lab_wire.sym} -100 610 2 0 {name=l15 lab=g2_p}
C {devices/lab_wire.sym} -40 320 2 0 {name=l16 lab=g2_p}
C {devices/lab_wire.sym} 110 430 0 1 {name=l17 lab=g2_p}
C {devices/lab_wire.sym} 555 610 2 0 {name=l18 lab=g2_p}
C {devices/lab_wire.sym} 930 610 2 0 {name=l19 lab=g2_p}
C {devices/lab_wire.sym} -475 350 2 0 {name=l20 lab=out1_n}
C {devices/lab_wire.sym} 745 350 2 0 {name=l21 lab=out1_p}
C {devices/lab_wire.sym} 130 90 2 0 {name=l22 lab=tail}
C {devices/lab_wire.sym} 1060 170 0 1 {name=l23 lab=tail}
C {devices/lab_wire.sym} 30 780 0 0 {name=l24 lab=vb1}
C {devices/lab_wire.sym} 305 720 0 1 {name=l25 lab=vb1}
C {devices/lab_wire.sym} -435 580 2 0 {name=l26 lab=vb2}
C {devices/lab_wire.sym} 705 520 0 0 {name=l27 lab=vb2}
C {devices/lab_wire.sym} -375 260 0 1 {name=l28 lab=vb3}
C {devices/lab_wire.sym} 645 260 0 0 {name=l29 lab=vb3}
C {devices/lab_wire.sym} -375 0 0 1 {name=l30 lab=vb4}
C {devices/lab_wire.sym} -40 60 2 0 {name=l31 lab=vb4}
C {devices/lab_wire.sym} 315 -60 0 1 {name=l32 lab=vb4}
C {devices/lab_wire.sym} 645 0 0 0 {name=l33 lab=vb4}
C {devices/lab_wire.sym} 1020 200 0 1 {name=l34 lab=vinn}
C {devices/lab_wire.sym} 90 260 0 0 {name=l35 lab=vinp}
C {devices/lab_wire.sym} 325 610 2 0 {name=l36 lab=voutn}
C {devices/lab_wire.sym} 355 90 2 0 {name=l37 lab=voutn}
C {devices/lab_wire.sym} 355 170 0 1 {name=l38 lab=voutn}
C {devices/lab_wire.sym} -80 90 2 0 {name=l39 lab=voutp}
C {devices/lab_wire.sym} 110 610 2 0 {name=l40 lab=voutp}
C {devices/lab_wire.sym} 190 94 2 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} -535 354 2 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} 805 354 2 0 {name=l43 lab=vdd}
C {devices/lab_wire.sym} -720 614 2 0 {name=l44 lab=vdd}
C {devices/lab_wire.sym} 615 614 2 0 {name=l45 lab=vdd}
C {devices/lab_wire.sym} 190 354 2 0 {name=l46 lab=vdd}
C {devices/lab_wire.sym} 1370 614 2 0 {name=l47 lab=vdd}
C {devices/lab_wire.sym} -910 614 2 0 {name=l48 lab=vdd}
C {devices/lab_wire.sym} 1120 354 2 0 {name=l49 lab=vdd}
C {devices/lab_wire.sym} -535 94 2 0 {name=l50 lab=vdd}
C {devices/lab_wire.sym} 805 94 2 0 {name=l51 lab=vdd}
C {devices/lab_wire.sym} -140 94 2 0 {name=l52 lab=vdd}
C {devices/lab_wire.sym} 415 94 2 0 {name=l53 lab=vdd}
C {devices/lab_wire.sym} 805 614 2 0 {name=l54 lab=vss}
C {devices/lab_wire.sym} -535 614 2 0 {name=l55 lab=vss}
C {devices/lab_wire.sym} -140 354 2 0 {name=l56 lab=vss}
C {devices/lab_wire.sym} 415 354 2 0 {name=l57 lab=vss}
C {devices/lab_wire.sym} -345 614 2 0 {name=l58 lab=vss}
C {devices/lab_wire.sym} 990 614 2 0 {name=l59 lab=vss}
C {devices/lab_wire.sym} 1180 614 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} -160 614 2 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} 190 874 2 0 {name=l62 lab=vss}
C {devices/lab_wire.sym} 405 874 2 0 {name=l63 lab=vss}
C {devices/lab_wire.sym} -1170 690 0 1 {name=l64 lab=vb1}
C {devices/lab_wire.sym} -1170 870 2 0 {name=l65 lab=vss}
C {devices/lab_wire.sym} -1170 610 2 0 {name=l66 lab=vss}
C {devices/lab_wire.sym} -1170 350 2 0 {name=l67 lab=vss}
C {devices/lab_wire.sym} -1170 90 2 0 {name=l68 lab=vss}
C {devices/lab_wire.sym} -1170 430 0 1 {name=l69 lab=vb2}
C {devices/lab_wire.sym} -1170 170 0 1 {name=l70 lab=vb3}
C {devices/lab_wire.sym} -1170 -90 0 1 {name=l71 lab=vb4}
C {devices/lab_wire.sym} 355 350 2 0 {name=l72 lab=vss}
C {devices/ipin.sym} -1370 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -1370 380 0 0 {name=p1 lab=vinn}
C {devices/opin.sym} 1645 30 0 0 {name=p2 lab=voutp}
C {devices/opin.sym} 1645 150 0 0 {name=p3 lab=voutn}
B 8 40 182 1228 338 {fill=0}
T {PMOS Differential Pair} 40 164 0 0 0.3 0.3 {layer=8}
