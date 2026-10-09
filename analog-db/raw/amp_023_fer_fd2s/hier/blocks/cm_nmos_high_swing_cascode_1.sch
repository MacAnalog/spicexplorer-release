v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_high_swing_cascode_1} -550 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -510 260 0 1 {name=MKA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmka_w l=x_dut_xmka_l m=x_dut_xmka_m}
C {devices/sg13_lv_nmos_np.sym} -170 260 0 1 {name=MKB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmkb_w l=x_dut_xmkb_l m=x_dut_xmkb_m}
C {devices/sg13_lv_nmos_np.sym} -510 0 0 1 {name=MNA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmna_w l=x_dut_xmna_l m=x_dut_xmna_m}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=MNB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb_w l=x_dut_xmnb_l m=x_dut_xmnb_m}
C {devices/sg13_lv_nmos_np.sym} 170 260 0 0 {name=MNCD model=sg13_lv_nmos spiceprefix=X w=x_dut_xmncd_w l=x_dut_xmncd_l m=x_dut_xmncd_m}
C {devices/sg13_lv_nmos_np.sym} 510 260 0 0 {name=MND1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnd1_w l=x_dut_xmnd1_l m=x_dut_xmnd1_m}
N -590 0 -590 94 {}
N -590 260 -590 354 {}
N -530 -60 -530 -30 {}
N -530 30 -530 230 {}
N -530 290 -530 400 {}
N -460 -120 -460 0 {}
N -460 260 -460 320 {}
N -250 0 -250 94 {}
N -250 260 -250 354 {}
N -190 -60 -190 -30 {}
N -190 30 -190 230 {}
N -190 290 -190 400 {}
N -120 -120 -120 0 {}
N -120 260 -120 320 {}
N 150 190 150 260 {}
N 190 190 190 230 {}
N 190 290 190 400 {}
N 250 260 250 354 {}
N 490 190 490 260 {}
N 530 0 530 230 {}
N 530 290 530 400 {}
N 590 260 590 354 {}
N -460 -120 -120 -120 {}
N -590 0 -530 0 {}
N -490 0 -460 0 {}
N -250 0 -190 0 {}
N -150 0 530 0 {}
N 150 190 190 190 {}
N 490 190 530 190 {}
N -590 260 -530 260 {}
N -490 260 -460 260 {}
N -250 260 -190 260 {}
N -180 260 150 260 {}
N 190 260 250 260 {}
N 530 260 590 260 {}
N -460 320 -120 320 {}
N -1010 400 1035 400 {}
C {devices/lab_wire.sym} -530 90 2 0 {name=l0 lab=x1a}
C {devices/lab_wire.sym} -190 90 2 0 {name=l1 lab=x1b}
C {devices/lab_wire.sym} -590 354 2 0 {name=l2 lab=vss}
C {devices/lab_wire.sym} -250 354 2 0 {name=l3 lab=vss}
C {devices/lab_wire.sym} -590 94 2 0 {name=l4 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} 250 354 2 0 {name=l6 lab=vss}
C {devices/lab_wire.sym} 590 354 2 0 {name=l7 lab=vss}
C {devices/iopin.sym} -1010 400 0 0 {name=p0 lab=vss}
C {devices/opin.sym} -530 -60 0 0 {name=p1 lab=o1a}
C {devices/opin.sym} -190 -60 0 0 {name=p2 lab=o1b}
C {devices/opin.sym} 530 0 0 0 {name=p3 lab=vcn}
C {devices/opin.sym} 190 190 0 0 {name=p4 lab=vcmfb}
