v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -1060 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} -1020 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 680 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 1020 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -1100 0 -1100 94 {}
N -1040 -140 -1040 -30 {}
N -1040 30 -1040 70 {}
N -1000 0 -1000 70 {}
N -760 0 -760 94 {}
N -700 -140 -700 -30 {}
N -700 30 -700 90 {}
N -630 -60 -630 0 {}
N -420 0 -420 94 {}
N -360 -140 -360 -30 {}
N -360 30 -360 60 {}
N -290 -60 -290 0 {}
N -50 -60 -50 0 {}
N 20 -140 20 -30 {}
N 20 30 20 60 {}
N 80 0 80 94 {}
N 290 -60 290 0 {}
N 360 -140 360 -30 {}
N 360 30 360 60 {}
N 420 0 420 94 {}
N 700 -140 700 -30 {}
N 700 30 700 60 {}
N 760 0 760 94 {}
N 1040 -140 1040 -30 {}
N 1040 30 1040 60 {}
N 1100 0 1100 94 {}
N -1495 -140 1495 -140 {}
N -630 -60 -290 -60 {}
N -50 -60 290 -60 {}
N -1100 0 -1040 0 {}
N -1000 0 -940 0 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -420 0 -360 0 {}
N -320 0 -20 0 {}
N 20 0 80 0 {}
N 290 0 320 0 {}
N 360 0 420 0 {}
N 600 0 660 0 {}
N 700 0 760 0 {}
N 970 0 1000 0 {}
N 1040 0 1100 0 {}
N -1040 70 -1000 70 {}
C {devices/lab_wire.sym} -940 0 0 1 {name=l0 lab=ib}
C {devices/lab_wire.sym} -600 0 0 1 {name=l1 lab=ib}
C {devices/lab_wire.sym} 600 0 0 0 {name=l2 lab=ib}
C {devices/lab_wire.sym} -700 90 2 0 {name=l3 lab=vb4}
C {devices/lab_wire.sym} -1100 94 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} -760 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l8 lab=vdd}
C {devices/lab_wire.sym} 760 94 2 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} 1100 94 2 0 {name=l10 lab=vdd}
C {devices/iopin.sym} -1495 -140 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 970 0 0 0 {name=p1 lab=ib}
C {devices/opin.sym} -360 60 0 0 {name=p2 lab=dm_1}
C {devices/opin.sym} 20 60 0 0 {name=p3 lab=net1}
C {devices/opin.sym} 360 60 0 0 {name=p4 lab=vb3}
C {devices/opin.sym} 700 60 0 0 {name=p5 lab=net20}
C {devices/opin.sym} 1040 60 0 0 {name=p6 lab=net7}
C {devices/opin.sym} 1635 30 0 0 {name=p7 lab=vb4}
