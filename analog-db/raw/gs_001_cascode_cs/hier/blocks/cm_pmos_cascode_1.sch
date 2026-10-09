v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_cascode_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=MPB1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpb1_w l=x_dut_xmpb1_l m=x_dut_xmpb1_m}
C {devices/sg13_lv_pmos_np.sym} -170 260 0 1 {name=MPB2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpb2_w l=x_dut_xmpb2_l m=x_dut_xmpb2_m}
C {devices/sg13_lv_pmos_np.sym} 170 260 0 0 {name=MPCA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpca_w l=x_dut_xmpca_l m=x_dut_xmpca_m}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=MPLD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpld_w l=x_dut_xmpld_l m=x_dut_xmpld_m}
N -250 0 -250 94 {}
N -250 260 -250 354 {}
N -190 -140 -190 -30 {}
N -190 30 -190 230 {}
N -190 290 -190 330 {}
N -150 0 -150 70 {}
N -150 260 -150 330 {}
N 120 0 120 60 {}
N 120 260 120 320 {}
N 190 -140 190 -30 {}
N 190 30 190 230 {}
N 190 290 190 320 {}
N 250 0 250 94 {}
N 250 260 250 354 {}
N -695 -140 695 -140 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 120 0 150 0 {}
N 190 0 250 0 {}
N -190 60 120 60 {}
N -190 70 -150 70 {}
N -250 260 -190 260 {}
N 120 260 150 260 {}
N 190 260 250 260 {}
N -190 320 120 320 {}
N -190 330 -150 330 {}
C {devices/lab_wire.sym} -90 0 0 1 {name=l0 lab=pbias1}
C {devices/lab_wire.sym} 190 90 2 0 {name=l1 lab=pint}
C {devices/lab_wire.sym} -250 94 2 0 {name=l2 lab=vdd}
C {devices/lab_wire.sym} -250 354 2 0 {name=l3 lab=vdd}
C {devices/lab_wire.sym} 250 354 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l5 lab=vdd}
C {devices/iopin.sym} -695 -140 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 120 260 0 0 {name=p1 lab=ibias}
C {devices/opin.sym} 190 320 0 0 {name=p2 lab=vout}
