v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_030_miller_cmfb_composite} -1250 -560 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -220 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_nmos_simple_1.sym} 220 0 0 0 {name=xdp_nmos_simple_1}
C {devices/capa_np.sym} -990 360 0 0 {name=C1_CORE value='x_dut_c1_core_value'}
C {devices/capa_np.sym} -770 360 0 0 {name=C2_CORE value='x_dut_c2_core_value'}
C {devices/capa_np.sym} -550 360 0 0 {name=CIN_SERVO_SERVO value='cin_val_servo'}
C {devices/capa_np.sym} -330 360 0 0 {name=COUT_SERVO_SERVO value='cout_val_servo'}
C {devices/isource_np.sym} -1210 360 0 0 {name=IBIAS_CORE value="dc {i_bias_core}"}
C {devices/res_np.sym} -110 360 0 0 {name=R1_CORE value='x_dut_r1_core_value'}
C {devices/res_np.sym} 110 360 0 0 {name=R2_CORE value='x_dut_r2_core_value'}
C {devices/res_np.sym} 330 360 0 0 {name=RIN_SERVO_SERVO value='rin_val_servo'}
C {devices/res_np.sym} 550 360 0 0 {name=RMN_SERVO value='x_dut_rmn_servo_value'}
C {devices/res_np.sym} 770 360 0 0 {name=RMP_SERVO value='x_dut_rmp_servo_value'}
C {devices/res_np.sym} 990 360 0 0 {name=ROUT_SERVO_SERVO value='rout_val_servo'}
C {devices/vsource_np.sym} -1210 140 0 0 {name=VBL0 value="dc {vbl0}"}
C {devices/vsource_np.sym} -1210 -80 0 0 {name=VREFCM value="dc {vcm_ref}"}
C {devices/sg13_lv_pmos_np.sym} -330 -360 0 0 {name=M3_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_core_w l=x_dut_xm3_core_l m=x_dut_xm3_core_m}
C {devices/sg13_lv_pmos_np.sym} -110 -360 0 0 {name=M4_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_core_w l=x_dut_xm4_core_l m=x_dut_xm4_core_m}
C {devices/sg13_lv_pmos_np.sym} 110 -360 0 0 {name=M5_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_core_w l=x_dut_xm5_core_l m=x_dut_xm5_core_m}
C {devices/sg13_lv_pmos_np.sym} 330 -360 0 0 {name=M9_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_core_w l=x_dut_xm9_core_l m=x_dut_xm9_core_m}
N -110 -60 -70 -60 {}
C {devices/lab_wire.sym} -70 -60 0 1 {name=l0 lab=core__ref}
N -110 -20 -70 -20 {}
C {devices/lab_wire.sym} -70 -20 0 1 {name=l1 lab=core__tail}
N -110 20 -70 20 {}
C {devices/lab_wire.sym} -70 20 0 1 {name=l2 lab=voutn}
N -110 60 -70 60 {}
C {devices/lab_wire.sym} -70 60 0 1 {name=l3 lab=voutp}
N -220 120 -220 160 {}
C {devices/lab_wire.sym} -220 160 2 0 {name=l4 lab=vss}
N 110 -20 70 -20 {}
C {devices/lab_wire.sym} 70 -20 0 0 {name=l5 lab=vinn}
N 110 20 70 20 {}
C {devices/lab_wire.sym} 70 20 0 0 {name=l6 lab=vinp}
N 330 -40 370 -40 {}
C {devices/lab_wire.sym} 370 -40 0 1 {name=l7 lab=core__stg1n}
N 330 0 370 0 {}
C {devices/lab_wire.sym} 370 0 0 1 {name=l8 lab=core__stg1p}
N 330 40 370 40 {}
C {devices/lab_wire.sym} 370 40 0 1 {name=l9 lab=core__tail}
N 220 100 220 140 {}
C {devices/lab_wire.sym} 220 140 2 0 {name=l10 lab=vss}
N -990 330 -990 290 {}
C {devices/lab_wire.sym} -990 290 0 1 {name=l11 lab=core__mill_p}
N -990 390 -990 430 {}
C {devices/lab_wire.sym} -990 430 2 0 {name=l12 lab=voutp}
N -770 330 -770 290 {}
C {devices/lab_wire.sym} -770 290 0 1 {name=l13 lab=core__mill_n}
N -770 390 -770 430 {}
C {devices/lab_wire.sym} -770 430 2 0 {name=l14 lab=voutn}
N -550 330 -550 290 {}
C {devices/lab_wire.sym} -550 290 0 1 {name=l15 lab=servo__cm_sense}
N -550 390 -550 430 {}
C {devices/lab_wire.sym} -550 430 2 0 {name=l16 lab=vref_cm}
N -330 330 -330 290 {}
C {devices/lab_wire.sym} -330 290 0 1 {name=l17 lab=vss}
N -330 390 -330 430 {}
C {devices/lab_wire.sym} -330 430 2 0 {name=l18 lab=vcmfb_raw}
N -1210 330 -1210 290 {}
C {devices/lab_wire.sym} -1210 290 0 1 {name=l19 lab=vdd}
N -1210 390 -1210 430 {}
C {devices/lab_wire.sym} -1210 430 2 0 {name=l20 lab=core__ref}
N -110 330 -110 290 {}
C {devices/lab_wire.sym} -110 290 0 1 {name=l21 lab=core__stg1p}
N -110 390 -110 430 {}
C {devices/lab_wire.sym} -110 430 2 0 {name=l22 lab=core__mill_p}
N 110 330 110 290 {}
C {devices/lab_wire.sym} 110 290 0 1 {name=l23 lab=core__stg1n}
N 110 390 110 430 {}
C {devices/lab_wire.sym} 110 430 2 0 {name=l24 lab=core__mill_n}
N 330 330 330 290 {}
C {devices/lab_wire.sym} 330 290 0 1 {name=l25 lab=servo__cm_sense}
N 330 390 330 430 {}
C {devices/lab_wire.sym} 330 430 2 0 {name=l26 lab=vref_cm}
N 550 330 550 290 {}
C {devices/lab_wire.sym} 550 290 0 1 {name=l27 lab=voutn}
N 550 390 550 430 {}
C {devices/lab_wire.sym} 550 430 2 0 {name=l28 lab=servo__cm_sense}
N 770 330 770 290 {}
C {devices/lab_wire.sym} 770 290 0 1 {name=l29 lab=servo__cm_sense}
N 770 390 770 430 {}
C {devices/lab_wire.sym} 770 430 2 0 {name=l30 lab=voutp}
N 990 330 990 290 {}
C {devices/lab_wire.sym} 990 290 0 1 {name=l31 lab=vss}
N 990 390 990 430 {}
C {devices/lab_wire.sym} 990 430 2 0 {name=l32 lab=vcmfb_raw}
N -1210 110 -1210 70 {}
C {devices/lab_wire.sym} -1210 70 0 1 {name=l33 lab=vbl_ctl}
N -1210 170 -1210 210 {}
C {devices/lab_wire.sym} -1210 210 2 0 {name=l34 lab=vcmfb_raw}
N -1210 -110 -1210 -150 {}
C {devices/lab_wire.sym} -1210 -150 0 1 {name=l35 lab=vref_cm}
N -1210 -50 -1210 -10 {}
C {devices/lab_wire.sym} -1210 -10 2 0 {name=l36 lab=vss}
N -310 -330 -310 -290 {}
C {devices/lab_wire.sym} -310 -290 2 0 {name=l37 lab=core__stg1p}
N -350 -360 -390 -360 {}
C {devices/lab_wire.sym} -390 -360 0 0 {name=l38 lab=vbl_ctl}
N -310 -390 -310 -430 {}
C {devices/lab_wire.sym} -310 -430 0 1 {name=l39 lab=vdd}
N -310 -360 -270 -360 {}
C {devices/lab_wire.sym} -270 -360 0 1 {name=l40 lab=vdd}
N -90 -330 -90 -290 {}
C {devices/lab_wire.sym} -90 -290 2 0 {name=l41 lab=core__stg1n}
N -130 -360 -170 -360 {}
C {devices/lab_wire.sym} -170 -360 0 0 {name=l42 lab=vbl_ctl}
N -90 -390 -90 -430 {}
C {devices/lab_wire.sym} -90 -430 0 1 {name=l43 lab=vdd}
N -90 -360 -50 -360 {}
C {devices/lab_wire.sym} -50 -360 0 1 {name=l44 lab=vdd}
N 130 -330 130 -290 {}
C {devices/lab_wire.sym} 130 -290 2 0 {name=l45 lab=voutp}
N 90 -360 50 -360 {}
C {devices/lab_wire.sym} 50 -360 0 0 {name=l46 lab=core__stg1p}
N 130 -390 130 -430 {}
C {devices/lab_wire.sym} 130 -430 0 1 {name=l47 lab=vdd}
N 130 -360 170 -360 {}
C {devices/lab_wire.sym} 170 -360 0 1 {name=l48 lab=vdd}
N 350 -330 350 -290 {}
C {devices/lab_wire.sym} 350 -290 2 0 {name=l49 lab=voutn}
N 310 -360 270 -360 {}
C {devices/lab_wire.sym} 270 -360 0 0 {name=l50 lab=core__stg1n}
N 350 -390 350 -430 {}
C {devices/lab_wire.sym} 350 -430 0 1 {name=l51 lab=vdd}
N 350 -360 390 -360 {}
C {devices/lab_wire.sym} 390 -360 0 1 {name=l52 lab=vdd}
