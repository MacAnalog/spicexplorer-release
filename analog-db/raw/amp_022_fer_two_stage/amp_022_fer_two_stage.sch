v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_022_fer_two_stage} -720 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -340 390 0 0 {name=CC value=x_dut_cc_value}
C {devices/sg13_lv_pmos_np.sym} -680 260 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -340 260 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 1 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} -680 520 0 1 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 680 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_nmos_np.sym} 340 520 0 1 {name=MBD model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbd_w l=x_dut_xmbd_l m=x_dut_xmbd_m}
C {devices/sg13_lv_nmos_np.sym} 680 260 0 0 {name=MBS model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbs_w l=x_dut_xmbs_l m=x_dut_xmbs_m}
N -760 260 -760 354 {}
N -760 520 -760 614 {}
N -700 200 -700 230 {}
N -700 290 -700 490 {}
N -700 550 -700 660 {}
N -660 450 -660 520 {}
N -590 0 -590 94 {}
N -530 -140 -530 -30 {}
N -530 30 -530 200 {}
N -390 460 -390 520 {}
N -340 330 -340 360 {}
N -340 420 -340 450 {}
N -320 200 -320 230 {}
N -320 290 -320 490 {}
N -320 550 -320 660 {}
N -260 260 -260 354 {}
N -260 520 -260 614 {}
N -80 0 -80 94 {}
N -80 260 -80 354 {}
N -20 -140 -20 -30 {}
N -20 30 -20 230 {}
N -20 290 -20 350 {}
N 50 260 50 320 {}
N 260 520 260 614 {}
N 320 450 320 490 {}
N 320 550 320 660 {}
N 360 450 360 520 {}
N 630 260 630 460 {}
N 660 0 660 70 {}
N 700 -140 700 -30 {}
N 700 30 700 230 {}
N 700 290 700 660 {}
N 760 0 760 94 {}
N 760 260 760 354 {}
N -890 -140 895 -140 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N -80 0 -20 0 {}
N 20 0 80 0 {}
N 600 0 660 0 {}
N 700 0 760 0 {}
N 660 70 700 70 {}
N -700 200 -320 200 {}
N -760 260 -700 260 {}
N -660 260 -600 260 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N -80 260 -20 260 {}
N 20 260 80 260 {}
N 600 260 660 260 {}
N 700 260 760 260 {}
N -320 320 50 320 {}
N -340 330 -320 330 {}
N -400 420 -340 420 {}
N -700 450 -660 450 {}
N 320 450 360 450 {}
N -700 460 -390 460 {}
N 320 460 630 460 {}
N -760 520 -700 520 {}
N -390 520 -360 520 {}
N -320 520 -260 520 {}
N 260 520 320 520 {}
N -890 660 895 660 {}
C {devices/lab_wire.sym} -890 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -890 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -700 350 2 0 {name=l2 lab=a}
C {devices/lab_wire.sym} 80 260 0 1 {name=l3 lab=b}
C {devices/lab_wire.sym} -530 90 2 0 {name=l4 lab=c}
C {devices/lab_wire.sym} 600 260 0 0 {name=l5 lab=ibias}
C {devices/lab_wire.sym} -430 0 0 1 {name=l6 lab=pbias}
C {devices/lab_wire.sym} 80 0 0 1 {name=l7 lab=pbias}
C {devices/lab_wire.sym} 600 0 0 0 {name=l8 lab=pbias}
C {devices/lab_wire.sym} -600 260 0 1 {name=l9 lab=vinn}
C {devices/lab_wire.sym} -420 260 0 0 {name=l10 lab=vinp}
C {devices/lab_wire.sym} -400 420 0 0 {name=l11 lab=vout}
C {devices/lab_wire.sym} -20 90 2 0 {name=l12 lab=vout}
C {devices/lab_wire.sym} -760 354 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} -260 354 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} -590 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} -80 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 760 94 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} -80 354 2 0 {name=l18 lab=vss}
C {devices/lab_wire.sym} -760 614 2 0 {name=l19 lab=vss}
C {devices/lab_wire.sym} -260 614 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} 260 614 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} 760 354 2 0 {name=l22 lab=vss}
C {devices/lab_wire.sym} -20 350 2 0 {name=l23 lab=vss}
C {devices/ipin.sym} -1030 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -1030 380 0 0 {name=p1 lab=vinp}
C {devices/opin.sym} 1035 30 0 0 {name=p2 lab=vout}
C {devices/opin.sym} 1035 260 0 0 {name=p3 lab=ibias}
