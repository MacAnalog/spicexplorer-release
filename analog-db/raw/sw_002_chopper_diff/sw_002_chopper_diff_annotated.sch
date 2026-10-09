v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sw_002_chopper_diff} -580 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 790 0 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 335 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1380 0 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 1085 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 105 0 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} -190 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} -540 0 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 560 0 0 1 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
N -520 -60 -520 -30 {}
N -520 30 -520 60 {}
N -460 0 -460 94 {}
N -270 0 -270 94 {}
N -210 -90 -210 -30 {}
N -210 30 -210 90 {}
N 25 0 25 94 {}
N 85 -90 85 -30 {}
N 85 30 85 90 {}
N 315 -90 315 -30 {}
N 315 30 315 90 {}
N 480 -60 480 -30 {}
N 600 -60 600 -30 {}
N 810 -90 810 -30 {}
N 870 0 870 94 {}
N 1105 -60 1105 -30 {}
N 1105 30 1105 60 {}
N 1165 0 1165 94 {}
N 1400 -60 1400 -30 {}
N 1400 30 1400 60 {}
N 1460 0 1460 94 {}
N -665 -140 1855 -140 {}
N -520 -60 1400 -60 {}
N 480 -30 600 -30 {}
N -650 0 -560 0 {}
N -520 0 -460 0 {}
N -270 0 -210 0 {}
N -170 0 -140 0 {}
N 25 0 85 0 {}
N 125 0 185 0 {}
N 355 0 415 0 {}
N 580 0 770 0 {}
N 810 0 870 0 {}
N 1005 0 1065 0 {}
N 1105 0 1165 0 {}
N 1300 0 1360 0 {}
N 1400 0 1460 0 {}
N 255 30 810 30 {}
N 1105 60 1400 60 {}
N -665 140 1855 140 {}
C {devices/lab_wire.sym} -665 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -665 140 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -210 -90 0 1 {name=l2 lab=va_p}
C {devices/lab_wire.sym} 85 -90 0 1 {name=l3 lab=va_p}
C {devices/lab_wire.sym} 315 -90 0 1 {name=l4 lab=va_p}
C {devices/lab_wire.sym} 810 -90 0 1 {name=l5 lab=va_p}
C {devices/lab_wire.sym} -210 90 2 0 {name=l6 lab=vb_n}
C {devices/lab_wire.sym} 85 90 2 0 {name=l7 lab=vb_n}
C {devices/lab_wire.sym} 315 90 2 0 {name=l8 lab=vb_p}
C {devices/lab_wire.sym} 640 0 0 1 {name=l9 lab=vctl}
C {devices/lab_wire.sym} 1300 0 0 0 {name=l10 lab=vctl}
C {devices/lab_wire.sym} 185 0 0 1 {name=l11 lab=vctl_not}
C {devices/lab_wire.sym} 415 0 0 1 {name=l12 lab=vctl_not}
C {devices/lab_wire.sym} 1005 0 0 0 {name=l13 lab=vctl_not}
C {devices/lab_wire.sym} 315 0 0 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} 1165 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} -270 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 540 0 0 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} 870 94 2 0 {name=l18 lab=vss}
C {devices/lab_wire.sym} 1460 94 2 0 {name=l19 lab=vss}
C {devices/lab_wire.sym} 25 94 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} -460 94 2 0 {name=l21 lab=vss}
C {devices/ipin.sym} -650 0 0 0 {name=p0 lab=vctl_not}
C {devices/ipin.sym} -140 0 0 0 {name=p1 lab=vctl}
C {devices/opin.sym} 1400 -60 0 0 {name=p2 lab=va_n}
C {devices/opin.sym} -520 60 0 0 {name=p3 lab=vb_p}
C {devices/opin.sym} 1400 60 0 0 {name=p4 lab=vb_n}
C {devices/opin.sym} 1995 -30 0 0 {name=p5 lab=va_p}
B 8 -121 -78 1246 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -121 -96 0 0 0.3 0.3 {layer=8}
B 10 1015 -78 1836 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1015 -96 0 0 0.3 0.3 {layer=10}
B 12 -646 -78 175 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -646 -96 0 0 0.3 0.3 {layer=12}
B 21 -610 -78 630 78 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -610 -96 0 0 0.3 0.3 {layer=21}
