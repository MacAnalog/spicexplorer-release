v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_pmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=M57 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm57_w l=x_dut_xm57_l m=x_dut_xm57_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M58 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm58_w l=x_dut_xm58_l m=x_dut_xm58_m}
N -250 0 -250 94 {}
N -190 -60 -190 -30 {}
N -190 30 -190 60 {}
N 190 -60 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N -190 -60 190 -60 {}
N -250 0 -190 0 {}
N -150 0 -120 0 {}
N 60 0 150 0 {}
N 190 0 250 0 {}
C {devices/lab_wire.sym} 250 94 2 0 {name=l0 lab=net1}
C {devices/lab_wire.sym} -250 94 2 0 {name=l1 lab=net1}
C {devices/ipin.sym} -120 0 0 0 {name=p0 lab=VINP}
C {devices/ipin.sym} 60 0 0 0 {name=p1 lab=VINN}
C {devices/iopin.sym} -190 -60 0 0 {name=p2 lab=net1}
C {devices/opin.sym} -190 60 0 0 {name=p3 lab=net049}
C {devices/opin.sym} 190 60 0 0 {name=p4 lab=net043}
