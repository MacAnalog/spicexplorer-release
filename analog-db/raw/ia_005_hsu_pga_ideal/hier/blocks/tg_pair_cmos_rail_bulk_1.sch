v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {tg_pair_cmos_rail_bulk_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=MA1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xma1_w l=x_dut_xma1_l m=x_dut_xma1_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=MA2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xma2_w l=x_dut_xma2_l m=x_dut_xma2_m}
N -250 0 -250 94 {}
N -190 -60 -190 -30 {}
N -190 30 -190 60 {}
N 190 -60 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N -670 -140 670 -140 {}
N -190 -60 190 -60 {}
N -250 0 -190 0 {}
N -150 0 -120 0 {}
N 60 0 150 0 {}
N 190 0 250 0 {}
N -190 60 190 60 {}
N -670 140 670 140 {}
C {devices/lab_wire.sym} -670 -140 0 0 {name=l0 lab=VDD}
C {devices/lab_wire.sym} -670 140 0 0 {name=l1 lab=VSS}
C {devices/lab_wire.sym} -250 94 2 0 {name=l2 lab=VDD}
C {devices/lab_wire.sym} 250 94 2 0 {name=l3 lab=VSS}
C {devices/ipin.sym} -120 0 0 0 {name=p0 lab=V_D0_NOT}
C {devices/ipin.sym} 60 0 0 0 {name=p1 lab=V_D0}
C {devices/opin.sym} 190 -60 0 0 {name=p2 lab=vinp}
C {devices/opin.sym} 190 60 0 0 {name=p3 lab=bota0}
