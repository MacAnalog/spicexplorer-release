v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_1} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -340 0 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l ng=x_dut_xm13_ng m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 0 0 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l ng=x_dut_xm3_ng m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} 340 0 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l ng=x_dut_xm4_ng m=x_dut_xm4_m}
N -420 0 -420 94 {}
N -360 -70 -360 -30 {}
N -360 30 -360 140 {}
N -320 -70 -320 0 {}
N -50 -60 -50 60 {}
N 20 -60 20 -30 {}
N 20 30 20 140 {}
N 80 0 80 94 {}
N 290 0 290 60 {}
N 360 -60 360 -30 {}
N 360 30 360 140 {}
N 420 0 420 94 {}
N -360 -70 -320 -70 {}
N -360 -60 -50 -60 {}
N -420 0 -360 0 {}
N -50 0 -20 0 {}
N 20 0 80 0 {}
N 290 0 320 0 {}
N 360 0 420 0 {}
N -50 60 290 60 {}
N -935 140 905 140 {}
C {devices/lab_wire.sym} -420 94 2 0 {name=l0 lab=vss}
C {devices/lab_wire.sym} 80 94 2 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 420 94 2 0 {name=l2 lab=vss}
C {devices/iopin.sym} -935 140 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 290 0 0 0 {name=p1 lab=nbias}
C {devices/opin.sym} 20 -60 0 0 {name=p2 lab=foldp}
C {devices/opin.sym} 360 -60 0 0 {name=p3 lab=foldn}
