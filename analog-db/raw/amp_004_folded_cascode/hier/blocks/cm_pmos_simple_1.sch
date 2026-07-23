v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 205 0 0 0 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l ng=x_dut_xm0_ng m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l ng=x_dut_xm11_ng m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l ng=x_dut_xm12_ng m=x_dut_xm12_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N -150 0 -150 60 {}
N -20 0 -20 70 {}
N 20 -60 20 -30 {}
N 20 30 20 70 {}
N 80 0 80 94 {}
N 225 -60 225 -30 {}
N 225 30 225 90 {}
N 285 0 285 94 {}
N -190 -60 225 -60 {}
N -250 0 -190 0 {}
N -150 0 -120 0 {}
N 20 0 80 0 {}
N 155 0 185 0 {}
N 225 0 285 0 {}
N -20 70 20 70 {}
C {devices/lab_wire.sym} -150 60 2 0 {name=l0 lab=ibias}
C {devices/lab_wire.sym} -20 0 0 0 {name=l1 lab=ibias}
C {devices/lab_wire.sym} 185 0 0 0 {name=l2 lab=ibias}
C {devices/lab_wire.sym} -190 90 2 0 {name=l3 lab=nbias}
C {devices/lab_wire.sym} 225 90 2 0 {name=l4 lab=tail}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l5 lab=vdd}
C {devices/lab_wire.sym} 285 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l8 lab=vdd}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 570 0 0 0 {name=p1 lab=ibias}
C {devices/opin.sym} 570 120 0 0 {name=p2 lab=nbias}
C {devices/opin.sym} 570 240 0 0 {name=p3 lab=tail}
