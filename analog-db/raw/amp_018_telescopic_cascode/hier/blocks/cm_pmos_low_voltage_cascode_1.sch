v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_low_voltage_cascode_1} -550 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 350 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=M3C model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3c_w l=x_dut_xm3c_l m=x_dut_xm3c_m}
C {devices/sg13_lv_pmos_np.sym} -330 0 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 530 0 0 0 {name=M4C model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4c_w l=x_dut_xm4c_l m=x_dut_xm4c_m}
N -590 0 -590 94 {}
N -530 -90 -530 -30 {}
N -530 30 -530 90 {}
N -490 0 -490 60 {}
N -410 0 -410 94 {}
N -350 -90 -350 -30 {}
N -350 30 -350 90 {}
N 370 -90 370 -30 {}
N 370 30 370 90 {}
N 430 0 430 94 {}
N 510 -60 510 0 {}
N 550 -90 550 -30 {}
N 550 30 550 90 {}
N 610 0 610 94 {}
N -590 0 -530 0 {}
N -490 0 -460 0 {}
N -410 0 -350 0 {}
N -310 0 330 0 {}
N 370 0 430 0 {}
N 480 0 510 0 {}
N 550 0 610 0 {}
C {devices/lab_wire.sym} -530 90 2 0 {name=l0 lab=gate_p}
C {devices/lab_wire.sym} -250 0 0 1 {name=l1 lab=gate_p}
C {devices/lab_wire.sym} -490 60 2 0 {name=l2 lab=gate_pc}
C {devices/lab_wire.sym} 510 -60 0 1 {name=l3 lab=gate_pc}
C {devices/lab_wire.sym} -530 -90 0 1 {name=l4 lab=s3}
C {devices/lab_wire.sym} 370 90 2 0 {name=l5 lab=s3}
C {devices/lab_wire.sym} -350 90 2 0 {name=l6 lab=s4}
C {devices/lab_wire.sym} 550 -90 0 1 {name=l7 lab=s4}
C {devices/lab_wire.sym} -350 -90 0 1 {name=l8 lab=vdd}
C {devices/lab_wire.sym} 370 -90 0 1 {name=l9 lab=vdd}
C {devices/lab_wire.sym} 550 90 2 0 {name=l10 lab=vout}
C {devices/lab_wire.sym} 430 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} -590 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -410 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 610 94 2 0 {name=l14 lab=vdd}
C {devices/ipin.sym} -865 0 0 0 {name=p0 lab=gate_pc}
C {devices/iopin.sym} -350 280 0 0 {name=p1 lab=vdd}
C {devices/opin.sym} 885 0 0 0 {name=p2 lab=gate_p}
C {devices/opin.sym} 885 120 0 0 {name=p3 lab=vout}
