v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_035_fan_chopper_cmfb_dual} -2460 -740 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -1320 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_pmos_simple_2.sym} -880 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/cm_nmos_simple_1.sym} -440 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_nmos_simple_2.sym} 0 0 0 0 {name=xcm_nmos_simple_2}
C {blocks/dp_pmos_simple_1.sym} 440 0 0 0 {name=xdp_pmos_simple_1}
C {blocks/dp_pmos_simple_2.sym} 880 0 0 0 {name=xdp_pmos_simple_2}
C {blocks/dp_pmos_simple_3.sym} 1320 0 0 0 {name=xdp_pmos_simple_3}
C {devices/capa_np.sym} -2200 340 0 0 {name=CCM_S1 value='c_cm_s1'}
C {devices/capa_np.sym} -1980 340 0 0 {name=CM1_CORE value='x_dut_cm1_core_value'}
C {devices/capa_np.sym} -1760 340 0 0 {name=CM2_CORE value='x_dut_cm2_core_value'}
C {devices/res_np.sym} -1540 340 0 0 {name=RMN_CMFB_OUT value=…b_out_value'}
C {devices/res_np.sym} -1320 340 0 0 {name=RMN_CMFB_S1 value=…fb_s1_value'}
C {devices/res_np.sym} -1100 340 0 0 {name=RMP_CMFB_OUT value=…b_out_value'}
C {devices/res_np.sym} -880 340 0 0 {name=RMP_CMFB_S1 value=…fb_s1_value'}
C {devices/vsource_np.sym} -2420 340 0 0 {name=VB1_CORE value="dc {vb1_core}"}
C {devices/vsource_np.sym} -2420 120 0 0 {name=VB2_CORE value="dc {vb2_core}"}
C {devices/vsource_np.sym} -2420 -100 0 0 {name=VB3_CORE value="dc {vb3_core}"}
C {devices/vsource_np.sym} -2420 -320 0 0 {name=VREFOUT value="dc {vcm_ref}"}
C {devices/vsource_np.sym} -2420 -540 0 0 {name=VREFS1 value="dc {vcm_ref_stg1}"}
C {devices/sg13_lv_pmos_np.sym} -880 -340 0 0 {name=M10_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_core_w l=x_dut_xm10_core_l m=x_dut_xm10_core_m}
C {devices/sg13_lv_pmos_np.sym} -660 -340 0 0 {name=M11_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_core_w l=x_dut_xm11_core_l m=x_dut_xm11_core_m}
C {devices/sg13_lv_nmos_np.sym} -660 340 0 0 {name=M12_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_core_w l=x_dut_xm12_core_l m=x_dut_xm12_core_m}
C {devices/sg13_lv_nmos_np.sym} -440 340 0 0 {name=M13_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_core_w l=x_dut_xm13_core_l m=x_dut_xm13_core_m}
C {devices/sg13_lv_nmos_np.sym} -220 340 0 0 {name=M14_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_core_w l=x_dut_xm14_core_l m=x_dut_xm14_core_m}
C {devices/sg13_lv_nmos_np.sym} 0 340 0 0 {name=M15_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_core_w l=x_dut_xm15_core_l m=x_dut_xm15_core_m}
C {devices/sg13_lv_nmos_np.sym} 220 340 0 0 {name=M16_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_core_w l=x_dut_xm16_core_l m=x_dut_xm16_core_m}
C {devices/sg13_lv_pmos_np.sym} 440 340 0 0 {name=M17_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_core_w l=x_dut_xm17_core_l m=x_dut_xm17_core_m}
C {devices/sg13_lv_nmos_np.sym} 660 340 0 0 {name=M18_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_core_w l=x_dut_xm18_core_l m=x_dut_xm18_core_m}
C {devices/sg13_lv_pmos_np.sym} 880 340 0 0 {name=M19_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_core_w l=x_dut_xm19_core_l m=x_dut_xm19_core_m}
C {devices/sg13_lv_pmos_np.sym} -440 -340 0 0 {name=M1_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_core_w l=x_dut_xm1_core_l m=x_dut_xm1_core_m}
C {devices/sg13_lv_nmos_np.sym} 1100 340 0 0 {name=M20_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_core_w l=x_dut_xm20_core_l m=x_dut_xm20_core_m}
C {devices/sg13_lv_pmos_np.sym} -220 -340 0 0 {name=M21_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_core_w l=x_dut_xm21_core_l m=x_dut_xm21_core_m}
C {devices/sg13_lv_nmos_np.sym} 1320 340 0 0 {name=M22_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_core_w l=x_dut_xm22_core_l m=x_dut_xm22_core_m}
C {devices/sg13_lv_pmos_np.sym} 0 -340 0 0 {name=M23_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_core_w l=x_dut_xm23_core_l m=x_dut_xm23_core_m}
C {devices/sg13_lv_nmos_np.sym} 1540 340 0 0 {name=M4_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_core_w l=x_dut_xm4_core_l m=x_dut_xm4_core_m}
C {devices/sg13_lv_nmos_np.sym} 1760 340 0 0 {name=M5_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_core_w l=x_dut_xm5_core_l m=x_dut_xm5_core_m}
C {devices/sg13_lv_pmos_np.sym} 220 -340 0 0 {name=M6_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_core_w l=x_dut_xm6_core_l m=x_dut_xm6_core_m}
C {devices/sg13_lv_nmos_np.sym} 1980 340 0 0 {name=M7_CMFB_OUT model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_cmfb_out_w l=x_dut_xm7_cmfb_out_l m=x_dut_xm7_cmfb_out_m}
C {devices/sg13_lv_nmos_np.sym} 2200 340 0 0 {name=M7_CMFB_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_cmfb_s1_w l=x_dut_xm7_cmfb_s1_l m=x_dut_xm7_cmfb_s1_m}
C {devices/sg13_lv_pmos_np.sym} 440 -340 0 0 {name=M7_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_core_w l=x_dut_xm7_core_l m=x_dut_xm7_core_m}
C {devices/sg13_lv_pmos_np.sym} 660 -340 0 0 {name=M8O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8o_w l=x_dut_xm8o_l m=x_dut_xm8o_m}
C {devices/sg13_lv_pmos_np.sym} 880 -340 0 0 {name=M9O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9o_w l=x_dut_xm9o_l m=x_dut_xm9o_m}
N -1210 -20 -1170 -20 {}
C {devices/lab_wire.sym} -1170 -20 0 1 {name=l0 lab=cmfb_out__bias}
N -1210 20 -1170 20 {}
C {devices/lab_wire.sym} -1170 20 0 1 {name=l1 lab=cmfb_out__ptail}
N -1320 -80 -1320 -120 {}
C {devices/lab_wire.sym} -1320 -120 0 1 {name=l2 lab=vdd}
N -770 -20 -730 -20 {}
C {devices/lab_wire.sym} -730 -20 0 1 {name=l3 lab=cmfb_s1__bias}
N -770 20 -730 20 {}
C {devices/lab_wire.sym} -730 20 0 1 {name=l4 lab=cmfb_s1__ptail}
N -880 -80 -880 -120 {}
C {devices/lab_wire.sym} -880 -120 0 1 {name=l5 lab=vdd}
N -330 -20 -290 -20 {}
C {devices/lab_wire.sym} -290 -20 0 1 {name=l6 lab=cmfb_out__mirr}
N -330 20 -290 20 {}
C {devices/lab_wire.sym} -290 20 0 1 {name=l7 lab=vb4o}
N -440 80 -440 120 {}
C {devices/lab_wire.sym} -440 120 2 0 {name=l8 lab=vss}
N 110 -20 150 -20 {}
C {devices/lab_wire.sym} 150 -20 0 1 {name=l9 lab=cmfb_s1__mirr}
N 110 20 150 20 {}
C {devices/lab_wire.sym} 150 20 0 1 {name=l10 lab=vb4_ctl}
N 0 80 0 120 {}
C {devices/lab_wire.sym} 0 120 2 0 {name=l11 lab=vss}
N 330 -20 290 -20 {}
C {devices/lab_wire.sym} 290 -20 0 0 {name=l12 lab=vinn}
N 330 20 290 20 {}
C {devices/lab_wire.sym} 290 20 0 0 {name=l13 lab=vinp}
N 550 -40 590 -40 {}
C {devices/lab_wire.sym} 590 -40 0 1 {name=l14 lab=core__fold_n}
N 550 0 590 0 {}
C {devices/lab_wire.sym} 590 0 0 1 {name=l15 lab=core__fold_p}
N 550 40 590 40 {}
C {devices/lab_wire.sym} 590 40 0 1 {name=l16 lab=core__tail}
N 440 -100 440 -140 {}
C {devices/lab_wire.sym} 440 -140 0 1 {name=l17 lab=vdd}
N 770 -20 730 -20 {}
C {devices/lab_wire.sym} 730 -20 0 0 {name=l18 lab=cmfb_out__cm_sense}
N 770 20 730 20 {}
C {devices/lab_wire.sym} 730 20 0 0 {name=l19 lab=vref_out}
N 990 -40 1030 -40 {}
C {devices/lab_wire.sym} 1030 -40 0 1 {name=l20 lab=cmfb_out__mirr}
N 990 0 1030 0 {}
C {devices/lab_wire.sym} 1030 0 0 1 {name=l21 lab=cmfb_out__ptail}
N 990 40 1030 40 {}
C {devices/lab_wire.sym} 1030 40 0 1 {name=l22 lab=vb4o}
N 880 -100 880 -140 {}
C {devices/lab_wire.sym} 880 -140 0 1 {name=l23 lab=vdd}
N 1210 -20 1170 -20 {}
C {devices/lab_wire.sym} 1170 -20 0 0 {name=l24 lab=cmfb_s1__cm_sense}
N 1210 20 1170 20 {}
C {devices/lab_wire.sym} 1170 20 0 0 {name=l25 lab=vref_s1}
N 1430 -40 1470 -40 {}
C {devices/lab_wire.sym} 1470 -40 0 1 {name=l26 lab=cmfb_s1__mirr}
N 1430 0 1470 0 {}
C {devices/lab_wire.sym} 1470 0 0 1 {name=l27 lab=cmfb_s1__ptail}
N 1430 40 1470 40 {}
C {devices/lab_wire.sym} 1470 40 0 1 {name=l28 lab=vb4_ctl}
N 1320 -100 1320 -140 {}
C {devices/lab_wire.sym} 1320 -140 0 1 {name=l29 lab=vdd}
N -2200 310 -2200 270 {}
C {devices/lab_wire.sym} -2200 270 0 1 {name=l30 lab=vb4_ctl}
N -2200 370 -2200 410 {}
C {devices/lab_wire.sym} -2200 410 2 0 {name=l31 lab=vss}
N -1980 310 -1980 270 {}
C {devices/lab_wire.sym} -1980 270 0 1 {name=l32 lab=core__g2_p}
N -1980 370 -1980 410 {}
C {devices/lab_wire.sym} -1980 410 2 0 {name=l33 lab=voutp}
N -1760 310 -1760 270 {}
C {devices/lab_wire.sym} -1760 270 0 1 {name=l34 lab=core__g2_n}
N -1760 370 -1760 410 {}
C {devices/lab_wire.sym} -1760 410 2 0 {name=l35 lab=voutn}
N -1540 310 -1540 270 {}
C {devices/lab_wire.sym} -1540 270 0 1 {name=l36 lab=voutn}
N -1540 370 -1540 410 {}
C {devices/lab_wire.sym} -1540 410 2 0 {name=l37 lab=cmfb_out__cm_sense}
N -1320 310 -1320 270 {}
C {devices/lab_wire.sym} -1320 270 0 1 {name=l38 lab=stg1_n}
N -1320 370 -1320 410 {}
C {devices/lab_wire.sym} -1320 410 2 0 {name=l39 lab=cmfb_s1__cm_sense}
N -1100 310 -1100 270 {}
C {devices/lab_wire.sym} -1100 270 0 1 {name=l40 lab=cmfb_out__cm_sense}
N -1100 370 -1100 410 {}
C {devices/lab_wire.sym} -1100 410 2 0 {name=l41 lab=voutp}
N -880 310 -880 270 {}
C {devices/lab_wire.sym} -880 270 0 1 {name=l42 lab=cmfb_s1__cm_sense}
N -880 370 -880 410 {}
C {devices/lab_wire.sym} -880 410 2 0 {name=l43 lab=stg1_p}
N -2420 310 -2420 270 {}
C {devices/lab_wire.sym} -2420 270 0 1 {name=l44 lab=core__vb1}
N -2420 370 -2420 410 {}
C {devices/lab_wire.sym} -2420 410 2 0 {name=l45 lab=vss}
N -2420 90 -2420 50 {}
C {devices/lab_wire.sym} -2420 50 0 1 {name=l46 lab=core__vb2}
N -2420 150 -2420 190 {}
C {devices/lab_wire.sym} -2420 190 2 0 {name=l47 lab=vss}
N -2420 -130 -2420 -170 {}
C {devices/lab_wire.sym} -2420 -170 0 1 {name=l48 lab=core__vb3}
N -2420 -70 -2420 -30 {}
C {devices/lab_wire.sym} -2420 -30 2 0 {name=l49 lab=vss}
N -2420 -350 -2420 -390 {}
C {devices/lab_wire.sym} -2420 -390 0 1 {name=l50 lab=vref_out}
N -2420 -290 -2420 -250 {}
C {devices/lab_wire.sym} -2420 -250 2 0 {name=l51 lab=vss}
N -2420 -570 -2420 -610 {}
C {devices/lab_wire.sym} -2420 -610 0 1 {name=l52 lab=vref_s1}
N -2420 -510 -2420 -470 {}
C {devices/lab_wire.sym} -2420 -470 2 0 {name=l53 lab=vss}
N -860 -310 -860 -270 {}
C {devices/lab_wire.sym} -860 -270 2 0 {name=l54 lab=stg1_n}
N -900 -340 -940 -340 {}
C {devices/lab_wire.sym} -940 -340 0 0 {name=l55 lab=core__vb3}
N -860 -370 -860 -410 {}
C {devices/lab_wire.sym} -860 -410 0 1 {name=l56 lab=core__casc_src_n}
N -860 -340 -820 -340 {}
C {devices/lab_wire.sym} -820 -340 0 1 {name=l57 lab=vdd}
N -640 -310 -640 -270 {}
C {devices/lab_wire.sym} -640 -270 2 0 {name=l58 lab=stg1_p}
N -680 -340 -720 -340 {}
C {devices/lab_wire.sym} -720 -340 0 0 {name=l59 lab=core__vb3}
N -640 -370 -640 -410 {}
C {devices/lab_wire.sym} -640 -410 0 1 {name=l60 lab=core__casc_src_p}
N -640 -340 -600 -340 {}
C {devices/lab_wire.sym} -600 -340 0 1 {name=l61 lab=vdd}
N -640 310 -640 270 {}
C {devices/lab_wire.sym} -640 270 0 1 {name=l62 lab=stg1_p}
N -680 340 -720 340 {}
C {devices/lab_wire.sym} -720 340 0 0 {name=l63 lab=core__vb2}
N -640 370 -640 410 {}
C {devices/lab_wire.sym} -640 410 2 0 {name=l64 lab=core__fold_p}
N -640 340 -600 340 {}
C {devices/lab_wire.sym} -600 340 0 1 {name=l65 lab=vss}
N -420 310 -420 270 {}
C {devices/lab_wire.sym} -420 270 0 1 {name=l66 lab=stg1_n}
N -460 340 -500 340 {}
C {devices/lab_wire.sym} -500 340 0 0 {name=l67 lab=core__vb2}
N -420 370 -420 410 {}
C {devices/lab_wire.sym} -420 410 2 0 {name=l68 lab=core__fold_n}
N -420 340 -380 340 {}
C {devices/lab_wire.sym} -380 340 0 1 {name=l69 lab=vss}
N -200 310 -200 270 {}
C {devices/lab_wire.sym} -200 270 0 1 {name=l70 lab=voutp}
N -240 340 -280 340 {}
C {devices/lab_wire.sym} -280 340 0 0 {name=l71 lab=core__g2_p}
N -200 370 -200 410 {}
C {devices/lab_wire.sym} -200 410 2 0 {name=l72 lab=vss}
N -200 340 -160 340 {}
C {devices/lab_wire.sym} -160 340 0 1 {name=l73 lab=vss}
N 20 310 20 270 {}
C {devices/lab_wire.sym} 20 270 0 1 {name=l74 lab=voutn}
N -20 340 -60 340 {}
C {devices/lab_wire.sym} -60 340 0 0 {name=l75 lab=core__g2_n}
N 20 370 20 410 {}
C {devices/lab_wire.sym} 20 410 2 0 {name=l76 lab=vss}
N 20 340 60 340 {}
C {devices/lab_wire.sym} 60 340 0 1 {name=l77 lab=vss}
N 240 310 240 270 {}
C {devices/lab_wire.sym} 240 270 0 1 {name=l78 lab=stg1_n}
N 200 340 160 340 {}
C {devices/lab_wire.sym} 160 340 0 0 {name=l79 lab=vdd}
N 240 370 240 410 {}
C {devices/lab_wire.sym} 240 410 2 0 {name=l80 lab=core__g2_n}
N 240 340 280 340 {}
C {devices/lab_wire.sym} 280 340 0 1 {name=l81 lab=vss}
N 460 370 460 410 {}
C {devices/lab_wire.sym} 460 410 2 0 {name=l82 lab=core__g2_n}
N 420 340 380 340 {}
C {devices/lab_wire.sym} 380 340 0 0 {name=l83 lab=vss}
N 460 310 460 270 {}
C {devices/lab_wire.sym} 460 270 0 1 {name=l84 lab=stg1_n}
N 460 340 500 340 {}
C {devices/lab_wire.sym} 500 340 0 1 {name=l85 lab=vdd}
N 680 310 680 270 {}
C {devices/lab_wire.sym} 680 270 0 1 {name=l86 lab=stg1_p}
N 640 340 600 340 {}
C {devices/lab_wire.sym} 600 340 0 0 {name=l87 lab=vdd}
N 680 370 680 410 {}
C {devices/lab_wire.sym} 680 410 2 0 {name=l88 lab=core__g2_p}
N 680 340 720 340 {}
C {devices/lab_wire.sym} 720 340 0 1 {name=l89 lab=vss}
N 900 370 900 410 {}
C {devices/lab_wire.sym} 900 410 2 0 {name=l90 lab=core__g2_p}
N 860 340 820 340 {}
C {devices/lab_wire.sym} 820 340 0 0 {name=l91 lab=vss}
N 900 310 900 270 {}
C {devices/lab_wire.sym} 900 270 0 1 {name=l92 lab=stg1_p}
N 900 340 940 340 {}
C {devices/lab_wire.sym} 940 340 0 1 {name=l93 lab=vdd}
N -420 -310 -420 -270 {}
C {devices/lab_wire.sym} -420 -270 2 0 {name=l94 lab=core__tail}
N -460 -340 -500 -340 {}
C {devices/lab_wire.sym} -500 -340 0 0 {name=l95 lab=vb4_ctl}
N -420 -370 -420 -410 {}
C {devices/lab_wire.sym} -420 -410 0 1 {name=l96 lab=vdd}
N -420 -340 -380 -340 {}
C {devices/lab_wire.sym} -380 -340 0 1 {name=l97 lab=vdd}
N 1120 310 1120 270 {}
C {devices/lab_wire.sym} 1120 270 0 1 {name=l98 lab=stg1_p}
N 1080 340 1040 340 {}
C {devices/lab_wire.sym} 1040 340 0 0 {name=l99 lab=vss}
N 1120 370 1120 410 {}
C {devices/lab_wire.sym} 1120 410 2 0 {name=l100 lab=core__g2_n}
N 1120 340 1160 340 {}
C {devices/lab_wire.sym} 1160 340 0 1 {name=l101 lab=vss}
N -200 -310 -200 -270 {}
C {devices/lab_wire.sym} -200 -270 2 0 {name=l102 lab=core__g2_n}
N -240 -340 -280 -340 {}
C {devices/lab_wire.sym} -280 -340 0 0 {name=l103 lab=vdd}
N -200 -370 -200 -410 {}
C {devices/lab_wire.sym} -200 -410 0 1 {name=l104 lab=stg1_p}
N -200 -340 -160 -340 {}
C {devices/lab_wire.sym} -160 -340 0 1 {name=l105 lab=vdd}
N 1340 310 1340 270 {}
C {devices/lab_wire.sym} 1340 270 0 1 {name=l106 lab=stg1_n}
N 1300 340 1260 340 {}
C {devices/lab_wire.sym} 1260 340 0 0 {name=l107 lab=vss}
N 1340 370 1340 410 {}
C {devices/lab_wire.sym} 1340 410 2 0 {name=l108 lab=core__g2_p}
N 1340 340 1380 340 {}
C {devices/lab_wire.sym} 1380 340 0 1 {name=l109 lab=vss}
N 20 -310 20 -270 {}
C {devices/lab_wire.sym} 20 -270 2 0 {name=l110 lab=core__g2_p}
N -20 -340 -60 -340 {}
C {devices/lab_wire.sym} -60 -340 0 0 {name=l111 lab=vdd}
N 20 -370 20 -410 {}
C {devices/lab_wire.sym} 20 -410 0 1 {name=l112 lab=stg1_n}
N 20 -340 60 -340 {}
C {devices/lab_wire.sym} 60 -340 0 1 {name=l113 lab=vdd}
N 1560 310 1560 270 {}
C {devices/lab_wire.sym} 1560 270 0 1 {name=l114 lab=core__fold_p}
N 1520 340 1480 340 {}
C {devices/lab_wire.sym} 1480 340 0 0 {name=l115 lab=core__vb1}
N 1560 370 1560 410 {}
C {devices/lab_wire.sym} 1560 410 2 0 {name=l116 lab=vss}
N 1560 340 1600 340 {}
C {devices/lab_wire.sym} 1600 340 0 1 {name=l117 lab=vss}
N 1780 310 1780 270 {}
C {devices/lab_wire.sym} 1780 270 0 1 {name=l118 lab=core__fold_n}
N 1740 340 1700 340 {}
C {devices/lab_wire.sym} 1700 340 0 0 {name=l119 lab=core__vb1}
N 1780 370 1780 410 {}
C {devices/lab_wire.sym} 1780 410 2 0 {name=l120 lab=vss}
N 1780 340 1820 340 {}
C {devices/lab_wire.sym} 1820 340 0 1 {name=l121 lab=vss}
N 240 -310 240 -270 {}
C {devices/lab_wire.sym} 240 -270 2 0 {name=l122 lab=core__casc_src_n}
N 200 -340 160 -340 {}
C {devices/lab_wire.sym} 160 -340 0 0 {name=l123 lab=vb4_ctl}
N 240 -370 240 -410 {}
C {devices/lab_wire.sym} 240 -410 0 1 {name=l124 lab=vdd}
N 240 -340 280 -340 {}
C {devices/lab_wire.sym} 280 -340 0 1 {name=l125 lab=vdd}
N 2000 310 2000 270 {}
C {devices/lab_wire.sym} 2000 270 0 1 {name=l126 lab=cmfb_out__bias}
N 1960 340 1920 340 {}
C {devices/lab_wire.sym} 1920 340 0 0 {name=l127 lab=cmfb_out__bias}
N 2000 370 2000 410 {}
C {devices/lab_wire.sym} 2000 410 2 0 {name=l128 lab=vss}
N 2000 340 2040 340 {}
C {devices/lab_wire.sym} 2040 340 0 1 {name=l129 lab=vss}
N 2220 310 2220 270 {}
C {devices/lab_wire.sym} 2220 270 0 1 {name=l130 lab=cmfb_s1__bias}
N 2180 340 2140 340 {}
C {devices/lab_wire.sym} 2140 340 0 0 {name=l131 lab=cmfb_s1__bias}
N 2220 370 2220 410 {}
C {devices/lab_wire.sym} 2220 410 2 0 {name=l132 lab=vss}
N 2220 340 2260 340 {}
C {devices/lab_wire.sym} 2260 340 0 1 {name=l133 lab=vss}
N 460 -310 460 -270 {}
C {devices/lab_wire.sym} 460 -270 2 0 {name=l134 lab=core__casc_src_p}
N 420 -340 380 -340 {}
C {devices/lab_wire.sym} 380 -340 0 0 {name=l135 lab=vb4_ctl}
N 460 -370 460 -410 {}
C {devices/lab_wire.sym} 460 -410 0 1 {name=l136 lab=vdd}
N 460 -340 500 -340 {}
C {devices/lab_wire.sym} 500 -340 0 1 {name=l137 lab=vdd}
N 680 -310 680 -270 {}
C {devices/lab_wire.sym} 680 -270 2 0 {name=l138 lab=voutp}
N 640 -340 600 -340 {}
C {devices/lab_wire.sym} 600 -340 0 0 {name=l139 lab=vb4o}
N 680 -370 680 -410 {}
C {devices/lab_wire.sym} 680 -410 0 1 {name=l140 lab=vdd}
N 680 -340 720 -340 {}
C {devices/lab_wire.sym} 720 -340 0 1 {name=l141 lab=vdd}
N 900 -310 900 -270 {}
C {devices/lab_wire.sym} 900 -270 2 0 {name=l142 lab=voutn}
N 860 -340 820 -340 {}
C {devices/lab_wire.sym} 820 -340 0 0 {name=l143 lab=vb4o}
N 900 -370 900 -410 {}
C {devices/lab_wire.sym} 900 -410 0 1 {name=l144 lab=vdd}
N 900 -340 940 -340 {}
C {devices/lab_wire.sym} 940 -340 0 1 {name=l145 lab=vdd}
