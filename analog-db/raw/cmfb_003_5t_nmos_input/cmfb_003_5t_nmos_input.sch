v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmfb_003_5t_nmos_input} -545 -200 0 0 0.4 0.4 {}
C {devices/res_np.sym} -505 260 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 760 260 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/sg13_lv_nmos_np.sym} -195 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} 145 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -195 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 145 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 485 260 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 485 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} -25 520 0 1 {name=M8 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
N -505 170 -505 230 {}
N -505 290 -505 350 {}
N -275 0 -275 94 {}
N -275 260 -275 354 {}
N -215 -140 -215 -30 {}
N -215 30 -215 230 {}
N -215 290 -215 350 {}
N -175 0 -175 70 {}
N -105 520 -105 614 {}
N -45 320 -45 490 {}
N -45 550 -45 660 {}
N 95 0 95 60 {}
N 165 -140 165 -30 {}
N 165 30 165 230 {}
N 165 290 165 350 {}
N 225 0 225 94 {}
N 225 260 225 354 {}
N 465 0 465 70 {}
N 465 190 465 260 {}
N 505 -140 505 -30 {}
N 505 30 505 230 {}
N 505 290 505 350 {}
N 565 0 565 94 {}
N 565 260 565 354 {}
N 760 170 760 260 {}
N 760 290 760 350 {}
N -565 -140 1000 -140 {}
N -275 0 -215 0 {}
N -175 0 -115 0 {}
N 95 0 125 0 {}
N 165 0 225 0 {}
N 405 0 465 0 {}
N 505 0 565 0 {}
N -215 60 95 60 {}
N -215 70 -175 70 {}
N 465 70 505 70 {}
N 465 190 505 190 {}
N -275 260 -215 260 {}
N -175 260 -115 260 {}
N 65 260 125 260 {}
N 165 260 225 260 {}
N 505 260 565 260 {}
N -105 520 -45 520 {}
N -5 520 55 520 {}
N -565 660 1000 660 {}
C {devices/lab_wire.sym} -565 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -565 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 55 520 0 1 {name=l2 lab=bias}
C {devices/lab_wire.sym} 405 0 0 0 {name=l3 lab=bias}
C {devices/lab_wire.sym} -505 350 2 0 {name=l4 lab=cm_sense}
C {devices/lab_wire.sym} -115 260 0 1 {name=l5 lab=cm_sense}
C {devices/lab_wire.sym} 760 170 0 1 {name=l6 lab=cm_sense}
C {devices/lab_wire.sym} -115 0 0 1 {name=l7 lab=mirr}
C {devices/lab_wire.sym} -215 350 2 0 {name=l8 lab=ntail}
C {devices/lab_wire.sym} -45 430 0 1 {name=l9 lab=ntail}
C {devices/lab_wire.sym} 165 350 2 0 {name=l10 lab=ntail}
C {devices/lab_wire.sym} 165 90 2 0 {name=l11 lab=vcmfb}
C {devices/lab_wire.sym} -505 170 0 1 {name=l12 lab=vinn}
C {devices/lab_wire.sym} 760 350 2 0 {name=l13 lab=vinp}
C {devices/lab_wire.sym} 65 260 0 0 {name=l14 lab=vref}
C {devices/lab_wire.sym} -275 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 225 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 565 94 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} -275 354 2 0 {name=l18 lab=vss}
C {devices/lab_wire.sym} 225 354 2 0 {name=l19 lab=vss}
C {devices/lab_wire.sym} 565 354 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} -105 614 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} 505 350 2 0 {name=l22 lab=vss}
C {devices/ipin.sym} -705 260 0 0 {name=p0 lab=vref}
C {devices/iopin.sym} -505 800 0 0 {name=p1 lab=vinn}
C {devices/iopin.sym} 760 800 0 0 {name=p2 lab=vinp}
C {devices/opin.sym} 1140 30 0 0 {name=p3 lab=vcmfb}
