v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_029_two_stage_miller_comp} -1060 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 955 260 1 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} 1160 260 1 0 {name=C2 value='x_dut_c2_value'}
C {devices/isource_np.sym} -1020 520 0 0 {name=IBIAS value="dc {i_bias}"}
C {devices/res_np.sym} -110 260 1 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} 145 260 1 0 {name=R2 value='x_dut_r2_value'}
C {devices/vsource_np.sym} -1020 260 0 0 {name=VBL value="dc {vbl}"}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} 690 260 0 0 {name=M10 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 350 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_nmos_np.sym} 0 520 0 1 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} 350 260 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_nmos_np.sym} -510 520 0 1 {name=M8 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 690 0 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1020 170 -1020 230 {}
N -1020 290 -1020 350 {}
N -1020 430 -1020 490 {}
N -1020 550 -1020 610 {}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -700 -140 -700 -30 {}
N -700 30 -700 230 {}
N -700 290 -700 350 {}
N -590 520 -590 614 {}
N -530 320 -530 490 {}
N -530 550 -530 660 {}
N -320 -140 -320 -30 {}
N -320 30 -320 90 {}
N -320 170 -320 230 {}
N -320 290 -320 320 {}
N -260 0 -260 94 {}
N -260 260 -260 354 {}
N -140 200 -140 260 {}
N -80 260 -80 320 {}
N -80 520 -80 614 {}
N -20 430 -20 490 {}
N -20 550 -20 660 {}
N 20 450 20 520 {}
N 115 200 115 260 {}
N 175 260 175 320 {}
N 205 200 205 260 {}
N 330 200 330 260 {}
N 370 -140 370 -30 {}
N 370 30 370 230 {}
N 370 290 370 660 {}
N 430 0 430 94 {}
N 430 260 430 354 {}
N 710 -140 710 -30 {}
N 710 30 710 90 {}
N 710 170 710 230 {}
N 710 290 710 660 {}
N 770 0 770 94 {}
N 770 260 770 354 {}
N 925 200 925 260 {}
N 985 260 985 320 {}
N 1100 200 1100 260 {}
N 1190 260 1190 320 {}
N -1080 -140 1390 -140 {}
N -760 0 -700 0 {}
N -660 0 -360 0 {}
N -320 0 -260 0 {}
N 270 0 330 0 {}
N 370 0 430 0 {}
N 610 0 670 0 {}
N 710 0 770 0 {}
N -760 260 -700 260 {}
N -660 260 -600 260 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N -170 260 -140 260 {}
N -80 260 -50 260 {}
N 85 260 115 260 {}
N 175 260 205 260 {}
N 370 260 430 260 {}
N 610 260 670 260 {}
N 710 260 770 260 {}
N 895 260 925 260 {}
N 985 260 1015 260 {}
N 1070 260 1130 260 {}
N 1190 260 1220 260 {}
N -700 320 -320 320 {}
N -20 450 20 450 {}
N -20 460 300 460 {}
N -590 520 -530 520 {}
N -490 520 -430 520 {}
N -80 520 -20 520 {}
N -1080 660 1390 660 {}
C {devices/lab_wire.sym} -1080 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1080 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 115 200 0 1 {name=l2 lab=mill_n}
C {devices/lab_wire.sym} 1190 320 2 0 {name=l3 lab=mill_n}
C {devices/lab_wire.sym} -140 200 0 1 {name=l4 lab=mill_p}
C {devices/lab_wire.sym} 985 320 2 0 {name=l5 lab=mill_p}
C {devices/lab_wire.sym} -430 520 0 1 {name=l6 lab=ref}
C {devices/lab_wire.sym} -20 430 0 1 {name=l7 lab=ref}
C {devices/lab_wire.sym} 330 200 0 1 {name=l8 lab=ref}
C {devices/lab_wire.sym} 610 260 0 0 {name=l9 lab=ref}
C {devices/lab_wire.sym} -320 90 2 0 {name=l10 lab=stg1n}
C {devices/lab_wire.sym} -320 170 0 1 {name=l11 lab=stg1n}
C {devices/lab_wire.sym} 175 320 2 0 {name=l12 lab=stg1n}
C {devices/lab_wire.sym} 610 0 0 0 {name=l13 lab=stg1n}
C {devices/lab_wire.sym} -700 90 2 0 {name=l14 lab=stg1p}
C {devices/lab_wire.sym} -80 320 2 0 {name=l15 lab=stg1p}
C {devices/lab_wire.sym} 270 0 0 0 {name=l16 lab=stg1p}
C {devices/lab_wire.sym} -700 350 2 0 {name=l17 lab=tail}
C {devices/lab_wire.sym} -600 0 0 1 {name=l18 lab=vbl}
C {devices/lab_wire.sym} -420 260 0 0 {name=l19 lab=vinn}
C {devices/lab_wire.sym} -600 260 0 1 {name=l20 lab=vinp}
C {devices/lab_wire.sym} 710 90 2 0 {name=l21 lab=voutn}
C {devices/lab_wire.sym} 710 170 0 1 {name=l22 lab=voutn}
C {devices/lab_wire.sym} 1070 260 0 0 {name=l23 lab=voutn}
C {devices/lab_wire.sym} 370 90 2 0 {name=l24 lab=voutp}
C {devices/lab_wire.sym} 925 200 0 1 {name=l25 lab=voutp}
C {devices/lab_wire.sym} -760 94 2 0 {name=l26 lab=vdd}
C {devices/lab_wire.sym} -260 94 2 0 {name=l27 lab=vdd}
C {devices/lab_wire.sym} 430 94 2 0 {name=l28 lab=vdd}
C {devices/lab_wire.sym} 770 94 2 0 {name=l29 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l30 lab=vss}
C {devices/lab_wire.sym} 770 354 2 0 {name=l31 lab=vss}
C {devices/lab_wire.sym} -260 354 2 0 {name=l32 lab=vss}
C {devices/lab_wire.sym} -80 614 2 0 {name=l33 lab=vss}
C {devices/lab_wire.sym} 430 354 2 0 {name=l34 lab=vss}
C {devices/lab_wire.sym} -590 614 2 0 {name=l35 lab=vss}
C {devices/lab_wire.sym} -1020 430 0 1 {name=l36 lab=vdd}
C {devices/lab_wire.sym} -1020 610 2 0 {name=l37 lab=ref}
C {devices/lab_wire.sym} -1020 170 0 1 {name=l38 lab=vbl}
C {devices/lab_wire.sym} -1020 350 2 0 {name=l39 lab=vss}
C {devices/ipin.sym} -1220 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -1220 380 0 0 {name=p1 lab=vinn}
C {devices/opin.sym} 1530 30 0 0 {name=p2 lab=voutp}
C {devices/opin.sym} 1530 150 0 0 {name=p3 lab=voutn}
