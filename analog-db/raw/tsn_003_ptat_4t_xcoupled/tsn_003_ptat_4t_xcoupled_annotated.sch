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
N -645 -140 645 -140 {}
N -250 0 -190 0 {}
N 120 0 150 0 {}
N 190 0 250 0 {}
N -190 60 120 60 {}
N -190 70 -150 70 {}
N 150 190 190 190 {}
N -250 260 -190 260 {}
N -180 260 150 260 {}
N 190 260 250 260 {}
N -645 400 645 400 {}
C {devices/lab_wire.sym} 190 90 2 0 {name=l0 lab=na}
C {devices/lab_wire.sym} -250 94 2 0 {name=l1 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l2 lab=vdd}
C {devices/lab_wire.sym} -250 354 2 0 {name=l3 lab=vss}
C {devices/lab_wire.sym} 250 354 2 0 {name=l4 lab=vss}
C {devices/iopin.sym} -645 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -645 400 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 120 0 0 0 {name=p2 lab=vout}
B 8 -626 182 626 338 {fill=0}
T {NMOS Simple Current Mirror} -626 164 0 0 0.3 0.3 {layer=8}
B 10 -626 -78 626 78 {fill=0}
T {PMOS Simple Current Mirror} -626 -96 0 0 0.3 0.3 {layer=10}
