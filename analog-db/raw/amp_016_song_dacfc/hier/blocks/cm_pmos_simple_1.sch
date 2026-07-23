v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 810 0 0 0 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} 565 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 320 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 75 0 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M59 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm59_w l=x_dut_xm59_l m=x_dut_xm59_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N -150 0 -150 60 {}
N -5 0 -5 94 {}
N 55 -60 55 -30 {}
N 55 30 55 90 {}
N 340 -60 340 -30 {}
N 340 30 340 90 {}
N 400 0 400 94 {}
N 585 -60 585 -30 {}
N 585 30 585 90 {}
N 645 0 645 94 {}
N 790 0 790 70 {}
N 830 -60 830 -30 {}
N 830 30 830 70 {}
N 890 0 890 94 {}
N -190 -60 830 -60 {}
N -250 0 -190 0 {}
N -150 0 -120 0 {}
N -5 0 55 0 {}
N 95 0 300 0 {}
N 340 0 400 0 {}
N 515 0 545 0 {}
N 585 0 645 0 {}
N 830 0 890 0 {}
N 790 70 830 70 {}
C {devices/lab_wire.sym} 340 90 2 0 {name=l0 lab=VB3}
C {devices/lab_wire.sym} 585 90 2 0 {name=l1 lab=VB4}
C {devices/lab_wire.sym} -150 60 2 0 {name=l2 lab=net013}
C {devices/lab_wire.sym} 155 0 0 1 {name=l3 lab=net013}
C {devices/lab_wire.sym} 545 0 0 0 {name=l4 lab=net013}
C {devices/lab_wire.sym} 790 0 0 0 {name=l5 lab=net013}
C {devices/lab_wire.sym} -190 90 2 0 {name=l6 lab=net1}
C {devices/lab_wire.sym} 55 90 2 0 {name=l7 lab=net31}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l8 lab=vdd}
C {devices/lab_wire.sym} 890 94 2 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} 645 94 2 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} 400 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} -5 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l13 lab=vdd}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 1160 0 0 0 {name=p1 lab=net013}
C {devices/opin.sym} 1160 120 0 0 {name=p2 lab=net1}
C {devices/opin.sym} 1160 240 0 0 {name=p3 lab=net31}
C {devices/opin.sym} 1160 360 0 0 {name=p4 lab=VB3}
C {devices/opin.sym} 1160 480 0 0 {name=p5 lab=VB4}
