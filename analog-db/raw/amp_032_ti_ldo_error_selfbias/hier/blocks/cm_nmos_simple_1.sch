v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 650 0 0 0 {name=MB0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} 375 0 0 0 {name=MBC model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbc_w l=x_dut_xmbc_l m=x_dut_xmbc_m}
C {devices/sg13_lv_nmos_np.sym} 105 0 0 1 {name=MBF model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbf_w l=x_dut_xmbf_l}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=MBO model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbo_w l=x_dut_xmbo_l m=x_dut_xmbo_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 25 0 25 94 {}
N 85 -90 85 -30 {}
N 85 30 85 60 {}
N 395 -90 395 -30 {}
N 395 30 395 60 {}
N 455 0 455 94 {}
N 630 -70 630 0 {}
N 670 -90 670 -30 {}
N 670 30 670 60 {}
N 730 0 730 94 {}
N 630 -70 670 -70 {}
N -250 0 -190 0 {}
N -150 0 -120 0 {}
N 25 0 85 0 {}
N 125 0 355 0 {}
N 395 0 455 0 {}
N 670 0 730 0 {}
N -190 60 670 60 {}
C {devices/lab_wire.sym} -150 0 0 0 {name=l0 lab=ibias}
C {devices/lab_wire.sym} 185 0 0 1 {name=l1 lab=ibias}
C {devices/lab_wire.sym} 670 -90 0 1 {name=l2 lab=ibias}
C {devices/lab_wire.sym} 85 -90 0 1 {name=l3 lab=nlev}
C {devices/lab_wire.sym} 395 -90 0 1 {name=l4 lab=tail}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l5 lab=vout}
C {devices/lab_wire.sym} -190 90 2 0 {name=l6 lab=vss}
C {devices/lab_wire.sym} 730 94 2 0 {name=l7 lab=vss}
C {devices/lab_wire.sym} 455 94 2 0 {name=l8 lab=vss}
C {devices/lab_wire.sym} 25 94 2 0 {name=l9 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l10 lab=vss}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 1005 -30 0 0 {name=p1 lab=vout}
C {devices/opin.sym} 1005 90 0 0 {name=p2 lab=nlev}
C {devices/opin.sym} 1005 210 0 0 {name=p3 lab=tail}
C {devices/opin.sym} 1005 330 0 0 {name=p4 lab=ibias}
