v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_032_ti_ldo_error_selfbias} -480 -560 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -220 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_nmos_simple_1.sym} 220 0 0 0 {name=xdp_nmos_simple_1}
C {devices/capa_np.sym} -220 360 0 0 {name=CC value='c_comp'}
C {devices/res_np.sym} 0 360 0 0 {name=RND value='r_nd'}
C {devices/res_np.sym} 220 360 0 0 {name=RZ value='r_z'}
C {devices/sg13_lv_pmos_np.sym} -440 -360 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} -220 -360 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} 0 -360 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 220 -360 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_pmos_np.sym} 440 -360 0 0 {name=MBP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmbp_w l=x_dut_xmbp_l}
N -110 -60 -70 -60 {}
C {devices/lab_wire.sym} -70 -60 0 1 {name=l0 lab=ibias}
N -110 -20 -70 -20 {}
C {devices/lab_wire.sym} -70 -20 0 1 {name=l1 lab=nlev}
N -110 20 -70 20 {}
C {devices/lab_wire.sym} -70 20 0 1 {name=l2 lab=tail}
N -110 60 -70 60 {}
C {devices/lab_wire.sym} -70 60 0 1 {name=l3 lab=vout}
N -220 120 -220 160 {}
C {devices/lab_wire.sym} -220 160 2 0 {name=l4 lab=vss}
N 110 -20 70 -20 {}
C {devices/lab_wire.sym} 70 -20 0 0 {name=l5 lab=vinn}
N 110 20 70 20 {}
C {devices/lab_wire.sym} 70 20 0 0 {name=l6 lab=vinp}
N 330 -40 370 -40 {}
C {devices/lab_wire.sym} 370 -40 0 1 {name=l7 lab=na}
N 330 0 370 0 {}
C {devices/lab_wire.sym} 370 0 0 1 {name=l8 lab=nb}
N 330 40 370 40 {}
C {devices/lab_wire.sym} 370 40 0 1 {name=l9 lab=tail}
N 220 100 220 140 {}
C {devices/lab_wire.sym} 220 140 2 0 {name=l10 lab=vss}
N -220 330 -220 290 {}
C {devices/lab_wire.sym} -220 290 0 1 {name=l11 lab=ncz}
N -220 390 -220 430 {}
C {devices/lab_wire.sym} -220 430 2 0 {name=l12 lab=vout}
N 0 330 0 290 {}
C {devices/lab_wire.sym} 0 290 0 1 {name=l13 lab=na}
N 0 390 0 430 {}
C {devices/lab_wire.sym} 0 430 2 0 {name=l14 lab=nd}
N 220 330 220 290 {}
C {devices/lab_wire.sym} 220 290 0 1 {name=l15 lab=nb}
N 220 390 220 430 {}
C {devices/lab_wire.sym} 220 430 2 0 {name=l16 lab=ncz}
N -420 -330 -420 -290 {}
C {devices/lab_wire.sym} -420 -290 2 0 {name=l17 lab=na}
N -460 -360 -500 -360 {}
C {devices/lab_wire.sym} -500 -360 0 0 {name=l18 lab=nd}
N -420 -390 -420 -430 {}
C {devices/lab_wire.sym} -420 -430 0 1 {name=l19 lab=vdd}
N -420 -360 -380 -360 {}
C {devices/lab_wire.sym} -380 -360 0 1 {name=l20 lab=vdd}
N -200 -330 -200 -290 {}
C {devices/lab_wire.sym} -200 -290 2 0 {name=l21 lab=nlev}
N -240 -360 -280 -360 {}
C {devices/lab_wire.sym} -280 -360 0 0 {name=l22 lab=na}
N -200 -390 -200 -430 {}
C {devices/lab_wire.sym} -200 -430 0 1 {name=l23 lab=nd}
N -200 -360 -160 -360 {}
C {devices/lab_wire.sym} -160 -360 0 1 {name=l24 lab=vdd}
N 20 -330 20 -290 {}
C {devices/lab_wire.sym} 20 -290 2 0 {name=l25 lab=nb}
N -20 -360 -60 -360 {}
C {devices/lab_wire.sym} -60 -360 0 0 {name=l26 lab=nd}
N 20 -390 20 -430 {}
C {devices/lab_wire.sym} 20 -430 0 1 {name=l27 lab=vdd}
N 20 -360 60 -360 {}
C {devices/lab_wire.sym} 60 -360 0 1 {name=l28 lab=vdd}
N 240 -330 240 -290 {}
C {devices/lab_wire.sym} 240 -290 2 0 {name=l29 lab=vout}
N 200 -360 160 -360 {}
C {devices/lab_wire.sym} 160 -360 0 0 {name=l30 lab=nb}
N 240 -390 240 -430 {}
C {devices/lab_wire.sym} 240 -430 0 1 {name=l31 lab=vdd}
N 240 -360 280 -360 {}
C {devices/lab_wire.sym} 280 -360 0 1 {name=l32 lab=vdd}
N 460 -330 460 -290 {}
C {devices/lab_wire.sym} 460 -290 2 0 {name=l33 lab=ibias}
N 420 -360 380 -360 {}
C {devices/lab_wire.sym} 380 -360 0 0 {name=l34 lab=ibias}
N 460 -390 460 -430 {}
C {devices/lab_wire.sym} 460 -430 0 1 {name=l35 lab=vdd}
N 460 -360 500 -360 {}
C {devices/lab_wire.sym} 500 -360 0 1 {name=l36 lab=vdd}
