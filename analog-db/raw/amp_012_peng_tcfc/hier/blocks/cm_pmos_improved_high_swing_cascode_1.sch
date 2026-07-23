v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_improved_high_swing_cascode_1} -1060 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 1115 0 0 0 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} 525 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 115 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -475 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -1020 0 0 1 {name=M57 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm57_w l=x_dut_xm57_l m=x_dut_xm57_m}
C {devices/sg13_lv_pmos_np.sym} -180 0 0 1 {name=M58 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm58_w l=x_dut_xm58_l m=x_dut_xm58_m}
C {devices/sg13_lv_pmos_np.sym} 820 0 0 0 {name=M61 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm61_w l=x_dut_xm61_l m=x_dut_xm61_m}
C {devices/sg13_lv_pmos_np.sym} 1340 0 0 0 {name=M62 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm62_w l=x_dut_xm62_l m=x_dut_xm62_m}
C {devices/sg13_lv_pmos_np.sym} 320 0 0 0 {name=M65 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm65_w l=x_dut_xm65_l m=x_dut_xm65_m}
N -1100 0 -1100 94 {}
N -1040 -90 -1040 -30 {}
N -1040 30 -1040 90 {}
N -555 0 -555 94 {}
N -495 -90 -495 -30 {}
N -495 30 -495 90 {}
N -455 0 -455 60 {}
N -260 0 -260 94 {}
N -200 -90 -200 -30 {}
N -200 30 -200 90 {}
N -160 0 -160 60 {}
N 35 0 35 94 {}
N 95 -90 95 -30 {}
N 95 30 95 90 {}
N 300 0 300 70 {}
N 340 -90 340 -30 {}
N 340 30 340 70 {}
N 400 0 400 94 {}
N 505 -60 505 0 {}
N 545 -90 545 -30 {}
N 545 30 545 90 {}
N 605 0 605 94 {}
N 800 -60 800 0 {}
N 840 -90 840 -30 {}
N 840 30 840 90 {}
N 900 0 900 94 {}
N 1095 -60 1095 0 {}
N 1135 -90 1135 -30 {}
N 1135 30 1135 90 {}
N 1195 0 1195 94 {}
N 1320 -60 1320 0 {}
N 1360 -90 1360 -30 {}
N 1360 30 1360 90 {}
N 1420 0 1420 94 {}
N -1100 0 -1040 0 {}
N -1000 0 -940 0 {}
N -555 0 -495 0 {}
N -455 0 -425 0 {}
N -260 0 -200 0 {}
N -160 0 -130 0 {}
N 35 0 95 0 {}
N 135 0 195 0 {}
N 240 0 300 0 {}
N 340 0 400 0 {}
N 475 0 505 0 {}
N 545 0 605 0 {}
N 770 0 800 0 {}
N 840 0 900 0 {}
N 1065 0 1095 0 {}
N 1135 0 1195 0 {}
N 1290 0 1320 0 {}
N 1360 0 1420 0 {}
N 300 70 340 70 {}
C {devices/lab_wire.sym} -1040 90 2 0 {name=l0 lab=VB1}
C {devices/lab_wire.sym} -455 60 2 0 {name=l1 lab=VB1}
C {devices/lab_wire.sym} 195 0 0 1 {name=l2 lab=VB1}
C {devices/lab_wire.sym} 505 -60 0 1 {name=l3 lab=VB1}
C {devices/lab_wire.sym} 1095 -60 0 1 {name=l4 lab=VB1}
C {devices/lab_wire.sym} -940 0 0 1 {name=l5 lab=VB2}
C {devices/lab_wire.sym} -160 60 2 0 {name=l6 lab=VB2}
C {devices/lab_wire.sym} 240 0 0 0 {name=l7 lab=VB2}
C {devices/lab_wire.sym} 800 -60 0 1 {name=l8 lab=VB2}
C {devices/lab_wire.sym} 1320 -60 0 1 {name=l9 lab=VB2}
C {devices/lab_wire.sym} 1360 90 2 0 {name=l10 lab=VB3}
C {devices/lab_wire.sym} -200 90 2 0 {name=l11 lab=VB4}
C {devices/lab_wire.sym} -1040 -90 0 1 {name=l12 lab=net2}
C {devices/lab_wire.sym} 1135 90 2 0 {name=l13 lab=net2}
C {devices/lab_wire.sym} -200 -90 0 1 {name=l14 lab=net3}
C {devices/lab_wire.sym} 545 90 2 0 {name=l15 lab=net3}
C {devices/lab_wire.sym} 95 90 2 0 {name=l16 lab=net6}
C {devices/lab_wire.sym} 840 -90 0 1 {name=l17 lab=net6}
C {devices/lab_wire.sym} 840 90 2 0 {name=l18 lab=net7}
C {devices/lab_wire.sym} -495 90 2 0 {name=l19 lab=net8}
C {devices/lab_wire.sym} 1360 -90 0 1 {name=l20 lab=net8}
C {devices/lab_wire.sym} -495 -90 0 1 {name=l21 lab=vdd}
C {devices/lab_wire.sym} 95 -90 0 1 {name=l22 lab=vdd}
C {devices/lab_wire.sym} 340 -90 0 1 {name=l23 lab=vdd}
C {devices/lab_wire.sym} 545 -90 0 1 {name=l24 lab=vdd}
C {devices/lab_wire.sym} 1135 -90 0 1 {name=l25 lab=vdd}
C {devices/lab_wire.sym} 1195 94 2 0 {name=l26 lab=vdd}
C {devices/lab_wire.sym} 605 94 2 0 {name=l27 lab=vdd}
C {devices/lab_wire.sym} 35 94 2 0 {name=l28 lab=vdd}
C {devices/lab_wire.sym} -555 94 2 0 {name=l29 lab=vdd}
C {devices/lab_wire.sym} -1100 94 2 0 {name=l30 lab=vdd}
C {devices/lab_wire.sym} -260 94 2 0 {name=l31 lab=vdd}
C {devices/lab_wire.sym} 900 94 2 0 {name=l32 lab=vdd}
C {devices/lab_wire.sym} 1420 94 2 0 {name=l33 lab=vdd}
C {devices/lab_wire.sym} 400 94 2 0 {name=l34 lab=vdd}
C {devices/iopin.sym} -495 280 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 1695 0 0 0 {name=p1 lab=VB2}
C {devices/opin.sym} 1695 120 0 0 {name=p2 lab=VB1}
C {devices/opin.sym} 1695 240 0 0 {name=p3 lab=VB4}
C {devices/opin.sym} 1695 360 0 0 {name=p4 lab=net7}
C {devices/opin.sym} 1695 480 0 0 {name=p5 lab=VB3}
