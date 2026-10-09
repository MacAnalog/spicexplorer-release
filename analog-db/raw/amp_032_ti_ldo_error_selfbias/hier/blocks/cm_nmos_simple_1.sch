v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_1} -550 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -510 0 0 1 {name=MB0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=MBC model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbc_w l=x_dut_xmbc_l m=x_dut_xmbc_m}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=MBF model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbf_w l=x_dut_xmbf_l}
C {devices/sg13_lv_nmos_np.sym} 510 0 0 0 {name=MBO model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbo_w l=x_dut_xmbo_l m=x_dut_xmbo_m}
N -590 0 -590 94 {}
N -530 -70 -530 -30 {}
N -530 30 -530 140 {}
N -490 -70 -490 0 {}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 140 {}
N -120 -60 -120 0 {}
N 120 0 120 60 {}
N 190 -60 190 -30 {}
N 190 30 190 140 {}
N 250 0 250 94 {}
N 460 0 460 60 {}
N 530 -60 530 -30 {}
N 530 30 530 140 {}
N 590 0 590 94 {}
N -530 -70 -490 -70 {}
N -490 -60 -120 -60 {}
N -590 0 -530 0 {}
N -250 0 -190 0 {}
N -150 0 150 0 {}
N 190 0 250 0 {}
N 460 0 490 0 {}
N 530 0 590 0 {}
N 120 60 460 60 {}
N -920 140 1010 140 {}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l0 lab=tail}
C {devices/lab_wire.sym} -590 94 2 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l2 lab=vss}
C {devices/lab_wire.sym} 250 94 2 0 {name=l3 lab=vss}
C {devices/lab_wire.sym} 590 94 2 0 {name=l4 lab=vss}
C {devices/iopin.sym} -920 140 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 460 0 0 0 {name=p1 lab=ibias}
C {devices/opin.sym} 190 -60 0 0 {name=p2 lab=nlev}
C {devices/opin.sym} 530 -60 0 0 {name=p3 lab=vout}
C {devices/opin.sym} 1150 -30 0 0 {name=p4 lab=tail}
