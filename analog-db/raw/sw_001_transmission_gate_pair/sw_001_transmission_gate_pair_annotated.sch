v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sw_001_transmission_gate_pair} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
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
C {devices/lab_wire.sym} -190 -90 0 1 {name=l0 lab=port_a}
C {devices/lab_wire.sym} -190 90 2 0 {name=l1 lab=port_b}
C {devices/lab_wire.sym} 90 0 0 0 {name=l2 lab=vctl}
C {devices/lab_wire.sym} -90 0 0 1 {name=l3 lab=vctl_not}
C {devices/lab_wire.sym} -250 94 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l5 lab=vss}
C {devices/ipin.sym} -520 0 0 0 {name=p0 lab=vctl_not}
C {devices/ipin.sym} -520 120 0 0 {name=p1 lab=vctl}
C {devices/opin.sym} 520 -30 0 0 {name=p2 lab=port_a}
C {devices/opin.sym} 520 90 0 0 {name=p3 lab=port_b}
B 8 -358 -78 358 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -358 -96 0 0 0.3 0.3 {layer=8}
