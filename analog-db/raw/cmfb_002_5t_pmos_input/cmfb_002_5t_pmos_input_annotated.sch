v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmfb_002_5t_pmos_input} -545 -200 0 0 0.4 0.4 {}
C {devices/res_np.sym} -505 260 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 835 260 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/sg13_lv_pmos_np.sym} 50 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} -120 520 0 1 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 560 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 220 260 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} -120 260 0 1 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_nmos_np.sym} 220 520 0 0 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} 560 260 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -505 200 -505 230 {}
N -505 290 -505 320 {}
N -200 290 -200 460 {}
N -200 520 -200 614 {}
N -140 200 -140 230 {}
N -140 460 -140 490 {}
N -140 550 -140 660 {}
N -30 0 -30 94 {}
N 30 -140 30 -30 {}
N 30 30 30 200 {}
N 170 140 170 260 {}
N 200 450 200 520 {}
N 230 260 230 320 {}
N 240 200 240 230 {}
N 240 290 240 490 {}
N 240 550 240 660 {}
N 300 260 300 354 {}
N 300 520 300 614 {}
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
N -30 0 30 0 {}
N 40 0 540 0 {}
N 580 0 640 0 {}
N 540 70 580 70 {}
N 170 140 835 140 {}
N 540 190 580 190 {}
N -140 200 240 200 {}
N -100 260 -70 260 {}
N 170 260 230 260 {}
N 240 260 300 260 {}
N 580 260 640 260 {}
N -200 290 -140 290 {}
N -505 320 230 320 {}
N 200 450 240 450 {}
N -200 460 -140 460 {}
N -200 520 -140 520 {}
N -130 520 200 520 {}
N 240 520 300 520 {}
N -595 660 1150 660 {}
C {devices/lab_wire.sym} 130 0 0 1 {name=l0 lab=bias}
C {devices/lab_wire.sym} 835 170 0 1 {name=l1 lab=cm_sense}
C {devices/lab_wire.sym} 240 350 2 0 {name=l2 lab=mirr}
C {devices/lab_wire.sym} 30 90 2 0 {name=l3 lab=ptail}
C {devices/lab_wire.sym} -30 94 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} 640 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} 300 354 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} -140 260 0 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} -200 614 2 0 {name=l8 lab=vss}
C {devices/lab_wire.sym} 300 614 2 0 {name=l9 lab=vss}
C {devices/lab_wire.sym} 640 354 2 0 {name=l10 lab=vss}
C {devices/ipin.sym} -70 260 0 0 {name=p0 lab=vref}
C {devices/iopin.sym} -595 -140 0 0 {name=p1 lab=vdd}
C {devices/iopin.sym} -505 200 0 0 {name=p2 lab=vinn}
C {devices/iopin.sym} -595 660 0 0 {name=p3 lab=vss}
C {devices/iopin.sym} 835 380 0 0 {name=p4 lab=vinp}
C {devices/opin.sym} -140 460 0 0 {name=p5 lab=vcmfb}
B 8 -406 -78 1016 78 {fill=0}
T {PMOS Simple Current Mirror} -406 -96 0 0 0.3 0.3 {layer=8}
B 10 -576 442 676 598 {fill=0}
T {NMOS Simple Current Mirror} -576 424 0 0 0.3 0.3 {layer=10}
B 12 -576 182 676 338 {fill=0}
T {PMOS Differential Pair} -576 164 0 0 0.3 0.3 {layer=12}
