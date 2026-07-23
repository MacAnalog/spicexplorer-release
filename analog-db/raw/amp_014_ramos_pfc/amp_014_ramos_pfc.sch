v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_014_ramos_pfc} -1740 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1275 260 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/capa_np.sym} 910 260 0 0 {name=C1 value='CAPACITOR_1'}
C {devices/isource_np.sym} -1700 520 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/sg13_lv_pmos_np.sym} -660 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -320 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -1360 0 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 1455 0 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -320 260 0 1 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 20 260 0 0 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 380 260 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} -1020 260 0 1 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 1090 260 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} -320 520 0 1 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 20 520 0 0 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} -1020 520 0 1 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} 20 0 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1090 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} -1360 260 0 1 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 720 260 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_nmos_np.sym} 1455 260 0 0 {name=M23 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_pmos_np.sym} 380 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 200 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} -1020 0 0 1 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 1090 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 720 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} -840 260 0 1 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 1755 260 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1700 430 -1700 490 {}
N -1700 550 -1700 610 {}
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
N -920 260 -920 354 {}
N -860 170 -860 230 {}
N -860 290 -860 320 {}
N -740 0 -740 94 {}
N -680 -140 -680 -30 {}
N -680 30 -680 70 {}
N -640 0 -640 70 {}
N -400 0 -400 94 {}
N -400 260 -400 354 {}
N -400 520 -400 614 {}
N -340 -140 -340 -30 {}
N -340 30 -340 90 {}
N -340 170 -340 230 {}
N -340 290 -340 490 {}
N -340 550 -340 660 {}
N 40 -140 40 -30 {}
N 40 30 40 90 {}
N 40 170 40 230 {}
N 40 290 40 490 {}
N 40 550 40 660 {}
N 100 0 100 94 {}
N 100 260 100 354 {}
N 100 520 100 614 {}
N 180 -60 180 0 {}
N 220 -140 220 -30 {}
N 220 30 220 90 {}
N 280 0 280 94 {}
N 360 -60 360 0 {}
N 360 190 360 260 {}
N 400 -140 400 -30 {}
N 400 30 400 90 {}
N 400 170 400 230 {}
N 400 290 400 660 {}
N 460 0 460 94 {}
N 460 260 460 354 {}
N 740 -140 740 -30 {}
N 740 30 740 90 {}
N 740 170 740 230 {}
N 740 290 740 660 {}
N 800 0 800 94 {}
N 800 260 800 354 {}
N 910 170 910 230 {}
N 910 290 910 350 {}
N 1040 0 1040 60 {}
N 1070 200 1070 260 {}
N 1110 -140 1110 -30 {}
N 1110 30 1110 90 {}
N 1110 170 1110 230 {}
N 1110 290 1110 350 {}
N 1110 430 1110 490 {}
N 1110 550 1110 660 {}
N 1170 0 1170 94 {}
N 1170 260 1170 354 {}
N 1170 520 1170 614 {}
N 1275 170 1275 230 {}
N 1275 290 1275 350 {}
N 1435 200 1435 260 {}
N 1475 -140 1475 -30 {}
N 1475 30 1475 90 {}
N 1475 170 1475 230 {}
N 1475 290 1475 350 {}
N 1535 0 1535 94 {}
N 1535 260 1535 354 {}
N 1735 200 1735 260 {}
N 1775 170 1775 230 {}
N 1775 290 1775 350 {}
N 1835 260 1835 354 {}
N -1760 -140 1965 -140 {}
N -1440 0 -1380 0 {}
N -1340 0 -1280 0 {}
N -1100 0 -1040 0 {}
N -1000 0 -940 0 {}
N -740 0 -680 0 {}
N -640 0 -580 0 {}
N -400 0 -340 0 {}
N -300 0 0 0 {}
N 40 0 100 0 {}
N 150 0 180 0 {}
N 220 0 280 0 {}
N 330 0 360 0 {}
N 400 0 460 0 {}
N 640 0 700 0 {}
N 740 0 800 0 {}
N 1010 0 1070 0 {}
N 1110 0 1170 0 {}
N 1275 0 1435 0 {}
N 1475 0 1535 0 {}
N -1040 70 -1000 70 {}
N -680 70 -640 70 {}
N -1380 190 -1340 190 {}
N 360 190 400 190 {}
N -1440 260 -1380 260 {}
N -1100 260 -1040 260 {}
N -1000 260 -970 260 {}
N -920 260 -860 260 {}
N -820 260 -760 260 {}
N -400 260 -340 260 {}
N -300 260 0 260 {}
N 40 260 100 260 {}
N 400 260 460 260 {}
N 640 260 700 260 {}
N 740 260 800 260 {}
N 1040 260 1070 260 {}
N 1110 260 1170 260 {}
N 1405 260 1435 260 {}
N 1475 260 1535 260 {}
N 1705 260 1735 260 {}
N 1775 260 1835 260 {}
N -1040 320 -860 320 {}
N -1100 520 -1040 520 {}
N -1000 520 -940 520 {}
N -400 520 -340 520 {}
N -300 520 0 520 {}
N 40 520 100 520 {}
N 1010 520 1070 520 {}
N 1110 520 1170 520 {}
N -1760 660 1965 660 {}
C {devices/lab_wire.sym} -1760 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1760 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 40 90 2 0 {name=l2 lab=DM_1}
C {devices/lab_wire.sym} 40 170 0 1 {name=l3 lab=DM_1}
C {devices/lab_wire.sym} -1040 350 2 0 {name=l4 lab=DM_2}
C {devices/lab_wire.sym} -1000 260 0 0 {name=l5 lab=VB3}
C {devices/lab_wire.sym} -240 260 0 1 {name=l6 lab=VB3}
C {devices/lab_wire.sym} 400 170 0 1 {name=l7 lab=VB3}
C {devices/lab_wire.sym} 400 90 2 0 {name=l8 lab=VB3}
C {devices/lab_wire.sym} 1070 200 0 1 {name=l9 lab=VB3}
C {devices/lab_wire.sym} -940 520 0 1 {name=l10 lab=VB4}
C {devices/lab_wire.sym} -340 90 2 0 {name=l11 lab=VB4}
C {devices/lab_wire.sym} -340 170 0 1 {name=l12 lab=VB4}
C {devices/lab_wire.sym} -240 520 0 1 {name=l13 lab=VB4}
C {devices/lab_wire.sym} 1010 520 0 0 {name=l14 lab=VB4}
C {devices/lab_wire.sym} -760 260 0 1 {name=l15 lab=VINN}
C {devices/lab_wire.sym} 1735 200 0 1 {name=l16 lab=VINP}
C {devices/lab_wire.sym} 1275 350 2 0 {name=l17 lab=VOUT}
C {devices/lab_wire.sym} 1475 90 2 0 {name=l18 lab=VOUT}
C {devices/lab_wire.sym} 1475 170 0 1 {name=l19 lab=VOUT}
C {devices/lab_wire.sym} -940 0 0 1 {name=l20 lab=VOUTN}
C {devices/lab_wire.sym} -1040 170 0 1 {name=l21 lab=VOUTN}
C {devices/lab_wire.sym} 1010 0 0 0 {name=l22 lab=VOUTN}
C {devices/lab_wire.sym} -1380 90 2 0 {name=l23 lab=net043}
C {devices/lab_wire.sym} 640 260 0 0 {name=l24 lab=net043}
C {devices/lab_wire.sym} 740 90 2 0 {name=l25 lab=net049}
C {devices/lab_wire.sym} 740 170 0 1 {name=l26 lab=net049}
C {devices/lab_wire.sym} 910 350 2 0 {name=l27 lab=net049}
C {devices/lab_wire.sym} 1435 200 0 1 {name=l28 lab=net049}
C {devices/lab_wire.sym} -1280 0 0 1 {name=l29 lab=net050}
C {devices/lab_wire.sym} 910 170 0 1 {name=l30 lab=net050}
C {devices/lab_wire.sym} 1110 90 2 0 {name=l31 lab=net050}
C {devices/lab_wire.sym} 1110 170 0 1 {name=l32 lab=net050}
C {devices/lab_wire.sym} 1275 170 0 1 {name=l33 lab=net050}
C {devices/lab_wire.sym} 1375 0 0 0 {name=l34 lab=net050}
C {devices/lab_wire.sym} 1110 350 2 0 {name=l35 lab=net063}
C {devices/lab_wire.sym} 1110 430 0 1 {name=l36 lab=net063}
C {devices/lab_wire.sym} 1775 350 2 0 {name=l37 lab=net063}
C {devices/lab_wire.sym} -580 0 0 1 {name=l38 lab=net1}
C {devices/lab_wire.sym} -240 0 0 1 {name=l39 lab=net1}
C {devices/lab_wire.sym} 180 -60 0 1 {name=l40 lab=net1}
C {devices/lab_wire.sym} 360 -60 0 1 {name=l41 lab=net1}
C {devices/lab_wire.sym} 640 0 0 0 {name=l42 lab=net1}
C {devices/lab_wire.sym} -860 170 0 1 {name=l43 lab=net31}
C {devices/lab_wire.sym} 220 90 2 0 {name=l44 lab=net31}
C {devices/lab_wire.sym} 1775 170 0 1 {name=l45 lab=net31}
C {devices/lab_wire.sym} -340 350 2 0 {name=l46 lab=net54}
C {devices/lab_wire.sym} 40 350 2 0 {name=l47 lab=net56}
C {devices/lab_wire.sym} -920 354 2 0 {name=l48 lab=net31}
C {devices/lab_wire.sym} 1835 354 2 0 {name=l49 lab=net31}
C {devices/lab_wire.sym} -740 94 2 0 {name=l50 lab=vdd}
C {devices/lab_wire.sym} -400 94 2 0 {name=l51 lab=vdd}
C {devices/lab_wire.sym} -1440 94 2 0 {name=l52 lab=vdd}
C {devices/lab_wire.sym} 1535 94 2 0 {name=l53 lab=vdd}
C {devices/lab_wire.sym} 100 94 2 0 {name=l54 lab=vdd}
C {devices/lab_wire.sym} 460 94 2 0 {name=l55 lab=vdd}
C {devices/lab_wire.sym} 280 94 2 0 {name=l56 lab=vdd}
C {devices/lab_wire.sym} -1100 94 2 0 {name=l57 lab=vdd}
C {devices/lab_wire.sym} 1170 94 2 0 {name=l58 lab=vdd}
C {devices/lab_wire.sym} 800 94 2 0 {name=l59 lab=vdd}
C {devices/lab_wire.sym} -400 354 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} 100 354 2 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} 460 354 2 0 {name=l62 lab=vss}
C {devices/lab_wire.sym} -1100 354 2 0 {name=l63 lab=vss}
C {devices/lab_wire.sym} 1170 354 2 0 {name=l64 lab=vss}
C {devices/lab_wire.sym} -400 614 2 0 {name=l65 lab=vss}
C {devices/lab_wire.sym} 100 614 2 0 {name=l66 lab=vss}
C {devices/lab_wire.sym} -1100 614 2 0 {name=l67 lab=vss}
C {devices/lab_wire.sym} 1170 614 2 0 {name=l68 lab=vss}
C {devices/lab_wire.sym} -1440 354 2 0 {name=l69 lab=vss}
C {devices/lab_wire.sym} 800 354 2 0 {name=l70 lab=vss}
C {devices/lab_wire.sym} 1535 354 2 0 {name=l71 lab=vss}
C {devices/lab_wire.sym} -1700 430 0 1 {name=l72 lab=net1}
C {devices/lab_wire.sym} -1700 610 2 0 {name=l73 lab=vss}
C {devices/lab_wire.sym} 1475 350 2 0 {name=l74 lab=vss}
C {devices/ipin.sym} -1900 260 0 0 {name=p0 lab=VINN}
C {devices/ipin.sym} -1900 380 0 0 {name=p1 lab=VINP}
