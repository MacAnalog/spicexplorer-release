v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_030_miller_cmfb_composite} -1405 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1870 260 1 0 {name=C1_CORE value='x_dut_c1_core_value'}
C {devices/capa_np.sym} 2115 260 1 0 {name=C2_CORE value='x_dut_c2_core_value'}
C {devices/capa_np.sym} 400 260 0 0 {name=CIN_SERVO_SERVO value='cin_val_servo'}
C {devices/capa_np.sym} 195 520 0 0 {name=COUT_SERVO_SERVO value='cout_val_servo'}
C {devices/isource_np.sym} -1365 520 0 0 {name=IBIAS_CORE value="dc {i_bias_core}"}
C {devices/res_np.sym} 135 260 1 0 {name=R1_CORE value='x_dut_r1_core_value'}
C {devices/res_np.sym} 1365 260 1 0 {name=R2_CORE value='x_dut_r2_core_value'}
C {devices/res_np.sym} -765 260 0 0 {name=RIN_SERVO_SERVO value='rin_val_servo'}
C {devices/res_np.sym} -1025 260 1 0 {name=RMN_SERVO value='x_dut_rmn_servo_value'}
C {devices/res_np.sym} 1610 260 0 0 {name=RMP_SERVO value='x_dut_rmp_servo_value'}
C {devices/res_np.sym} 400 520 0 0 {name=ROUT_SERVO_SERVO value='rout_val_servo'}
C {devices/vsource_np.sym} -1365 260 0 0 {name=VBL0 value="dc {vbl0}"}
C {devices/vsource_np.sym} -1365 0 0 0 {name=VREFCM value="dc {vcm_ref}"}
C {devices/sg13_lv_nmos_np.sym} 1100 260 0 0 {name=M10_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm10_core_w l=x_dut_xm10_core_l m=x_dut_xm10_core_m}
C {devices/sg13_lv_nmos_np.sym} -435 260 0 1 {name=M1_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_core_w l=x_dut_xm1_core_l m=x_dut_xm1_core_m}
C {devices/sg13_lv_nmos_np.sym} -95 260 0 0 {name=M2_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_core_w l=x_dut_xm2_core_l m=x_dut_xm2_core_m}
C {devices/sg13_lv_pmos_np.sym} -435 0 0 1 {name=M3_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_core_w l=x_dut_xm3_core_l m=x_dut_xm3_core_m}
C {devices/sg13_lv_pmos_np.sym} -95 0 0 0 {name=M4_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_core_w l=x_dut_xm4_core_l m=x_dut_xm4_core_m}
C {devices/sg13_lv_pmos_np.sym} 760 0 0 0 {name=M5_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_core_w l=x_dut_xm5_core_l m=x_dut_xm5_core_m}
C {devices/sg13_lv_nmos_np.sym} 740 520 0 1 {name=M6_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_core_w l=x_dut_xm6_core_l m=x_dut_xm6_core_m}
C {devices/sg13_lv_nmos_np.sym} 760 260 0 0 {name=M7_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_core_w l=x_dut_xm7_core_l m=x_dut_xm7_core_m}
C {devices/sg13_lv_nmos_np.sym} -265 520 0 1 {name=M8_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm8_core_w l=x_dut_xm8_core_l m=x_dut_xm8_core_m}
C {devices/sg13_lv_pmos_np.sym} 1100 0 0 0 {name=M9_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_core_w l=x_dut_xm9_core_l m=x_dut_xm9_core_m}
N -1365 -90 -1365 -30 {}
N -1365 30 -1365 90 {}
N -1365 170 -1365 230 {}
N -1365 290 -1365 350 {}
N -1365 430 -1365 490 {}
N -1365 550 -1365 610 {}
N -995 260 -995 320 {}
N -765 170 -765 260 {}
N -765 290 -765 350 {}
N -515 0 -515 94 {}
N -515 260 -515 354 {}
N -455 -140 -455 -30 {}
N -455 30 -455 90 {}
N -455 170 -455 230 {}
N -455 290 -455 350 {}
N -345 520 -345 614 {}
N -285 430 -285 490 {}
N -285 550 -285 660 {}
N -75 -140 -75 -30 {}
N -75 30 -75 90 {}
N -75 170 -75 230 {}
N -75 290 -75 350 {}
N -15 0 -15 94 {}
N -15 260 -15 354 {}
N 105 200 105 260 {}
N 165 260 165 320 {}
N 195 430 195 490 {}
N 195 550 195 610 {}
N 400 170 400 230 {}
N 400 290 400 350 {}
N 400 430 400 490 {}
N 400 550 400 580 {}
N 720 260 720 490 {}
N 720 550 720 660 {}
N 760 450 760 520 {}
N 780 -140 780 -30 {}
N 780 30 780 90 {}
N 780 170 780 230 {}
N 780 290 780 660 {}
N 840 0 840 94 {}
N 840 260 840 354 {}
N 1050 0 1050 60 {}
N 1080 -60 1080 0 {}
N 1080 200 1080 260 {}
N 1120 -140 1120 -30 {}
N 1120 30 1120 90 {}
N 1120 170 1120 230 {}
N 1120 290 1120 660 {}
N 1180 0 1180 94 {}
N 1180 260 1180 354 {}
N 1335 200 1335 260 {}
N 1395 260 1395 320 {}
N 1425 0 1425 260 {}
N 1610 170 1610 230 {}
N 1610 290 1610 320 {}
N 1810 260 1810 320 {}
N 1900 260 1900 320 {}
N 2145 260 2145 320 {}
N -1425 -140 2385 -140 {}
N -515 0 -455 0 {}
N -415 0 -115 0 {}
N -75 0 -15 0 {}
N 680 0 740 0 {}
N 780 0 840 0 {}
N 1050 0 1080 0 {}
N 1120 0 1180 0 {}
N -1115 260 -1055 260 {}
N -995 260 -965 260 {}
N -515 260 -455 260 {}
N -415 260 -355 260 {}
N -175 260 -115 260 {}
N -75 260 -15 260 {}
N 75 260 105 260 {}
N 165 260 195 260 {}
N 680 260 740 260 {}
N 780 260 840 260 {}
N 1050 260 1080 260 {}
N 1120 260 1180 260 {}
N 1305 260 1335 260 {}
N 1395 260 1425 260 {}
N 1780 260 1840 260 {}
N 1900 260 1930 260 {}
N 2025 260 2085 260 {}
N 2145 260 2175 260 {}
N 1610 320 1810 320 {}
N 720 450 760 450 {}
N -345 520 -285 520 {}
N -245 520 710 520 {}
N 195 580 400 580 {}
N -1425 660 2385 660 {}
C {devices/lab_wire.sym} -1425 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1425 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 1335 200 0 1 {name=l2 lab=core__mill_n}
C {devices/lab_wire.sym} 2145 320 2 0 {name=l3 lab=core__mill_n}
C {devices/lab_wire.sym} 105 200 0 1 {name=l4 lab=core__mill_p}
C {devices/lab_wire.sym} 1900 320 2 0 {name=l5 lab=core__mill_p}
C {devices/lab_wire.sym} -185 520 0 1 {name=l6 lab=core__ref}
C {devices/lab_wire.sym} 720 430 0 1 {name=l7 lab=core__ref}
C {devices/lab_wire.sym} 680 260 0 0 {name=l8 lab=core__ref}
C {devices/lab_wire.sym} 1080 200 0 1 {name=l9 lab=core__ref}
C {devices/lab_wire.sym} -75 90 2 0 {name=l10 lab=core__stg1n}
C {devices/lab_wire.sym} -75 170 0 1 {name=l11 lab=core__stg1n}
C {devices/lab_wire.sym} 1080 -60 0 1 {name=l12 lab=core__stg1n}
C {devices/lab_wire.sym} 1395 320 2 0 {name=l13 lab=core__stg1n}
C {devices/lab_wire.sym} -455 90 2 0 {name=l14 lab=core__stg1p}
C {devices/lab_wire.sym} -455 170 0 1 {name=l15 lab=core__stg1p}
C {devices/lab_wire.sym} 165 320 2 0 {name=l16 lab=core__stg1p}
C {devices/lab_wire.sym} 680 0 0 0 {name=l17 lab=core__stg1p}
C {devices/lab_wire.sym} -455 350 2 0 {name=l18 lab=core__tail}
C {devices/lab_wire.sym} -285 430 0 1 {name=l19 lab=core__tail}
C {devices/lab_wire.sym} -75 350 2 0 {name=l20 lab=core__tail}
C {devices/lab_wire.sym} -1115 260 0 0 {name=l21 lab=servo__cm_sense}
C {devices/lab_wire.sym} -765 170 0 1 {name=l22 lab=servo__cm_sense}
C {devices/lab_wire.sym} 400 170 0 1 {name=l23 lab=servo__cm_sense}
C {devices/lab_wire.sym} 1610 170 0 1 {name=l24 lab=servo__cm_sense}
C {devices/lab_wire.sym} -355 0 0 1 {name=l25 lab=vbl_ctl}
C {devices/lab_wire.sym} 195 610 2 0 {name=l26 lab=vcmfb_raw}
C {devices/lab_wire.sym} -175 260 0 0 {name=l27 lab=vinn}
C {devices/lab_wire.sym} -355 260 0 1 {name=l28 lab=vinp}
C {devices/lab_wire.sym} -995 320 2 0 {name=l29 lab=voutn}
C {devices/lab_wire.sym} 1120 90 2 0 {name=l30 lab=voutn}
C {devices/lab_wire.sym} 1120 170 0 1 {name=l31 lab=voutn}
C {devices/lab_wire.sym} 2025 260 0 0 {name=l32 lab=voutn}
C {devices/lab_wire.sym} 780 90 2 0 {name=l33 lab=voutp}
C {devices/lab_wire.sym} 780 170 0 1 {name=l34 lab=voutp}
C {devices/lab_wire.sym} 1780 260 0 0 {name=l35 lab=voutp}
C {devices/lab_wire.sym} -765 350 2 0 {name=l36 lab=vref_cm}
C {devices/lab_wire.sym} 400 350 2 0 {name=l37 lab=vref_cm}
C {devices/lab_wire.sym} -515 94 2 0 {name=l38 lab=vdd}
C {devices/lab_wire.sym} -15 94 2 0 {name=l39 lab=vdd}
C {devices/lab_wire.sym} 840 94 2 0 {name=l40 lab=vdd}
C {devices/lab_wire.sym} 1180 94 2 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} 1180 354 2 0 {name=l42 lab=vss}
C {devices/lab_wire.sym} -515 354 2 0 {name=l43 lab=vss}
C {devices/lab_wire.sym} -15 354 2 0 {name=l44 lab=vss}
C {devices/lab_wire.sym} 720 520 0 0 {name=l45 lab=vss}
C {devices/lab_wire.sym} 840 354 2 0 {name=l46 lab=vss}
C {devices/lab_wire.sym} -345 614 2 0 {name=l47 lab=vss}
C {devices/lab_wire.sym} -1365 -90 0 1 {name=l48 lab=vref_cm}
C {devices/lab_wire.sym} -1365 90 2 0 {name=l49 lab=vss}
C {devices/lab_wire.sym} -1365 350 2 0 {name=l50 lab=vcmfb_raw}
C {devices/lab_wire.sym} -1365 430 0 1 {name=l51 lab=vdd}
C {devices/lab_wire.sym} -1365 610 2 0 {name=l52 lab=core__ref}
C {devices/lab_wire.sym} -1365 170 0 1 {name=l53 lab=vbl_ctl}
C {devices/lab_wire.sym} 195 430 0 1 {name=l54 lab=vss}
C {devices/lab_wire.sym} 400 430 0 1 {name=l55 lab=vss}
C {devices/ipin.sym} -1565 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -1565 380 0 0 {name=p1 lab=vinn}
C {devices/opin.sym} 2525 30 0 0 {name=p2 lab=voutp}
C {devices/opin.sym} 2525 150 0 0 {name=p3 lab=voutn}
B 8 -493 182 1336 598 {fill=0}
T {NMOS Simple Current Mirror (3 outputs)} -493 164 0 0 0.3 0.3 {layer=8}
B 10 -663 182 133 338 {fill=0}
T {NMOS Differential Pair} -663 164 0 0 0.3 0.3 {layer=10}
