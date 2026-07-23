v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_cascode_1} -550 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 365 0 0 0 {name=MPB1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpb1_w l=x_dut_xmpb1_l m=x_dut_xmpb1_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=MPB2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpb2_w l=x_dut_xmpb2_l m=x_dut_xmpb2_m}
C {devices/sg13_lv_pmos_np.sym} 560 0 0 0 {name=MPCA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpca_w l=x_dut_xmpca_l m=x_dut_xmpca_m}
C {devices/sg13_lv_pmos_np.sym} -315 0 0 1 {name=MPLD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpld_w l=x_dut_xmpld_l m=x_dut_xmpld_m}
N -590 0 -590 94 {}
N -530 -90 -530 -30 {}
N -530 30 -530 70 {}
N -490 0 -490 70 {}
N -395 0 -395 94 {}
N -335 -90 -335 -30 {}
N -335 30 -335 90 {}
N 345 0 345 70 {}
N 385 -90 385 -30 {}
N 385 30 385 70 {}
N 445 0 445 94 {}
N 540 -60 540 0 {}
N 580 -90 580 -30 {}
N 580 30 580 90 {}
N 640 0 640 94 {}
N -590 0 -530 0 {}
N -395 0 -335 0 {}
N -295 0 -235 0 {}
N 285 0 345 0 {}
N 385 0 445 0 {}
N 510 0 540 0 {}
N 580 0 640 0 {}
N -530 70 -490 70 {}
N 345 70 385 70 {}
C {devices/lab_wire.sym} -490 60 2 0 {name=l0 lab=ibias}
C {devices/lab_wire.sym} 540 -60 0 1 {name=l1 lab=ibias}
C {devices/lab_wire.sym} -530 -90 0 1 {name=l2 lab=pbias1}
C {devices/lab_wire.sym} -235 0 0 1 {name=l3 lab=pbias1}
C {devices/lab_wire.sym} 285 0 0 0 {name=l4 lab=pbias1}
C {devices/lab_wire.sym} -335 90 2 0 {name=l5 lab=pint}
C {devices/lab_wire.sym} 580 -90 0 1 {name=l6 lab=pint}
C {devices/lab_wire.sym} -335 -90 0 1 {name=l7 lab=vdd}
C {devices/lab_wire.sym} 385 -90 0 1 {name=l8 lab=vdd}
C {devices/lab_wire.sym} 580 90 2 0 {name=l9 lab=vout}
C {devices/lab_wire.sym} 445 94 2 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} -590 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} 640 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -395 94 2 0 {name=l13 lab=vdd}
C {devices/iopin.sym} -335 280 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 925 0 0 0 {name=p1 lab=ibias}
C {devices/opin.sym} 925 120 0 0 {name=p2 lab=vout}
