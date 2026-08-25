v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_001_analoggym_basic} -1740 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 70 390 1 0 {name=C0 value='c_comp'}
C {devices/isource_np.sym} -1700 520 0 0 {name=IBIAS value="dc {i_bias}"}
C {devices/res_np.sym} -165 260 1 0 {name=R1 value='r_top'}
C {devices/res_np.sym} 725 520 0 0 {name=R2 value='r_bot'}
C {devices/vsource_np.sym} -1700 260 0 0 {name=VLP value="dc 0"}
C {devices/vsource_np.sym} -1700 0 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} 70 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -1020 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} -1360 0 0 1 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} 70 260 0 1 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 430 260 0 0 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 770 260 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 1110 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 1480 260 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} 70 520 0 1 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 430 520 0 0 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 1110 520 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} 430 0 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1480 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} -1020 520 0 1 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} -1020 0 0 1 {name=M24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_pmos_np.sym} 770 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 250 0 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 1110 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 1480 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 1300 260 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 1665 260 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1700 -90 -1700 -30 {}
N -1700 30 -1700 90 {}
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
N -195 200 -195 260 {}
N -135 260 -135 320 {}
N -10 0 -10 94 {}
N -10 260 -10 354 {}
N -10 520 -10 614 {}
N 10 60 10 390 {}
N 50 -140 50 -30 {}
N 50 30 50 230 {}
N 50 290 50 490 {}
N 50 550 50 660 {}
N 90 0 90 60 {}
N 170 0 170 94 {}
N 230 -140 230 -30 {}
N 230 30 230 90 {}
N 270 0 270 60 {}
N 450 -140 450 -30 {}
N 450 30 450 90 {}
N 450 170 450 230 {}
N 450 290 450 490 {}
N 450 550 450 660 {}
N 510 0 510 94 {}
N 510 260 510 354 {}
N 510 520 510 614 {}
N 725 260 725 490 {}
N 725 550 725 660 {}
N 750 190 750 260 {}
N 790 -140 790 -30 {}
N 790 30 790 90 {}
N 790 170 790 230 {}
N 790 290 790 660 {}
N 850 0 850 94 {}
N 850 260 850 354 {}
N 1090 0 1090 70 {}
N 1130 -140 1130 -30 {}
N 1130 30 1130 70 {}
N 1130 170 1130 230 {}
N 1130 290 1130 490 {}
N 1130 550 1130 660 {}
N 1190 0 1190 94 {}
N 1190 260 1190 354 {}
N 1190 520 1190 614 {}
N 1280 200 1280 260 {}
N 1320 170 1320 230 {}
N 1320 290 1320 320 {}
N 1380 260 1380 354 {}
N 1430 0 1430 60 {}
N 1460 200 1460 260 {}
N 1500 -140 1500 -30 {}
N 1500 30 1500 90 {}
N 1500 170 1500 230 {}
N 1500 290 1500 490 {}
N 1500 550 1500 660 {}
N 1560 0 1560 94 {}
N 1560 260 1560 354 {}
N 1560 520 1560 614 {}
N 1645 200 1645 260 {}
N 1685 170 1685 230 {}
N 1685 290 1685 320 {}
N 1745 260 1745 354 {}
N -1760 -140 1875 -140 {}
N -1440 0 -1380 0 {}
N -1340 0 -1280 0 {}
N -1100 0 -1040 0 {}
N -1000 0 -940 0 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -420 0 -360 0 {}
N -320 0 -260 0 {}
N -10 0 50 0 {}
N 90 0 120 0 {}
N 170 0 230 0 {}
N 270 0 410 0 {}
N 450 0 510 0 {}
N 690 0 750 0 {}
N 790 0 850 0 {}
N 1030 0 1090 0 {}
N 1130 0 1190 0 {}
N 1400 0 1460 0 {}
N 1500 0 1560 0 {}
N -700 70 -660 70 {}
N 1090 70 1130 70 {}
N -360 190 -320 190 {}
N 750 190 790 190 {}
N 50 200 120 200 {}
N -1100 260 -1040 260 {}
N -1000 260 -940 260 {}
N -420 260 -360 260 {}
N -225 260 -195 260 {}
N -135 260 -105 260 {}
N -10 260 50 260 {}
N 90 260 150 260 {}
N 350 260 410 260 {}
N 450 260 510 260 {}
N 790 260 850 260 {}
N 1030 260 1090 260 {}
N 1130 260 1190 260 {}
N 1250 260 1280 260 {}
N 1320 260 1380 260 {}
N 1430 260 1460 260 {}
N 1500 260 1560 260 {}
N 1615 260 1645 260 {}
N 1685 260 1745 260 {}
N 1130 320 1320 320 {}
N 1500 320 1685 320 {}
N -20 390 40 390 {}
N 100 390 1500 390 {}
N -1100 520 -1040 520 {}
N -1000 520 -940 520 {}
N -10 520 50 520 {}
N 90 520 410 520 {}
N 450 520 510 520 {}
N 1030 520 1090 520 {}
N 1130 520 1190 520 {}
N 1400 520 1460 520 {}
N 1500 520 1560 520 {}
N -1760 660 1875 660 {}
C {devices/lab_wire.sym} -1760 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1760 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 450 90 2 0 {name=l2 lab=dm_1}
C {devices/lab_wire.sym} 450 170 0 1 {name=l3 lab=dm_1}
C {devices/lab_wire.sym} 1130 350 2 0 {name=l4 lab=dm_2}
C {devices/lab_wire.sym} -940 0 0 1 {name=l5 lab=ib}
C {devices/lab_wire.sym} -600 0 0 1 {name=l6 lab=ib}
C {devices/lab_wire.sym} -260 0 0 1 {name=l7 lab=ib}
C {devices/lab_wire.sym} 90 60 2 0 {name=l8 lab=ib}
C {devices/lab_wire.sym} 270 60 2 0 {name=l9 lab=ib}
C {devices/lab_wire.sym} 690 0 0 0 {name=l10 lab=ib}
C {devices/lab_wire.sym} -135 320 2 0 {name=l11 lab=lp_brk}
C {devices/lab_wire.sym} -1280 0 0 1 {name=l12 lab=net1}
C {devices/lab_wire.sym} -1040 90 2 0 {name=l13 lab=net1}
C {devices/lab_wire.sym} -1040 170 0 1 {name=l14 lab=net1}
C {devices/lab_wire.sym} -940 260 0 1 {name=l15 lab=net10}
C {devices/lab_wire.sym} 1500 90 2 0 {name=l16 lab=net10}
C {devices/lab_wire.sym} 1500 170 0 1 {name=l17 lab=net10}
C {devices/lab_wire.sym} 1500 350 2 0 {name=l18 lab=net106}
C {devices/lab_wire.sym} -1040 350 2 0 {name=l19 lab=net12}
C {devices/lab_wire.sym} 230 90 2 0 {name=l20 lab=net20}
C {devices/lab_wire.sym} 1320 170 0 1 {name=l21 lab=net20}
C {devices/lab_wire.sym} 1685 170 0 1 {name=l22 lab=net20}
C {devices/lab_wire.sym} 50 350 2 0 {name=l23 lab=net28}
C {devices/lab_wire.sym} 450 350 2 0 {name=l24 lab=net31}
C {devices/lab_wire.sym} -940 520 0 1 {name=l25 lab=net7}
C {devices/lab_wire.sym} -360 90 2 0 {name=l26 lab=net7}
C {devices/lab_wire.sym} -360 170 0 1 {name=l27 lab=net7}
C {devices/lab_wire.sym} 150 260 0 1 {name=l28 lab=vb3}
C {devices/lab_wire.sym} 350 260 0 0 {name=l29 lab=vb3}
C {devices/lab_wire.sym} 790 170 0 1 {name=l30 lab=vb3}
C {devices/lab_wire.sym} 790 90 2 0 {name=l31 lab=vb3}
C {devices/lab_wire.sym} 1030 260 0 0 {name=l32 lab=vb3}
C {devices/lab_wire.sym} 1460 200 0 1 {name=l33 lab=vb3}
C {devices/lab_wire.sym} 50 90 2 0 {name=l34 lab=vb4}
C {devices/lab_wire.sym} 150 520 0 1 {name=l35 lab=vb4}
C {devices/lab_wire.sym} 1030 520 0 0 {name=l36 lab=vb4}
C {devices/lab_wire.sym} 1400 520 0 0 {name=l37 lab=vb4}
C {devices/lab_wire.sym} -195 200 0 1 {name=l38 lab=vfb}
C {devices/lab_wire.sym} 725 430 0 1 {name=l39 lab=vfb}
C {devices/lab_wire.sym} 1280 200 0 1 {name=l40 lab=vfb}
C {devices/lab_wire.sym} -1380 90 2 0 {name=l41 lab=vout}
C {devices/lab_wire.sym} -20 390 0 0 {name=l42 lab=vout}
C {devices/lab_wire.sym} 1030 0 0 0 {name=l43 lab=voutn}
C {devices/lab_wire.sym} 1130 170 0 1 {name=l44 lab=voutn}
C {devices/lab_wire.sym} 1400 0 0 0 {name=l45 lab=voutn}
C {devices/lab_wire.sym} 1645 200 0 1 {name=l46 lab=vref}
C {devices/lab_wire.sym} -1100 354 2 0 {name=l47 lab=net1}
C {devices/lab_wire.sym} 1380 354 2 0 {name=l48 lab=net20}
C {devices/lab_wire.sym} 1745 354 2 0 {name=l49 lab=net20}
C {devices/lab_wire.sym} -760 94 2 0 {name=l50 lab=vdd}
C {devices/lab_wire.sym} -10 94 2 0 {name=l51 lab=vdd}
C {devices/lab_wire.sym} -1440 94 2 0 {name=l52 lab=vdd}
C {devices/lab_wire.sym} 510 94 2 0 {name=l53 lab=vdd}
C {devices/lab_wire.sym} -1100 94 2 0 {name=l54 lab=vdd}
C {devices/lab_wire.sym} 850 94 2 0 {name=l55 lab=vdd}
C {devices/lab_wire.sym} 170 94 2 0 {name=l56 lab=vdd}
C {devices/lab_wire.sym} 1190 94 2 0 {name=l57 lab=vdd}
C {devices/lab_wire.sym} 1560 94 2 0 {name=l58 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l59 lab=vdd}
C {devices/lab_wire.sym} -10 354 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} 510 354 2 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} 850 354 2 0 {name=l62 lab=vss}
C {devices/lab_wire.sym} 1190 354 2 0 {name=l63 lab=vss}
C {devices/lab_wire.sym} 1560 354 2 0 {name=l64 lab=vss}
C {devices/lab_wire.sym} -10 614 2 0 {name=l65 lab=vss}
C {devices/lab_wire.sym} 510 614 2 0 {name=l66 lab=vss}
C {devices/lab_wire.sym} 1190 614 2 0 {name=l67 lab=vss}
C {devices/lab_wire.sym} 1560 614 2 0 {name=l68 lab=vss}
C {devices/lab_wire.sym} -1100 614 2 0 {name=l69 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l70 lab=vss}
C {devices/lab_wire.sym} -1700 350 2 0 {name=l71 lab=vout}
C {devices/lab_wire.sym} -1700 430 0 1 {name=l72 lab=ib}
C {devices/lab_wire.sym} -1700 610 2 0 {name=l73 lab=vss}
C {devices/lab_wire.sym} -1700 90 2 0 {name=l74 lab=vss}
C {devices/lab_wire.sym} -1700 170 0 1 {name=l75 lab=lp_brk}
C {devices/lab_wire.sym} -1700 -90 0 1 {name=l76 lab=vref}
C {devices/lab_wire.sym} -360 350 2 0 {name=l77 lab=vss}
C {devices/opin.sym} 2015 30 0 0 {name=p0 lab=vout}
