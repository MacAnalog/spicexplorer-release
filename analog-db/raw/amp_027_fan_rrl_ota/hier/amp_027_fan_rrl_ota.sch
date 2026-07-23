v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_027_fan_rrl_ota} -1360 -540 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -1100 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_pmos_cascode_1.sym} -660 0 0 0 {name=xdp_pmos_cascode_1}
C {blocks/dp_pmos_simple_1.sym} -220 0 0 0 {name=xdp_pmos_simple_1}
C {blocks/dp_pmos_simple_2.sym} 220 0 0 0 {name=xdp_pmos_simple_2}
C {blocks/dp_pmos_simple_3.sym} 660 0 0 0 {name=xdp_pmos_simple_3}
C {blocks/dp_pmos_simple_4.sym} 1100 0 0 0 {name=xdp_pmos_simple_4}
C {devices/vsource_np.sym} -1320 340 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -1320 120 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -1320 -100 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -1320 -320 0 0 {name=VB4 value="dc {vb4}"}
C {devices/sg13_lv_pmos_np.sym} -110 -340 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} -220 340 0 0 {name=M11 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} 0 340 0 0 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 220 340 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} 110 -340 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
N -990 -40 -950 -40 {}
C {devices/lab_wire.sym} -950 -40 0 1 {name=l0 lab=cm_bias}
N -990 0 -950 0 {}
C {devices/lab_wire.sym} -950 0 0 1 {name=l1 lab=csrc_n}
N -990 40 -950 40 {}
C {devices/lab_wire.sym} -950 40 0 1 {name=l2 lab=csrc_p}
N -1100 100 -1100 140 {}
C {devices/lab_wire.sym} -1100 140 2 0 {name=l3 lab=vss}
N -770 -40 -810 -40 {}
C {devices/lab_wire.sym} -810 -40 0 0 {name=l4 lab=vb1}
N -770 0 -810 0 {}
C {devices/lab_wire.sym} -810 0 0 0 {name=l5 lab=vinn}
N -770 40 -810 40 {}
C {devices/lab_wire.sym} -810 40 0 0 {name=l6 lab=vinp}
N -550 -40 -510 -40 {}
C {devices/lab_wire.sym} -510 -40 0 1 {name=l7 lab=tail}
N -550 0 -510 0 {}
C {devices/lab_wire.sym} -510 0 0 1 {name=l8 lab=voutn}
N -550 40 -510 40 {}
C {devices/lab_wire.sym} -510 40 0 1 {name=l9 lab=voutp}
N -660 -100 -660 -140 {}
C {devices/lab_wire.sym} -660 -140 0 1 {name=l10 lab=vdd}
N -330 -20 -370 -20 {}
C {devices/lab_wire.sym} -370 -20 0 0 {name=l11 lab=vb4}
N -330 20 -370 20 {}
C {devices/lab_wire.sym} -370 20 0 0 {name=l12 lab=voutn}
N -110 -40 -70 -40 {}
C {devices/lab_wire.sym} -70 -40 0 1 {name=l13 lab=cm_bias}
N -110 0 -70 0 {}
C {devices/lab_wire.sym} -70 0 0 1 {name=l14 lab=cm_sense}
N -110 40 -70 40 {}
C {devices/lab_wire.sym} -70 40 0 1 {name=l15 lab=cm_tail}
N -220 -100 -220 -140 {}
C {devices/lab_wire.sym} -220 -140 0 1 {name=l16 lab=vdd}
N 110 -20 70 -20 {}
C {devices/lab_wire.sym} 70 -20 0 0 {name=l17 lab=vb4}
N 110 20 70 20 {}
C {devices/lab_wire.sym} 70 20 0 0 {name=l18 lab=voutn}
N 330 -40 370 -40 {}
C {devices/lab_wire.sym} 370 -40 0 1 {name=l19 lab=cm_bias}
N 330 0 370 0 {}
C {devices/lab_wire.sym} 370 0 0 1 {name=l20 lab=cm_sense}
N 330 40 370 40 {}
C {devices/lab_wire.sym} 370 40 0 1 {name=l21 lab=cm_tail}
N 220 -100 220 -140 {}
C {devices/lab_wire.sym} 220 -140 0 1 {name=l22 lab=vdd}
N 550 -20 510 -20 {}
C {devices/lab_wire.sym} 510 -20 0 0 {name=l23 lab=vb4}
N 550 20 510 20 {}
C {devices/lab_wire.sym} 510 20 0 0 {name=l24 lab=voutp}
N 770 -40 810 -40 {}
C {devices/lab_wire.sym} 810 -40 0 1 {name=l25 lab=cm_bias}
N 770 0 810 0 {}
C {devices/lab_wire.sym} 810 0 0 1 {name=l26 lab=cm_sense}
N 770 40 810 40 {}
C {devices/lab_wire.sym} 810 40 0 1 {name=l27 lab=cm_tail}
N 660 -100 660 -140 {}
C {devices/lab_wire.sym} 660 -140 0 1 {name=l28 lab=vdd}
N 990 -20 950 -20 {}
C {devices/lab_wire.sym} 950 -20 0 0 {name=l29 lab=vb4}
N 990 20 950 20 {}
C {devices/lab_wire.sym} 950 20 0 0 {name=l30 lab=voutp}
N 1210 -40 1250 -40 {}
C {devices/lab_wire.sym} 1250 -40 0 1 {name=l31 lab=cm_bias}
N 1210 0 1250 0 {}
C {devices/lab_wire.sym} 1250 0 0 1 {name=l32 lab=cm_sense}
N 1210 40 1250 40 {}
C {devices/lab_wire.sym} 1250 40 0 1 {name=l33 lab=cm_tail}
N 1100 -100 1100 -140 {}
C {devices/lab_wire.sym} 1100 -140 0 1 {name=l34 lab=vdd}
N -1320 310 -1320 270 {}
C {devices/lab_wire.sym} -1320 270 0 1 {name=l35 lab=vb1}
N -1320 370 -1320 410 {}
C {devices/lab_wire.sym} -1320 410 2 0 {name=l36 lab=vss}
N -1320 90 -1320 50 {}
C {devices/lab_wire.sym} -1320 50 0 1 {name=l37 lab=vb2}
N -1320 150 -1320 190 {}
C {devices/lab_wire.sym} -1320 190 2 0 {name=l38 lab=vss}
N -1320 -130 -1320 -170 {}
C {devices/lab_wire.sym} -1320 -170 0 1 {name=l39 lab=vb3}
N -1320 -70 -1320 -30 {}
C {devices/lab_wire.sym} -1320 -30 2 0 {name=l40 lab=vss}
N -1320 -350 -1320 -390 {}
C {devices/lab_wire.sym} -1320 -390 0 1 {name=l41 lab=vb4}
N -1320 -290 -1320 -250 {}
C {devices/lab_wire.sym} -1320 -250 2 0 {name=l42 lab=vss}
N -90 -310 -90 -270 {}
C {devices/lab_wire.sym} -90 -270 2 0 {name=l43 lab=tail}
N -130 -340 -170 -340 {}
C {devices/lab_wire.sym} -170 -340 0 0 {name=l44 lab=vb3}
N -90 -370 -90 -410 {}
C {devices/lab_wire.sym} -90 -410 0 1 {name=l45 lab=vdd}
N -90 -340 -50 -340 {}
C {devices/lab_wire.sym} -50 -340 0 1 {name=l46 lab=vdd}
N -200 310 -200 270 {}
C {devices/lab_wire.sym} -200 270 0 1 {name=l47 lab=voutn}
N -240 340 -280 340 {}
C {devices/lab_wire.sym} -280 340 0 0 {name=l48 lab=vb2}
N -200 370 -200 410 {}
C {devices/lab_wire.sym} -200 410 2 0 {name=l49 lab=csrc_n}
N -200 340 -160 340 {}
C {devices/lab_wire.sym} -160 340 0 1 {name=l50 lab=vss}
N 20 310 20 270 {}
C {devices/lab_wire.sym} 20 270 0 1 {name=l51 lab=voutp}
N -20 340 -60 340 {}
C {devices/lab_wire.sym} -60 340 0 0 {name=l52 lab=vb2}
N 20 370 20 410 {}
C {devices/lab_wire.sym} 20 410 2 0 {name=l53 lab=csrc_p}
N 20 340 60 340 {}
C {devices/lab_wire.sym} 60 340 0 1 {name=l54 lab=vss}
N 240 310 240 270 {}
C {devices/lab_wire.sym} 240 270 0 1 {name=l55 lab=cm_sense}
N 200 340 160 340 {}
C {devices/lab_wire.sym} 160 340 0 0 {name=l56 lab=cm_sense}
N 240 370 240 410 {}
C {devices/lab_wire.sym} 240 410 2 0 {name=l57 lab=vss}
N 240 340 280 340 {}
C {devices/lab_wire.sym} 280 340 0 1 {name=l58 lab=vss}
N 130 -310 130 -270 {}
C {devices/lab_wire.sym} 130 -270 2 0 {name=l59 lab=cm_tail}
N 90 -340 50 -340 {}
C {devices/lab_wire.sym} 50 -340 0 0 {name=l60 lab=vb3}
N 130 -370 130 -410 {}
C {devices/lab_wire.sym} 130 -410 0 1 {name=l61 lab=vdd}
N 130 -340 170 -340 {}
C {devices/lab_wire.sym} 170 -340 0 1 {name=l62 lab=vdd}
