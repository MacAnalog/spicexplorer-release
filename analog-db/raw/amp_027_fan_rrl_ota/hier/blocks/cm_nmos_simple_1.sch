v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_1} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -340 0 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 0 0 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 340 0 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
N -420 0 -420 94 {}
N -360 -60 -360 -30 {}
N -360 30 -360 140 {}
N -50 0 -50 60 {}
N 20 -60 20 -30 {}
N 20 30 20 140 {}
N 80 0 80 94 {}
N 320 -70 320 60 {}
N 360 -70 360 -30 {}
N 360 30 360 140 {}
N 420 0 420 94 {}
N 320 -70 360 -70 {}
N -420 0 -360 0 {}
N -320 0 -20 0 {}
N 20 0 80 0 {}
N 360 0 420 0 {}
N -50 60 320 60 {}
N -840 140 840 140 {}
C {devices/lab_wire.sym} -420 94 2 0 {name=l0 lab=vss}
C {devices/lab_wire.sym} 80 94 2 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 420 94 2 0 {name=l2 lab=vss}
C {devices/iopin.sym} -840 140 0 0 {name=p0 lab=vss}
C {devices/opin.sym} -360 -60 0 0 {name=p1 lab=csrc_n}
C {devices/opin.sym} 20 -60 0 0 {name=p2 lab=csrc_p}
C {devices/opin.sym} 360 -70 0 0 {name=p3 lab=cm_bias}
