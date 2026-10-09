v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_low_voltage_cascode_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -170 260 0 1 {name=M3C model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3c_w l=x_dut_xm3c_l m=x_dut_xm3c_m}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 170 260 0 0 {name=M4C model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4c_w l=x_dut_xm4c_l m=x_dut_xm4c_m}
N -250 0 -250 94 {}
N -250 260 -250 354 {}
N -190 -140 -190 -30 {}
N -190 30 -190 230 {}
N -190 290 -190 320 {}
N -60 0 -60 320 {}
N 190 -140 190 -30 {}
N 190 30 190 230 {}
N 190 290 190 320 {}
N 250 0 250 94 {}
N 250 260 250 354 {}
N -670 -140 670 -140 {}
N -250 0 -190 0 {}
N -150 0 150 0 {}
N 190 0 250 0 {}
N -250 260 -190 260 {}
N -150 260 180 260 {}
N 190 260 250 260 {}
N -190 320 -60 320 {}
C {devices/lab_wire.sym} -190 90 2 0 {name=l0 lab=s3}
C {devices/lab_wire.sym} 190 90 2 0 {name=l1 lab=s4}
C {devices/lab_wire.sym} -250 94 2 0 {name=l2 lab=vdd}
C {devices/lab_wire.sym} -250 354 2 0 {name=l3 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} 250 354 2 0 {name=l5 lab=vdd}
C {devices/ipin.sym} 120 260 0 0 {name=p0 lab=gate_pc}
C {devices/iopin.sym} -670 -140 0 0 {name=p1 lab=vdd}
C {devices/opin.sym} 120 0 0 0 {name=p2 lab=gate_p}
C {devices/opin.sym} 190 320 0 0 {name=p3 lab=vout}
