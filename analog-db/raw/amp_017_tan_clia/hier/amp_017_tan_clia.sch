v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_017_tan_clia} -1440 -560 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -1180 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_improved_high_swing_cascode_1.sym} -660 0 0 0 {name=xcm_nmos_improved_high_swing_cascode_1}
C {blocks/cm_pmos_simple_2.sym} -140 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/cm_pmos_simple_3.sym} 300 0 0 0 {name=xcm_pmos_simple_3}
C {blocks/cm_nmos_simple_1.sym} 740 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_pmos_simple_1.sym} 1180 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -880 360 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/capa_np.sym} -660 360 0 0 {name=C1 value='CAPACITOR_1'}
C {devices/isource_np.sym} -1400 360 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/res_np.sym} -440 360 0 0 {name=R0 value='RESISTOR_0'}
C {devices/sg13_lv_nmos_np.sym} -220 360 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 0 360 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} 220 360 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_nmos_np.sym} 440 360 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 660 360 0 0 {name=M61 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm61_w l=x_dut_xm61_l m=x_dut_xm61_m}
C {devices/sg13_lv_pmos_np.sym} -110 -360 0 0 {name=M68 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm68_w l=x_dut_xm68_l m=x_dut_xm68_m}
C {devices/sg13_lv_nmos_np.sym} 880 360 0 0 {name=M69 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm69_w l=x_dut_xm69_l m=x_dut_xm69_m}
C {devices/sg13_lv_pmos_np.sym} 110 -360 0 0 {name=M70 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm70_w l=x_dut_xm70_l m=x_dut_xm70_m}
N -1070 -60 -1030 -60 {}
C {devices/lab_wire.sym} -1030 -60 0 1 {name=l0 lab=VB3}
N -1070 -20 -1030 -20 {}
C {devices/lab_wire.sym} -1030 -20 0 1 {name=l1 lab=VB4}
N -1070 20 -1030 20 {}
C {devices/lab_wire.sym} -1030 20 0 1 {name=l2 lab=net1}
N -1070 60 -1030 60 {}
C {devices/lab_wire.sym} -1030 60 0 1 {name=l3 lab=net31}
N -1180 -120 -1180 -160 {}
C {devices/lab_wire.sym} -1180 -160 0 1 {name=l4 lab=vdd}
N -470 -40 -430 -40 {}
C {devices/lab_wire.sym} -430 -40 0 1 {name=l5 lab=DM_1}
N -470 0 -430 0 {}
C {devices/lab_wire.sym} -430 0 0 1 {name=l6 lab=VB3}
N -470 40 -430 40 {}
C {devices/lab_wire.sym} -430 40 0 1 {name=l7 lab=VB4}
N -660 100 -660 140 {}
C {devices/lab_wire.sym} -660 140 2 0 {name=l8 lab=vss}
N -30 -20 10 -20 {}
C {devices/lab_wire.sym} 10 -20 0 1 {name=l9 lab=DM_1}
N -30 20 10 20 {}
C {devices/lab_wire.sym} 10 20 0 1 {name=l10 lab=net5}
N -140 -80 -140 -120 {}
C {devices/lab_wire.sym} -140 -120 0 1 {name=l11 lab=vdd}
N 410 -20 450 -20 {}
C {devices/lab_wire.sym} 450 -20 0 1 {name=l12 lab=VOUTN}
N 410 20 450 20 {}
C {devices/lab_wire.sym} 450 20 0 1 {name=l13 lab=net050}
N 300 -80 300 -120 {}
C {devices/lab_wire.sym} 300 -120 0 1 {name=l14 lab=vdd}
N 850 -20 890 -20 {}
C {devices/lab_wire.sym} 890 -20 0 1 {name=l15 lab=net3}
N 850 20 890 20 {}
C {devices/lab_wire.sym} 890 20 0 1 {name=l16 lab=net5}
N 740 80 740 120 {}
C {devices/lab_wire.sym} 740 120 2 0 {name=l17 lab=vss}
N 1070 -20 1030 -20 {}
C {devices/lab_wire.sym} 1030 -20 0 0 {name=l18 lab=VINN}
N 1070 20 1030 20 {}
C {devices/lab_wire.sym} 1030 20 0 0 {name=l19 lab=VINP}
N 1290 -40 1330 -40 {}
C {devices/lab_wire.sym} 1330 -40 0 1 {name=l20 lab=DM_2}
N 1290 0 1330 0 {}
C {devices/lab_wire.sym} 1330 0 0 1 {name=l21 lab=net31}
N 1290 40 1330 40 {}
C {devices/lab_wire.sym} 1330 40 0 1 {name=l22 lab=net8}
N -880 330 -880 290 {}
C {devices/lab_wire.sym} -880 290 0 1 {name=l23 lab=net2}
N -880 390 -880 430 {}
C {devices/lab_wire.sym} -880 430 2 0 {name=l24 lab=vss}
N -660 330 -660 290 {}
C {devices/lab_wire.sym} -660 290 0 1 {name=l25 lab=net8}
N -660 390 -660 430 {}
C {devices/lab_wire.sym} -660 430 2 0 {name=l26 lab=VOUT}
N -1400 330 -1400 290 {}
C {devices/lab_wire.sym} -1400 290 0 1 {name=l27 lab=net1}
N -1400 390 -1400 430 {}
C {devices/lab_wire.sym} -1400 430 2 0 {name=l28 lab=vss}
N -440 330 -440 290 {}
C {devices/lab_wire.sym} -440 290 0 1 {name=l29 lab=net5}
N -440 390 -440 430 {}
C {devices/lab_wire.sym} -440 430 2 0 {name=l30 lab=net2}
N -200 330 -200 290 {}
C {devices/lab_wire.sym} -200 290 0 1 {name=l31 lab=VOUTN}
N -240 360 -280 360 {}
C {devices/lab_wire.sym} -280 360 0 0 {name=l32 lab=VB3}
N -200 390 -200 430 {}
C {devices/lab_wire.sym} -200 430 2 0 {name=l33 lab=DM_2}
N -200 360 -160 360 {}
C {devices/lab_wire.sym} -160 360 0 1 {name=l34 lab=vss}
N 20 330 20 290 {}
C {devices/lab_wire.sym} 20 290 0 1 {name=l35 lab=net050}
N -20 360 -60 360 {}
C {devices/lab_wire.sym} -60 360 0 0 {name=l36 lab=VB3}
N 20 390 20 430 {}
C {devices/lab_wire.sym} 20 430 2 0 {name=l37 lab=net8}
N 20 360 60 360 {}
C {devices/lab_wire.sym} 60 360 0 1 {name=l38 lab=vss}
N 240 330 240 290 {}
C {devices/lab_wire.sym} 240 290 0 1 {name=l39 lab=DM_2}
N 200 360 160 360 {}
C {devices/lab_wire.sym} 160 360 0 0 {name=l40 lab=VB4}
N 240 390 240 430 {}
C {devices/lab_wire.sym} 240 430 2 0 {name=l41 lab=vss}
N 240 360 280 360 {}
C {devices/lab_wire.sym} 280 360 0 1 {name=l42 lab=vss}
N 460 330 460 290 {}
C {devices/lab_wire.sym} 460 290 0 1 {name=l43 lab=net8}
N 420 360 380 360 {}
C {devices/lab_wire.sym} 380 360 0 0 {name=l44 lab=VB4}
N 460 390 460 430 {}
C {devices/lab_wire.sym} 460 430 2 0 {name=l45 lab=vss}
N 460 360 500 360 {}
C {devices/lab_wire.sym} 500 360 0 1 {name=l46 lab=vss}
N 680 330 680 290 {}
C {devices/lab_wire.sym} 680 290 0 1 {name=l47 lab=net3}
N 640 360 600 360 {}
C {devices/lab_wire.sym} 600 360 0 0 {name=l48 lab=VB4}
N 680 390 680 430 {}
C {devices/lab_wire.sym} 680 430 2 0 {name=l49 lab=vss}
N 680 360 720 360 {}
C {devices/lab_wire.sym} 720 360 0 1 {name=l50 lab=vss}
N -90 -330 -90 -290 {}
C {devices/lab_wire.sym} -90 -290 2 0 {name=l51 lab=VOUT}
N -130 -360 -170 -360 {}
C {devices/lab_wire.sym} -170 -360 0 0 {name=l52 lab=net050}
N -90 -390 -90 -430 {}
C {devices/lab_wire.sym} -90 -430 0 1 {name=l53 lab=vdd}
N -90 -360 -50 -360 {}
C {devices/lab_wire.sym} -50 -360 0 1 {name=l54 lab=vdd}
N 900 330 900 290 {}
C {devices/lab_wire.sym} 900 290 0 1 {name=l55 lab=VOUT}
N 860 360 820 360 {}
C {devices/lab_wire.sym} 820 360 0 0 {name=l56 lab=net5}
N 900 390 900 430 {}
C {devices/lab_wire.sym} 900 430 2 0 {name=l57 lab=vss}
N 900 360 940 360 {}
C {devices/lab_wire.sym} 940 360 0 1 {name=l58 lab=vss}
N 130 -330 130 -290 {}
C {devices/lab_wire.sym} 130 -290 2 0 {name=l59 lab=net3}
N 90 -360 50 -360 {}
C {devices/lab_wire.sym} 50 -360 0 0 {name=l60 lab=net050}
N 130 -390 130 -430 {}
C {devices/lab_wire.sym} 130 -430 0 1 {name=l61 lab=vdd}
N 130 -360 170 -360 {}
C {devices/lab_wire.sym} 170 -360 0 1 {name=l62 lab=vdd}
