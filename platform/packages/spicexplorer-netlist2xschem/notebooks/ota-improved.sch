v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ota-improved} -1060 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 1020 780 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=X_DUT_M5_W l=X_DUT_M5_L ng=X_DUT_M5_NG}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=X_DUT_M3M4_W l=X_DUT_M3M4_L}
C {devices/sg13_lv_nmos_np.sym} -680 780 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=X_DUT_M1M2_W l=X_DUT_M1M2_L}
C {devices/sg13_lv_nmos_np.sym} 680 780 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=X_DUT_M1M2_W l=X_DUT_M1M2_L}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=X_DUT_M3M4_W l=X_DUT_M3M4_L}
C {devices/sg13_lv_nmos_np.sym} 2555 520 0 0 {name=M6 model=sg13_lv_nmos spiceprefix=X w=X_DUT_M6_W l=X_DUT_M6_L}
C {devices/sg13_lv_nmos_np.sym} 2380 780 0 0 {name=MPD5 model=sg13_lv_nmos spiceprefix=X w=1u l=0.13u}
C {devices/sg13_lv_nmos_np.sym} 2040 260 0 0 {name=MPD3 model=sg13_lv_nmos spiceprefix=X w=1u l=0.13u}
C {devices/sg13_lv_pmos_np.sym} 2040 0 0 0 {name=MPD4 model=sg13_lv_pmos spiceprefix=X w=1u l=0.13u}
C {devices/sg13_lv_nmos_np.sym} 2380 520 0 0 {name=MPD6 model=sg13_lv_nmos spiceprefix=X w=1u l=0.13u}
C {devices/sg13_lv_nmos_np.sym} 680 520 0 0 {name=M2C model=sg13_lv_nmos spiceprefix=X w=X_DUT_M1CM2C_W l=X_DUT_M1CM2C_L}
C {devices/sg13_lv_nmos_np.sym} -680 520 0 1 {name=M1C model=sg13_lv_nmos spiceprefix=X w=X_DUT_M1CM2C_W l=X_DUT_M1CM2C_L}
C {devices/sg13_lv_pmos_np.sym} -340 260 0 1 {name=M4C model=sg13_lv_pmos spiceprefix=X w=X_DUT_M3CM4C_W l=X_DUT_M3PCM4C_L}
C {devices/sg13_lv_pmos_np.sym} 340 260 0 0 {name=M3C model=sg13_lv_pmos spiceprefix=X w=X_DUT_M3CM4C_W l=X_DUT_M3CM4C_L}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=MPD8 model=sg13_lv_pmos spiceprefix=X w=1u l=0.13u}
C {devices/vsource_np.sym} -1020 520 0 0 {name=VMEAS1 value=0}
C {devices/sg13_lv_nmos_np.sym} 1700 260 0 0 {name=MPD1 model=sg13_lv_nmos spiceprefix=X w=1u l=0.13u}
C {devices/sg13_lv_pmos_np.sym} 1700 0 0 0 {name=MPD2 model=sg13_lv_pmos spiceprefix=X w=1u l=0.13u}
C {devices/vsource_np.sym} -1020 260 0 0 {name=VMEAS4 value=0P}
C {devices/sg13_lv_nmos_np.sym} 170 520 0 1 {name=MPD11 model=sg13_lv_nmos spiceprefix=X w=0.5u l=0.13u}
C {devices/sg13_lv_nmos_np.sym} 1360 1040 0 1 {name=MDECOUP1 model=sg13_lv_nmos spiceprefix=X w=8u l=1u ng=4}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=MDECOUP3 model=sg13_lv_pmos spiceprefix=X w=12u l=0.5u ng=4}
C {devices/vsource_np.sym} -1020 1040 0 0 {name=V1 value=X_DUT_V_BIAS_2}
C {devices/vsource_np.sym} -1020 780 0 0 {name=V2 value=X_DUT_V_BIAS_1}
N -1020 170 -1020 230 {}
N -1020 290 -1020 350 {}
N -1020 430 -1020 490 {}
N -1020 550 -1020 610 {}
N -1020 690 -1020 750 {}
N -1020 810 -1020 870 {}
N -1020 950 -1020 1010 {}
N -1020 1070 -1020 1130 {}
N -760 520 -760 614 {}
N -760 780 -760 874 {}
N -700 430 -700 490 {}
N -700 550 -700 750 {}
N -700 810 -700 870 {}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 350 {}
N -320 0 -320 60 {}
N -250 0 -250 94 {}
N -190 -140 -190 -30 {}
N -190 30 -190 90 {}
N -150 0 -150 60 {}
N -50 0 -50 260 {}
N -20 -60 -20 0 {}
N 20 -140 20 30 {}
N 80 0 80 94 {}
N 90 520 90 614 {}
N 150 320 150 490 {}
N 150 550 150 1180 {}
N 360 -140 360 -30 {}
N 360 30 360 90 {}
N 360 170 360 230 {}
N 360 290 360 350 {}
N 420 0 420 94 {}
N 420 260 420 354 {}
N 700 460 700 490 {}
N 700 550 700 750 {}
N 700 810 700 840 {}
N 760 520 760 614 {}
N 760 780 760 874 {}
N 940 780 940 874 {}
N 1000 690 1000 750 {}
N 1000 810 1000 1180 {}
N 1280 1040 1280 1134 {}
N 1340 1010 1340 1180 {}
N 1410 780 1410 1040 {}
N 1650 0 1650 260 {}
N 1720 -140 1720 -30 {}
N 1720 30 1720 230 {}
N 1720 290 1720 1180 {}
N 1780 0 1780 94 {}
N 1780 260 1780 354 {}
N 1990 0 1990 260 {}
N 2060 -140 2060 -30 {}
N 2060 30 2060 230 {}
N 2060 290 2060 1180 {}
N 2120 0 2120 94 {}
N 2120 260 2120 354 {}
N 2400 430 2400 490 {}
N 2400 550 2400 750 {}
N 2400 810 2400 870 {}
N 2460 520 2460 614 {}
N 2460 780 2460 874 {}
N 2505 520 2505 580 {}
N 2575 460 2575 490 {}
N 2575 550 2575 1180 {}
N 2635 520 2635 614 {}
N -1080 -140 2755 -140 {}
N -420 0 -360 0 {}
N -320 0 -290 0 {}
N -250 0 -190 0 {}
N -150 0 -120 0 {}
N -50 0 -20 0 {}
N 20 0 80 0 {}
N 260 0 320 0 {}
N 360 0 420 0 {}
N 1620 0 1680 0 {}
N 1720 0 1780 0 {}
N 1960 0 2020 0 {}
N 2060 0 2120 0 {}
N 1720 60 1990 60 {}
N 2060 200 2330 200 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N 260 260 320 260 {}
N 360 260 420 260 {}
N 1650 260 1680 260 {}
N 1720 260 1780 260 {}
N 1990 260 2020 260 {}
N 2060 260 2120 260 {}
N -360 320 150 320 {}
N -700 460 -290 460 {}
N 150 460 700 460 {}
N 2400 460 2575 460 {}
N -760 520 -700 520 {}
N -660 520 -600 520 {}
N 90 520 150 520 {}
N 190 520 250 520 {}
N 600 520 660 520 {}
N 700 520 760 520 {}
N 2300 520 2360 520 {}
N 2400 520 2460 520 {}
N 2505 520 2535 520 {}
N 2575 520 2635 520 {}
N 2400 580 2505 580 {}
N -760 780 -700 780 {}
N -660 780 -600 780 {}
N 600 780 660 780 {}
N 700 780 760 780 {}
N 940 780 1000 780 {}
N 1040 780 1410 780 {}
N 2300 780 2360 780 {}
N 2400 780 2460 780 {}
N -700 840 700 840 {}
N 1280 1040 1340 1040 {}
N 1380 1040 1410 1040 {}
N -1080 1180 2755 1180 {}
C {devices/lab_wire.sym} -1080 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1080 1180 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 1620 0 0 0 {name=l2 lab=d_ena}
C {devices/lab_wire.sym} -600 520 0 1 {name=l3 lab=dp_casc}
C {devices/lab_wire.sym} 600 520 0 0 {name=l4 lab=dp_casc}
C {devices/lab_wire.sym} -150 60 2 0 {name=l5 lab=ena}
C {devices/lab_wire.sym} 2060 90 2 0 {name=l6 lab=ena}
C {devices/lab_wire.sym} 2300 520 0 0 {name=l7 lab=ena}
C {devices/lab_wire.sym} 250 520 0 1 {name=l8 lab=ena_n}
C {devices/lab_wire.sym} 1960 0 0 0 {name=l9 lab=ena_n}
C {devices/lab_wire.sym} 2300 780 0 0 {name=l10 lab=ena_n}
C {devices/lab_wire.sym} 1100 780 0 1 {name=l11 lab=gate}
C {devices/lab_wire.sym} 2535 520 0 0 {name=l12 lab=gate}
C {devices/lab_wire.sym} -700 430 0 1 {name=l13 lab=gate_p}
C {devices/lab_wire.sym} -320 60 2 0 {name=l14 lab=gate_p}
C {devices/lab_wire.sym} -190 90 2 0 {name=l15 lab=gate_p}
C {devices/lab_wire.sym} 260 0 0 0 {name=l16 lab=gate_p}
C {devices/lab_wire.sym} 360 350 2 0 {name=l17 lab=gate_p}
C {devices/lab_wire.sym} -260 260 0 1 {name=l18 lab=gate_pc}
C {devices/lab_wire.sym} -20 -60 0 1 {name=l19 lab=gate_pc}
C {devices/lab_wire.sym} 260 260 0 0 {name=l20 lab=gate_pc}
C {devices/lab_wire.sym} 2400 430 0 1 {name=l21 lab=net1}
C {devices/lab_wire.sym} -360 90 2 0 {name=l22 lab=net2}
C {devices/lab_wire.sym} 360 90 2 0 {name=l23 lab=net3}
C {devices/lab_wire.sym} 360 170 0 1 {name=l24 lab=net3}
C {devices/lab_wire.sym} -700 610 2 0 {name=l25 lab=net4}
C {devices/lab_wire.sym} 700 610 2 0 {name=l26 lab=net5}
C {devices/lab_wire.sym} 1000 690 0 1 {name=l27 lab=net6}
C {devices/lab_wire.sym} -700 870 2 0 {name=l28 lab=tail}
C {devices/lab_wire.sym} 600 780 0 0 {name=l29 lab=vinn}
C {devices/lab_wire.sym} -600 780 0 1 {name=l30 lab=vinp}
C {devices/lab_wire.sym} -360 350 2 0 {name=l31 lab=vout}
C {devices/lab_wire.sym} -420 94 2 0 {name=l32 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l33 lab=vdd}
C {devices/lab_wire.sym} 2120 94 2 0 {name=l34 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l35 lab=vdd}
C {devices/lab_wire.sym} 420 354 2 0 {name=l36 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l37 lab=vdd}
C {devices/lab_wire.sym} 1780 94 2 0 {name=l38 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l39 lab=vdd}
C {devices/lab_wire.sym} 940 874 2 0 {name=l40 lab=vss}
C {devices/lab_wire.sym} -760 874 2 0 {name=l41 lab=vss}
C {devices/lab_wire.sym} 760 874 2 0 {name=l42 lab=vss}
C {devices/lab_wire.sym} 2635 614 2 0 {name=l43 lab=vss}
C {devices/lab_wire.sym} 2460 874 2 0 {name=l44 lab=vss}
C {devices/lab_wire.sym} 2120 354 2 0 {name=l45 lab=vss}
C {devices/lab_wire.sym} 2460 614 2 0 {name=l46 lab=vss}
C {devices/lab_wire.sym} 760 614 2 0 {name=l47 lab=vss}
C {devices/lab_wire.sym} -760 614 2 0 {name=l48 lab=vss}
C {devices/lab_wire.sym} 1780 354 2 0 {name=l49 lab=vss}
C {devices/lab_wire.sym} 90 614 2 0 {name=l50 lab=vss}
C {devices/lab_wire.sym} 1280 1134 2 0 {name=l51 lab=vss}
C {devices/lab_wire.sym} -1020 610 2 0 {name=l52 lab=net6}
C {devices/lab_wire.sym} -1020 950 0 1 {name=l53 lab=vdd}
C {devices/lab_wire.sym} -1020 430 0 1 {name=l54 lab=tail}
C {devices/lab_wire.sym} -1020 870 2 0 {name=l55 lab=tail}
C {devices/lab_wire.sym} -1020 350 2 0 {name=l56 lab=net1}
C {devices/lab_wire.sym} -1020 690 0 1 {name=l57 lab=dp_casc}
C {devices/lab_wire.sym} -1020 1130 2 0 {name=l58 lab=gate_pc}
C {devices/lab_wire.sym} -1020 170 0 1 {name=l59 lab=ibias_5u}
C {devices/lab_wire.sym} 2400 870 2 0 {name=l60 lab=vss}
C {devices/ipin.sym} -1220 780 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -1220 900 0 0 {name=p1 lab=vinn}
C {devices/iopin.sym} -1020 1320 0 0 {name=p2 lab=ibias_5u}
