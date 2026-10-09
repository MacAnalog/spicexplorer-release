v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sw_002_chopper_diff} -550 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 695 0 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 465 0 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1150 0 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 920 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} -280 0 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} 175 0 0 1 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} -55 0 0 1 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
N -590 0 -590 94 {}
N -530 -60 -530 -30 {}
N -530 30 -530 60 {}
N -300 -120 -300 -30 {}
N -300 30 -300 60 {}
N 95 -60 95 -30 {}
N 485 -120 485 -30 {}
N 545 0 545 94 {}
N 775 0 775 94 {}
N 940 -60 940 -30 {}
N 940 30 940 60 {}
N 1000 0 1000 94 {}
N 1170 -60 1170 -30 {}
N 1170 30 1170 60 {}
N 1230 0 1230 94 {}
N -985 -140 1625 -140 {}
N -300 -120 485 -120 {}
N -530 -60 -300 -60 {}
N 95 -60 1170 -60 {}
N -135 -30 155 -30 {}
N 425 -30 715 -30 {}
N -590 0 -530 0 {}
N -490 0 -460 0 {}
N -260 0 -230 0 {}
N -35 0 25 0 {}
N 195 0 445 0 {}
N 485 0 545 0 {}
N 615 0 675 0 {}
N 715 0 775 0 {}
N 840 0 900 0 {}
N 940 0 1000 0 {}
N 1070 0 1130 0 {}
N 1170 0 1230 0 {}
N -135 30 715 30 {}
N -530 60 1170 60 {}
N -985 140 1625 140 {}
C {devices/lab_wire.sym} -985 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -985 140 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 25 0 0 1 {name=l2 lab=vctl}
C {devices/lab_wire.sym} 615 0 0 0 {name=l3 lab=vctl}
C {devices/lab_wire.sym} 1070 0 0 0 {name=l4 lab=vctl}
C {devices/lab_wire.sym} 255 0 0 1 {name=l5 lab=vctl_not}
C {devices/lab_wire.sym} 840 0 0 0 {name=l6 lab=vctl_not}
C {devices/lab_wire.sym} 545 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} 1000 94 2 0 {name=l8 lab=vdd}
C {devices/lab_wire.sym} -590 94 2 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} -75 0 0 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} 775 94 2 0 {name=l11 lab=vss}
C {devices/lab_wire.sym} 1230 94 2 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} -300 0 0 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} 155 0 0 0 {name=l14 lab=vss}
C {devices/ipin.sym} -460 0 0 0 {name=p0 lab=vctl}
C {devices/ipin.sym} -230 0 0 0 {name=p1 lab=vctl_not}
C {devices/opin.sym} 485 -120 0 0 {name=p2 lab=va_p}
C {devices/opin.sym} 1170 -60 0 0 {name=p3 lab=va_n}
C {devices/opin.sym} 1170 60 0 0 {name=p4 lab=vb_n}
C {devices/opin.sym} 425 30 0 0 {name=p5 lab=vb_p}
