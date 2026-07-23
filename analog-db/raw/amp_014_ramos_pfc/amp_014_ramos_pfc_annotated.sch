v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_014_ramos_pfc} -1740 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1285 260 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/capa_np.sym} 915 260 1 0 {name=C1 value='CAPACITOR_1'}
C {devices/isource_np.sym} -1700 520 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/sg13_lv_pmos_np.sym} -1020 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -1360 0 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 1465 0 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 20 260 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 730 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 1095 260 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} -680 520 0 1 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 1 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 730 520 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1095 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} -1360 260 0 1 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 360 260 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_nmos_np.sym} 1465 260 0 0 {name=M23 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_pmos_np.sym} 20 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -160 0 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 730 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 1095 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 360 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 550 260 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 1765 260 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1700 430 -1700 490 {}
N -1700 550 -1700 610 {}
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
N -630 0 -630 60 {}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -420 520 -420 614 {}
N -360 -140 -360 -30 {}
N -360 30 -360 90 {}
N -360 170 -360 230 {}
N -360 290 -360 490 {}
N -360 550 -360 660 {}
N -320 0 -320 60 {}
N -240 0 -240 94 {}
N -180 -140 -180 -30 {}
N -180 30 -180 90 {}
N -140 0 -140 60 {}
N 0 190 0 260 {}
N 40 -140 40 -30 {}
N 40 30 40 90 {}
N 40 170 40 230 {}
N 40 290 40 660 {}
N 100 0 100 94 {}
N 100 260 100 354 {}
N 310 200 310 260 {}
N 380 -140 380 -30 {}
N 380 30 380 90 {}
N 380 170 380 230 {}
N 380 290 380 660 {}
N 440 0 440 94 {}
N 440 260 440 354 {}
N 530 200 530 260 {}
N 570 170 570 230 {}
N 570 290 570 350 {}
N 630 260 630 354 {}
N 710 0 710 70 {}
N 710 200 710 260 {}
N 750 -140 750 -30 {}
N 750 30 750 70 {}
N 750 170 750 230 {}
N 750 290 750 490 {}
N 750 550 750 660 {}
N 810 0 810 94 {}
N 810 260 810 354 {}
N 810 520 810 614 {}
N 945 260 945 320 {}
N 975 0 975 260 {}
N 1045 0 1045 60 {}
N 1075 200 1075 260 {}
N 1115 -140 1115 -30 {}
N 1115 30 1115 90 {}
N 1115 170 1115 230 {}
N 1115 290 1115 490 {}
N 1115 550 1115 660 {}
N 1175 0 1175 94 {}
N 1175 260 1175 354 {}
N 1175 520 1175 614 {}
N 1285 170 1285 230 {}
N 1285 290 1285 350 {}
N 1445 200 1445 260 {}
N 1485 -140 1485 -30 {}
N 1485 30 1485 90 {}
N 1485 170 1485 230 {}
N 1485 290 1485 350 {}
N 1545 0 1545 94 {}
N 1545 260 1545 354 {}
N 1745 200 1745 260 {}
N 1785 170 1785 230 {}
N 1785 290 1785 350 {}
N 1845 260 1845 354 {}
N -1760 -140 1975 -140 {}
N -1440 0 -1380 0 {}
N -1340 0 -1280 0 {}
N -1100 0 -1040 0 {}
N -1000 0 -940 0 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -420 0 -360 0 {}
N -320 0 -290 0 {}
N -240 0 -180 0 {}
N -140 0 0 0 {}
N 40 0 100 0 {}
N 280 0 340 0 {}
N 380 0 440 0 {}
N 650 0 710 0 {}
N 750 0 810 0 {}
N 1045 0 1075 0 {}
N 1115 0 1175 0 {}
N 1385 0 1445 0 {}
N 1485 0 1545 0 {}
N 750 60 1045 60 {}
N -1040 70 -1000 70 {}
N 710 70 750 70 {}
N -1380 190 -1340 190 {}
N 0 190 40 190 {}
N -1440 260 -1380 260 {}
N -760 260 -700 260 {}
N -660 260 -600 260 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N 40 260 100 260 {}
N 280 260 340 260 {}
N 380 260 440 260 {}
N 500 260 530 260 {}
N 570 260 630 260 {}
N 680 260 710 260 {}
N 750 260 810 260 {}
N 825 260 885 260 {}
N 945 260 975 260 {}
N 1045 260 1075 260 {}
N 1115 260 1175 260 {}
N 1415 260 1445 260 {}
N 1485 260 1545 260 {}
N 1715 260 1745 260 {}
N 1785 260 1845 260 {}
N 570 320 750 320 {}
N -760 520 -700 520 {}
N -660 520 -600 520 {}
N -420 520 -360 520 {}
N -320 520 710 520 {}
N 750 520 810 520 {}
N 1015 520 1075 520 {}
N 1115 520 1175 520 {}
N -1760 660 1975 660 {}
C {devices/lab_wire.sym} -1760 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1760 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -360 90 2 0 {name=l2 lab=DM_1}
C {devices/lab_wire.sym} -360 170 0 1 {name=l3 lab=DM_1}
C {devices/lab_wire.sym} 570 350 2 0 {name=l4 lab=DM_2}
C {devices/lab_wire.sym} -600 260 0 1 {name=l5 lab=VB3}
C {devices/lab_wire.sym} -260 260 0 1 {name=l6 lab=VB3}
C {devices/lab_wire.sym} 40 170 0 1 {name=l7 lab=VB3}
C {devices/lab_wire.sym} 40 90 2 0 {name=l8 lab=VB3}
C {devices/lab_wire.sym} 710 200 0 1 {name=l9 lab=VB3}
C {devices/lab_wire.sym} 1075 200 0 1 {name=l10 lab=VB3}
C {devices/lab_wire.sym} -700 90 2 0 {name=l11 lab=VB4}
C {devices/lab_wire.sym} -700 170 0 1 {name=l12 lab=VB4}
C {devices/lab_wire.sym} -600 520 0 1 {name=l13 lab=VB4}
C {devices/lab_wire.sym} -260 520 0 1 {name=l14 lab=VB4}
C {devices/lab_wire.sym} 1015 520 0 0 {name=l15 lab=VB4}
C {devices/lab_wire.sym} 530 200 0 1 {name=l16 lab=VINN}
C {devices/lab_wire.sym} 1745 200 0 1 {name=l17 lab=VINP}
C {devices/lab_wire.sym} 1285 350 2 0 {name=l18 lab=VOUT}
C {devices/lab_wire.sym} 1485 90 2 0 {name=l19 lab=VOUT}
C {devices/lab_wire.sym} 1485 170 0 1 {name=l20 lab=VOUT}
C {devices/lab_wire.sym} 650 0 0 0 {name=l21 lab=VOUTN}
C {devices/lab_wire.sym} 750 170 0 1 {name=l22 lab=VOUTN}
C {devices/lab_wire.sym} -1380 90 2 0 {name=l23 lab=net043}
C {devices/lab_wire.sym} 280 260 0 0 {name=l24 lab=net043}
C {devices/lab_wire.sym} 380 90 2 0 {name=l25 lab=net049}
C {devices/lab_wire.sym} 380 170 0 1 {name=l26 lab=net049}
C {devices/lab_wire.sym} 825 260 0 0 {name=l27 lab=net049}
C {devices/lab_wire.sym} 1445 200 0 1 {name=l28 lab=net049}
C {devices/lab_wire.sym} -1280 0 0 1 {name=l29 lab=net050}
C {devices/lab_wire.sym} 945 320 2 0 {name=l30 lab=net050}
C {devices/lab_wire.sym} 1115 90 2 0 {name=l31 lab=net050}
C {devices/lab_wire.sym} 1115 170 0 1 {name=l32 lab=net050}
C {devices/lab_wire.sym} 1285 170 0 1 {name=l33 lab=net050}
C {devices/lab_wire.sym} 1385 0 0 0 {name=l34 lab=net050}
C {devices/lab_wire.sym} 1115 350 2 0 {name=l35 lab=net063}
C {devices/lab_wire.sym} 1785 350 2 0 {name=l36 lab=net063}
C {devices/lab_wire.sym} -940 0 0 1 {name=l37 lab=net1}
C {devices/lab_wire.sym} -600 0 0 1 {name=l38 lab=net1}
C {devices/lab_wire.sym} -320 60 2 0 {name=l39 lab=net1}
C {devices/lab_wire.sym} -140 60 2 0 {name=l40 lab=net1}
C {devices/lab_wire.sym} 280 0 0 0 {name=l41 lab=net1}
C {devices/lab_wire.sym} -180 90 2 0 {name=l42 lab=net31}
C {devices/lab_wire.sym} 570 170 0 1 {name=l43 lab=net31}
C {devices/lab_wire.sym} 1785 170 0 1 {name=l44 lab=net31}
C {devices/lab_wire.sym} -700 350 2 0 {name=l45 lab=net54}
C {devices/lab_wire.sym} -360 350 2 0 {name=l46 lab=net56}
C {devices/lab_wire.sym} 630 354 2 0 {name=l47 lab=net31}
C {devices/lab_wire.sym} 1845 354 2 0 {name=l48 lab=net31}
C {devices/lab_wire.sym} -1100 94 2 0 {name=l49 lab=vdd}
C {devices/lab_wire.sym} -760 94 2 0 {name=l50 lab=vdd}
C {devices/lab_wire.sym} -1440 94 2 0 {name=l51 lab=vdd}
C {devices/lab_wire.sym} 1545 94 2 0 {name=l52 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l53 lab=vdd}
C {devices/lab_wire.sym} 100 94 2 0 {name=l54 lab=vdd}
C {devices/lab_wire.sym} -240 94 2 0 {name=l55 lab=vdd}
C {devices/lab_wire.sym} 810 94 2 0 {name=l56 lab=vdd}
C {devices/lab_wire.sym} 1175 94 2 0 {name=l57 lab=vdd}
C {devices/lab_wire.sym} 440 94 2 0 {name=l58 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l59 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} 100 354 2 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} 810 354 2 0 {name=l62 lab=vss}
C {devices/lab_wire.sym} 1175 354 2 0 {name=l63 lab=vss}
C {devices/lab_wire.sym} -760 614 2 0 {name=l64 lab=vss}
C {devices/lab_wire.sym} -420 614 2 0 {name=l65 lab=vss}
C {devices/lab_wire.sym} 810 614 2 0 {name=l66 lab=vss}
C {devices/lab_wire.sym} 1175 614 2 0 {name=l67 lab=vss}
C {devices/lab_wire.sym} -1440 354 2 0 {name=l68 lab=vss}
C {devices/lab_wire.sym} 440 354 2 0 {name=l69 lab=vss}
C {devices/lab_wire.sym} 1545 354 2 0 {name=l70 lab=vss}
C {devices/lab_wire.sym} -1700 430 0 1 {name=l71 lab=net1}
C {devices/lab_wire.sym} -1700 610 2 0 {name=l72 lab=vss}
C {devices/lab_wire.sym} 1485 350 2 0 {name=l73 lab=vss}
C {devices/ipin.sym} -1900 260 0 0 {name=p0 lab=VINN}
C {devices/ipin.sym} -1900 380 0 0 {name=p1 lab=VINP}
B 8 -1208 -78 548 78 {fill=0}
T {PMOS Simple Current Mirror (5 outputs)} -1208 -96 0 0 0.3 0.3 {layer=8}
B 10 -876 182 216 598 {fill=0}
T {NMOS Improved High Swing Cascode Current Mirror [alt: cm.nmos.low_voltage_cascode]} -876 164 0 0 0.3 0.3 {layer=10}
B 12 -1556 182 556 338 {fill=0}
T {NMOS Simple Current Mirror} -1556 164 0 0 0.3 0.3 {layer=12}
B 21 660 -78 1283 78 {fill=0}
T {PMOS Simple Current Mirror} 660 -96 0 0 0.3 0.3 {layer=21}
B 15 480 182 1953 338 {fill=0}
T {PMOS Differential Pair} 480 164 0 0 0.3 0.3 {layer=15}
