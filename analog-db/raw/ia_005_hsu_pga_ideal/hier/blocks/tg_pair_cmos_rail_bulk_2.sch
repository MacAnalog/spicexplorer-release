v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {tg_pair_cmos_rail_bulk_2} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=MA10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xma10_w l=x_dut_xma10_l m=x_dut_xma10_m}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=MA9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xma9_w l=x_dut_xma9_l m=x_dut_xma9_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 190 -60 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N -190 -60 190 -60 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 90 0 150 0 {}
N 190 0 250 0 {}
N -190 60 190 60 {}
C {devices/lab_wire.sym} -90 0 0 1 {name=l0 lab=V_D2}
C {devices/lab_wire.sym} 90 0 0 0 {name=l1 lab=V_D2_NOT}
C {devices/lab_wire.sym} -190 90 2 0 {name=l2 lab=bota2}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l3 lab=vinp}
C {devices/lab_wire.sym} 250 94 2 0 {name=l4 lab=VDD}
C {devices/lab_wire.sym} -250 94 2 0 {name=l5 lab=VSS}
C {devices/ipin.sym} -525 0 0 0 {name=p0 lab=V_D2}
C {devices/ipin.sym} -525 120 0 0 {name=p1 lab=V_D2_NOT}
C {devices/opin.sym} 535 -30 0 0 {name=p2 lab=vinp}
C {devices/opin.sym} 535 90 0 0 {name=p3 lab=bota2}
