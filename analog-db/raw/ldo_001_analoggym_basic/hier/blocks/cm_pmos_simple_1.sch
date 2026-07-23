v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -465 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 990 0 0 0 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} 775 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -425 0 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 500 0 0 0 {name=M24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_pmos_np.sym} 285 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 65 0 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} -150 0 0 1 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -405 -90 -405 -30 {}
N -405 30 -405 90 {}
N -345 0 -345 94 {}
N -230 0 -230 94 {}
N -170 -60 -170 -30 {}
N -170 30 -170 90 {}
N -130 0 -130 60 {}
N -15 0 -15 94 {}
N 45 -60 45 -30 {}
N 45 30 45 90 {}
N 85 0 85 60 {}
N 205 0 205 94 {}
N 265 -60 265 -30 {}
N 265 30 265 90 {}
N 520 -60 520 -30 {}
N 520 30 520 90 {}
N 580 0 580 94 {}
N 795 -60 795 -30 {}
N 795 30 795 90 {}
N 855 0 855 94 {}
N 970 0 970 70 {}
N 1010 -60 1010 -30 {}
N 1010 30 1010 70 {}
N 1070 0 1070 94 {}
N -405 -60 1010 -60 {}
N -505 0 -445 0 {}
N -405 0 -345 0 {}
N -230 0 -170 0 {}
N -130 0 -100 0 {}
N -15 0 45 0 {}
N 85 0 115 0 {}
N 205 0 265 0 {}
N 305 0 480 0 {}
N 520 0 580 0 {}
N 725 0 755 0 {}
N 795 0 855 0 {}
N 1010 0 1070 0 {}
N 970 70 1010 70 {}
C {devices/lab_wire.sym} -405 90 2 0 {name=l0 lab=dm_1}
C {devices/lab_wire.sym} -505 0 0 0 {name=l1 lab=ib}
C {devices/lab_wire.sym} -130 60 2 0 {name=l2 lab=ib}
C {devices/lab_wire.sym} 85 60 2 0 {name=l3 lab=ib}
C {devices/lab_wire.sym} 365 0 0 1 {name=l4 lab=ib}
C {devices/lab_wire.sym} 755 0 0 0 {name=l5 lab=ib}
C {devices/lab_wire.sym} 970 0 0 0 {name=l6 lab=ib}
C {devices/lab_wire.sym} 520 90 2 0 {name=l7 lab=net1}
C {devices/lab_wire.sym} 45 90 2 0 {name=l8 lab=net20}
C {devices/lab_wire.sym} -170 90 2 0 {name=l9 lab=net7}
C {devices/lab_wire.sym} 265 90 2 0 {name=l10 lab=vb3}
C {devices/lab_wire.sym} 795 90 2 0 {name=l11 lab=vb4}
C {devices/lab_wire.sym} -405 -90 0 1 {name=l12 lab=vdd}
C {devices/lab_wire.sym} 1070 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 855 94 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} -345 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 580 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 205 94 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} -15 94 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} -230 94 2 0 {name=l19 lab=vdd}
C {devices/iopin.sym} -405 280 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 1340 0 0 0 {name=p1 lab=ib}
C {devices/opin.sym} 1340 120 0 0 {name=p2 lab=dm_1}
C {devices/opin.sym} 1340 240 0 0 {name=p3 lab=net7}
C {devices/opin.sym} 1340 360 0 0 {name=p4 lab=net20}
C {devices/opin.sym} 1340 480 0 0 {name=p5 lab=vb3}
C {devices/opin.sym} 1340 600 0 0 {name=p6 lab=net1}
C {devices/opin.sym} 1340 720 0 0 {name=p7 lab=vb4}
