v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {tg_pair_cmos_rail_bulk_7} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=M1_S3_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s3_rrl_w l=x_dut_xm1_s3_rrl_l m=x_dut_xm1_s3_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M2_S3_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s3_rrl_w l=x_dut_xm2_s3_rrl_l m=x_dut_xm2_s3_rrl_m}
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
C {devices/lab_wire.sym} -90 0 0 1 {name=l0 lab=clk_phi_1}
C {devices/lab_wire.sym} 90 0 0 0 {name=l1 lab=clk_phi_2}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l2 lab=rrl__oa_inp}
C {devices/lab_wire.sym} -190 90 2 0 {name=l3 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -250 94 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l5 lab=vss}
C {devices/ipin.sym} -575 0 0 0 {name=p0 lab=clk_phi_1}
C {devices/ipin.sym} -575 120 0 0 {name=p1 lab=clk_phi_2}
C {devices/opin.sym} 575 -30 0 0 {name=p2 lab=rrl__oa_inp}
C {devices/opin.sym} 575 90 0 0 {name=p3 lab=rrl__oa_outn}
