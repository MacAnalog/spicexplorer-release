v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_nmos_simple_2} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=MRA_1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_1_w l=x_dut_xmra_1_l}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=MRA_2 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_2_w l=x_dut_xmra_2_l}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 190 -90 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 90 0 150 0 {}
N 190 0 250 0 {}
N -190 60 190 60 {}
C {devices/lab_wire.sym} 190 -90 0 1 {name=l0 lab=ra_na}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l1 lab=ra_nb}
C {devices/lab_wire.sym} -190 90 2 0 {name=l2 lab=ra_tail}
C {devices/lab_wire.sym} 90 0 0 0 {name=l3 lab=v_ref_fb}
C {devices/lab_wire.sym} -90 0 0 1 {name=l4 lab=vref}
C {devices/lab_wire.sym} 250 94 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l6 lab=vss}
C {devices/ipin.sym} -540 0 0 0 {name=p0 lab=vref}
C {devices/ipin.sym} -540 120 0 0 {name=p1 lab=v_ref_fb}
C {devices/iopin.sym} -190 280 0 0 {name=p2 lab=ra_tail}
C {devices/opin.sym} 540 -30 0 0 {name=p3 lab=ra_nb}
C {devices/opin.sym} 540 90 0 0 {name=p4 lab=ra_na}
