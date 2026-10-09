v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_low_voltage_cascode_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l ng=x_dut_xm10_ng m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 170 260 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l ng=x_dut_xm7_ng m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} -170 260 0 1 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l ng=x_dut_xm8_ng m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l ng=x_dut_xm9_ng m=x_dut_xm9_m}
N -250 0 -250 94 {}
N -250 260 -250 354 {}
N -190 -140 -190 -30 {}
N -190 30 -190 230 {}
N -190 290 -190 320 {}
N 60 0 60 320 {}
N 190 -140 190 -30 {}
N 190 30 190 230 {}
N 190 290 190 320 {}
N 250 0 250 94 {}
N 250 260 250 354 {}
N -765 -140 735 -140 {}
N -250 0 -190 0 {}
N -150 0 150 0 {}
N 190 0 250 0 {}
N -250 260 -190 260 {}
N -150 260 150 260 {}
N 190 260 250 260 {}
N 60 320 190 320 {}
C {devices/lab_wire.sym} -190 90 2 0 {name=l0 lab=s10}
C {devices/lab_wire.sym} 190 90 2 0 {name=l1 lab=s9}
C {devices/lab_wire.sym} -250 94 2 0 {name=l2 lab=vdd}
C {devices/lab_wire.sym} 250 354 2 0 {name=l3 lab=vdd}
C {devices/lab_wire.sym} -250 354 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l5 lab=vdd}
C {devices/ipin.sym} -120 260 0 0 {name=p0 lab=vb2}
C {devices/iopin.sym} -765 -140 0 0 {name=p1 lab=vdd}
C {devices/opin.sym} 190 320 0 0 {name=p2 lab=cascp}
C {devices/opin.sym} -190 320 0 0 {name=p3 lab=vout}
