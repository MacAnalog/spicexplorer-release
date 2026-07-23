v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_pmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 190 -60 190 -30 {}
N 190 30 190 90 {}
N 250 0 250 94 {}
N -190 -60 190 -60 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 90 0 150 0 {}
N 190 0 250 0 {}
C {devices/lab_wire.sym} 190 90 2 0 {name=l0 lab=a}
C {devices/lab_wire.sym} -190 90 2 0 {name=l1 lab=b}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l2 lab=c}
C {devices/lab_wire.sym} 90 0 0 0 {name=l3 lab=vinn}
C {devices/lab_wire.sym} -90 0 0 1 {name=l4 lab=vinp}
C {devices/lab_wire.sym} 250 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l6 lab=vdd}
C {devices/ipin.sym} -520 0 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -520 120 0 0 {name=p1 lab=vinn}
C {devices/iopin.sym} -190 280 0 0 {name=p2 lab=c}
C {devices/opin.sym} 520 30 0 0 {name=p3 lab=b}
C {devices/opin.sym} 520 150 0 0 {name=p4 lab=a}
