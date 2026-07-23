v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_nmos_simple_4} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=M30 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm30_w l=x_dut_xm30_l m=x_dut_xm30_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 190 -90 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 90 0 150 0 {}
N 190 0 250 0 {}
N -190 60 190 60 {}
C {devices/lab_wire.sym} 90 0 0 0 {name=l0 lab=clk_chfb}
C {devices/lab_wire.sym} -90 0 0 1 {name=l1 lab=clk_chpf}
C {devices/lab_wire.sym} 190 -90 0 1 {name=l2 lab=fbch_n}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l3 lab=pfch_n}
C {devices/lab_wire.sym} -190 90 2 0 {name=l4 lab=voutn}
C {devices/lab_wire.sym} 250 94 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l6 lab=vss}
C {devices/ipin.sym} -525 0 0 0 {name=p0 lab=clk_chpf}
C {devices/ipin.sym} -525 120 0 0 {name=p1 lab=clk_chfb}
C {devices/iopin.sym} -190 280 0 0 {name=p2 lab=voutn}
C {devices/opin.sym} 525 -30 0 0 {name=p3 lab=pfch_n}
C {devices/opin.sym} 525 90 0 0 {name=p4 lab=fbch_n}
