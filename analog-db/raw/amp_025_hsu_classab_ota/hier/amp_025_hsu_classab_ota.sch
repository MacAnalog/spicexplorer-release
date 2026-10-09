v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_025_hsu_classab_ota} -2460 -540 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -440 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_nmos_simple_2.sym} 0 0 0 0 {name=xcm_nmos_simple_2}
C {blocks/dp_pmos_simple_1.sym} 440 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -2200 340 0 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} -1980 340 0 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} -1760 340 0 0 {name=CIN value='cin_val'}
C {devices/capa_np.sym} -1540 340 0 0 {name=COUT value='cout_val'}
C {devices/vccs.sym} -1320 340 0 0 {name=GM value="\{gm_val\}"}
C {devices/res_np.sym} -1100 340 0 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} -880 340 0 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} -660 340 0 0 {name=RIN value='rin_val'}
C {devices/res_np.sym} -440 340 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} -220 340 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} 0 340 0 0 {name=ROUT value='rout_val'}
C {devices/vsource_np.sym} -2420 340 0 0 {name=VB1 value="dc \{vb1\}" savecurrent=false}
C {devices/vsource_np.sym} -2420 120 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -2420 -100 0 0 {name=VB3 value="dc \{vb3\}" savecurrent=false}
C {devices/vsource_np.sym} -2420 -320 0 0 {name=VCMFB_REF value="dc \{vcmfb_ref\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} -880 -340 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -660 -340 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} -440 -340 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} -220 -340 0 0 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_pmos_np.sym} 0 -340 0 0 {name=M13 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_pmos_np.sym} 220 -340 0 0 {name=M14 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 220 340 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 440 340 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} 440 -340 0 0 {name=M17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_pmos_np.sym} 660 340 0 0 {name=M18 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 880 340 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} 660 -340 0 0 {name=M20 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 1100 340 0 0 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 1320 340 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} 880 -340 0 0 {name=M23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_pmos_np.sym} 1540 340 0 0 {name=M24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_nmos_np.sym} 1760 340 0 0 {name=M25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
C {devices/sg13_lv_nmos_np.sym} 1980 340 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_nmos_np.sym} 2200 340 0 0 {name=M9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -330 -20 -290 -20 {}
C {devices/lab_wire.sym} -290 -20 0 1 {name=l0 lab=csrc_p}
N -330 20 -290 20 {}
C {devices/lab_wire.sym} -290 20 0 1 {name=l1 lab=mir_p}
N -440 80 -440 120 {}
C {devices/lab_wire.sym} -440 120 2 0 {name=l2 lab=vss}
N 110 -20 150 -20 {}
C {devices/lab_wire.sym} 150 -20 0 1 {name=l3 lab=csrc_n}
N 110 20 150 20 {}
C {devices/lab_wire.sym} 150 20 0 1 {name=l4 lab=mir_n}
N 0 80 0 120 {}
C {devices/lab_wire.sym} 0 120 2 0 {name=l5 lab=vss}
N 330 -20 290 -20 {}
C {devices/lab_wire.sym} 290 -20 0 0 {name=l6 lab=vinn}
N 330 20 290 20 {}
C {devices/lab_wire.sym} 290 20 0 0 {name=l7 lab=vinp}
N 550 -40 590 -40 {}
C {devices/lab_wire.sym} 590 -40 0 1 {name=l8 lab=mir_n}
N 550 0 590 0 {}
C {devices/lab_wire.sym} 590 0 0 1 {name=l9 lab=mir_p}
N 550 40 590 40 {}
C {devices/lab_wire.sym} 590 40 0 1 {name=l10 lab=tail}
N 440 -100 440 -140 {}
C {devices/lab_wire.sym} 440 -140 0 1 {name=l11 lab=vdd}
N -2200 310 -2200 270 {}
C {devices/lab_wire.sym} -2200 270 0 1 {name=l12 lab=abm_p}
N -2200 370 -2200 410 {}
C {devices/lab_wire.sym} -2200 410 2 0 {name=l13 lab=zc_p}
N -1980 310 -1980 270 {}
C {devices/lab_wire.sym} -1980 270 0 1 {name=l14 lab=abm_n}
N -1980 370 -1980 410 {}
C {devices/lab_wire.sym} -1980 410 2 0 {name=l15 lab=zc_n}
N -1760 310 -1760 270 {}
C {devices/lab_wire.sym} -1760 270 0 1 {name=l16 lab=cm_det}
N -1760 370 -1760 410 {}
C {devices/lab_wire.sym} -1760 410 2 0 {name=l17 lab=vcmfb_ref}
N -1540 310 -1540 270 {}
C {devices/lab_wire.sym} -1540 270 0 1 {name=l18 lab=vss}
N -1540 370 -1540 410 {}
C {devices/lab_wire.sym} -1540 410 2 0 {name=l19 lab=vcmfb}
N -1320 310 -1320 270 {}
C {devices/lab_wire.sym} -1320 270 0 1 {name=l20 lab=vss}
N -1320 370 -1320 410 {}
C {devices/lab_wire.sym} -1320 410 2 0 {name=l21 lab=vcmfb}
N -1360 320 -1400 320 {}
C {devices/lab_wire.sym} -1400 320 0 0 {name=l22 lab=vcmfb_ref}
N -1360 360 -1400 360 {}
C {devices/lab_wire.sym} -1400 360 0 0 {name=l23 lab=cm_det}
N -1100 310 -1100 270 {}
C {devices/lab_wire.sym} -1100 270 0 1 {name=l24 lab=zc_p}
N -1100 370 -1100 410 {}
C {devices/lab_wire.sym} -1100 410 2 0 {name=l25 lab=drv_p}
N -880 310 -880 270 {}
C {devices/lab_wire.sym} -880 270 0 1 {name=l26 lab=drv_n}
N -880 370 -880 410 {}
C {devices/lab_wire.sym} -880 410 2 0 {name=l27 lab=zc_n}
N -660 310 -660 270 {}
C {devices/lab_wire.sym} -660 270 0 1 {name=l28 lab=cm_det}
N -660 370 -660 410 {}
C {devices/lab_wire.sym} -660 410 2 0 {name=l29 lab=vcmfb_ref}
N -440 310 -440 270 {}
C {devices/lab_wire.sym} -440 270 0 1 {name=l30 lab=voutn}
N -440 370 -440 410 {}
C {devices/lab_wire.sym} -440 410 2 0 {name=l31 lab=cm_det}
N -220 310 -220 270 {}
C {devices/lab_wire.sym} -220 270 0 1 {name=l32 lab=cm_det}
N -220 370 -220 410 {}
C {devices/lab_wire.sym} -220 410 2 0 {name=l33 lab=voutp}
N 0 310 0 270 {}
C {devices/lab_wire.sym} 0 270 0 1 {name=l34 lab=vss}
N 0 370 0 410 {}
C {devices/lab_wire.sym} 0 410 2 0 {name=l35 lab=vcmfb}
N -2420 310 -2420 270 {}
C {devices/lab_wire.sym} -2420 270 0 1 {name=l36 lab=vb1}
N -2420 370 -2420 410 {}
C {devices/lab_wire.sym} -2420 410 2 0 {name=l37 lab=vss}
N -2420 90 -2420 50 {}
C {devices/lab_wire.sym} -2420 50 0 1 {name=l38 lab=vb2}
N -2420 150 -2420 190 {}
C {devices/lab_wire.sym} -2420 190 2 0 {name=l39 lab=vss}
N -2420 -130 -2420 -170 {}
C {devices/lab_wire.sym} -2420 -170 0 1 {name=l40 lab=vb3}
N -2420 -70 -2420 -30 {}
C {devices/lab_wire.sym} -2420 -30 2 0 {name=l41 lab=vss}
N -2420 -350 -2420 -390 {}
C {devices/lab_wire.sym} -2420 -390 0 1 {name=l42 lab=vcmfb_ref}
N -2420 -290 -2420 -250 {}
C {devices/lab_wire.sym} -2420 -250 2 0 {name=l43 lab=vss}
N -860 -310 -860 -270 {}
C {devices/lab_wire.sym} -860 -270 2 0 {name=l44 lab=tail}
N -900 -340 -940 -340 {}
C {devices/lab_wire.sym} -940 -340 0 0 {name=l45 lab=vb1}
N -860 -370 -860 -410 {}
C {devices/lab_wire.sym} -860 -410 0 1 {name=l46 lab=vdd}
N -860 -340 -820 -340 {}
C {devices/lab_wire.sym} -820 -340 0 1 {name=l47 lab=vdd}
N -640 -310 -640 -270 {}
C {devices/lab_wire.sym} -640 -270 2 0 {name=l48 lab=drv_n}
N -680 -340 -720 -340 {}
C {devices/lab_wire.sym} -720 -340 0 0 {name=l49 lab=vb2}
N -640 -370 -640 -410 {}
C {devices/lab_wire.sym} -640 -410 0 1 {name=l50 lab=psrc_n}
N -640 -340 -600 -340 {}
C {devices/lab_wire.sym} -600 -340 0 1 {name=l51 lab=vdd}
N -420 -310 -420 -270 {}
C {devices/lab_wire.sym} -420 -270 2 0 {name=l52 lab=drv_p}
N -460 -340 -500 -340 {}
C {devices/lab_wire.sym} -500 -340 0 0 {name=l53 lab=vb2}
N -420 -370 -420 -410 {}
C {devices/lab_wire.sym} -420 -410 0 1 {name=l54 lab=psrc_p}
N -420 -340 -380 -340 {}
C {devices/lab_wire.sym} -380 -340 0 1 {name=l55 lab=vdd}
N -200 -310 -200 -270 {}
C {devices/lab_wire.sym} -200 -270 2 0 {name=l56 lab=psrc_n}
N -240 -340 -280 -340 {}
C {devices/lab_wire.sym} -280 -340 0 0 {name=l57 lab=vcmfb}
N -200 -370 -200 -410 {}
C {devices/lab_wire.sym} -200 -410 0 1 {name=l58 lab=vdd}
N -200 -340 -160 -340 {}
C {devices/lab_wire.sym} -160 -340 0 1 {name=l59 lab=vdd}
N 20 -310 20 -270 {}
C {devices/lab_wire.sym} 20 -270 2 0 {name=l60 lab=psrc_p}
N -20 -340 -60 -340 {}
C {devices/lab_wire.sym} -60 -340 0 0 {name=l61 lab=vcmfb}
N 20 -370 20 -410 {}
C {devices/lab_wire.sym} 20 -410 0 1 {name=l62 lab=vdd}
N 20 -340 60 -340 {}
C {devices/lab_wire.sym} 60 -340 0 1 {name=l63 lab=vdd}
N 240 -310 240 -270 {}
C {devices/lab_wire.sym} 240 -270 2 0 {name=l64 lab=gnf_p}
N 200 -340 160 -340 {}
C {devices/lab_wire.sym} 160 -340 0 0 {name=l65 lab=vb1}
N 240 -370 240 -410 {}
C {devices/lab_wire.sym} 240 -410 0 1 {name=l66 lab=vdd}
N 240 -340 280 -340 {}
C {devices/lab_wire.sym} 280 -340 0 1 {name=l67 lab=vdd}
N 240 310 240 270 {}
C {devices/lab_wire.sym} 240 270 0 1 {name=l68 lab=gnf_p}
N 200 340 160 340 {}
C {devices/lab_wire.sym} 160 340 0 0 {name=l69 lab=gnf_p}
N 240 370 240 410 {}
C {devices/lab_wire.sym} 240 410 2 0 {name=l70 lab=abm_p}
N 240 340 280 340 {}
C {devices/lab_wire.sym} 280 340 0 1 {name=l71 lab=vss}
N 460 310 460 270 {}
C {devices/lab_wire.sym} 460 270 0 1 {name=l72 lab=vdd}
N 420 340 380 340 {}
C {devices/lab_wire.sym} 380 340 0 0 {name=l73 lab=gnf_p}
N 460 370 460 410 {}
C {devices/lab_wire.sym} 460 410 2 0 {name=l74 lab=voutp}
N 460 340 500 340 {}
C {devices/lab_wire.sym} 500 340 0 1 {name=l75 lab=vss}
N 460 -310 460 -270 {}
C {devices/lab_wire.sym} 460 -270 2 0 {name=l76 lab=gpf_p}
N 420 -340 380 -340 {}
C {devices/lab_wire.sym} 380 -340 0 0 {name=l77 lab=gpf_p}
N 460 -370 460 -410 {}
C {devices/lab_wire.sym} 460 -410 0 1 {name=l78 lab=abm_p}
N 460 -340 500 -340 {}
C {devices/lab_wire.sym} 500 -340 0 1 {name=l79 lab=vdd}
N 680 370 680 410 {}
C {devices/lab_wire.sym} 680 410 2 0 {name=l80 lab=vss}
N 640 340 600 340 {}
C {devices/lab_wire.sym} 600 340 0 0 {name=l81 lab=gpf_p}
N 680 310 680 270 {}
C {devices/lab_wire.sym} 680 270 0 1 {name=l82 lab=voutp}
N 680 340 720 340 {}
C {devices/lab_wire.sym} 720 340 0 1 {name=l83 lab=vdd}
N 900 310 900 270 {}
C {devices/lab_wire.sym} 900 270 0 1 {name=l84 lab=gpf_p}
N 860 340 820 340 {}
C {devices/lab_wire.sym} 820 340 0 0 {name=l85 lab=drv_p}
N 900 370 900 410 {}
C {devices/lab_wire.sym} 900 410 2 0 {name=l86 lab=vss}
N 900 340 940 340 {}
C {devices/lab_wire.sym} 940 340 0 1 {name=l87 lab=vss}
N 680 -310 680 -270 {}
C {devices/lab_wire.sym} 680 -270 2 0 {name=l88 lab=gnf_n}
N 640 -340 600 -340 {}
C {devices/lab_wire.sym} 600 -340 0 0 {name=l89 lab=vb1}
N 680 -370 680 -410 {}
C {devices/lab_wire.sym} 680 -410 0 1 {name=l90 lab=vdd}
N 680 -340 720 -340 {}
C {devices/lab_wire.sym} 720 -340 0 1 {name=l91 lab=vdd}
N 1120 310 1120 270 {}
C {devices/lab_wire.sym} 1120 270 0 1 {name=l92 lab=gnf_n}
N 1080 340 1040 340 {}
C {devices/lab_wire.sym} 1040 340 0 0 {name=l93 lab=gnf_n}
N 1120 370 1120 410 {}
C {devices/lab_wire.sym} 1120 410 2 0 {name=l94 lab=abm_n}
N 1120 340 1160 340 {}
C {devices/lab_wire.sym} 1160 340 0 1 {name=l95 lab=vss}
N 1340 310 1340 270 {}
C {devices/lab_wire.sym} 1340 270 0 1 {name=l96 lab=vdd}
N 1300 340 1260 340 {}
C {devices/lab_wire.sym} 1260 340 0 0 {name=l97 lab=gnf_n}
N 1340 370 1340 410 {}
C {devices/lab_wire.sym} 1340 410 2 0 {name=l98 lab=voutn}
N 1340 340 1380 340 {}
C {devices/lab_wire.sym} 1380 340 0 1 {name=l99 lab=vss}
N 900 -310 900 -270 {}
C {devices/lab_wire.sym} 900 -270 2 0 {name=l100 lab=gpf_n}
N 860 -340 820 -340 {}
C {devices/lab_wire.sym} 820 -340 0 0 {name=l101 lab=gpf_n}
N 900 -370 900 -410 {}
C {devices/lab_wire.sym} 900 -410 0 1 {name=l102 lab=abm_n}
N 900 -340 940 -340 {}
C {devices/lab_wire.sym} 940 -340 0 1 {name=l103 lab=vdd}
N 1560 370 1560 410 {}
C {devices/lab_wire.sym} 1560 410 2 0 {name=l104 lab=vss}
N 1520 340 1480 340 {}
C {devices/lab_wire.sym} 1480 340 0 0 {name=l105 lab=gpf_n}
N 1560 310 1560 270 {}
C {devices/lab_wire.sym} 1560 270 0 1 {name=l106 lab=voutn}
N 1560 340 1600 340 {}
C {devices/lab_wire.sym} 1600 340 0 1 {name=l107 lab=vdd}
N 1780 310 1780 270 {}
C {devices/lab_wire.sym} 1780 270 0 1 {name=l108 lab=gpf_n}
N 1740 340 1700 340 {}
C {devices/lab_wire.sym} 1700 340 0 0 {name=l109 lab=drv_n}
N 1780 370 1780 410 {}
C {devices/lab_wire.sym} 1780 410 2 0 {name=l110 lab=vss}
N 1780 340 1820 340 {}
C {devices/lab_wire.sym} 1820 340 0 1 {name=l111 lab=vss}
N 2000 310 2000 270 {}
C {devices/lab_wire.sym} 2000 270 0 1 {name=l112 lab=drv_n}
N 1960 340 1920 340 {}
C {devices/lab_wire.sym} 1920 340 0 0 {name=l113 lab=vb3}
N 2000 370 2000 410 {}
C {devices/lab_wire.sym} 2000 410 2 0 {name=l114 lab=csrc_n}
N 2000 340 2040 340 {}
C {devices/lab_wire.sym} 2040 340 0 1 {name=l115 lab=vss}
N 2220 310 2220 270 {}
C {devices/lab_wire.sym} 2220 270 0 1 {name=l116 lab=drv_p}
N 2180 340 2140 340 {}
C {devices/lab_wire.sym} 2140 340 0 0 {name=l117 lab=vb3}
N 2220 370 2220 410 {}
C {devices/lab_wire.sym} 2220 410 2 0 {name=l118 lab=csrc_p}
N 2220 340 2260 340 {}
C {devices/lab_wire.sym} 2260 340 0 1 {name=l119 lab=vss}
