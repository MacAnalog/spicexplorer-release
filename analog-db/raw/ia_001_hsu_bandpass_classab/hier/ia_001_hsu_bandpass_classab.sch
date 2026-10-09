v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_001_hsu_bandpass_classab} -2900 -540 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -930 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_nmos_simple_2.sym} -490 0 0 0 {name=xcm_nmos_simple_2}
C {blocks/pr_series_shared_well_1.sym} -25 0 0 0 {name=xpr_series_shared_well_1}
C {blocks/pr_series_shared_well_2.sym} 465 0 0 0 {name=xpr_series_shared_well_2}
C {blocks/dp_pmos_simple_1.sym} 930 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -2640 340 0 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} -2420 340 0 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} -2200 340 0 0 {name=CF1 value='x_dut_cf1_value'}
C {devices/capa_np.sym} -1980 340 0 0 {name=CF2 value='x_dut_cf2_value'}
C {devices/capa_np.sym} -1760 340 0 0 {name=CIN1 value='x_dut_cin1_value'}
C {devices/capa_np.sym} -1540 340 0 0 {name=CIN2 value='x_dut_cin2_value'}
C {devices/capa_np.sym} -1320 340 0 0 {name=CISRV value='cin_val'}
C {devices/capa_np.sym} -1100 340 0 0 {name=COSRV value='cout_val'}
C {devices/vccs.sym} -880 340 0 0 {name=GSRV value="\{gm_val\}"}
C {devices/res_np.sym} -660 340 0 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} -440 340 0 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} -220 340 0 0 {name=RISRV value='rin_val'}
C {devices/res_np.sym} 0 340 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 220 340 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} 440 340 0 0 {name=ROSRV value='rout_val'}
C {devices/vsource_np.sym} -2860 340 0 0 {name=VB1 value="dc \{vb1\}" savecurrent=false}
C {devices/vsource_np.sym} -2860 120 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -2860 -100 0 0 {name=VB3 value="dc \{vb3\}" savecurrent=false}
C {devices/vsource_np.sym} -2860 -320 0 0 {name=VCMREF value="dc \{vcmfb_ref\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} -880 -340 0 0 {name=MO1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo1_w l=x_dut_xmo1_l m=x_dut_xmo1_m}
C {devices/sg13_lv_pmos_np.sym} -660 -340 0 0 {name=MO10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo10_w l=x_dut_xmo10_l m=x_dut_xmo10_m}
C {devices/sg13_lv_pmos_np.sym} -440 -340 0 0 {name=MO11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo11_w l=x_dut_xmo11_l m=x_dut_xmo11_m}
C {devices/sg13_lv_pmos_np.sym} -220 -340 0 0 {name=MO12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo12_w l=x_dut_xmo12_l m=x_dut_xmo12_m}
C {devices/sg13_lv_pmos_np.sym} 0 -340 0 0 {name=MO13 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo13_w l=x_dut_xmo13_l m=x_dut_xmo13_m}
C {devices/sg13_lv_pmos_np.sym} 220 -340 0 0 {name=MO14 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo14_w l=x_dut_xmo14_l m=x_dut_xmo14_m}
C {devices/sg13_lv_nmos_np.sym} 660 340 0 0 {name=MO15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo15_w l=x_dut_xmo15_l m=x_dut_xmo15_m}
C {devices/sg13_lv_nmos_np.sym} 880 340 0 0 {name=MO16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo16_w l=x_dut_xmo16_l m=x_dut_xmo16_m}
C {devices/sg13_lv_pmos_np.sym} 440 -340 0 0 {name=MO17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo17_w l=x_dut_xmo17_l m=x_dut_xmo17_m}
C {devices/sg13_lv_pmos_np.sym} 1100 340 0 0 {name=MO18 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo18_w l=x_dut_xmo18_l m=x_dut_xmo18_m}
C {devices/sg13_lv_nmos_np.sym} 1320 340 0 0 {name=MO19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo19_w l=x_dut_xmo19_l m=x_dut_xmo19_m}
C {devices/sg13_lv_pmos_np.sym} 660 -340 0 0 {name=MO20 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo20_w l=x_dut_xmo20_l m=x_dut_xmo20_m}
C {devices/sg13_lv_nmos_np.sym} 1540 340 0 0 {name=MO21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo21_w l=x_dut_xmo21_l m=x_dut_xmo21_m}
C {devices/sg13_lv_nmos_np.sym} 1760 340 0 0 {name=MO22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo22_w l=x_dut_xmo22_l m=x_dut_xmo22_m}
C {devices/sg13_lv_pmos_np.sym} 880 -340 0 0 {name=MO23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo23_w l=x_dut_xmo23_l m=x_dut_xmo23_m}
C {devices/sg13_lv_pmos_np.sym} 1980 340 0 0 {name=MO24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo24_w l=x_dut_xmo24_l m=x_dut_xmo24_m}
C {devices/sg13_lv_nmos_np.sym} 2200 340 0 0 {name=MO25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo25_w l=x_dut_xmo25_l m=x_dut_xmo25_m}
C {devices/sg13_lv_nmos_np.sym} 2420 340 0 0 {name=MO7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo7_w l=x_dut_xmo7_l m=x_dut_xmo7_m}
C {devices/sg13_lv_nmos_np.sym} 2640 340 0 0 {name=MO9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo9_w l=x_dut_xmo9_l m=x_dut_xmo9_m}
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
N -2640 310 -2640 270 {}
C {devices/lab_wire.sym} -2640 270 0 1 {name=l16 lab=flt_p}
N -2640 370 -2640 410 {}
C {devices/lab_wire.sym} -2640 410 2 0 {name=l17 lab=zc_p}
N -2420 310 -2420 270 {}
C {devices/lab_wire.sym} -2420 270 0 1 {name=l18 lab=flt_n}
N -2420 370 -2420 410 {}
C {devices/lab_wire.sym} -2420 410 2 0 {name=l19 lab=zc_n}
N -2200 310 -2200 270 {}
C {devices/lab_wire.sym} -2200 270 0 1 {name=l20 lab=sum_p}
N -2200 370 -2200 410 {}
C {devices/lab_wire.sym} -2200 410 2 0 {name=l21 lab=voutp}
N -1980 310 -1980 270 {}
C {devices/lab_wire.sym} -1980 270 0 1 {name=l22 lab=voutn}
N -1980 370 -1980 410 {}
C {devices/lab_wire.sym} -1980 410 2 0 {name=l23 lab=sum_n}
N -1760 310 -1760 270 {}
C {devices/lab_wire.sym} -1760 270 0 1 {name=l24 lab=vinn}
N -1760 370 -1760 410 {}
C {devices/lab_wire.sym} -1760 410 2 0 {name=l25 lab=sum_p}
N -1540 310 -1540 270 {}
C {devices/lab_wire.sym} -1540 270 0 1 {name=l26 lab=vinp}
N -1540 370 -1540 410 {}
C {devices/lab_wire.sym} -1540 410 2 0 {name=l27 lab=sum_n}
N -1320 310 -1320 270 {}
C {devices/lab_wire.sym} -1320 270 0 1 {name=l28 lab=vcm_sense}
N -1320 370 -1320 410 {}
C {devices/lab_wire.sym} -1320 410 2 0 {name=l29 lab=vcmfb_ref}
N -1100 310 -1100 270 {}
C {devices/lab_wire.sym} -1100 270 0 1 {name=l30 lab=vss}
N -1100 370 -1100 410 {}
C {devices/lab_wire.sym} -1100 410 2 0 {name=l31 lab=vcmfb}
N -880 310 -880 270 {}
C {devices/lab_wire.sym} -880 270 0 1 {name=l32 lab=vss}
N -880 370 -880 410 {}
C {devices/lab_wire.sym} -880 410 2 0 {name=l33 lab=vcmfb}
N -920 320 -960 320 {}
C {devices/lab_wire.sym} -960 320 0 0 {name=l34 lab=vcmfb_ref}
N -920 360 -960 360 {}
C {devices/lab_wire.sym} -960 360 0 0 {name=l35 lab=vcm_sense}
N -660 310 -660 270 {}
C {devices/lab_wire.sym} -660 270 0 1 {name=l36 lab=zc_p}
N -660 370 -660 410 {}
C {devices/lab_wire.sym} -660 410 2 0 {name=l37 lab=out1p}
N -440 310 -440 270 {}
C {devices/lab_wire.sym} -440 270 0 1 {name=l38 lab=out1n}
N -440 370 -440 410 {}
C {devices/lab_wire.sym} -440 410 2 0 {name=l39 lab=zc_n}
N -220 310 -220 270 {}
C {devices/lab_wire.sym} -220 270 0 1 {name=l40 lab=vcm_sense}
N -220 370 -220 410 {}
C {devices/lab_wire.sym} -220 410 2 0 {name=l41 lab=vcmfb_ref}
N 0 310 0 270 {}
C {devices/lab_wire.sym} 0 270 0 1 {name=l42 lab=voutn}
N 0 370 0 410 {}
C {devices/lab_wire.sym} 0 410 2 0 {name=l43 lab=vcm_sense}
N 220 310 220 270 {}
C {devices/lab_wire.sym} 220 270 0 1 {name=l44 lab=vcm_sense}
N 220 370 220 410 {}
C {devices/lab_wire.sym} 220 410 2 0 {name=l45 lab=voutp}
N 440 310 440 270 {}
C {devices/lab_wire.sym} 440 270 0 1 {name=l46 lab=vcmfb_ref}
N 440 370 440 410 {}
C {devices/lab_wire.sym} 440 410 2 0 {name=l47 lab=vcmfb}
N -2860 310 -2860 270 {}
C {devices/lab_wire.sym} -2860 270 0 1 {name=l48 lab=vb1}
N -2860 370 -2860 410 {}
C {devices/lab_wire.sym} -2860 410 2 0 {name=l49 lab=vss}
N -2860 90 -2860 50 {}
C {devices/lab_wire.sym} -2860 50 0 1 {name=l50 lab=vb2}
N -2860 150 -2860 190 {}
C {devices/lab_wire.sym} -2860 190 2 0 {name=l51 lab=vss}
N -2860 -130 -2860 -170 {}
C {devices/lab_wire.sym} -2860 -170 0 1 {name=l52 lab=vb3}
N -2860 -70 -2860 -30 {}
C {devices/lab_wire.sym} -2860 -30 2 0 {name=l53 lab=vss}
N -2860 -350 -2860 -390 {}
C {devices/lab_wire.sym} -2860 -390 0 1 {name=l54 lab=vcmfb_ref}
N -2860 -290 -2860 -250 {}
C {devices/lab_wire.sym} -2860 -250 2 0 {name=l55 lab=vss}
N -860 -310 -860 -270 {}
C {devices/lab_wire.sym} -860 -270 2 0 {name=l56 lab=tail}
N -900 -340 -940 -340 {}
C {devices/lab_wire.sym} -940 -340 0 0 {name=l57 lab=vb1}
N -860 -370 -860 -410 {}
C {devices/lab_wire.sym} -860 -410 0 1 {name=l58 lab=vdd}
N -860 -340 -820 -340 {}
C {devices/lab_wire.sym} -820 -340 0 1 {name=l59 lab=vdd}
N -640 -310 -640 -270 {}
C {devices/lab_wire.sym} -640 -270 2 0 {name=l60 lab=out1n}
N -680 -340 -720 -340 {}
C {devices/lab_wire.sym} -720 -340 0 0 {name=l61 lab=vb2}
N -640 -370 -640 -410 {}
C {devices/lab_wire.sym} -640 -410 0 1 {name=l62 lab=csrc_n}
N -640 -340 -600 -340 {}
C {devices/lab_wire.sym} -600 -340 0 1 {name=l63 lab=vdd}
N -420 -310 -420 -270 {}
C {devices/lab_wire.sym} -420 -270 2 0 {name=l64 lab=out1p}
N -460 -340 -500 -340 {}
C {devices/lab_wire.sym} -500 -340 0 0 {name=l65 lab=vb2}
N -420 -370 -420 -410 {}
C {devices/lab_wire.sym} -420 -410 0 1 {name=l66 lab=csrc_p}
N -420 -340 -380 -340 {}
C {devices/lab_wire.sym} -380 -340 0 1 {name=l67 lab=vdd}
N -200 -310 -200 -270 {}
C {devices/lab_wire.sym} -200 -270 2 0 {name=l68 lab=csrc_n}
N -240 -340 -280 -340 {}
C {devices/lab_wire.sym} -280 -340 0 0 {name=l69 lab=vcmfb}
N -200 -370 -200 -410 {}
C {devices/lab_wire.sym} -200 -410 0 1 {name=l70 lab=vdd}
N -200 -340 -160 -340 {}
C {devices/lab_wire.sym} -160 -340 0 1 {name=l71 lab=vdd}
N 20 -310 20 -270 {}
C {devices/lab_wire.sym} 20 -270 2 0 {name=l72 lab=csrc_p}
N -20 -340 -60 -340 {}
C {devices/lab_wire.sym} -60 -340 0 0 {name=l73 lab=vcmfb}
N 20 -370 20 -410 {}
C {devices/lab_wire.sym} 20 -410 0 1 {name=l74 lab=vdd}
N 20 -340 60 -340 {}
C {devices/lab_wire.sym} 60 -340 0 1 {name=l75 lab=vdd}
N 240 -310 240 -270 {}
C {devices/lab_wire.sym} 240 -270 2 0 {name=l76 lab=gup_p}
N 200 -340 160 -340 {}
C {devices/lab_wire.sym} 160 -340 0 0 {name=l77 lab=vb1}
N 240 -370 240 -410 {}
C {devices/lab_wire.sym} 240 -410 0 1 {name=l78 lab=vdd}
N 240 -340 280 -340 {}
C {devices/lab_wire.sym} 280 -340 0 1 {name=l79 lab=vdd}
N 680 310 680 270 {}
C {devices/lab_wire.sym} 680 270 0 1 {name=l80 lab=gup_p}
N 640 340 600 340 {}
C {devices/lab_wire.sym} 600 340 0 0 {name=l81 lab=gup_p}
N 680 370 680 410 {}
C {devices/lab_wire.sym} 680 410 2 0 {name=l82 lab=flt_p}
N 680 340 720 340 {}
C {devices/lab_wire.sym} 720 340 0 1 {name=l83 lab=vss}
N 900 310 900 270 {}
C {devices/lab_wire.sym} 900 270 0 1 {name=l84 lab=vdd}
N 860 340 820 340 {}
C {devices/lab_wire.sym} 820 340 0 0 {name=l85 lab=gup_p}
N 900 370 900 410 {}
C {devices/lab_wire.sym} 900 410 2 0 {name=l86 lab=voutp}
N 900 340 940 340 {}
C {devices/lab_wire.sym} 940 340 0 1 {name=l87 lab=vss}
N 460 -310 460 -270 {}
C {devices/lab_wire.sym} 460 -270 2 0 {name=l88 lab=gdn_p}
N 420 -340 380 -340 {}
C {devices/lab_wire.sym} 380 -340 0 0 {name=l89 lab=gdn_p}
N 460 -370 460 -410 {}
C {devices/lab_wire.sym} 460 -410 0 1 {name=l90 lab=flt_p}
N 460 -340 500 -340 {}
C {devices/lab_wire.sym} 500 -340 0 1 {name=l91 lab=vdd}
N 1120 370 1120 410 {}
C {devices/lab_wire.sym} 1120 410 2 0 {name=l92 lab=vss}
N 1080 340 1040 340 {}
C {devices/lab_wire.sym} 1040 340 0 0 {name=l93 lab=gdn_p}
N 1120 310 1120 270 {}
C {devices/lab_wire.sym} 1120 270 0 1 {name=l94 lab=voutp}
N 1120 340 1160 340 {}
C {devices/lab_wire.sym} 1160 340 0 1 {name=l95 lab=vdd}
N 1340 310 1340 270 {}
C {devices/lab_wire.sym} 1340 270 0 1 {name=l96 lab=gdn_p}
N 1300 340 1260 340 {}
C {devices/lab_wire.sym} 1260 340 0 0 {name=l97 lab=out1p}
N 1340 370 1340 410 {}
C {devices/lab_wire.sym} 1340 410 2 0 {name=l98 lab=vss}
N 1340 340 1380 340 {}
C {devices/lab_wire.sym} 1380 340 0 1 {name=l99 lab=vss}
N 680 -310 680 -270 {}
C {devices/lab_wire.sym} 680 -270 2 0 {name=l100 lab=gup_n}
N 640 -340 600 -340 {}
C {devices/lab_wire.sym} 600 -340 0 0 {name=l101 lab=vb1}
N 680 -370 680 -410 {}
C {devices/lab_wire.sym} 680 -410 0 1 {name=l102 lab=vdd}
N 680 -340 720 -340 {}
C {devices/lab_wire.sym} 720 -340 0 1 {name=l103 lab=vdd}
N 1560 310 1560 270 {}
C {devices/lab_wire.sym} 1560 270 0 1 {name=l104 lab=gup_n}
N 1520 340 1480 340 {}
C {devices/lab_wire.sym} 1480 340 0 0 {name=l105 lab=gup_n}
N 1560 370 1560 410 {}
C {devices/lab_wire.sym} 1560 410 2 0 {name=l106 lab=flt_n}
N 1560 340 1600 340 {}
C {devices/lab_wire.sym} 1600 340 0 1 {name=l107 lab=vss}
N 1780 310 1780 270 {}
C {devices/lab_wire.sym} 1780 270 0 1 {name=l108 lab=vdd}
N 1740 340 1700 340 {}
C {devices/lab_wire.sym} 1700 340 0 0 {name=l109 lab=gup_n}
N 1780 370 1780 410 {}
C {devices/lab_wire.sym} 1780 410 2 0 {name=l110 lab=voutn}
N 1780 340 1820 340 {}
C {devices/lab_wire.sym} 1820 340 0 1 {name=l111 lab=vss}
N 900 -310 900 -270 {}
C {devices/lab_wire.sym} 900 -270 2 0 {name=l112 lab=gdn_n}
N 860 -340 820 -340 {}
C {devices/lab_wire.sym} 820 -340 0 0 {name=l113 lab=gdn_n}
N 900 -370 900 -410 {}
C {devices/lab_wire.sym} 900 -410 0 1 {name=l114 lab=flt_n}
N 900 -340 940 -340 {}
C {devices/lab_wire.sym} 940 -340 0 1 {name=l115 lab=vdd}
N 2000 370 2000 410 {}
C {devices/lab_wire.sym} 2000 410 2 0 {name=l116 lab=vss}
N 1960 340 1920 340 {}
C {devices/lab_wire.sym} 1920 340 0 0 {name=l117 lab=gdn_n}
N 2000 310 2000 270 {}
C {devices/lab_wire.sym} 2000 270 0 1 {name=l118 lab=voutn}
N 2000 340 2040 340 {}
C {devices/lab_wire.sym} 2040 340 0 1 {name=l119 lab=vdd}
N 2220 310 2220 270 {}
C {devices/lab_wire.sym} 2220 270 0 1 {name=l120 lab=gdn_n}
N 2180 340 2140 340 {}
C {devices/lab_wire.sym} 2140 340 0 0 {name=l121 lab=out1n}
N 2220 370 2220 410 {}
C {devices/lab_wire.sym} 2220 410 2 0 {name=l122 lab=vss}
N 2220 340 2260 340 {}
C {devices/lab_wire.sym} 2260 340 0 1 {name=l123 lab=vss}
N 2440 310 2440 270 {}
C {devices/lab_wire.sym} 2440 270 0 1 {name=l124 lab=out1n}
N 2400 340 2360 340 {}
C {devices/lab_wire.sym} 2360 340 0 0 {name=l125 lab=vb3}
N 2440 370 2440 410 {}
C {devices/lab_wire.sym} 2440 410 2 0 {name=l126 lab=msrc_n}
N 2440 340 2480 340 {}
C {devices/lab_wire.sym} 2480 340 0 1 {name=l127 lab=vss}
N 2660 310 2660 270 {}
C {devices/lab_wire.sym} 2660 270 0 1 {name=l128 lab=out1p}
N 2620 340 2580 340 {}
C {devices/lab_wire.sym} 2580 340 0 0 {name=l129 lab=vb3}
N 2660 370 2660 410 {}
C {devices/lab_wire.sym} 2660 410 2 0 {name=l130 lab=msrc_p}
N 2660 340 2700 340 {}
C {devices/lab_wire.sym} 2700 340 0 1 {name=l131 lab=vss}
