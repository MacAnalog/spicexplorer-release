v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_014_ramos_pfc} -1785 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1510 260 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/capa_np.sym} 1070 260 1 0 {name=C1 value='CAPACITOR_1'}
C {devices/isource_np.sym} -1745 520 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/sg13_lv_pmos_np.sym} -1020 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -1360 0 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 1730 0 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 60 260 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 840 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 1285 260 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} -680 520 0 1 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 1 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 840 520 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1285 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} -1360 260 0 1 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 400 260 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_nmos_np.sym} 1730 260 0 0 {name=M23 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_pmos_np.sym} 60 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -120 0 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 840 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 1285 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 400 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 625 260 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 2030 260 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1745 430 -1745 490 {}
N -1745 550 -1745 610 {}
N -1440 0 -1440 94 {}
N -1440 260 -1440 354 {}
N -1380 -140 -1380 -30 {}
N -1380 30 -1380 230 {}
N -1380 290 -1380 660 {}
N -1340 190 -1340 260 {}
N -1100 0 -1100 94 {}
N -1040 -140 -1040 -30 {}
N -1040 30 -1040 70 {}
N -1000 0 -1000 70 {}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -760 520 -760 614 {}
N -700 -140 -700 -30 {}
N -700 30 -700 90 {}
N -700 170 -700 230 {}
N -700 290 -700 490 {}
N -700 550 -700 660 {}
N -660 200 -660 260 {}
N -630 520 -630 580 {}
N -420 60 -420 230 {}
N -420 260 -420 354 {}
N -420 520 -420 614 {}
N -360 -140 -360 -30 {}
N -360 30 -360 90 {}
N -360 290 -360 490 {}
N -360 550 -360 660 {}
N -290 -60 -290 0 {}
N -290 200 -290 260 {}
N -290 520 -290 580 {}
N -200 0 -200 94 {}
N -140 -140 -140 -30 {}
N -140 30 -140 90 {}
N -70 -60 -70 0 {}
N 10 -60 10 0 {}
N 20 30 20 230 {}
N 40 190 40 260 {}
N 80 -140 80 -30 {}
N 80 30 80 90 {}
N 80 190 80 230 {}
N 80 290 80 660 {}
N 140 0 140 94 {}
N 140 260 140 354 {}
N 350 -60 350 0 {}
N 420 -140 420 -30 {}
N 420 30 420 90 {}
N 420 170 420 230 {}
N 420 290 420 660 {}
N 480 0 480 94 {}
N 480 260 480 354 {}
N 645 170 645 230 {}
N 645 290 645 350 {}
N 705 260 705 354 {}
N 790 520 790 580 {}
N 820 0 820 70 {}
N 860 -140 860 -30 {}
N 860 30 860 70 {}
N 860 170 860 230 {}
N 860 290 860 490 {}
N 860 550 860 660 {}
N 920 0 920 94 {}
N 920 260 920 354 {}
N 920 520 920 614 {}
N 1100 260 1100 320 {}
N 1235 0 1235 60 {}
N 1235 520 1235 580 {}
N 1305 -140 1305 -30 {}
N 1305 30 1305 90 {}
N 1305 290 1305 320 {}
N 1305 320 1305 490 {}
N 1305 550 1305 660 {}
N 1365 60 1365 230 {}
N 1365 260 1365 354 {}
N 1365 520 1365 614 {}
N 1510 290 1510 350 {}
N 1710 -60 1710 0 {}
N 1750 -140 1750 -30 {}
N 1750 30 1750 90 {}
N 1750 290 1750 660 {}
N 1810 60 1810 230 {}
N 1810 260 1810 354 {}
N 2050 170 2050 230 {}
N 2050 290 2050 320 {}
N 2110 260 2110 354 {}
N -1860 -140 2505 -140 {}
N -290 -60 -70 -60 {}
N 10 -60 350 -60 {}
N -1440 0 -1380 0 {}
N -1340 0 -1280 0 {}
N -1100 0 -1040 0 {}
N -1000 0 -940 0 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -320 0 -260 0 {}
N -200 0 -140 0 {}
N -100 0 40 0 {}
N 80 0 140 0 {}
N 350 0 380 0 {}
N 420 0 480 0 {}
N 760 0 820 0 {}
N 860 0 920 0 {}
N 1235 0 1265 0 {}
N 1680 0 1710 0 {}
N 20 30 80 30 {}
N -420 60 -360 60 {}
N 860 60 1235 60 {}
N 1305 60 1365 60 {}
N 1750 60 1810 60 {}
N -1040 70 -1000 70 {}
N 820 70 860 70 {}
N -1380 190 -1340 190 {}
N 40 190 80 190 {}
N -660 200 -290 200 {}
N -420 230 -360 230 {}
N 20 230 80 230 {}
N 1305 230 1570 230 {}
N 1750 230 1810 230 {}
N -1440 260 -1380 260 {}
N -760 260 -700 260 {}
N -420 260 -360 260 {}
N -350 260 40 260 {}
N 80 260 140 260 {}
N 320 260 380 260 {}
N 420 260 480 260 {}
N 515 260 605 260 {}
N 645 260 705 260 {}
N 760 260 820 260 {}
N 860 260 920 260 {}
N 980 260 1040 260 {}
N 1100 260 1130 260 {}
N 1205 260 1265 260 {}
N 1305 260 1365 260 {}
N 1650 260 1710 260 {}
N 1750 260 1810 260 {}
N 1920 260 2010 260 {}
N 2050 260 2110 260 {}
N 645 320 860 320 {}
N 1245 320 2050 320 {}
N -760 520 -700 520 {}
N -660 520 -600 520 {}
N -420 520 -360 520 {}
N -320 520 820 520 {}
N 860 520 920 520 {}
N 1235 520 1265 520 {}
N 1305 520 1365 520 {}
N -630 580 -290 580 {}
N 790 580 1235 580 {}
N -1860 660 2505 660 {}
C {devices/lab_wire.sym} -360 90 2 0 {name=l0 lab=DM_1}
C {devices/lab_wire.sym} 645 350 2 0 {name=l1 lab=DM_2}
C {devices/lab_wire.sym} 80 90 2 0 {name=l2 lab=VB3}
C {devices/lab_wire.sym} 760 260 0 0 {name=l3 lab=VB3}
C {devices/lab_wire.sym} 1205 260 0 0 {name=l4 lab=VB3}
C {devices/lab_wire.sym} -700 90 2 0 {name=l5 lab=VB4}
C {devices/lab_wire.sym} -700 170 0 1 {name=l6 lab=VB4}
C {devices/lab_wire.sym} -600 520 0 1 {name=l7 lab=VB4}
C {devices/lab_wire.sym} 1510 350 2 0 {name=l8 lab=VOUT}
C {devices/lab_wire.sym} 1750 90 2 0 {name=l9 lab=VOUT}
C {devices/lab_wire.sym} 760 0 0 0 {name=l10 lab=VOUTN}
C {devices/lab_wire.sym} 860 170 0 1 {name=l11 lab=VOUTN}
C {devices/lab_wire.sym} -1380 90 2 0 {name=l12 lab=net043}
C {devices/lab_wire.sym} 320 260 0 0 {name=l13 lab=net043}
C {devices/lab_wire.sym} 420 90 2 0 {name=l14 lab=net049}
C {devices/lab_wire.sym} 420 170 0 1 {name=l15 lab=net049}
C {devices/lab_wire.sym} 980 260 0 0 {name=l16 lab=net049}
C {devices/lab_wire.sym} 1650 260 0 0 {name=l17 lab=net049}
C {devices/lab_wire.sym} -1280 0 0 1 {name=l18 lab=net050}
C {devices/lab_wire.sym} 1100 320 2 0 {name=l19 lab=net050}
C {devices/lab_wire.sym} 1305 90 2 0 {name=l20 lab=net050}
C {devices/lab_wire.sym} 1710 -60 0 1 {name=l21 lab=net050}
C {devices/lab_wire.sym} 1305 350 2 0 {name=l22 lab=net063}
C {devices/lab_wire.sym} -940 0 0 1 {name=l23 lab=net1}
C {devices/lab_wire.sym} -600 0 0 1 {name=l24 lab=net1}
C {devices/lab_wire.sym} -260 0 0 1 {name=l25 lab=net1}
C {devices/lab_wire.sym} -140 90 2 0 {name=l26 lab=net31}
C {devices/lab_wire.sym} 645 170 0 1 {name=l27 lab=net31}
C {devices/lab_wire.sym} 2050 170 0 1 {name=l28 lab=net31}
C {devices/lab_wire.sym} -700 350 2 0 {name=l29 lab=net54}
C {devices/lab_wire.sym} -360 350 2 0 {name=l30 lab=net56}
C {devices/lab_wire.sym} 705 354 2 0 {name=l31 lab=net31}
C {devices/lab_wire.sym} 2110 354 2 0 {name=l32 lab=net31}
C {devices/lab_wire.sym} -1100 94 2 0 {name=l33 lab=vdd}
C {devices/lab_wire.sym} -760 94 2 0 {name=l34 lab=vdd}
C {devices/lab_wire.sym} -1440 94 2 0 {name=l35 lab=vdd}
C {devices/lab_wire.sym} 1750 0 0 0 {name=l36 lab=vdd}
C {devices/lab_wire.sym} -360 0 0 0 {name=l37 lab=vdd}
C {devices/lab_wire.sym} 140 94 2 0 {name=l38 lab=vdd}
C {devices/lab_wire.sym} -200 94 2 0 {name=l39 lab=vdd}
C {devices/lab_wire.sym} 920 94 2 0 {name=l40 lab=vdd}
C {devices/lab_wire.sym} 1305 0 0 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} 480 94 2 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l43 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l44 lab=vss}
C {devices/lab_wire.sym} 140 354 2 0 {name=l45 lab=vss}
C {devices/lab_wire.sym} 920 354 2 0 {name=l46 lab=vss}
C {devices/lab_wire.sym} 1365 354 2 0 {name=l47 lab=vss}
C {devices/lab_wire.sym} -760 614 2 0 {name=l48 lab=vss}
C {devices/lab_wire.sym} -420 614 2 0 {name=l49 lab=vss}
C {devices/lab_wire.sym} 920 614 2 0 {name=l50 lab=vss}
C {devices/lab_wire.sym} 1365 614 2 0 {name=l51 lab=vss}
C {devices/lab_wire.sym} -1440 354 2 0 {name=l52 lab=vss}
C {devices/lab_wire.sym} 480 354 2 0 {name=l53 lab=vss}
C {devices/lab_wire.sym} 1810 354 2 0 {name=l54 lab=vss}
C {devices/lab_wire.sym} -1745 430 0 1 {name=l55 lab=net1}
C {devices/lab_wire.sym} -1745 610 2 0 {name=l56 lab=vss}
C {devices/ipin.sym} 515 260 0 0 {name=p0 lab=VINN}
C {devices/ipin.sym} 1920 260 0 0 {name=p1 lab=VINP}
C {devices/iopin.sym} -1860 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1860 660 0 0 {name=p3 lab=vss}
B 8 -1476 -78 856 78 {fill=0}
T {PMOS Simple Current Mirror (5 outputs)} -1476 -96 0 0 0.3 0.3 {layer=8}
B 10 -1160 182 540 598 {fill=0}
T {NMOS Improved High Swing Cascode Current Mirror [alt: cm.nmos.low_voltage_cascode]} -1160 164 0 0 0.3 0.3 {layer=10}
B 12 -1840 182 880 338 {fill=0}
T {NMOS Simple Current Mirror} -1840 164 0 0 0.3 0.3 {layer=12}
B 21 770 -78 1741 78 {fill=0}
T {PMOS Simple Current Mirror} 770 -96 0 0 0.3 0.3 {layer=21}
B 15 555 182 2486 338 {fill=0}
T {PMOS Differential Pair} 555 164 0 0 0.3 0.3 {layer=15}
