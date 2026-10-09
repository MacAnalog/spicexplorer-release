v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmfb_003_5t_nmos_input} -545 -200 0 0 0.4 0.4 {}
C {devices/res_np.sym} -505 260 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 835 260 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/sg13_lv_nmos_np.sym} -120 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} 220 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -120 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 220 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 560 260 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 560 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} 50 520 0 1 {name=M8 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
N -505 200 -505 230 {}
N -505 290 -505 320 {}
N -200 0 -200 94 {}
N -200 290 -200 460 {}
N -140 -140 -140 -30 {}
N -140 30 -140 230 {}
N -140 290 -140 350 {}
N -100 0 -100 70 {}
N -70 140 -70 260 {}
N -30 520 -30 614 {}
N -10 260 -10 320 {}
N 30 460 30 490 {}
N 30 550 30 660 {}
N 170 0 170 60 {}
N 240 -140 240 -30 {}
N 240 30 240 230 {}
N 240 290 240 320 {}
N 300 0 300 94 {}
N 300 320 300 460 {}
N 540 0 540 70 {}
N 540 190 540 260 {}
N 580 -140 580 -30 {}
N 580 30 580 230 {}
N 580 290 580 660 {}
N 640 0 640 94 {}
N 640 260 640 354 {}
N 835 140 835 230 {}
N 835 290 835 380 {}
N -595 -140 1150 -140 {}
N -200 0 -140 0 {}
N -100 0 -40 0 {}
N 170 0 200 0 {}
N 240 0 300 0 {}
N 480 0 540 0 {}
N 580 0 640 0 {}
N -140 60 170 60 {}
N -140 70 -100 70 {}
N 540 70 580 70 {}
N -70 140 835 140 {}
N 540 190 580 190 {}
N -100 260 -10 260 {}
N 110 260 200 260 {}
N 580 260 640 260 {}
N -200 290 -140 290 {}
N -505 320 -10 320 {}
N 240 320 300 320 {}
N -200 460 300 460 {}
N -30 520 30 520 {}
N 70 520 130 520 {}
N -595 660 1150 660 {}
C {devices/lab_wire.sym} 130 520 0 1 {name=l0 lab=bias}
C {devices/lab_wire.sym} 480 0 0 0 {name=l1 lab=bias}
C {devices/lab_wire.sym} 835 170 0 1 {name=l2 lab=cm_sense}
C {devices/lab_wire.sym} -40 0 0 1 {name=l3 lab=mirr}
C {devices/lab_wire.sym} -140 350 2 0 {name=l4 lab=ntail}
C {devices/lab_wire.sym} -200 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} 300 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} 640 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} -140 260 0 0 {name=l8 lab=vss}
C {devices/lab_wire.sym} 240 260 0 0 {name=l9 lab=vss}
C {devices/lab_wire.sym} 640 354 2 0 {name=l10 lab=vss}
C {devices/lab_wire.sym} -30 614 2 0 {name=l11 lab=vss}
C {devices/ipin.sym} 110 260 0 0 {name=p0 lab=vref}
C {devices/iopin.sym} -595 -140 0 0 {name=p1 lab=vdd}
C {devices/iopin.sym} -505 200 0 0 {name=p2 lab=vinn}
C {devices/iopin.sym} -595 660 0 0 {name=p3 lab=vss}
C {devices/iopin.sym} 835 380 0 0 {name=p4 lab=vinp}
C {devices/opin.sym} 240 60 0 0 {name=p5 lab=vcmfb}
