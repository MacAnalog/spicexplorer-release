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
N -530 -90 -530 -30 {}
N -530 30 -530 90 {}
N -360 0 -360 94 {}
N -300 -60 -300 -30 {}
N -300 30 -300 60 {}
N -260 0 -260 60 {}
N -135 0 -135 94 {}
N -75 -90 -75 -30 {}
N -75 30 -75 90 {}
N -35 0 -35 60 {}
N 95 0 95 94 {}
N 155 -90 155 -30 {}
N 155 30 155 90 {}
N 485 -90 485 -30 {}
N 485 30 485 90 {}
N 545 0 545 94 {}
N 675 -60 675 0 {}
N 715 -90 715 -30 {}
N 715 30 715 90 {}
N 775 0 775 94 {}
N 900 -60 900 0 {}
N 940 -90 940 -30 {}
N 940 30 940 90 {}
N 1000 0 1000 94 {}
N 1170 -60 1170 -30 {}
N 1170 30 1170 60 {}
N 1230 0 1230 94 {}
N -530 -60 -300 -60 {}
N 940 -60 1170 -60 {}
N -590 0 -530 0 {}
N -490 0 -460 0 {}
N -360 0 -300 0 {}
N -260 0 -230 0 {}
N -135 0 -75 0 {}
N -35 0 -5 0 {}
N 95 0 155 0 {}
N 195 0 445 0 {}
N 485 0 545 0 {}
N 645 0 675 0 {}
N 715 0 775 0 {}
N 870 0 900 0 {}
N 940 0 1000 0 {}
N 1100 0 1130 0 {}
N 1170 0 1230 0 {}
N -530 60 -300 60 {}
N 940 60 1170 60 {}
C {devices/lab_wire.sym} -75 -90 0 1 {name=l0 lab=va_n}
C {devices/lab_wire.sym} 155 -90 0 1 {name=l1 lab=va_n}
C {devices/lab_wire.sym} 940 -90 0 1 {name=l2 lab=va_n}
C {devices/lab_wire.sym} -530 -90 0 1 {name=l3 lab=va_p}
C {devices/lab_wire.sym} 485 -90 0 1 {name=l4 lab=va_p}
C {devices/lab_wire.sym} 715 -90 0 1 {name=l5 lab=va_p}
C {devices/lab_wire.sym} -530 90 2 0 {name=l6 lab=vb_n}
C {devices/lab_wire.sym} 940 90 2 0 {name=l7 lab=vb_n}
C {devices/lab_wire.sym} -75 90 2 0 {name=l8 lab=vb_p}
C {devices/lab_wire.sym} 155 90 2 0 {name=l9 lab=vb_p}
C {devices/lab_wire.sym} 485 90 2 0 {name=l10 lab=vb_p}
C {devices/lab_wire.sym} 715 90 2 0 {name=l11 lab=vb_p}
C {devices/lab_wire.sym} -490 0 0 0 {name=l12 lab=vctl}
C {devices/lab_wire.sym} -35 60 2 0 {name=l13 lab=vctl}
C {devices/lab_wire.sym} 675 -60 0 1 {name=l14 lab=vctl}
C {devices/lab_wire.sym} 1130 0 0 0 {name=l15 lab=vctl}
C {devices/lab_wire.sym} -260 60 2 0 {name=l16 lab=vctl_not}
C {devices/lab_wire.sym} 255 0 0 1 {name=l17 lab=vctl_not}
C {devices/lab_wire.sym} 900 -60 0 1 {name=l18 lab=vctl_not}
C {devices/lab_wire.sym} 545 94 2 0 {name=l19 lab=vdd}
C {devices/lab_wire.sym} 1000 94 2 0 {name=l20 lab=vdd}
C {devices/lab_wire.sym} -590 94 2 0 {name=l21 lab=vdd}
C {devices/lab_wire.sym} -135 94 2 0 {name=l22 lab=vdd}
C {devices/lab_wire.sym} 775 94 2 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} 1230 94 2 0 {name=l24 lab=vss}
C {devices/lab_wire.sym} -360 94 2 0 {name=l25 lab=vss}
C {devices/lab_wire.sym} 95 94 2 0 {name=l26 lab=vss}
C {devices/ipin.sym} -860 0 0 0 {name=p0 lab=vctl}
C {devices/ipin.sym} -860 120 0 0 {name=p1 lab=vctl_not}
C {devices/opin.sym} 1500 -30 0 0 {name=p2 lab=va_p}
C {devices/opin.sym} 1500 90 0 0 {name=p3 lab=va_n}
C {devices/opin.sym} 1500 210 0 0 {name=p4 lab=vb_n}
C {devices/opin.sym} 1500 330 0 0 {name=p5 lab=vb_p}
