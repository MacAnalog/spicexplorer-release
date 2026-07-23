v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {inv_cmos_stack_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=MOBN1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmobn1_w l=x_dut_xmobn1_l m=x_dut_xmobn1_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=MOBP1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmobp1_w l=x_dut_xmobp1_l m=x_dut_xmobp1_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 190 -90 190 -30 {}
N 190 30 190 90 {}
N 250 0 250 94 {}
N -250 0 -190 0 {}
N -150 0 150 0 {}
N 190 0 250 0 {}
C {devices/lab_wire.sym} -90 0 0 1 {name=l0 lab=lm}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l1 lab=vdd}
C {devices/lab_wire.sym} -190 90 2 0 {name=l2 lab=voutp}
C {devices/lab_wire.sym} 190 -90 0 1 {name=l3 lab=voutp}
C {devices/lab_wire.sym} 190 90 2 0 {name=l4 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l6 lab=vss}
C {devices/ipin.sym} -540 0 0 0 {name=p0 lab=lm}
C {devices/iopin.sym} -190 280 0 0 {name=p1 lab=vdd}
C {devices/iopin.sym} 190 280 0 0 {name=p2 lab=vss}
C {devices/opin.sym} 540 -30 0 0 {name=p3 lab=voutp}
