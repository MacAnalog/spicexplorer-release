v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {tg_pair_cmos_rail_bulk_2} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=M18_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_main_w l=x_dut_xm18_main_l m=x_dut_xm18_main_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M19_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_main_w l=x_dut_xm19_main_l m=x_dut_xm19_main_m}
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
C {devices/lab_wire.sym} 90 0 0 0 {name=l0 lab=clk_chout}
C {devices/lab_wire.sym} -90 0 0 1 {name=l1 lab=clk_chout_not}
C {devices/lab_wire.sym} -190 90 2 0 {name=l2 lab=main__g2_p}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l3 lab=out1_p}
C {devices/lab_wire.sym} -250 94 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l5 lab=vss}
C {devices/ipin.sym} -565 0 0 0 {name=p0 lab=clk_chout_not}
C {devices/ipin.sym} -565 120 0 0 {name=p1 lab=clk_chout}
C {devices/opin.sym} 565 -30 0 0 {name=p2 lab=out1_p}
C {devices/opin.sym} 565 90 0 0 {name=p3 lab=main__g2_p}
