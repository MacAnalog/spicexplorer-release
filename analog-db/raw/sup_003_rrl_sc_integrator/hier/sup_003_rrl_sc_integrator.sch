v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sup_003_rrl_sc_integrator} -3800 -540 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -3540 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_pmos_cascode_1.sym} -3100 0 0 0 {name=xdp_pmos_cascode_1}
C {blocks/dp_nmos_simple_1.sym} -2660 0 0 0 {name=xdp_nmos_simple_1}
C {blocks/tg_pair_cmos_rail_bulk_1.sym} -2190 0 0 0 {name=xtg_pair_cmos_rail_bulk_1}
C {blocks/dp_nmos_simple_2.sym} -1720 0 0 0 {name=xdp_nmos_simple_2}
C {blocks/tg_pair_cmos_rail_bulk_2.sym} -1250 0 0 0 {name=xtg_pair_cmos_rail_bulk_2}
C {blocks/tg_pair_cmos_rail_bulk_3.sym} -750 0 0 0 {name=xtg_pair_cmos_rail_bulk_3}
C {blocks/tg_pair_cmos_rail_bulk_4.sym} -250 0 0 0 {name=xtg_pair_cmos_rail_bulk_4}
C {blocks/tg_pair_cmos_rail_bulk_5.sym} 250 0 0 0 {name=xtg_pair_cmos_rail_bulk_5}
C {blocks/tg_pair_cmos_rail_bulk_6.sym} 750 0 0 0 {name=xtg_pair_cmos_rail_bulk_6}
C {blocks/tg_pair_cmos_rail_bulk_7.sym} 1250 0 0 0 {name=xtg_pair_cmos_rail_bulk_7}
C {blocks/tg_pair_cmos_rail_bulk_8.sym} 1750 0 0 0 {name=xtg_pair_cmos_rail_bulk_8}
C {blocks/dp_pmos_simple_1.sym} 2220 0 0 0 {name=xdp_pmos_simple_1}
C {blocks/dp_pmos_simple_2.sym} 2660 0 0 0 {name=xdp_pmos_simple_2}
C {blocks/dp_pmos_simple_3.sym} 3100 0 0 0 {name=xdp_pmos_simple_3}
C {blocks/dp_pmos_simple_4.sym} 3540 0 0 0 {name=xdp_pmos_simple_4}
C {devices/capa_np.sym} -1760 340 0 0 {name=CAZ1 value='x_dut_caz1_value'}
C {devices/capa_np.sym} -1540 340 0 0 {name=CAZ2 value='x_dut_caz2_value'}
C {devices/capa_np.sym} -1320 340 0 0 {name=CINT1 value='x_dut_cint1_value'}
C {devices/capa_np.sym} -1100 340 0 0 {name=CINT2 value='x_dut_cint2_value'}
C {devices/capa_np.sym} -880 340 0 0 {name=CIN_1 value='cin_val'}
C {devices/capa_np.sym} -660 340 0 0 {name=COUT_1 value='cout_val'}
C {devices/capa_np.sym} -440 340 0 0 {name=CS1 value='x_dut_cs1_value'}
C {devices/capa_np.sym} -220 340 0 0 {name=CS2 value='x_dut_cs2_value'}
C {devices/res_np.sym} 0 340 0 0 {name=RIN_1 value='rin_val'}
C {devices/res_np.sym} 220 340 0 0 {name=ROUT_1 value='rout_val'}
C {devices/vsource_np.sym} -3760 340 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -3760 120 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -3760 -100 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -3760 -320 0 0 {name=VB4 value="dc {vb4}"}
C {devices/sg13_lv_nmos_np.sym} 440 340 0 0 {name=M11_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_opamp_w l=x_dut_xm11_opamp_l m=x_dut_xm11_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 660 340 0 0 {name=M12_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_opamp_w l=x_dut_xm12_opamp_l m=x_dut_xm12_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 880 340 0 0 {name=M16_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_opamp_w l=x_dut_xm16_opamp_l m=x_dut_xm16_opamp_m}
C {devices/sg13_lv_pmos_np.sym} -110 -340 0 0 {name=M1_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_opamp_w l=x_dut_xm1_opamp_l m=x_dut_xm1_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 1100 340 0 0 {name=M1_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s1_w l=x_dut_xm1_s1_l m=x_dut_xm1_s1_m}
C {devices/sg13_lv_nmos_np.sym} 1320 340 0 0 {name=M1_S2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s2_w l=x_dut_xm1_s2_l m=x_dut_xm1_s2_m}
C {devices/sg13_lv_pmos_np.sym} 1540 340 0 0 {name=M2_S1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s1_w l=x_dut_xm2_s1_l m=x_dut_xm2_s1_m}
C {devices/sg13_lv_pmos_np.sym} 1760 340 0 0 {name=M2_S2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s2_w l=x_dut_xm2_s2_l m=x_dut_xm2_s2_m}
C {devices/sg13_lv_pmos_np.sym} 110 -340 0 0 {name=M4_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_opamp_w l=x_dut_xm4_opamp_l m=x_dut_xm4_opamp_m}
N -3430 -40 -3390 -40 {}
C {devices/lab_wire.sym} -3390 -40 0 1 {name=l0 lab=oa_cm_bias}
N -3430 0 -3390 0 {}
C {devices/lab_wire.sym} -3390 0 0 1 {name=l1 lab=oa_csrc_n}
N -3430 40 -3390 40 {}
C {devices/lab_wire.sym} -3390 40 0 1 {name=l2 lab=oa_csrc_p}
N -3540 100 -3540 140 {}
C {devices/lab_wire.sym} -3540 140 2 0 {name=l3 lab=vss}
N -3210 -40 -3250 -40 {}
C {devices/lab_wire.sym} -3250 -40 0 0 {name=l4 lab=oa_inn}
N -3210 0 -3250 0 {}
C {devices/lab_wire.sym} -3250 0 0 0 {name=l5 lab=oa_inp}
N -3210 40 -3250 40 {}
C {devices/lab_wire.sym} -3250 40 0 0 {name=l6 lab=vb1}
N -2990 -40 -2950 -40 {}
C {devices/lab_wire.sym} -2950 -40 0 1 {name=l7 lab=oa_outn}
N -2990 0 -2950 0 {}
C {devices/lab_wire.sym} -2950 0 0 1 {name=l8 lab=oa_outp}
N -2990 40 -2950 40 {}
C {devices/lab_wire.sym} -2950 40 0 1 {name=l9 lab=oa_tail}
N -3100 -100 -3100 -140 {}
C {devices/lab_wire.sym} -3100 -140 0 1 {name=l10 lab=vdd}
N -2770 -20 -2810 -20 {}
C {devices/lab_wire.sym} -2810 -20 0 0 {name=l11 lab=clk_ch_rrl}
N -2770 20 -2810 20 {}
C {devices/lab_wire.sym} -2810 20 0 0 {name=l12 lab=clk_ch_rrl_not}
N -2550 -40 -2510 -40 {}
C {devices/lab_wire.sym} -2510 -40 0 1 {name=l13 lab=sc_p}
N -2550 0 -2510 0 {}
C {devices/lab_wire.sym} -2510 0 0 1 {name=l14 lab=sum_n}
N -2550 40 -2510 40 {}
C {devices/lab_wire.sym} -2510 40 0 1 {name=l15 lab=sum_p}
N -2660 100 -2660 140 {}
C {devices/lab_wire.sym} -2660 140 2 0 {name=l16 lab=vss}
N -2330 -20 -2370 -20 {}
C {devices/lab_wire.sym} -2370 -20 0 0 {name=l17 lab=clk_ch_rrl}
N -2330 20 -2370 20 {}
C {devices/lab_wire.sym} -2370 20 0 0 {name=l18 lab=clk_ch_rrl_not}
N -2050 -20 -2010 -20 {}
C {devices/lab_wire.sym} -2010 -20 0 1 {name=l19 lab=sc_p}
N -2050 20 -2010 20 {}
C {devices/lab_wire.sym} -2010 20 0 1 {name=l20 lab=sum_p}
N -2190 -80 -2190 -120 {}
C {devices/lab_wire.sym} -2190 -120 0 1 {name=l21 lab=vdd}
N -2190 80 -2190 120 {}
C {devices/lab_wire.sym} -2190 120 2 0 {name=l22 lab=vss}
N -1830 -20 -1870 -20 {}
C {devices/lab_wire.sym} -1870 -20 0 0 {name=l23 lab=clk_ch_rrl}
N -1830 20 -1870 20 {}
C {devices/lab_wire.sym} -1870 20 0 0 {name=l24 lab=clk_ch_rrl_not}
N -1610 -40 -1570 -40 {}
C {devices/lab_wire.sym} -1570 -40 0 1 {name=l25 lab=sc_n}
N -1610 0 -1570 0 {}
C {devices/lab_wire.sym} -1570 0 0 1 {name=l26 lab=sum_n}
N -1610 40 -1570 40 {}
C {devices/lab_wire.sym} -1570 40 0 1 {name=l27 lab=sum_p}
N -1720 100 -1720 140 {}
C {devices/lab_wire.sym} -1720 140 2 0 {name=l28 lab=vss}
N -1390 -20 -1430 -20 {}
C {devices/lab_wire.sym} -1430 -20 0 0 {name=l29 lab=clk_ch_rrl}
N -1390 20 -1430 20 {}
C {devices/lab_wire.sym} -1430 20 0 0 {name=l30 lab=clk_ch_rrl_not}
N -1110 -20 -1070 -20 {}
C {devices/lab_wire.sym} -1070 -20 0 1 {name=l31 lab=sc_n}
N -1110 20 -1070 20 {}
C {devices/lab_wire.sym} -1070 20 0 1 {name=l32 lab=sum_n}
N -1250 -80 -1250 -120 {}
C {devices/lab_wire.sym} -1250 -120 0 1 {name=l33 lab=vdd}
N -1250 80 -1250 120 {}
C {devices/lab_wire.sym} -1250 120 2 0 {name=l34 lab=vss}
N -890 -20 -930 -20 {}
C {devices/lab_wire.sym} -930 -20 0 0 {name=l35 lab=clk_ch_rrl}
N -890 20 -930 20 {}
C {devices/lab_wire.sym} -930 20 0 0 {name=l36 lab=clk_ch_rrl_not}
N -610 -20 -570 -20 {}
C {devices/lab_wire.sym} -570 -20 0 1 {name=l37 lab=sc_n}
N -610 20 -570 20 {}
C {devices/lab_wire.sym} -570 20 0 1 {name=l38 lab=sum_p}
N -750 -80 -750 -120 {}
C {devices/lab_wire.sym} -750 -120 0 1 {name=l39 lab=vdd}
N -750 80 -750 120 {}
C {devices/lab_wire.sym} -750 120 2 0 {name=l40 lab=vss}
N -390 -20 -430 -20 {}
C {devices/lab_wire.sym} -430 -20 0 0 {name=l41 lab=clk_ch_rrl}
N -390 20 -430 20 {}
C {devices/lab_wire.sym} -430 20 0 0 {name=l42 lab=clk_ch_rrl_not}
N -110 -20 -70 -20 {}
C {devices/lab_wire.sym} -70 -20 0 1 {name=l43 lab=sc_p}
N -110 20 -70 20 {}
C {devices/lab_wire.sym} -70 20 0 1 {name=l44 lab=sum_n}
N -250 -80 -250 -120 {}
C {devices/lab_wire.sym} -250 -120 0 1 {name=l45 lab=vdd}
N -250 80 -250 120 {}
C {devices/lab_wire.sym} -250 120 2 0 {name=l46 lab=vss}
N 110 -20 70 -20 {}
C {devices/lab_wire.sym} 70 -20 0 0 {name=l47 lab=clk_phi_1}
N 110 20 70 20 {}
C {devices/lab_wire.sym} 70 20 0 0 {name=l48 lab=clk_phi_2}
N 390 -20 430 -20 {}
C {devices/lab_wire.sym} 430 -20 0 1 {name=l49 lab=oa_inp}
N 390 20 430 20 {}
C {devices/lab_wire.sym} 430 20 0 1 {name=l50 lab=oa_outn}
N 250 -80 250 -120 {}
C {devices/lab_wire.sym} 250 -120 0 1 {name=l51 lab=vdd}
N 250 80 250 120 {}
C {devices/lab_wire.sym} 250 120 2 0 {name=l52 lab=vss}
N 610 -20 570 -20 {}
C {devices/lab_wire.sym} 570 -20 0 0 {name=l53 lab=clk_phi_1}
N 610 20 570 20 {}
C {devices/lab_wire.sym} 570 20 0 0 {name=l54 lab=clk_phi_2}
N 890 -20 930 -20 {}
C {devices/lab_wire.sym} 930 -20 0 1 {name=l55 lab=oa_inn}
N 890 20 930 20 {}
C {devices/lab_wire.sym} 930 20 0 1 {name=l56 lab=oa_outp}
N 750 -80 750 -120 {}
C {devices/lab_wire.sym} 750 -120 0 1 {name=l57 lab=vdd}
N 750 80 750 120 {}
C {devices/lab_wire.sym} 750 120 2 0 {name=l58 lab=vss}
N 1110 -20 1070 -20 {}
C {devices/lab_wire.sym} 1070 -20 0 0 {name=l59 lab=clk_phi_1}
N 1110 20 1070 20 {}
C {devices/lab_wire.sym} 1070 20 0 0 {name=l60 lab=clk_phi_2}
N 1390 -20 1430 -20 {}
C {devices/lab_wire.sym} 1430 -20 0 1 {name=l61 lab=int_p}
N 1390 20 1430 20 {}
C {devices/lab_wire.sym} 1430 20 0 1 {name=l62 lab=oa_outn}
N 1250 -80 1250 -120 {}
C {devices/lab_wire.sym} 1250 -120 0 1 {name=l63 lab=vdd}
N 1250 80 1250 120 {}
C {devices/lab_wire.sym} 1250 120 2 0 {name=l64 lab=vss}
N 1610 -20 1570 -20 {}
C {devices/lab_wire.sym} 1570 -20 0 0 {name=l65 lab=clk_phi_1}
N 1610 20 1570 20 {}
C {devices/lab_wire.sym} 1570 20 0 0 {name=l66 lab=clk_phi_2}
N 1890 -20 1930 -20 {}
C {devices/lab_wire.sym} 1930 -20 0 1 {name=l67 lab=int_n}
N 1890 20 1930 20 {}
C {devices/lab_wire.sym} 1930 20 0 1 {name=l68 lab=oa_outp}
N 1750 -80 1750 -120 {}
C {devices/lab_wire.sym} 1750 -120 0 1 {name=l69 lab=vdd}
N 1750 80 1750 120 {}
C {devices/lab_wire.sym} 1750 120 2 0 {name=l70 lab=vss}
N 2110 -20 2070 -20 {}
C {devices/lab_wire.sym} 2070 -20 0 0 {name=l71 lab=oa_outn}
N 2110 20 2070 20 {}
C {devices/lab_wire.sym} 2070 20 0 0 {name=l72 lab=vb4}
N 2330 -40 2370 -40 {}
C {devices/lab_wire.sym} 2370 -40 0 1 {name=l73 lab=oa_cm_bias}
N 2330 0 2370 0 {}
C {devices/lab_wire.sym} 2370 0 0 1 {name=l74 lab=oa_cm_sense}
N 2330 40 2370 40 {}
C {devices/lab_wire.sym} 2370 40 0 1 {name=l75 lab=oa_cm_tail}
N 2220 -100 2220 -140 {}
C {devices/lab_wire.sym} 2220 -140 0 1 {name=l76 lab=vdd}
N 2550 -20 2510 -20 {}
C {devices/lab_wire.sym} 2510 -20 0 0 {name=l77 lab=oa_outn}
N 2550 20 2510 20 {}
C {devices/lab_wire.sym} 2510 20 0 0 {name=l78 lab=vb4}
N 2770 -40 2810 -40 {}
C {devices/lab_wire.sym} 2810 -40 0 1 {name=l79 lab=oa_cm_bias}
N 2770 0 2810 0 {}
C {devices/lab_wire.sym} 2810 0 0 1 {name=l80 lab=oa_cm_sense}
N 2770 40 2810 40 {}
C {devices/lab_wire.sym} 2810 40 0 1 {name=l81 lab=oa_cm_tail}
N 2660 -100 2660 -140 {}
C {devices/lab_wire.sym} 2660 -140 0 1 {name=l82 lab=vdd}
N 2990 -20 2950 -20 {}
C {devices/lab_wire.sym} 2950 -20 0 0 {name=l83 lab=oa_outp}
N 2990 20 2950 20 {}
C {devices/lab_wire.sym} 2950 20 0 0 {name=l84 lab=vb4}
N 3210 -40 3250 -40 {}
C {devices/lab_wire.sym} 3250 -40 0 1 {name=l85 lab=oa_cm_bias}
N 3210 0 3250 0 {}
C {devices/lab_wire.sym} 3250 0 0 1 {name=l86 lab=oa_cm_sense}
N 3210 40 3250 40 {}
C {devices/lab_wire.sym} 3250 40 0 1 {name=l87 lab=oa_cm_tail}
N 3100 -100 3100 -140 {}
C {devices/lab_wire.sym} 3100 -140 0 1 {name=l88 lab=vdd}
N 3430 -20 3390 -20 {}
C {devices/lab_wire.sym} 3390 -20 0 0 {name=l89 lab=oa_outp}
N 3430 20 3390 20 {}
C {devices/lab_wire.sym} 3390 20 0 0 {name=l90 lab=vb4}
N 3650 -40 3690 -40 {}
C {devices/lab_wire.sym} 3690 -40 0 1 {name=l91 lab=oa_cm_bias}
N 3650 0 3690 0 {}
C {devices/lab_wire.sym} 3690 0 0 1 {name=l92 lab=oa_cm_sense}
N 3650 40 3690 40 {}
C {devices/lab_wire.sym} 3690 40 0 1 {name=l93 lab=oa_cm_tail}
N 3540 -100 3540 -140 {}
C {devices/lab_wire.sym} 3540 -140 0 1 {name=l94 lab=vdd}
N -1760 310 -1760 270 {}
C {devices/lab_wire.sym} -1760 270 0 1 {name=l95 lab=sum_p}
N -1760 370 -1760 410 {}
C {devices/lab_wire.sym} -1760 410 2 0 {name=l96 lab=oa_inp}
N -1540 310 -1540 270 {}
C {devices/lab_wire.sym} -1540 270 0 1 {name=l97 lab=sum_n}
N -1540 370 -1540 410 {}
C {devices/lab_wire.sym} -1540 410 2 0 {name=l98 lab=oa_inn}
N -1320 310 -1320 270 {}
C {devices/lab_wire.sym} -1320 270 0 1 {name=l99 lab=sum_p}
N -1320 370 -1320 410 {}
C {devices/lab_wire.sym} -1320 410 2 0 {name=l100 lab=int_p}
N -1100 310 -1100 270 {}
C {devices/lab_wire.sym} -1100 270 0 1 {name=l101 lab=sum_n}
N -1100 370 -1100 410 {}
C {devices/lab_wire.sym} -1100 410 2 0 {name=l102 lab=int_n}
N -880 310 -880 270 {}
C {devices/lab_wire.sym} -880 270 0 1 {name=l103 lab=int_p}
N -880 370 -880 410 {}
C {devices/lab_wire.sym} -880 410 2 0 {name=l104 lab=int_n}
N -660 310 -660 270 {}
C {devices/lab_wire.sym} -660 270 0 1 {name=l105 lab=voutn}
N -660 370 -660 410 {}
C {devices/lab_wire.sym} -660 410 2 0 {name=l106 lab=voutp}
N -440 310 -440 270 {}
C {devices/lab_wire.sym} -440 270 0 1 {name=l107 lab=vinp}
N -440 370 -440 410 {}
C {devices/lab_wire.sym} -440 410 2 0 {name=l108 lab=sc_p}
N -220 310 -220 270 {}
C {devices/lab_wire.sym} -220 270 0 1 {name=l109 lab=vinn}
N -220 370 -220 410 {}
C {devices/lab_wire.sym} -220 410 2 0 {name=l110 lab=sc_n}
N 0 310 0 270 {}
C {devices/lab_wire.sym} 0 270 0 1 {name=l111 lab=int_p}
N 0 370 0 410 {}
C {devices/lab_wire.sym} 0 410 2 0 {name=l112 lab=int_n}
N 220 310 220 270 {}
C {devices/lab_wire.sym} 220 270 0 1 {name=l113 lab=voutn}
N 220 370 220 410 {}
C {devices/lab_wire.sym} 220 410 2 0 {name=l114 lab=voutp}
N -3760 310 -3760 270 {}
C {devices/lab_wire.sym} -3760 270 0 1 {name=l115 lab=vb1}
N -3760 370 -3760 410 {}
C {devices/lab_wire.sym} -3760 410 2 0 {name=l116 lab=vss}
N -3760 90 -3760 50 {}
C {devices/lab_wire.sym} -3760 50 0 1 {name=l117 lab=vb2}
N -3760 150 -3760 190 {}
C {devices/lab_wire.sym} -3760 190 2 0 {name=l118 lab=vss}
N -3760 -130 -3760 -170 {}
C {devices/lab_wire.sym} -3760 -170 0 1 {name=l119 lab=vb3}
N -3760 -70 -3760 -30 {}
C {devices/lab_wire.sym} -3760 -30 2 0 {name=l120 lab=vss}
N -3760 -350 -3760 -390 {}
C {devices/lab_wire.sym} -3760 -390 0 1 {name=l121 lab=vb4}
N -3760 -290 -3760 -250 {}
C {devices/lab_wire.sym} -3760 -250 2 0 {name=l122 lab=vss}
N 460 310 460 270 {}
C {devices/lab_wire.sym} 460 270 0 1 {name=l123 lab=oa_outn}
N 420 340 380 340 {}
C {devices/lab_wire.sym} 380 340 0 0 {name=l124 lab=vb2}
N 460 370 460 410 {}
C {devices/lab_wire.sym} 460 410 2 0 {name=l125 lab=oa_csrc_n}
N 460 340 500 340 {}
C {devices/lab_wire.sym} 500 340 0 1 {name=l126 lab=vss}
N 680 310 680 270 {}
C {devices/lab_wire.sym} 680 270 0 1 {name=l127 lab=oa_outp}
N 640 340 600 340 {}
C {devices/lab_wire.sym} 600 340 0 0 {name=l128 lab=vb2}
N 680 370 680 410 {}
C {devices/lab_wire.sym} 680 410 2 0 {name=l129 lab=oa_csrc_p}
N 680 340 720 340 {}
C {devices/lab_wire.sym} 720 340 0 1 {name=l130 lab=vss}
N 900 310 900 270 {}
C {devices/lab_wire.sym} 900 270 0 1 {name=l131 lab=oa_cm_sense}
N 860 340 820 340 {}
C {devices/lab_wire.sym} 820 340 0 0 {name=l132 lab=oa_cm_sense}
N 900 370 900 410 {}
C {devices/lab_wire.sym} 900 410 2 0 {name=l133 lab=vss}
N 900 340 940 340 {}
C {devices/lab_wire.sym} 940 340 0 1 {name=l134 lab=vss}
N -90 -310 -90 -270 {}
C {devices/lab_wire.sym} -90 -270 2 0 {name=l135 lab=oa_tail}
N -130 -340 -170 -340 {}
C {devices/lab_wire.sym} -170 -340 0 0 {name=l136 lab=vb3}
N -90 -370 -90 -410 {}
C {devices/lab_wire.sym} -90 -410 0 1 {name=l137 lab=vdd}
N -90 -340 -50 -340 {}
C {devices/lab_wire.sym} -50 -340 0 1 {name=l138 lab=vdd}
N 1120 310 1120 270 {}
C {devices/lab_wire.sym} 1120 270 0 1 {name=l139 lab=sc_n}
N 1080 340 1040 340 {}
C {devices/lab_wire.sym} 1040 340 0 0 {name=l140 lab=clk_phi_2}
N 1120 370 1120 410 {}
C {devices/lab_wire.sym} 1120 410 2 0 {name=l141 lab=vss}
N 1120 340 1160 340 {}
C {devices/lab_wire.sym} 1160 340 0 1 {name=l142 lab=vss}
N 1340 310 1340 270 {}
C {devices/lab_wire.sym} 1340 270 0 1 {name=l143 lab=sc_p}
N 1300 340 1260 340 {}
C {devices/lab_wire.sym} 1260 340 0 0 {name=l144 lab=clk_phi_2}
N 1340 370 1340 410 {}
C {devices/lab_wire.sym} 1340 410 2 0 {name=l145 lab=vss}
N 1340 340 1380 340 {}
C {devices/lab_wire.sym} 1380 340 0 1 {name=l146 lab=vss}
N 1560 370 1560 410 {}
C {devices/lab_wire.sym} 1560 410 2 0 {name=l147 lab=vss}
N 1520 340 1480 340 {}
C {devices/lab_wire.sym} 1480 340 0 0 {name=l148 lab=clk_phi_1}
N 1560 310 1560 270 {}
C {devices/lab_wire.sym} 1560 270 0 1 {name=l149 lab=sc_n}
N 1560 340 1600 340 {}
C {devices/lab_wire.sym} 1600 340 0 1 {name=l150 lab=vdd}
N 1780 370 1780 410 {}
C {devices/lab_wire.sym} 1780 410 2 0 {name=l151 lab=vss}
N 1740 340 1700 340 {}
C {devices/lab_wire.sym} 1700 340 0 0 {name=l152 lab=clk_phi_1}
N 1780 310 1780 270 {}
C {devices/lab_wire.sym} 1780 270 0 1 {name=l153 lab=sc_p}
N 1780 340 1820 340 {}
C {devices/lab_wire.sym} 1820 340 0 1 {name=l154 lab=vdd}
N 130 -310 130 -270 {}
C {devices/lab_wire.sym} 130 -270 2 0 {name=l155 lab=oa_cm_tail}
N 90 -340 50 -340 {}
C {devices/lab_wire.sym} 50 -340 0 0 {name=l156 lab=vb3}
N 130 -370 130 -410 {}
C {devices/lab_wire.sym} 130 -410 0 1 {name=l157 lab=vdd}
N 130 -340 170 -340 {}
C {devices/lab_wire.sym} 170 -340 0 1 {name=l158 lab=vdd}
