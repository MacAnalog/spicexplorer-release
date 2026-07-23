v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -420 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 875 0 0 0 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -380 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 580 0 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 350 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 125 0 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} -105 0 0 1 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -360 -90 -360 -30 {}
N -360 30 -360 90 {}
N -300 0 -300 94 {}
N -185 0 -185 94 {}
N -125 -60 -125 -30 {}
N -125 30 -125 90 {}
N -85 0 -85 60 {}
N 45 0 45 94 {}
N 105 -60 105 -30 {}
N 105 30 105 90 {}
N 145 0 145 60 {}
N 270 0 270 94 {}
N 330 -60 330 -30 {}
N 330 30 330 90 {}
N 600 -60 600 -30 {}
N 600 30 600 90 {}
N 660 0 660 94 {}
N 855 0 855 70 {}
N 895 -60 895 -30 {}
N 895 30 895 70 {}
N 955 0 955 94 {}
N -360 -60 895 -60 {}
N -460 0 -400 0 {}
N -360 0 -300 0 {}
N -185 0 -125 0 {}
N -85 0 -55 0 {}
N 45 0 105 0 {}
N 145 0 175 0 {}
N 270 0 330 0 {}
N 370 0 560 0 {}
N 600 0 660 0 {}
N 895 0 955 0 {}
N 855 70 895 70 {}
C {devices/lab_wire.sym} 600 90 2 0 {name=l0 lab=DM_1}
C {devices/lab_wire.sym} 330 90 2 0 {name=l1 lab=VB3}
C {devices/lab_wire.sym} -360 90 2 0 {name=l2 lab=VB4}
C {devices/lab_wire.sym} -125 90 2 0 {name=l3 lab=net049}
C {devices/lab_wire.sym} -460 0 0 0 {name=l4 lab=net1}
C {devices/lab_wire.sym} -85 60 2 0 {name=l5 lab=net1}
C {devices/lab_wire.sym} 145 60 2 0 {name=l6 lab=net1}
C {devices/lab_wire.sym} 430 0 0 1 {name=l7 lab=net1}
C {devices/lab_wire.sym} 855 0 0 0 {name=l8 lab=net1}
C {devices/lab_wire.sym} 105 90 2 0 {name=l9 lab=net31}
C {devices/lab_wire.sym} -360 -90 0 1 {name=l10 lab=vdd}
C {devices/lab_wire.sym} 955 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} -300 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} 660 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 270 94 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} 45 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} -185 94 2 0 {name=l16 lab=vdd}
C {devices/iopin.sym} -360 280 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 1225 0 0 0 {name=p1 lab=net1}
C {devices/opin.sym} 1225 120 0 0 {name=p2 lab=VB4}
C {devices/opin.sym} 1225 240 0 0 {name=p3 lab=net049}
C {devices/opin.sym} 1225 360 0 0 {name=p4 lab=net31}
C {devices/opin.sym} 1225 480 0 0 {name=p5 lab=VB3}
C {devices/opin.sym} 1225 600 0 0 {name=p6 lab=DM_1}
