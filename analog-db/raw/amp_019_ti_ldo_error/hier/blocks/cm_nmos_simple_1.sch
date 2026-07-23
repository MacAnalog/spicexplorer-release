v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 810 0 0 0 {name=MB0 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} 565 0 0 0 {name=MBC model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbc_w l=x_dut_xmbc_l m=x_dut_xmbc_m}
C {devices/sg13_lv_nmos_np.sym} 320 0 0 0 {name=MBE model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbe_w l=x_dut_xmbe_l}
C {devices/sg13_lv_nmos_np.sym} 75 0 0 1 {name=MBF model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbf_w l=x_dut_xmbf_l}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=MBO model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbo_w l=x_dut_xmbo_l m=x_dut_xmbo_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N -5 0 -5 94 {}
N 55 -90 55 -30 {}
N 55 30 55 60 {}
N 340 -90 340 -30 {}
N 340 30 340 60 {}
N 400 0 400 94 {}
N 545 -60 545 0 {}
N 585 -90 585 -30 {}
N 585 30 585 60 {}
N 645 0 645 94 {}
N 790 -70 790 0 {}
N 830 -90 830 -30 {}
N 830 30 830 60 {}
N 890 0 890 94 {}
N 790 -70 830 -70 {}
N -250 0 -190 0 {}
N -150 0 -120 0 {}
N -5 0 55 0 {}
N 95 0 300 0 {}
N 340 0 400 0 {}
N 515 0 545 0 {}
N 585 0 645 0 {}
N 830 0 890 0 {}
N -190 60 830 60 {}
C {devices/lab_wire.sym} -150 0 0 0 {name=l0 lab=ibias}
C {devices/lab_wire.sym} 155 0 0 1 {name=l1 lab=ibias}
C {devices/lab_wire.sym} 545 -60 0 1 {name=l2 lab=ibias}
C {devices/lab_wire.sym} 830 -90 0 1 {name=l3 lab=ibias}
C {devices/lab_wire.sym} 340 -90 0 1 {name=l4 lab=ne}
C {devices/lab_wire.sym} 55 -90 0 1 {name=l5 lab=nlev}
C {devices/lab_wire.sym} 585 -90 0 1 {name=l6 lab=tail}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l7 lab=vout}
C {devices/lab_wire.sym} -190 90 2 0 {name=l8 lab=vss}
C {devices/lab_wire.sym} 890 94 2 0 {name=l9 lab=vss}
C {devices/lab_wire.sym} 645 94 2 0 {name=l10 lab=vss}
C {devices/lab_wire.sym} 400 94 2 0 {name=l11 lab=vss}
C {devices/lab_wire.sym} -5 94 2 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l13 lab=vss}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 1165 -30 0 0 {name=p1 lab=vout}
C {devices/opin.sym} 1165 90 0 0 {name=p2 lab=nlev}
C {devices/opin.sym} 1165 210 0 0 {name=p3 lab=ne}
C {devices/opin.sym} 1165 330 0 0 {name=p4 lab=tail}
C {devices/opin.sym} 1165 450 0 0 {name=p5 lab=ibias}
