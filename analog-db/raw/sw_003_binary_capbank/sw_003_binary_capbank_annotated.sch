v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sw_003_binary_capbank} -1220 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 650 0 1 0 {name=C1 value='Cu' m=x_dut_c1_m}
C {devices/capa_np.sym} -1020 0 0 0 {name=C2 value='Cu' m=x_dut_c2_m}
C {devices/capa_np.sym} 810 0 0 0 {name=C3 value='Cu' m=x_dut_c3_m}
C {devices/capa_np.sym} -1180 0 0 0 {name=C4 value='Cu' m=x_dut_c4_m}
C {devices/sg13_lv_nmos_np.sym} -80 0 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -730 0 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_nmos_np.sym} 1245 0 0 0 {name=M11 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} 1685 0 0 0 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_pmos_np.sym} -515 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1470 0 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 1025 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 395 0 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 175 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} 2130 0 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 1915 0 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_nmos_np.sym} -295 0 0 1 {name=M9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1180 -60 -1180 -30 {}
N -1180 30 -1180 90 {}
N -1020 -60 -1020 -30 {}
N -1020 30 -1020 90 {}
N -810 0 -810 94 {}
N -750 -90 -750 -30 {}
N -750 30 -750 90 {}
N -595 0 -595 94 {}
N -535 -90 -535 -30 {}
N -535 30 -535 90 {}
N -375 0 -375 94 {}
N -315 -90 -315 -30 {}
N -315 30 -315 90 {}
N -160 0 -160 94 {}
N -100 -90 -100 -30 {}
N -100 30 -100 90 {}
N 155 30 155 90 {}
N 315 0 315 94 {}
N 375 30 375 90 {}
N 650 -30 650 0 {}
N 710 -60 710 0 {}
N 770 -60 770 0 {}
N 810 -60 810 -30 {}
N 810 30 810 120 {}
N 1005 -60 1005 0 {}
N 1045 -60 1045 -30 {}
N 1045 30 1045 90 {}
N 1105 0 1105 94 {}
N 1265 -60 1265 -30 {}
N 1265 30 1265 90 {}
N 1325 0 1325 94 {}
N 1490 -60 1490 -30 {}
N 1490 30 1490 90 {}
N 1550 0 1550 94 {}
N 1705 -60 1705 -30 {}
N 1705 30 1705 90 {}
N 1765 0 1765 94 {}
N 1935 -60 1935 -30 {}
N 1935 30 1935 120 {}
N 1995 0 1995 94 {}
N 2150 -60 2150 -30 {}
N 2150 30 2150 60 {}
N 2210 0 2210 94 {}
N -1240 -140 2605 -140 {}
N -1180 -60 810 -60 {}
N 1045 -60 2150 -60 {}
N 95 -30 650 -30 {}
N -810 0 -750 0 {}
N -710 0 -680 0 {}
N -595 0 -535 0 {}
N -495 0 -465 0 {}
N -375 0 -315 0 {}
N -275 0 -245 0 {}
N -160 0 -100 0 {}
N -60 0 -30 0 {}
N 195 0 225 0 {}
N 315 0 375 0 {}
N 415 0 445 0 {}
N 590 0 650 0 {}
N 680 0 770 0 {}
N 975 0 1005 0 {}
N 1045 0 1105 0 {}
N 1165 0 1225 0 {}
N 1265 0 1325 0 {}
N 1390 0 1450 0 {}
N 1490 0 1550 0 {}
N 1605 0 1665 0 {}
N 1705 0 1765 0 {}
N 1835 0 1895 0 {}
N 1935 0 1995 0 {}
N 2050 0 2110 0 {}
N 2150 0 2210 0 {}
N 95 30 375 30 {}
N 1935 60 2150 60 {}
N 375 90 810 90 {}
N 810 120 1935 120 {}
N -1240 140 2605 140 {}
C {devices/lab_wire.sym} -1240 -140 0 0 {name=l0 lab=VDD}
C {devices/lab_wire.sym} -1240 140 0 0 {name=l1 lab=VSS}
C {devices/lab_wire.sym} 1005 -60 0 1 {name=l2 lab=V_D0}
C {devices/lab_wire.sym} 1390 0 0 0 {name=l3 lab=V_D0_NOT}
C {devices/lab_wire.sym} 1835 0 0 0 {name=l4 lab=V_D1}
C {devices/lab_wire.sym} 2050 0 0 0 {name=l5 lab=V_D1_NOT}
C {devices/lab_wire.sym} 1605 0 0 0 {name=l6 lab=V_D2}
C {devices/lab_wire.sym} 1165 0 0 0 {name=l7 lab=V_D2_NOT}
C {devices/lab_wire.sym} -1020 90 2 0 {name=l8 lab=bot0}
C {devices/lab_wire.sym} -535 90 2 0 {name=l9 lab=bot0}
C {devices/lab_wire.sym} -100 90 2 0 {name=l10 lab=bot0}
C {devices/lab_wire.sym} 1045 90 2 0 {name=l11 lab=bot0}
C {devices/lab_wire.sym} 1490 90 2 0 {name=l12 lab=bot0}
C {devices/lab_wire.sym} 155 90 2 0 {name=l13 lab=bot1}
C {devices/lab_wire.sym} -1180 90 2 0 {name=l14 lab=bot2}
C {devices/lab_wire.sym} -750 90 2 0 {name=l15 lab=bot2}
C {devices/lab_wire.sym} -315 90 2 0 {name=l16 lab=bot2}
C {devices/lab_wire.sym} 1265 90 2 0 {name=l17 lab=bot2}
C {devices/lab_wire.sym} 1705 90 2 0 {name=l18 lab=bot2}
C {devices/lab_wire.sym} -750 -90 0 1 {name=l19 lab=vinp}
C {devices/lab_wire.sym} -535 -90 0 1 {name=l20 lab=vinp}
C {devices/lab_wire.sym} -315 -90 0 1 {name=l21 lab=vinp}
C {devices/lab_wire.sym} -100 -90 0 1 {name=l22 lab=vinp}
C {devices/lab_wire.sym} -810 94 2 0 {name=l23 lab=VDD}
C {devices/lab_wire.sym} 1765 94 2 0 {name=l24 lab=VDD}
C {devices/lab_wire.sym} -595 94 2 0 {name=l25 lab=VDD}
C {devices/lab_wire.sym} 1105 94 2 0 {name=l26 lab=VDD}
C {devices/lab_wire.sym} 155 0 0 0 {name=l27 lab=VDD}
C {devices/lab_wire.sym} 1995 94 2 0 {name=l28 lab=VDD}
C {devices/lab_wire.sym} -160 94 2 0 {name=l29 lab=VSS}
C {devices/lab_wire.sym} 1325 94 2 0 {name=l30 lab=VSS}
C {devices/lab_wire.sym} 1550 94 2 0 {name=l31 lab=VSS}
C {devices/lab_wire.sym} 315 94 2 0 {name=l32 lab=VSS}
C {devices/lab_wire.sym} 2210 94 2 0 {name=l33 lab=VSS}
C {devices/lab_wire.sym} -375 94 2 0 {name=l34 lab=VSS}
C {devices/ipin.sym} -680 0 0 0 {name=p0 lab=V_D2_NOT}
C {devices/ipin.sym} -465 0 0 0 {name=p1 lab=V_D0_NOT}
C {devices/ipin.sym} -245 0 0 0 {name=p2 lab=V_D2}
C {devices/ipin.sym} -30 0 0 0 {name=p3 lab=V_D0}
C {devices/ipin.sym} 225 0 0 0 {name=p4 lab=V_D1_NOT}
C {devices/ipin.sym} 445 0 0 0 {name=p5 lab=V_D1}
C {devices/iopin.sym} 710 0 0 0 {name=p6 lab=vout}
C {devices/opin.sym} 650 -30 0 0 {name=p7 lab=vinp}
C {devices/opin.sym} 2150 -60 0 0 {name=p8 lab=VCM}
B 8 -971 -78 -10 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -971 -96 0 0 0.3 0.3 {layer=8}
B 10 -1210 -78 -225 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1210 -96 0 0 0.3 0.3 {layer=10}
B 12 1175 -78 2165 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1175 -96 0 0 0.3 0.3 {layer=12}
B 21 955 -78 1926 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 955 -96 0 0 0.3 0.3 {layer=21}
B 15 -281 -78 465 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -281 -96 0 0 0.3 0.3 {layer=15}
B 13 1845 -78 2586 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1845 -96 0 0 0.3 0.3 {layer=13}
