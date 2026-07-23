v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_nmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=MIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmin_w l=x_dut_xmin_l m=x_dut_xmin_m}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=MIP model=sg13_lv_nmos spiceprefix=X w=x_dut_xmip_w l=x_dut_xmip_l m=x_dut_xmip_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 190 -90 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 90 0 150 0 {}
N 190 0 250 0 {}
N -190 60 190 60 {}
C {devices/lab_wire.sym} 190 -90 0 1 {name=l0 lab=otao}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l1 lab=otax}
C {devices/lab_wire.sym} -190 90 2 0 {name=l2 lab=tail}
C {devices/lab_wire.sym} -90 0 0 1 {name=l3 lab=vout}
C {devices/lab_wire.sym} 90 0 0 0 {name=l4 lab=vref}
C {devices/lab_wire.sym} 250 94 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l6 lab=vss}
C {devices/ipin.sym} -525 0 0 0 {name=p0 lab=vout}
C {devices/ipin.sym} -525 120 0 0 {name=p1 lab=vref}
C {devices/iopin.sym} -190 280 0 0 {name=p2 lab=tail}
C {devices/opin.sym} 525 -30 0 0 {name=p3 lab=otax}
C {devices/opin.sym} 525 90 0 0 {name=p4 lab=otao}
