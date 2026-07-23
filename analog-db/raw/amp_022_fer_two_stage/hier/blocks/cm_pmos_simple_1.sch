v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 180 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 70 {}
N -150 0 -150 70 {}
N -50 0 -50 60 {}
N 20 -60 20 -30 {}
N 20 30 20 90 {}
N 80 0 80 94 {}
N 200 -60 200 -30 {}
N 200 30 200 90 {}
N 260 0 260 94 {}
N -190 -60 200 -60 {}
N -250 0 -190 0 {}
N -50 0 -20 0 {}
N 20 0 80 0 {}
N 130 0 160 0 {}
N 200 0 260 0 {}
N -190 60 -50 60 {}
N -190 70 -150 70 {}
C {devices/lab_wire.sym} 200 90 2 0 {name=l0 lab=c}
C {devices/lab_wire.sym} -150 60 2 0 {name=l1 lab=pbias}
C {devices/lab_wire.sym} 160 0 0 0 {name=l2 lab=pbias}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l3 lab=vdd}
C {devices/lab_wire.sym} 20 90 2 0 {name=l4 lab=vout}
C {devices/lab_wire.sym} 260 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l7 lab=vdd}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 530 0 0 0 {name=p1 lab=pbias}
C {devices/opin.sym} 530 120 0 0 {name=p2 lab=vout}
C {devices/opin.sym} 530 240 0 0 {name=p3 lab=c}
