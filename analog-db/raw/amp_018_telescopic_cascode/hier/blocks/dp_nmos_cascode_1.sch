v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_nmos_cascode_1} -550 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 350 0 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} -510 0 0 1 {name=M1C model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1c_w l=x_dut_xm1c_l m=x_dut_xm1c_m}
C {devices/sg13_lv_nmos_np.sym} -330 0 0 1 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 530 0 0 0 {name=M2C model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2c_w l=x_dut_xm2c_l m=x_dut_xm2c_m}
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
N -310 0 -250 0 {}
N 270 0 330 0 {}
N 370 0 430 0 {}
N 480 0 510 0 {}
N 550 0 610 0 {}
C {devices/lab_wire.sym} -490 60 2 0 {name=l0 lab=casc_n}
C {devices/lab_wire.sym} 510 -60 0 1 {name=l1 lab=casc_n}
C {devices/lab_wire.sym} -530 90 2 0 {name=l2 lab=d1}
C {devices/lab_wire.sym} 370 -90 0 1 {name=l3 lab=d1}
C {devices/lab_wire.sym} -350 -90 0 1 {name=l4 lab=d2}
C {devices/lab_wire.sym} 550 90 2 0 {name=l5 lab=d2}
C {devices/lab_wire.sym} -530 -90 0 1 {name=l6 lab=gate_p}
C {devices/lab_wire.sym} -350 90 2 0 {name=l7 lab=tail}
C {devices/lab_wire.sym} 370 90 2 0 {name=l8 lab=tail}
C {devices/lab_wire.sym} -250 0 0 1 {name=l9 lab=vinn}
C {devices/lab_wire.sym} 270 0 0 0 {name=l10 lab=vinp}
C {devices/lab_wire.sym} 550 -90 0 1 {name=l11 lab=vout}
C {devices/lab_wire.sym} 430 94 2 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} -590 94 2 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} -410 94 2 0 {name=l14 lab=vss}
C {devices/lab_wire.sym} 610 94 2 0 {name=l15 lab=vss}
C {devices/ipin.sym} -865 0 0 0 {name=p0 lab=casc_n}
C {devices/ipin.sym} -865 120 0 0 {name=p1 lab=vinn}
C {devices/ipin.sym} -865 240 0 0 {name=p2 lab=vinp}
C {devices/iopin.sym} -350 280 0 0 {name=p3 lab=tail}
C {devices/opin.sym} 885 -30 0 0 {name=p4 lab=gate_p}
C {devices/opin.sym} 885 90 0 0 {name=p5 lab=vout}
