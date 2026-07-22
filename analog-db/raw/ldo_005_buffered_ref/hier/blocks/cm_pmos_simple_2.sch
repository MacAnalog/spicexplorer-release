v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_2} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 70 {}
N -150 0 -150 70 {}
N 120 0 120 60 {}
N 190 -60 190 -30 {}
N 190 30 190 90 {}
N 250 0 250 94 {}
N -190 -60 190 -60 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 120 0 150 0 {}
N 190 0 250 0 {}
N -190 60 120 60 {}
N -190 70 -150 70 {}
C {devices/lab_wire.sym} 190 90 2 0 {name=l0 lab=egate}
C {devices/lab_wire.sym} -90 0 0 1 {name=l1 lab=noutm}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l2 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l3 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l4 lab=vdd}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 525 0 0 0 {name=p1 lab=noutm}
C {devices/opin.sym} 525 120 0 0 {name=p2 lab=egate}
