v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {tg_pair_cmos_rail_bulk_10} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=M1_S6_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s6_rrl_w l=x_dut_xm1_s6_rrl_l m=x_dut_xm1_s6_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M2_S6_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s6_rrl_w l=x_dut_xm2_s6_rrl_l m=x_dut_xm2_s6_rrl_m}
N -250 0 -250 94 {}
N -190 -60 -190 -30 {}
N -190 30 -190 60 {}
N 190 -60 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N -815 -140 815 -140 {}
N -190 -60 190 -60 {}
N -250 0 -190 0 {}
N -150 0 -120 0 {}
N 60 0 150 0 {}
N 190 0 250 0 {}
N -190 60 190 60 {}
N -815 140 815 140 {}
C {devices/lab_wire.sym} -815 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -815 140 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l2 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l3 lab=vss}
C {devices/ipin.sym} -120 0 0 0 {name=p0 lab=clk_phi_2}
C {devices/ipin.sym} 60 0 0 0 {name=p1 lab=clk_phi_1}
C {devices/opin.sym} 190 -60 0 0 {name=p2 lab=rrl__oa_outp}
C {devices/opin.sym} 190 60 0 0 {name=p3 lab=rrl__int_n}
