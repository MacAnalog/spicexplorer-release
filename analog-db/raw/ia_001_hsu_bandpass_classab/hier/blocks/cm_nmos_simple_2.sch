v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_2} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=MO5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo5_w l=x_dut_xmo5_l m=x_dut_xmo5_m}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=MO6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo6_w l=x_dut_xmo6_l m=x_dut_xmo6_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 150 -70 150 0 {}
N 190 -90 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N 150 -70 190 -70 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 190 0 250 0 {}
N -190 60 190 60 {}
C {devices/lab_wire.sym} -90 0 0 1 {name=l0 lab=dio_n}
C {devices/lab_wire.sym} 190 -90 0 1 {name=l1 lab=dio_n}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l2 lab=msrc_n}
C {devices/lab_wire.sym} -190 90 2 0 {name=l3 lab=vss}
C {devices/lab_wire.sym} 250 94 2 0 {name=l4 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l5 lab=vss}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 525 -30 0 0 {name=p1 lab=msrc_n}
C {devices/opin.sym} 525 90 0 0 {name=p2 lab=dio_n}
