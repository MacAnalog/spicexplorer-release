v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_nmos_cascode_1} -550 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 390 0 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} -510 0 0 1 {name=M1C model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1c_w l=x_dut_xm1c_l m=x_dut_xm1c_m}
C {devices/sg13_lv_nmos_np.sym} -290 0 0 1 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 605 0 0 0 {name=M2C model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2c_w l=x_dut_xm2c_l m=x_dut_xm2c_m}
N -590 0 -590 94 {}
N -530 -60 -530 -30 {}
N -530 30 -530 90 {}
N -370 0 -370 94 {}
N -310 -90 -310 -30 {}
N -310 30 -310 60 {}
N 410 -90 410 -30 {}
N 410 30 410 60 {}
N 470 0 470 94 {}
N 625 -60 625 -30 {}
N 625 30 625 90 {}
N 685 0 685 94 {}
N -590 0 -530 0 {}
N -490 0 -460 0 {}
N -370 0 -310 0 {}
N -270 0 -240 0 {}
N 280 0 370 0 {}
N 410 0 470 0 {}
N 525 0 585 0 {}
N 625 0 685 0 {}
N -310 60 410 60 {}
N -1010 140 1105 140 {}
C {devices/lab_wire.sym} -1010 140 0 0 {name=l0 lab=vss}
C {devices/lab_wire.sym} 525 0 0 0 {name=l1 lab=casc_n}
C {devices/lab_wire.sym} -530 90 2 0 {name=l2 lab=d1}
C {devices/lab_wire.sym} 410 -90 0 1 {name=l3 lab=d1}
C {devices/lab_wire.sym} -310 -90 0 1 {name=l4 lab=d2}
C {devices/lab_wire.sym} 625 90 2 0 {name=l5 lab=d2}
C {devices/lab_wire.sym} 470 94 2 0 {name=l6 lab=vss}
C {devices/lab_wire.sym} -590 94 2 0 {name=l7 lab=vss}
C {devices/lab_wire.sym} -370 94 2 0 {name=l8 lab=vss}
C {devices/lab_wire.sym} 685 94 2 0 {name=l9 lab=vss}
C {devices/ipin.sym} -460 0 0 0 {name=p0 lab=casc_n}
C {devices/ipin.sym} -240 0 0 0 {name=p1 lab=vinn}
C {devices/ipin.sym} 280 0 0 0 {name=p2 lab=vinp}
C {devices/iopin.sym} -310 60 0 0 {name=p3 lab=tail}
C {devices/opin.sym} -530 -60 0 0 {name=p4 lab=gate_p}
C {devices/opin.sym} 625 -60 0 0 {name=p5 lab=vout}
