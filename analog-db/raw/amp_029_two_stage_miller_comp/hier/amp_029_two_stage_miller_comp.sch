v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_029_two_stage_miller_comp} -590 -560 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -220 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_nmos_simple_1.sym} 220 0 0 0 {name=xdp_nmos_simple_1}
C {devices/capa_np.sym} -330 360 0 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} -110 360 0 0 {name=C2 value='x_dut_c2_value'}
C {devices/isource_np.sym} -550 360 0 0 {name=IBIAS value="dc {i_bias}"}
C {devices/res_np.sym} 110 360 0 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} 330 360 0 0 {name=R2 value='x_dut_r2_value'}
C {devices/vsource_np.sym} -550 140 0 0 {name=VBL value="dc {vbl}"}
C {devices/sg13_lv_pmos_np.sym} -330 -360 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -110 -360 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 110 -360 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 330 -360 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -110 -60 -70 -60 {}
C {devices/lab_wire.sym} -70 -60 0 1 {name=l0 lab=ref}
N -110 -20 -70 -20 {}
C {devices/lab_wire.sym} -70 -20 0 1 {name=l1 lab=tail}
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
C {devices/lab_wire.sym} 370 -40 0 1 {name=l7 lab=stg1n}
N 330 0 370 0 {}
C {devices/lab_wire.sym} 370 0 0 1 {name=l8 lab=stg1p}
N 330 40 370 40 {}
C {devices/lab_wire.sym} 370 40 0 1 {name=l9 lab=tail}
N 220 100 220 140 {}
C {devices/lab_wire.sym} 220 140 2 0 {name=l10 lab=vss}
N -330 330 -330 290 {}
C {devices/lab_wire.sym} -330 290 0 1 {name=l11 lab=mill_p}
N -330 390 -330 430 {}
C {devices/lab_wire.sym} -330 430 2 0 {name=l12 lab=voutp}
N -110 330 -110 290 {}
C {devices/lab_wire.sym} -110 290 0 1 {name=l13 lab=mill_n}
N -110 390 -110 430 {}
C {devices/lab_wire.sym} -110 430 2 0 {name=l14 lab=voutn}
N -550 330 -550 290 {}
C {devices/lab_wire.sym} -550 290 0 1 {name=l15 lab=vdd}
N -550 390 -550 430 {}
C {devices/lab_wire.sym} -550 430 2 0 {name=l16 lab=ref}
N 110 330 110 290 {}
C {devices/lab_wire.sym} 110 290 0 1 {name=l17 lab=stg1p}
N 110 390 110 430 {}
C {devices/lab_wire.sym} 110 430 2 0 {name=l18 lab=mill_p}
N 330 330 330 290 {}
C {devices/lab_wire.sym} 330 290 0 1 {name=l19 lab=stg1n}
N 330 390 330 430 {}
C {devices/lab_wire.sym} 330 430 2 0 {name=l20 lab=mill_n}
N -550 110 -550 70 {}
C {devices/lab_wire.sym} -550 70 0 1 {name=l21 lab=vbl}
N -550 170 -550 210 {}
C {devices/lab_wire.sym} -550 210 2 0 {name=l22 lab=vss}
N -310 -330 -310 -290 {}
C {devices/lab_wire.sym} -310 -290 2 0 {name=l23 lab=stg1p}
N -350 -360 -390 -360 {}
C {devices/lab_wire.sym} -390 -360 0 0 {name=l24 lab=vbl}
N -310 -390 -310 -430 {}
C {devices/lab_wire.sym} -310 -430 0 1 {name=l25 lab=vdd}
N -310 -360 -270 -360 {}
C {devices/lab_wire.sym} -270 -360 0 1 {name=l26 lab=vdd}
N -90 -330 -90 -290 {}
C {devices/lab_wire.sym} -90 -290 2 0 {name=l27 lab=stg1n}
N -130 -360 -170 -360 {}
C {devices/lab_wire.sym} -170 -360 0 0 {name=l28 lab=vbl}
N -90 -390 -90 -430 {}
C {devices/lab_wire.sym} -90 -430 0 1 {name=l29 lab=vdd}
N -90 -360 -50 -360 {}
C {devices/lab_wire.sym} -50 -360 0 1 {name=l30 lab=vdd}
N 130 -330 130 -290 {}
C {devices/lab_wire.sym} 130 -290 2 0 {name=l31 lab=voutp}
N 90 -360 50 -360 {}
C {devices/lab_wire.sym} 50 -360 0 0 {name=l32 lab=stg1p}
N 130 -390 130 -430 {}
C {devices/lab_wire.sym} 130 -430 0 1 {name=l33 lab=vdd}
N 130 -360 170 -360 {}
C {devices/lab_wire.sym} 170 -360 0 1 {name=l34 lab=vdd}
N 350 -330 350 -290 {}
C {devices/lab_wire.sym} 350 -290 2 0 {name=l35 lab=voutn}
N 310 -360 270 -360 {}
C {devices/lab_wire.sym} 270 -360 0 0 {name=l36 lab=stg1n}
N 350 -390 350 -430 {}
C {devices/lab_wire.sym} 350 -430 0 1 {name=l37 lab=vdd}
N 350 -360 390 -360 {}
C {devices/lab_wire.sym} 390 -360 0 1 {name=l38 lab=vdd}
