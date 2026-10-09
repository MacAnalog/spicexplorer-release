v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_2} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=M2_CMFB_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_cmfb_s1_w l=x_dut_xm2_cmfb_s1_l m=x_dut_xm2_cmfb_s1_m}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=M6_CMFB_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_cmfb_s1_w l=x_dut_xm6_cmfb_s1_l m=x_dut_xm6_cmfb_s1_m}
N -250 0 -250 94 {}
N -190 -60 -190 -30 {}
N -190 30 -190 140 {}
N 150 -70 150 0 {}
N 190 -70 190 -30 {}
N 190 30 190 140 {}
N 250 0 250 94 {}
N 150 -70 190 -70 {}
N -250 0 -190 0 {}
N -180 0 150 0 {}
N 190 0 250 0 {}
N -840 140 840 140 {}
C {devices/lab_wire.sym} -250 94 2 0 {name=l0 lab=vss}
C {devices/lab_wire.sym} 250 94 2 0 {name=l1 lab=vss}
C {devices/iopin.sym} -840 140 0 0 {name=p0 lab=vss}
C {devices/opin.sym} -190 -60 0 0 {name=p1 lab=vb4_ctl}
C {devices/opin.sym} 190 -70 0 0 {name=p2 lab=cmfb_s1__mirr}
