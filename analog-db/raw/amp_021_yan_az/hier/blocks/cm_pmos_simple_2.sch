v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_2} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 180 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M67 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm67_w l=x_dut_xm67_l m=x_dut_xm67_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N -150 0 -150 60 {}
N 20 -60 20 -30 {}
N 20 30 20 90 {}
N 80 0 80 94 {}
N 160 0 160 70 {}
N 200 -60 200 -30 {}
N 200 30 200 70 {}
N 260 0 260 94 {}
N -190 -60 200 -60 {}
N -250 0 -190 0 {}
N -150 0 -20 0 {}
N 20 0 80 0 {}
N 200 0 260 0 {}
N 160 70 200 70 {}
C {devices/lab_wire.sym} -150 60 2 0 {name=l0 lab=VOUTN}
C {devices/lab_wire.sym} 160 0 0 0 {name=l1 lab=VOUTN}
C {devices/lab_wire.sym} 20 90 2 0 {name=l2 lab=net050}
C {devices/lab_wire.sym} -190 90 2 0 {name=l3 lab=net057}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l4 lab=vdd}
C {devices/lab_wire.sym} 260 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l7 lab=vdd}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 530 0 0 0 {name=p1 lab=VOUTN}
C {devices/opin.sym} 530 120 0 0 {name=p2 lab=net057}
C {devices/opin.sym} 530 240 0 0 {name=p3 lab=net050}
