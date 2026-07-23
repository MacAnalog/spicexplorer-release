v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_007_leung_dfcfc2} -1220 -600 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -960 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_improved_high_swing_cascode_1.sym} -440 0 0 0 {name=xcm_nmos_improved_high_swing_cascode_1}
C {blocks/cm_nmos_simple_1.sym} 80 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_2.sym} 520 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/dp_pmos_simple_1.sym} 960 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -770 400 0 0 {name=C1 value='CAPACITOR_0'}
C {devices/capa_np.sym} -550 400 0 0 {name=C2 value='CAPACITOR_1'}
C {devices/isource_np.sym} -1180 400 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/sg13_lv_pmos_np.sym} -220 -400 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 0 -400 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} 220 -400 0 0 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} -330 400 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} -110 400 0 0 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 110 400 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 330 400 0 0 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 550 400 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_nmos_np.sym} 770 400 0 0 {name=M25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
N -850 -100 -810 -100 {}
C {devices/lab_wire.sym} -810 -100 0 1 {name=l0 lab=DM_1}
N -850 -60 -810 -60 {}
C {devices/lab_wire.sym} -810 -60 0 1 {name=l1 lab=VB3}
N -850 -20 -810 -20 {}
C {devices/lab_wire.sym} -810 -20 0 1 {name=l2 lab=VB4}
N -850 20 -810 20 {}
C {devices/lab_wire.sym} -810 20 0 1 {name=l3 lab=net049}
N -850 60 -810 60 {}
C {devices/lab_wire.sym} -810 60 0 1 {name=l4 lab=net1}
N -850 100 -810 100 {}
C {devices/lab_wire.sym} -810 100 0 1 {name=l5 lab=net31}
N -960 -160 -960 -200 {}
C {devices/lab_wire.sym} -960 -200 0 1 {name=l6 lab=vdd}
N -250 -40 -210 -40 {}
C {devices/lab_wire.sym} -210 -40 0 1 {name=l7 lab=DM_1}
N -250 0 -210 0 {}
C {devices/lab_wire.sym} -210 0 0 1 {name=l8 lab=VB3}
N -250 40 -210 40 {}
C {devices/lab_wire.sym} -210 40 0 1 {name=l9 lab=VB4}
N -440 100 -440 140 {}
C {devices/lab_wire.sym} -440 140 2 0 {name=l10 lab=vss}
N 190 -20 230 -20 {}
C {devices/lab_wire.sym} 230 -20 0 1 {name=l11 lab=net043}
N 190 20 230 20 {}
C {devices/lab_wire.sym} 230 20 0 1 {name=l12 lab=net049}
N 80 80 80 120 {}
C {devices/lab_wire.sym} 80 120 2 0 {name=l13 lab=vss}
N 630 -20 670 -20 {}
C {devices/lab_wire.sym} 670 -20 0 1 {name=l14 lab=VOUTN}
N 630 20 670 20 {}
C {devices/lab_wire.sym} 670 20 0 1 {name=l15 lab=net050}
N 520 -80 520 -120 {}
C {devices/lab_wire.sym} 520 -120 0 1 {name=l16 lab=vdd}
N 850 -20 810 -20 {}
C {devices/lab_wire.sym} 810 -20 0 0 {name=l17 lab=VINN}
N 850 20 810 20 {}
C {devices/lab_wire.sym} 810 20 0 0 {name=l18 lab=VINP}
N 1070 -40 1110 -40 {}
C {devices/lab_wire.sym} 1110 -40 0 1 {name=l19 lab=DM_2}
N 1070 0 1110 0 {}
C {devices/lab_wire.sym} 1110 0 0 1 {name=l20 lab=net063}
N 1070 40 1110 40 {}
C {devices/lab_wire.sym} 1110 40 0 1 {name=l21 lab=net31}
N -770 370 -770 330 {}
C {devices/lab_wire.sym} -770 330 0 1 {name=l22 lab=net050}
N -770 430 -770 470 {}
C {devices/lab_wire.sym} -770 470 2 0 {name=l23 lab=VOUT}
N -550 370 -550 330 {}
C {devices/lab_wire.sym} -550 330 0 1 {name=l24 lab=net050}
N -550 430 -550 470 {}
C {devices/lab_wire.sym} -550 470 2 0 {name=l25 lab=net2}
N -1180 370 -1180 330 {}
C {devices/lab_wire.sym} -1180 330 0 1 {name=l26 lab=net1}
N -1180 430 -1180 470 {}
C {devices/lab_wire.sym} -1180 470 2 0 {name=l27 lab=vss}
N -200 -370 -200 -330 {}
C {devices/lab_wire.sym} -200 -330 2 0 {name=l28 lab=net2}
N -240 -400 -280 -400 {}
C {devices/lab_wire.sym} -280 -400 0 0 {name=l29 lab=net050}
N -200 -430 -200 -470 {}
C {devices/lab_wire.sym} -200 -470 0 1 {name=l30 lab=vdd}
N -200 -400 -160 -400 {}
C {devices/lab_wire.sym} -160 -400 0 1 {name=l31 lab=vdd}
N 20 -370 20 -330 {}
C {devices/lab_wire.sym} 20 -330 2 0 {name=l32 lab=net043}
N -20 -400 -60 -400 {}
C {devices/lab_wire.sym} -60 -400 0 0 {name=l33 lab=net050}
N 20 -430 20 -470 {}
C {devices/lab_wire.sym} 20 -470 0 1 {name=l34 lab=vdd}
N 20 -400 60 -400 {}
C {devices/lab_wire.sym} 60 -400 0 1 {name=l35 lab=vdd}
N 240 -370 240 -330 {}
C {devices/lab_wire.sym} 240 -330 2 0 {name=l36 lab=VOUT}
N 200 -400 160 -400 {}
C {devices/lab_wire.sym} 160 -400 0 0 {name=l37 lab=net050}
N 240 -430 240 -470 {}
C {devices/lab_wire.sym} 240 -470 0 1 {name=l38 lab=vdd}
N 240 -400 280 -400 {}
C {devices/lab_wire.sym} 280 -400 0 1 {name=l39 lab=vdd}
N -310 370 -310 330 {}
C {devices/lab_wire.sym} -310 330 0 1 {name=l40 lab=VOUTN}
N -350 400 -390 400 {}
C {devices/lab_wire.sym} -390 400 0 0 {name=l41 lab=VB3}
N -310 430 -310 470 {}
C {devices/lab_wire.sym} -310 470 2 0 {name=l42 lab=DM_2}
N -310 400 -270 400 {}
C {devices/lab_wire.sym} -270 400 0 1 {name=l43 lab=vss}
N -90 370 -90 330 {}
C {devices/lab_wire.sym} -90 330 0 1 {name=l44 lab=net050}
N -130 400 -170 400 {}
C {devices/lab_wire.sym} -170 400 0 0 {name=l45 lab=VB3}
N -90 430 -90 470 {}
C {devices/lab_wire.sym} -90 470 2 0 {name=l46 lab=net063}
N -90 400 -50 400 {}
C {devices/lab_wire.sym} -50 400 0 1 {name=l47 lab=vss}
N 130 370 130 330 {}
C {devices/lab_wire.sym} 130 330 0 1 {name=l48 lab=DM_2}
N 90 400 50 400 {}
C {devices/lab_wire.sym} 50 400 0 0 {name=l49 lab=VB4}
N 130 430 130 470 {}
C {devices/lab_wire.sym} 130 470 2 0 {name=l50 lab=vss}
N 130 400 170 400 {}
C {devices/lab_wire.sym} 170 400 0 1 {name=l51 lab=vss}
N 350 370 350 330 {}
C {devices/lab_wire.sym} 350 330 0 1 {name=l52 lab=net063}
N 310 400 270 400 {}
C {devices/lab_wire.sym} 270 400 0 0 {name=l53 lab=VB4}
N 350 430 350 470 {}
C {devices/lab_wire.sym} 350 470 2 0 {name=l54 lab=vss}
N 350 400 390 400 {}
C {devices/lab_wire.sym} 390 400 0 1 {name=l55 lab=vss}
N 570 370 570 330 {}
C {devices/lab_wire.sym} 570 330 0 1 {name=l56 lab=net2}
N 530 400 490 400 {}
C {devices/lab_wire.sym} 490 400 0 0 {name=l57 lab=VB4}
N 570 430 570 470 {}
C {devices/lab_wire.sym} 570 470 2 0 {name=l58 lab=vss}
N 570 400 610 400 {}
C {devices/lab_wire.sym} 610 400 0 1 {name=l59 lab=vss}
N 790 370 790 330 {}
C {devices/lab_wire.sym} 790 330 0 1 {name=l60 lab=VOUT}
N 750 400 710 400 {}
C {devices/lab_wire.sym} 710 400 0 0 {name=l61 lab=net049}
N 790 430 790 470 {}
C {devices/lab_wire.sym} 790 470 2 0 {name=l62 lab=vss}
N 790 400 830 400 {}
C {devices/lab_wire.sym} 830 400 0 1 {name=l63 lab=vss}
