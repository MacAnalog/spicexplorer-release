v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_018_telescopic_cascode} -720 -200 0 0 0.4 0.4 {}
C {devices/vsource_np.sym} -680 1040 0 0 {name=V1 value=x_dut_v_bias_2}
C {devices/vsource_np.sym} -680 780 0 0 {name=V2 value=x_dut_v_bias_1}
C {devices/sg13_lv_nmos_np.sym} -340 780 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 1 {name=M1C model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1c_w l=x_dut_xm1c_l m=x_dut_xm1c_m}
C {devices/sg13_lv_nmos_np.sym} 0 780 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 0 520 0 0 {name=M2C model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2c_w l=x_dut_xm2c_l m=x_dut_xm2c_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -340 260 0 1 {name=M3C model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3c_w l=x_dut_xm3c_l m=x_dut_xm3c_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 0 260 0 0 {name=M4C model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4c_w l=x_dut_xm4c_l m=x_dut_xm4c_m}
C {devices/sg13_lv_nmos_np.sym} -170 1040 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l ng=x_dut_xm5_ng m=x_dut_xm5_m}
C {devices/sg13_lv_nmos_np.sym} 340 1040 0 0 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
N -680 690 -680 750 {}
N -680 810 -680 870 {}
N -680 950 -680 1010 {}
N -680 1070 -680 1130 {}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -420 520 -420 614 {}
N -420 780 -420 874 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 490 {}
N -360 550 -360 750 {}
N -360 810 -360 870 {}
N -250 1040 -250 1134 {}
N -190 840 -190 1010 {}
N -190 1070 -190 1180 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 490 {}
N 20 550 20 750 {}
N 20 810 20 840 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 80 520 80 614 {}
N 80 780 80 874 {}
N 320 970 320 1040 {}
N 360 950 360 1010 {}
N 360 1070 360 1180 {}
N 420 1040 420 1134 {}
N -740 -140 550 -140 {}
N -420 0 -360 0 {}
N -320 0 -20 0 {}
N 20 0 80 0 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N -80 260 -20 260 {}
N 20 260 80 260 {}
N -360 320 -290 320 {}
N -420 520 -360 520 {}
N -320 520 -20 520 {}
N 20 520 80 520 {}
N -420 780 -360 780 {}
N -320 780 -260 780 {}
N -80 780 -20 780 {}
N 20 780 80 780 {}
N -360 840 20 840 {}
N 320 970 360 970 {}
N -250 1040 -190 1040 {}
N -150 1040 -90 1040 {}
N 360 1040 420 1040 {}
N -740 1180 550 1180 {}
C {devices/lab_wire.sym} -740 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -740 1180 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -260 520 0 1 {name=l2 lab=casc_n}
C {devices/lab_wire.sym} -360 610 2 0 {name=l3 lab=d1}
C {devices/lab_wire.sym} 20 610 2 0 {name=l4 lab=d2}
C {devices/lab_wire.sym} -360 350 2 0 {name=l5 lab=gate_p}
C {devices/lab_wire.sym} -260 0 0 1 {name=l6 lab=gate_p}
C {devices/lab_wire.sym} -260 260 0 1 {name=l7 lab=gate_pc}
C {devices/lab_wire.sym} -80 260 0 0 {name=l8 lab=gate_pc}
C {devices/lab_wire.sym} -90 1040 0 1 {name=l9 lab=ibias}
C {devices/lab_wire.sym} 360 950 0 1 {name=l10 lab=ibias}
C {devices/lab_wire.sym} -360 90 2 0 {name=l11 lab=s3}
C {devices/lab_wire.sym} 20 90 2 0 {name=l12 lab=s4}
C {devices/lab_wire.sym} -360 870 2 0 {name=l13 lab=tail}
C {devices/lab_wire.sym} -80 780 0 0 {name=l14 lab=vinn}
C {devices/lab_wire.sym} -260 780 0 1 {name=l15 lab=vinp}
C {devices/lab_wire.sym} 20 350 2 0 {name=l16 lab=vout}
C {devices/lab_wire.sym} -420 94 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l19 lab=vdd}
C {devices/lab_wire.sym} 80 354 2 0 {name=l20 lab=vdd}
C {devices/lab_wire.sym} -420 874 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} -420 614 2 0 {name=l22 lab=vss}
C {devices/lab_wire.sym} 80 874 2 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} 80 614 2 0 {name=l24 lab=vss}
C {devices/lab_wire.sym} -250 1134 2 0 {name=l25 lab=vss}
C {devices/lab_wire.sym} 420 1134 2 0 {name=l26 lab=vss}
C {devices/lab_wire.sym} -680 950 0 1 {name=l27 lab=vdd}
C {devices/lab_wire.sym} -680 1130 2 0 {name=l28 lab=gate_pc}
C {devices/lab_wire.sym} -680 690 0 1 {name=l29 lab=casc_n}
C {devices/lab_wire.sym} -680 870 2 0 {name=l30 lab=tail}
C {devices/ipin.sym} -880 780 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -880 900 0 0 {name=p1 lab=vinn}
C {devices/opin.sym} 690 290 0 0 {name=p2 lab=vout}
C {devices/opin.sym} 690 1010 0 0 {name=p3 lab=ibias}
