v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_005_hoilee_affc} -1440 -600 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -1180 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_improved_high_swing_cascode_1.sym} -660 0 0 0 {name=xcm_nmos_improved_high_swing_cascode_1}
C {blocks/cm_nmos_simple_1.sym} -140 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_2.sym} 300 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/cm_pmos_simple_3.sym} 740 0 0 0 {name=xcm_pmos_simple_3}
C {blocks/dp_pmos_simple_1.sym} 1180 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -880 400 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/capa_np.sym} -660 400 0 0 {name=C1 value='CAPACITOR_1'}
C {devices/isource_np.sym} -1400 400 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/sg13_lv_pmos_np.sym} -110 -400 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} 110 -400 0 0 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} -440 400 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} -220 400 0 0 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 0 400 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 220 400 0 0 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 440 400 0 0 {name=M25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
C {devices/sg13_lv_nmos_np.sym} 660 400 0 0 {name=M63 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm63_w l=x_dut_xm63_l m=x_dut_xm63_m}
C {devices/sg13_lv_nmos_np.sym} 880 400 0 0 {name=M64 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm64_w l=x_dut_xm64_l m=x_dut_xm64_m}
N -1070 -100 -1030 -100 {}
C {devices/lab_wire.sym} -1030 -100 0 1 {name=l0 lab=DM_1}
N -1070 -60 -1030 -60 {}
C {devices/lab_wire.sym} -1030 -60 0 1 {name=l1 lab=VB3}
N -1070 -20 -1030 -20 {}
C {devices/lab_wire.sym} -1030 -20 0 1 {name=l2 lab=VB4}
N -1070 20 -1030 20 {}
C {devices/lab_wire.sym} -1030 20 0 1 {name=l3 lab=net013}
N -1070 60 -1030 60 {}
C {devices/lab_wire.sym} -1030 60 0 1 {name=l4 lab=net049}
N -1070 100 -1030 100 {}
C {devices/lab_wire.sym} -1030 100 0 1 {name=l5 lab=net31}
N -1180 -160 -1180 -200 {}
C {devices/lab_wire.sym} -1180 -200 0 1 {name=l6 lab=vdd}
N -470 -60 -430 -60 {}
C {devices/lab_wire.sym} -430 -60 0 1 {name=l7 lab=DM_1}
N -470 -20 -430 -20 {}
C {devices/lab_wire.sym} -430 -20 0 1 {name=l8 lab=VB3}
N -470 20 -430 20 {}
C {devices/lab_wire.sym} -430 20 0 1 {name=l9 lab=VB4}
N -470 60 -430 60 {}
C {devices/lab_wire.sym} -430 60 0 1 {name=l10 lab=net2}
N -660 120 -660 160 {}
C {devices/lab_wire.sym} -660 160 2 0 {name=l11 lab=vss}
N -30 -20 10 -20 {}
C {devices/lab_wire.sym} 10 -20 0 1 {name=l12 lab=net043}
N -30 20 10 20 {}
C {devices/lab_wire.sym} 10 20 0 1 {name=l13 lab=net049}
N -140 80 -140 120 {}
C {devices/lab_wire.sym} -140 120 2 0 {name=l14 lab=vss}
N 410 -20 450 -20 {}
C {devices/lab_wire.sym} 450 -20 0 1 {name=l15 lab=VOUTN}
N 410 20 450 20 {}
C {devices/lab_wire.sym} 450 20 0 1 {name=l16 lab=net050}
N 300 -80 300 -120 {}
C {devices/lab_wire.sym} 300 -120 0 1 {name=l17 lab=vdd}
N 850 -20 890 -20 {}
C {devices/lab_wire.sym} 890 -20 0 1 {name=l18 lab=net050}
N 850 20 890 20 {}
C {devices/lab_wire.sym} 890 20 0 1 {name=l19 lab=net2}
N 740 -80 740 -120 {}
C {devices/lab_wire.sym} 740 -120 0 1 {name=l20 lab=vdd}
N 1070 -20 1030 -20 {}
C {devices/lab_wire.sym} 1030 -20 0 0 {name=l21 lab=VINN}
N 1070 20 1030 20 {}
C {devices/lab_wire.sym} 1030 20 0 0 {name=l22 lab=VINP}
N 1290 -40 1330 -40 {}
C {devices/lab_wire.sym} 1330 -40 0 1 {name=l23 lab=DM_2}
N 1290 0 1330 0 {}
C {devices/lab_wire.sym} 1330 0 0 1 {name=l24 lab=net063}
N 1290 40 1330 40 {}
C {devices/lab_wire.sym} 1330 40 0 1 {name=l25 lab=net31}
N -880 370 -880 330 {}
C {devices/lab_wire.sym} -880 330 0 1 {name=l26 lab=net049}
N -880 430 -880 470 {}
C {devices/lab_wire.sym} -880 470 2 0 {name=l27 lab=VOUT}
N -660 370 -660 330 {}
C {devices/lab_wire.sym} -660 330 0 1 {name=l28 lab=VOUT}
N -660 430 -660 470 {}
C {devices/lab_wire.sym} -660 470 2 0 {name=l29 lab=net1}
N -1400 370 -1400 330 {}
C {devices/lab_wire.sym} -1400 330 0 1 {name=l30 lab=net013}
N -1400 430 -1400 470 {}
C {devices/lab_wire.sym} -1400 470 2 0 {name=l31 lab=vss}
N -90 -370 -90 -330 {}
C {devices/lab_wire.sym} -90 -330 2 0 {name=l32 lab=net043}
N -130 -400 -170 -400 {}
C {devices/lab_wire.sym} -170 -400 0 0 {name=l33 lab=net050}
N -90 -430 -90 -470 {}
C {devices/lab_wire.sym} -90 -470 0 1 {name=l34 lab=vdd}
N -90 -400 -50 -400 {}
C {devices/lab_wire.sym} -50 -400 0 1 {name=l35 lab=vdd}
N 130 -370 130 -330 {}
C {devices/lab_wire.sym} 130 -330 2 0 {name=l36 lab=VOUT}
N 90 -400 50 -400 {}
C {devices/lab_wire.sym} 50 -400 0 0 {name=l37 lab=net050}
N 130 -430 130 -470 {}
C {devices/lab_wire.sym} 130 -470 0 1 {name=l38 lab=vdd}
N 130 -400 170 -400 {}
C {devices/lab_wire.sym} 170 -400 0 1 {name=l39 lab=vdd}
N -420 370 -420 330 {}
C {devices/lab_wire.sym} -420 330 0 1 {name=l40 lab=VOUTN}
N -460 400 -500 400 {}
C {devices/lab_wire.sym} -500 400 0 0 {name=l41 lab=VB3}
N -420 430 -420 470 {}
C {devices/lab_wire.sym} -420 470 2 0 {name=l42 lab=DM_2}
N -420 400 -380 400 {}
C {devices/lab_wire.sym} -380 400 0 1 {name=l43 lab=vss}
N -200 370 -200 330 {}
C {devices/lab_wire.sym} -200 330 0 1 {name=l44 lab=net050}
N -240 400 -280 400 {}
C {devices/lab_wire.sym} -280 400 0 0 {name=l45 lab=VB3}
N -200 430 -200 470 {}
C {devices/lab_wire.sym} -200 470 2 0 {name=l46 lab=net063}
N -200 400 -160 400 {}
C {devices/lab_wire.sym} -160 400 0 1 {name=l47 lab=vss}
N 20 370 20 330 {}
C {devices/lab_wire.sym} 20 330 0 1 {name=l48 lab=DM_2}
N -20 400 -60 400 {}
C {devices/lab_wire.sym} -60 400 0 0 {name=l49 lab=VB4}
N 20 430 20 470 {}
C {devices/lab_wire.sym} 20 470 2 0 {name=l50 lab=vss}
N 20 400 60 400 {}
C {devices/lab_wire.sym} 60 400 0 1 {name=l51 lab=vss}
N 240 370 240 330 {}
C {devices/lab_wire.sym} 240 330 0 1 {name=l52 lab=net063}
N 200 400 160 400 {}
C {devices/lab_wire.sym} 160 400 0 0 {name=l53 lab=VB4}
N 240 430 240 470 {}
C {devices/lab_wire.sym} 240 470 2 0 {name=l54 lab=vss}
N 240 400 280 400 {}
C {devices/lab_wire.sym} 280 400 0 1 {name=l55 lab=vss}
N 460 370 460 330 {}
C {devices/lab_wire.sym} 460 330 0 1 {name=l56 lab=VOUT}
N 420 400 380 400 {}
C {devices/lab_wire.sym} 380 400 0 0 {name=l57 lab=net049}
N 460 430 460 470 {}
C {devices/lab_wire.sym} 460 470 2 0 {name=l58 lab=vss}
N 460 400 500 400 {}
C {devices/lab_wire.sym} 500 400 0 1 {name=l59 lab=vss}
N 680 370 680 330 {}
C {devices/lab_wire.sym} 680 330 0 1 {name=l60 lab=net050}
N 640 400 600 400 {}
C {devices/lab_wire.sym} 600 400 0 0 {name=l61 lab=VB3}
N 680 430 680 470 {}
C {devices/lab_wire.sym} 680 470 2 0 {name=l62 lab=net1}
N 680 400 720 400 {}
C {devices/lab_wire.sym} 720 400 0 1 {name=l63 lab=vss}
N 900 370 900 330 {}
C {devices/lab_wire.sym} 900 330 0 1 {name=l64 lab=net1}
N 860 400 820 400 {}
C {devices/lab_wire.sym} 820 400 0 0 {name=l65 lab=VB4}
N 900 430 900 470 {}
C {devices/lab_wire.sym} 900 470 2 0 {name=l66 lab=vss}
N 900 400 940 400 {}
C {devices/lab_wire.sym} 940 400 0 1 {name=l67 lab=vss}
