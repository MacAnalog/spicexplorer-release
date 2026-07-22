v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_001_analoggym_basic} -1740 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 105 390 1 0 {name=C0 value='c_comp'}
C {devices/isource_np.sym} -1700 520 0 0 {name=IBIAS value="dc {i_bias}"}
C {devices/res_np.sym} 275 260 1 0 {name=R1 value='r_top'}
C {devices/res_np.sym} 275 520 0 0 {name=R2 value='r_bot'}
C {devices/vsource_np.sym} -1700 260 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -1020 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} -1360 0 0 1 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 105 260 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 445 260 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 1125 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 1495 260 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} -680 520 0 1 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 105 520 0 1 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 1125 520 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} 105 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1495 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} -1020 520 0 1 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 785 260 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} -1020 0 0 1 {name=M24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_pmos_np.sym} 445 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 1125 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 1495 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 785 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 1315 260 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 1680 260 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
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
N -760 260 -760 354 {}
N -760 520 -760 614 {}
N -700 -140 -700 -30 {}
N -700 30 -700 90 {}
N -700 170 -700 230 {}
N -700 290 -700 490 {}
N -700 550 -700 660 {}
N -420 0 -420 94 {}
N -360 -140 -360 -30 {}
N -360 30 -360 70 {}
N -320 0 -320 70 {}
N -190 -60 -190 0 {}
N -150 -140 -150 -30 {}
N -150 30 -150 90 {}
N -90 0 -90 94 {}
N 25 0 25 94 {}
N 25 260 25 354 {}
N 25 520 25 614 {}
N 85 -140 85 -30 {}
N 85 30 85 90 {}
N 85 170 85 230 {}
N 85 290 85 490 {}
N 85 550 85 660 {}
N 125 200 125 260 {}
N 125 520 125 580 {}
N 215 260 215 390 {}
N 245 200 245 260 {}
N 275 460 275 490 {}
N 275 550 275 660 {}
N 305 260 305 320 {}
N 335 260 335 460 {}
N 425 190 425 260 {}
N 465 -140 465 -30 {}
N 465 30 465 90 {}
N 465 170 465 230 {}
N 465 290 465 660 {}
N 525 0 525 94 {}
N 525 260 525 354 {}
N 765 190 765 260 {}
N 805 -140 805 -30 {}
N 805 30 805 90 {}
N 805 170 805 230 {}
N 805 290 805 660 {}
N 865 0 865 94 {}
N 865 260 865 354 {}
N 1105 0 1105 70 {}
N 1145 -140 1145 -30 {}
N 1145 30 1145 70 {}
N 1145 170 1145 230 {}
N 1145 290 1145 490 {}
N 1145 550 1145 660 {}
N 1205 0 1205 94 {}
N 1205 260 1205 354 {}
N 1205 520 1205 614 {}
N 1295 200 1295 260 {}
N 1335 170 1335 230 {}
N 1335 290 1335 320 {}
N 1395 260 1395 354 {}
N 1445 0 1445 60 {}
N 1475 200 1475 260 {}
N 1515 -140 1515 -30 {}
N 1515 30 1515 90 {}
N 1515 170 1515 230 {}
N 1515 290 1515 490 {}
N 1515 550 1515 660 {}
N 1575 0 1575 94 {}
N 1575 260 1575 354 {}
N 1575 520 1575 614 {}
N 1660 200 1660 260 {}
N 1700 170 1700 230 {}
N 1700 290 1700 320 {}
N 1760 260 1760 354 {}
N -1760 -140 1890 -140 {}
N -1440 0 -1380 0 {}
N -1340 0 -1280 0 {}
N -1100 0 -1040 0 {}
N -1000 0 -940 0 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -420 0 -360 0 {}
N -220 0 -190 0 {}
N -150 0 -90 0 {}
N 25 0 85 0 {}
N 125 0 425 0 {}
N 465 0 525 0 {}
N 705 0 765 0 {}
N 805 0 865 0 {}
N 1045 0 1105 0 {}
N 1145 0 1205 0 {}
N 1415 0 1475 0 {}
N 1515 0 1575 0 {}
N -360 70 -320 70 {}
N 1105 70 1145 70 {}
N 425 190 465 190 {}
N 765 190 805 190 {}
N -700 200 -630 200 {}
N -1100 260 -1040 260 {}
N -1000 260 -940 260 {}
N -760 260 -700 260 {}
N -660 260 -600 260 {}
N 25 260 85 260 {}
N 125 260 155 260 {}
N 215 260 245 260 {}
N 305 260 335 260 {}
N 465 260 525 260 {}
N 805 260 865 260 {}
N 1045 260 1105 260 {}
N 1145 260 1205 260 {}
N 1265 260 1295 260 {}
N 1335 260 1395 260 {}
N 1445 260 1475 260 {}
N 1515 260 1575 260 {}
N 1630 260 1660 260 {}
N 1700 260 1760 260 {}
N 1145 320 1335 320 {}
N 1515 320 1700 320 {}
N 15 390 75 390 {}
N 135 390 215 390 {}
N 275 460 335 460 {}
N -1100 520 -1040 520 {}
N -1000 520 -940 520 {}
N -760 520 -700 520 {}
N -660 520 -600 520 {}
N 25 520 85 520 {}
N 125 520 1105 520 {}
N 1145 520 1205 520 {}
N 1415 520 1475 520 {}
N 1515 520 1575 520 {}
N -1760 660 1890 660 {}
C {devices/lab_wire.sym} -1760 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1760 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 85 90 2 0 {name=l2 lab=dm_1}
C {devices/lab_wire.sym} 85 170 0 1 {name=l3 lab=dm_1}
C {devices/lab_wire.sym} 1145 350 2 0 {name=l4 lab=dm_2}
C {devices/lab_wire.sym} -940 0 0 1 {name=l5 lab=ib}
C {devices/lab_wire.sym} -600 0 0 1 {name=l6 lab=ib}
C {devices/lab_wire.sym} -320 60 2 0 {name=l7 lab=ib}
C {devices/lab_wire.sym} -190 -60 0 1 {name=l8 lab=ib}
C {devices/lab_wire.sym} 185 0 0 1 {name=l9 lab=ib}
C {devices/lab_wire.sym} 705 0 0 0 {name=l10 lab=ib}
C {devices/lab_wire.sym} -1280 0 0 1 {name=l11 lab=net1}
C {devices/lab_wire.sym} -1040 90 2 0 {name=l12 lab=net1}
C {devices/lab_wire.sym} -1040 170 0 1 {name=l13 lab=net1}
C {devices/lab_wire.sym} -940 260 0 1 {name=l14 lab=net10}
C {devices/lab_wire.sym} 1515 90 2 0 {name=l15 lab=net10}
C {devices/lab_wire.sym} 1515 170 0 1 {name=l16 lab=net10}
C {devices/lab_wire.sym} 15 390 0 0 {name=l17 lab=net106}
C {devices/lab_wire.sym} 1515 350 2 0 {name=l18 lab=net106}
C {devices/lab_wire.sym} -1040 350 2 0 {name=l19 lab=net12}
C {devices/lab_wire.sym} -150 90 2 0 {name=l20 lab=net20}
C {devices/lab_wire.sym} 1335 170 0 1 {name=l21 lab=net20}
C {devices/lab_wire.sym} 1700 170 0 1 {name=l22 lab=net20}
C {devices/lab_wire.sym} -700 350 2 0 {name=l23 lab=net28}
C {devices/lab_wire.sym} 85 350 2 0 {name=l24 lab=net31}
C {devices/lab_wire.sym} -940 520 0 1 {name=l25 lab=net7}
C {devices/lab_wire.sym} 805 170 0 1 {name=l26 lab=net7}
C {devices/lab_wire.sym} 805 90 2 0 {name=l27 lab=net7}
C {devices/lab_wire.sym} -600 260 0 1 {name=l28 lab=vb3}
C {devices/lab_wire.sym} 125 200 0 1 {name=l29 lab=vb3}
C {devices/lab_wire.sym} 465 170 0 1 {name=l30 lab=vb3}
C {devices/lab_wire.sym} 465 90 2 0 {name=l31 lab=vb3}
C {devices/lab_wire.sym} 1045 260 0 0 {name=l32 lab=vb3}
C {devices/lab_wire.sym} 1475 200 0 1 {name=l33 lab=vb3}
C {devices/lab_wire.sym} -700 90 2 0 {name=l34 lab=vb4}
C {devices/lab_wire.sym} -700 170 0 1 {name=l35 lab=vb4}
C {devices/lab_wire.sym} -600 520 0 1 {name=l36 lab=vb4}
C {devices/lab_wire.sym} 125 580 2 0 {name=l37 lab=vb4}
C {devices/lab_wire.sym} 1415 520 0 0 {name=l38 lab=vb4}
C {devices/lab_wire.sym} 305 320 2 0 {name=l39 lab=vfb}
C {devices/lab_wire.sym} 1295 200 0 1 {name=l40 lab=vfb}
C {devices/lab_wire.sym} -1380 90 2 0 {name=l41 lab=vout}
C {devices/lab_wire.sym} 245 200 0 1 {name=l42 lab=vout}
C {devices/lab_wire.sym} 1045 0 0 0 {name=l43 lab=voutn}
C {devices/lab_wire.sym} 1145 170 0 1 {name=l44 lab=voutn}
C {devices/lab_wire.sym} 1415 0 0 0 {name=l45 lab=voutn}
C {devices/lab_wire.sym} 1660 200 0 1 {name=l46 lab=vref}
C {devices/lab_wire.sym} -1100 354 2 0 {name=l47 lab=net1}
C {devices/lab_wire.sym} 1395 354 2 0 {name=l48 lab=net20}
C {devices/lab_wire.sym} 1760 354 2 0 {name=l49 lab=net20}
C {devices/lab_wire.sym} -420 94 2 0 {name=l50 lab=vdd}
C {devices/lab_wire.sym} -760 94 2 0 {name=l51 lab=vdd}
C {devices/lab_wire.sym} -1440 94 2 0 {name=l52 lab=vdd}
C {devices/lab_wire.sym} 25 94 2 0 {name=l53 lab=vdd}
C {devices/lab_wire.sym} -1100 94 2 0 {name=l54 lab=vdd}
C {devices/lab_wire.sym} 525 94 2 0 {name=l55 lab=vdd}
C {devices/lab_wire.sym} -90 94 2 0 {name=l56 lab=vdd}
C {devices/lab_wire.sym} 1205 94 2 0 {name=l57 lab=vdd}
C {devices/lab_wire.sym} 1575 94 2 0 {name=l58 lab=vdd}
C {devices/lab_wire.sym} 865 94 2 0 {name=l59 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} 25 354 2 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} 525 354 2 0 {name=l62 lab=vss}
C {devices/lab_wire.sym} 1205 354 2 0 {name=l63 lab=vss}
C {devices/lab_wire.sym} 1575 354 2 0 {name=l64 lab=vss}
C {devices/lab_wire.sym} -760 614 2 0 {name=l65 lab=vss}
C {devices/lab_wire.sym} 25 614 2 0 {name=l66 lab=vss}
C {devices/lab_wire.sym} 1205 614 2 0 {name=l67 lab=vss}
C {devices/lab_wire.sym} 1575 614 2 0 {name=l68 lab=vss}
C {devices/lab_wire.sym} -1100 614 2 0 {name=l69 lab=vss}
C {devices/lab_wire.sym} 865 354 2 0 {name=l70 lab=vss}
C {devices/lab_wire.sym} -1700 430 0 1 {name=l71 lab=ib}
C {devices/lab_wire.sym} -1700 610 2 0 {name=l72 lab=vss}
C {devices/lab_wire.sym} -1700 350 2 0 {name=l73 lab=vss}
C {devices/lab_wire.sym} -1700 170 0 1 {name=l74 lab=vref}
C {devices/opin.sym} 2030 30 0 0 {name=p0 lab=vout}
B 8 -1216 -78 973 78 {fill=0}
T {PMOS Simple Current Mirror (6 outputs)} -1216 -96 0 0 0.3 0.3 {layer=8}
B 10 -876 182 641 598 {fill=0}
T {NMOS Improved High Swing Cascode Current Mirror [alt: cm.nmos.low_voltage_cascode]} -876 164 0 0 0.3 0.3 {layer=10}
B 12 -1216 182 981 598 {fill=0}
T {NMOS Simple Current Mirror} -1216 164 0 0 0.3 0.3 {layer=12}
B 21 1055 -78 1683 78 {fill=0}
T {PMOS Simple Current Mirror} 1055 -96 0 0 0.3 0.3 {layer=21}
B 15 1245 182 1868 338 {fill=0}
T {PMOS Differential Pair} 1245 164 0 0 0.3 0.3 {layer=15}
