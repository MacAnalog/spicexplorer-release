v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_improved_high_swing_cascode_1} -720 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} -680 260 0 1 {name=M60 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm60_w l=x_dut_xm60_l m=x_dut_xm60_m}
C {devices/sg13_lv_pmos_np.sym} 340 260 0 0 {name=M61 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm61_w l=x_dut_xm61_l m=x_dut_xm61_m}
C {devices/sg13_lv_pmos_np.sym} 680 260 0 0 {name=M62 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm62_w l=x_dut_xm62_l m=x_dut_xm62_m}
C {devices/sg13_lv_pmos_np.sym} -340 260 0 1 {name=M63 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm63_w l=x_dut_xm63_l m=x_dut_xm63_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M68 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm68_w l=x_dut_xm68_l m=x_dut_xm68_m}
C {devices/sg13_lv_pmos_np.sym} 680 0 0 0 {name=M69 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm69_w l=x_dut_xm69_l m=x_dut_xm69_m}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -700 -140 -700 -30 {}
N -700 30 -700 230 {}
N -700 290 -700 350 {}
N -660 260 -660 320 {}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -320 260 -320 320 {}
N -230 0 -230 290 {}
N -20 0 -20 70 {}
N 20 -140 20 -30 {}
N 20 30 20 260 {}
N 80 60 80 260 {}
N 290 260 290 320 {}
N 360 -140 360 -30 {}
N 360 30 360 230 {}
N 360 290 360 350 {}
N 420 0 420 94 {}
N 420 260 420 354 {}
N 630 260 630 320 {}
N 700 -140 700 -30 {}
N 700 30 700 230 {}
N 700 290 700 320 {}
N 760 0 760 94 {}
N 760 260 760 354 {}
N -1180 -140 1180 -140 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -420 0 -360 0 {}
N -320 0 -230 0 {}
N 260 0 320 0 {}
N 360 0 420 0 {}
N 630 0 660 0 {}
N 700 0 760 0 {}
N 20 60 80 60 {}
N -20 70 20 70 {}
N -760 260 -700 260 {}
N -420 260 -360 260 {}
N -320 260 320 260 {}
N 360 260 420 260 {}
N 630 260 660 260 {}
N 700 260 760 260 {}
N -360 290 -230 290 {}
N -660 320 -320 320 {}
N 290 320 630 320 {}
C {devices/lab_wire.sym} -700 350 2 0 {name=l0 lab=VOUTN}
C {devices/lab_wire.sym} -600 0 0 1 {name=l1 lab=VOUTN}
C {devices/lab_wire.sym} 260 0 0 0 {name=l2 lab=VOUTN}
C {devices/lab_wire.sym} 360 90 2 0 {name=l3 lab=net050}
C {devices/lab_wire.sym} -360 90 2 0 {name=l4 lab=net2}
C {devices/lab_wire.sym} 700 90 2 0 {name=l5 lab=net3}
C {devices/lab_wire.sym} 360 350 2 0 {name=l6 lab=net4}
C {devices/lab_wire.sym} -700 90 2 0 {name=l7 lab=net5}
C {devices/lab_wire.sym} -260 0 0 1 {name=l8 lab=net70}
C {devices/lab_wire.sym} 20 0 0 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} -760 94 2 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} 420 354 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 760 354 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 760 94 2 0 {name=l17 lab=vdd}
C {devices/iopin.sym} -1180 -140 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 700 320 0 0 {name=p1 lab=VOUTN}
C {devices/opin.sym} 630 0 0 0 {name=p2 lab=net70}
C {devices/opin.sym} 630 260 0 0 {name=p3 lab=DM_1}
C {devices/opin.sym} 1320 290 0 0 {name=p4 lab=net4}
