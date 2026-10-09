v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_035_fan_chopper_cmfb_dual} -2365 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -1190 780 0 0 {name=CCM_S1 value='c_cm_s1'}
C {devices/capa_np.sym} 1910 520 1 0 {name=CM1_CORE value='x_dut_cm1_core_value'}
C {devices/capa_np.sym} 3530 520 1 0 {name=CM2_CORE value='x_dut_cm2_core_value'}
C {devices/res_np.sym} 965 390 1 0 {name=RMN_CMFB_OUT value='x_dut_rmn_cmfb_out_value'}
C {devices/res_np.sym} 115 520 0 0 {name=RMN_CMFB_S1 value='x_dut_rmn_cmfb_s1_value'}
C {devices/res_np.sym} 1585 390 1 0 {name=RMP_CMFB_OUT value='x_dut_rmp_cmfb_out_value'}
C {devices/res_np.sym} 1600 520 1 0 {name=RMP_CMFB_S1 value='x_dut_rmp_cmfb_s1_value'}
C {devices/vsource_np.sym} -1985 780 0 0 {name=VB1_CORE value="dc \{vb1_core\}" savecurrent=false}
C {devices/vsource_np.sym} -1985 520 0 0 {name=VB2_CORE value="dc \{vb2_core\}" savecurrent=false}
C {devices/vsource_np.sym} -1985 260 0 0 {name=VB3_CORE value="dc \{vb3_core\}" savecurrent=false}
C {devices/vsource_np.sym} -1985 0 0 0 {name=VREFOUT value="dc \{vcm_ref\}" savecurrent=false}
C {devices/vsource_np.sym} -2325 780 0 0 {name=VREFS1 value="dc \{vcm_ref_stg1\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 115 260 0 1 {name=M10_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_core_w l=x_dut_xm10_core_l m=x_dut_xm10_core_m}
C {devices/sg13_lv_pmos_np.sym} 1790 260 0 0 {name=M11_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_core_w l=x_dut_xm11_core_l m=x_dut_xm11_core_m}
C {devices/sg13_lv_nmos_np.sym} 2200 520 0 0 {name=M12_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_core_w l=x_dut_xm12_core_l m=x_dut_xm12_core_m}
C {devices/sg13_lv_nmos_np.sym} 610 520 0 1 {name=M13_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_core_w l=x_dut_xm13_core_l m=x_dut_xm13_core_m}
C {devices/sg13_lv_nmos_np.sym} 2235 260 0 1 {name=M14_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_core_w l=x_dut_xm14_core_l m=x_dut_xm14_core_m}
C {devices/sg13_lv_nmos_np.sym} 2775 260 0 0 {name=M15_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_core_w l=x_dut_xm15_core_l m=x_dut_xm15_core_m}
C {devices/sg13_lv_nmos_np.sym} -45 520 0 1 {name=M16_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_core_w l=x_dut_xm16_core_l m=x_dut_xm16_core_m}
C {devices/sg13_lv_pmos_np.sym} 875 520 0 1 {name=M17_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_core_w l=x_dut_xm17_core_l m=x_dut_xm17_core_m}
C {devices/sg13_lv_nmos_np.sym} 2470 520 0 0 {name=M18_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_core_w l=x_dut_xm18_core_l m=x_dut_xm18_core_m}
C {devices/sg13_lv_pmos_np.sym} 2735 520 0 0 {name=M19_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_core_w l=x_dut_xm19_core_l m=x_dut_xm19_core_m}
C {devices/sg13_lv_pmos_np.sym} -1190 0 0 1 {name=M1_CMFB_OUT model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_cmfb_out_w l=x_dut_xm1_cmfb_out_l m=x_dut_xm1_cmfb_out_m}
C {devices/sg13_lv_pmos_np.sym} -850 0 0 1 {name=M1_CMFB_S1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_cmfb_s1_w l=x_dut_xm1_cmfb_s1_l m=x_dut_xm1_cmfb_s1_m}
C {devices/sg13_lv_pmos_np.sym} 620 0 0 1 {name=M1_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_core_w l=x_dut_xm1_core_l m=x_dut_xm1_core_m}
C {devices/sg13_lv_nmos_np.sym} 3000 520 0 0 {name=M20_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_core_w l=x_dut_xm20_core_l m=x_dut_xm20_core_m}
C {devices/sg13_lv_pmos_np.sym} 3265 520 0 0 {name=M21_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_core_w l=x_dut_xm21_core_l m=x_dut_xm21_core_m}
C {devices/sg13_lv_nmos_np.sym} 1140 520 0 1 {name=M22_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_core_w l=x_dut_xm22_core_l m=x_dut_xm22_core_m}
C {devices/sg13_lv_pmos_np.sym} 1410 520 0 1 {name=M23_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_core_w l=x_dut_xm23_core_l m=x_dut_xm23_core_m}
C {devices/sg13_lv_nmos_np.sym} -1530 520 0 1 {name=M2_CMFB_OUT model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_cmfb_out_w l=x_dut_xm2_cmfb_out_l m=x_dut_xm2_cmfb_out_m}
C {devices/sg13_lv_nmos_np.sym} -1190 520 0 1 {name=M2_CMFB_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_cmfb_s1_w l=x_dut_xm2_cmfb_s1_l m=x_dut_xm2_cmfb_s1_m}
C {devices/sg13_lv_pmos_np.sym} 620 260 0 1 {name=M2_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_core_w l=x_dut_xm2_core_l m=x_dut_xm2_core_m}
C {devices/sg13_lv_pmos_np.sym} 895 0 0 0 {name=M3_CMFB_OUT model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_cmfb_out_w l=x_dut_xm3_cmfb_out_l m=x_dut_xm3_cmfb_out_m}
C {devices/sg13_lv_pmos_np.sym} 1450 0 0 0 {name=M3_CMFB_S1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_cmfb_s1_w l=x_dut_xm3_cmfb_s1_l m=x_dut_xm3_cmfb_s1_m}
C {devices/sg13_lv_pmos_np.sym} 3215 260 0 1 {name=M3_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_core_w l=x_dut_xm3_core_l m=x_dut_xm3_core_m}
C {devices/sg13_lv_pmos_np.sym} -850 260 0 1 {name=M4_CMFB_OUT model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_cmfb_out_w l=x_dut_xm4_cmfb_out_l m=x_dut_xm4_cmfb_out_m}
C {devices/sg13_lv_pmos_np.sym} -510 260 0 0 {name=M4_CMFB_S1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_cmfb_s1_w l=x_dut_xm4_cmfb_s1_l m=x_dut_xm4_cmfb_s1_m}
C {devices/sg13_lv_nmos_np.sym} 620 780 0 1 {name=M4_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_core_w l=x_dut_xm4_core_l m=x_dut_xm4_core_m}
C {devices/sg13_lv_pmos_np.sym} -1530 260 0 1 {name=M5_CMFB_OUT model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_cmfb_out_w l=x_dut_xm5_cmfb_out_l m=x_dut_xm5_cmfb_out_m}
C {devices/sg13_lv_pmos_np.sym} -1190 260 0 1 {name=M5_CMFB_S1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_cmfb_s1_w l=x_dut_xm5_cmfb_s1_l m=x_dut_xm5_cmfb_s1_m}
C {devices/sg13_lv_nmos_np.sym} 885 780 0 1 {name=M5_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_core_w l=x_dut_xm5_core_l m=x_dut_xm5_core_m}
C {devices/sg13_lv_nmos_np.sym} -850 520 0 1 {name=M6_CMFB_OUT model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_cmfb_out_w l=x_dut_xm6_cmfb_out_l m=x_dut_xm6_cmfb_out_m}
C {devices/sg13_lv_nmos_np.sym} -510 520 0 0 {name=M6_CMFB_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_cmfb_s1_w l=x_dut_xm6_cmfb_s1_l m=x_dut_xm6_cmfb_s1_m}
C {devices/sg13_lv_pmos_np.sym} 115 0 0 1 {name=M6_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_core_w l=x_dut_xm6_core_l m=x_dut_xm6_core_m}
C {devices/sg13_lv_nmos_np.sym} 895 260 0 0 {name=M7_CMFB_OUT model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_cmfb_out_w l=x_dut_xm7_cmfb_out_l m=x_dut_xm7_cmfb_out_m}
C {devices/sg13_lv_nmos_np.sym} 1450 260 0 0 {name=M7_CMFB_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_cmfb_s1_w l=x_dut_xm7_cmfb_s1_l m=x_dut_xm7_cmfb_s1_m}
C {devices/sg13_lv_pmos_np.sym} 1790 0 0 0 {name=M7_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_core_w l=x_dut_xm7_core_l m=x_dut_xm7_core_m}
C {devices/sg13_lv_pmos_np.sym} 2235 0 0 1 {name=M8O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8o_w l=x_dut_xm8o_l m=x_dut_xm8o_m}
C {devices/sg13_lv_pmos_np.sym} 2775 0 0 0 {name=M9O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9o_w l=x_dut_xm9o_l m=x_dut_xm9o_m}
N -2325 690 -2325 750 {}
N -2325 810 -2325 870 {}
N -1985 -90 -1985 -30 {}
N -1985 30 -1985 90 {}
N -1985 170 -1985 230 {}
N -1985 290 -1985 350 {}
N -1985 430 -1985 490 {}
N -1985 550 -1985 610 {}
N -1985 690 -1985 750 {}
N -1985 810 -1985 870 {}
N -1610 60 -1610 200 {}
N -1610 260 -1610 354 {}
N -1610 520 -1610 614 {}
N -1550 200 -1550 230 {}
N -1550 290 -1550 490 {}
N -1550 550 -1550 920 {}
N -1270 0 -1270 94 {}
N -1270 260 -1270 354 {}
N -1270 520 -1270 614 {}
N -1210 -140 -1210 -30 {}
N -1210 30 -1210 90 {}
N -1210 170 -1210 230 {}
N -1210 290 -1210 350 {}
N -1210 430 -1210 490 {}
N -1210 550 -1210 920 {}
N -1190 460 -1190 750 {}
N -1190 810 -1190 920 {}
N -930 60 -930 200 {}
N -930 290 -930 460 {}
N -930 520 -930 614 {}
N -870 -140 -870 -30 {}
N -870 30 -870 90 {}
N -870 170 -870 230 {}
N -870 290 -870 350 {}
N -870 450 -870 490 {}
N -870 550 -870 920 {}
N -860 260 -860 390 {}
N -830 450 -830 520 {}
N -550 290 -550 460 {}
N -530 450 -530 520 {}
N -490 200 -490 230 {}
N -490 290 -490 350 {}
N -490 450 -490 490 {}
N -490 550 -490 920 {}
N -430 260 -430 354 {}
N -430 520 -430 614 {}
N -125 520 -125 614 {}
N -65 430 -65 490 {}
N -65 550 -65 610 {}
N -25 -140 -25 520 {}
N 35 0 35 94 {}
N 35 260 35 354 {}
N 95 -140 95 -30 {}
N 95 30 95 230 {}
N 95 290 95 350 {}
N 115 460 115 490 {}
N 115 550 115 610 {}
N 165 -60 165 0 {}
N 530 520 530 614 {}
N 540 0 540 94 {}
N 540 260 540 354 {}
N 540 780 540 874 {}
N 590 460 590 490 {}
N 590 550 590 610 {}
N 600 -140 600 -30 {}
N 600 30 600 230 {}
N 600 290 600 350 {}
N 600 720 600 750 {}
N 600 810 600 920 {}
N 670 -60 670 0 {}
N 670 780 670 840 {}
N 795 520 795 614 {}
N 805 780 805 874 {}
N 855 60 855 230 {}
N 855 460 855 490 {}
N 855 550 855 610 {}
N 865 690 865 750 {}
N 865 810 865 920 {}
N 875 0 875 70 {}
N 875 190 875 260 {}
N 895 520 895 920 {}
N 905 330 905 390 {}
N 915 -140 915 -30 {}
N 915 30 915 70 {}
N 915 190 915 230 {}
N 915 290 915 920 {}
N 935 780 935 840 {}
N 975 0 975 94 {}
N 975 260 975 354 {}
N 995 390 995 450 {}
N 1120 460 1120 490 {}
N 1160 520 1160 920 {}
N 1330 520 1330 614 {}
N 1390 460 1390 490 {}
N 1390 550 1390 610 {}
N 1430 0 1430 70 {}
N 1430 190 1430 260 {}
N 1430 520 1430 580 {}
N 1470 -140 1470 -30 {}
N 1470 30 1470 70 {}
N 1470 170 1470 230 {}
N 1470 290 1470 920 {}
N 1530 0 1530 94 {}
N 1530 260 1530 354 {}
N 1570 520 1570 580 {}
N 1630 520 1630 580 {}
N 1645 330 1645 390 {}
N 1810 -140 1810 -30 {}
N 1810 30 1810 90 {}
N 1810 170 1810 230 {}
N 1810 290 1810 350 {}
N 1870 0 1870 94 {}
N 1870 260 1870 354 {}
N 1940 520 1940 580 {}
N 1970 520 1970 610 {}
N 2155 0 2155 94 {}
N 2155 260 2155 354 {}
N 2215 -140 2215 -30 {}
N 2215 30 2215 60 {}
N 2215 170 2215 230 {}
N 2215 290 2215 920 {}
N 2220 430 2220 490 {}
N 2220 550 2220 610 {}
N 2280 550 2280 720 {}
N 2450 -140 2450 520 {}
N 2490 460 2490 490 {}
N 2490 550 2490 610 {}
N 2550 520 2550 614 {}
N 2715 520 2715 920 {}
N 2755 460 2755 490 {}
N 2755 550 2755 610 {}
N 2795 -140 2795 -30 {}
N 2795 30 2795 90 {}
N 2795 170 2795 230 {}
N 2795 290 2795 920 {}
N 2815 520 2815 614 {}
N 2855 0 2855 94 {}
N 2855 260 2855 354 {}
N 2980 520 2980 920 {}
N 3020 460 3020 490 {}
N 3020 550 3020 580 {}
N 3080 520 3080 614 {}
N 3135 260 3135 354 {}
N 3195 170 3195 230 {}
N 3195 290 3195 350 {}
N 3245 -140 3245 520 {}
N 3285 460 3285 490 {}
N 3285 550 3285 580 {}
N 3345 520 3345 614 {}
N 3560 520 3560 580 {}
N 3650 520 3650 580 {}
N -2385 -140 3885 -140 {}
N 165 -60 670 -60 {}
N -1270 0 -1210 0 {}
N -1170 0 -1110 0 {}
N -830 0 -770 0 {}
N 35 0 95 0 {}
N 135 0 195 0 {}
N 540 0 600 0 {}
N 640 0 670 0 {}
N 815 0 875 0 {}
N 915 0 975 0 {}
N 1370 0 1430 0 {}
N 1470 0 1530 0 {}
N 1710 0 1770 0 {}
N 1810 0 1870 0 {}
N 2155 0 2215 0 {}
N 2255 0 2755 0 {}
N 2795 0 2855 0 {}
N -1610 60 -1210 60 {}
N -930 60 -870 60 {}
N 855 60 915 60 {}
N 875 70 915 70 {}
N 1430 70 1470 70 {}
N 875 190 915 190 {}
N 1430 190 1470 190 {}
N -1610 200 -1550 200 {}
N -930 200 -490 200 {}
N 855 230 915 230 {}
N -1610 260 -1550 260 {}
N -1510 260 -1450 260 {}
N -1270 260 -1210 260 {}
N -1170 260 -1110 260 {}
N -860 260 -770 260 {}
N -590 260 -530 260 {}
N -490 260 -430 260 {}
N 35 260 95 260 {}
N 135 260 195 260 {}
N 540 260 600 260 {}
N 640 260 670 260 {}
N 915 260 975 260 {}
N 1470 260 1530 260 {}
N 1710 260 1770 260 {}
N 1810 260 1870 260 {}
N 2155 260 2215 260 {}
N 2255 260 2315 260 {}
N 2695 260 2755 260 {}
N 2795 260 2855 260 {}
N 3135 260 3195 260 {}
N 3235 260 3265 260 {}
N -930 290 -870 290 {}
N -550 290 -490 290 {}
N 905 330 1645 330 {}
N -860 390 935 390 {}
N 995 390 1025 390 {}
N 1495 390 1555 390 {}
N 1615 390 1645 390 {}
N -870 450 -830 450 {}
N -530 450 -490 450 {}
N -1210 460 -1190 460 {}
N -930 460 -870 460 {}
N -550 460 -490 460 {}
N -65 460 1390 460 {}
N 2220 460 3285 460 {}
N -1610 520 -1550 520 {}
N -1510 520 -1450 520 {}
N -1270 520 -1210 520 {}
N -1170 520 -1110 520 {}
N -930 520 -870 520 {}
N -490 520 -430 520 {}
N -125 520 -65 520 {}
N 530 520 590 520 {}
N 630 520 690 520 {}
N 795 520 855 520 {}
N 1330 520 1390 520 {}
N 1540 520 1570 520 {}
N 1630 520 1660 520 {}
N 1820 520 1880 520 {}
N 1940 520 1970 520 {}
N 2120 520 2180 520 {}
N 2490 520 2550 520 {}
N 2755 520 2815 520 {}
N 3020 520 3080 520 {}
N 3285 520 3345 520 {}
N 3470 520 3500 520 {}
N 3560 520 3650 520 {}
N 1060 550 1390 550 {}
N 2220 550 2280 550 {}
N 3020 580 3650 580 {}
N 1390 610 1970 610 {}
N 600 720 2280 720 {}
N 540 780 600 780 {}
N 640 780 700 780 {}
N 805 780 865 780 {}
N 905 780 935 780 {}
N 670 840 935 840 {}
N -2385 920 3885 920 {}
C {devices/lab_wire.sym} -1110 0 0 1 {name=l0 lab=cmfb_out__bias}
C {devices/lab_wire.sym} 815 0 0 0 {name=l1 lab=cmfb_out__bias}
C {devices/lab_wire.sym} -770 260 0 1 {name=l2 lab=cmfb_out__cm_sense}
C {devices/lab_wire.sym} -1450 520 0 1 {name=l3 lab=cmfb_out__mirr}
C {devices/lab_wire.sym} -870 350 2 0 {name=l4 lab=cmfb_out__mirr}
C {devices/lab_wire.sym} -1210 90 2 0 {name=l5 lab=cmfb_out__ptail}
C {devices/lab_wire.sym} -870 170 0 1 {name=l6 lab=cmfb_out__ptail}
C {devices/lab_wire.sym} -770 0 0 1 {name=l7 lab=cmfb_s1__bias}
C {devices/lab_wire.sym} 1370 0 0 0 {name=l8 lab=cmfb_s1__bias}
C {devices/lab_wire.sym} 1470 170 0 1 {name=l9 lab=cmfb_s1__bias}
C {devices/lab_wire.sym} -590 260 0 0 {name=l10 lab=cmfb_s1__cm_sense}
C {devices/lab_wire.sym} 115 610 2 0 {name=l11 lab=cmfb_s1__cm_sense}
C {devices/lab_wire.sym} 1630 580 2 0 {name=l12 lab=cmfb_s1__cm_sense}
C {devices/lab_wire.sym} -1110 520 0 1 {name=l13 lab=cmfb_s1__mirr}
C {devices/lab_wire.sym} -490 350 2 0 {name=l14 lab=cmfb_s1__mirr}
C {devices/lab_wire.sym} -1210 170 0 1 {name=l15 lab=cmfb_s1__ptail}
C {devices/lab_wire.sym} -870 90 2 0 {name=l16 lab=cmfb_s1__ptail}
C {devices/lab_wire.sym} 95 90 2 0 {name=l17 lab=core__casc_src_n}
C {devices/lab_wire.sym} 1810 90 2 0 {name=l18 lab=core__casc_src_p}
C {devices/lab_wire.sym} 1810 170 0 1 {name=l19 lab=core__casc_src_p}
C {devices/lab_wire.sym} 590 610 2 0 {name=l20 lab=core__fold_n}
C {devices/lab_wire.sym} 865 690 0 1 {name=l21 lab=core__fold_n}
C {devices/lab_wire.sym} 3195 350 2 0 {name=l22 lab=core__fold_n}
C {devices/lab_wire.sym} 600 350 2 0 {name=l23 lab=core__fold_p}
C {devices/lab_wire.sym} 2220 610 2 0 {name=l24 lab=core__fold_p}
C {devices/lab_wire.sym} -65 610 2 0 {name=l25 lab=core__g2_n}
C {devices/lab_wire.sym} 855 610 2 0 {name=l26 lab=core__g2_n}
C {devices/lab_wire.sym} 2695 260 0 0 {name=l27 lab=core__g2_n}
C {devices/lab_wire.sym} 3560 580 2 0 {name=l28 lab=core__g2_n}
C {devices/lab_wire.sym} 1940 580 2 0 {name=l29 lab=core__g2_p}
C {devices/lab_wire.sym} 2315 260 0 1 {name=l30 lab=core__g2_p}
C {devices/lab_wire.sym} 2490 610 2 0 {name=l31 lab=core__g2_p}
C {devices/lab_wire.sym} 2755 610 2 0 {name=l32 lab=core__g2_p}
C {devices/lab_wire.sym} 600 90 2 0 {name=l33 lab=core__tail}
C {devices/lab_wire.sym} 3195 170 0 1 {name=l34 lab=core__tail}
C {devices/lab_wire.sym} 700 780 0 1 {name=l35 lab=core__vb1}
C {devices/lab_wire.sym} 690 520 0 1 {name=l36 lab=core__vb2}
C {devices/lab_wire.sym} 2120 520 0 0 {name=l37 lab=core__vb2}
C {devices/lab_wire.sym} 195 260 0 1 {name=l38 lab=core__vb3}
C {devices/lab_wire.sym} 1710 260 0 0 {name=l39 lab=core__vb3}
C {devices/lab_wire.sym} -65 430 0 1 {name=l40 lab=stg1_n}
C {devices/lab_wire.sym} 95 350 2 0 {name=l41 lab=stg1_n}
C {devices/lab_wire.sym} 1570 580 2 0 {name=l42 lab=stg1_p}
C {devices/lab_wire.sym} 1810 350 2 0 {name=l43 lab=stg1_p}
C {devices/lab_wire.sym} 2220 430 0 1 {name=l44 lab=stg1_p}
C {devices/lab_wire.sym} -1210 350 2 0 {name=l45 lab=vb4_ctl}
C {devices/lab_wire.sym} -1210 430 0 1 {name=l46 lab=vb4_ctl}
C {devices/lab_wire.sym} 195 0 0 1 {name=l47 lab=vb4_ctl}
C {devices/lab_wire.sym} 1710 0 0 0 {name=l48 lab=vb4_ctl}
C {devices/lab_wire.sym} -1550 350 2 0 {name=l49 lab=vb4o}
C {devices/lab_wire.sym} 2315 0 0 1 {name=l50 lab=vb4o}
C {devices/lab_wire.sym} 995 450 2 0 {name=l51 lab=voutn}
C {devices/lab_wire.sym} 2795 90 2 0 {name=l52 lab=voutn}
C {devices/lab_wire.sym} 2795 170 0 1 {name=l53 lab=voutn}
C {devices/lab_wire.sym} 1495 390 0 0 {name=l54 lab=voutp}
C {devices/lab_wire.sym} 1820 520 0 0 {name=l55 lab=voutp}
C {devices/lab_wire.sym} 2215 170 0 1 {name=l56 lab=voutp}
C {devices/lab_wire.sym} -1450 260 0 1 {name=l57 lab=vref_out}
C {devices/lab_wire.sym} -1110 260 0 1 {name=l58 lab=vref_s1}
C {devices/lab_wire.sym} 35 354 2 0 {name=l59 lab=vdd}
C {devices/lab_wire.sym} 1870 354 2 0 {name=l60 lab=vdd}
C {devices/lab_wire.sym} 795 614 2 0 {name=l61 lab=vdd}
C {devices/lab_wire.sym} 2815 614 2 0 {name=l62 lab=vdd}
C {devices/lab_wire.sym} -1270 94 2 0 {name=l63 lab=vdd}
C {devices/lab_wire.sym} -870 0 0 0 {name=l64 lab=vdd}
C {devices/lab_wire.sym} 540 94 2 0 {name=l65 lab=vdd}
C {devices/lab_wire.sym} 3345 614 2 0 {name=l66 lab=vdd}
C {devices/lab_wire.sym} 1330 614 2 0 {name=l67 lab=vdd}
C {devices/lab_wire.sym} 540 354 2 0 {name=l68 lab=vdd}
C {devices/lab_wire.sym} 975 94 2 0 {name=l69 lab=vdd}
C {devices/lab_wire.sym} 1530 94 2 0 {name=l70 lab=vdd}
C {devices/lab_wire.sym} 3135 354 2 0 {name=l71 lab=vdd}
C {devices/lab_wire.sym} -870 260 0 0 {name=l72 lab=vdd}
C {devices/lab_wire.sym} -430 354 2 0 {name=l73 lab=vdd}
C {devices/lab_wire.sym} -1610 354 2 0 {name=l74 lab=vdd}
C {devices/lab_wire.sym} -1270 354 2 0 {name=l75 lab=vdd}
C {devices/lab_wire.sym} 35 94 2 0 {name=l76 lab=vdd}
C {devices/lab_wire.sym} 1870 94 2 0 {name=l77 lab=vdd}
C {devices/lab_wire.sym} 2155 94 2 0 {name=l78 lab=vdd}
C {devices/lab_wire.sym} 2855 94 2 0 {name=l79 lab=vdd}
C {devices/lab_wire.sym} 2220 520 0 0 {name=l80 lab=vss}
C {devices/lab_wire.sym} 530 614 2 0 {name=l81 lab=vss}
C {devices/lab_wire.sym} 2155 354 2 0 {name=l82 lab=vss}
C {devices/lab_wire.sym} 2855 354 2 0 {name=l83 lab=vss}
C {devices/lab_wire.sym} -125 614 2 0 {name=l84 lab=vss}
C {devices/lab_wire.sym} 2550 614 2 0 {name=l85 lab=vss}
C {devices/lab_wire.sym} 3080 614 2 0 {name=l86 lab=vss}
C {devices/lab_wire.sym} 1120 520 0 0 {name=l87 lab=vss}
C {devices/lab_wire.sym} -1610 614 2 0 {name=l88 lab=vss}
C {devices/lab_wire.sym} -1270 614 2 0 {name=l89 lab=vss}
C {devices/lab_wire.sym} 540 874 2 0 {name=l90 lab=vss}
C {devices/lab_wire.sym} 805 874 2 0 {name=l91 lab=vss}
C {devices/lab_wire.sym} -930 614 2 0 {name=l92 lab=vss}
C {devices/lab_wire.sym} -430 614 2 0 {name=l93 lab=vss}
C {devices/lab_wire.sym} 975 354 2 0 {name=l94 lab=vss}
C {devices/lab_wire.sym} 1530 354 2 0 {name=l95 lab=vss}
C {devices/lab_wire.sym} -1985 870 2 0 {name=l96 lab=vss}
C {devices/lab_wire.sym} -1985 610 2 0 {name=l97 lab=vss}
C {devices/lab_wire.sym} -1985 350 2 0 {name=l98 lab=vss}
C {devices/lab_wire.sym} -1985 90 2 0 {name=l99 lab=vss}
C {devices/lab_wire.sym} -2325 870 2 0 {name=l100 lab=vss}
C {devices/lab_wire.sym} -1985 690 0 1 {name=l101 lab=core__vb1}
C {devices/lab_wire.sym} -1985 430 0 1 {name=l102 lab=core__vb2}
C {devices/lab_wire.sym} -1985 170 0 1 {name=l103 lab=core__vb3}
C {devices/lab_wire.sym} -1985 -90 0 1 {name=l104 lab=vref_out}
C {devices/lab_wire.sym} -2325 690 0 1 {name=l105 lab=vref_s1}
C {devices/lab_wire.sym} 1430 580 2 0 {name=l106 lab=vdd}
C {devices/ipin.sym} 670 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} 3265 260 0 0 {name=p1 lab=vinn}
C {devices/iopin.sym} -2385 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -2385 920 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 2215 60 0 0 {name=p4 lab=voutp}
C {devices/opin.sym} 3470 520 0 0 {name=p5 lab=voutn}
B 8 -1862 -78 1567 78 {fill=0}
T {PMOS Simple Current Mirror} -1862 -96 0 0 0.3 0.3 {layer=8}
B 10 -1498 -78 2098 78 {fill=0}
T {PMOS Simple Current Mirror} -1498 -96 0 0 0.3 0.3 {layer=10}
B 12 -2202 442 -780 598 {fill=0}
T {NMOS Simple Current Mirror} -2202 424 0 0 0.3 0.3 {layer=12}
B 21 -1838 442 138 598 {fill=0}
T {NMOS Simple Current Mirror} -1838 424 0 0 0.3 0.3 {layer=21}
B 15 44 182 3285 338 {fill=0}
T {PMOS Differential Pair} 44 164 0 0 0.3 0.3 {layer=15}
B 13 -2202 182 -780 338 {fill=0}
T {PMOS Differential Pair} -2202 164 0 0 0.3 0.3 {layer=13}
B 18 -1838 182 138 338 {fill=0}
T {PMOS Differential Pair} -1838 164 0 0 0.3 0.3 {layer=18}
