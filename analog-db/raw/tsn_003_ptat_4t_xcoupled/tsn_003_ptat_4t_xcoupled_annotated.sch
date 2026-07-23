v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {tsn_003_ptat_4t_xcoupled} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -170 260 0 1 {name=M0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_nmos_np.sym} 170 260 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
N -250 0 -250 94 {}
N -250 260 -250 354 {}
N -190 -140 -190 -30 {}
N -190 30 -190 230 {}
N -190 290 -190 400 {}
N -150 0 -150 70 {}
N 120 0 120 60 {}
N 150 190 150 260 {}
N 190 -140 190 -30 {}
N 190 30 190 230 {}
N 190 290 190 400 {}
N 250 0 250 94 {}
N 250 260 250 354 {}
N -380 -140 380 -140 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 120 0 150 0 {}
N 190 0 250 0 {}
N -190 60 120 60 {}
N -190 70 -150 70 {}
N 150 190 190 190 {}
N -250 260 -190 260 {}
N -150 260 -90 260 {}
N 190 260 250 260 {}
N -380 400 380 400 {}
C {devices/lab_wire.sym} -380 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -380 400 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -90 260 0 1 {name=l2 lab=na}
C {devices/lab_wire.sym} 190 90 2 0 {name=l3 lab=na}
C {devices/lab_wire.sym} -90 0 0 1 {name=l4 lab=vout}
C {devices/lab_wire.sym} -250 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} -250 354 2 0 {name=l7 lab=vss}
C {devices/lab_wire.sym} 250 354 2 0 {name=l8 lab=vss}
C {devices/opin.sym} 520 0 0 0 {name=p0 lab=vout}
B 8 -358 182 358 338 {fill=0}
T {NMOS Simple Current Mirror} -358 164 0 0 0.3 0.3 {layer=8}
B 10 -358 -78 358 78 {fill=0}
T {PMOS Simple Current Mirror} -358 -96 0 0 0.3 0.3 {layer=10}
