v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 195 0 0 0 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l ng=x_dut_xm13_ng m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 0 0 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l ng=x_dut_xm3_ng m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l ng=x_dut_xm4_ng m=x_dut_xm4_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 20 -90 20 -30 {}
N 20 30 20 60 {}
N 80 0 80 94 {}
N 175 -70 175 0 {}
N 215 -90 215 -30 {}
N 215 30 215 60 {}
N 275 0 275 94 {}
N 175 -70 215 -70 {}
N -250 0 -190 0 {}
N -150 0 -20 0 {}
N 20 0 80 0 {}
N 215 0 275 0 {}
N -190 60 215 60 {}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l0 lab=foldn}
C {devices/lab_wire.sym} 20 -90 0 1 {name=l1 lab=foldp}
C {devices/lab_wire.sym} -150 0 0 0 {name=l2 lab=nbias}
C {devices/lab_wire.sym} 215 -90 0 1 {name=l3 lab=nbias}
C {devices/lab_wire.sym} -190 90 2 0 {name=l4 lab=vss}
C {devices/lab_wire.sym} 275 94 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} 80 94 2 0 {name=l6 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l7 lab=vss}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 565 -30 0 0 {name=p1 lab=foldn}
C {devices/opin.sym} 565 90 0 0 {name=p2 lab=foldp}
C {devices/opin.sym} 565 210 0 0 {name=p3 lab=nbias}
