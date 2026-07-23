v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_026_fan_chopper_ota} -1690 -540 0 0 0.4 0.4 {}
C {blocks/dp_pmos_simple_1.sym} 0 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -1430 340 0 0 {name=CM1 value='x_dut_cm1_value'}
C {devices/capa_np.sym} -1210 340 0 0 {name=CM2 value='x_dut_cm2_value'}
C {devices/vsource_np.sym} -1650 340 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -1650 120 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -1650 -100 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -1650 -320 0 0 {name=VB4 value="dc {vb4}"}
C {devices/sg13_lv_pmos_np.sym} -880 -340 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -660 -340 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} -440 -340 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -990 340 0 0 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} -770 340 0 0 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} -550 340 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} -330 340 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} -110 340 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} 110 340 0 0 {name=M17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 330 340 0 0 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_pmos_np.sym} 550 340 0 0 {name=M19 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_nmos_np.sym} 770 340 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_pmos_np.sym} -220 -340 0 0 {name=M21 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 990 340 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} 0 -340 0 0 {name=M23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_nmos_np.sym} 1210 340 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 1430 340 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 220 -340 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 440 -340 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 660 -340 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 880 -340 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -110 -20 -150 -20 {}
C {devices/lab_wire.sym} -150 -20 0 0 {name=l0 lab=vinn}
N -110 20 -150 20 {}
C {devices/lab_wire.sym} -150 20 0 0 {name=l1 lab=vinp}
N 110 -40 150 -40 {}
C {devices/lab_wire.sym} 150 -40 0 1 {name=l2 lab=fold_n}
N 110 0 150 0 {}
C {devices/lab_wire.sym} 150 0 0 1 {name=l3 lab=fold_p}
N 110 40 150 40 {}
C {devices/lab_wire.sym} 150 40 0 1 {name=l4 lab=tail}
N 0 -100 0 -140 {}
C {devices/lab_wire.sym} 0 -140 0 1 {name=l5 lab=vdd}
N -1430 310 -1430 270 {}
C {devices/lab_wire.sym} -1430 270 0 1 {name=l6 lab=g2_p}
N -1430 370 -1430 410 {}
C {devices/lab_wire.sym} -1430 410 2 0 {name=l7 lab=voutp}
N -1210 310 -1210 270 {}
C {devices/lab_wire.sym} -1210 270 0 1 {name=l8 lab=g2_n}
N -1210 370 -1210 410 {}
C {devices/lab_wire.sym} -1210 410 2 0 {name=l9 lab=voutn}
N -1650 310 -1650 270 {}
C {devices/lab_wire.sym} -1650 270 0 1 {name=l10 lab=vb1}
N -1650 370 -1650 410 {}
C {devices/lab_wire.sym} -1650 410 2 0 {name=l11 lab=vss}
N -1650 90 -1650 50 {}
C {devices/lab_wire.sym} -1650 50 0 1 {name=l12 lab=vb2}
N -1650 150 -1650 190 {}
C {devices/lab_wire.sym} -1650 190 2 0 {name=l13 lab=vss}
N -1650 -130 -1650 -170 {}
C {devices/lab_wire.sym} -1650 -170 0 1 {name=l14 lab=vb3}
N -1650 -70 -1650 -30 {}
C {devices/lab_wire.sym} -1650 -30 2 0 {name=l15 lab=vss}
N -1650 -350 -1650 -390 {}
C {devices/lab_wire.sym} -1650 -390 0 1 {name=l16 lab=vb4}
N -1650 -290 -1650 -250 {}
C {devices/lab_wire.sym} -1650 -250 2 0 {name=l17 lab=vss}
N -860 -310 -860 -270 {}
C {devices/lab_wire.sym} -860 -270 2 0 {name=l18 lab=tail}
N -900 -340 -940 -340 {}
C {devices/lab_wire.sym} -940 -340 0 0 {name=l19 lab=vb4}
N -860 -370 -860 -410 {}
C {devices/lab_wire.sym} -860 -410 0 1 {name=l20 lab=vdd}
N -860 -340 -820 -340 {}
C {devices/lab_wire.sym} -820 -340 0 1 {name=l21 lab=vdd}
N -640 -310 -640 -270 {}
C {devices/lab_wire.sym} -640 -270 2 0 {name=l22 lab=out1_n}
N -680 -340 -720 -340 {}
C {devices/lab_wire.sym} -720 -340 0 0 {name=l23 lab=vb3}
N -640 -370 -640 -410 {}
C {devices/lab_wire.sym} -640 -410 0 1 {name=l24 lab=casc_src_n}
N -640 -340 -600 -340 {}
C {devices/lab_wire.sym} -600 -340 0 1 {name=l25 lab=vdd}
N -420 -310 -420 -270 {}
C {devices/lab_wire.sym} -420 -270 2 0 {name=l26 lab=out1_p}
N -460 -340 -500 -340 {}
C {devices/lab_wire.sym} -500 -340 0 0 {name=l27 lab=vb3}
N -420 -370 -420 -410 {}
C {devices/lab_wire.sym} -420 -410 0 1 {name=l28 lab=casc_src_p}
N -420 -340 -380 -340 {}
C {devices/lab_wire.sym} -380 -340 0 1 {name=l29 lab=vdd}
N -970 310 -970 270 {}
C {devices/lab_wire.sym} -970 270 0 1 {name=l30 lab=out1_p}
N -1010 340 -1050 340 {}
C {devices/lab_wire.sym} -1050 340 0 0 {name=l31 lab=vb2}
N -970 370 -970 410 {}
C {devices/lab_wire.sym} -970 410 2 0 {name=l32 lab=fold_p}
N -970 340 -930 340 {}
C {devices/lab_wire.sym} -930 340 0 1 {name=l33 lab=vss}
N -750 310 -750 270 {}
C {devices/lab_wire.sym} -750 270 0 1 {name=l34 lab=out1_n}
N -790 340 -830 340 {}
C {devices/lab_wire.sym} -830 340 0 0 {name=l35 lab=vb2}
N -750 370 -750 410 {}
C {devices/lab_wire.sym} -750 410 2 0 {name=l36 lab=fold_n}
N -750 340 -710 340 {}
C {devices/lab_wire.sym} -710 340 0 1 {name=l37 lab=vss}
N -530 310 -530 270 {}
C {devices/lab_wire.sym} -530 270 0 1 {name=l38 lab=voutp}
N -570 340 -610 340 {}
C {devices/lab_wire.sym} -610 340 0 0 {name=l39 lab=g2_p}
N -530 370 -530 410 {}
C {devices/lab_wire.sym} -530 410 2 0 {name=l40 lab=vss}
N -530 340 -490 340 {}
C {devices/lab_wire.sym} -490 340 0 1 {name=l41 lab=vss}
N -310 310 -310 270 {}
C {devices/lab_wire.sym} -310 270 0 1 {name=l42 lab=voutn}
N -350 340 -390 340 {}
C {devices/lab_wire.sym} -390 340 0 0 {name=l43 lab=g2_n}
N -310 370 -310 410 {}
C {devices/lab_wire.sym} -310 410 2 0 {name=l44 lab=vss}
N -310 340 -270 340 {}
C {devices/lab_wire.sym} -270 340 0 1 {name=l45 lab=vss}
N -90 310 -90 270 {}
C {devices/lab_wire.sym} -90 270 0 1 {name=l46 lab=out1_n}
N -130 340 -170 340 {}
C {devices/lab_wire.sym} -170 340 0 0 {name=l47 lab=vdd}
N -90 370 -90 410 {}
C {devices/lab_wire.sym} -90 410 2 0 {name=l48 lab=g2_n}
N -90 340 -50 340 {}
C {devices/lab_wire.sym} -50 340 0 1 {name=l49 lab=vss}
N 130 370 130 410 {}
C {devices/lab_wire.sym} 130 410 2 0 {name=l50 lab=g2_n}
N 90 340 50 340 {}
C {devices/lab_wire.sym} 50 340 0 0 {name=l51 lab=vss}
N 130 310 130 270 {}
C {devices/lab_wire.sym} 130 270 0 1 {name=l52 lab=out1_n}
N 130 340 170 340 {}
C {devices/lab_wire.sym} 170 340 0 1 {name=l53 lab=vdd}
N 350 310 350 270 {}
C {devices/lab_wire.sym} 350 270 0 1 {name=l54 lab=out1_p}
N 310 340 270 340 {}
C {devices/lab_wire.sym} 270 340 0 0 {name=l55 lab=vdd}
N 350 370 350 410 {}
C {devices/lab_wire.sym} 350 410 2 0 {name=l56 lab=g2_p}
N 350 340 390 340 {}
C {devices/lab_wire.sym} 390 340 0 1 {name=l57 lab=vss}
N 570 370 570 410 {}
C {devices/lab_wire.sym} 570 410 2 0 {name=l58 lab=g2_p}
N 530 340 490 340 {}
C {devices/lab_wire.sym} 490 340 0 0 {name=l59 lab=vss}
N 570 310 570 270 {}
C {devices/lab_wire.sym} 570 270 0 1 {name=l60 lab=out1_p}
N 570 340 610 340 {}
C {devices/lab_wire.sym} 610 340 0 1 {name=l61 lab=vdd}
N 790 310 790 270 {}
C {devices/lab_wire.sym} 790 270 0 1 {name=l62 lab=out1_p}
N 750 340 710 340 {}
C {devices/lab_wire.sym} 710 340 0 0 {name=l63 lab=vss}
N 790 370 790 410 {}
C {devices/lab_wire.sym} 790 410 2 0 {name=l64 lab=g2_n}
N 790 340 830 340 {}
C {devices/lab_wire.sym} 830 340 0 1 {name=l65 lab=vss}
N -200 -310 -200 -270 {}
C {devices/lab_wire.sym} -200 -270 2 0 {name=l66 lab=g2_n}
N -240 -340 -280 -340 {}
C {devices/lab_wire.sym} -280 -340 0 0 {name=l67 lab=vdd}
N -200 -370 -200 -410 {}
C {devices/lab_wire.sym} -200 -410 0 1 {name=l68 lab=out1_p}
N -200 -340 -160 -340 {}
C {devices/lab_wire.sym} -160 -340 0 1 {name=l69 lab=vdd}
N 1010 310 1010 270 {}
C {devices/lab_wire.sym} 1010 270 0 1 {name=l70 lab=out1_n}
N 970 340 930 340 {}
C {devices/lab_wire.sym} 930 340 0 0 {name=l71 lab=vss}
N 1010 370 1010 410 {}
C {devices/lab_wire.sym} 1010 410 2 0 {name=l72 lab=g2_p}
N 1010 340 1050 340 {}
C {devices/lab_wire.sym} 1050 340 0 1 {name=l73 lab=vss}
N 20 -310 20 -270 {}
C {devices/lab_wire.sym} 20 -270 2 0 {name=l74 lab=g2_p}
N -20 -340 -60 -340 {}
C {devices/lab_wire.sym} -60 -340 0 0 {name=l75 lab=vdd}
N 20 -370 20 -410 {}
C {devices/lab_wire.sym} 20 -410 0 1 {name=l76 lab=out1_n}
N 20 -340 60 -340 {}
C {devices/lab_wire.sym} 60 -340 0 1 {name=l77 lab=vdd}
N 1230 310 1230 270 {}
C {devices/lab_wire.sym} 1230 270 0 1 {name=l78 lab=fold_p}
N 1190 340 1150 340 {}
C {devices/lab_wire.sym} 1150 340 0 0 {name=l79 lab=vb1}
N 1230 370 1230 410 {}
C {devices/lab_wire.sym} 1230 410 2 0 {name=l80 lab=vss}
N 1230 340 1270 340 {}
C {devices/lab_wire.sym} 1270 340 0 1 {name=l81 lab=vss}
N 1450 310 1450 270 {}
C {devices/lab_wire.sym} 1450 270 0 1 {name=l82 lab=fold_n}
N 1410 340 1370 340 {}
C {devices/lab_wire.sym} 1370 340 0 0 {name=l83 lab=vb1}
N 1450 370 1450 410 {}
C {devices/lab_wire.sym} 1450 410 2 0 {name=l84 lab=vss}
N 1450 340 1490 340 {}
C {devices/lab_wire.sym} 1490 340 0 1 {name=l85 lab=vss}
N 240 -310 240 -270 {}
C {devices/lab_wire.sym} 240 -270 2 0 {name=l86 lab=casc_src_n}
N 200 -340 160 -340 {}
C {devices/lab_wire.sym} 160 -340 0 0 {name=l87 lab=vb4}
N 240 -370 240 -410 {}
C {devices/lab_wire.sym} 240 -410 0 1 {name=l88 lab=vdd}
N 240 -340 280 -340 {}
C {devices/lab_wire.sym} 280 -340 0 1 {name=l89 lab=vdd}
N 460 -310 460 -270 {}
C {devices/lab_wire.sym} 460 -270 2 0 {name=l90 lab=casc_src_p}
N 420 -340 380 -340 {}
C {devices/lab_wire.sym} 380 -340 0 0 {name=l91 lab=vb4}
N 460 -370 460 -410 {}
C {devices/lab_wire.sym} 460 -410 0 1 {name=l92 lab=vdd}
N 460 -340 500 -340 {}
C {devices/lab_wire.sym} 500 -340 0 1 {name=l93 lab=vdd}
N 680 -310 680 -270 {}
C {devices/lab_wire.sym} 680 -270 2 0 {name=l94 lab=voutp}
N 640 -340 600 -340 {}
C {devices/lab_wire.sym} 600 -340 0 0 {name=l95 lab=vb4}
N 680 -370 680 -410 {}
C {devices/lab_wire.sym} 680 -410 0 1 {name=l96 lab=vdd}
N 680 -340 720 -340 {}
C {devices/lab_wire.sym} 720 -340 0 1 {name=l97 lab=vdd}
N 900 -310 900 -270 {}
C {devices/lab_wire.sym} 900 -270 2 0 {name=l98 lab=voutn}
N 860 -340 820 -340 {}
C {devices/lab_wire.sym} 820 -340 0 0 {name=l99 lab=vb4}
N 900 -370 900 -410 {}
C {devices/lab_wire.sym} 900 -410 0 1 {name=l100 lab=vdd}
N 900 -340 940 -340 {}
C {devices/lab_wire.sym} 940 -340 0 1 {name=l101 lab=vdd}
