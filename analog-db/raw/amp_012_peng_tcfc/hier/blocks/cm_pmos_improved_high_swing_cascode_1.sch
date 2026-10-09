v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_improved_high_swing_cascode_1} -720 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 680 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -680 260 0 1 {name=M57 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm57_w l=x_dut_xm57_l m=x_dut_xm57_m}
C {devices/sg13_lv_pmos_np.sym} -340 260 0 1 {name=M58 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm58_w l=x_dut_xm58_l m=x_dut_xm58_m}
C {devices/sg13_lv_pmos_np.sym} 0 260 0 0 {name=M61 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm61_w l=x_dut_xm61_l m=x_dut_xm61_m}
C {devices/sg13_lv_pmos_np.sym} 680 260 0 0 {name=M62 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm62_w l=x_dut_xm62_l m=x_dut_xm62_m}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 0 {name=M65 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm65_w l=x_dut_xm65_l m=x_dut_xm65_m}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -700 -140 -700 -30 {}
N -700 30 -700 230 {}
N -700 290 -700 350 {}
N -660 140 -660 260 {}
N -630 -60 -630 0 {}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 320 {}
N -290 -60 -290 0 {}
N -290 140 -290 260 {}
N -50 260 -50 380 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 320 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 320 0 320 70 {}
N 360 -140 360 -30 {}
N 360 30 360 380 {}
N 420 0 420 94 {}
N 700 -140 700 -30 {}
N 700 30 700 230 {}
N 700 290 700 320 {}
N 760 0 760 94 {}
N 760 260 760 354 {}
N -1180 -140 1180 -140 {}
N -630 -60 -290 -60 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -420 0 -360 0 {}
N -320 0 -20 0 {}
N 20 0 80 0 {}
N 360 0 420 0 {}
N 630 0 660 0 {}
N 700 0 760 0 {}
N 320 70 360 70 {}
N -660 140 -290 140 {}
N -760 260 -700 260 {}
N -420 260 -360 260 {}
N -320 260 -20 260 {}
N 20 260 80 260 {}
N 360 260 660 260 {}
N 700 260 760 260 {}
N -50 380 360 380 {}
C {devices/lab_wire.sym} -700 350 2 0 {name=l0 lab=VB1}
C {devices/lab_wire.sym} -600 0 0 1 {name=l1 lab=VB1}
C {devices/lab_wire.sym} -700 90 2 0 {name=l2 lab=net2}
C {devices/lab_wire.sym} -360 90 2 0 {name=l3 lab=net3}
C {devices/lab_wire.sym} 20 90 2 0 {name=l4 lab=net6}
C {devices/lab_wire.sym} 700 90 2 0 {name=l5 lab=net8}
C {devices/lab_wire.sym} -760 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l8 lab=vdd}
C {devices/lab_wire.sym} 760 94 2 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} 80 354 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} 760 354 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l14 lab=vdd}
C {devices/iopin.sym} -1180 -140 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 630 0 0 0 {name=p1 lab=VB1}
C {devices/opin.sym} 630 260 0 0 {name=p2 lab=VB2}
C {devices/opin.sym} -360 320 0 0 {name=p3 lab=VB4}
C {devices/opin.sym} 20 320 0 0 {name=p4 lab=net7}
C {devices/opin.sym} 700 320 0 0 {name=p5 lab=VB3}
