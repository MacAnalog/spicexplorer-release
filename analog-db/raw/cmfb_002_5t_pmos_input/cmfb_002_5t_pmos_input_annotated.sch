v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmfb_002_5t_pmos_input} -545 -200 0 0 0.4 0.4 {}
C {devices/res_np.sym} -505 260 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 760 260 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/sg13_lv_pmos_np.sym} -25 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} -195 520 0 1 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 485 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 145 260 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} -195 260 0 1 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_nmos_np.sym} 145 520 0 0 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} 485 260 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -505 170 -505 230 {}
N -505 290 -505 350 {}
N -275 260 -275 354 {}
N -275 520 -275 614 {}
N -215 200 -215 230 {}
N -215 290 -215 350 {}
N -215 430 -215 490 {}
N -215 550 -215 660 {}
N -105 0 -105 94 {}
N -45 -140 -45 -30 {}
N -45 30 -45 200 {}
N 95 260 95 320 {}
N 125 450 125 520 {}
N 165 200 165 230 {}
N 165 290 165 490 {}
N 165 550 165 660 {}
N 225 260 225 354 {}
N 225 520 225 614 {}
N 465 0 465 70 {}
N 465 190 465 260 {}
N 505 -140 505 -30 {}
N 505 30 505 230 {}
N 505 290 505 660 {}
N 565 0 565 94 {}
N 565 260 565 354 {}
N 760 170 760 260 {}
N 760 290 760 350 {}
N -565 -140 1000 -140 {}
N -105 0 -45 0 {}
N -5 0 55 0 {}
N 405 0 465 0 {}
N 505 0 565 0 {}
N 465 70 505 70 {}
N 465 190 505 190 {}
N -215 200 165 200 {}
N -275 260 -215 260 {}
N -175 260 -115 260 {}
N 65 260 125 260 {}
N 165 260 225 260 {}
N 505 260 565 260 {}
N 125 450 165 450 {}
N -275 520 -215 520 {}
N -175 520 -115 520 {}
N 165 520 225 520 {}
N -565 660 1000 660 {}
C {devices/lab_wire.sym} -565 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -565 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 55 0 0 1 {name=l2 lab=bias}
C {devices/lab_wire.sym} 405 0 0 0 {name=l3 lab=bias}
C {devices/lab_wire.sym} -505 350 2 0 {name=l4 lab=cm_sense}
C {devices/lab_wire.sym} 65 260 0 0 {name=l5 lab=cm_sense}
C {devices/lab_wire.sym} 760 170 0 1 {name=l6 lab=cm_sense}
C {devices/lab_wire.sym} -115 520 0 1 {name=l7 lab=mirr}
C {devices/lab_wire.sym} 165 350 2 0 {name=l8 lab=mirr}
C {devices/lab_wire.sym} -45 90 2 0 {name=l9 lab=ptail}
C {devices/lab_wire.sym} -215 350 2 0 {name=l10 lab=vcmfb}
C {devices/lab_wire.sym} -215 430 0 1 {name=l11 lab=vcmfb}
C {devices/lab_wire.sym} -505 170 0 1 {name=l12 lab=vinn}
C {devices/lab_wire.sym} 760 350 2 0 {name=l13 lab=vinp}
C {devices/lab_wire.sym} -115 260 0 1 {name=l14 lab=vref}
C {devices/lab_wire.sym} -105 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 565 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 225 354 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} -275 354 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} -275 614 2 0 {name=l19 lab=vss}
C {devices/lab_wire.sym} 225 614 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} 565 354 2 0 {name=l21 lab=vss}
C {devices/ipin.sym} -705 260 0 0 {name=p0 lab=vref}
C {devices/iopin.sym} -505 800 0 0 {name=p1 lab=vinn}
C {devices/iopin.sym} 760 800 0 0 {name=p2 lab=vinp}
C {devices/opin.sym} 1140 290 0 0 {name=p3 lab=vcmfb}
B 8 -213 -78 673 78 {fill=0}
T {PMOS Simple Current Mirror} -213 -96 0 0 0.3 0.3 {layer=8}
B 10 -383 442 333 598 {fill=0}
T {NMOS Simple Current Mirror} -383 424 0 0 0.3 0.3 {layer=10}
B 12 -383 182 333 338 {fill=0}
T {PMOS Differential Pair} -383 164 0 0 0.3 0.3 {layer=12}
