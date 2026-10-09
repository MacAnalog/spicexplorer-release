v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_1} -720 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -680 0 0 1 {name=MB0 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} -340 0 0 1 {name=MBC model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbc_w l=x_dut_xmbc_l m=x_dut_xmbc_m}
C {devices/sg13_lv_nmos_np.sym} 0 0 0 0 {name=MBE model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbe_w l=x_dut_xmbe_l}
C {devices/sg13_lv_nmos_np.sym} 340 0 0 0 {name=MBF model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbf_w l=x_dut_xmbf_l}
C {devices/sg13_lv_nmos_np.sym} 680 0 0 0 {name=MBO model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbo_w l=x_dut_xmbo_l m=x_dut_xmbo_m}
N -760 0 -760 94 {}
N -700 -90 -700 -30 {}
N -700 30 -700 140 {}
N -660 -70 -660 0 {}
N -420 0 -420 94 {}
N -360 -90 -360 -30 {}
N -360 30 -360 140 {}
N -290 -60 -290 0 {}
N -50 0 -50 60 {}
N 20 -60 20 -30 {}
N 20 30 20 140 {}
N 80 0 80 94 {}
N 290 0 290 60 {}
N 360 -60 360 -30 {}
N 360 30 360 140 {}
N 420 0 420 94 {}
N 700 -60 700 -30 {}
N 700 30 700 140 {}
N 760 0 760 94 {}
N -700 -70 -660 -70 {}
N -660 -60 -290 -60 {}
N -760 0 -700 0 {}
N -420 0 -360 0 {}
N -320 0 -20 0 {}
N 20 0 80 0 {}
N 290 0 320 0 {}
N 360 0 420 0 {}
N 630 0 660 0 {}
N 700 0 760 0 {}
N -50 60 290 60 {}
N -1090 140 1180 140 {}
C {devices/lab_wire.sym} -700 -90 0 1 {name=l0 lab=ibias}
C {devices/lab_wire.sym} -360 -90 0 1 {name=l1 lab=tail}
C {devices/lab_wire.sym} -760 94 2 0 {name=l2 lab=vss}
C {devices/lab_wire.sym} -420 94 2 0 {name=l3 lab=vss}
C {devices/lab_wire.sym} 80 94 2 0 {name=l4 lab=vss}
C {devices/lab_wire.sym} 420 94 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} 760 94 2 0 {name=l6 lab=vss}
C {devices/iopin.sym} -1090 140 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 630 0 0 0 {name=p1 lab=ibias}
C {devices/opin.sym} 20 -60 0 0 {name=p2 lab=ne}
C {devices/opin.sym} 360 -60 0 0 {name=p3 lab=nlev}
C {devices/opin.sym} 700 -60 0 0 {name=p4 lab=vout}
C {devices/opin.sym} 1320 -30 0 0 {name=p5 lab=tail}
