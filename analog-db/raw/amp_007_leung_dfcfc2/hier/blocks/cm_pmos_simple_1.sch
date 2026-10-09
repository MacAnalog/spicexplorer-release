v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -890 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} -850 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 510 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 850 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -930 0 -930 94 {}
N -870 -140 -870 -30 {}
N -870 30 -870 70 {}
N -830 0 -830 70 {}
N -590 0 -590 94 {}
N -530 -140 -530 -30 {}
N -530 30 -530 90 {}
N -460 -60 -460 0 {}
N -250 0 -250 94 {}
N -190 -140 -190 -30 {}
N -190 30 -190 60 {}
N -120 -60 -120 0 {}
N 120 -60 120 0 {}
N 190 -140 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N 460 -60 460 0 {}
N 530 -140 530 -30 {}
N 530 30 530 60 {}
N 590 0 590 94 {}
N 870 -140 870 -30 {}
N 870 30 870 60 {}
N 930 0 930 94 {}
N -1325 -140 1325 -140 {}
N -460 -60 -120 -60 {}
N 120 -60 460 -60 {}
N -930 0 -870 0 {}
N -830 0 -770 0 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N -250 0 -190 0 {}
N -150 0 150 0 {}
N 190 0 250 0 {}
N 460 0 490 0 {}
N 530 0 590 0 {}
N 800 0 830 0 {}
N 870 0 930 0 {}
N -870 70 -830 70 {}
C {devices/lab_wire.sym} -530 90 2 0 {name=l0 lab=VB4}
C {devices/lab_wire.sym} -770 0 0 1 {name=l1 lab=net1}
C {devices/lab_wire.sym} -430 0 0 1 {name=l2 lab=net1}
C {devices/lab_wire.sym} -930 94 2 0 {name=l3 lab=vdd}
C {devices/lab_wire.sym} -590 94 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} 590 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} 930 94 2 0 {name=l8 lab=vdd}
C {devices/iopin.sym} -1325 -140 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 800 0 0 0 {name=p1 lab=net1}
C {devices/opin.sym} -190 60 0 0 {name=p2 lab=DM_1}
C {devices/opin.sym} 190 60 0 0 {name=p3 lab=VB3}
C {devices/opin.sym} 530 60 0 0 {name=p4 lab=net31}
C {devices/opin.sym} 870 60 0 0 {name=p5 lab=net049}
C {devices/opin.sym} 1465 30 0 0 {name=p6 lab=VB4}
