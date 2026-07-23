v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_011_peng_iac} -1470 -600 0 0 0.4 0.4 {}
C {blocks/cm_nmos_improved_high_swing_cascode_1.sym} -740 0 0 0 {name=xcm_nmos_improved_high_swing_cascode_1}
C {blocks/cm_pmos_simple_1.sym} -220 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_pmos_improved_high_swing_cascode_1.sym} 300 0 0 0 {name=xcm_pmos_improved_high_swing_cascode_1}
C {blocks/dp_pmos_simple_1.sym} 820 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -1210 400 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/capa_np.sym} -990 400 0 0 {name=C1 value='CAPACITOR_1'}
C {devices/isource_np.sym} -1430 400 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/res_np.sym} -770 400 0 0 {name=R0 value='RESISTOR_0'}
C {devices/sg13_lv_pmos_np.sym} -220 -400 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 0 -400 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -550 400 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} -330 400 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} -110 400 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_nmos_np.sym} 110 400 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 330 400 0 0 {name=M23 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_pmos_np.sym} 220 -400 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 550 400 0 0 {name=M67 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm67_w l=x_dut_xm67_l m=x_dut_xm67_m}
C {devices/sg13_lv_nmos_np.sym} 770 400 0 0 {name=M68 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm68_w l=x_dut_xm68_l m=x_dut_xm68_m}
C {devices/sg13_lv_nmos_np.sym} 990 400 0 0 {name=M69 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm69_w l=x_dut_xm69_l m=x_dut_xm69_m}
C {devices/sg13_lv_nmos_np.sym} 1210 400 0 0 {name=M70 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm70_w l=x_dut_xm70_l m=x_dut_xm70_m}
N -550 -60 -510 -60 {}
C {devices/lab_wire.sym} -510 -60 0 1 {name=l0 lab=VB2}
N -550 -20 -510 -20 {}
C {devices/lab_wire.sym} -510 -20 0 1 {name=l1 lab=VB3}
N -550 20 -510 20 {}
C {devices/lab_wire.sym} -510 20 0 1 {name=l2 lab=VB4}
N -550 60 -510 60 {}
C {devices/lab_wire.sym} -510 60 0 1 {name=l3 lab=net7}
N -740 120 -740 160 {}
C {devices/lab_wire.sym} -740 160 2 0 {name=l4 lab=vss}
N -110 -20 -70 -20 {}
C {devices/lab_wire.sym} -70 -20 0 1 {name=l5 lab=VOUTN}
N -110 20 -70 20 {}
C {devices/lab_wire.sym} -70 20 0 1 {name=l6 lab=VOUTP}
N -220 -80 -220 -120 {}
C {devices/lab_wire.sym} -220 -120 0 1 {name=l7 lab=vdd}
N 490 -100 530 -100 {}
C {devices/lab_wire.sym} 530 -100 0 1 {name=l8 lab=VB1}
N 490 -60 530 -60 {}
C {devices/lab_wire.sym} 530 -60 0 1 {name=l9 lab=VB2}
N 490 -20 530 -20 {}
C {devices/lab_wire.sym} 530 -20 0 1 {name=l10 lab=VB3}
N 490 20 530 20 {}
C {devices/lab_wire.sym} 530 20 0 1 {name=l11 lab=VB4}
N 490 60 530 60 {}
C {devices/lab_wire.sym} 530 60 0 1 {name=l12 lab=net10}
N 490 100 530 100 {}
C {devices/lab_wire.sym} 530 100 0 1 {name=l13 lab=net7}
N 300 -160 300 -200 {}
C {devices/lab_wire.sym} 300 -200 0 1 {name=l14 lab=vdd}
N 710 -20 670 -20 {}
C {devices/lab_wire.sym} 670 -20 0 0 {name=l15 lab=VINN}
N 710 20 670 20 {}
C {devices/lab_wire.sym} 670 20 0 0 {name=l16 lab=VINP}
N 930 -40 970 -40 {}
C {devices/lab_wire.sym} 970 -40 0 1 {name=l17 lab=DM_2}
N 930 0 970 0 {}
C {devices/lab_wire.sym} 970 0 0 1 {name=l18 lab=net063}
N 930 40 970 40 {}
C {devices/lab_wire.sym} 970 40 0 1 {name=l19 lab=net31}
N -1210 370 -1210 330 {}
C {devices/lab_wire.sym} -1210 330 0 1 {name=l20 lab=VOUTP}
N -1210 430 -1210 470 {}
C {devices/lab_wire.sym} -1210 470 2 0 {name=l21 lab=VOUT}
N -990 370 -990 330 {}
C {devices/lab_wire.sym} -990 330 0 1 {name=l22 lab=net10}
N -990 430 -990 470 {}
C {devices/lab_wire.sym} -990 470 2 0 {name=l23 lab=net4}
N -1430 370 -1430 330 {}
C {devices/lab_wire.sym} -1430 330 0 1 {name=l24 lab=VB1}
N -1430 430 -1430 470 {}
C {devices/lab_wire.sym} -1430 470 2 0 {name=l25 lab=vss}
N -770 370 -770 330 {}
C {devices/lab_wire.sym} -770 330 0 1 {name=l26 lab=net4}
N -770 430 -770 470 {}
C {devices/lab_wire.sym} -770 470 2 0 {name=l27 lab=vss}
N -200 -370 -200 -330 {}
C {devices/lab_wire.sym} -200 -330 2 0 {name=l28 lab=net043}
N -240 -400 -280 -400 {}
C {devices/lab_wire.sym} -280 -400 0 0 {name=l29 lab=VOUTP}
N -200 -430 -200 -470 {}
C {devices/lab_wire.sym} -200 -470 0 1 {name=l30 lab=vdd}
N -200 -400 -160 -400 {}
C {devices/lab_wire.sym} -160 -400 0 1 {name=l31 lab=vdd}
N 20 -370 20 -330 {}
C {devices/lab_wire.sym} 20 -330 2 0 {name=l32 lab=VOUT}
N -20 -400 -60 -400 {}
C {devices/lab_wire.sym} -60 -400 0 0 {name=l33 lab=VOUTP}
N 20 -430 20 -470 {}
C {devices/lab_wire.sym} 20 -470 0 1 {name=l34 lab=vdd}
N 20 -400 60 -400 {}
C {devices/lab_wire.sym} 60 -400 0 1 {name=l35 lab=vdd}
N -530 370 -530 330 {}
C {devices/lab_wire.sym} -530 330 0 1 {name=l36 lab=VOUTN}
N -570 400 -610 400 {}
C {devices/lab_wire.sym} -610 400 0 0 {name=l37 lab=VB3}
N -530 430 -530 470 {}
C {devices/lab_wire.sym} -530 470 2 0 {name=l38 lab=DM_2}
N -530 400 -490 400 {}
C {devices/lab_wire.sym} -490 400 0 1 {name=l39 lab=vss}
N -310 370 -310 330 {}
C {devices/lab_wire.sym} -310 330 0 1 {name=l40 lab=VOUTP}
N -350 400 -390 400 {}
C {devices/lab_wire.sym} -390 400 0 0 {name=l41 lab=VB3}
N -310 430 -310 470 {}
C {devices/lab_wire.sym} -310 470 2 0 {name=l42 lab=net063}
N -310 400 -270 400 {}
C {devices/lab_wire.sym} -270 400 0 1 {name=l43 lab=vss}
N -90 370 -90 330 {}
C {devices/lab_wire.sym} -90 330 0 1 {name=l44 lab=DM_2}
N -130 400 -170 400 {}
C {devices/lab_wire.sym} -170 400 0 0 {name=l45 lab=VB4}
N -90 430 -90 470 {}
C {devices/lab_wire.sym} -90 470 2 0 {name=l46 lab=vss}
N -90 400 -50 400 {}
C {devices/lab_wire.sym} -50 400 0 1 {name=l47 lab=vss}
N 130 370 130 330 {}
C {devices/lab_wire.sym} 130 330 0 1 {name=l48 lab=net063}
N 90 400 50 400 {}
C {devices/lab_wire.sym} 50 400 0 0 {name=l49 lab=VB4}
N 130 430 130 470 {}
C {devices/lab_wire.sym} 130 470 2 0 {name=l50 lab=vss}
N 130 400 170 400 {}
C {devices/lab_wire.sym} 170 400 0 1 {name=l51 lab=vss}
N 350 370 350 330 {}
C {devices/lab_wire.sym} 350 330 0 1 {name=l52 lab=VOUT}
N 310 400 270 400 {}
C {devices/lab_wire.sym} 270 400 0 0 {name=l53 lab=net10}
N 350 430 350 470 {}
C {devices/lab_wire.sym} 350 470 2 0 {name=l54 lab=vss}
N 350 400 390 400 {}
C {devices/lab_wire.sym} 390 400 0 1 {name=l55 lab=vss}
N 240 -370 240 -330 {}
C {devices/lab_wire.sym} 240 -330 2 0 {name=l56 lab=net31}
N 200 -400 160 -400 {}
C {devices/lab_wire.sym} 160 -400 0 0 {name=l57 lab=VB1}
N 240 -430 240 -470 {}
C {devices/lab_wire.sym} 240 -470 0 1 {name=l58 lab=vdd}
N 240 -400 280 -400 {}
C {devices/lab_wire.sym} 280 -400 0 1 {name=l59 lab=vdd}
N 570 370 570 330 {}
C {devices/lab_wire.sym} 570 330 0 1 {name=l60 lab=net043}
N 530 400 490 400 {}
C {devices/lab_wire.sym} 490 400 0 0 {name=l61 lab=VB3}
N 570 430 570 470 {}
C {devices/lab_wire.sym} 570 470 2 0 {name=l62 lab=net1}
N 570 400 610 400 {}
C {devices/lab_wire.sym} 610 400 0 1 {name=l63 lab=vss}
N 790 370 790 330 {}
C {devices/lab_wire.sym} 790 330 0 1 {name=l64 lab=net1}
N 750 400 710 400 {}
C {devices/lab_wire.sym} 710 400 0 0 {name=l65 lab=VB4}
N 790 430 790 470 {}
C {devices/lab_wire.sym} 790 470 2 0 {name=l66 lab=vss}
N 790 400 830 400 {}
C {devices/lab_wire.sym} 830 400 0 1 {name=l67 lab=vss}
N 1010 370 1010 330 {}
C {devices/lab_wire.sym} 1010 330 0 1 {name=l68 lab=net10}
N 970 400 930 400 {}
C {devices/lab_wire.sym} 930 400 0 0 {name=l69 lab=net043}
N 1010 430 1010 470 {}
C {devices/lab_wire.sym} 1010 470 2 0 {name=l70 lab=vss}
N 1010 400 1050 400 {}
C {devices/lab_wire.sym} 1050 400 0 1 {name=l71 lab=vss}
N 1230 370 1230 330 {}
C {devices/lab_wire.sym} 1230 330 0 1 {name=l72 lab=net1}
N 1190 400 1150 400 {}
C {devices/lab_wire.sym} 1150 400 0 0 {name=l73 lab=net043}
N 1230 430 1230 470 {}
C {devices/lab_wire.sym} 1230 470 2 0 {name=l74 lab=vss}
N 1230 400 1270 400 {}
C {devices/lab_wire.sym} 1270 400 0 1 {name=l75 lab=vss}
