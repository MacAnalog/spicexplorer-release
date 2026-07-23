v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_low_voltage_cascode_1} -550 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 365 0 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l ng=x_dut_xm10_ng m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 570 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l ng=x_dut_xm7_ng m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l ng=x_dut_xm8_ng m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} -315 0 0 1 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l ng=x_dut_xm9_ng m=x_dut_xm9_m}
N -590 0 -590 94 {}
N -530 -90 -530 -30 {}
N -530 30 -530 90 {}
N -490 0 -490 60 {}
N -395 0 -395 94 {}
N -335 -90 -335 -30 {}
N -335 30 -335 90 {}
N 385 -90 385 -30 {}
N 385 30 385 90 {}
N 445 0 445 94 {}
N 550 -60 550 0 {}
N 590 -90 590 -30 {}
N 590 30 590 90 {}
N 650 0 650 94 {}
N -590 0 -530 0 {}
N -490 0 -460 0 {}
N -395 0 -335 0 {}
N -295 0 345 0 {}
N 385 0 445 0 {}
N 520 0 550 0 {}
N 590 0 650 0 {}
C {devices/lab_wire.sym} -235 0 0 1 {name=l0 lab=cascp}
C {devices/lab_wire.sym} 590 90 2 0 {name=l1 lab=cascp}
C {devices/lab_wire.sym} -530 -90 0 1 {name=l2 lab=s10}
C {devices/lab_wire.sym} 385 90 2 0 {name=l3 lab=s10}
C {devices/lab_wire.sym} -335 90 2 0 {name=l4 lab=s9}
C {devices/lab_wire.sym} 590 -90 0 1 {name=l5 lab=s9}
C {devices/lab_wire.sym} -490 60 2 0 {name=l6 lab=vb2}
C {devices/lab_wire.sym} 550 -60 0 1 {name=l7 lab=vb2}
C {devices/lab_wire.sym} -335 -90 0 1 {name=l8 lab=vdd}
C {devices/lab_wire.sym} 385 -90 0 1 {name=l9 lab=vdd}
C {devices/lab_wire.sym} -530 90 2 0 {name=l10 lab=vout}
C {devices/lab_wire.sym} 445 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} 650 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -590 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} -395 94 2 0 {name=l14 lab=vdd}
C {devices/ipin.sym} -875 0 0 0 {name=p0 lab=vb2}
C {devices/iopin.sym} -335 280 0 0 {name=p1 lab=vdd}
C {devices/opin.sym} 935 0 0 0 {name=p2 lab=cascp}
C {devices/opin.sym} 935 120 0 0 {name=p3 lab=vout}
