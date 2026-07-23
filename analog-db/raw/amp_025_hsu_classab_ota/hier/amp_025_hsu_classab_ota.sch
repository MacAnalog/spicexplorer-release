v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_025_hsu_classab_ota} -2350 -540 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -440 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_nmos_simple_2.sym} 0 0 0 0 {name=xcm_nmos_simple_2}
C {blocks/dp_pmos_simple_1.sym} 440 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -2090 340 0 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} -1870 340 0 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} -1650 340 0 0 {name=CIN value='cin_val'}
C {devices/capa_np.sym} -1430 340 0 0 {name=COUT value='cout_val'}
C {devices/res_np.sym} -1210 340 0 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} -990 340 0 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} -770 340 0 0 {name=RIN value='rin_val'}
C {devices/res_np.sym} -550 340 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} -330 340 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} -110 340 0 0 {name=ROUT value='rout_val'}
C {devices/vsource_np.sym} -2310 340 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -2310 120 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -2310 -100 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -2310 -320 0 0 {name=VCMFB_REF value="dc {vcmfb_ref}"}
C {devices/sg13_lv_pmos_np.sym} -880 -340 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -660 -340 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} -440 -340 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} -220 -340 0 0 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_pmos_np.sym} 0 -340 0 0 {name=M13 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_pmos_np.sym} 220 -340 0 0 {name=M14 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 110 340 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 330 340 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} 440 -340 0 0 {name=M17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_pmos_np.sym} 550 340 0 0 {name=M18 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 770 340 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} 660 -340 0 0 {name=M20 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 990 340 0 0 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 1210 340 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} 880 -340 0 0 {name=M23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_pmos_np.sym} 1430 340 0 0 {name=M24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_nmos_np.sym} 1650 340 0 0 {name=M25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
C {devices/sg13_lv_nmos_np.sym} 1870 340 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_nmos_np.sym} 2090 340 0 0 {name=M9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
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
N -2090 310 -2090 270 {}
C {devices/lab_wire.sym} -2090 270 0 1 {name=l12 lab=abm_p}
N -2090 370 -2090 410 {}
C {devices/lab_wire.sym} -2090 410 2 0 {name=l13 lab=zc_p}
N -1870 310 -1870 270 {}
C {devices/lab_wire.sym} -1870 270 0 1 {name=l14 lab=abm_n}
N -1870 370 -1870 410 {}
C {devices/lab_wire.sym} -1870 410 2 0 {name=l15 lab=zc_n}
N -1650 310 -1650 270 {}
C {devices/lab_wire.sym} -1650 270 0 1 {name=l16 lab=cm_det}
N -1650 370 -1650 410 {}
C {devices/lab_wire.sym} -1650 410 2 0 {name=l17 lab=vcmfb_ref}
N -1430 310 -1430 270 {}
C {devices/lab_wire.sym} -1430 270 0 1 {name=l18 lab=vss}
N -1430 370 -1430 410 {}
C {devices/lab_wire.sym} -1430 410 2 0 {name=l19 lab=vcmfb}
N -1210 310 -1210 270 {}
C {devices/lab_wire.sym} -1210 270 0 1 {name=l20 lab=zc_p}
N -1210 370 -1210 410 {}
C {devices/lab_wire.sym} -1210 410 2 0 {name=l21 lab=drv_p}
N -990 310 -990 270 {}
C {devices/lab_wire.sym} -990 270 0 1 {name=l22 lab=drv_n}
N -990 370 -990 410 {}
C {devices/lab_wire.sym} -990 410 2 0 {name=l23 lab=zc_n}
N -770 310 -770 270 {}
C {devices/lab_wire.sym} -770 270 0 1 {name=l24 lab=cm_det}
N -770 370 -770 410 {}
C {devices/lab_wire.sym} -770 410 2 0 {name=l25 lab=vcmfb_ref}
N -550 310 -550 270 {}
C {devices/lab_wire.sym} -550 270 0 1 {name=l26 lab=voutn}
N -550 370 -550 410 {}
C {devices/lab_wire.sym} -550 410 2 0 {name=l27 lab=cm_det}
N -330 310 -330 270 {}
C {devices/lab_wire.sym} -330 270 0 1 {name=l28 lab=cm_det}
N -330 370 -330 410 {}
C {devices/lab_wire.sym} -330 410 2 0 {name=l29 lab=voutp}
N -110 310 -110 270 {}
C {devices/lab_wire.sym} -110 270 0 1 {name=l30 lab=vss}
N -110 370 -110 410 {}
C {devices/lab_wire.sym} -110 410 2 0 {name=l31 lab=vcmfb}
N -2310 310 -2310 270 {}
C {devices/lab_wire.sym} -2310 270 0 1 {name=l32 lab=vb1}
N -2310 370 -2310 410 {}
C {devices/lab_wire.sym} -2310 410 2 0 {name=l33 lab=vss}
N -2310 90 -2310 50 {}
C {devices/lab_wire.sym} -2310 50 0 1 {name=l34 lab=vb2}
N -2310 150 -2310 190 {}
C {devices/lab_wire.sym} -2310 190 2 0 {name=l35 lab=vss}
N -2310 -130 -2310 -170 {}
C {devices/lab_wire.sym} -2310 -170 0 1 {name=l36 lab=vb3}
N -2310 -70 -2310 -30 {}
C {devices/lab_wire.sym} -2310 -30 2 0 {name=l37 lab=vss}
N -2310 -350 -2310 -390 {}
C {devices/lab_wire.sym} -2310 -390 0 1 {name=l38 lab=vcmfb_ref}
N -2310 -290 -2310 -250 {}
C {devices/lab_wire.sym} -2310 -250 2 0 {name=l39 lab=vss}
N -860 -310 -860 -270 {}
C {devices/lab_wire.sym} -860 -270 2 0 {name=l40 lab=tail}
N -900 -340 -940 -340 {}
C {devices/lab_wire.sym} -940 -340 0 0 {name=l41 lab=vb1}
N -860 -370 -860 -410 {}
C {devices/lab_wire.sym} -860 -410 0 1 {name=l42 lab=vdd}
N -860 -340 -820 -340 {}
C {devices/lab_wire.sym} -820 -340 0 1 {name=l43 lab=vdd}
N -640 -310 -640 -270 {}
C {devices/lab_wire.sym} -640 -270 2 0 {name=l44 lab=drv_n}
N -680 -340 -720 -340 {}
C {devices/lab_wire.sym} -720 -340 0 0 {name=l45 lab=vb2}
N -640 -370 -640 -410 {}
C {devices/lab_wire.sym} -640 -410 0 1 {name=l46 lab=psrc_n}
N -640 -340 -600 -340 {}
C {devices/lab_wire.sym} -600 -340 0 1 {name=l47 lab=vdd}
N -420 -310 -420 -270 {}
C {devices/lab_wire.sym} -420 -270 2 0 {name=l48 lab=drv_p}
N -460 -340 -500 -340 {}
C {devices/lab_wire.sym} -500 -340 0 0 {name=l49 lab=vb2}
N -420 -370 -420 -410 {}
C {devices/lab_wire.sym} -420 -410 0 1 {name=l50 lab=psrc_p}
N -420 -340 -380 -340 {}
C {devices/lab_wire.sym} -380 -340 0 1 {name=l51 lab=vdd}
N -200 -310 -200 -270 {}
C {devices/lab_wire.sym} -200 -270 2 0 {name=l52 lab=psrc_n}
N -240 -340 -280 -340 {}
C {devices/lab_wire.sym} -280 -340 0 0 {name=l53 lab=vcmfb}
N -200 -370 -200 -410 {}
C {devices/lab_wire.sym} -200 -410 0 1 {name=l54 lab=vdd}
N -200 -340 -160 -340 {}
C {devices/lab_wire.sym} -160 -340 0 1 {name=l55 lab=vdd}
N 20 -310 20 -270 {}
C {devices/lab_wire.sym} 20 -270 2 0 {name=l56 lab=psrc_p}
N -20 -340 -60 -340 {}
C {devices/lab_wire.sym} -60 -340 0 0 {name=l57 lab=vcmfb}
N 20 -370 20 -410 {}
C {devices/lab_wire.sym} 20 -410 0 1 {name=l58 lab=vdd}
N 20 -340 60 -340 {}
C {devices/lab_wire.sym} 60 -340 0 1 {name=l59 lab=vdd}
N 240 -310 240 -270 {}
C {devices/lab_wire.sym} 240 -270 2 0 {name=l60 lab=gnf_p}
N 200 -340 160 -340 {}
C {devices/lab_wire.sym} 160 -340 0 0 {name=l61 lab=vb1}
N 240 -370 240 -410 {}
C {devices/lab_wire.sym} 240 -410 0 1 {name=l62 lab=vdd}
N 240 -340 280 -340 {}
C {devices/lab_wire.sym} 280 -340 0 1 {name=l63 lab=vdd}
N 130 310 130 270 {}
C {devices/lab_wire.sym} 130 270 0 1 {name=l64 lab=gnf_p}
N 90 340 50 340 {}
C {devices/lab_wire.sym} 50 340 0 0 {name=l65 lab=gnf_p}
N 130 370 130 410 {}
C {devices/lab_wire.sym} 130 410 2 0 {name=l66 lab=abm_p}
N 130 340 170 340 {}
C {devices/lab_wire.sym} 170 340 0 1 {name=l67 lab=vss}
N 350 310 350 270 {}
C {devices/lab_wire.sym} 350 270 0 1 {name=l68 lab=vdd}
N 310 340 270 340 {}
C {devices/lab_wire.sym} 270 340 0 0 {name=l69 lab=gnf_p}
N 350 370 350 410 {}
C {devices/lab_wire.sym} 350 410 2 0 {name=l70 lab=voutp}
N 350 340 390 340 {}
C {devices/lab_wire.sym} 390 340 0 1 {name=l71 lab=vss}
N 460 -310 460 -270 {}
C {devices/lab_wire.sym} 460 -270 2 0 {name=l72 lab=gpf_p}
N 420 -340 380 -340 {}
C {devices/lab_wire.sym} 380 -340 0 0 {name=l73 lab=gpf_p}
N 460 -370 460 -410 {}
C {devices/lab_wire.sym} 460 -410 0 1 {name=l74 lab=abm_p}
N 460 -340 500 -340 {}
C {devices/lab_wire.sym} 500 -340 0 1 {name=l75 lab=vdd}
N 570 370 570 410 {}
C {devices/lab_wire.sym} 570 410 2 0 {name=l76 lab=vss}
N 530 340 490 340 {}
C {devices/lab_wire.sym} 490 340 0 0 {name=l77 lab=gpf_p}
N 570 310 570 270 {}
C {devices/lab_wire.sym} 570 270 0 1 {name=l78 lab=voutp}
N 570 340 610 340 {}
C {devices/lab_wire.sym} 610 340 0 1 {name=l79 lab=vdd}
N 790 310 790 270 {}
C {devices/lab_wire.sym} 790 270 0 1 {name=l80 lab=gpf_p}
N 750 340 710 340 {}
C {devices/lab_wire.sym} 710 340 0 0 {name=l81 lab=drv_p}
N 790 370 790 410 {}
C {devices/lab_wire.sym} 790 410 2 0 {name=l82 lab=vss}
N 790 340 830 340 {}
C {devices/lab_wire.sym} 830 340 0 1 {name=l83 lab=vss}
N 680 -310 680 -270 {}
C {devices/lab_wire.sym} 680 -270 2 0 {name=l84 lab=gnf_n}
N 640 -340 600 -340 {}
C {devices/lab_wire.sym} 600 -340 0 0 {name=l85 lab=vb1}
N 680 -370 680 -410 {}
C {devices/lab_wire.sym} 680 -410 0 1 {name=l86 lab=vdd}
N 680 -340 720 -340 {}
C {devices/lab_wire.sym} 720 -340 0 1 {name=l87 lab=vdd}
N 1010 310 1010 270 {}
C {devices/lab_wire.sym} 1010 270 0 1 {name=l88 lab=gnf_n}
N 970 340 930 340 {}
C {devices/lab_wire.sym} 930 340 0 0 {name=l89 lab=gnf_n}
N 1010 370 1010 410 {}
C {devices/lab_wire.sym} 1010 410 2 0 {name=l90 lab=abm_n}
N 1010 340 1050 340 {}
C {devices/lab_wire.sym} 1050 340 0 1 {name=l91 lab=vss}
N 1230 310 1230 270 {}
C {devices/lab_wire.sym} 1230 270 0 1 {name=l92 lab=vdd}
N 1190 340 1150 340 {}
C {devices/lab_wire.sym} 1150 340 0 0 {name=l93 lab=gnf_n}
N 1230 370 1230 410 {}
C {devices/lab_wire.sym} 1230 410 2 0 {name=l94 lab=voutn}
N 1230 340 1270 340 {}
C {devices/lab_wire.sym} 1270 340 0 1 {name=l95 lab=vss}
N 900 -310 900 -270 {}
C {devices/lab_wire.sym} 900 -270 2 0 {name=l96 lab=gpf_n}
N 860 -340 820 -340 {}
C {devices/lab_wire.sym} 820 -340 0 0 {name=l97 lab=gpf_n}
N 900 -370 900 -410 {}
C {devices/lab_wire.sym} 900 -410 0 1 {name=l98 lab=abm_n}
N 900 -340 940 -340 {}
C {devices/lab_wire.sym} 940 -340 0 1 {name=l99 lab=vdd}
N 1450 370 1450 410 {}
C {devices/lab_wire.sym} 1450 410 2 0 {name=l100 lab=vss}
N 1410 340 1370 340 {}
C {devices/lab_wire.sym} 1370 340 0 0 {name=l101 lab=gpf_n}
N 1450 310 1450 270 {}
C {devices/lab_wire.sym} 1450 270 0 1 {name=l102 lab=voutn}
N 1450 340 1490 340 {}
C {devices/lab_wire.sym} 1490 340 0 1 {name=l103 lab=vdd}
N 1670 310 1670 270 {}
C {devices/lab_wire.sym} 1670 270 0 1 {name=l104 lab=gpf_n}
N 1630 340 1590 340 {}
C {devices/lab_wire.sym} 1590 340 0 0 {name=l105 lab=drv_n}
N 1670 370 1670 410 {}
C {devices/lab_wire.sym} 1670 410 2 0 {name=l106 lab=vss}
N 1670 340 1710 340 {}
C {devices/lab_wire.sym} 1710 340 0 1 {name=l107 lab=vss}
N 1890 310 1890 270 {}
C {devices/lab_wire.sym} 1890 270 0 1 {name=l108 lab=drv_n}
N 1850 340 1810 340 {}
C {devices/lab_wire.sym} 1810 340 0 0 {name=l109 lab=vb3}
N 1890 370 1890 410 {}
C {devices/lab_wire.sym} 1890 410 2 0 {name=l110 lab=csrc_n}
N 1890 340 1930 340 {}
C {devices/lab_wire.sym} 1930 340 0 1 {name=l111 lab=vss}
N 2110 310 2110 270 {}
C {devices/lab_wire.sym} 2110 270 0 1 {name=l112 lab=drv_p}
N 2070 340 2030 340 {}
C {devices/lab_wire.sym} 2030 340 0 0 {name=l113 lab=vb3}
N 2110 370 2110 410 {}
C {devices/lab_wire.sym} 2110 410 2 0 {name=l114 lab=csrc_p}
N 2110 340 2150 340 {}
C {devices/lab_wire.sym} 2150 340 0 1 {name=l115 lab=vss}
