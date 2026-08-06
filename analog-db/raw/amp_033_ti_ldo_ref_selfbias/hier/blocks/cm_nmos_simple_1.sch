v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 190 0 0 0 {name=MB0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} 0 0 0 0 {name=MBC model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbc_w l=x_dut_xmbc_l m=x_dut_xmbc_m}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=MBO model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbo_w l=x_dut_xmbo_l m=x_dut_xmbo_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 20 -90 20 -30 {}
N 20 30 20 60 {}
N 80 0 80 94 {}
N 170 -70 170 0 {}
N 210 -90 210 -30 {}
N 210 30 210 60 {}
N 270 0 270 94 {}
N 170 -70 210 -70 {}
N -250 0 -190 0 {}
N -150 0 -20 0 {}
N 20 0 80 0 {}
N 210 0 270 0 {}
N -190 60 210 60 {}
C {devices/lab_wire.sym} -150 0 0 0 {name=l0 lab=ibias}
C {devices/lab_wire.sym} 210 -90 0 1 {name=l1 lab=ibias}
C {devices/lab_wire.sym} 20 -90 0 1 {name=l2 lab=tail}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l3 lab=vout}
C {devices/lab_wire.sym} -190 90 2 0 {name=l4 lab=vss}
C {devices/lab_wire.sym} 270 94 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} 80 94 2 0 {name=l6 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l7 lab=vss}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 545 -30 0 0 {name=p1 lab=vout}
C {devices/opin.sym} 545 90 0 0 {name=p2 lab=tail}
C {devices/opin.sym} 545 210 0 0 {name=p3 lab=ibias}
