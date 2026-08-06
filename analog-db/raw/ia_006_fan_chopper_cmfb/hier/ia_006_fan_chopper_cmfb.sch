v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_006_fan_chopper_cmfb} -4375 -740 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -4115 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_simple_1.sym} -3675 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/tg_pair_cmos_rail_bulk_1.sym} -3205 0 0 0 {name=xtg_pair_cmos_rail_bulk_1}
C {blocks/tg_pair_cmos_rail_bulk_2.sym} -2705 0 0 0 {name=xtg_pair_cmos_rail_bulk_2}
C {blocks/tg_pair_cmos_rail_bulk_3.sym} -2205 0 0 0 {name=xtg_pair_cmos_rail_bulk_3}
C {blocks/dp_nmos_simple_1.sym} -1735 0 0 0 {name=xdp_nmos_simple_1}
C {blocks/tg_pair_cmos_rail_bulk_4.sym} -1265 0 0 0 {name=xtg_pair_cmos_rail_bulk_4}
C {blocks/dp_nmos_simple_2.sym} -795 0 0 0 {name=xdp_nmos_simple_2}
C {blocks/tg_pair_cmos_rail_bulk_5.sym} -325 0 0 0 {name=xtg_pair_cmos_rail_bulk_5}
C {blocks/tg_pair_cmos_rail_bulk_6.sym} 175 0 0 0 {name=xtg_pair_cmos_rail_bulk_6}
C {blocks/tg_pair_cmos_rail_bulk_7.sym} 675 0 0 0 {name=xtg_pair_cmos_rail_bulk_7}
C {blocks/dp_pmos_simple_1.sym} 1145 0 0 0 {name=xdp_pmos_simple_1}
C {blocks/tg_pair_cmos_rail_bulk_8.sym} 1615 0 0 0 {name=xtg_pair_cmos_rail_bulk_8}
C {blocks/tg_pair_cmos_rail_bulk_9.sym} 2115 0 0 0 {name=xtg_pair_cmos_rail_bulk_9}
C {blocks/tg_pair_cmos_rail_bulk_10.sym} 2620 0 0 0 {name=xtg_pair_cmos_rail_bulk_10}
C {blocks/tg_pair_cmos_rail_bulk_11.sym} 3130 0 0 0 {name=xtg_pair_cmos_rail_bulk_11}
C {blocks/tg_pair_cmos_rail_bulk_12.sym} 3640 0 0 0 {name=xtg_pair_cmos_rail_bulk_12}
C {blocks/dp_pmos_simple_2.sym} 4115 0 0 0 {name=xdp_pmos_simple_2}
C {devices/capa_np.sym} -1870 340 0 0 {name=CCM value='c_cm'}
C {devices/capa_np.sym} -1650 340 0 0 {name=CFB1_CORE value='x_dut_cfb1_core_value'}
C {devices/capa_np.sym} -1430 340 0 0 {name=CFB2_CORE value='x_dut_cfb2_core_value'}
C {devices/capa_np.sym} -1210 340 0 0 {name=CIN1_CORE value='x_dut_cin1_core_value'}
C {devices/capa_np.sym} -990 340 0 0 {name=CIN2_CORE value='x_dut_cin2_core_value'}
C {devices/capa_np.sym} -770 340 0 0 {name=CM1_CORE value='x_dut_cm1_core_value'}
C {devices/capa_np.sym} -550 340 0 0 {name=CM2_CORE value='x_dut_cm2_core_value'}
C {devices/res_np.sym} -330 340 0 0 {name=RB1_CORE value='x_dut_rb1_core_value'}
C {devices/res_np.sym} -110 340 0 0 {name=RB2_CORE value='x_dut_rb2_core_value'}
C {devices/res_np.sym} 110 340 0 0 {name=RMN_CMFB value='x_dut_rmn_cmfb_value'}
C {devices/res_np.sym} 330 340 0 0 {name=RMP_CMFB value='x_dut_rmp_cmfb_value'}
C {devices/vsource_np.sym} -4335 340 0 0 {name=VB1_CORE value="dc {vb1_core}"}
C {devices/vsource_np.sym} -4335 120 0 0 {name=VB2_CORE value="dc {vb2_core}"}
C {devices/vsource_np.sym} -4335 -100 0 0 {name=VB3_CORE value="dc {vb3_core}"}
C {devices/vsource_np.sym} -4335 -320 0 0 {name=VB4_CORE value="dc {vb4_core}"}
C {devices/vsource_np.sym} -4335 -540 0 0 {name=VREFCM value="dc {vcm_ref}"}
C {devices/sg13_lv_pmos_np.sym} -660 -340 0 0 {name=M10_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_core_w l=x_dut_xm10_core_l m=x_dut_xm10_core_m}
C {devices/sg13_lv_pmos_np.sym} -440 -340 0 0 {name=M11_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_core_w l=x_dut_xm11_core_l m=x_dut_xm11_core_m}
C {devices/sg13_lv_nmos_np.sym} 550 340 0 0 {name=M12_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_core_w l=x_dut_xm12_core_l m=x_dut_xm12_core_m}
C {devices/sg13_lv_nmos_np.sym} 770 340 0 0 {name=M13_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_core_w l=x_dut_xm13_core_l m=x_dut_xm13_core_m}
C {devices/sg13_lv_nmos_np.sym} 990 340 0 0 {name=M14_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_core_w l=x_dut_xm14_core_l m=x_dut_xm14_core_m}
C {devices/sg13_lv_nmos_np.sym} 1210 340 0 0 {name=M15_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_core_w l=x_dut_xm15_core_l m=x_dut_xm15_core_m}
C {devices/sg13_lv_pmos_np.sym} -220 -340 0 0 {name=M1_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_core_w l=x_dut_xm1_core_l m=x_dut_xm1_core_m}
C {devices/sg13_lv_nmos_np.sym} 1430 340 0 0 {name=M4_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_core_w l=x_dut_xm4_core_l m=x_dut_xm4_core_m}
C {devices/sg13_lv_nmos_np.sym} 1650 340 0 0 {name=M5_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_core_w l=x_dut_xm5_core_l m=x_dut_xm5_core_m}
C {devices/sg13_lv_pmos_np.sym} 0 -340 0 0 {name=M6_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_core_w l=x_dut_xm6_core_l m=x_dut_xm6_core_m}
C {devices/sg13_lv_nmos_np.sym} 1870 340 0 0 {name=M7_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_cmfb_w l=x_dut_xm7_cmfb_l m=x_dut_xm7_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 220 -340 0 0 {name=M7_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_core_w l=x_dut_xm7_core_l m=x_dut_xm7_core_m}
C {devices/sg13_lv_pmos_np.sym} 440 -340 0 0 {name=M8O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8o_w l=x_dut_xm8o_l m=x_dut_xm8o_m}
C {devices/sg13_lv_pmos_np.sym} 660 -340 0 0 {name=M9O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9o_w l=x_dut_xm9o_l m=x_dut_xm9o_m}
N -4005 -20 -3965 -20 {}
C {devices/lab_wire.sym} -3965 -20 0 1 {name=l0 lab=cmfb__bias}
N -4005 20 -3965 20 {}
C {devices/lab_wire.sym} -3965 20 0 1 {name=l1 lab=cmfb__ptail}
N -4115 -80 -4115 -120 {}
C {devices/lab_wire.sym} -4115 -120 0 1 {name=l2 lab=vdd}
N -3565 -20 -3525 -20 {}
C {devices/lab_wire.sym} -3525 -20 0 1 {name=l3 lab=cmfb__mirr}
N -3565 20 -3525 20 {}
C {devices/lab_wire.sym} -3525 20 0 1 {name=l4 lab=vb4o}
N -3675 80 -3675 120 {}
C {devices/lab_wire.sym} -3675 120 2 0 {name=l5 lab=vss}
N -3345 -20 -3385 -20 {}
C {devices/lab_wire.sym} -3385 -20 0 0 {name=l6 lab=clk_chout}
N -3345 20 -3385 20 {}
C {devices/lab_wire.sym} -3385 20 0 0 {name=l7 lab=clk_chout_not}
N -3065 -20 -3025 -20 {}
C {devices/lab_wire.sym} -3025 -20 0 1 {name=l8 lab=core__g2_n}
N -3065 20 -3025 20 {}
C {devices/lab_wire.sym} -3025 20 0 1 {name=l9 lab=core__out1_n}
N -3205 -80 -3205 -120 {}
C {devices/lab_wire.sym} -3205 -120 0 1 {name=l10 lab=vdd}
N -3205 80 -3205 120 {}
C {devices/lab_wire.sym} -3205 120 2 0 {name=l11 lab=vss}
N -2845 -20 -2885 -20 {}
C {devices/lab_wire.sym} -2885 -20 0 0 {name=l12 lab=clk_chout}
N -2845 20 -2885 20 {}
C {devices/lab_wire.sym} -2885 20 0 0 {name=l13 lab=clk_chout_not}
N -2565 -20 -2525 -20 {}
C {devices/lab_wire.sym} -2525 -20 0 1 {name=l14 lab=core__g2_p}
N -2565 20 -2525 20 {}
C {devices/lab_wire.sym} -2525 20 0 1 {name=l15 lab=core__out1_p}
N -2705 -80 -2705 -120 {}
C {devices/lab_wire.sym} -2705 -120 0 1 {name=l16 lab=vdd}
N -2705 80 -2705 120 {}
C {devices/lab_wire.sym} -2705 120 2 0 {name=l17 lab=vss}
N -2345 -20 -2385 -20 {}
C {devices/lab_wire.sym} -2385 -20 0 0 {name=l18 lab=clk_chfb}
N -2345 20 -2385 20 {}
C {devices/lab_wire.sym} -2385 20 0 0 {name=l19 lab=clk_chfb_not}
N -2065 -20 -2025 -20 {}
C {devices/lab_wire.sym} -2025 -20 0 1 {name=l20 lab=core__fbch_p}
N -2065 20 -2025 20 {}
C {devices/lab_wire.sym} -2025 20 0 1 {name=l21 lab=voutp}
N -2205 -80 -2205 -120 {}
C {devices/lab_wire.sym} -2205 -120 0 1 {name=l22 lab=vdd}
N -2205 80 -2205 120 {}
C {devices/lab_wire.sym} -2205 120 2 0 {name=l23 lab=vss}
N -1845 -20 -1885 -20 {}
C {devices/lab_wire.sym} -1885 -20 0 0 {name=l24 lab=clk_chfb}
N -1845 20 -1885 20 {}
C {devices/lab_wire.sym} -1885 20 0 0 {name=l25 lab=clk_chfb_not}
N -1625 -40 -1585 -40 {}
C {devices/lab_wire.sym} -1585 -40 0 1 {name=l26 lab=core__fbch_n}
N -1625 0 -1585 0 {}
C {devices/lab_wire.sym} -1585 0 0 1 {name=l27 lab=core__fbch_p}
N -1625 40 -1585 40 {}
C {devices/lab_wire.sym} -1585 40 0 1 {name=l28 lab=voutp}
N -1735 100 -1735 140 {}
C {devices/lab_wire.sym} -1735 140 2 0 {name=l29 lab=vss}
N -1405 -20 -1445 -20 {}
C {devices/lab_wire.sym} -1445 -20 0 0 {name=l30 lab=clk_chfb}
N -1405 20 -1445 20 {}
C {devices/lab_wire.sym} -1445 20 0 0 {name=l31 lab=clk_chfb_not}
N -1125 -20 -1085 -20 {}
C {devices/lab_wire.sym} -1085 -20 0 1 {name=l32 lab=core__fbch_n}
N -1125 20 -1085 20 {}
C {devices/lab_wire.sym} -1085 20 0 1 {name=l33 lab=voutn}
N -1265 -80 -1265 -120 {}
C {devices/lab_wire.sym} -1265 -120 0 1 {name=l34 lab=vdd}
N -1265 80 -1265 120 {}
C {devices/lab_wire.sym} -1265 120 2 0 {name=l35 lab=vss}
N -905 -20 -945 -20 {}
C {devices/lab_wire.sym} -945 -20 0 0 {name=l36 lab=clk_chfb}
N -905 20 -945 20 {}
C {devices/lab_wire.sym} -945 20 0 0 {name=l37 lab=clk_chfb_not}
N -685 -40 -645 -40 {}
C {devices/lab_wire.sym} -645 -40 0 1 {name=l38 lab=core__fbch_n}
N -685 0 -645 0 {}
C {devices/lab_wire.sym} -645 0 0 1 {name=l39 lab=core__fbch_p}
N -685 40 -645 40 {}
C {devices/lab_wire.sym} -645 40 0 1 {name=l40 lab=voutn}
N -795 100 -795 140 {}
C {devices/lab_wire.sym} -795 140 2 0 {name=l41 lab=vss}
N -465 -20 -505 -20 {}
C {devices/lab_wire.sym} -505 -20 0 0 {name=l42 lab=clk_chin}
N -465 20 -505 20 {}
C {devices/lab_wire.sym} -505 20 0 0 {name=l43 lab=clk_chin_not}
N -185 -20 -145 -20 {}
C {devices/lab_wire.sym} -145 -20 0 1 {name=l44 lab=core__inch_n}
N -185 20 -145 20 {}
C {devices/lab_wire.sym} -145 20 0 1 {name=l45 lab=vinn}
N -325 -80 -325 -120 {}
C {devices/lab_wire.sym} -325 -120 0 1 {name=l46 lab=vdd}
N -325 80 -325 120 {}
C {devices/lab_wire.sym} -325 120 2 0 {name=l47 lab=vss}
N 35 -20 -5 -20 {}
C {devices/lab_wire.sym} -5 -20 0 0 {name=l48 lab=clk_chin}
N 35 20 -5 20 {}
C {devices/lab_wire.sym} -5 20 0 0 {name=l49 lab=clk_chin_not}
N 315 -20 355 -20 {}
C {devices/lab_wire.sym} 355 -20 0 1 {name=l50 lab=core__inch_p}
N 315 20 355 20 {}
C {devices/lab_wire.sym} 355 20 0 1 {name=l51 lab=vinp}
N 175 -80 175 -120 {}
C {devices/lab_wire.sym} 175 -120 0 1 {name=l52 lab=vdd}
N 175 80 175 120 {}
C {devices/lab_wire.sym} 175 120 2 0 {name=l53 lab=vss}
N 535 -20 495 -20 {}
C {devices/lab_wire.sym} 495 -20 0 0 {name=l54 lab=clk_chout}
N 535 20 495 20 {}
C {devices/lab_wire.sym} 495 20 0 0 {name=l55 lab=clk_chout_not}
N 815 -20 855 -20 {}
C {devices/lab_wire.sym} 855 -20 0 1 {name=l56 lab=core__g2_p}
N 815 20 855 20 {}
C {devices/lab_wire.sym} 855 20 0 1 {name=l57 lab=core__out1_n}
N 675 -80 675 -120 {}
C {devices/lab_wire.sym} 675 -120 0 1 {name=l58 lab=vdd}
N 675 80 675 120 {}
C {devices/lab_wire.sym} 675 120 2 0 {name=l59 lab=vss}
N 1035 -20 995 -20 {}
C {devices/lab_wire.sym} 995 -20 0 0 {name=l60 lab=core__vsum_n}
N 1035 20 995 20 {}
C {devices/lab_wire.sym} 995 20 0 0 {name=l61 lab=core__vsum_p}
N 1255 -40 1295 -40 {}
C {devices/lab_wire.sym} 1295 -40 0 1 {name=l62 lab=core__fold_n}
N 1255 0 1295 0 {}
C {devices/lab_wire.sym} 1295 0 0 1 {name=l63 lab=core__fold_p}
N 1255 40 1295 40 {}
C {devices/lab_wire.sym} 1295 40 0 1 {name=l64 lab=core__tail}
N 1145 -100 1145 -140 {}
C {devices/lab_wire.sym} 1145 -140 0 1 {name=l65 lab=vdd}
N 1475 -20 1435 -20 {}
C {devices/lab_wire.sym} 1435 -20 0 0 {name=l66 lab=clk_chout}
N 1475 20 1435 20 {}
C {devices/lab_wire.sym} 1435 20 0 0 {name=l67 lab=clk_chout_not}
N 1755 -20 1795 -20 {}
C {devices/lab_wire.sym} 1795 -20 0 1 {name=l68 lab=core__g2_n}
N 1755 20 1795 20 {}
C {devices/lab_wire.sym} 1795 20 0 1 {name=l69 lab=core__out1_p}
N 1615 -80 1615 -120 {}
C {devices/lab_wire.sym} 1615 -120 0 1 {name=l70 lab=vdd}
N 1615 80 1615 120 {}
C {devices/lab_wire.sym} 1615 120 2 0 {name=l71 lab=vss}
N 1975 -20 1935 -20 {}
C {devices/lab_wire.sym} 1935 -20 0 0 {name=l72 lab=clk_chin}
N 1975 20 1935 20 {}
C {devices/lab_wire.sym} 1935 20 0 0 {name=l73 lab=clk_chin_not}
N 2255 -20 2295 -20 {}
C {devices/lab_wire.sym} 2295 -20 0 1 {name=l74 lab=core__inch_p}
N 2255 20 2295 20 {}
C {devices/lab_wire.sym} 2295 20 0 1 {name=l75 lab=vinn}
N 2115 -80 2115 -120 {}
C {devices/lab_wire.sym} 2115 -120 0 1 {name=l76 lab=vdd}
N 2115 80 2115 120 {}
C {devices/lab_wire.sym} 2115 120 2 0 {name=l77 lab=vss}
N 2475 -20 2435 -20 {}
C {devices/lab_wire.sym} 2435 -20 0 0 {name=l78 lab=clk_chin}
N 2475 20 2435 20 {}
C {devices/lab_wire.sym} 2435 20 0 0 {name=l79 lab=clk_chin_not}
N 2765 -20 2805 -20 {}
C {devices/lab_wire.sym} 2805 -20 0 1 {name=l80 lab=core__inch_n}
N 2765 20 2805 20 {}
C {devices/lab_wire.sym} 2805 20 0 1 {name=l81 lab=vinp}
N 2620 -80 2620 -120 {}
C {devices/lab_wire.sym} 2620 -120 0 1 {name=l82 lab=vdd}
N 2620 80 2620 120 {}
C {devices/lab_wire.sym} 2620 120 2 0 {name=l83 lab=vss}
N 2985 -20 2945 -20 {}
C {devices/lab_wire.sym} 2945 -20 0 0 {name=l84 lab=clk_chfb}
N 2985 20 2945 20 {}
C {devices/lab_wire.sym} 2945 20 0 0 {name=l85 lab=clk_chfb_not}
N 3275 -20 3315 -20 {}
C {devices/lab_wire.sym} 3315 -20 0 1 {name=l86 lab=core__fbch_p}
N 3275 20 3315 20 {}
C {devices/lab_wire.sym} 3315 20 0 1 {name=l87 lab=voutn}
N 3130 -80 3130 -120 {}
C {devices/lab_wire.sym} 3130 -120 0 1 {name=l88 lab=vdd}
N 3130 80 3130 120 {}
C {devices/lab_wire.sym} 3130 120 2 0 {name=l89 lab=vss}
N 3495 -20 3455 -20 {}
C {devices/lab_wire.sym} 3455 -20 0 0 {name=l90 lab=clk_chfb}
N 3495 20 3455 20 {}
C {devices/lab_wire.sym} 3455 20 0 0 {name=l91 lab=clk_chfb_not}
N 3785 -20 3825 -20 {}
C {devices/lab_wire.sym} 3825 -20 0 1 {name=l92 lab=core__fbch_n}
N 3785 20 3825 20 {}
C {devices/lab_wire.sym} 3825 20 0 1 {name=l93 lab=voutp}
N 3640 -80 3640 -120 {}
C {devices/lab_wire.sym} 3640 -120 0 1 {name=l94 lab=vdd}
N 3640 80 3640 120 {}
C {devices/lab_wire.sym} 3640 120 2 0 {name=l95 lab=vss}
N 4005 -20 3965 -20 {}
C {devices/lab_wire.sym} 3965 -20 0 0 {name=l96 lab=cmfb__cm_sense}
N 4005 20 3965 20 {}
C {devices/lab_wire.sym} 3965 20 0 0 {name=l97 lab=vref_cm}
N 4225 -40 4265 -40 {}
C {devices/lab_wire.sym} 4265 -40 0 1 {name=l98 lab=cmfb__mirr}
N 4225 0 4265 0 {}
C {devices/lab_wire.sym} 4265 0 0 1 {name=l99 lab=cmfb__ptail}
N 4225 40 4265 40 {}
C {devices/lab_wire.sym} 4265 40 0 1 {name=l100 lab=vb4o}
N 4115 -100 4115 -140 {}
C {devices/lab_wire.sym} 4115 -140 0 1 {name=l101 lab=vdd}
N -1870 310 -1870 270 {}
C {devices/lab_wire.sym} -1870 270 0 1 {name=l102 lab=vb4o}
N -1870 370 -1870 410 {}
C {devices/lab_wire.sym} -1870 410 2 0 {name=l103 lab=vss}
N -1650 310 -1650 270 {}
C {devices/lab_wire.sym} -1650 270 0 1 {name=l104 lab=core__fbch_p}
N -1650 370 -1650 410 {}
C {devices/lab_wire.sym} -1650 410 2 0 {name=l105 lab=core__vsum_n}
N -1430 310 -1430 270 {}
C {devices/lab_wire.sym} -1430 270 0 1 {name=l106 lab=core__fbch_n}
N -1430 370 -1430 410 {}
C {devices/lab_wire.sym} -1430 410 2 0 {name=l107 lab=core__vsum_p}
N -1210 310 -1210 270 {}
C {devices/lab_wire.sym} -1210 270 0 1 {name=l108 lab=core__vsum_n}
N -1210 370 -1210 410 {}
C {devices/lab_wire.sym} -1210 410 2 0 {name=l109 lab=core__inch_n}
N -990 310 -990 270 {}
C {devices/lab_wire.sym} -990 270 0 1 {name=l110 lab=core__vsum_p}
N -990 370 -990 410 {}
C {devices/lab_wire.sym} -990 410 2 0 {name=l111 lab=core__inch_p}
N -770 310 -770 270 {}
C {devices/lab_wire.sym} -770 270 0 1 {name=l112 lab=core__g2_p}
N -770 370 -770 410 {}
C {devices/lab_wire.sym} -770 410 2 0 {name=l113 lab=voutp}
N -550 310 -550 270 {}
C {devices/lab_wire.sym} -550 270 0 1 {name=l114 lab=core__g2_n}
N -550 370 -550 410 {}
C {devices/lab_wire.sym} -550 410 2 0 {name=l115 lab=voutn}
N -330 310 -330 270 {}
C {devices/lab_wire.sym} -330 270 0 1 {name=l116 lab=core__vsum_n}
N -330 370 -330 410 {}
C {devices/lab_wire.sym} -330 410 2 0 {name=l117 lab=vref}
N -110 310 -110 270 {}
C {devices/lab_wire.sym} -110 270 0 1 {name=l118 lab=core__vsum_p}
N -110 370 -110 410 {}
C {devices/lab_wire.sym} -110 410 2 0 {name=l119 lab=vref}
N 110 310 110 270 {}
C {devices/lab_wire.sym} 110 270 0 1 {name=l120 lab=voutn}
N 110 370 110 410 {}
C {devices/lab_wire.sym} 110 410 2 0 {name=l121 lab=cmfb__cm_sense}
N 330 310 330 270 {}
C {devices/lab_wire.sym} 330 270 0 1 {name=l122 lab=cmfb__cm_sense}
N 330 370 330 410 {}
C {devices/lab_wire.sym} 330 410 2 0 {name=l123 lab=voutp}
N -4335 310 -4335 270 {}
C {devices/lab_wire.sym} -4335 270 0 1 {name=l124 lab=core__vb1}
N -4335 370 -4335 410 {}
C {devices/lab_wire.sym} -4335 410 2 0 {name=l125 lab=vss}
N -4335 90 -4335 50 {}
C {devices/lab_wire.sym} -4335 50 0 1 {name=l126 lab=core__vb2}
N -4335 150 -4335 190 {}
C {devices/lab_wire.sym} -4335 190 2 0 {name=l127 lab=vss}
N -4335 -130 -4335 -170 {}
C {devices/lab_wire.sym} -4335 -170 0 1 {name=l128 lab=core__vb3}
N -4335 -70 -4335 -30 {}
C {devices/lab_wire.sym} -4335 -30 2 0 {name=l129 lab=vss}
N -4335 -350 -4335 -390 {}
C {devices/lab_wire.sym} -4335 -390 0 1 {name=l130 lab=core__vb4}
N -4335 -290 -4335 -250 {}
C {devices/lab_wire.sym} -4335 -250 2 0 {name=l131 lab=vss}
N -4335 -570 -4335 -610 {}
C {devices/lab_wire.sym} -4335 -610 0 1 {name=l132 lab=vref_cm}
N -4335 -510 -4335 -470 {}
C {devices/lab_wire.sym} -4335 -470 2 0 {name=l133 lab=vss}
N -640 -310 -640 -270 {}
C {devices/lab_wire.sym} -640 -270 2 0 {name=l134 lab=core__out1_n}
N -680 -340 -720 -340 {}
C {devices/lab_wire.sym} -720 -340 0 0 {name=l135 lab=core__vb3}
N -640 -370 -640 -410 {}
C {devices/lab_wire.sym} -640 -410 0 1 {name=l136 lab=core__casc_src_n}
N -640 -340 -600 -340 {}
C {devices/lab_wire.sym} -600 -340 0 1 {name=l137 lab=vdd}
N -420 -310 -420 -270 {}
C {devices/lab_wire.sym} -420 -270 2 0 {name=l138 lab=core__out1_p}
N -460 -340 -500 -340 {}
C {devices/lab_wire.sym} -500 -340 0 0 {name=l139 lab=core__vb3}
N -420 -370 -420 -410 {}
C {devices/lab_wire.sym} -420 -410 0 1 {name=l140 lab=core__casc_src_p}
N -420 -340 -380 -340 {}
C {devices/lab_wire.sym} -380 -340 0 1 {name=l141 lab=vdd}
N 570 310 570 270 {}
C {devices/lab_wire.sym} 570 270 0 1 {name=l142 lab=core__out1_p}
N 530 340 490 340 {}
C {devices/lab_wire.sym} 490 340 0 0 {name=l143 lab=core__vb2}
N 570 370 570 410 {}
C {devices/lab_wire.sym} 570 410 2 0 {name=l144 lab=core__fold_p}
N 570 340 610 340 {}
C {devices/lab_wire.sym} 610 340 0 1 {name=l145 lab=vss}
N 790 310 790 270 {}
C {devices/lab_wire.sym} 790 270 0 1 {name=l146 lab=core__out1_n}
N 750 340 710 340 {}
C {devices/lab_wire.sym} 710 340 0 0 {name=l147 lab=core__vb2}
N 790 370 790 410 {}
C {devices/lab_wire.sym} 790 410 2 0 {name=l148 lab=core__fold_n}
N 790 340 830 340 {}
C {devices/lab_wire.sym} 830 340 0 1 {name=l149 lab=vss}
N 1010 310 1010 270 {}
C {devices/lab_wire.sym} 1010 270 0 1 {name=l150 lab=voutp}
N 970 340 930 340 {}
C {devices/lab_wire.sym} 930 340 0 0 {name=l151 lab=core__g2_p}
N 1010 370 1010 410 {}
C {devices/lab_wire.sym} 1010 410 2 0 {name=l152 lab=vss}
N 1010 340 1050 340 {}
C {devices/lab_wire.sym} 1050 340 0 1 {name=l153 lab=vss}
N 1230 310 1230 270 {}
C {devices/lab_wire.sym} 1230 270 0 1 {name=l154 lab=voutn}
N 1190 340 1150 340 {}
C {devices/lab_wire.sym} 1150 340 0 0 {name=l155 lab=core__g2_n}
N 1230 370 1230 410 {}
C {devices/lab_wire.sym} 1230 410 2 0 {name=l156 lab=vss}
N 1230 340 1270 340 {}
C {devices/lab_wire.sym} 1270 340 0 1 {name=l157 lab=vss}
N -200 -310 -200 -270 {}
C {devices/lab_wire.sym} -200 -270 2 0 {name=l158 lab=core__tail}
N -240 -340 -280 -340 {}
C {devices/lab_wire.sym} -280 -340 0 0 {name=l159 lab=core__vb4}
N -200 -370 -200 -410 {}
C {devices/lab_wire.sym} -200 -410 0 1 {name=l160 lab=vdd}
N -200 -340 -160 -340 {}
C {devices/lab_wire.sym} -160 -340 0 1 {name=l161 lab=vdd}
N 1450 310 1450 270 {}
C {devices/lab_wire.sym} 1450 270 0 1 {name=l162 lab=core__fold_p}
N 1410 340 1370 340 {}
C {devices/lab_wire.sym} 1370 340 0 0 {name=l163 lab=core__vb1}
N 1450 370 1450 410 {}
C {devices/lab_wire.sym} 1450 410 2 0 {name=l164 lab=vss}
N 1450 340 1490 340 {}
C {devices/lab_wire.sym} 1490 340 0 1 {name=l165 lab=vss}
N 1670 310 1670 270 {}
C {devices/lab_wire.sym} 1670 270 0 1 {name=l166 lab=core__fold_n}
N 1630 340 1590 340 {}
C {devices/lab_wire.sym} 1590 340 0 0 {name=l167 lab=core__vb1}
N 1670 370 1670 410 {}
C {devices/lab_wire.sym} 1670 410 2 0 {name=l168 lab=vss}
N 1670 340 1710 340 {}
C {devices/lab_wire.sym} 1710 340 0 1 {name=l169 lab=vss}
N 20 -310 20 -270 {}
C {devices/lab_wire.sym} 20 -270 2 0 {name=l170 lab=core__casc_src_n}
N -20 -340 -60 -340 {}
C {devices/lab_wire.sym} -60 -340 0 0 {name=l171 lab=core__vb4}
N 20 -370 20 -410 {}
C {devices/lab_wire.sym} 20 -410 0 1 {name=l172 lab=vdd}
N 20 -340 60 -340 {}
C {devices/lab_wire.sym} 60 -340 0 1 {name=l173 lab=vdd}
N 1890 310 1890 270 {}
C {devices/lab_wire.sym} 1890 270 0 1 {name=l174 lab=cmfb__bias}
N 1850 340 1810 340 {}
C {devices/lab_wire.sym} 1810 340 0 0 {name=l175 lab=cmfb__bias}
N 1890 370 1890 410 {}
C {devices/lab_wire.sym} 1890 410 2 0 {name=l176 lab=vss}
N 1890 340 1930 340 {}
C {devices/lab_wire.sym} 1930 340 0 1 {name=l177 lab=vss}
N 240 -310 240 -270 {}
C {devices/lab_wire.sym} 240 -270 2 0 {name=l178 lab=core__casc_src_p}
N 200 -340 160 -340 {}
C {devices/lab_wire.sym} 160 -340 0 0 {name=l179 lab=core__vb4}
N 240 -370 240 -410 {}
C {devices/lab_wire.sym} 240 -410 0 1 {name=l180 lab=vdd}
N 240 -340 280 -340 {}
C {devices/lab_wire.sym} 280 -340 0 1 {name=l181 lab=vdd}
N 460 -310 460 -270 {}
C {devices/lab_wire.sym} 460 -270 2 0 {name=l182 lab=voutp}
N 420 -340 380 -340 {}
C {devices/lab_wire.sym} 380 -340 0 0 {name=l183 lab=vb4o}
N 460 -370 460 -410 {}
C {devices/lab_wire.sym} 460 -410 0 1 {name=l184 lab=vdd}
N 460 -340 500 -340 {}
C {devices/lab_wire.sym} 500 -340 0 1 {name=l185 lab=vdd}
N 680 -310 680 -270 {}
C {devices/lab_wire.sym} 680 -270 2 0 {name=l186 lab=voutn}
N 640 -340 600 -340 {}
C {devices/lab_wire.sym} 600 -340 0 0 {name=l187 lab=vb4o}
N 680 -370 680 -410 {}
C {devices/lab_wire.sym} 680 -410 0 1 {name=l188 lab=vdd}
N 680 -340 720 -340 {}
C {devices/lab_wire.sym} 720 -340 0 1 {name=l189 lab=vdd}
