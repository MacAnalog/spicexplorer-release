v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_030_miller_cmfb_composite} -1230 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 2000 260 1 0 {name=C1_CORE value='x_dut_c1_core_value'}
C {devices/capa_np.sym} 2580 260 1 0 {name=C2_CORE value='x_dut_c2_core_value'}
C {devices/capa_np.sym} 460 260 0 0 {name=CIN_SERVO_SERVO value='cin_val_servo'}
C {devices/capa_np.sym} 215 520 0 0 {name=COUT_SERVO_SERVO value='cout_val_servo'}
C {devices/vccs.sym} 215 390 0 0 {name=GM_SERVO_SERVO value="\{gm_val_servo\}"}
C {devices/isource_np.sym} -1190 520 0 0 {name=IBIAS_CORE value="dc \{i_bias_core\}"}
C {devices/res_np.sym} 155 260 1 0 {name=R1_CORE value='x_dut_r1_core_value'}
C {devices/res_np.sym} 1715 260 1 0 {name=R2_CORE value='x_dut_r2_core_value'}
C {devices/res_np.sym} -850 260 0 0 {name=RIN_SERVO_SERVO value='rin_val_servo'}
C {devices/res_np.sym} 2280 260 1 0 {name=RMN_SERVO value='x_dut_rmn_servo_value'}
C {devices/res_np.sym} 1150 260 0 0 {name=RMP_SERVO value='x_dut_rmp_servo_value'}
C {devices/res_np.sym} 460 520 0 0 {name=ROUT_SERVO_SERVO value='rout_val_servo'}
C {devices/vsource_np.sym} -1190 260 0 0 {name=VBL0 value="dc \{vbl0\}" savecurrent=false}
C {devices/vsource_np.sym} -1190 0 0 0 {name=VREFCM value="dc \{vcm_ref\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} 1450 260 0 0 {name=M10_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm10_core_w l=x_dut_xm10_core_l m=x_dut_xm10_core_m}
C {devices/sg13_lv_nmos_np.sym} -440 260 0 1 {name=M1_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_core_w l=x_dut_xm1_core_l m=x_dut_xm1_core_m}
C {devices/sg13_lv_nmos_np.sym} -100 260 0 0 {name=M2_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_core_w l=x_dut_xm2_core_l m=x_dut_xm2_core_m}
C {devices/sg13_lv_pmos_np.sym} -440 0 0 1 {name=M3_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_core_w l=x_dut_xm3_core_l m=x_dut_xm3_core_m}
C {devices/sg13_lv_pmos_np.sym} -100 0 0 0 {name=M4_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_core_w l=x_dut_xm4_core_l m=x_dut_xm4_core_m}
C {devices/sg13_lv_pmos_np.sym} 895 0 0 0 {name=M5_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_core_w l=x_dut_xm5_core_l m=x_dut_xm5_core_m}
C {devices/sg13_lv_nmos_np.sym} 875 520 0 1 {name=M6_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_core_w l=x_dut_xm6_core_l m=x_dut_xm6_core_m}
C {devices/sg13_lv_nmos_np.sym} 895 260 0 0 {name=M7_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_core_w l=x_dut_xm7_core_l m=x_dut_xm7_core_m}
C {devices/sg13_lv_nmos_np.sym} -270 520 0 1 {name=M8_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm8_core_w l=x_dut_xm8_core_l m=x_dut_xm8_core_m}
C {devices/sg13_lv_pmos_np.sym} 1450 0 0 0 {name=M9_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_core_w l=x_dut_xm9_core_l m=x_dut_xm9_core_m}
N -1190 -90 -1190 -30 {}
N -1190 30 -1190 90 {}
N -1190 170 -1190 230 {}
N -1190 290 -1190 350 {}
N -1190 430 -1190 490 {}
N -1190 550 -1190 610 {}
N -910 320 -910 370 {}
N -850 170 -850 230 {}
N -850 290 -850 350 {}
N -520 60 -520 230 {}
N -520 290 -520 460 {}
N -460 -140 -460 -30 {}
N -460 30 -460 90 {}
N -460 290 -460 350 {}
N -350 290 -350 460 {}
N -350 520 -350 614 {}
N -290 460 -290 490 {}
N -290 550 -290 660 {}
N -220 460 -220 520 {}
N -140 60 -140 230 {}
N -80 -140 -80 -30 {}
N -80 30 -80 90 {}
N -20 0 -20 94 {}
N -20 260 -20 354 {}
N 115 320 115 370 {}
N 155 450 155 580 {}
N 215 420 215 450 {}
N 215 550 215 580 {}
N 460 170 460 200 {}
N 460 200 460 230 {}
N 460 290 460 320 {}
N 460 430 460 490 {}
N 460 550 460 580 {}
N 520 200 520 410 {}
N 795 260 795 460 {}
N 795 520 795 614 {}
N 855 30 855 320 {}
N 855 450 855 460 {}
N 855 460 855 490 {}
N 855 550 855 660 {}
N 895 450 895 520 {}
N 915 -140 915 -30 {}
N 915 290 915 660 {}
N 975 0 975 94 {}
N 975 260 975 354 {}
N 1150 200 1150 230 {}
N 1150 290 1150 320 {}
N 1470 -140 1470 -30 {}
N 1470 30 1470 230 {}
N 1470 290 1470 660 {}
N 1530 0 1530 94 {}
N 1530 260 1530 354 {}
N 1940 260 1940 320 {}
N 2030 260 2030 320 {}
N 2220 260 2220 410 {}
N 2340 200 2340 260 {}
N 2610 260 2610 320 {}
N -1250 -140 2930 -140 {}
N -420 0 -120 0 {}
N -80 0 -20 0 {}
N 815 0 875 0 {}
N 915 0 975 0 {}
N 1370 0 1430 0 {}
N 1470 0 1530 0 {}
N 855 30 915 30 {}
N -520 60 -460 60 {}
N -140 60 -80 60 {}
N 400 200 1150 200 {}
N 1470 200 2340 200 {}
N -520 230 -460 230 {}
N -140 230 -80 230 {}
N 855 230 915 230 {}
N -420 260 -390 260 {}
N -210 260 -120 260 {}
N -80 260 -20 260 {}
N 65 260 125 260 {}
N 185 260 215 260 {}
N 795 260 875 260 {}
N 915 260 975 260 {}
N 1370 260 1430 260 {}
N 1470 260 1530 260 {}
N 1625 260 1685 260 {}
N 1745 260 1775 260 {}
N 1940 260 1970 260 {}
N 2030 260 2060 260 {}
N 2220 260 2250 260 {}
N 2310 260 2550 260 {}
N 2610 260 2640 260 {}
N -520 290 -460 290 {}
N -350 290 -80 290 {}
N -910 320 -850 320 {}
N 115 320 460 320 {}
N 855 320 1940 320 {}
N 155 360 215 360 {}
N -910 370 175 370 {}
N 145 410 2220 410 {}
N 155 420 215 420 {}
N 155 450 215 450 {}
N 855 450 895 450 {}
N -520 460 -290 460 {}
N -220 460 895 460 {}
N -350 520 -290 520 {}
N -250 520 -220 520 {}
N 795 520 855 520 {}
N 155 580 460 580 {}
N -1250 660 2930 660 {}
C {devices/lab_wire.sym} 1625 260 0 0 {name=l0 lab=core__mill_n}
C {devices/lab_wire.sym} 2610 320 2 0 {name=l1 lab=core__mill_n}
C {devices/lab_wire.sym} 65 260 0 0 {name=l2 lab=core__mill_p}
C {devices/lab_wire.sym} 2030 320 2 0 {name=l3 lab=core__mill_p}
C {devices/lab_wire.sym} 815 260 0 0 {name=l4 lab=core__ref}
C {devices/lab_wire.sym} 1370 260 0 0 {name=l5 lab=core__ref}
C {devices/lab_wire.sym} -80 90 2 0 {name=l6 lab=core__stg1n}
C {devices/lab_wire.sym} 1370 0 0 0 {name=l7 lab=core__stg1n}
C {devices/lab_wire.sym} 1745 260 0 0 {name=l8 lab=core__stg1n}
C {devices/lab_wire.sym} -460 90 2 0 {name=l9 lab=core__stg1p}
C {devices/lab_wire.sym} 185 260 0 0 {name=l10 lab=core__stg1p}
C {devices/lab_wire.sym} 815 0 0 0 {name=l11 lab=core__stg1p}
C {devices/lab_wire.sym} -460 350 2 0 {name=l12 lab=core__tail}
C {devices/lab_wire.sym} -850 170 0 1 {name=l13 lab=servo__cm_sense}
C {devices/lab_wire.sym} 460 170 0 1 {name=l14 lab=servo__cm_sense}
C {devices/lab_wire.sym} -360 0 0 1 {name=l15 lab=vbl_ctl}
C {devices/lab_wire.sym} 155 420 0 0 {name=l16 lab=vcmfb_raw}
C {devices/lab_wire.sym} -850 350 2 0 {name=l17 lab=vref_cm}
C {devices/lab_wire.sym} -460 0 0 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} -20 94 2 0 {name=l19 lab=vdd}
C {devices/lab_wire.sym} 975 94 2 0 {name=l20 lab=vdd}
C {devices/lab_wire.sym} 1530 94 2 0 {name=l21 lab=vdd}
C {devices/lab_wire.sym} 1530 354 2 0 {name=l22 lab=vss}
C {devices/lab_wire.sym} -460 260 0 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} -20 354 2 0 {name=l24 lab=vss}
C {devices/lab_wire.sym} 795 614 2 0 {name=l25 lab=vss}
C {devices/lab_wire.sym} 975 354 2 0 {name=l26 lab=vss}
C {devices/lab_wire.sym} -350 614 2 0 {name=l27 lab=vss}
C {devices/lab_wire.sym} -1190 -90 0 1 {name=l28 lab=vref_cm}
C {devices/lab_wire.sym} -1190 90 2 0 {name=l29 lab=vss}
C {devices/lab_wire.sym} -1190 350 2 0 {name=l30 lab=vcmfb_raw}
C {devices/lab_wire.sym} -1190 430 0 1 {name=l31 lab=vdd}
C {devices/lab_wire.sym} -1190 610 2 0 {name=l32 lab=core__ref}
C {devices/lab_wire.sym} -1190 170 0 1 {name=l33 lab=vbl_ctl}
C {devices/lab_wire.sym} 215 490 0 0 {name=l34 lab=vss}
C {devices/lab_wire.sym} 155 360 0 0 {name=l35 lab=vss}
C {devices/lab_wire.sym} 460 430 0 1 {name=l36 lab=vss}
C {devices/ipin.sym} -390 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -210 260 0 0 {name=p1 lab=vinn}
C {devices/iopin.sym} -1250 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1250 660 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 1940 260 0 0 {name=p4 lab=voutp}
C {devices/opin.sym} 2520 260 0 0 {name=p5 lab=voutn}
B 8 -846 182 2050 598 {fill=0}
T {NMOS Simple Current Mirror (3 outputs)} -846 164 0 0 0.3 0.3 {layer=8}
B 10 -1016 182 476 338 {fill=0}
T {NMOS Differential Pair} -1016 164 0 0 0.3 0.3 {layer=10}
