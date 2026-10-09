v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_3} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=MA model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=MB model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
N -250 0 -250 94 {}
N -190 -70 -190 -30 {}
N -190 30 -190 140 {}
N -150 -70 -150 0 {}
N 120 -60 120 0 {}
N 190 -60 190 -30 {}
N 190 30 190 140 {}
N 250 0 250 94 {}
N -190 -70 -150 -70 {}
N -190 -60 120 -60 {}
N -250 0 -190 0 {}
N 120 0 150 0 {}
N 190 0 250 0 {}
N -565 140 565 140 {}
C {devices/lab_wire.sym} -250 94 2 0 {name=l0 lab=vss}
C {devices/lab_wire.sym} 250 94 2 0 {name=l1 lab=vss}
C {devices/iopin.sym} -565 140 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 120 -60 0 0 {name=p1 lab=x1}
C {devices/opin.sym} 190 -60 0 0 {name=p2 lab=y}
