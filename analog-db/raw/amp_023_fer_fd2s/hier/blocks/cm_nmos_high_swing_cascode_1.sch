v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_high_swing_cascode_1} -590 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 845 0 0 0 {name=MKA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmka_w l=x_dut_xmka_l m=x_dut_xmka_m}
C {devices/sg13_lv_nmos_np.sym} 665 0 0 1 {name=MKB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmkb_w l=x_dut_xmkb_l m=x_dut_xmkb_m}
C {devices/sg13_lv_nmos_np.sym} -550 0 0 1 {name=MNA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmna_w l=x_dut_xmna_l m=x_dut_xmna_m}
C {devices/sg13_lv_nmos_np.sym} -210 0 0 0 {name=MNB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb_w l=x_dut_xmnb_l m=x_dut_xmnb_m}
C {devices/sg13_lv_nmos_np.sym} 90 0 0 1 {name=MNCD model=sg13_lv_nmos spiceprefix=X w=x_dut_xmncd_w l=x_dut_xmncd_l m=x_dut_xmncd_m}
C {devices/sg13_lv_nmos_np.sym} 365 0 0 0 {name=MND1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnd1_w l=x_dut_xmnd1_l m=x_dut_xmnd1_m}
N -630 0 -630 94 {}
N -570 -90 -570 -30 {}
N -570 30 -570 90 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N -130 0 -130 94 {}
N 10 0 10 94 {}
N 70 -90 70 -30 {}
N 70 30 70 90 {}
N 110 -70 110 0 {}
N 345 -70 345 0 {}
N 385 -90 385 -30 {}
N 385 30 385 90 {}
N 445 0 445 94 {}
N 585 0 585 94 {}
N 645 -90 645 -30 {}
N 645 30 645 90 {}
N 685 0 685 60 {}
N 715 -60 715 0 {}
N 865 -90 865 -30 {}
N 865 30 865 90 {}
N 925 0 925 94 {}
N 70 -70 110 -70 {}
N 345 -70 385 -70 {}
N -630 0 -570 0 {}
N -530 0 -230 0 {}
N -190 0 -130 0 {}
N 10 0 70 0 {}
N 385 0 445 0 {}
N 585 0 645 0 {}
N 685 0 825 0 {}
N 865 0 925 0 {}
C {devices/lab_wire.sym} -570 -90 0 1 {name=l0 lab=o1a}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l1 lab=o1b}
C {devices/lab_wire.sym} 70 -90 0 1 {name=l2 lab=vcmfb}
C {devices/lab_wire.sym} 685 60 2 0 {name=l3 lab=vcmfb}
C {devices/lab_wire.sym} -470 0 0 1 {name=l4 lab=vcn}
C {devices/lab_wire.sym} 385 -90 0 1 {name=l5 lab=vcn}
C {devices/lab_wire.sym} 70 90 2 0 {name=l6 lab=vss}
C {devices/lab_wire.sym} 385 90 2 0 {name=l7 lab=vss}
C {devices/lab_wire.sym} 645 90 2 0 {name=l8 lab=vss}
C {devices/lab_wire.sym} 865 90 2 0 {name=l9 lab=vss}
C {devices/lab_wire.sym} -570 90 2 0 {name=l10 lab=x1a}
C {devices/lab_wire.sym} 865 -90 0 1 {name=l11 lab=x1a}
C {devices/lab_wire.sym} -190 90 2 0 {name=l12 lab=x1b}
C {devices/lab_wire.sym} 645 -90 0 1 {name=l13 lab=x1b}
C {devices/lab_wire.sym} 925 94 2 0 {name=l14 lab=vss}
C {devices/lab_wire.sym} 585 94 2 0 {name=l15 lab=vss}
C {devices/lab_wire.sym} -630 94 2 0 {name=l16 lab=vss}
C {devices/lab_wire.sym} -130 94 2 0 {name=l17 lab=vss}
C {devices/lab_wire.sym} 10 94 2 0 {name=l18 lab=vss}
C {devices/lab_wire.sym} 445 94 2 0 {name=l19 lab=vss}
C {devices/iopin.sym} 70 280 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 1200 -30 0 0 {name=p1 lab=o1a}
C {devices/opin.sym} 1200 90 0 0 {name=p2 lab=o1b}
C {devices/opin.sym} 1200 210 0 0 {name=p3 lab=vcmfb}
C {devices/opin.sym} 1200 330 0 0 {name=p4 lab=vcn}
