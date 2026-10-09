v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_034_fan_chopper_cmfb} -1790 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -1020 780 0 0 {name=CCM value='c_cm'}
C {devices/capa_np.sym} 1100 520 1 0 {name=CM1_CORE value='x_dut_cm1_core_value'}
C {devices/capa_np.sym} 2720 520 1 0 {name=CM2_CORE value='x_dut_cm2_core_value'}
C {devices/res_np.sym} 665 390 1 0 {name=RMN_CMFB value='x_dut_rmn_cmfb_value'}
C {devices/res_np.sym} 1010 390 1 0 {name=RMP_CMFB value='x_dut_rmp_cmfb_value'}
C {devices/vsource_np.sym} -1410 780 0 0 {name=VB1_CORE value="dc \{vb1_core\}" savecurrent=false}
C {devices/vsource_np.sym} -1410 520 0 0 {name=VB2_CORE value="dc \{vb2_core\}" savecurrent=false}
C {devices/vsource_np.sym} -1410 260 0 0 {name=VB3_CORE value="dc \{vb3_core\}" savecurrent=false}
C {devices/vsource_np.sym} -1410 0 0 0 {name=VB4_CORE value="dc \{vb4_core\}" savecurrent=false}
C {devices/vsource_np.sym} -1750 780 0 0 {name=VREFCM value="dc \{vcm_ref\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 25 260 0 1 {name=M10_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_core_w l=x_dut_xm10_core_l m=x_dut_xm10_core_m}
C {devices/sg13_lv_pmos_np.sym} 1100 260 0 0 {name=M11_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_core_w l=x_dut_xm11_core_l m=x_dut_xm11_core_m}
C {devices/sg13_lv_nmos_np.sym} 1390 520 0 0 {name=M12_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_core_w l=x_dut_xm12_core_l m=x_dut_xm12_core_m}
C {devices/sg13_lv_nmos_np.sym} 25 520 0 1 {name=M13_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_core_w l=x_dut_xm13_core_l m=x_dut_xm13_core_m}
C {devices/sg13_lv_nmos_np.sym} 1680 260 0 1 {name=M14_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_core_w l=x_dut_xm14_core_l m=x_dut_xm14_core_m}
C {devices/sg13_lv_nmos_np.sym} 2230 260 0 0 {name=M15_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_core_w l=x_dut_xm15_core_l m=x_dut_xm15_core_m}
C {devices/sg13_lv_nmos_np.sym} 290 520 0 1 {name=M16_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_core_w l=x_dut_xm16_core_l m=x_dut_xm16_core_m}
C {devices/sg13_lv_pmos_np.sym} -240 520 0 1 {name=M17_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_core_w l=x_dut_xm17_core_l m=x_dut_xm17_core_m}
C {devices/sg13_lv_nmos_np.sym} 1660 520 0 0 {name=M18_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_core_w l=x_dut_xm18_core_l m=x_dut_xm18_core_m}
C {devices/sg13_lv_pmos_np.sym} 1925 520 0 0 {name=M19_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_core_w l=x_dut_xm19_core_l m=x_dut_xm19_core_m}
C {devices/sg13_lv_pmos_np.sym} -850 0 0 1 {name=M1_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_cmfb_w l=x_dut_xm1_cmfb_l m=x_dut_xm1_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 845 0 0 0 {name=M1_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_core_w l=x_dut_xm1_core_l m=x_dut_xm1_core_m}
C {devices/sg13_lv_nmos_np.sym} 2190 520 0 0 {name=M20_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_core_w l=x_dut_xm20_core_l m=x_dut_xm20_core_m}
C {devices/sg13_lv_pmos_np.sym} 2455 520 0 0 {name=M21_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_core_w l=x_dut_xm21_core_l m=x_dut_xm21_core_m}
C {devices/sg13_lv_nmos_np.sym} 560 520 0 1 {name=M22_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_core_w l=x_dut_xm22_core_l m=x_dut_xm22_core_m}
C {devices/sg13_lv_pmos_np.sym} 825 520 0 1 {name=M23_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_core_w l=x_dut_xm23_core_l m=x_dut_xm23_core_m}
C {devices/sg13_lv_nmos_np.sym} -1020 520 0 1 {name=M2_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_cmfb_w l=x_dut_xm2_cmfb_l m=x_dut_xm2_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 845 260 0 0 {name=M2_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_core_w l=x_dut_xm2_core_l m=x_dut_xm2_core_m}
C {devices/sg13_lv_pmos_np.sym} 580 0 0 0 {name=M3_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_cmfb_w l=x_dut_xm3_cmfb_l m=x_dut_xm3_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 310 260 0 0 {name=M3_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_core_w l=x_dut_xm3_core_l m=x_dut_xm3_core_m}
C {devices/sg13_lv_pmos_np.sym} -680 260 0 0 {name=M4_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_cmfb_w l=x_dut_xm4_cmfb_l m=x_dut_xm4_cmfb_m}
C {devices/sg13_lv_nmos_np.sym} 580 780 0 0 {name=M4_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_core_w l=x_dut_xm4_core_l m=x_dut_xm4_core_m}
C {devices/sg13_lv_pmos_np.sym} -1020 260 0 1 {name=M5_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_cmfb_w l=x_dut_xm5_cmfb_l m=x_dut_xm5_cmfb_m}
C {devices/sg13_lv_nmos_np.sym} 845 780 0 0 {name=M5_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_core_w l=x_dut_xm5_core_l m=x_dut_xm5_core_m}
C {devices/sg13_lv_nmos_np.sym} -680 520 0 0 {name=M6_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_cmfb_w l=x_dut_xm6_cmfb_l m=x_dut_xm6_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 25 0 0 1 {name=M6_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_core_w l=x_dut_xm6_core_l m=x_dut_xm6_core_m}
C {devices/sg13_lv_nmos_np.sym} 580 260 0 0 {name=M7_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_cmfb_w l=x_dut_xm7_cmfb_l m=x_dut_xm7_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 1100 0 0 0 {name=M7_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_core_w l=x_dut_xm7_core_l m=x_dut_xm7_core_m}
C {devices/sg13_lv_pmos_np.sym} 1680 0 0 1 {name=M8O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8o_w l=x_dut_xm8o_l m=x_dut_xm8o_m}
C {devices/sg13_lv_pmos_np.sym} 2230 0 0 0 {name=M9O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9o_w l=x_dut_xm9o_l m=x_dut_xm9o_m}
N -1750 690 -1750 750 {}
N -1750 810 -1750 870 {}
N -1410 -90 -1410 -30 {}
N -1410 30 -1410 90 {}
N -1410 170 -1410 230 {}
N -1410 290 -1410 350 {}
N -1410 430 -1410 490 {}
N -1410 550 -1410 610 {}
N -1410 690 -1410 750 {}
N -1410 810 -1410 870 {}
N -1100 260 -1100 354 {}
N -1100 520 -1100 614 {}
N -1040 200 -1040 230 {}
N -1040 290 -1040 490 {}
N -1040 550 -1040 920 {}
N -1020 460 -1020 750 {}
N -1020 810 -1020 920 {}
N -930 0 -930 94 {}
N -870 -140 -870 -30 {}
N -870 30 -870 200 {}
N -800 -60 -800 0 {}
N -790 260 -790 390 {}
N -700 450 -700 520 {}
N -660 200 -660 230 {}
N -660 290 -660 490 {}
N -660 550 -660 920 {}
N -600 260 -600 354 {}
N -600 520 -600 614 {}
N -320 520 -320 614 {}
N -260 460 -260 490 {}
N -260 550 -260 610 {}
N -220 520 -220 920 {}
N -55 0 -55 94 {}
N -55 260 -55 354 {}
N -55 520 -55 614 {}
N 5 -140 5 -30 {}
N 5 30 5 230 {}
N 5 290 5 460 {}
N 5 460 5 490 {}
N 5 550 5 610 {}
N 210 520 210 614 {}
N 270 460 270 490 {}
N 270 550 270 610 {}
N 310 -140 310 520 {}
N 330 200 330 230 {}
N 330 290 330 350 {}
N 390 260 390 354 {}
N 530 720 530 780 {}
N 540 460 540 490 {}
N 560 -60 560 70 {}
N 560 190 560 260 {}
N 580 520 580 920 {}
N 600 -140 600 -30 {}
N 600 30 600 70 {}
N 600 170 600 230 {}
N 600 290 600 350 {}
N 600 690 600 750 {}
N 600 810 600 920 {}
N 605 330 605 390 {}
N 660 0 660 94 {}
N 660 260 660 354 {}
N 660 780 660 874 {}
N 745 520 745 614 {}
N 795 720 795 780 {}
N 805 460 805 490 {}
N 845 -140 845 520 {}
N 865 -140 865 -30 {}
N 865 30 865 230 {}
N 865 290 865 350 {}
N 865 690 865 750 {}
N 865 810 865 920 {}
N 925 0 925 94 {}
N 925 260 925 354 {}
N 925 780 925 874 {}
N 980 390 980 450 {}
N 1070 330 1070 390 {}
N 1120 -140 1120 -30 {}
N 1120 30 1120 230 {}
N 1120 290 1120 350 {}
N 1130 520 1130 580 {}
N 1180 0 1180 94 {}
N 1180 260 1180 354 {}
N 1220 520 1220 550 {}
N 1410 320 1410 490 {}
N 1410 550 1410 610 {}
N 1470 520 1470 614 {}
N 1600 0 1600 94 {}
N 1600 260 1600 354 {}
N 1640 -140 1640 520 {}
N 1660 -140 1660 -30 {}
N 1660 30 1660 230 {}
N 1660 290 1660 920 {}
N 1680 460 1680 490 {}
N 1680 550 1680 610 {}
N 1730 0 1730 440 {}
N 1740 520 1740 614 {}
N 1905 520 1905 920 {}
N 1945 460 1945 490 {}
N 1945 550 1945 610 {}
N 2005 520 2005 614 {}
N 2170 520 2170 920 {}
N 2180 260 2180 580 {}
N 2210 460 2210 490 {}
N 2210 550 2210 580 {}
N 2250 -140 2250 -30 {}
N 2250 30 2250 230 {}
N 2250 290 2250 920 {}
N 2270 520 2270 614 {}
N 2310 0 2310 94 {}
N 2310 260 2310 354 {}
N 2435 -140 2435 520 {}
N 2475 460 2475 490 {}
N 2475 550 2475 580 {}
N 2535 520 2535 614 {}
N 2660 200 2660 520 {}
N 2840 520 2840 580 {}
N -1810 -140 3075 -140 {}
N -800 -60 560 -60 {}
N -930 0 -870 0 {}
N -830 0 -770 0 {}
N -55 0 5 0 {}
N 45 0 105 0 {}
N 600 0 660 0 {}
N 765 0 825 0 {}
N 865 0 925 0 {}
N 1020 0 1080 0 {}
N 1120 0 1180 0 {}
N 1600 0 1660 0 {}
N 1700 0 2210 0 {}
N 2250 0 2310 0 {}
N 560 70 600 70 {}
N 560 190 600 190 {}
N -1040 200 -660 200 {}
N 270 200 865 200 {}
N 2250 200 2660 200 {}
N -1100 260 -1040 260 {}
N -1000 260 -940 260 {}
N -790 260 -700 260 {}
N -660 260 -600 260 {}
N -55 260 5 260 {}
N 45 260 105 260 {}
N 200 260 290 260 {}
N 330 260 390 260 {}
N 600 260 660 260 {}
N 735 260 825 260 {}
N 865 260 925 260 {}
N 1020 260 1080 260 {}
N 1120 260 1180 260 {}
N 1600 260 1660 260 {}
N 1700 260 1760 260 {}
N 2150 260 2210 260 {}
N 2250 260 2310 260 {}
N 1120 320 1410 320 {}
N 605 330 1070 330 {}
N -790 390 635 390 {}
N 695 390 785 390 {}
N 950 390 980 390 {}
N 1040 390 1070 390 {}
N -1040 440 1730 440 {}
N -700 450 -660 450 {}
N -1040 460 -1020 460 {}
N -260 460 805 460 {}
N 1410 460 2475 460 {}
N -1100 520 -1040 520 {}
N -1000 520 -940 520 {}
N -660 520 -600 520 {}
N -320 520 -260 520 {}
N -55 520 5 520 {}
N 45 520 105 520 {}
N 210 520 270 520 {}
N 745 520 805 520 {}
N 1040 520 1070 520 {}
N 1130 520 1220 520 {}
N 1310 520 1370 520 {}
N 1410 520 1470 520 {}
N 1680 520 1740 520 {}
N 1945 520 2005 520 {}
N 2210 520 2270 520 {}
N 2475 520 2535 520 {}
N 2660 520 2690 520 {}
N 2750 520 2840 520 {}
N 480 550 1220 550 {}
N 2180 580 2840 580 {}
N 530 720 795 720 {}
N 500 780 560 780 {}
N 600 780 660 780 {}
N 795 780 825 780 {}
N 865 780 925 780 {}
N -1810 920 3075 920 {}
C {devices/lab_wire.sym} -770 0 0 1 {name=l0 lab=cmfb__bias}
C {devices/lab_wire.sym} 600 170 0 1 {name=l1 lab=cmfb__bias}
C {devices/lab_wire.sym} -760 260 0 0 {name=l2 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} -940 520 0 1 {name=l3 lab=cmfb__mirr}
C {devices/lab_wire.sym} -660 350 2 0 {name=l4 lab=cmfb__mirr}
C {devices/lab_wire.sym} -870 90 2 0 {name=l5 lab=cmfb__ptail}
C {devices/lab_wire.sym} 5 90 2 0 {name=l6 lab=core__casc_src_n}
C {devices/lab_wire.sym} 1120 90 2 0 {name=l7 lab=core__casc_src_p}
C {devices/lab_wire.sym} 5 610 2 0 {name=l8 lab=core__fold_n}
C {devices/lab_wire.sym} 330 350 2 0 {name=l9 lab=core__fold_n}
C {devices/lab_wire.sym} 865 690 0 1 {name=l10 lab=core__fold_n}
C {devices/lab_wire.sym} 600 690 0 1 {name=l11 lab=core__fold_p}
C {devices/lab_wire.sym} 865 350 2 0 {name=l12 lab=core__fold_p}
C {devices/lab_wire.sym} 1410 610 2 0 {name=l13 lab=core__fold_p}
C {devices/lab_wire.sym} -260 610 2 0 {name=l14 lab=core__g2_n}
C {devices/lab_wire.sym} 270 610 2 0 {name=l15 lab=core__g2_n}
C {devices/lab_wire.sym} 2150 260 0 0 {name=l16 lab=core__g2_n}
C {devices/lab_wire.sym} 1130 580 2 0 {name=l17 lab=core__g2_p}
C {devices/lab_wire.sym} 1680 610 2 0 {name=l18 lab=core__g2_p}
C {devices/lab_wire.sym} 1760 260 0 1 {name=l19 lab=core__g2_p}
C {devices/lab_wire.sym} 1945 610 2 0 {name=l20 lab=core__g2_p}
C {devices/lab_wire.sym} 5 350 2 0 {name=l21 lab=core__out1_n}
C {devices/lab_wire.sym} 1120 350 2 0 {name=l22 lab=core__out1_p}
C {devices/lab_wire.sym} 865 90 2 0 {name=l23 lab=core__tail}
C {devices/lab_wire.sym} 500 780 0 0 {name=l24 lab=core__vb1}
C {devices/lab_wire.sym} 105 520 0 1 {name=l25 lab=core__vb2}
C {devices/lab_wire.sym} 1310 520 0 0 {name=l26 lab=core__vb2}
C {devices/lab_wire.sym} 105 260 0 1 {name=l27 lab=core__vb3}
C {devices/lab_wire.sym} 1020 260 0 0 {name=l28 lab=core__vb3}
C {devices/lab_wire.sym} 105 0 0 1 {name=l29 lab=core__vb4}
C {devices/lab_wire.sym} 765 0 0 0 {name=l30 lab=core__vb4}
C {devices/lab_wire.sym} 1020 0 0 0 {name=l31 lab=core__vb4}
C {devices/lab_wire.sym} 1760 0 0 1 {name=l32 lab=vb4o}
C {devices/lab_wire.sym} 2250 90 2 0 {name=l33 lab=voutn}
C {devices/lab_wire.sym} 980 450 2 0 {name=l34 lab=voutp}
C {devices/lab_wire.sym} 1660 90 2 0 {name=l35 lab=voutp}
C {devices/lab_wire.sym} -940 260 0 1 {name=l36 lab=vref_cm}
C {devices/lab_wire.sym} -55 354 2 0 {name=l37 lab=vdd}
C {devices/lab_wire.sym} 1180 354 2 0 {name=l38 lab=vdd}
C {devices/lab_wire.sym} -320 614 2 0 {name=l39 lab=vdd}
C {devices/lab_wire.sym} 2005 614 2 0 {name=l40 lab=vdd}
C {devices/lab_wire.sym} -930 94 2 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} 925 94 2 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} 2535 614 2 0 {name=l43 lab=vdd}
C {devices/lab_wire.sym} 745 614 2 0 {name=l44 lab=vdd}
C {devices/lab_wire.sym} 925 354 2 0 {name=l45 lab=vdd}
C {devices/lab_wire.sym} 660 94 2 0 {name=l46 lab=vdd}
C {devices/lab_wire.sym} 390 354 2 0 {name=l47 lab=vdd}
C {devices/lab_wire.sym} -600 354 2 0 {name=l48 lab=vdd}
C {devices/lab_wire.sym} -1100 354 2 0 {name=l49 lab=vdd}
C {devices/lab_wire.sym} -55 94 2 0 {name=l50 lab=vdd}
C {devices/lab_wire.sym} 1180 94 2 0 {name=l51 lab=vdd}
C {devices/lab_wire.sym} 1600 94 2 0 {name=l52 lab=vdd}
C {devices/lab_wire.sym} 2310 94 2 0 {name=l53 lab=vdd}
C {devices/lab_wire.sym} 1470 614 2 0 {name=l54 lab=vss}
C {devices/lab_wire.sym} -55 614 2 0 {name=l55 lab=vss}
C {devices/lab_wire.sym} 1600 354 2 0 {name=l56 lab=vss}
C {devices/lab_wire.sym} 2310 354 2 0 {name=l57 lab=vss}
C {devices/lab_wire.sym} 210 614 2 0 {name=l58 lab=vss}
C {devices/lab_wire.sym} 1740 614 2 0 {name=l59 lab=vss}
C {devices/lab_wire.sym} 2270 614 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} 540 520 0 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} -1100 614 2 0 {name=l62 lab=vss}
C {devices/lab_wire.sym} 660 874 2 0 {name=l63 lab=vss}
C {devices/lab_wire.sym} 925 874 2 0 {name=l64 lab=vss}
C {devices/lab_wire.sym} -600 614 2 0 {name=l65 lab=vss}
C {devices/lab_wire.sym} 660 354 2 0 {name=l66 lab=vss}
C {devices/lab_wire.sym} -1410 870 2 0 {name=l67 lab=vss}
C {devices/lab_wire.sym} -1410 610 2 0 {name=l68 lab=vss}
C {devices/lab_wire.sym} -1410 350 2 0 {name=l69 lab=vss}
C {devices/lab_wire.sym} -1410 90 2 0 {name=l70 lab=vss}
C {devices/lab_wire.sym} -1750 870 2 0 {name=l71 lab=vss}
C {devices/lab_wire.sym} -1410 690 0 1 {name=l72 lab=core__vb1}
C {devices/lab_wire.sym} -1410 430 0 1 {name=l73 lab=core__vb2}
C {devices/lab_wire.sym} -1410 170 0 1 {name=l74 lab=core__vb3}
C {devices/lab_wire.sym} -1410 -90 0 1 {name=l75 lab=core__vb4}
C {devices/lab_wire.sym} -1750 690 0 1 {name=l76 lab=vref_cm}
C {devices/lab_wire.sym} 600 350 2 0 {name=l77 lab=vss}
C {devices/ipin.sym} 200 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} 735 260 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -1810 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1810 920 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 1040 520 0 0 {name=p4 lab=voutp}
C {devices/opin.sym} 785 390 0 0 {name=p5 lab=voutn}
B 8 -1426 -78 1156 78 {fill=0}
T {PMOS Simple Current Mirror} -1426 -96 0 0 0.3 0.3 {layer=8}
B 10 -1596 442 -104 598 {fill=0}
T {NMOS Simple Current Mirror} -1596 424 0 0 0.3 0.3 {layer=10}
B 12 240 182 1421 338 {fill=0}
T {PMOS Differential Pair} 240 164 0 0 0.3 0.3 {layer=12}
B 21 -1596 182 -104 338 {fill=0}
T {PMOS Differential Pair} -1596 164 0 0 0.3 0.3 {layer=21}
