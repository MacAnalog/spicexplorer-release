v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sw_003_binary_capbank} -1220 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 585 0 1 0 {name=C1 value='Cu' m=x_dut_c1_m}
C {devices/capa_np.sym} -1020 0 0 0 {name=C2 value='Cu' m=x_dut_c2_m}
C {devices/capa_np.sym} 745 0 0 0 {name=C3 value='Cu' m=x_dut_c3_m}
C {devices/capa_np.sym} -1180 0 0 0 {name=C4 value='Cu' m=x_dut_c4_m}
C {devices/sg13_lv_nmos_np.sym} -135 0 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -735 0 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_nmos_np.sym} 1170 0 0 0 {name=M11 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} 1585 0 0 0 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_pmos_np.sym} -555 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1380 0 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 960 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 330 0 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 120 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} 2005 0 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 1795 0 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_nmos_np.sym} -345 0 0 1 {name=M9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1180 -90 -1180 -30 {}
N -1180 30 -1180 90 {}
N -1020 -60 -1020 -30 {}
N -1020 30 -1020 90 {}
N -815 0 -815 94 {}
N -755 -90 -755 -30 {}
N -755 30 -755 90 {}
N -715 0 -715 60 {}
N -635 0 -635 94 {}
N -575 -90 -575 -30 {}
N -575 30 -575 90 {}
N -535 0 -535 60 {}
N -425 0 -425 94 {}
N -365 -90 -365 -30 {}
N -365 30 -365 90 {}
N -325 0 -325 60 {}
N -215 0 -215 94 {}
N -155 -90 -155 -30 {}
N -155 30 -155 90 {}
N -115 0 -115 60 {}
N 40 0 40 94 {}
N 100 -90 100 -30 {}
N 100 30 100 90 {}
N 140 0 140 60 {}
N 250 0 250 94 {}
N 310 -90 310 -30 {}
N 310 30 310 90 {}
N 645 -60 645 0 {}
N 745 -90 745 -30 {}
N 745 30 745 90 {}
N 940 -60 940 0 {}
N 980 -90 980 -30 {}
N 980 30 980 90 {}
N 1040 0 1040 94 {}
N 1190 -60 1190 -30 {}
N 1190 30 1190 90 {}
N 1250 0 1250 94 {}
N 1400 -60 1400 -30 {}
N 1400 30 1400 90 {}
N 1460 0 1460 94 {}
N 1605 -60 1605 -30 {}
N 1605 30 1605 90 {}
N 1665 0 1665 94 {}
N 1815 -60 1815 -30 {}
N 1815 30 1815 90 {}
N 1875 0 1875 94 {}
N 2025 -60 2025 -30 {}
N 2025 30 2025 60 {}
N 2085 0 2085 94 {}
N -1180 -60 -1020 -60 {}
N 645 -60 745 -60 {}
N 980 -60 2025 -60 {}
N -815 0 -755 0 {}
N -715 0 -685 0 {}
N -635 0 -575 0 {}
N -535 0 -505 0 {}
N -425 0 -365 0 {}
N -325 0 -295 0 {}
N -215 0 -155 0 {}
N -115 0 -85 0 {}
N 40 0 100 0 {}
N 140 0 170 0 {}
N 250 0 310 0 {}
N 350 0 410 0 {}
N 495 0 555 0 {}
N 615 0 645 0 {}
N 910 0 940 0 {}
N 980 0 1040 0 {}
N 1120 0 1150 0 {}
N 1190 0 1250 0 {}
N 1330 0 1360 0 {}
N 1400 0 1460 0 {}
N 1535 0 1565 0 {}
N 1605 0 1665 0 {}
N 1745 0 1775 0 {}
N 1815 0 1875 0 {}
N 1955 0 1985 0 {}
N 2025 0 2085 0 {}
N 1815 60 2025 60 {}
C {devices/lab_wire.sym} 980 -90 0 1 {name=l0 lab=VCM}
C {devices/lab_wire.sym} -115 60 2 0 {name=l1 lab=V_D0}
C {devices/lab_wire.sym} 940 -60 0 1 {name=l2 lab=V_D0}
C {devices/lab_wire.sym} -535 60 2 0 {name=l3 lab=V_D0_NOT}
C {devices/lab_wire.sym} 1360 0 0 0 {name=l4 lab=V_D0_NOT}
C {devices/lab_wire.sym} 410 0 0 1 {name=l5 lab=V_D1}
C {devices/lab_wire.sym} 1775 0 0 0 {name=l6 lab=V_D1}
C {devices/lab_wire.sym} 140 60 2 0 {name=l7 lab=V_D1_NOT}
C {devices/lab_wire.sym} 1985 0 0 0 {name=l8 lab=V_D1_NOT}
C {devices/lab_wire.sym} -325 60 2 0 {name=l9 lab=V_D2}
C {devices/lab_wire.sym} 1565 0 0 0 {name=l10 lab=V_D2}
C {devices/lab_wire.sym} -715 60 2 0 {name=l11 lab=V_D2_NOT}
C {devices/lab_wire.sym} 1150 0 0 0 {name=l12 lab=V_D2_NOT}
C {devices/lab_wire.sym} -1020 90 2 0 {name=l13 lab=bot0}
C {devices/lab_wire.sym} -575 90 2 0 {name=l14 lab=bot0}
C {devices/lab_wire.sym} -155 90 2 0 {name=l15 lab=bot0}
C {devices/lab_wire.sym} 980 90 2 0 {name=l16 lab=bot0}
C {devices/lab_wire.sym} 1400 90 2 0 {name=l17 lab=bot0}
C {devices/lab_wire.sym} 100 90 2 0 {name=l18 lab=bot1}
C {devices/lab_wire.sym} 310 90 2 0 {name=l19 lab=bot1}
C {devices/lab_wire.sym} 745 90 2 0 {name=l20 lab=bot1}
C {devices/lab_wire.sym} 1815 90 2 0 {name=l21 lab=bot1}
C {devices/lab_wire.sym} -1180 90 2 0 {name=l22 lab=bot2}
C {devices/lab_wire.sym} -755 90 2 0 {name=l23 lab=bot2}
C {devices/lab_wire.sym} -365 90 2 0 {name=l24 lab=bot2}
C {devices/lab_wire.sym} 1190 90 2 0 {name=l25 lab=bot2}
C {devices/lab_wire.sym} 1605 90 2 0 {name=l26 lab=bot2}
C {devices/lab_wire.sym} -755 -90 0 1 {name=l27 lab=vinp}
C {devices/lab_wire.sym} -575 -90 0 1 {name=l28 lab=vinp}
C {devices/lab_wire.sym} -365 -90 0 1 {name=l29 lab=vinp}
C {devices/lab_wire.sym} -155 -90 0 1 {name=l30 lab=vinp}
C {devices/lab_wire.sym} 100 -90 0 1 {name=l31 lab=vinp}
C {devices/lab_wire.sym} 310 -90 0 1 {name=l32 lab=vinp}
C {devices/lab_wire.sym} 495 0 0 0 {name=l33 lab=vinp}
C {devices/lab_wire.sym} -1180 -90 0 1 {name=l34 lab=vout}
C {devices/lab_wire.sym} 745 -90 0 1 {name=l35 lab=vout}
C {devices/lab_wire.sym} -815 94 2 0 {name=l36 lab=VDD}
C {devices/lab_wire.sym} 1665 94 2 0 {name=l37 lab=VDD}
C {devices/lab_wire.sym} -635 94 2 0 {name=l38 lab=VDD}
C {devices/lab_wire.sym} 1040 94 2 0 {name=l39 lab=VDD}
C {devices/lab_wire.sym} 40 94 2 0 {name=l40 lab=VDD}
C {devices/lab_wire.sym} 1875 94 2 0 {name=l41 lab=VDD}
C {devices/lab_wire.sym} -215 94 2 0 {name=l42 lab=VSS}
C {devices/lab_wire.sym} 1250 94 2 0 {name=l43 lab=VSS}
C {devices/lab_wire.sym} 1460 94 2 0 {name=l44 lab=VSS}
C {devices/lab_wire.sym} 250 94 2 0 {name=l45 lab=VSS}
C {devices/lab_wire.sym} 2085 94 2 0 {name=l46 lab=VSS}
C {devices/lab_wire.sym} -425 94 2 0 {name=l47 lab=VSS}
C {devices/ipin.sym} -1380 0 0 0 {name=p0 lab=V_D2_NOT}
C {devices/ipin.sym} -1380 120 0 0 {name=p1 lab=V_D0_NOT}
C {devices/ipin.sym} -1380 240 0 0 {name=p2 lab=V_D2}
C {devices/ipin.sym} -1380 360 0 0 {name=p3 lab=V_D0}
C {devices/ipin.sym} -1380 480 0 0 {name=p4 lab=V_D1_NOT}
C {devices/ipin.sym} -1380 600 0 0 {name=p5 lab=V_D1}
C {devices/iopin.sym} -1180 280 0 0 {name=p6 lab=vout}
C {devices/opin.sym} 2355 -30 0 0 {name=p7 lab=vinp}
C {devices/opin.sym} 2355 90 0 0 {name=p8 lab=VCM}
B 8 -743 -78 -65 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -743 -96 0 0 0.3 0.3 {layer=8}
B 10 -931 -78 -275 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -931 -96 0 0 0.3 0.3 {layer=10}
B 12 1100 -78 1781 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1100 -96 0 0 0.3 0.3 {layer=12}
B 21 890 -78 1568 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 890 -96 0 0 0.3 0.3 {layer=21}
B 15 -68 -78 400 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -68 -96 0 0 0.3 0.3 {layer=15}
B 13 1725 -78 2193 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1725 -96 0 0 0.3 0.3 {layer=13}
