v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_034_fan_chopper_cmfb} -2130 -740 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -660 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_simple_1.sym} -220 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_pmos_simple_1.sym} 220 0 0 0 {name=xdp_pmos_simple_1}
C {blocks/dp_pmos_simple_2.sym} 660 0 0 0 {name=xdp_pmos_simple_2}
C {devices/capa_np.sym} -1870 340 0 0 {name=CCM value='c_cm'}
C {devices/capa_np.sym} -1650 340 0 0 {name=CM1_CORE value='x_dut_cm1_core_value'}
C {devices/capa_np.sym} -1430 340 0 0 {name=CM2_CORE value='x_dut_cm2_core_value'}
C {devices/res_np.sym} -1210 340 0 0 {name=RMN_CMFB value='x_dut_rmn_cmfb_value'}
C {devices/res_np.sym} -990 340 0 0 {name=RMP_CMFB value='x_dut_rmp_cmfb_value'}
C {devices/vsource_np.sym} -2090 340 0 0 {name=VB1_CORE value="dc {vb1_core}"}
C {devices/vsource_np.sym} -2090 120 0 0 {name=VB2_CORE value="dc {vb2_core}"}
C {devices/vsource_np.sym} -2090 -100 0 0 {name=VB3_CORE value="dc {vb3_core}"}
C {devices/vsource_np.sym} -2090 -320 0 0 {name=VB4_CORE value="dc {vb4_core}"}
C {devices/vsource_np.sym} -2090 -540 0 0 {name=VREFCM value="dc {vcm_ref}"}
C {devices/sg13_lv_pmos_np.sym} -880 -340 0 0 {name=M10_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_core_w l=x_dut_xm10_core_l m=x_dut_xm10_core_m}
C {devices/sg13_lv_pmos_np.sym} -660 -340 0 0 {name=M11_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_core_w l=x_dut_xm11_core_l m=x_dut_xm11_core_m}
C {devices/sg13_lv_nmos_np.sym} -770 340 0 0 {name=M12_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_core_w l=x_dut_xm12_core_l m=x_dut_xm12_core_m}
C {devices/sg13_lv_nmos_np.sym} -550 340 0 0 {name=M13_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_core_w l=x_dut_xm13_core_l m=x_dut_xm13_core_m}
C {devices/sg13_lv_nmos_np.sym} -330 340 0 0 {name=M14_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_core_w l=x_dut_xm14_core_l m=x_dut_xm14_core_m}
C {devices/sg13_lv_nmos_np.sym} -110 340 0 0 {name=M15_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_core_w l=x_dut_xm15_core_l m=x_dut_xm15_core_m}
C {devices/sg13_lv_nmos_np.sym} 110 340 0 0 {name=M16_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_core_w l=x_dut_xm16_core_l m=x_dut_xm16_core_m}
C {devices/sg13_lv_pmos_np.sym} 330 340 0 0 {name=M17_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_core_w l=x_dut_xm17_core_l m=x_dut_xm17_core_m}
C {devices/sg13_lv_nmos_np.sym} 550 340 0 0 {name=M18_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_core_w l=x_dut_xm18_core_l m=x_dut_xm18_core_m}
C {devices/sg13_lv_pmos_np.sym} 770 340 0 0 {name=M19_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_core_w l=x_dut_xm19_core_l m=x_dut_xm19_core_m}
C {devices/sg13_lv_pmos_np.sym} -440 -340 0 0 {name=M1_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_core_w l=x_dut_xm1_core_l m=x_dut_xm1_core_m}
C {devices/sg13_lv_nmos_np.sym} 990 340 0 0 {name=M20_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_core_w l=x_dut_xm20_core_l m=x_dut_xm20_core_m}
C {devices/sg13_lv_pmos_np.sym} -220 -340 0 0 {name=M21_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_core_w l=x_dut_xm21_core_l m=x_dut_xm21_core_m}
C {devices/sg13_lv_nmos_np.sym} 1210 340 0 0 {name=M22_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_core_w l=x_dut_xm22_core_l m=x_dut_xm22_core_m}
C {devices/sg13_lv_pmos_np.sym} 0 -340 0 0 {name=M23_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_core_w l=x_dut_xm23_core_l m=x_dut_xm23_core_m}
C {devices/sg13_lv_nmos_np.sym} 1430 340 0 0 {name=M4_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_core_w l=x_dut_xm4_core_l m=x_dut_xm4_core_m}
C {devices/sg13_lv_nmos_np.sym} 1650 340 0 0 {name=M5_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_core_w l=x_dut_xm5_core_l m=x_dut_xm5_core_m}
C {devices/sg13_lv_pmos_np.sym} 220 -340 0 0 {name=M6_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_core_w l=x_dut_xm6_core_l m=x_dut_xm6_core_m}
C {devices/sg13_lv_nmos_np.sym} 1870 340 0 0 {name=M7_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_cmfb_w l=x_dut_xm7_cmfb_l m=x_dut_xm7_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 440 -340 0 0 {name=M7_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_core_w l=x_dut_xm7_core_l m=x_dut_xm7_core_m}
C {devices/sg13_lv_pmos_np.sym} 660 -340 0 0 {name=M8O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8o_w l=x_dut_xm8o_l m=x_dut_xm8o_m}
C {devices/sg13_lv_pmos_np.sym} 880 -340 0 0 {name=M9O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9o_w l=x_dut_xm9o_l m=x_dut_xm9o_m}
N -550 -20 -510 -20 {}
C {devices/lab_wire.sym} -510 -20 0 1 {name=l0 lab=cmfb__bias}
N -550 20 -510 20 {}
C {devices/lab_wire.sym} -510 20 0 1 {name=l1 lab=cmfb__ptail}
N -660 -80 -660 -120 {}
C {devices/lab_wire.sym} -660 -120 0 1 {name=l2 lab=vdd}
N -110 -20 -70 -20 {}
C {devices/lab_wire.sym} -70 -20 0 1 {name=l3 lab=cmfb__mirr}
N -110 20 -70 20 {}
C {devices/lab_wire.sym} -70 20 0 1 {name=l4 lab=vb4o}
N -220 80 -220 120 {}
C {devices/lab_wire.sym} -220 120 2 0 {name=l5 lab=vss}
N 110 -20 70 -20 {}
C {devices/lab_wire.sym} 70 -20 0 0 {name=l6 lab=vinn}
N 110 20 70 20 {}
C {devices/lab_wire.sym} 70 20 0 0 {name=l7 lab=vinp}
N 330 -40 370 -40 {}
C {devices/lab_wire.sym} 370 -40 0 1 {name=l8 lab=core__fold_n}
N 330 0 370 0 {}
C {devices/lab_wire.sym} 370 0 0 1 {name=l9 lab=core__fold_p}
N 330 40 370 40 {}
C {devices/lab_wire.sym} 370 40 0 1 {name=l10 lab=core__tail}
N 220 -100 220 -140 {}
C {devices/lab_wire.sym} 220 -140 0 1 {name=l11 lab=vdd}
N 550 -20 510 -20 {}
C {devices/lab_wire.sym} 510 -20 0 0 {name=l12 lab=cmfb__cm_sense}
N 550 20 510 20 {}
C {devices/lab_wire.sym} 510 20 0 0 {name=l13 lab=vref_cm}
N 770 -40 810 -40 {}
C {devices/lab_wire.sym} 810 -40 0 1 {name=l14 lab=cmfb__mirr}
N 770 0 810 0 {}
C {devices/lab_wire.sym} 810 0 0 1 {name=l15 lab=cmfb__ptail}
N 770 40 810 40 {}
C {devices/lab_wire.sym} 810 40 0 1 {name=l16 lab=vb4o}
N 660 -100 660 -140 {}
C {devices/lab_wire.sym} 660 -140 0 1 {name=l17 lab=vdd}
N -1870 310 -1870 270 {}
C {devices/lab_wire.sym} -1870 270 0 1 {name=l18 lab=vb4o}
N -1870 370 -1870 410 {}
C {devices/lab_wire.sym} -1870 410 2 0 {name=l19 lab=vss}
N -1650 310 -1650 270 {}
C {devices/lab_wire.sym} -1650 270 0 1 {name=l20 lab=core__g2_p}
N -1650 370 -1650 410 {}
C {devices/lab_wire.sym} -1650 410 2 0 {name=l21 lab=voutp}
N -1430 310 -1430 270 {}
C {devices/lab_wire.sym} -1430 270 0 1 {name=l22 lab=core__g2_n}
N -1430 370 -1430 410 {}
C {devices/lab_wire.sym} -1430 410 2 0 {name=l23 lab=voutn}
N -1210 310 -1210 270 {}
C {devices/lab_wire.sym} -1210 270 0 1 {name=l24 lab=voutn}
N -1210 370 -1210 410 {}
C {devices/lab_wire.sym} -1210 410 2 0 {name=l25 lab=cmfb__cm_sense}
N -990 310 -990 270 {}
C {devices/lab_wire.sym} -990 270 0 1 {name=l26 lab=cmfb__cm_sense}
N -990 370 -990 410 {}
C {devices/lab_wire.sym} -990 410 2 0 {name=l27 lab=voutp}
N -2090 310 -2090 270 {}
C {devices/lab_wire.sym} -2090 270 0 1 {name=l28 lab=core__vb1}
N -2090 370 -2090 410 {}
C {devices/lab_wire.sym} -2090 410 2 0 {name=l29 lab=vss}
N -2090 90 -2090 50 {}
C {devices/lab_wire.sym} -2090 50 0 1 {name=l30 lab=core__vb2}
N -2090 150 -2090 190 {}
C {devices/lab_wire.sym} -2090 190 2 0 {name=l31 lab=vss}
N -2090 -130 -2090 -170 {}
C {devices/lab_wire.sym} -2090 -170 0 1 {name=l32 lab=core__vb3}
N -2090 -70 -2090 -30 {}
C {devices/lab_wire.sym} -2090 -30 2 0 {name=l33 lab=vss}
N -2090 -350 -2090 -390 {}
C {devices/lab_wire.sym} -2090 -390 0 1 {name=l34 lab=core__vb4}
N -2090 -290 -2090 -250 {}
C {devices/lab_wire.sym} -2090 -250 2 0 {name=l35 lab=vss}
N -2090 -570 -2090 -610 {}
C {devices/lab_wire.sym} -2090 -610 0 1 {name=l36 lab=vref_cm}
N -2090 -510 -2090 -470 {}
C {devices/lab_wire.sym} -2090 -470 2 0 {name=l37 lab=vss}
N -860 -310 -860 -270 {}
C {devices/lab_wire.sym} -860 -270 2 0 {name=l38 lab=core__out1_n}
N -900 -340 -940 -340 {}
C {devices/lab_wire.sym} -940 -340 0 0 {name=l39 lab=core__vb3}
N -860 -370 -860 -410 {}
C {devices/lab_wire.sym} -860 -410 0 1 {name=l40 lab=core__casc_src_n}
N -860 -340 -820 -340 {}
C {devices/lab_wire.sym} -820 -340 0 1 {name=l41 lab=vdd}
N -640 -310 -640 -270 {}
C {devices/lab_wire.sym} -640 -270 2 0 {name=l42 lab=core__out1_p}
N -680 -340 -720 -340 {}
C {devices/lab_wire.sym} -720 -340 0 0 {name=l43 lab=core__vb3}
N -640 -370 -640 -410 {}
C {devices/lab_wire.sym} -640 -410 0 1 {name=l44 lab=core__casc_src_p}
N -640 -340 -600 -340 {}
C {devices/lab_wire.sym} -600 -340 0 1 {name=l45 lab=vdd}
N -750 310 -750 270 {}
C {devices/lab_wire.sym} -750 270 0 1 {name=l46 lab=core__out1_p}
N -790 340 -830 340 {}
C {devices/lab_wire.sym} -830 340 0 0 {name=l47 lab=core__vb2}
N -750 370 -750 410 {}
C {devices/lab_wire.sym} -750 410 2 0 {name=l48 lab=core__fold_p}
N -750 340 -710 340 {}
C {devices/lab_wire.sym} -710 340 0 1 {name=l49 lab=vss}
N -530 310 -530 270 {}
C {devices/lab_wire.sym} -530 270 0 1 {name=l50 lab=core__out1_n}
N -570 340 -610 340 {}
C {devices/lab_wire.sym} -610 340 0 0 {name=l51 lab=core__vb2}
N -530 370 -530 410 {}
C {devices/lab_wire.sym} -530 410 2 0 {name=l52 lab=core__fold_n}
N -530 340 -490 340 {}
C {devices/lab_wire.sym} -490 340 0 1 {name=l53 lab=vss}
N -310 310 -310 270 {}
C {devices/lab_wire.sym} -310 270 0 1 {name=l54 lab=voutp}
N -350 340 -390 340 {}
C {devices/lab_wire.sym} -390 340 0 0 {name=l55 lab=core__g2_p}
N -310 370 -310 410 {}
C {devices/lab_wire.sym} -310 410 2 0 {name=l56 lab=vss}
N -310 340 -270 340 {}
C {devices/lab_wire.sym} -270 340 0 1 {name=l57 lab=vss}
N -90 310 -90 270 {}
C {devices/lab_wire.sym} -90 270 0 1 {name=l58 lab=voutn}
N -130 340 -170 340 {}
C {devices/lab_wire.sym} -170 340 0 0 {name=l59 lab=core__g2_n}
N -90 370 -90 410 {}
C {devices/lab_wire.sym} -90 410 2 0 {name=l60 lab=vss}
N -90 340 -50 340 {}
C {devices/lab_wire.sym} -50 340 0 1 {name=l61 lab=vss}
N 130 310 130 270 {}
C {devices/lab_wire.sym} 130 270 0 1 {name=l62 lab=core__out1_n}
N 90 340 50 340 {}
C {devices/lab_wire.sym} 50 340 0 0 {name=l63 lab=vdd}
N 130 370 130 410 {}
C {devices/lab_wire.sym} 130 410 2 0 {name=l64 lab=core__g2_n}
N 130 340 170 340 {}
C {devices/lab_wire.sym} 170 340 0 1 {name=l65 lab=vss}
N 350 370 350 410 {}
C {devices/lab_wire.sym} 350 410 2 0 {name=l66 lab=core__g2_n}
N 310 340 270 340 {}
C {devices/lab_wire.sym} 270 340 0 0 {name=l67 lab=vss}
N 350 310 350 270 {}
C {devices/lab_wire.sym} 350 270 0 1 {name=l68 lab=core__out1_n}
N 350 340 390 340 {}
C {devices/lab_wire.sym} 390 340 0 1 {name=l69 lab=vdd}
N 570 310 570 270 {}
C {devices/lab_wire.sym} 570 270 0 1 {name=l70 lab=core__out1_p}
N 530 340 490 340 {}
C {devices/lab_wire.sym} 490 340 0 0 {name=l71 lab=vdd}
N 570 370 570 410 {}
C {devices/lab_wire.sym} 570 410 2 0 {name=l72 lab=core__g2_p}
N 570 340 610 340 {}
C {devices/lab_wire.sym} 610 340 0 1 {name=l73 lab=vss}
N 790 370 790 410 {}
C {devices/lab_wire.sym} 790 410 2 0 {name=l74 lab=core__g2_p}
N 750 340 710 340 {}
C {devices/lab_wire.sym} 710 340 0 0 {name=l75 lab=vss}
N 790 310 790 270 {}
C {devices/lab_wire.sym} 790 270 0 1 {name=l76 lab=core__out1_p}
N 790 340 830 340 {}
C {devices/lab_wire.sym} 830 340 0 1 {name=l77 lab=vdd}
N -420 -310 -420 -270 {}
C {devices/lab_wire.sym} -420 -270 2 0 {name=l78 lab=core__tail}
N -460 -340 -500 -340 {}
C {devices/lab_wire.sym} -500 -340 0 0 {name=l79 lab=core__vb4}
N -420 -370 -420 -410 {}
C {devices/lab_wire.sym} -420 -410 0 1 {name=l80 lab=vdd}
N -420 -340 -380 -340 {}
C {devices/lab_wire.sym} -380 -340 0 1 {name=l81 lab=vdd}
N 1010 310 1010 270 {}
C {devices/lab_wire.sym} 1010 270 0 1 {name=l82 lab=core__out1_p}
N 970 340 930 340 {}
C {devices/lab_wire.sym} 930 340 0 0 {name=l83 lab=vss}
N 1010 370 1010 410 {}
C {devices/lab_wire.sym} 1010 410 2 0 {name=l84 lab=core__g2_n}
N 1010 340 1050 340 {}
C {devices/lab_wire.sym} 1050 340 0 1 {name=l85 lab=vss}
N -200 -310 -200 -270 {}
C {devices/lab_wire.sym} -200 -270 2 0 {name=l86 lab=core__g2_n}
N -240 -340 -280 -340 {}
C {devices/lab_wire.sym} -280 -340 0 0 {name=l87 lab=vdd}
N -200 -370 -200 -410 {}
C {devices/lab_wire.sym} -200 -410 0 1 {name=l88 lab=core__out1_p}
N -200 -340 -160 -340 {}
C {devices/lab_wire.sym} -160 -340 0 1 {name=l89 lab=vdd}
N 1230 310 1230 270 {}
C {devices/lab_wire.sym} 1230 270 0 1 {name=l90 lab=core__out1_n}
N 1190 340 1150 340 {}
C {devices/lab_wire.sym} 1150 340 0 0 {name=l91 lab=vss}
N 1230 370 1230 410 {}
C {devices/lab_wire.sym} 1230 410 2 0 {name=l92 lab=core__g2_p}
N 1230 340 1270 340 {}
C {devices/lab_wire.sym} 1270 340 0 1 {name=l93 lab=vss}
N 20 -310 20 -270 {}
C {devices/lab_wire.sym} 20 -270 2 0 {name=l94 lab=core__g2_p}
N -20 -340 -60 -340 {}
C {devices/lab_wire.sym} -60 -340 0 0 {name=l95 lab=vdd}
N 20 -370 20 -410 {}
C {devices/lab_wire.sym} 20 -410 0 1 {name=l96 lab=core__out1_n}
N 20 -340 60 -340 {}
C {devices/lab_wire.sym} 60 -340 0 1 {name=l97 lab=vdd}
N 1450 310 1450 270 {}
C {devices/lab_wire.sym} 1450 270 0 1 {name=l98 lab=core__fold_p}
N 1410 340 1370 340 {}
C {devices/lab_wire.sym} 1370 340 0 0 {name=l99 lab=core__vb1}
N 1450 370 1450 410 {}
C {devices/lab_wire.sym} 1450 410 2 0 {name=l100 lab=vss}
N 1450 340 1490 340 {}
C {devices/lab_wire.sym} 1490 340 0 1 {name=l101 lab=vss}
N 1670 310 1670 270 {}
C {devices/lab_wire.sym} 1670 270 0 1 {name=l102 lab=core__fold_n}
N 1630 340 1590 340 {}
C {devices/lab_wire.sym} 1590 340 0 0 {name=l103 lab=core__vb1}
N 1670 370 1670 410 {}
C {devices/lab_wire.sym} 1670 410 2 0 {name=l104 lab=vss}
N 1670 340 1710 340 {}
C {devices/lab_wire.sym} 1710 340 0 1 {name=l105 lab=vss}
N 240 -310 240 -270 {}
C {devices/lab_wire.sym} 240 -270 2 0 {name=l106 lab=core__casc_src_n}
N 200 -340 160 -340 {}
C {devices/lab_wire.sym} 160 -340 0 0 {name=l107 lab=core__vb4}
N 240 -370 240 -410 {}
C {devices/lab_wire.sym} 240 -410 0 1 {name=l108 lab=vdd}
N 240 -340 280 -340 {}
C {devices/lab_wire.sym} 280 -340 0 1 {name=l109 lab=vdd}
N 1890 310 1890 270 {}
C {devices/lab_wire.sym} 1890 270 0 1 {name=l110 lab=cmfb__bias}
N 1850 340 1810 340 {}
C {devices/lab_wire.sym} 1810 340 0 0 {name=l111 lab=cmfb__bias}
N 1890 370 1890 410 {}
C {devices/lab_wire.sym} 1890 410 2 0 {name=l112 lab=vss}
N 1890 340 1930 340 {}
C {devices/lab_wire.sym} 1930 340 0 1 {name=l113 lab=vss}
N 460 -310 460 -270 {}
C {devices/lab_wire.sym} 460 -270 2 0 {name=l114 lab=core__casc_src_p}
N 420 -340 380 -340 {}
C {devices/lab_wire.sym} 380 -340 0 0 {name=l115 lab=core__vb4}
N 460 -370 460 -410 {}
C {devices/lab_wire.sym} 460 -410 0 1 {name=l116 lab=vdd}
N 460 -340 500 -340 {}
C {devices/lab_wire.sym} 500 -340 0 1 {name=l117 lab=vdd}
N 680 -310 680 -270 {}
C {devices/lab_wire.sym} 680 -270 2 0 {name=l118 lab=voutp}
N 640 -340 600 -340 {}
C {devices/lab_wire.sym} 600 -340 0 0 {name=l119 lab=vb4o}
N 680 -370 680 -410 {}
C {devices/lab_wire.sym} 680 -410 0 1 {name=l120 lab=vdd}
N 680 -340 720 -340 {}
C {devices/lab_wire.sym} 720 -340 0 1 {name=l121 lab=vdd}
N 900 -310 900 -270 {}
C {devices/lab_wire.sym} 900 -270 2 0 {name=l122 lab=voutn}
N 860 -340 820 -340 {}
C {devices/lab_wire.sym} 820 -340 0 0 {name=l123 lab=vb4o}
N 900 -370 900 -410 {}
C {devices/lab_wire.sym} 900 -410 0 1 {name=l124 lab=vdd}
N 900 -340 940 -340 {}
C {devices/lab_wire.sym} 940 -340 0 1 {name=l125 lab=vdd}
