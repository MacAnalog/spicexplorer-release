v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_020_two_stage_miller_cmfb} -1715 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1430 260 1 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} 1630 260 1 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} 225 260 1 0 {name=C3 value='x_dut_c3_value'}
C {devices/capa_np.sym} -925 260 0 0 {name=C4 value='x_dut_c4_value'}
C {devices/isource_np.sym} -1675 520 0 0 {name=IBIAS value="dc {i_bias}"}
C {devices/res_np.sym} -1335 260 1 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} 1225 260 1 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} -455 260 0 0 {name=R3 value='x_dut_r3_value'}
C {devices/res_np.sym} 980 260 0 0 {name=R4 value='x_dut_r4_value'}
C {devices/res_np.sym} 20 260 0 0 {name=R5 value='x_dut_r5_value'}
C {devices/res_np.sym} -1130 260 0 0 {name=R6 value='x_dut_r6_value'}
C {devices/sg13_lv_nmos_np.sym} -625 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} 790 260 0 0 {name=M10 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_nmos_np.sym} -255 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -625 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -255 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 450 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_nmos_np.sym} 85 520 0 1 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} 450 260 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_nmos_np.sym} -455 520 0 1 {name=M8 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 790 0 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1675 430 -1675 490 {}
N -1675 550 -1675 610 {}
N -1305 260 -1305 320 {}
N -1130 170 -1130 230 {}
N -1130 290 -1130 350 {}
N -925 170 -925 230 {}
N -925 290 -925 350 {}
N -705 0 -705 94 {}
N -705 260 -705 354 {}
N -645 -140 -645 -30 {}
N -645 30 -645 90 {}
N -645 170 -645 230 {}
N -645 290 -645 350 {}
N -605 260 -605 320 {}
N -535 520 -535 614 {}
N -475 430 -475 490 {}
N -475 550 -475 660 {}
N -455 170 -455 230 {}
N -455 290 -455 350 {}
N -275 200 -275 260 {}
N -235 -140 -235 -30 {}
N -235 30 -235 90 {}
N -235 170 -235 230 {}
N -235 290 -235 350 {}
N -175 0 -175 94 {}
N -175 260 -175 354 {}
N 5 520 5 614 {}
N 20 170 20 230 {}
N 20 290 20 350 {}
N 65 430 65 490 {}
N 65 550 65 660 {}
N 105 450 105 520 {}
N 255 260 255 320 {}
N 430 200 430 260 {}
N 470 -140 470 -30 {}
N 470 30 470 90 {}
N 470 170 470 230 {}
N 470 290 470 660 {}
N 530 0 530 94 {}
N 530 260 530 354 {}
N 810 -140 810 -30 {}
N 810 30 810 90 {}
N 810 170 810 230 {}
N 810 290 810 660 {}
N 870 0 870 94 {}
N 870 260 870 354 {}
N 980 170 980 230 {}
N 980 290 980 350 {}
N 1195 200 1195 260 {}
N 1255 260 1255 320 {}
N 1285 0 1285 260 {}
N 1460 260 1460 320 {}
N 1570 200 1570 260 {}
N 1660 260 1660 320 {}
N -1735 -140 1860 -140 {}
N -705 0 -645 0 {}
N -605 0 -275 0 {}
N -235 0 -175 0 {}
N 370 0 430 0 {}
N 470 0 530 0 {}
N 710 0 770 0 {}
N 810 0 870 0 {}
N -1425 260 -1365 260 {}
N -1305 260 -1275 260 {}
N -705 260 -645 260 {}
N -305 260 -275 260 {}
N -235 260 -175 260 {}
N 135 260 195 260 {}
N 255 260 285 260 {}
N 470 260 530 260 {}
N 710 260 770 260 {}
N 810 260 870 260 {}
N 1165 260 1195 260 {}
N 1255 260 1285 260 {}
N 1340 260 1400 260 {}
N 1460 260 1490 260 {}
N 1540 260 1600 260 {}
N 1660 260 1690 260 {}
N 65 450 105 450 {}
N 65 460 400 460 {}
N -535 520 -475 520 {}
N -435 520 -375 520 {}
N 5 520 65 520 {}
N -1735 660 1860 660 {}
C {devices/lab_wire.sym} -1735 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1735 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -1130 350 2 0 {name=l2 lab=cmfb}
C {devices/lab_wire.sym} -545 0 0 1 {name=l3 lab=cmfb}
C {devices/lab_wire.sym} -455 170 0 1 {name=l4 lab=cmfb}
C {devices/lab_wire.sym} 20 170 0 1 {name=l5 lab=cmfb}
C {devices/lab_wire.sym} 980 350 2 0 {name=l6 lab=cmfb}
C {devices/lab_wire.sym} -1130 170 0 1 {name=l7 lab=cmz_n}
C {devices/lab_wire.sym} -925 350 2 0 {name=l8 lab=cmz_n}
C {devices/lab_wire.sym} 20 350 2 0 {name=l9 lab=cmz_p}
C {devices/lab_wire.sym} 255 320 2 0 {name=l10 lab=cmz_p}
C {devices/lab_wire.sym} 1195 200 0 1 {name=l11 lab=mill_n}
C {devices/lab_wire.sym} 1660 320 2 0 {name=l12 lab=mill_n}
C {devices/lab_wire.sym} -1425 260 0 0 {name=l13 lab=mill_p}
C {devices/lab_wire.sym} 1460 320 2 0 {name=l14 lab=mill_p}
C {devices/lab_wire.sym} -375 520 0 1 {name=l15 lab=ref}
C {devices/lab_wire.sym} 65 430 0 1 {name=l16 lab=ref}
C {devices/lab_wire.sym} 430 200 0 1 {name=l17 lab=ref}
C {devices/lab_wire.sym} 710 260 0 0 {name=l18 lab=ref}
C {devices/lab_wire.sym} -925 170 0 1 {name=l19 lab=stg1n}
C {devices/lab_wire.sym} -235 90 2 0 {name=l20 lab=stg1n}
C {devices/lab_wire.sym} -235 170 0 1 {name=l21 lab=stg1n}
C {devices/lab_wire.sym} 710 0 0 0 {name=l22 lab=stg1n}
C {devices/lab_wire.sym} 980 170 0 1 {name=l23 lab=stg1n}
C {devices/lab_wire.sym} 1255 320 2 0 {name=l24 lab=stg1n}
C {devices/lab_wire.sym} -1305 320 2 0 {name=l25 lab=stg1p}
C {devices/lab_wire.sym} -645 90 2 0 {name=l26 lab=stg1p}
C {devices/lab_wire.sym} -645 170 0 1 {name=l27 lab=stg1p}
C {devices/lab_wire.sym} -455 350 2 0 {name=l28 lab=stg1p}
C {devices/lab_wire.sym} 135 260 0 0 {name=l29 lab=stg1p}
C {devices/lab_wire.sym} 370 0 0 0 {name=l30 lab=stg1p}
C {devices/lab_wire.sym} -645 350 2 0 {name=l31 lab=tail}
C {devices/lab_wire.sym} -475 430 0 1 {name=l32 lab=tail}
C {devices/lab_wire.sym} -235 350 2 0 {name=l33 lab=tail}
C {devices/lab_wire.sym} -275 200 0 1 {name=l34 lab=vinn}
C {devices/lab_wire.sym} -605 320 2 0 {name=l35 lab=vinp}
C {devices/lab_wire.sym} 810 90 2 0 {name=l36 lab=voutn}
C {devices/lab_wire.sym} 810 170 0 1 {name=l37 lab=voutn}
C {devices/lab_wire.sym} 1540 260 0 0 {name=l38 lab=voutn}
C {devices/lab_wire.sym} 470 90 2 0 {name=l39 lab=voutp}
C {devices/lab_wire.sym} 470 170 0 1 {name=l40 lab=voutp}
C {devices/lab_wire.sym} 1340 260 0 0 {name=l41 lab=voutp}
C {devices/lab_wire.sym} -705 94 2 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} -175 94 2 0 {name=l43 lab=vdd}
C {devices/lab_wire.sym} 530 94 2 0 {name=l44 lab=vdd}
C {devices/lab_wire.sym} 870 94 2 0 {name=l45 lab=vdd}
C {devices/lab_wire.sym} -705 354 2 0 {name=l46 lab=vss}
C {devices/lab_wire.sym} 870 354 2 0 {name=l47 lab=vss}
C {devices/lab_wire.sym} -175 354 2 0 {name=l48 lab=vss}
C {devices/lab_wire.sym} 5 614 2 0 {name=l49 lab=vss}
C {devices/lab_wire.sym} 530 354 2 0 {name=l50 lab=vss}
C {devices/lab_wire.sym} -535 614 2 0 {name=l51 lab=vss}
C {devices/lab_wire.sym} -1675 430 0 1 {name=l52 lab=vdd}
C {devices/lab_wire.sym} -1675 610 2 0 {name=l53 lab=ref}
C {devices/ipin.sym} -1875 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -1875 380 0 0 {name=p1 lab=vinn}
C {devices/opin.sym} 2000 30 0 0 {name=p2 lab=voutp}
C {devices/opin.sym} 2000 150 0 0 {name=p3 lab=voutn}
B 8 -643 182 986 598 {fill=0}
T {NMOS Simple Current Mirror (3 outputs)} -643 164 0 0 0.3 0.3 {layer=8}
B 10 -813 182 -67 338 {fill=0}
T {NMOS Differential Pair} -813 164 0 0 0.3 0.3 {layer=10}
