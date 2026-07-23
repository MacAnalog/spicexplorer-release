v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_001_analoggym_basic} -1740 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 0 390 1 0 {name=C0 value='c_comp'}
C {devices/isource_np.sym} -1700 520 0 0 {name=IBIAS value="dc {i_bias}"}
C {devices/res_np.sym} 190 260 1 0 {name=R1 value='r_top'}
C {devices/res_np.sym} 190 520 0 0 {name=R2 value='r_bot'}
C {devices/vsource_np.sym} -1700 260 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -1020 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} -1360 0 0 1 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 1 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 360 260 0 0 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 700 260 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 1040 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 1410 260 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} 0 520 0 1 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 360 520 0 0 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 1040 520 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} 360 0 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1410 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} -1020 520 0 1 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} -1020 0 0 1 {name=M24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_pmos_np.sym} 700 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 180 0 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 1040 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 1410 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 1230 260 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 1595 260 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1700 170 -1700 230 {}
N -1700 290 -1700 350 {}
N -1700 430 -1700 490 {}
N -1700 550 -1700 610 {}
N -1440 0 -1440 94 {}
N -1380 -140 -1380 -30 {}
N -1380 30 -1380 90 {}
N -1100 0 -1100 94 {}
N -1100 260 -1100 354 {}
N -1100 520 -1100 614 {}
N -1040 -140 -1040 -30 {}
N -1040 30 -1040 90 {}
N -1040 170 -1040 230 {}
N -1040 290 -1040 490 {}
N -1040 550 -1040 660 {}
N -760 0 -760 94 {}
N -700 -140 -700 -30 {}
N -700 30 -700 70 {}
N -660 0 -660 70 {}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 30 -360 90 {}
N -360 170 -360 230 {}
N -360 290 -360 350 {}
N -320 190 -320 260 {}
N -80 0 -80 94 {}
N -80 260 -80 354 {}
N -80 520 -80 614 {}
N -60 60 -60 390 {}
N -20 -140 -20 -30 {}
N -20 30 -20 230 {}
N -20 290 -20 490 {}
N -20 550 -20 660 {}
N 20 0 20 60 {}
N 20 520 20 580 {}
N 30 390 30 450 {}
N 100 0 100 94 {}
N 160 -140 160 -30 {}
N 160 30 160 90 {}
N 160 200 160 260 {}
N 190 260 190 490 {}
N 190 550 190 660 {}
N 200 0 200 60 {}
N 220 260 220 320 {}
N 340 200 340 260 {}
N 380 -140 380 -30 {}
N 380 30 380 90 {}
N 380 170 380 230 {}
N 380 290 380 490 {}
N 380 550 380 660 {}
N 440 0 440 94 {}
N 440 260 440 354 {}
N 440 520 440 614 {}
N 680 190 680 260 {}
N 720 -140 720 -30 {}
N 720 30 720 90 {}
N 720 170 720 230 {}
N 720 290 720 660 {}
N 780 0 780 94 {}
N 780 260 780 354 {}
N 1020 0 1020 70 {}
N 1060 -140 1060 -30 {}
N 1060 30 1060 70 {}
N 1060 170 1060 230 {}
N 1060 290 1060 490 {}
N 1060 550 1060 660 {}
N 1120 0 1120 94 {}
N 1120 260 1120 354 {}
N 1120 520 1120 614 {}
N 1210 200 1210 260 {}
N 1250 170 1250 230 {}
N 1250 290 1250 320 {}
N 1310 260 1310 354 {}
N 1360 0 1360 60 {}
N 1390 200 1390 260 {}
N 1430 -140 1430 -30 {}
N 1430 30 1430 90 {}
N 1430 170 1430 230 {}
N 1430 290 1430 490 {}
N 1430 550 1430 660 {}
N 1490 0 1490 94 {}
N 1490 260 1490 354 {}
N 1490 520 1490 614 {}
N 1575 200 1575 260 {}
N 1615 170 1615 230 {}
N 1615 290 1615 320 {}
N 1675 260 1675 354 {}
N -1760 -140 1805 -140 {}
N -1440 0 -1380 0 {}
N -1340 0 -1280 0 {}
N -1100 0 -1040 0 {}
N -1000 0 -940 0 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -420 0 -360 0 {}
N -320 0 -260 0 {}
N -80 0 -20 0 {}
N 20 0 50 0 {}
N 100 0 160 0 {}
N 200 0 340 0 {}
N 380 0 440 0 {}
N 620 0 680 0 {}
N 720 0 780 0 {}
N 960 0 1020 0 {}
N 1060 0 1120 0 {}
N 1330 0 1390 0 {}
N 1430 0 1490 0 {}
N -700 70 -660 70 {}
N 1020 70 1060 70 {}
N -360 190 -320 190 {}
N 680 190 720 190 {}
N -20 200 50 200 {}
N -1100 260 -1040 260 {}
N -1000 260 -940 260 {}
N -420 260 -360 260 {}
N -80 260 -20 260 {}
N 130 260 190 260 {}
N 220 260 250 260 {}
N 310 260 340 260 {}
N 380 260 440 260 {}
N 720 260 780 260 {}
N 960 260 1020 260 {}
N 1060 260 1120 260 {}
N 1180 260 1210 260 {}
N 1250 260 1310 260 {}
N 1360 260 1390 260 {}
N 1430 260 1490 260 {}
N 1545 260 1575 260 {}
N 1615 260 1675 260 {}
N 1060 320 1250 320 {}
N 1430 320 1615 320 {}
N -90 390 -30 390 {}
N 30 390 60 390 {}
N -1100 520 -1040 520 {}
N -1000 520 -940 520 {}
N -80 520 -20 520 {}
N 20 520 340 520 {}
N 380 520 440 520 {}
N 960 520 1020 520 {}
N 1060 520 1120 520 {}
N 1330 520 1390 520 {}
N 1430 520 1490 520 {}
N -1760 660 1805 660 {}
C {devices/lab_wire.sym} -1760 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1760 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 380 90 2 0 {name=l2 lab=dm_1}
C {devices/lab_wire.sym} 380 170 0 1 {name=l3 lab=dm_1}
C {devices/lab_wire.sym} 1060 350 2 0 {name=l4 lab=dm_2}
C {devices/lab_wire.sym} -940 0 0 1 {name=l5 lab=ib}
C {devices/lab_wire.sym} -600 0 0 1 {name=l6 lab=ib}
C {devices/lab_wire.sym} -260 0 0 1 {name=l7 lab=ib}
C {devices/lab_wire.sym} 20 60 2 0 {name=l8 lab=ib}
C {devices/lab_wire.sym} 200 60 2 0 {name=l9 lab=ib}
C {devices/lab_wire.sym} 620 0 0 0 {name=l10 lab=ib}
C {devices/lab_wire.sym} -1280 0 0 1 {name=l11 lab=net1}
C {devices/lab_wire.sym} -1040 90 2 0 {name=l12 lab=net1}
C {devices/lab_wire.sym} -1040 170 0 1 {name=l13 lab=net1}
C {devices/lab_wire.sym} -940 260 0 1 {name=l14 lab=net10}
C {devices/lab_wire.sym} 1430 90 2 0 {name=l15 lab=net10}
C {devices/lab_wire.sym} 1430 170 0 1 {name=l16 lab=net10}
C {devices/lab_wire.sym} 30 450 2 0 {name=l17 lab=net106}
C {devices/lab_wire.sym} 1430 350 2 0 {name=l18 lab=net106}
C {devices/lab_wire.sym} -1040 350 2 0 {name=l19 lab=net12}
C {devices/lab_wire.sym} 160 90 2 0 {name=l20 lab=net20}
C {devices/lab_wire.sym} 1250 170 0 1 {name=l21 lab=net20}
C {devices/lab_wire.sym} 1615 170 0 1 {name=l22 lab=net20}
C {devices/lab_wire.sym} -20 350 2 0 {name=l23 lab=net28}
C {devices/lab_wire.sym} 380 350 2 0 {name=l24 lab=net31}
C {devices/lab_wire.sym} -940 520 0 1 {name=l25 lab=net7}
C {devices/lab_wire.sym} -360 90 2 0 {name=l26 lab=net7}
C {devices/lab_wire.sym} -360 170 0 1 {name=l27 lab=net7}
C {devices/lab_wire.sym} 20 260 0 0 {name=l28 lab=vb3}
C {devices/lab_wire.sym} 340 200 0 1 {name=l29 lab=vb3}
C {devices/lab_wire.sym} 720 170 0 1 {name=l30 lab=vb3}
C {devices/lab_wire.sym} 720 90 2 0 {name=l31 lab=vb3}
C {devices/lab_wire.sym} 960 260 0 0 {name=l32 lab=vb3}
C {devices/lab_wire.sym} 1390 200 0 1 {name=l33 lab=vb3}
C {devices/lab_wire.sym} -20 90 2 0 {name=l34 lab=vb4}
C {devices/lab_wire.sym} 20 580 2 0 {name=l35 lab=vb4}
C {devices/lab_wire.sym} 960 520 0 0 {name=l36 lab=vb4}
C {devices/lab_wire.sym} 1330 520 0 0 {name=l37 lab=vb4}
C {devices/lab_wire.sym} 160 200 0 1 {name=l38 lab=vfb}
C {devices/lab_wire.sym} 1210 200 0 1 {name=l39 lab=vfb}
C {devices/lab_wire.sym} -1380 90 2 0 {name=l40 lab=vout}
C {devices/lab_wire.sym} -90 390 0 0 {name=l41 lab=vout}
C {devices/lab_wire.sym} 220 320 2 0 {name=l42 lab=vout}
C {devices/lab_wire.sym} 960 0 0 0 {name=l43 lab=voutn}
C {devices/lab_wire.sym} 1060 170 0 1 {name=l44 lab=voutn}
C {devices/lab_wire.sym} 1330 0 0 0 {name=l45 lab=voutn}
C {devices/lab_wire.sym} 1575 200 0 1 {name=l46 lab=vref}
C {devices/lab_wire.sym} -1100 354 2 0 {name=l47 lab=net1}
C {devices/lab_wire.sym} 1310 354 2 0 {name=l48 lab=net20}
C {devices/lab_wire.sym} 1675 354 2 0 {name=l49 lab=net20}
C {devices/lab_wire.sym} -760 94 2 0 {name=l50 lab=vdd}
C {devices/lab_wire.sym} -80 94 2 0 {name=l51 lab=vdd}
C {devices/lab_wire.sym} -1440 94 2 0 {name=l52 lab=vdd}
C {devices/lab_wire.sym} 440 94 2 0 {name=l53 lab=vdd}
C {devices/lab_wire.sym} -1100 94 2 0 {name=l54 lab=vdd}
C {devices/lab_wire.sym} 780 94 2 0 {name=l55 lab=vdd}
C {devices/lab_wire.sym} 100 94 2 0 {name=l56 lab=vdd}
C {devices/lab_wire.sym} 1120 94 2 0 {name=l57 lab=vdd}
C {devices/lab_wire.sym} 1490 94 2 0 {name=l58 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l59 lab=vdd}
C {devices/lab_wire.sym} -80 354 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} 440 354 2 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} 780 354 2 0 {name=l62 lab=vss}
C {devices/lab_wire.sym} 1120 354 2 0 {name=l63 lab=vss}
C {devices/lab_wire.sym} 1490 354 2 0 {name=l64 lab=vss}
C {devices/lab_wire.sym} -80 614 2 0 {name=l65 lab=vss}
C {devices/lab_wire.sym} 440 614 2 0 {name=l66 lab=vss}
C {devices/lab_wire.sym} 1120 614 2 0 {name=l67 lab=vss}
C {devices/lab_wire.sym} 1490 614 2 0 {name=l68 lab=vss}
C {devices/lab_wire.sym} -1100 614 2 0 {name=l69 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l70 lab=vss}
C {devices/lab_wire.sym} -1700 430 0 1 {name=l71 lab=ib}
C {devices/lab_wire.sym} -1700 610 2 0 {name=l72 lab=vss}
C {devices/lab_wire.sym} -1700 350 2 0 {name=l73 lab=vss}
C {devices/lab_wire.sym} -1700 170 0 1 {name=l74 lab=vref}
C {devices/lab_wire.sym} -360 350 2 0 {name=l75 lab=vss}
C {devices/opin.sym} 1945 30 0 0 {name=p0 lab=vout}
