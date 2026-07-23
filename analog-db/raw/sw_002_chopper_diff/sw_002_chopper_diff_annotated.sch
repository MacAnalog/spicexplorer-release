v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sw_002_chopper_diff} -580 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 715 0 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 260 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1305 0 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 1010 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 30 0 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} -265 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} -540 0 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 485 0 0 1 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
N -520 -90 -520 -30 {}
N -520 30 -520 90 {}
N -460 0 -460 94 {}
N -345 0 -345 94 {}
N -285 -90 -285 -30 {}
N -285 30 -285 90 {}
N -245 0 -245 60 {}
N -50 0 -50 94 {}
N 10 -90 10 -30 {}
N 10 30 10 90 {}
N 50 0 50 60 {}
N 180 0 180 94 {}
N 240 -90 240 -30 {}
N 240 30 240 90 {}
N 280 0 280 60 {}
N 405 0 405 94 {}
N 465 -90 465 -30 {}
N 465 30 465 90 {}
N 735 -90 735 -30 {}
N 735 30 735 90 {}
N 795 0 795 94 {}
N 990 -60 990 0 {}
N 1030 -90 1030 -30 {}
N 1030 30 1030 90 {}
N 1090 0 1090 94 {}
N 1325 -60 1325 -30 {}
N 1325 30 1325 60 {}
N 1385 0 1385 94 {}
N 1030 -60 1325 -60 {}
N -620 0 -560 0 {}
N -520 0 -460 0 {}
N -345 0 -285 0 {}
N -245 0 -215 0 {}
N -50 0 10 0 {}
N 50 0 80 0 {}
N 180 0 240 0 {}
N 280 0 310 0 {}
N 405 0 465 0 {}
N 505 0 695 0 {}
N 735 0 795 0 {}
N 960 0 990 0 {}
N 1030 0 1090 0 {}
N 1255 0 1285 0 {}
N 1325 0 1385 0 {}
N 1030 60 1325 60 {}
C {devices/lab_wire.sym} -520 -90 0 1 {name=l0 lab=va_n}
C {devices/lab_wire.sym} 465 -90 0 1 {name=l1 lab=va_n}
C {devices/lab_wire.sym} 1030 -90 0 1 {name=l2 lab=va_n}
C {devices/lab_wire.sym} -285 -90 0 1 {name=l3 lab=va_p}
C {devices/lab_wire.sym} 10 -90 0 1 {name=l4 lab=va_p}
C {devices/lab_wire.sym} 240 -90 0 1 {name=l5 lab=va_p}
C {devices/lab_wire.sym} 735 -90 0 1 {name=l6 lab=va_p}
C {devices/lab_wire.sym} -285 90 2 0 {name=l7 lab=vb_n}
C {devices/lab_wire.sym} 10 90 2 0 {name=l8 lab=vb_n}
C {devices/lab_wire.sym} 1030 90 2 0 {name=l9 lab=vb_n}
C {devices/lab_wire.sym} -520 90 2 0 {name=l10 lab=vb_p}
C {devices/lab_wire.sym} 240 90 2 0 {name=l11 lab=vb_p}
C {devices/lab_wire.sym} 465 90 2 0 {name=l12 lab=vb_p}
C {devices/lab_wire.sym} 735 90 2 0 {name=l13 lab=vb_p}
C {devices/lab_wire.sym} -245 60 2 0 {name=l14 lab=vctl}
C {devices/lab_wire.sym} 565 0 0 1 {name=l15 lab=vctl}
C {devices/lab_wire.sym} 1285 0 0 0 {name=l16 lab=vctl}
C {devices/lab_wire.sym} -620 0 0 0 {name=l17 lab=vctl_not}
C {devices/lab_wire.sym} 50 60 2 0 {name=l18 lab=vctl_not}
C {devices/lab_wire.sym} 280 60 2 0 {name=l19 lab=vctl_not}
C {devices/lab_wire.sym} 990 -60 0 1 {name=l20 lab=vctl_not}
C {devices/lab_wire.sym} 180 94 2 0 {name=l21 lab=vdd}
C {devices/lab_wire.sym} 1090 94 2 0 {name=l22 lab=vdd}
C {devices/lab_wire.sym} -345 94 2 0 {name=l23 lab=vdd}
C {devices/lab_wire.sym} 405 94 2 0 {name=l24 lab=vdd}
C {devices/lab_wire.sym} 795 94 2 0 {name=l25 lab=vss}
C {devices/lab_wire.sym} 1385 94 2 0 {name=l26 lab=vss}
C {devices/lab_wire.sym} -50 94 2 0 {name=l27 lab=vss}
C {devices/lab_wire.sym} -460 94 2 0 {name=l28 lab=vss}
C {devices/ipin.sym} -790 0 0 0 {name=p0 lab=vctl_not}
C {devices/ipin.sym} -790 120 0 0 {name=p1 lab=vctl}
C {devices/opin.sym} 1655 -30 0 0 {name=p2 lab=va_n}
C {devices/opin.sym} 1655 90 0 0 {name=p3 lab=va_p}
C {devices/opin.sym} 1655 210 0 0 {name=p4 lab=vb_p}
C {devices/opin.sym} 1655 330 0 0 {name=p5 lab=vb_n}
B 8 72 -78 903 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 72 -96 0 0 0.3 0.3 {layer=8}
B 10 940 -78 1493 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 940 -96 0 0 0.3 0.3 {layer=10}
B 12 -453 -78 100 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -453 -96 0 0 0.3 0.3 {layer=12}
B 21 -610 -78 555 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -610 -96 0 0 0.3 0.3 {layer=21}
