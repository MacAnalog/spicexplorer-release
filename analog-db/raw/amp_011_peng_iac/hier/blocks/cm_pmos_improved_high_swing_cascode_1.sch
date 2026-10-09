v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_improved_high_swing_cascode_1} -890 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} -850 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -850 260 0 1 {name=M57 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm57_w l=x_dut_xm57_l m=x_dut_xm57_m}
C {devices/sg13_lv_pmos_np.sym} -510 260 0 1 {name=M58 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm58_w l=x_dut_xm58_l m=x_dut_xm58_m}
C {devices/sg13_lv_pmos_np.sym} -170 260 0 1 {name=M61 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm61_w l=x_dut_xm61_l m=x_dut_xm61_m}
C {devices/sg13_lv_pmos_np.sym} 170 260 0 0 {name=M62 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm62_w l=x_dut_xm62_l m=x_dut_xm62_m}
C {devices/sg13_lv_pmos_np.sym} 510 0 0 0 {name=M65 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm65_w l=x_dut_xm65_l m=x_dut_xm65_m}
C {devices/sg13_lv_pmos_np.sym} 850 260 0 0 {name=M66 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm66_w l=x_dut_xm66_l m=x_dut_xm66_m}
C {devices/sg13_lv_pmos_np.sym} 850 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -930 0 -930 94 {}
N -930 260 -930 354 {}
N -870 -140 -870 -30 {}
N -870 30 -870 230 {}
N -870 290 -870 350 {}
N -590 0 -590 94 {}
N -590 260 -590 354 {}
N -530 -140 -530 -30 {}
N -530 30 -530 230 {}
N -530 290 -530 320 {}
N -460 -60 -460 0 {}
N -460 140 -460 260 {}
N -250 0 -250 94 {}
N -250 260 -250 354 {}
N -190 -140 -190 -30 {}
N -190 30 -190 230 {}
N -190 290 -190 320 {}
N -120 -60 -120 0 {}
N -120 140 -120 260 {}
N 120 260 120 380 {}
N 190 -140 190 -30 {}
N 190 30 190 230 {}
N 190 290 190 320 {}
N 250 0 250 94 {}
N 250 260 250 354 {}
N 490 0 490 70 {}
N 530 -140 530 -30 {}
N 530 30 530 380 {}
N 590 0 590 94 {}
N 870 -140 870 -30 {}
N 870 30 870 230 {}
N 870 290 870 320 {}
N 930 0 930 94 {}
N 930 260 930 354 {}
N -1350 -140 1350 -140 {}
N -460 -60 -120 -60 {}
N -930 0 -870 0 {}
N -830 0 -770 0 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N -250 0 -190 0 {}
N -150 0 150 0 {}
N 190 0 250 0 {}
N 530 0 590 0 {}
N 800 0 830 0 {}
N 870 0 930 0 {}
N 490 70 530 70 {}
N -460 140 -120 140 {}
N -930 260 -870 260 {}
N -830 260 -770 260 {}
N -590 260 -530 260 {}
N -490 260 -460 260 {}
N -250 260 -190 260 {}
N -150 260 150 260 {}
N 190 260 250 260 {}
N 530 260 830 260 {}
N 870 260 930 260 {}
N 120 380 530 380 {}
C {devices/lab_wire.sym} -870 350 2 0 {name=l0 lab=VB1}
C {devices/lab_wire.sym} -770 0 0 1 {name=l1 lab=VB1}
C {devices/lab_wire.sym} -430 0 0 1 {name=l2 lab=VB1}
C {devices/lab_wire.sym} -770 260 0 1 {name=l3 lab=VB2}
C {devices/lab_wire.sym} 870 90 2 0 {name=l4 lab=net049}
C {devices/lab_wire.sym} -870 90 2 0 {name=l5 lab=net2}
C {devices/lab_wire.sym} -530 90 2 0 {name=l6 lab=net3}
C {devices/lab_wire.sym} -190 90 2 0 {name=l7 lab=net6}
C {devices/lab_wire.sym} 190 90 2 0 {name=l8 lab=net8}
C {devices/lab_wire.sym} -930 94 2 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} -590 94 2 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -930 354 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} -590 354 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} -250 354 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 250 354 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 590 94 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} 930 354 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} 930 94 2 0 {name=l19 lab=vdd}
C {devices/iopin.sym} -1350 -140 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 800 0 0 0 {name=p1 lab=VB1}
C {devices/opin.sym} 800 260 0 0 {name=p2 lab=VB2}
C {devices/opin.sym} -530 320 0 0 {name=p3 lab=VB4}
C {devices/opin.sym} -190 320 0 0 {name=p4 lab=net7}
C {devices/opin.sym} 190 320 0 0 {name=p5 lab=VB3}
C {devices/opin.sym} 870 320 0 0 {name=p6 lab=net10}
