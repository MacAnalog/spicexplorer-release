v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_001_hsu_bandpass_classab} -2790 -540 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -930 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_nmos_simple_2.sym} -490 0 0 0 {name=xcm_nmos_simple_2}
C {blocks/pr_series_shared_well_1.sym} -25 0 0 0 {name=xpr_series_shared_well_1}
C {blocks/pr_series_shared_well_2.sym} 465 0 0 0 {name=xpr_series_shared_well_2}
C {blocks/dp_pmos_simple_1.sym} 930 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -2530 340 0 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} -2310 340 0 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} -2090 340 0 0 {name=CF1 value='x_dut_cf1_value'}
C {devices/capa_np.sym} -1870 340 0 0 {name=CF2 value='x_dut_cf2_value'}
C {devices/capa_np.sym} -1650 340 0 0 {name=CIN1 value='x_dut_cin1_value'}
C {devices/capa_np.sym} -1430 340 0 0 {name=CIN2 value='x_dut_cin2_value'}
C {devices/capa_np.sym} -1210 340 0 0 {name=CISRV value='cin_val'}
C {devices/capa_np.sym} -990 340 0 0 {name=COSRV value='cout_val'}
C {devices/res_np.sym} -770 340 0 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} -550 340 0 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} -330 340 0 0 {name=RISRV value='rin_val'}
C {devices/res_np.sym} -110 340 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 110 340 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} 330 340 0 0 {name=ROSRV value='rout_val'}
C {devices/vsource_np.sym} -2750 340 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -2750 120 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -2750 -100 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -2750 -320 0 0 {name=VCMREF value="dc {vcmfb_ref}"}
C {devices/sg13_lv_pmos_np.sym} -880 -340 0 0 {name=MO1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo1_w l=x_dut_xmo1_l m=x_dut_xmo1_m}
C {devices/sg13_lv_pmos_np.sym} -660 -340 0 0 {name=MO10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo10_w l=x_dut_xmo10_l m=x_dut_xmo10_m}
C {devices/sg13_lv_pmos_np.sym} -440 -340 0 0 {name=MO11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo11_w l=x_dut_xmo11_l m=x_dut_xmo11_m}
C {devices/sg13_lv_pmos_np.sym} -220 -340 0 0 {name=MO12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo12_w l=x_dut_xmo12_l m=x_dut_xmo12_m}
C {devices/sg13_lv_pmos_np.sym} 0 -340 0 0 {name=MO13 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo13_w l=x_dut_xmo13_l m=x_dut_xmo13_m}
C {devices/sg13_lv_pmos_np.sym} 220 -340 0 0 {name=MO14 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo14_w l=x_dut_xmo14_l m=x_dut_xmo14_m}
C {devices/sg13_lv_nmos_np.sym} 550 340 0 0 {name=MO15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo15_w l=x_dut_xmo15_l m=x_dut_xmo15_m}
C {devices/sg13_lv_nmos_np.sym} 770 340 0 0 {name=MO16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo16_w l=x_dut_xmo16_l m=x_dut_xmo16_m}
C {devices/sg13_lv_pmos_np.sym} 440 -340 0 0 {name=MO17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo17_w l=x_dut_xmo17_l m=x_dut_xmo17_m}
C {devices/sg13_lv_pmos_np.sym} 990 340 0 0 {name=MO18 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo18_w l=x_dut_xmo18_l m=x_dut_xmo18_m}
C {devices/sg13_lv_nmos_np.sym} 1210 340 0 0 {name=MO19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo19_w l=x_dut_xmo19_l m=x_dut_xmo19_m}
C {devices/sg13_lv_pmos_np.sym} 660 -340 0 0 {name=MO20 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo20_w l=x_dut_xmo20_l m=x_dut_xmo20_m}
C {devices/sg13_lv_nmos_np.sym} 1430 340 0 0 {name=MO21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo21_w l=x_dut_xmo21_l m=x_dut_xmo21_m}
C {devices/sg13_lv_nmos_np.sym} 1650 340 0 0 {name=MO22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo22_w l=x_dut_xmo22_l m=x_dut_xmo22_m}
C {devices/sg13_lv_pmos_np.sym} 880 -340 0 0 {name=MO23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo23_w l=x_dut_xmo23_l m=x_dut_xmo23_m}
C {devices/sg13_lv_pmos_np.sym} 1870 340 0 0 {name=MO24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo24_w l=x_dut_xmo24_l m=x_dut_xmo24_m}
C {devices/sg13_lv_nmos_np.sym} 2090 340 0 0 {name=MO25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo25_w l=x_dut_xmo25_l m=x_dut_xmo25_m}
C {devices/sg13_lv_nmos_np.sym} 2310 340 0 0 {name=MO7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo7_w l=x_dut_xmo7_l m=x_dut_xmo7_m}
C {devices/sg13_lv_nmos_np.sym} 2530 340 0 0 {name=MO9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo9_w l=x_dut_xmo9_l m=x_dut_xmo9_m}
N -820 -20 -780 -20 {}
C {devices/lab_wire.sym} -780 -20 0 1 {name=l0 lab=dio_p}
N -820 20 -780 20 {}
C {devices/lab_wire.sym} -780 20 0 1 {name=l1 lab=msrc_p}
N -930 80 -930 120 {}
C {devices/lab_wire.sym} -930 120 2 0 {name=l2 lab=vss}
N -380 -20 -340 -20 {}
C {devices/lab_wire.sym} -340 -20 0 1 {name=l3 lab=dio_n}
N -380 20 -340 20 {}
C {devices/lab_wire.sym} -340 20 0 1 {name=l4 lab=msrc_n}
N -490 80 -490 120 {}
C {devices/lab_wire.sym} -490 120 2 0 {name=l5 lab=vss}
N 110 -20 150 -20 {}
C {devices/lab_wire.sym} 150 -20 0 1 {name=l6 lab=sum_p}
N 110 20 150 20 {}
C {devices/lab_wire.sym} 150 20 0 1 {name=l7 lab=voutp}
N 600 -20 640 -20 {}
C {devices/lab_wire.sym} 640 -20 0 1 {name=l8 lab=sum_n}
N 600 20 640 20 {}
C {devices/lab_wire.sym} 640 20 0 1 {name=l9 lab=voutn}
N 820 -20 780 -20 {}
C {devices/lab_wire.sym} 780 -20 0 0 {name=l10 lab=sum_n}
N 820 20 780 20 {}
C {devices/lab_wire.sym} 780 20 0 0 {name=l11 lab=sum_p}
N 1040 -40 1080 -40 {}
C {devices/lab_wire.sym} 1080 -40 0 1 {name=l12 lab=dio_n}
N 1040 0 1080 0 {}
C {devices/lab_wire.sym} 1080 0 0 1 {name=l13 lab=dio_p}
N 1040 40 1080 40 {}
C {devices/lab_wire.sym} 1080 40 0 1 {name=l14 lab=tail}
N 930 -100 930 -140 {}
C {devices/lab_wire.sym} 930 -140 0 1 {name=l15 lab=vdd}
N -2530 310 -2530 270 {}
C {devices/lab_wire.sym} -2530 270 0 1 {name=l16 lab=flt_p}
N -2530 370 -2530 410 {}
C {devices/lab_wire.sym} -2530 410 2 0 {name=l17 lab=zc_p}
N -2310 310 -2310 270 {}
C {devices/lab_wire.sym} -2310 270 0 1 {name=l18 lab=flt_n}
N -2310 370 -2310 410 {}
C {devices/lab_wire.sym} -2310 410 2 0 {name=l19 lab=zc_n}
N -2090 310 -2090 270 {}
C {devices/lab_wire.sym} -2090 270 0 1 {name=l20 lab=sum_p}
N -2090 370 -2090 410 {}
C {devices/lab_wire.sym} -2090 410 2 0 {name=l21 lab=voutp}
N -1870 310 -1870 270 {}
C {devices/lab_wire.sym} -1870 270 0 1 {name=l22 lab=voutn}
N -1870 370 -1870 410 {}
C {devices/lab_wire.sym} -1870 410 2 0 {name=l23 lab=sum_n}
N -1650 310 -1650 270 {}
C {devices/lab_wire.sym} -1650 270 0 1 {name=l24 lab=vinn}
N -1650 370 -1650 410 {}
C {devices/lab_wire.sym} -1650 410 2 0 {name=l25 lab=sum_p}
N -1430 310 -1430 270 {}
C {devices/lab_wire.sym} -1430 270 0 1 {name=l26 lab=vinp}
N -1430 370 -1430 410 {}
C {devices/lab_wire.sym} -1430 410 2 0 {name=l27 lab=sum_n}
N -1210 310 -1210 270 {}
C {devices/lab_wire.sym} -1210 270 0 1 {name=l28 lab=vcm_sense}
N -1210 370 -1210 410 {}
C {devices/lab_wire.sym} -1210 410 2 0 {name=l29 lab=vcmfb_ref}
N -990 310 -990 270 {}
C {devices/lab_wire.sym} -990 270 0 1 {name=l30 lab=vss}
N -990 370 -990 410 {}
C {devices/lab_wire.sym} -990 410 2 0 {name=l31 lab=vcmfb}
N -770 310 -770 270 {}
C {devices/lab_wire.sym} -770 270 0 1 {name=l32 lab=zc_p}
N -770 370 -770 410 {}
C {devices/lab_wire.sym} -770 410 2 0 {name=l33 lab=out1p}
N -550 310 -550 270 {}
C {devices/lab_wire.sym} -550 270 0 1 {name=l34 lab=out1n}
N -550 370 -550 410 {}
C {devices/lab_wire.sym} -550 410 2 0 {name=l35 lab=zc_n}
N -330 310 -330 270 {}
C {devices/lab_wire.sym} -330 270 0 1 {name=l36 lab=vcm_sense}
N -330 370 -330 410 {}
C {devices/lab_wire.sym} -330 410 2 0 {name=l37 lab=vcmfb_ref}
N -110 310 -110 270 {}
C {devices/lab_wire.sym} -110 270 0 1 {name=l38 lab=voutn}
N -110 370 -110 410 {}
C {devices/lab_wire.sym} -110 410 2 0 {name=l39 lab=vcm_sense}
N 110 310 110 270 {}
C {devices/lab_wire.sym} 110 270 0 1 {name=l40 lab=vcm_sense}
N 110 370 110 410 {}
C {devices/lab_wire.sym} 110 410 2 0 {name=l41 lab=voutp}
N 330 310 330 270 {}
C {devices/lab_wire.sym} 330 270 0 1 {name=l42 lab=vcmfb_ref}
N 330 370 330 410 {}
C {devices/lab_wire.sym} 330 410 2 0 {name=l43 lab=vcmfb}
N -2750 310 -2750 270 {}
C {devices/lab_wire.sym} -2750 270 0 1 {name=l44 lab=vb1}
N -2750 370 -2750 410 {}
C {devices/lab_wire.sym} -2750 410 2 0 {name=l45 lab=vss}
N -2750 90 -2750 50 {}
C {devices/lab_wire.sym} -2750 50 0 1 {name=l46 lab=vb2}
N -2750 150 -2750 190 {}
C {devices/lab_wire.sym} -2750 190 2 0 {name=l47 lab=vss}
N -2750 -130 -2750 -170 {}
C {devices/lab_wire.sym} -2750 -170 0 1 {name=l48 lab=vb3}
N -2750 -70 -2750 -30 {}
C {devices/lab_wire.sym} -2750 -30 2 0 {name=l49 lab=vss}
N -2750 -350 -2750 -390 {}
C {devices/lab_wire.sym} -2750 -390 0 1 {name=l50 lab=vcmfb_ref}
N -2750 -290 -2750 -250 {}
C {devices/lab_wire.sym} -2750 -250 2 0 {name=l51 lab=vss}
N -860 -310 -860 -270 {}
C {devices/lab_wire.sym} -860 -270 2 0 {name=l52 lab=tail}
N -900 -340 -940 -340 {}
C {devices/lab_wire.sym} -940 -340 0 0 {name=l53 lab=vb1}
N -860 -370 -860 -410 {}
C {devices/lab_wire.sym} -860 -410 0 1 {name=l54 lab=vdd}
N -860 -340 -820 -340 {}
C {devices/lab_wire.sym} -820 -340 0 1 {name=l55 lab=vdd}
N -640 -310 -640 -270 {}
C {devices/lab_wire.sym} -640 -270 2 0 {name=l56 lab=out1n}
N -680 -340 -720 -340 {}
C {devices/lab_wire.sym} -720 -340 0 0 {name=l57 lab=vb2}
N -640 -370 -640 -410 {}
C {devices/lab_wire.sym} -640 -410 0 1 {name=l58 lab=csrc_n}
N -640 -340 -600 -340 {}
C {devices/lab_wire.sym} -600 -340 0 1 {name=l59 lab=vdd}
N -420 -310 -420 -270 {}
C {devices/lab_wire.sym} -420 -270 2 0 {name=l60 lab=out1p}
N -460 -340 -500 -340 {}
C {devices/lab_wire.sym} -500 -340 0 0 {name=l61 lab=vb2}
N -420 -370 -420 -410 {}
C {devices/lab_wire.sym} -420 -410 0 1 {name=l62 lab=csrc_p}
N -420 -340 -380 -340 {}
C {devices/lab_wire.sym} -380 -340 0 1 {name=l63 lab=vdd}
N -200 -310 -200 -270 {}
C {devices/lab_wire.sym} -200 -270 2 0 {name=l64 lab=csrc_n}
N -240 -340 -280 -340 {}
C {devices/lab_wire.sym} -280 -340 0 0 {name=l65 lab=vcmfb}
N -200 -370 -200 -410 {}
C {devices/lab_wire.sym} -200 -410 0 1 {name=l66 lab=vdd}
N -200 -340 -160 -340 {}
C {devices/lab_wire.sym} -160 -340 0 1 {name=l67 lab=vdd}
N 20 -310 20 -270 {}
C {devices/lab_wire.sym} 20 -270 2 0 {name=l68 lab=csrc_p}
N -20 -340 -60 -340 {}
C {devices/lab_wire.sym} -60 -340 0 0 {name=l69 lab=vcmfb}
N 20 -370 20 -410 {}
C {devices/lab_wire.sym} 20 -410 0 1 {name=l70 lab=vdd}
N 20 -340 60 -340 {}
C {devices/lab_wire.sym} 60 -340 0 1 {name=l71 lab=vdd}
N 240 -310 240 -270 {}
C {devices/lab_wire.sym} 240 -270 2 0 {name=l72 lab=gup_p}
N 200 -340 160 -340 {}
C {devices/lab_wire.sym} 160 -340 0 0 {name=l73 lab=vb1}
N 240 -370 240 -410 {}
C {devices/lab_wire.sym} 240 -410 0 1 {name=l74 lab=vdd}
N 240 -340 280 -340 {}
C {devices/lab_wire.sym} 280 -340 0 1 {name=l75 lab=vdd}
N 570 310 570 270 {}
C {devices/lab_wire.sym} 570 270 0 1 {name=l76 lab=gup_p}
N 530 340 490 340 {}
C {devices/lab_wire.sym} 490 340 0 0 {name=l77 lab=gup_p}
N 570 370 570 410 {}
C {devices/lab_wire.sym} 570 410 2 0 {name=l78 lab=flt_p}
N 570 340 610 340 {}
C {devices/lab_wire.sym} 610 340 0 1 {name=l79 lab=vss}
N 790 310 790 270 {}
C {devices/lab_wire.sym} 790 270 0 1 {name=l80 lab=vdd}
N 750 340 710 340 {}
C {devices/lab_wire.sym} 710 340 0 0 {name=l81 lab=gup_p}
N 790 370 790 410 {}
C {devices/lab_wire.sym} 790 410 2 0 {name=l82 lab=voutp}
N 790 340 830 340 {}
C {devices/lab_wire.sym} 830 340 0 1 {name=l83 lab=vss}
N 460 -310 460 -270 {}
C {devices/lab_wire.sym} 460 -270 2 0 {name=l84 lab=gdn_p}
N 420 -340 380 -340 {}
C {devices/lab_wire.sym} 380 -340 0 0 {name=l85 lab=gdn_p}
N 460 -370 460 -410 {}
C {devices/lab_wire.sym} 460 -410 0 1 {name=l86 lab=flt_p}
N 460 -340 500 -340 {}
C {devices/lab_wire.sym} 500 -340 0 1 {name=l87 lab=vdd}
N 1010 370 1010 410 {}
C {devices/lab_wire.sym} 1010 410 2 0 {name=l88 lab=vss}
N 970 340 930 340 {}
C {devices/lab_wire.sym} 930 340 0 0 {name=l89 lab=gdn_p}
N 1010 310 1010 270 {}
C {devices/lab_wire.sym} 1010 270 0 1 {name=l90 lab=voutp}
N 1010 340 1050 340 {}
C {devices/lab_wire.sym} 1050 340 0 1 {name=l91 lab=vdd}
N 1230 310 1230 270 {}
C {devices/lab_wire.sym} 1230 270 0 1 {name=l92 lab=gdn_p}
N 1190 340 1150 340 {}
C {devices/lab_wire.sym} 1150 340 0 0 {name=l93 lab=out1p}
N 1230 370 1230 410 {}
C {devices/lab_wire.sym} 1230 410 2 0 {name=l94 lab=vss}
N 1230 340 1270 340 {}
C {devices/lab_wire.sym} 1270 340 0 1 {name=l95 lab=vss}
N 680 -310 680 -270 {}
C {devices/lab_wire.sym} 680 -270 2 0 {name=l96 lab=gup_n}
N 640 -340 600 -340 {}
C {devices/lab_wire.sym} 600 -340 0 0 {name=l97 lab=vb1}
N 680 -370 680 -410 {}
C {devices/lab_wire.sym} 680 -410 0 1 {name=l98 lab=vdd}
N 680 -340 720 -340 {}
C {devices/lab_wire.sym} 720 -340 0 1 {name=l99 lab=vdd}
N 1450 310 1450 270 {}
C {devices/lab_wire.sym} 1450 270 0 1 {name=l100 lab=gup_n}
N 1410 340 1370 340 {}
C {devices/lab_wire.sym} 1370 340 0 0 {name=l101 lab=gup_n}
N 1450 370 1450 410 {}
C {devices/lab_wire.sym} 1450 410 2 0 {name=l102 lab=flt_n}
N 1450 340 1490 340 {}
C {devices/lab_wire.sym} 1490 340 0 1 {name=l103 lab=vss}
N 1670 310 1670 270 {}
C {devices/lab_wire.sym} 1670 270 0 1 {name=l104 lab=vdd}
N 1630 340 1590 340 {}
C {devices/lab_wire.sym} 1590 340 0 0 {name=l105 lab=gup_n}
N 1670 370 1670 410 {}
C {devices/lab_wire.sym} 1670 410 2 0 {name=l106 lab=voutn}
N 1670 340 1710 340 {}
C {devices/lab_wire.sym} 1710 340 0 1 {name=l107 lab=vss}
N 900 -310 900 -270 {}
C {devices/lab_wire.sym} 900 -270 2 0 {name=l108 lab=gdn_n}
N 860 -340 820 -340 {}
C {devices/lab_wire.sym} 820 -340 0 0 {name=l109 lab=gdn_n}
N 900 -370 900 -410 {}
C {devices/lab_wire.sym} 900 -410 0 1 {name=l110 lab=flt_n}
N 900 -340 940 -340 {}
C {devices/lab_wire.sym} 940 -340 0 1 {name=l111 lab=vdd}
N 1890 370 1890 410 {}
C {devices/lab_wire.sym} 1890 410 2 0 {name=l112 lab=vss}
N 1850 340 1810 340 {}
C {devices/lab_wire.sym} 1810 340 0 0 {name=l113 lab=gdn_n}
N 1890 310 1890 270 {}
C {devices/lab_wire.sym} 1890 270 0 1 {name=l114 lab=voutn}
N 1890 340 1930 340 {}
C {devices/lab_wire.sym} 1930 340 0 1 {name=l115 lab=vdd}
N 2110 310 2110 270 {}
C {devices/lab_wire.sym} 2110 270 0 1 {name=l116 lab=gdn_n}
N 2070 340 2030 340 {}
C {devices/lab_wire.sym} 2030 340 0 0 {name=l117 lab=out1n}
N 2110 370 2110 410 {}
C {devices/lab_wire.sym} 2110 410 2 0 {name=l118 lab=vss}
N 2110 340 2150 340 {}
C {devices/lab_wire.sym} 2150 340 0 1 {name=l119 lab=vss}
N 2330 310 2330 270 {}
C {devices/lab_wire.sym} 2330 270 0 1 {name=l120 lab=out1n}
N 2290 340 2250 340 {}
C {devices/lab_wire.sym} 2250 340 0 0 {name=l121 lab=vb3}
N 2330 370 2330 410 {}
C {devices/lab_wire.sym} 2330 410 2 0 {name=l122 lab=msrc_n}
N 2330 340 2370 340 {}
C {devices/lab_wire.sym} 2370 340 0 1 {name=l123 lab=vss}
N 2550 310 2550 270 {}
C {devices/lab_wire.sym} 2550 270 0 1 {name=l124 lab=out1p}
N 2510 340 2470 340 {}
C {devices/lab_wire.sym} 2470 340 0 0 {name=l125 lab=vb3}
N 2550 370 2550 410 {}
C {devices/lab_wire.sym} 2550 410 2 0 {name=l126 lab=msrc_p}
N 2550 340 2590 340 {}
C {devices/lab_wire.sym} 2590 340 0 1 {name=l127 lab=vss}
