v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_2} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N -150 -70 -150 0 {}
N 120 -60 120 0 {}
N 190 -90 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N -190 -70 -150 -70 {}
N -190 -60 120 -60 {}
N -250 0 -190 0 {}
N 120 0 150 0 {}
N 190 0 250 0 {}
N -190 60 190 60 {}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l0 lab=ebias_ref}
C {devices/lab_wire.sym} 190 -90 0 1 {name=l1 lab=retail}
C {devices/lab_wire.sym} -190 90 2 0 {name=l2 lab=vss}
C {devices/lab_wire.sym} 250 94 2 0 {name=l3 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l4 lab=vss}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 520 -30 0 0 {name=p1 lab=ebias_ref}
C {devices/opin.sym} 520 90 0 0 {name=p2 lab=retail}
