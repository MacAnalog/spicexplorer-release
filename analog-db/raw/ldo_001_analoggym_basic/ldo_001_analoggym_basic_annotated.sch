v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_001_analoggym_basic} -1760 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 180 390 1 0 {name=C0 value='c_comp'}
C {devices/isource_np.sym} -1720 520 0 0 {name=IBIAS value="dc \{i_bias\}"}
C {devices/res_np.sym} -195 260 1 0 {name=R1 value='r_top'}
C {devices/res_np.sym} 785 520 0 0 {name=R2 value='r_bot'}
C {devices/vsource_np.sym} -1720 260 0 0 {name=VLP value="dc 0" savecurrent=false}
C {devices/vsource_np.sym} -1720 0 0 0 {name=VREF value="dc \{vref_val\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -1020 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} -1360 0 0 1 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 180 260 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 520 260 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 1200 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 1645 260 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} -680 520 0 1 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 180 520 0 1 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 1200 520 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} 180 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1645 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} -1020 520 0 1 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 860 260 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} -1020 0 0 1 {name=M24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_pmos_np.sym} 520 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 1200 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 1645 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 860 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 1430 260 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 1870 260 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1720 -90 -1720 -30 {}
N -1720 30 -1720 90 {}
N -1720 170 -1720 230 {}
N -1720 290 -1720 350 {}
N -1720 430 -1720 490 {}
N -1720 550 -1720 610 {}
N -1500 60 -1500 390 {}
N -1440 0 -1440 94 {}
N -1380 -140 -1380 -30 {}
N -1380 30 -1380 60 {}
N -1100 0 -1100 94 {}
N -1100 260 -1100 354 {}
N -1100 520 -1100 614 {}
N -1040 -140 -1040 -30 {}
N -1040 30 -1040 90 {}
N -1040 170 -1040 230 {}
N -1040 290 -1040 490 {}
N -1040 550 -1040 660 {}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -760 520 -760 614 {}
N -700 -140 -700 -30 {}
N -700 30 -700 90 {}
N -700 170 -700 230 {}
N -700 290 -700 490 {}
N -700 550 -700 660 {}
N -690 0 -690 30 {}
N -660 140 -660 260 {}
N -630 520 -630 580 {}
N -570 200 -570 520 {}
N -420 0 -420 94 {}
N -360 -140 -360 -30 {}
N -360 30 -360 70 {}
N -320 0 -320 70 {}
N -220 -60 -220 0 {}
N -165 260 -165 320 {}
N -150 -140 -150 -30 {}
N -150 30 -150 90 {}
N -90 0 -90 94 {}
N 100 0 100 94 {}
N 100 260 100 354 {}
N 100 520 100 614 {}
N 160 -140 160 -30 {}
N 160 30 160 90 {}
N 160 170 160 230 {}
N 160 290 160 490 {}
N 160 550 160 660 {}
N 230 -60 230 0 {}
N 230 140 230 260 {}
N 230 520 230 580 {}
N 470 -60 470 0 {}
N 480 30 480 200 {}
N 500 190 500 260 {}
N 540 -140 540 -30 {}
N 540 30 540 90 {}
N 540 190 540 230 {}
N 540 290 540 660 {}
N 600 0 600 94 {}
N 600 260 600 354 {}
N 785 430 785 490 {}
N 785 550 785 660 {}
N 810 -60 810 0 {}
N 840 190 840 260 {}
N 880 -140 880 -30 {}
N 880 30 880 90 {}
N 880 170 880 230 {}
N 880 290 880 660 {}
N 940 0 940 94 {}
N 940 260 940 354 {}
N 1150 520 1150 580 {}
N 1180 0 1180 70 {}
N 1220 -140 1220 -30 {}
N 1220 30 1220 70 {}
N 1220 170 1220 230 {}
N 1220 290 1220 490 {}
N 1220 550 1220 660 {}
N 1280 0 1280 94 {}
N 1280 260 1280 354 {}
N 1280 520 1280 614 {}
N 1450 170 1450 200 {}
N 1450 200 1450 230 {}
N 1450 290 1450 320 {}
N 1510 260 1510 354 {}
N 1595 520 1595 580 {}
N 1625 -60 1625 0 {}
N 1665 -140 1665 -30 {}
N 1665 30 1665 90 {}
N 1665 170 1665 230 {}
N 1665 290 1665 490 {}
N 1665 550 1665 660 {}
N 1725 0 1725 94 {}
N 1725 260 1725 354 {}
N 1725 520 1725 614 {}
N 1890 200 1890 230 {}
N 1890 290 1890 320 {}
N 1950 260 1950 354 {}
N -1860 -140 2345 -140 {}
N -220 -60 230 -60 {}
N 470 -60 810 -60 {}
N -1440 0 -1380 0 {}
N -1340 0 -1280 0 {}
N -1100 0 -1040 0 {}
N -1000 0 -940 0 {}
N -760 0 -700 0 {}
N -690 0 -600 0 {}
N -420 0 -360 0 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 100 0 160 0 {}
N 200 0 500 0 {}
N 540 0 600 0 {}
N 810 0 840 0 {}
N 880 0 940 0 {}
N 1120 0 1180 0 {}
N 1220 0 1280 0 {}
N 1595 0 1625 0 {}
N 1665 0 1725 0 {}
N -690 30 -360 30 {}
N 480 30 540 30 {}
N -1500 60 -1380 60 {}
N -360 70 -320 70 {}
N 1180 70 1220 70 {}
N -660 140 230 140 {}
N 500 190 540 190 {}
N 840 190 880 190 {}
N -700 200 -570 200 {}
N 480 200 540 200 {}
N 1390 200 1890 200 {}
N -1100 260 -1040 260 {}
N -1000 260 -940 260 {}
N -760 260 -700 260 {}
N -285 260 -225 260 {}
N -165 260 -135 260 {}
N 100 260 160 260 {}
N 170 260 500 260 {}
N 540 260 600 260 {}
N 880 260 940 260 {}
N 1120 260 1180 260 {}
N 1220 260 1280 260 {}
N 1350 260 1410 260 {}
N 1450 260 1510 260 {}
N 1565 260 1625 260 {}
N 1665 260 1725 260 {}
N 1790 260 1850 260 {}
N 1890 260 1950 260 {}
N 1220 320 1450 320 {}
N 1665 320 1890 320 {}
N -1500 390 150 390 {}
N 210 390 1665 390 {}
N -1100 520 -1040 520 {}
N -1000 520 -940 520 {}
N -760 520 -700 520 {}
N -660 520 -570 520 {}
N 100 520 160 520 {}
N 200 520 1180 520 {}
N 1220 520 1280 520 {}
N 1595 520 1625 520 {}
N 1665 520 1725 520 {}
N -630 580 230 580 {}
N 1150 580 1595 580 {}
N -1860 660 2345 660 {}
C {devices/lab_wire.sym} 160 90 2 0 {name=l0 lab=dm_1}
C {devices/lab_wire.sym} 160 170 0 1 {name=l1 lab=dm_1}
C {devices/lab_wire.sym} 1220 350 2 0 {name=l2 lab=dm_2}
C {devices/lab_wire.sym} -940 0 0 1 {name=l3 lab=ib}
C {devices/lab_wire.sym} -600 0 0 1 {name=l4 lab=ib}
C {devices/lab_wire.sym} -250 0 0 0 {name=l5 lab=ib}
C {devices/lab_wire.sym} -165 320 2 0 {name=l6 lab=lp_brk}
C {devices/lab_wire.sym} -1280 0 0 1 {name=l7 lab=net1}
C {devices/lab_wire.sym} -1040 90 2 0 {name=l8 lab=net1}
C {devices/lab_wire.sym} -1040 170 0 1 {name=l9 lab=net1}
C {devices/lab_wire.sym} -940 260 0 1 {name=l10 lab=net10}
C {devices/lab_wire.sym} 1665 90 2 0 {name=l11 lab=net10}
C {devices/lab_wire.sym} 1665 170 0 1 {name=l12 lab=net10}
C {devices/lab_wire.sym} 1665 350 2 0 {name=l13 lab=net106}
C {devices/lab_wire.sym} -1040 350 2 0 {name=l14 lab=net12}
C {devices/lab_wire.sym} -150 90 2 0 {name=l15 lab=net20}
C {devices/lab_wire.sym} 1450 170 0 1 {name=l16 lab=net20}
C {devices/lab_wire.sym} -700 350 2 0 {name=l17 lab=net28}
C {devices/lab_wire.sym} 160 350 2 0 {name=l18 lab=net31}
C {devices/lab_wire.sym} -940 520 0 1 {name=l19 lab=net7}
C {devices/lab_wire.sym} 880 170 0 1 {name=l20 lab=net7}
C {devices/lab_wire.sym} 880 90 2 0 {name=l21 lab=net7}
C {devices/lab_wire.sym} 540 90 2 0 {name=l22 lab=vb3}
C {devices/lab_wire.sym} 1120 260 0 0 {name=l23 lab=vb3}
C {devices/lab_wire.sym} 1565 260 0 0 {name=l24 lab=vb3}
C {devices/lab_wire.sym} -700 90 2 0 {name=l25 lab=vb4}
C {devices/lab_wire.sym} -700 170 0 1 {name=l26 lab=vb4}
C {devices/lab_wire.sym} -285 260 0 0 {name=l27 lab=vfb}
C {devices/lab_wire.sym} 785 430 0 1 {name=l28 lab=vfb}
C {devices/lab_wire.sym} 1350 260 0 0 {name=l29 lab=vfb}
C {devices/lab_wire.sym} 1120 0 0 0 {name=l30 lab=voutn}
C {devices/lab_wire.sym} 1220 170 0 1 {name=l31 lab=voutn}
C {devices/lab_wire.sym} 1625 -60 0 1 {name=l32 lab=voutn}
C {devices/lab_wire.sym} 1790 260 0 0 {name=l33 lab=vref}
C {devices/lab_wire.sym} -1100 354 2 0 {name=l34 lab=net1}
C {devices/lab_wire.sym} 1510 354 2 0 {name=l35 lab=net20}
C {devices/lab_wire.sym} 1950 354 2 0 {name=l36 lab=net20}
C {devices/lab_wire.sym} -420 94 2 0 {name=l37 lab=vdd}
C {devices/lab_wire.sym} -760 94 2 0 {name=l38 lab=vdd}
C {devices/lab_wire.sym} -1440 94 2 0 {name=l39 lab=vdd}
C {devices/lab_wire.sym} 100 94 2 0 {name=l40 lab=vdd}
C {devices/lab_wire.sym} -1100 94 2 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} 600 94 2 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} -90 94 2 0 {name=l43 lab=vdd}
C {devices/lab_wire.sym} 1280 94 2 0 {name=l44 lab=vdd}
C {devices/lab_wire.sym} 1725 94 2 0 {name=l45 lab=vdd}
C {devices/lab_wire.sym} 940 94 2 0 {name=l46 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l47 lab=vss}
C {devices/lab_wire.sym} 100 354 2 0 {name=l48 lab=vss}
C {devices/lab_wire.sym} 600 354 2 0 {name=l49 lab=vss}
C {devices/lab_wire.sym} 1280 354 2 0 {name=l50 lab=vss}
C {devices/lab_wire.sym} 1725 354 2 0 {name=l51 lab=vss}
C {devices/lab_wire.sym} -760 614 2 0 {name=l52 lab=vss}
C {devices/lab_wire.sym} 100 614 2 0 {name=l53 lab=vss}
C {devices/lab_wire.sym} 1280 614 2 0 {name=l54 lab=vss}
C {devices/lab_wire.sym} 1725 614 2 0 {name=l55 lab=vss}
C {devices/lab_wire.sym} -1100 614 2 0 {name=l56 lab=vss}
C {devices/lab_wire.sym} 940 354 2 0 {name=l57 lab=vss}
C {devices/lab_wire.sym} -1720 350 2 0 {name=l58 lab=vout}
C {devices/lab_wire.sym} -1720 430 0 1 {name=l59 lab=ib}
C {devices/lab_wire.sym} -1720 610 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} -1720 90 2 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} -1720 170 0 1 {name=l62 lab=lp_brk}
C {devices/lab_wire.sym} -1720 -90 0 1 {name=l63 lab=vref}
C {devices/iopin.sym} -1860 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -1860 660 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 120 390 0 0 {name=p2 lab=vout}
B 8 -1500 -78 1316 78 {fill=0}
T {PMOS Simple Current Mirror (6 outputs)} -1500 -96 0 0 0.3 0.3 {layer=8}
B 10 -1160 182 1000 598 {fill=0}
T {NMOS Improved High Swing Cascode Current Mirror [alt: cm.nmos.low_voltage_cascode]} -1160 164 0 0 0.3 0.3 {layer=10}
B 12 -1500 182 1340 598 {fill=0}
T {NMOS Simple Current Mirror} -1500 164 0 0 0.3 0.3 {layer=12}
B 21 1130 -78 2101 78 {fill=0}
T {PMOS Simple Current Mirror} 1130 -96 0 0 0.3 0.3 {layer=21}
B 15 1360 182 2326 338 {fill=0}
T {PMOS Differential Pair} 1360 164 0 0 0.3 0.3 {layer=15}
