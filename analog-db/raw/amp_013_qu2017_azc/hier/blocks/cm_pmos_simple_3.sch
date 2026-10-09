v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_3} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -250 0 -250 94 {}
N -190 -140 -190 -30 {}
N -190 30 -190 70 {}
N -150 0 -150 70 {}
N 120 0 120 60 {}
N 190 -140 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N -645 -140 645 -140 {}
N -250 0 -190 0 {}
N 120 0 150 0 {}
N 190 0 250 0 {}
N -190 60 120 60 {}
N -190 70 -150 70 {}
C {devices/lab_wire.sym} -250 94 2 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l1 lab=vdd}
C {devices/iopin.sym} -645 -140 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 120 0 0 0 {name=p1 lab=net055}
C {devices/opin.sym} 190 60 0 0 {name=p2 lab=net057}
