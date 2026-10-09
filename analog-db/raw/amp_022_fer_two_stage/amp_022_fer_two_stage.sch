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
C {devices/sg13_lv_nmos_np.sym} 10 260 0 1 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} -680 520 0 1 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 10 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 690 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_nmos_np.sym} 350 520 0 1 {name=MBD model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbd_w l=x_dut_xmbd_l m=x_dut_xmbd_m}
C {devices/sg13_lv_nmos_np.sym} 690 260 0 0 {name=MBS model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbs_w l=x_dut_xmbs_l m=x_dut_xmbs_m}
N -760 260 -760 354 {}
N -760 520 -760 614 {}
N -700 200 -700 230 {}
N -700 290 -700 490 {}
N -700 550 -700 660 {}
N -660 450 -660 520 {}
N -590 0 -590 94 {}
N -530 -140 -530 -30 {}
N -530 30 -530 200 {}
N -490 0 -490 60 {}
N -460 -60 -460 0 {}
N -390 460 -390 520 {}
N -340 330 -340 360 {}
N -340 420 -340 450 {}
N -320 200 -320 230 {}
N -320 290 -320 490 {}
N -320 550 -320 660 {}
N -260 260 -260 354 {}
N -260 520 -260 614 {}
N -70 0 -70 94 {}
N -70 260 -70 354 {}
N -10 -140 -10 -30 {}
N -10 30 -10 230 {}
N -10 290 -10 660 {}
N 60 -60 60 0 {}
N 60 260 60 320 {}
N 110 200 110 450 {}
N 270 520 270 614 {}
N 330 450 330 490 {}
N 330 550 330 660 {}
N 370 450 370 520 {}
N 640 260 640 460 {}
N 670 0 670 70 {}
N 710 -140 710 -30 {}
N 710 30 710 230 {}
N 710 290 710 660 {}
N 770 0 770 94 {}
N 770 260 770 354 {}
N -1155 -140 1190 -140 {}
N -460 -60 60 -60 {}
N -590 0 -530 0 {}
N -490 0 -460 0 {}
N -70 0 -10 0 {}
N 0 0 670 0 {}
N 710 0 770 0 {}
N 670 70 710 70 {}
N -700 200 -320 200 {}
N -10 200 110 200 {}
N -760 260 -700 260 {}
N -660 260 -630 260 {}
N -450 260 -360 260 {}
N -320 260 -260 260 {}
N -70 260 -10 260 {}
N 30 260 90 260 {}
N 640 260 670 260 {}
N 710 260 770 260 {}
N -320 320 60 320 {}
N -340 330 -320 330 {}
N -700 450 -660 450 {}
N -340 450 110 450 {}
N 330 450 370 450 {}
N -700 460 -390 460 {}
N 330 460 640 460 {}
N -760 520 -700 520 {}
N -390 520 -360 520 {}
N -320 520 -260 520 {}
N 270 520 330 520 {}
N -1155 660 1190 660 {}
C {devices/lab_wire.sym} -700 350 2 0 {name=l0 lab=a}
C {devices/lab_wire.sym} 90 260 0 1 {name=l1 lab=b}
C {devices/lab_wire.sym} -530 90 2 0 {name=l2 lab=c}
C {devices/lab_wire.sym} -490 60 2 0 {name=l3 lab=pbias}
C {devices/lab_wire.sym} -760 354 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} -260 354 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} -590 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} -70 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} 770 94 2 0 {name=l8 lab=vdd}
C {devices/lab_wire.sym} -70 354 2 0 {name=l9 lab=vss}
C {devices/lab_wire.sym} -760 614 2 0 {name=l10 lab=vss}
C {devices/lab_wire.sym} -260 614 2 0 {name=l11 lab=vss}
C {devices/lab_wire.sym} 270 614 2 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} 770 354 2 0 {name=l13 lab=vss}
C {devices/ipin.sym} -630 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -450 260 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -1155 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1155 660 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 110 200 0 0 {name=p4 lab=vout}
C {devices/opin.sym} 640 260 0 0 {name=p5 lab=ibias}
