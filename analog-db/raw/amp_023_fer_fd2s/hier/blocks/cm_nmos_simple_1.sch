v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_1} -720 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -680 0 0 1 {name=MB1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb1_w l=x_dut_xmb1_l m=x_dut_xmb1_m}
C {devices/sg13_lv_nmos_np.sym} -340 0 0 1 {name=MB2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb2_w l=x_dut_xmb2_l m=x_dut_xmb2_m}
C {devices/sg13_lv_nmos_np.sym} 0 0 0 0 {name=MBD model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbd_w l=x_dut_xmbd_l m=x_dut_xmbd_m}
C {devices/sg13_lv_nmos_np.sym} 340 0 0 0 {name=MEAT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmeat_w l=x_dut_xmeat_l m=x_dut_xmeat_m}
C {devices/sg13_lv_nmos_np.sym} 680 0 0 0 {name=MT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmt_w l=x_dut_xmt_l m=x_dut_xmt_m}
N -760 0 -760 94 {}
N -700 -60 -700 -30 {}
N -700 30 -700 140 {}
N -630 0 -630 60 {}
N -420 0 -420 94 {}
N -360 -60 -360 -30 {}
N -360 30 -360 140 {}
N -290 0 -290 60 {}
N -20 -70 -20 0 {}
N 20 -90 20 -60 {}
N 20 -60 20 -30 {}
N 20 30 20 140 {}
N 80 0 80 94 {}
N 290 -60 290 0 {}
N 360 -60 360 -30 {}
N 360 30 360 140 {}
N 420 0 420 94 {}
N 700 -60 700 -30 {}
N 700 30 700 140 {}
N 760 0 760 94 {}
N -20 -70 20 -70 {}
N -20 -60 290 -60 {}
N -760 0 -700 0 {}
N -660 0 -630 0 {}
N -420 0 -360 0 {}
N -350 0 -20 0 {}
N 20 0 80 0 {}
N 290 0 320 0 {}
N 360 0 420 0 {}
N 630 0 660 0 {}
N 700 0 760 0 {}
N -630 60 -290 60 {}
N -1180 140 1155 140 {}
C {devices/lab_wire.sym} 20 -90 0 1 {name=l0 lab=ibias}
C {devices/lab_wire.sym} -760 94 2 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -420 94 2 0 {name=l2 lab=vss}
C {devices/lab_wire.sym} 80 94 2 0 {name=l3 lab=vss}
C {devices/lab_wire.sym} 420 94 2 0 {name=l4 lab=vss}
C {devices/lab_wire.sym} 760 94 2 0 {name=l5 lab=vss}
C {devices/iopin.sym} -1180 140 0 0 {name=p0 lab=vss}
C {devices/opin.sym} -700 -60 0 0 {name=p1 lab=vbp}
C {devices/opin.sym} -360 -60 0 0 {name=p2 lab=vcp}
C {devices/opin.sym} 630 0 0 0 {name=p3 lab=ibias}
C {devices/opin.sym} 360 -60 0 0 {name=p4 lab=eatail}
C {devices/opin.sym} 700 -60 0 0 {name=p5 lab=tail}
