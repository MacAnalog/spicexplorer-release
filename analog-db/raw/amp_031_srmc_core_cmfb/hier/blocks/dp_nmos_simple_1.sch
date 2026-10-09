v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_nmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
N -250 0 -250 94 {}
N -190 -60 -190 -30 {}
N -190 30 -190 60 {}
N 190 -60 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N -250 0 -190 0 {}
N -150 0 -120 0 {}
N 60 0 150 0 {}
N 190 0 250 0 {}
N -190 60 190 60 {}
N -645 140 645 140 {}
C {devices/lab_wire.sym} -645 140 0 0 {name=l0 lab=vss}
C {devices/lab_wire.sym} 250 94 2 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l2 lab=vss}
C {devices/ipin.sym} -120 0 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} 60 0 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -190 60 0 0 {name=p2 lab=ntail}
C {devices/opin.sym} -190 -60 0 0 {name=p3 lab=vo1p}
C {devices/opin.sym} 190 -60 0 0 {name=p4 lab=vo1n}
