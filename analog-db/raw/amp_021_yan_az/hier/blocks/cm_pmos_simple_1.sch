v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 650 0 0 0 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} 375 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 105 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N -150 0 -150 60 {}
N 25 0 25 94 {}
N 85 -60 85 -30 {}
N 85 30 85 90 {}
N 395 -60 395 -30 {}
N 395 30 395 90 {}
N 455 0 455 94 {}
N 630 0 630 70 {}
N 670 -60 670 -30 {}
N 670 30 670 70 {}
N 730 0 730 94 {}
N -190 -60 670 -60 {}
N -250 0 -190 0 {}
N -150 0 -120 0 {}
N 25 0 85 0 {}
N 125 0 355 0 {}
N 395 0 455 0 {}
N 670 0 730 0 {}
N 630 70 670 70 {}
C {devices/lab_wire.sym} -150 60 2 0 {name=l0 lab=VB1}
C {devices/lab_wire.sym} 185 0 0 1 {name=l1 lab=VB1}
C {devices/lab_wire.sym} 630 0 0 0 {name=l2 lab=VB1}
C {devices/lab_wire.sym} 395 90 2 0 {name=l3 lab=VB4}
C {devices/lab_wire.sym} 85 90 2 0 {name=l4 lab=net019}
C {devices/lab_wire.sym} -190 90 2 0 {name=l5 lab=net078}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l6 lab=vdd}
C {devices/lab_wire.sym} 730 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} 455 94 2 0 {name=l8 lab=vdd}
C {devices/lab_wire.sym} 25 94 2 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l10 lab=vdd}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 1000 0 0 0 {name=p1 lab=VB1}
C {devices/opin.sym} 1000 120 0 0 {name=p2 lab=net078}
C {devices/opin.sym} 1000 240 0 0 {name=p3 lab=net019}
C {devices/opin.sym} 1000 360 0 0 {name=p4 lab=VB4}
