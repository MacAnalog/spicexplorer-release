v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_021_yan_az} -1470 -560 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -660 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_simple_1.sym} -220 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_2.sym} 220 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/dp_pmos_simple_1.sym} 660 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -1210 360 0 0 {name=C0 value='CAPACITOR_1'}
C {devices/capa_np.sym} -990 360 0 0 {name=C1 value='CAPACITOR_0'}
C {devices/isource_np.sym} -1430 360 0 0 {name=I0 value='CURRENT_1_BIAS'}
C {devices/res_np.sym} -770 360 0 0 {name=R0 value='RESISTOR_1'}
C {devices/res_np.sym} -550 360 0 0 {name=R1 value='RESISTOR_2'}
C {devices/res_np.sym} -330 360 0 0 {name=R2 value='RESISTOR_0'}
C {devices/sg13_lv_pmos_np.sym} -110 -360 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} 110 -360 0 0 {name=M13 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} -110 360 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 110 360 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 330 360 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} 550 360 0 0 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 770 360 0 0 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 990 360 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_nmos_np.sym} 1210 360 0 0 {name=M23 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
N -550 -60 -510 -60 {}
C {devices/lab_wire.sym} -510 -60 0 1 {name=l0 lab=VB1}
N -550 -20 -510 -20 {}
C {devices/lab_wire.sym} -510 -20 0 1 {name=l1 lab=VB4}
N -550 20 -510 20 {}
C {devices/lab_wire.sym} -510 20 0 1 {name=l2 lab=net019}
N -550 60 -510 60 {}
C {devices/lab_wire.sym} -510 60 0 1 {name=l3 lab=net078}
N -660 -120 -660 -160 {}
C {devices/lab_wire.sym} -660 -160 0 1 {name=l4 lab=vdd}
N -110 -40 -70 -40 {}
C {devices/lab_wire.sym} -70 -40 0 1 {name=l5 lab=DM_2}
N -110 0 -70 0 {}
C {devices/lab_wire.sym} -70 0 0 1 {name=l6 lab=VB4}
N -110 40 -70 40 {}
C {devices/lab_wire.sym} -70 40 0 1 {name=l7 lab=net063}
N -220 100 -220 140 {}
C {devices/lab_wire.sym} -220 140 2 0 {name=l8 lab=vss}
N 330 -40 370 -40 {}
C {devices/lab_wire.sym} 370 -40 0 1 {name=l9 lab=VOUTN}
N 330 0 370 0 {}
C {devices/lab_wire.sym} 370 0 0 1 {name=l10 lab=net050}
N 330 40 370 40 {}
C {devices/lab_wire.sym} 370 40 0 1 {name=l11 lab=net057}
N 220 -100 220 -140 {}
C {devices/lab_wire.sym} 220 -140 0 1 {name=l12 lab=vdd}
N 550 -20 510 -20 {}
C {devices/lab_wire.sym} 510 -20 0 0 {name=l13 lab=VINN}
N 550 20 510 20 {}
C {devices/lab_wire.sym} 510 20 0 0 {name=l14 lab=VINP}
N 770 -40 810 -40 {}
C {devices/lab_wire.sym} 810 -40 0 1 {name=l15 lab=DM_2}
N 770 0 810 0 {}
C {devices/lab_wire.sym} 810 0 0 1 {name=l16 lab=net019}
N 770 40 810 40 {}
C {devices/lab_wire.sym} 810 40 0 1 {name=l17 lab=net063}
N -1210 330 -1210 290 {}
C {devices/lab_wire.sym} -1210 290 0 1 {name=l18 lab=net063}
N -1210 390 -1210 430 {}
C {devices/lab_wire.sym} -1210 430 2 0 {name=l19 lab=VOUT}
N -990 330 -990 290 {}
C {devices/lab_wire.sym} -990 290 0 1 {name=l20 lab=net051}
N -990 390 -990 430 {}
C {devices/lab_wire.sym} -990 430 2 0 {name=l21 lab=vss}
N -1430 330 -1430 290 {}
C {devices/lab_wire.sym} -1430 290 0 1 {name=l22 lab=VB1}
N -1430 390 -1430 430 {}
C {devices/lab_wire.sym} -1430 430 2 0 {name=l23 lab=vss}
N -770 330 -770 290 {}
C {devices/lab_wire.sym} -770 290 0 1 {name=l24 lab=net078}
N -770 390 -770 430 {}
C {devices/lab_wire.sym} -770 430 2 0 {name=l25 lab=net077}
N -550 330 -550 290 {}
C {devices/lab_wire.sym} -550 290 0 1 {name=l26 lab=net078}
N -550 390 -550 430 {}
C {devices/lab_wire.sym} -550 430 2 0 {name=l27 lab=net082}
N -330 330 -330 290 {}
C {devices/lab_wire.sym} -330 290 0 1 {name=l28 lab=net094}
N -330 390 -330 430 {}
C {devices/lab_wire.sym} -330 430 2 0 {name=l29 lab=net051}
N -90 -330 -90 -290 {}
C {devices/lab_wire.sym} -90 -290 2 0 {name=l30 lab=net094}
N -130 -360 -170 -360 {}
C {devices/lab_wire.sym} -170 -360 0 0 {name=l31 lab=net050}
N -90 -390 -90 -430 {}
C {devices/lab_wire.sym} -90 -430 0 1 {name=l32 lab=vdd}
N -90 -360 -50 -360 {}
C {devices/lab_wire.sym} -50 -360 0 1 {name=l33 lab=vdd}
N 130 -330 130 -290 {}
C {devices/lab_wire.sym} 130 -290 2 0 {name=l34 lab=VOUT}
N 90 -360 50 -360 {}
C {devices/lab_wire.sym} 50 -360 0 0 {name=l35 lab=net050}
N 130 -390 130 -430 {}
C {devices/lab_wire.sym} 130 -430 0 1 {name=l36 lab=vdd}
N 130 -360 170 -360 {}
C {devices/lab_wire.sym} 170 -360 0 1 {name=l37 lab=vdd}
N -90 330 -90 290 {}
C {devices/lab_wire.sym} -90 290 0 1 {name=l38 lab=VOUTN}
N -130 360 -170 360 {}
C {devices/lab_wire.sym} -170 360 0 0 {name=l39 lab=net077}
N -90 390 -90 430 {}
C {devices/lab_wire.sym} -90 430 2 0 {name=l40 lab=DM_2}
N -90 360 -50 360 {}
C {devices/lab_wire.sym} -50 360 0 1 {name=l41 lab=vss}
N 130 330 130 290 {}
C {devices/lab_wire.sym} 130 290 0 1 {name=l42 lab=net050}
N 90 360 50 360 {}
C {devices/lab_wire.sym} 50 360 0 0 {name=l43 lab=net082}
N 130 390 130 430 {}
C {devices/lab_wire.sym} 130 430 2 0 {name=l44 lab=net063}
N 130 360 170 360 {}
C {devices/lab_wire.sym} 170 360 0 1 {name=l45 lab=vss}
N 350 330 350 290 {}
C {devices/lab_wire.sym} 350 290 0 1 {name=l46 lab=net077}
N 310 360 270 360 {}
C {devices/lab_wire.sym} 270 360 0 0 {name=l47 lab=DM_2}
N 350 390 350 430 {}
C {devices/lab_wire.sym} 350 430 2 0 {name=l48 lab=vss}
N 350 360 390 360 {}
C {devices/lab_wire.sym} 390 360 0 1 {name=l49 lab=vss}
N 570 330 570 290 {}
C {devices/lab_wire.sym} 570 290 0 1 {name=l50 lab=net082}
N 530 360 490 360 {}
C {devices/lab_wire.sym} 490 360 0 0 {name=l51 lab=net063}
N 570 390 570 430 {}
C {devices/lab_wire.sym} 570 430 2 0 {name=l52 lab=vss}
N 570 360 610 360 {}
C {devices/lab_wire.sym} 610 360 0 1 {name=l53 lab=vss}
N 790 330 790 290 {}
C {devices/lab_wire.sym} 790 290 0 1 {name=l54 lab=VOUT}
N 750 360 710 360 {}
C {devices/lab_wire.sym} 710 360 0 0 {name=l55 lab=net057}
N 790 390 790 430 {}
C {devices/lab_wire.sym} 790 430 2 0 {name=l56 lab=vss}
N 790 360 830 360 {}
C {devices/lab_wire.sym} 830 360 0 1 {name=l57 lab=vss}
N 1010 330 1010 290 {}
C {devices/lab_wire.sym} 1010 290 0 1 {name=l58 lab=net094}
N 970 360 930 360 {}
C {devices/lab_wire.sym} 930 360 0 0 {name=l59 lab=net051}
N 1010 390 1010 430 {}
C {devices/lab_wire.sym} 1010 430 2 0 {name=l60 lab=vss}
N 1010 360 1050 360 {}
C {devices/lab_wire.sym} 1050 360 0 1 {name=l61 lab=vss}
N 1230 330 1230 290 {}
C {devices/lab_wire.sym} 1230 290 0 1 {name=l62 lab=net057}
N 1190 360 1150 360 {}
C {devices/lab_wire.sym} 1150 360 0 0 {name=l63 lab=net094}
N 1230 390 1230 430 {}
C {devices/lab_wire.sym} 1230 430 2 0 {name=l64 lab=vss}
N 1230 360 1270 360 {}
C {devices/lab_wire.sym} 1270 360 0 1 {name=l65 lab=vss}
