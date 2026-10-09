v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_pmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=M1A model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M2A model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
N -250 0 -250 94 {}
N -190 -60 -190 -30 {}
N -190 30 -190 60 {}
N 190 -60 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N -600 -140 600 -140 {}
N -190 -60 190 -60 {}
N -250 0 -190 0 {}
N -150 0 -120 0 {}
N 60 0 150 0 {}
N 190 0 250 0 {}
C {devices/lab_wire.sym} -600 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l1 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l2 lab=vdd}
C {devices/ipin.sym} -120 0 0 0 {name=p0 lab=vref}
C {devices/ipin.sym} 60 0 0 0 {name=p1 lab=fb}
C {devices/iopin.sym} -190 -60 0 0 {name=p2 lab=ea_tail}
C {devices/opin.sym} -190 60 0 0 {name=p3 lab=ea_o1}
C {devices/opin.sym} 190 60 0 0 {name=p4 lab=ea_n}
