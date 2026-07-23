v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -465 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 1000 0 0 0 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} 785 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -425 0 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} 510 0 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 295 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 75 0 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} -140 0 0 1 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -405 -90 -405 -30 {}
N -405 30 -405 90 {}
N -345 0 -345 94 {}
N -220 0 -220 94 {}
N -160 -60 -160 -30 {}
N -160 30 -160 90 {}
N -120 0 -120 60 {}
N -5 0 -5 94 {}
N 55 -60 55 -30 {}
N 55 30 55 90 {}
N 95 0 95 60 {}
N 215 0 215 94 {}
N 275 -60 275 -30 {}
N 275 30 275 90 {}
N 530 -60 530 -30 {}
N 530 30 530 90 {}
N 590 0 590 94 {}
N 805 -60 805 -30 {}
N 805 30 805 90 {}
N 865 0 865 94 {}
N 980 0 980 70 {}
N 1020 -60 1020 -30 {}
N 1020 30 1020 70 {}
N 1080 0 1080 94 {}
N -405 -60 1020 -60 {}
N -505 0 -445 0 {}
N -405 0 -345 0 {}
N -220 0 -160 0 {}
N -120 0 -90 0 {}
N -5 0 55 0 {}
N 95 0 125 0 {}
N 215 0 275 0 {}
N 315 0 490 0 {}
N 530 0 590 0 {}
N 735 0 765 0 {}
N 805 0 865 0 {}
N 1020 0 1080 0 {}
N 980 70 1020 70 {}
C {devices/lab_wire.sym} 530 90 2 0 {name=l0 lab=DM_1}
C {devices/lab_wire.sym} 275 90 2 0 {name=l1 lab=VB3}
C {devices/lab_wire.sym} 805 90 2 0 {name=l2 lab=VB4}
C {devices/lab_wire.sym} -405 90 2 0 {name=l3 lab=VOUT}
C {devices/lab_wire.sym} -505 0 0 0 {name=l4 lab=net013}
C {devices/lab_wire.sym} -120 60 2 0 {name=l5 lab=net013}
C {devices/lab_wire.sym} 95 60 2 0 {name=l6 lab=net013}
C {devices/lab_wire.sym} 375 0 0 1 {name=l7 lab=net013}
C {devices/lab_wire.sym} 765 0 0 0 {name=l8 lab=net013}
C {devices/lab_wire.sym} 980 0 0 0 {name=l9 lab=net013}
C {devices/lab_wire.sym} -160 90 2 0 {name=l10 lab=net049}
C {devices/lab_wire.sym} 55 90 2 0 {name=l11 lab=net31}
C {devices/lab_wire.sym} -405 -90 0 1 {name=l12 lab=vdd}
C {devices/lab_wire.sym} 1080 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 865 94 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} -345 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 590 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 215 94 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} -5 94 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} -220 94 2 0 {name=l19 lab=vdd}
C {devices/iopin.sym} -405 280 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 1350 0 0 0 {name=p1 lab=net013}
C {devices/opin.sym} 1350 120 0 0 {name=p2 lab=VOUT}
C {devices/opin.sym} 1350 240 0 0 {name=p3 lab=net049}
C {devices/opin.sym} 1350 360 0 0 {name=p4 lab=net31}
C {devices/opin.sym} 1350 480 0 0 {name=p5 lab=VB3}
C {devices/opin.sym} 1350 600 0 0 {name=p6 lab=DM_1}
C {devices/opin.sym} 1350 720 0 0 {name=p7 lab=VB4}
