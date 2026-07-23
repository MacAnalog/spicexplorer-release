v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_006_leung_dfcfc1} -1220 -620 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -960 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_improved_high_swing_cascode_1.sym} -440 0 0 0 {name=xcm_nmos_improved_high_swing_cascode_1}
C {blocks/cm_nmos_simple_1.sym} 80 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_2.sym} 520 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/dp_pmos_simple_1.sym} 960 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -770 420 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/capa_np.sym} -550 420 0 0 {name=C1 value='CAPACITOR_1'}
C {devices/isource_np.sym} -1180 420 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/sg13_lv_pmos_np.sym} -110 -420 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} 110 -420 0 0 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} -330 420 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} -110 420 0 0 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 110 420 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 330 420 0 0 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 550 420 0 0 {name=M24 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_nmos_np.sym} 770 420 0 0 {name=M25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
N -850 -120 -850 -160 {}
C {devices/lab_wire.sym} -850 -160 0 1 {name=l0 lab=DM_1}
N -850 -80 -810 -80 {}
C {devices/lab_wire.sym} -810 -80 0 1 {name=l1 lab=VB3}
N -850 -40 -810 -40 {}
C {devices/lab_wire.sym} -810 -40 0 1 {name=l2 lab=VB4}
N -850 0 -810 0 {}
C {devices/lab_wire.sym} -810 0 0 1 {name=l3 lab=net013}
N -850 40 -810 40 {}
C {devices/lab_wire.sym} -810 40 0 1 {name=l4 lab=net049}
N -850 80 -810 80 {}
C {devices/lab_wire.sym} -810 80 0 1 {name=l5 lab=net1}
N -850 120 -850 160 {}
C {devices/lab_wire.sym} -850 160 2 0 {name=l6 lab=net31}
N -960 -180 -960 -220 {}
C {devices/lab_wire.sym} -960 -220 0 1 {name=l7 lab=vdd}
N -250 -40 -210 -40 {}
C {devices/lab_wire.sym} -210 -40 0 1 {name=l8 lab=DM_1}
N -250 0 -210 0 {}
C {devices/lab_wire.sym} -210 0 0 1 {name=l9 lab=VB3}
N -250 40 -210 40 {}
C {devices/lab_wire.sym} -210 40 0 1 {name=l10 lab=VB4}
N -440 100 -440 140 {}
C {devices/lab_wire.sym} -440 140 2 0 {name=l11 lab=vss}
N 190 -20 230 -20 {}
C {devices/lab_wire.sym} 230 -20 0 1 {name=l12 lab=net043}
N 190 20 230 20 {}
C {devices/lab_wire.sym} 230 20 0 1 {name=l13 lab=net049}
N 80 80 80 120 {}
C {devices/lab_wire.sym} 80 120 2 0 {name=l14 lab=vss}
N 630 -20 670 -20 {}
C {devices/lab_wire.sym} 670 -20 0 1 {name=l15 lab=VOUTN}
N 630 20 670 20 {}
C {devices/lab_wire.sym} 670 20 0 1 {name=l16 lab=net050}
N 520 -80 520 -120 {}
C {devices/lab_wire.sym} 520 -120 0 1 {name=l17 lab=vdd}
N 850 -20 810 -20 {}
C {devices/lab_wire.sym} 810 -20 0 0 {name=l18 lab=VINN}
N 850 20 810 20 {}
C {devices/lab_wire.sym} 810 20 0 0 {name=l19 lab=VINP}
N 1070 -40 1110 -40 {}
C {devices/lab_wire.sym} 1110 -40 0 1 {name=l20 lab=DM_2}
N 1070 0 1110 0 {}
C {devices/lab_wire.sym} 1110 0 0 1 {name=l21 lab=net063}
N 1070 40 1110 40 {}
C {devices/lab_wire.sym} 1110 40 0 1 {name=l22 lab=net31}
N -770 390 -770 350 {}
C {devices/lab_wire.sym} -770 350 0 1 {name=l23 lab=net050}
N -770 450 -770 490 {}
C {devices/lab_wire.sym} -770 490 2 0 {name=l24 lab=VOUT}
N -550 390 -550 350 {}
C {devices/lab_wire.sym} -550 350 0 1 {name=l25 lab=net049}
N -550 450 -550 490 {}
C {devices/lab_wire.sym} -550 490 2 0 {name=l26 lab=net1}
N -1180 390 -1180 350 {}
C {devices/lab_wire.sym} -1180 350 0 1 {name=l27 lab=net013}
N -1180 450 -1180 490 {}
C {devices/lab_wire.sym} -1180 490 2 0 {name=l28 lab=vss}
N -90 -390 -90 -350 {}
C {devices/lab_wire.sym} -90 -350 2 0 {name=l29 lab=net043}
N -130 -420 -170 -420 {}
C {devices/lab_wire.sym} -170 -420 0 0 {name=l30 lab=net050}
N -90 -450 -90 -490 {}
C {devices/lab_wire.sym} -90 -490 0 1 {name=l31 lab=vdd}
N -90 -420 -50 -420 {}
C {devices/lab_wire.sym} -50 -420 0 1 {name=l32 lab=vdd}
N 130 -390 130 -350 {}
C {devices/lab_wire.sym} 130 -350 2 0 {name=l33 lab=VOUT}
N 90 -420 50 -420 {}
C {devices/lab_wire.sym} 50 -420 0 0 {name=l34 lab=net050}
N 130 -450 130 -490 {}
C {devices/lab_wire.sym} 130 -490 0 1 {name=l35 lab=vdd}
N 130 -420 170 -420 {}
C {devices/lab_wire.sym} 170 -420 0 1 {name=l36 lab=vdd}
N -310 390 -310 350 {}
C {devices/lab_wire.sym} -310 350 0 1 {name=l37 lab=VOUTN}
N -350 420 -390 420 {}
C {devices/lab_wire.sym} -390 420 0 0 {name=l38 lab=VB3}
N -310 450 -310 490 {}
C {devices/lab_wire.sym} -310 490 2 0 {name=l39 lab=DM_2}
N -310 420 -270 420 {}
C {devices/lab_wire.sym} -270 420 0 1 {name=l40 lab=vss}
N -90 390 -90 350 {}
C {devices/lab_wire.sym} -90 350 0 1 {name=l41 lab=net050}
N -130 420 -170 420 {}
C {devices/lab_wire.sym} -170 420 0 0 {name=l42 lab=VB3}
N -90 450 -90 490 {}
C {devices/lab_wire.sym} -90 490 2 0 {name=l43 lab=net063}
N -90 420 -50 420 {}
C {devices/lab_wire.sym} -50 420 0 1 {name=l44 lab=vss}
N 130 390 130 350 {}
C {devices/lab_wire.sym} 130 350 0 1 {name=l45 lab=DM_2}
N 90 420 50 420 {}
C {devices/lab_wire.sym} 50 420 0 0 {name=l46 lab=VB4}
N 130 450 130 490 {}
C {devices/lab_wire.sym} 130 490 2 0 {name=l47 lab=vss}
N 130 420 170 420 {}
C {devices/lab_wire.sym} 170 420 0 1 {name=l48 lab=vss}
N 350 390 350 350 {}
C {devices/lab_wire.sym} 350 350 0 1 {name=l49 lab=net063}
N 310 420 270 420 {}
C {devices/lab_wire.sym} 270 420 0 0 {name=l50 lab=VB4}
N 350 450 350 490 {}
C {devices/lab_wire.sym} 350 490 2 0 {name=l51 lab=vss}
N 350 420 390 420 {}
C {devices/lab_wire.sym} 390 420 0 1 {name=l52 lab=vss}
N 570 390 570 350 {}
C {devices/lab_wire.sym} 570 350 0 1 {name=l53 lab=net1}
N 530 420 490 420 {}
C {devices/lab_wire.sym} 490 420 0 0 {name=l54 lab=net049}
N 570 450 570 490 {}
C {devices/lab_wire.sym} 570 490 2 0 {name=l55 lab=vss}
N 570 420 610 420 {}
C {devices/lab_wire.sym} 610 420 0 1 {name=l56 lab=vss}
N 790 390 790 350 {}
C {devices/lab_wire.sym} 790 350 0 1 {name=l57 lab=VOUT}
N 750 420 710 420 {}
C {devices/lab_wire.sym} 710 420 0 0 {name=l58 lab=net049}
N 790 450 790 490 {}
C {devices/lab_wire.sym} 790 490 2 0 {name=l59 lab=vss}
N 790 420 830 420 {}
C {devices/lab_wire.sym} 830 420 0 1 {name=l60 lab=vss}
