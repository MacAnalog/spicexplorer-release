v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_010_peng_acbc} -1220 -620 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -960 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_improved_high_swing_cascode_1.sym} -440 0 0 0 {name=xcm_nmos_improved_high_swing_cascode_1}
C {blocks/cm_nmos_simple_1.sym} 80 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_2.sym} 520 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/dp_pmos_simple_1.sym} 960 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -660 420 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/capa_np.sym} -440 420 0 0 {name=C1 value='CAPACITOR_1'}
C {devices/isource_np.sym} -1180 420 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/sg13_lv_pmos_np.sym} -220 -420 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} 0 -420 0 0 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} -220 420 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} 0 420 0 0 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 220 420 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 440 420 0 0 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 660 420 0 0 {name=M25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
C {devices/sg13_lv_pmos_np.sym} 220 -420 0 0 {name=M59 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm59_w l=x_dut_xm59_l m=x_dut_xm59_m}
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
N 190 -40 230 -40 {}
C {devices/lab_wire.sym} 230 -40 0 1 {name=l12 lab=net043}
N 190 0 230 0 {}
C {devices/lab_wire.sym} 230 0 0 1 {name=l13 lab=net049}
N 190 40 230 40 {}
C {devices/lab_wire.sym} 230 40 0 1 {name=l14 lab=net1}
N 80 100 80 140 {}
C {devices/lab_wire.sym} 80 140 2 0 {name=l15 lab=vss}
N 630 -20 670 -20 {}
C {devices/lab_wire.sym} 670 -20 0 1 {name=l16 lab=VOUTN}
N 630 20 670 20 {}
C {devices/lab_wire.sym} 670 20 0 1 {name=l17 lab=net050}
N 520 -80 520 -120 {}
C {devices/lab_wire.sym} 520 -120 0 1 {name=l18 lab=vdd}
N 850 -20 810 -20 {}
C {devices/lab_wire.sym} 810 -20 0 0 {name=l19 lab=VINN}
N 850 20 810 20 {}
C {devices/lab_wire.sym} 810 20 0 0 {name=l20 lab=VINP}
N 1070 -40 1110 -40 {}
C {devices/lab_wire.sym} 1110 -40 0 1 {name=l21 lab=DM_2}
N 1070 0 1110 0 {}
C {devices/lab_wire.sym} 1110 0 0 1 {name=l22 lab=net063}
N 1070 40 1110 40 {}
C {devices/lab_wire.sym} 1110 40 0 1 {name=l23 lab=net31}
N -660 390 -660 350 {}
C {devices/lab_wire.sym} -660 350 0 1 {name=l24 lab=net050}
N -660 450 -660 490 {}
C {devices/lab_wire.sym} -660 490 2 0 {name=l25 lab=VOUT}
N -440 390 -440 350 {}
C {devices/lab_wire.sym} -440 350 0 1 {name=l26 lab=net049}
N -440 450 -440 490 {}
C {devices/lab_wire.sym} -440 490 2 0 {name=l27 lab=net1}
N -1180 390 -1180 350 {}
C {devices/lab_wire.sym} -1180 350 0 1 {name=l28 lab=net013}
N -1180 450 -1180 490 {}
C {devices/lab_wire.sym} -1180 490 2 0 {name=l29 lab=vss}
N -200 -390 -200 -350 {}
C {devices/lab_wire.sym} -200 -350 2 0 {name=l30 lab=net043}
N -240 -420 -280 -420 {}
C {devices/lab_wire.sym} -280 -420 0 0 {name=l31 lab=net050}
N -200 -450 -200 -490 {}
C {devices/lab_wire.sym} -200 -490 0 1 {name=l32 lab=vdd}
N -200 -420 -160 -420 {}
C {devices/lab_wire.sym} -160 -420 0 1 {name=l33 lab=vdd}
N 20 -390 20 -350 {}
C {devices/lab_wire.sym} 20 -350 2 0 {name=l34 lab=VOUT}
N -20 -420 -60 -420 {}
C {devices/lab_wire.sym} -60 -420 0 0 {name=l35 lab=net050}
N 20 -450 20 -490 {}
C {devices/lab_wire.sym} 20 -490 0 1 {name=l36 lab=vdd}
N 20 -420 60 -420 {}
C {devices/lab_wire.sym} 60 -420 0 1 {name=l37 lab=vdd}
N -200 390 -200 350 {}
C {devices/lab_wire.sym} -200 350 0 1 {name=l38 lab=VOUTN}
N -240 420 -280 420 {}
C {devices/lab_wire.sym} -280 420 0 0 {name=l39 lab=VB3}
N -200 450 -200 490 {}
C {devices/lab_wire.sym} -200 490 2 0 {name=l40 lab=DM_2}
N -200 420 -160 420 {}
C {devices/lab_wire.sym} -160 420 0 1 {name=l41 lab=vss}
N 20 390 20 350 {}
C {devices/lab_wire.sym} 20 350 0 1 {name=l42 lab=net050}
N -20 420 -60 420 {}
C {devices/lab_wire.sym} -60 420 0 0 {name=l43 lab=VB3}
N 20 450 20 490 {}
C {devices/lab_wire.sym} 20 490 2 0 {name=l44 lab=net063}
N 20 420 60 420 {}
C {devices/lab_wire.sym} 60 420 0 1 {name=l45 lab=vss}
N 240 390 240 350 {}
C {devices/lab_wire.sym} 240 350 0 1 {name=l46 lab=DM_2}
N 200 420 160 420 {}
C {devices/lab_wire.sym} 160 420 0 0 {name=l47 lab=VB4}
N 240 450 240 490 {}
C {devices/lab_wire.sym} 240 490 2 0 {name=l48 lab=vss}
N 240 420 280 420 {}
C {devices/lab_wire.sym} 280 420 0 1 {name=l49 lab=vss}
N 460 390 460 350 {}
C {devices/lab_wire.sym} 460 350 0 1 {name=l50 lab=net063}
N 420 420 380 420 {}
C {devices/lab_wire.sym} 380 420 0 0 {name=l51 lab=VB4}
N 460 450 460 490 {}
C {devices/lab_wire.sym} 460 490 2 0 {name=l52 lab=vss}
N 460 420 500 420 {}
C {devices/lab_wire.sym} 500 420 0 1 {name=l53 lab=vss}
N 680 390 680 350 {}
C {devices/lab_wire.sym} 680 350 0 1 {name=l54 lab=VOUT}
N 640 420 600 420 {}
C {devices/lab_wire.sym} 600 420 0 0 {name=l55 lab=net049}
N 680 450 680 490 {}
C {devices/lab_wire.sym} 680 490 2 0 {name=l56 lab=vss}
N 680 420 720 420 {}
C {devices/lab_wire.sym} 720 420 0 1 {name=l57 lab=vss}
N 240 -390 240 -350 {}
C {devices/lab_wire.sym} 240 -350 2 0 {name=l58 lab=net1}
N 200 -420 160 -420 {}
C {devices/lab_wire.sym} 160 -420 0 0 {name=l59 lab=net1}
N 240 -450 240 -490 {}
C {devices/lab_wire.sym} 240 -490 0 1 {name=l60 lab=vdd}
N 240 -420 280 -420 {}
C {devices/lab_wire.sym} 280 -420 0 1 {name=l61 lab=vdd}
