v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_030_miller_cmfb_composite} -1360 -560 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -220 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_nmos_simple_1.sym} 230 0 0 0 {name=xdp_nmos_simple_1}
C {devices/capa_np.sym} -1100 360 0 0 {name=C1_CORE value='x_dut_c1_core_value'}
C {devices/capa_np.sym} -880 360 0 0 {name=C2_CORE value='x_dut_c2_core_value'}
C {devices/capa_np.sym} -660 360 0 0 {name=CIN_SERVO_SERVO value='cin_val_servo'}
C {devices/capa_np.sym} -440 360 0 0 {name=COUT_SERVO_SERVO value='cout_val_servo'}
C {devices/vccs.sym} -220 360 0 0 {name=GM_SERVO_SERVO value="\{gm_val_servo\}"}
C {devices/isource_np.sym} -1320 360 0 0 {name=IBIAS_CORE value="dc \{i_bias_core\}"}
C {devices/res_np.sym} 0 360 0 0 {name=R1_CORE value='x_dut_r1_core_value'}
C {devices/res_np.sym} 220 360 0 0 {name=R2_CORE value='x_dut_r2_core_value'}
C {devices/res_np.sym} 440 360 0 0 {name=RIN_SERVO_SERVO value='rin_val_servo'}
C {devices/res_np.sym} 660 360 0 0 {name=RMN_SERVO value='x_dut_rmn_servo_value'}
C {devices/res_np.sym} 880 360 0 0 {name=RMP_SERVO value='x_dut_rmp_servo_value'}
C {devices/res_np.sym} 1100 360 0 0 {name=ROUT_SERVO_SERVO value='rout_val_servo'}
C {devices/vsource_np.sym} -1320 140 0 0 {name=VBL0 value="dc \{vbl0\}" savecurrent=false}
C {devices/vsource_np.sym} -1320 -80 0 0 {name=VREFCM value="dc \{vcm_ref\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} -330 -360 0 0 {name=M3_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_core_w l=x_dut_xm3_core_l m=x_dut_xm3_core_m}
C {devices/sg13_lv_pmos_np.sym} -110 -360 0 0 {name=M4_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_core_w l=x_dut_xm4_core_l m=x_dut_xm4_core_m}
C {devices/sg13_lv_pmos_np.sym} 110 -360 0 0 {name=M5_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_core_w l=x_dut_xm5_core_l m=x_dut_xm5_core_m}
C {devices/sg13_lv_pmos_np.sym} 330 -360 0 0 {name=M9_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_core_w l=x_dut_xm9_core_l m=x_dut_xm9_core_m}
N -100 -60 -60 -60 {}
C {devices/lab_wire.sym} -60 -60 0 1 {name=l0 lab=core__ref}
N -100 -20 -60 -20 {}
C {devices/lab_wire.sym} -60 -20 0 1 {name=l1 lab=core__tail}
N -100 20 -60 20 {}
C {devices/lab_wire.sym} -60 20 0 1 {name=l2 lab=voutn}
N -100 60 -60 60 {}
C {devices/lab_wire.sym} -60 60 0 1 {name=l3 lab=voutp}
N -220 120 -220 160 {}
C {devices/lab_wire.sym} -220 160 2 0 {name=l4 lab=vss}
N 120 -20 80 -20 {}
C {devices/lab_wire.sym} 80 -20 0 0 {name=l5 lab=vinn}
N 120 20 80 20 {}
C {devices/lab_wire.sym} 80 20 0 0 {name=l6 lab=vinp}
N 340 -40 380 -40 {}
C {devices/lab_wire.sym} 380 -40 0 1 {name=l7 lab=core__stg1n}
N 340 0 380 0 {}
C {devices/lab_wire.sym} 380 0 0 1 {name=l8 lab=core__stg1p}
N 340 40 380 40 {}
C {devices/lab_wire.sym} 380 40 0 1 {name=l9 lab=core__tail}
N 230 100 230 140 {}
C {devices/lab_wire.sym} 230 140 2 0 {name=l10 lab=vss}
N -1100 330 -1100 290 {}
C {devices/lab_wire.sym} -1100 290 0 1 {name=l11 lab=core__mill_p}
N -1100 390 -1100 430 {}
C {devices/lab_wire.sym} -1100 430 2 0 {name=l12 lab=voutp}
N -880 330 -880 290 {}
C {devices/lab_wire.sym} -880 290 0 1 {name=l13 lab=core__mill_n}
N -880 390 -880 430 {}
C {devices/lab_wire.sym} -880 430 2 0 {name=l14 lab=voutn}
N -660 330 -660 290 {}
C {devices/lab_wire.sym} -660 290 0 1 {name=l15 lab=servo__cm_sense}
N -660 390 -660 430 {}
C {devices/lab_wire.sym} -660 430 2 0 {name=l16 lab=vref_cm}
N -440 330 -440 290 {}
C {devices/lab_wire.sym} -440 290 0 1 {name=l17 lab=vss}
N -440 390 -440 430 {}
C {devices/lab_wire.sym} -440 430 2 0 {name=l18 lab=vcmfb_raw}
N -220 330 -220 290 {}
C {devices/lab_wire.sym} -220 290 0 1 {name=l19 lab=vss}
N -220 390 -220 430 {}
C {devices/lab_wire.sym} -220 430 2 0 {name=l20 lab=vcmfb_raw}
N -260 340 -300 340 {}
C {devices/lab_wire.sym} -300 340 0 0 {name=l21 lab=vref_cm}
N -260 380 -300 380 {}
C {devices/lab_wire.sym} -300 380 0 0 {name=l22 lab=servo__cm_sense}
N -1320 330 -1320 290 {}
C {devices/lab_wire.sym} -1320 290 0 1 {name=l23 lab=vdd}
N -1320 390 -1320 430 {}
C {devices/lab_wire.sym} -1320 430 2 0 {name=l24 lab=core__ref}
N 0 330 0 290 {}
C {devices/lab_wire.sym} 0 290 0 1 {name=l25 lab=core__stg1p}
N 0 390 0 430 {}
C {devices/lab_wire.sym} 0 430 2 0 {name=l26 lab=core__mill_p}
N 220 330 220 290 {}
C {devices/lab_wire.sym} 220 290 0 1 {name=l27 lab=core__stg1n}
N 220 390 220 430 {}
C {devices/lab_wire.sym} 220 430 2 0 {name=l28 lab=core__mill_n}
N 440 330 440 290 {}
C {devices/lab_wire.sym} 440 290 0 1 {name=l29 lab=servo__cm_sense}
N 440 390 440 430 {}
C {devices/lab_wire.sym} 440 430 2 0 {name=l30 lab=vref_cm}
N 660 330 660 290 {}
C {devices/lab_wire.sym} 660 290 0 1 {name=l31 lab=voutn}
N 660 390 660 430 {}
C {devices/lab_wire.sym} 660 430 2 0 {name=l32 lab=servo__cm_sense}
N 880 330 880 290 {}
C {devices/lab_wire.sym} 880 290 0 1 {name=l33 lab=servo__cm_sense}
N 880 390 880 430 {}
C {devices/lab_wire.sym} 880 430 2 0 {name=l34 lab=voutp}
N 1100 330 1100 290 {}
C {devices/lab_wire.sym} 1100 290 0 1 {name=l35 lab=vss}
N 1100 390 1100 430 {}
C {devices/lab_wire.sym} 1100 430 2 0 {name=l36 lab=vcmfb_raw}
N -1320 110 -1320 70 {}
C {devices/lab_wire.sym} -1320 70 0 1 {name=l37 lab=vbl_ctl}
N -1320 170 -1320 210 {}
C {devices/lab_wire.sym} -1320 210 2 0 {name=l38 lab=vcmfb_raw}
N -1320 -110 -1320 -150 {}
C {devices/lab_wire.sym} -1320 -150 0 1 {name=l39 lab=vref_cm}
N -1320 -50 -1320 -10 {}
C {devices/lab_wire.sym} -1320 -10 2 0 {name=l40 lab=vss}
N -310 -330 -310 -290 {}
C {devices/lab_wire.sym} -310 -290 2 0 {name=l41 lab=core__stg1p}
N -350 -360 -390 -360 {}
C {devices/lab_wire.sym} -390 -360 0 0 {name=l42 lab=vbl_ctl}
N -310 -390 -310 -430 {}
C {devices/lab_wire.sym} -310 -430 0 1 {name=l43 lab=vdd}
N -310 -360 -270 -360 {}
C {devices/lab_wire.sym} -270 -360 0 1 {name=l44 lab=vdd}
N -90 -330 -90 -290 {}
C {devices/lab_wire.sym} -90 -290 2 0 {name=l45 lab=core__stg1n}
N -130 -360 -170 -360 {}
C {devices/lab_wire.sym} -170 -360 0 0 {name=l46 lab=vbl_ctl}
N -90 -390 -90 -430 {}
C {devices/lab_wire.sym} -90 -430 0 1 {name=l47 lab=vdd}
N -90 -360 -50 -360 {}
C {devices/lab_wire.sym} -50 -360 0 1 {name=l48 lab=vdd}
N 130 -330 130 -290 {}
C {devices/lab_wire.sym} 130 -290 2 0 {name=l49 lab=voutp}
N 90 -360 50 -360 {}
C {devices/lab_wire.sym} 50 -360 0 0 {name=l50 lab=core__stg1p}
N 130 -390 130 -430 {}
C {devices/lab_wire.sym} 130 -430 0 1 {name=l51 lab=vdd}
N 130 -360 170 -360 {}
C {devices/lab_wire.sym} 170 -360 0 1 {name=l52 lab=vdd}
N 350 -330 350 -290 {}
C {devices/lab_wire.sym} 350 -290 2 0 {name=l53 lab=voutn}
N 310 -360 270 -360 {}
C {devices/lab_wire.sym} 270 -360 0 0 {name=l54 lab=core__stg1n}
N 350 -390 350 -430 {}
C {devices/lab_wire.sym} 350 -430 0 1 {name=l55 lab=vdd}
N 350 -360 390 -360 {}
C {devices/lab_wire.sym} 390 -360 0 1 {name=l56 lab=vdd}
