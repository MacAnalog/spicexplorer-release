v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_010_peng_acbc} -1785 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1700 260 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/capa_np.sym} 800 260 1 0 {name=C1 value='CAPACITOR_1'}
C {devices/isource_np.sym} -1745 520 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/sg13_lv_pmos_np.sym} -620 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -280 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 1245 260 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} -1360 0 0 1 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} 1915 0 0 0 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} -280 260 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 125 260 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 575 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} -1020 260 0 1 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} 1470 260 0 0 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} -280 520 0 1 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 125 520 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} 125 0 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} -1020 520 0 1 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 1470 520 0 0 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} -1360 260 0 1 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_nmos_np.sym} 1020 260 0 0 {name=M23 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_nmos_np.sym} 350 260 0 0 {name=M24 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_nmos_np.sym} 1915 260 0 0 {name=M25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
C {devices/sg13_lv_pmos_np.sym} 575 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 350 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} -1020 0 0 1 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} -100 0 0 0 {name=M59 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm59_w l=x_dut_xm59_l m=x_dut_xm59_m}
C {devices/sg13_lv_pmos_np.sym} 1470 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 1020 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 2155 0 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} -800 260 0 1 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1745 430 -1745 490 {}
N -1745 550 -1745 610 {}
N -1440 0 -1440 94 {}
N -1440 260 -1440 354 {}
N -1380 -140 -1380 -30 {}
N -1380 30 -1380 230 {}
N -1380 290 -1380 660 {}
N -1340 190 -1340 260 {}
N -1100 0 -1100 94 {}
N -1100 260 -1100 354 {}
N -1100 520 -1100 614 {}
N -1040 -140 -1040 -30 {}
N -1040 30 -1040 70 {}
N -1040 170 -1040 230 {}
N -1040 290 -1040 490 {}
N -1040 550 -1040 660 {}
N -1000 0 -1000 70 {}
N -880 260 -880 354 {}
N -820 170 -820 230 {}
N -820 290 -820 320 {}
N -700 0 -700 94 {}
N -640 -140 -640 -30 {}
N -640 30 -640 70 {}
N -600 -60 -600 70 {}
N -360 30 -360 230 {}
N -360 260 -360 354 {}
N -360 520 -360 614 {}
N -300 -140 -300 -30 {}
N -300 30 -300 90 {}
N -300 290 -300 490 {}
N -300 550 -300 660 {}
N -230 -60 -230 0 {}
N -170 230 -170 520 {}
N -120 -60 -120 70 {}
N -80 -140 -80 -30 {}
N -80 30 -80 70 {}
N -20 0 -20 94 {}
N 75 520 75 580 {}
N 145 -140 145 -30 {}
N 145 30 145 90 {}
N 145 170 145 230 {}
N 145 290 145 490 {}
N 145 550 145 660 {}
N 205 0 205 94 {}
N 205 260 205 354 {}
N 205 520 205 614 {}
N 370 -140 370 -30 {}
N 370 30 370 90 {}
N 370 170 370 230 {}
N 370 290 370 660 {}
N 430 0 430 94 {}
N 430 260 430 354 {}
N 555 190 555 260 {}
N 595 -140 595 -30 {}
N 595 30 595 90 {}
N 595 170 595 230 {}
N 595 290 595 660 {}
N 655 0 655 94 {}
N 655 260 655 354 {}
N 830 260 830 320 {}
N 1000 -60 1000 0 {}
N 1040 -140 1040 -30 {}
N 1040 30 1040 90 {}
N 1040 290 1040 660 {}
N 1100 30 1100 230 {}
N 1100 260 1100 354 {}
N 1265 170 1265 230 {}
N 1265 290 1265 350 {}
N 1325 260 1325 354 {}
N 1420 520 1420 580 {}
N 1450 -60 1450 0 {}
N 1490 -140 1490 -30 {}
N 1490 200 1490 230 {}
N 1490 290 1490 490 {}
N 1490 550 1490 660 {}
N 1550 30 1550 200 {}
N 1550 260 1550 354 {}
N 1550 520 1550 614 {}
N 1700 0 1700 230 {}
N 1700 290 1700 350 {}
N 1895 -60 1895 0 {}
N 1935 -140 1935 -30 {}
N 1935 30 1935 90 {}
N 1935 200 1935 230 {}
N 1935 290 1935 660 {}
N 1995 30 1995 200 {}
N 1995 260 1995 354 {}
N 2175 -140 2175 -30 {}
N 2175 30 2175 90 {}
N 2235 0 2235 94 {}
N -1860 -140 2630 -140 {}
N -600 -60 -230 -60 {}
N -1440 0 -1380 0 {}
N -1340 0 -1280 0 {}
N -1100 0 -1040 0 {}
N -1000 0 -940 0 {}
N -700 0 -640 0 {}
N -600 0 -540 0 {}
N -260 0 -230 0 {}
N -80 0 -20 0 {}
N 45 0 105 0 {}
N 145 0 205 0 {}
N 270 0 330 0 {}
N 370 0 430 0 {}
N 495 0 555 0 {}
N 595 0 655 0 {}
N 970 0 1000 0 {}
N 1420 0 1450 0 {}
N 1700 0 1895 0 {}
N 2075 0 2135 0 {}
N 2175 0 2235 0 {}
N -360 30 -300 30 {}
N 1040 30 1100 30 {}
N 1490 30 1550 30 {}
N 1935 30 1995 30 {}
N -1040 70 -1000 70 {}
N -640 70 -600 70 {}
N -120 70 -80 70 {}
N -1380 190 -1340 190 {}
N 555 190 595 190 {}
N 1490 200 1700 200 {}
N 1935 200 1995 200 {}
N -360 230 -170 230 {}
N 1040 230 1100 230 {}
N -1440 260 -1380 260 {}
N -1100 260 -1040 260 {}
N -1000 260 -940 260 {}
N -880 260 -820 260 {}
N -780 260 -750 260 {}
N -360 260 -300 260 {}
N -260 260 105 260 {}
N 145 260 205 260 {}
N 270 260 330 260 {}
N 370 260 430 260 {}
N 595 260 655 260 {}
N 710 260 770 260 {}
N 830 260 860 260 {}
N 940 260 1000 260 {}
N 1040 260 1100 260 {}
N 1135 260 1225 260 {}
N 1265 260 1325 260 {}
N 1390 260 1450 260 {}
N 1490 260 1550 260 {}
N 1835 260 1895 260 {}
N 1935 260 1995 260 {}
N -1040 320 -820 320 {}
N 1265 320 1490 320 {}
N -1100 520 -1040 520 {}
N -1000 520 -940 520 {}
N -360 520 -300 520 {}
N -260 520 105 520 {}
N 145 520 205 520 {}
N 1420 520 1450 520 {}
N 1490 520 1550 520 {}
N 75 580 1420 580 {}
N -1860 660 2630 660 {}
C {devices/lab_wire.sym} 145 90 2 0 {name=l0 lab=DM_1}
C {devices/lab_wire.sym} 145 170 0 1 {name=l1 lab=DM_1}
C {devices/lab_wire.sym} -1040 350 2 0 {name=l2 lab=DM_2}
C {devices/lab_wire.sym} -940 260 0 1 {name=l3 lab=VB3}
C {devices/lab_wire.sym} -200 260 0 1 {name=l4 lab=VB3}
C {devices/lab_wire.sym} 595 170 0 1 {name=l5 lab=VB3}
C {devices/lab_wire.sym} 595 90 2 0 {name=l6 lab=VB3}
C {devices/lab_wire.sym} 1390 260 0 0 {name=l7 lab=VB3}
C {devices/lab_wire.sym} -940 520 0 1 {name=l8 lab=VB4}
C {devices/lab_wire.sym} -300 90 2 0 {name=l9 lab=VB4}
C {devices/lab_wire.sym} 1700 350 2 0 {name=l10 lab=VOUT}
C {devices/lab_wire.sym} 1935 90 2 0 {name=l11 lab=VOUT}
C {devices/lab_wire.sym} -940 0 0 1 {name=l12 lab=VOUTN}
C {devices/lab_wire.sym} -1040 170 0 1 {name=l13 lab=VOUTN}
C {devices/lab_wire.sym} 1450 -60 0 1 {name=l14 lab=VOUTN}
C {devices/lab_wire.sym} -540 0 0 1 {name=l15 lab=net013}
C {devices/lab_wire.sym} 45 0 0 0 {name=l16 lab=net013}
C {devices/lab_wire.sym} 270 0 0 0 {name=l17 lab=net013}
C {devices/lab_wire.sym} 495 0 0 0 {name=l18 lab=net013}
C {devices/lab_wire.sym} 1000 -60 0 1 {name=l19 lab=net013}
C {devices/lab_wire.sym} 2075 0 0 0 {name=l20 lab=net013}
C {devices/lab_wire.sym} -1380 90 2 0 {name=l21 lab=net043}
C {devices/lab_wire.sym} 270 260 0 0 {name=l22 lab=net043}
C {devices/lab_wire.sym} 940 260 0 0 {name=l23 lab=net043}
C {devices/lab_wire.sym} 830 320 2 0 {name=l24 lab=net049}
C {devices/lab_wire.sym} 1040 90 2 0 {name=l25 lab=net049}
C {devices/lab_wire.sym} 1835 260 0 0 {name=l26 lab=net049}
C {devices/lab_wire.sym} -1280 0 0 1 {name=l27 lab=net050}
C {devices/lab_wire.sym} 1895 -60 0 1 {name=l28 lab=net050}
C {devices/lab_wire.sym} 1265 350 2 0 {name=l29 lab=net063}
C {devices/lab_wire.sym} -120 -60 0 1 {name=l30 lab=net1}
C {devices/lab_wire.sym} 370 170 0 1 {name=l31 lab=net1}
C {devices/lab_wire.sym} 710 260 0 0 {name=l32 lab=net1}
C {devices/lab_wire.sym} 2175 90 2 0 {name=l33 lab=net1}
C {devices/lab_wire.sym} -820 170 0 1 {name=l34 lab=net31}
C {devices/lab_wire.sym} 370 90 2 0 {name=l35 lab=net31}
C {devices/lab_wire.sym} 1265 170 0 1 {name=l36 lab=net31}
C {devices/lab_wire.sym} -300 350 2 0 {name=l37 lab=net54}
C {devices/lab_wire.sym} 145 350 2 0 {name=l38 lab=net56}
C {devices/lab_wire.sym} 1325 354 2 0 {name=l39 lab=net31}
C {devices/lab_wire.sym} -880 354 2 0 {name=l40 lab=net31}
C {devices/lab_wire.sym} -700 94 2 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} -300 0 0 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} -1440 94 2 0 {name=l43 lab=vdd}
C {devices/lab_wire.sym} 1935 0 0 0 {name=l44 lab=vdd}
C {devices/lab_wire.sym} 205 94 2 0 {name=l45 lab=vdd}
C {devices/lab_wire.sym} 655 94 2 0 {name=l46 lab=vdd}
C {devices/lab_wire.sym} 430 94 2 0 {name=l47 lab=vdd}
C {devices/lab_wire.sym} -1100 94 2 0 {name=l48 lab=vdd}
C {devices/lab_wire.sym} -20 94 2 0 {name=l49 lab=vdd}
C {devices/lab_wire.sym} 1490 0 0 0 {name=l50 lab=vdd}
C {devices/lab_wire.sym} 1040 0 0 0 {name=l51 lab=vdd}
C {devices/lab_wire.sym} 2235 94 2 0 {name=l52 lab=vdd}
C {devices/lab_wire.sym} -360 354 2 0 {name=l53 lab=vss}
C {devices/lab_wire.sym} 205 354 2 0 {name=l54 lab=vss}
C {devices/lab_wire.sym} 655 354 2 0 {name=l55 lab=vss}
C {devices/lab_wire.sym} -1100 354 2 0 {name=l56 lab=vss}
C {devices/lab_wire.sym} 1550 354 2 0 {name=l57 lab=vss}
C {devices/lab_wire.sym} -360 614 2 0 {name=l58 lab=vss}
C {devices/lab_wire.sym} 205 614 2 0 {name=l59 lab=vss}
C {devices/lab_wire.sym} -1100 614 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} 1550 614 2 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} -1440 354 2 0 {name=l62 lab=vss}
C {devices/lab_wire.sym} 1100 354 2 0 {name=l63 lab=vss}
C {devices/lab_wire.sym} 430 354 2 0 {name=l64 lab=vss}
C {devices/lab_wire.sym} 1995 354 2 0 {name=l65 lab=vss}
C {devices/lab_wire.sym} -1745 430 0 1 {name=l66 lab=net013}
C {devices/lab_wire.sym} -1745 610 2 0 {name=l67 lab=vss}
C {devices/ipin.sym} -750 260 0 0 {name=p0 lab=VINN}
C {devices/ipin.sym} 1135 260 0 0 {name=p1 lab=VINP}
C {devices/iopin.sym} -1860 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1860 660 0 0 {name=p3 lab=vss}
