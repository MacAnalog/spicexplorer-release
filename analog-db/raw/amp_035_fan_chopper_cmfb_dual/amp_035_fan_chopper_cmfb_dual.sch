v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_035_fan_chopper_cmfb_dual} -2250 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -1190 780 0 0 {name=CCM_S1 value='c_cm_s1'}
C {devices/capa_np.sym} 1610 520 1 0 {name=CM1_CORE value='x_dut_cm1_core_value'}
C {devices/capa_np.sym} 3015 520 1 0 {name=CM2_CORE value='x_dut_cm2_core_value'}
C {devices/res_np.sym} 775 390 1 0 {name=RMN_CMFB_OUT value=…b_out_value'}
C {devices/res_np.sym} 40 520 0 0 {name=RMN_CMFB_S1 value=…fb_s1_value'}
C {devices/res_np.sym} 1315 390 1 0 {name=RMP_CMFB_OUT value=…b_out_value'}
C {devices/res_np.sym} 1330 520 1 0 {name=RMP_CMFB_S1 value=…fb_s1_value'}
C {devices/vsource_np.sym} -1870 780 0 0 {name=VB1_CORE value="dc {vb1_core}"}
C {devices/vsource_np.sym} -1870 520 0 0 {name=VB2_CORE value="dc {vb2_core}"}
C {devices/vsource_np.sym} -1870 260 0 0 {name=VB3_CORE value="dc {vb3_core}"}
C {devices/vsource_np.sym} -1870 0 0 0 {name=VREFOUT value="dc {vcm_ref}"}
C {devices/vsource_np.sym} -2210 780 0 0 {name=VREFS1 value="dc {vcm_ref_stg1}"}
C {devices/sg13_lv_pmos_np.sym} 40 260 0 1 {name=M10_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_core_w l=x_dut_xm10_core_l m=x_dut_xm10_core_m}
C {devices/sg13_lv_pmos_np.sym} 1520 260 0 0 {name=M11_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_core_w l=x_dut_xm11_core_l m=x_dut_xm11_core_m}
C {devices/sg13_lv_nmos_np.sym} 1860 520 0 0 {name=M12_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_core_w l=x_dut_xm12_core_l m=x_dut_xm12_core_m}
C {devices/sg13_lv_nmos_np.sym} 460 520 0 1 {name=M13_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_core_w l=x_dut_xm13_core_l m=x_dut_xm13_core_m}
C {devices/sg13_lv_nmos_np.sym} 1895 260 0 1 {name=M14_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_core_w l=x_dut_xm14_core_l m=x_dut_xm14_core_m}
C {devices/sg13_lv_nmos_np.sym} 2355 260 0 0 {name=M15_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_core_w l=x_dut_xm15_core_l m=x_dut_xm15_core_m}
C {devices/sg13_lv_nmos_np.sym} -120 520 0 1 {name=M16_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_core_w l=x_dut_xm16_core_l m=x_dut_xm16_core_m}
C {devices/sg13_lv_pmos_np.sym} 685 520 0 1 {name=M17_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_core_w l=x_dut_xm17_core_l m=x_dut_xm17_core_m}
C {devices/sg13_lv_nmos_np.sym} 2090 520 0 0 {name=M18_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_core_w l=x_dut_xm18_core_l m=x_dut_xm18_core_m}
C {devices/sg13_lv_pmos_np.sym} 2315 520 0 0 {name=M19_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_core_w l=x_dut_xm19_core_l m=x_dut_xm19_core_m}
C {devices/sg13_lv_pmos_np.sym} -1190 0 0 1 {name=M1_CMFB_OUT model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_cmfb_out_w l=x_dut_xm1_cmfb_out_l m=x_dut_xm1_cmfb_out_m}
C {devices/sg13_lv_pmos_np.sym} -850 0 0 1 {name=M1_CMFB_S1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_cmfb_s1_w l=x_dut_xm1_cmfb_s1_l m=x_dut_xm1_cmfb_s1_m}
C {devices/sg13_lv_pmos_np.sym} 470 0 0 1 {name=M1_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_core_w l=x_dut_xm1_core_l m=x_dut_xm1_core_m}
C {devices/sg13_lv_nmos_np.sym} 2545 520 0 0 {name=M20_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_core_w l=x_dut_xm20_core_l m=x_dut_xm20_core_m}
C {devices/sg13_lv_pmos_np.sym} 2770 520 0 0 {name=M21_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_core_w l=x_dut_xm21_core_l m=x_dut_xm21_core_m}
C {devices/sg13_lv_nmos_np.sym} 915 520 0 1 {name=M22_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_core_w l=x_dut_xm22_core_l m=x_dut_xm22_core_m}
C {devices/sg13_lv_pmos_np.sym} 1140 520 0 1 {name=M23_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_core_w l=x_dut_xm23_core_l m=x_dut_xm23_core_m}
C {devices/sg13_lv_nmos_np.sym} -1530 520 0 1 {name=M2_CMFB_OUT model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_cmfb_out_w l=x_dut_xm2_cmfb_out_l m=x_dut_xm2_cmfb_out_m}
C {devices/sg13_lv_nmos_np.sym} -1190 520 0 1 {name=M2_CMFB_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_cmfb_s1_w l=x_dut_xm2_cmfb_s1_l m=x_dut_xm2_cmfb_s1_m}
C {devices/sg13_lv_pmos_np.sym} 470 260 0 1 {name=M2_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_core_w l=x_dut_xm2_core_l m=x_dut_xm2_core_m}
C {devices/sg13_lv_pmos_np.sym} 705 0 0 0 {name=M3_CMFB_OUT model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_cmfb_out_w l=x_dut_xm3_cmfb_out_l m=x_dut_xm3_cmfb_out_m}
C {devices/sg13_lv_pmos_np.sym} 1180 0 0 0 {name=M3_CMFB_S1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_cmfb_s1_w l=x_dut_xm3_cmfb_s1_l m=x_dut_xm3_cmfb_s1_m}
C {devices/sg13_lv_pmos_np.sym} 2720 260 0 1 {name=M3_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_core_w l=x_dut_xm3_core_l m=x_dut_xm3_core_m}
C {devices/sg13_lv_pmos_np.sym} -850 260 0 1 {name=M4_CMFB_OUT model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_cmfb_out_w l=x_dut_xm4_cmfb_out_l m=x_dut_xm4_cmfb_out_m}
C {devices/sg13_lv_pmos_np.sym} -510 260 0 0 {name=M4_CMFB_S1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_cmfb_s1_w l=x_dut_xm4_cmfb_s1_l m=x_dut_xm4_cmfb_s1_m}
C {devices/sg13_lv_nmos_np.sym} 470 780 0 1 {name=M4_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_core_w l=x_dut_xm4_core_l m=x_dut_xm4_core_m}
C {devices/sg13_lv_pmos_np.sym} -1530 260 0 1 {name=M5_CMFB_OUT model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_cmfb_out_w l=x_dut_xm5_cmfb_out_l m=x_dut_xm5_cmfb_out_m}
C {devices/sg13_lv_pmos_np.sym} -1190 260 0 1 {name=M5_CMFB_S1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_cmfb_s1_w l=x_dut_xm5_cmfb_s1_l m=x_dut_xm5_cmfb_s1_m}
C {devices/sg13_lv_nmos_np.sym} 695 780 0 1 {name=M5_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_core_w l=x_dut_xm5_core_l m=x_dut_xm5_core_m}
C {devices/sg13_lv_nmos_np.sym} -850 520 0 1 {name=M6_CMFB_OUT model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_cmfb_out_w l=x_dut_xm6_cmfb_out_l m=x_dut_xm6_cmfb_out_m}
C {devices/sg13_lv_nmos_np.sym} -510 520 0 0 {name=M6_CMFB_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_cmfb_s1_w l=x_dut_xm6_cmfb_s1_l m=x_dut_xm6_cmfb_s1_m}
C {devices/sg13_lv_pmos_np.sym} 40 0 0 1 {name=M6_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_core_w l=x_dut_xm6_core_l m=x_dut_xm6_core_m}
C {devices/sg13_lv_nmos_np.sym} 705 260 0 0 {name=M7_CMFB_OUT model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_cmfb_out_w l=x_dut_xm7_cmfb_out_l m=x_dut_xm7_cmfb_out_m}
C {devices/sg13_lv_nmos_np.sym} 1180 260 0 0 {name=M7_CMFB_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_cmfb_s1_w l=x_dut_xm7_cmfb_s1_l m=x_dut_xm7_cmfb_s1_m}
C {devices/sg13_lv_pmos_np.sym} 1520 0 0 0 {name=M7_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_core_w l=x_dut_xm7_core_l m=x_dut_xm7_core_m}
C {devices/sg13_lv_pmos_np.sym} 1895 0 0 1 {name=M8O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8o_w l=x_dut_xm8o_l m=x_dut_xm8o_m}
C {devices/sg13_lv_pmos_np.sym} 2355 0 0 0 {name=M9O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9o_w l=x_dut_xm9o_l m=x_dut_xm9o_m}
N -2210 690 -2210 750 {}
N -2210 810 -2210 870 {}
N -1870 -90 -1870 -30 {}
N -1870 30 -1870 90 {}
N -1870 170 -1870 230 {}
N -1870 290 -1870 350 {}
N -1870 430 -1870 490 {}
N -1870 550 -1870 610 {}
N -1870 690 -1870 750 {}
N -1870 810 -1870 870 {}
N -1610 260 -1610 354 {}
N -1610 520 -1610 614 {}
N -1550 170 -1550 230 {}
N -1550 290 -1550 490 {}
N -1550 550 -1550 920 {}
N -1510 260 -1510 320 {}
N -1510 520 -1510 580 {}
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
N -1170 0 -1170 60 {}
N -1170 260 -1170 320 {}
N -1170 520 -1170 580 {}
N -930 0 -930 94 {}
N -930 260 -930 354 {}
N -930 520 -930 614 {}
N -870 -140 -870 -30 {}
N -870 30 -870 90 {}
N -870 170 -870 230 {}
N -870 290 -870 350 {}
N -870 430 -870 490 {}
N -870 550 -870 920 {}
N -830 450 -830 520 {}
N -530 450 -530 520 {}
N -490 170 -490 230 {}
N -490 290 -490 350 {}
N -490 430 -490 490 {}
N -490 550 -490 920 {}
N -430 260 -430 354 {}
N -430 520 -430 614 {}
N -200 520 -200 614 {}
N -140 430 -140 490 {}
N -140 550 -140 610 {}
N -100 -140 -100 520 {}
N -40 0 -40 94 {}
N -40 260 -40 354 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 350 {}
N 40 460 40 490 {}
N 40 550 40 610 {}
N 380 520 380 614 {}
N 390 0 390 94 {}
N 390 260 390 354 {}
N 390 780 390 874 {}
N 440 460 440 490 {}
N 440 550 440 610 {}
N 450 -140 450 -30 {}
N 450 30 450 230 {}
N 450 290 450 350 {}
N 450 690 450 750 {}
N 450 810 450 920 {}
N 480 520 480 580 {}
N 490 780 490 840 {}
N 605 520 605 614 {}
N 615 780 615 874 {}
N 665 460 665 490 {}
N 665 550 665 610 {}
N 675 690 675 750 {}
N 675 810 675 920 {}
N 685 0 685 70 {}
N 685 190 685 260 {}
N 705 520 705 920 {}
N 715 260 715 390 {}
N 725 -140 725 -30 {}
N 725 30 725 70 {}
N 725 170 725 230 {}
N 725 290 725 920 {}
N 785 0 785 94 {}
N 785 260 785 354 {}
N 805 390 805 450 {}
N 835 520 835 614 {}
N 895 460 895 490 {}
N 895 550 895 610 {}
N 935 520 935 920 {}
N 1060 520 1060 614 {}
N 1120 460 1120 490 {}
N 1120 550 1120 610 {}
N 1160 0 1160 70 {}
N 1160 190 1160 260 {}
N 1160 520 1160 580 {}
N 1200 -140 1200 -30 {}
N 1200 30 1200 70 {}
N 1200 170 1200 230 {}
N 1200 290 1200 920 {}
N 1260 0 1260 94 {}
N 1260 260 1260 354 {}
N 1300 520 1300 580 {}
N 1345 390 1345 450 {}
N 1360 520 1360 580 {}
N 1500 -60 1500 0 {}
N 1500 200 1500 260 {}
N 1540 -140 1540 -30 {}
N 1540 30 1540 90 {}
N 1540 170 1540 230 {}
N 1540 290 1540 350 {}
N 1550 390 1550 520 {}
N 1580 460 1580 520 {}
N 1600 0 1600 94 {}
N 1600 260 1600 354 {}
N 1640 520 1640 580 {}
N 1815 0 1815 94 {}
N 1815 260 1815 354 {}
N 1840 460 1840 520 {}
N 1875 -140 1875 -30 {}
N 1875 30 1875 90 {}
N 1875 170 1875 230 {}
N 1875 290 1875 920 {}
N 1880 430 1880 490 {}
N 1880 550 1880 610 {}
N 1940 520 1940 614 {}
N 2070 -140 2070 520 {}
N 2110 460 2110 490 {}
N 2110 550 2110 610 {}
N 2170 520 2170 614 {}
N 2295 520 2295 920 {}
N 2335 460 2335 490 {}
N 2335 550 2335 610 {}
N 2375 -140 2375 -30 {}
N 2375 30 2375 90 {}
N 2375 170 2375 230 {}
N 2375 290 2375 920 {}
N 2395 520 2395 614 {}
N 2435 0 2435 94 {}
N 2435 260 2435 354 {}
N 2525 520 2525 920 {}
N 2565 460 2565 490 {}
N 2565 550 2565 610 {}
N 2625 520 2625 614 {}
N 2640 260 2640 354 {}
N 2700 170 2700 230 {}
N 2700 290 2700 720 {}
N 2750 -140 2750 520 {}
N 2790 460 2790 490 {}
N 2790 550 2790 580 {}
N 2850 520 2850 614 {}
N 2955 200 2955 520 {}
N 2985 460 2985 520 {}
N 3045 520 3045 580 {}
N 3075 260 3075 520 {}
N -2270 -140 3295 -140 {}
N -1270 0 -1210 0 {}
N -1170 0 -1140 0 {}
N -930 0 -870 0 {}
N -830 0 -770 0 {}
N -40 0 20 0 {}
N 60 0 120 0 {}
N 390 0 450 0 {}
N 490 0 550 0 {}
N 625 0 685 0 {}
N 725 0 785 0 {}
N 1100 0 1160 0 {}
N 1200 0 1260 0 {}
N 1470 0 1500 0 {}
N 1540 0 1600 0 {}
N 1815 0 1875 0 {}
N 1915 0 2335 0 {}
N 2375 0 2435 0 {}
N 685 70 725 70 {}
N 1160 70 1200 70 {}
N 685 190 725 190 {}
N 1160 190 1200 190 {}
N -1610 260 -1550 260 {}
N -1510 260 -1480 260 {}
N -1270 260 -1210 260 {}
N -1170 260 -1140 260 {}
N -930 260 -870 260 {}
N -830 260 -770 260 {}
N -590 260 -530 260 {}
N -490 260 -430 260 {}
N -40 260 20 260 {}
N 60 260 120 260 {}
N 390 260 450 260 {}
N 490 260 550 260 {}
N 725 260 785 260 {}
N 1200 260 1260 260 {}
N 1470 260 1500 260 {}
N 1540 260 1600 260 {}
N 1815 260 1875 260 {}
N 1915 260 1975 260 {}
N 2275 260 2335 260 {}
N 2375 260 2435 260 {}
N 2640 260 2700 260 {}
N 2740 260 2800 260 {}
N 685 390 745 390 {}
N 805 390 835 390 {}
N 1225 390 1285 390 {}
N 1345 390 1375 390 {}
N -870 450 -830 450 {}
N -530 450 -490 450 {}
N -1210 460 -1190 460 {}
N -140 460 1120 460 {}
N 1880 460 2790 460 {}
N -1610 520 -1550 520 {}
N -1510 520 -1480 520 {}
N -1270 520 -1210 520 {}
N -1170 520 -1140 520 {}
N -930 520 -870 520 {}
N -490 520 -430 520 {}
N -200 520 -140 520 {}
N 380 520 440 520 {}
N 480 520 510 520 {}
N 605 520 665 520 {}
N 835 520 895 520 {}
N 1060 520 1120 520 {}
N 1270 520 1300 520 {}
N 1360 520 1390 520 {}
N 1550 520 1580 520 {}
N 1640 520 1670 520 {}
N 1810 520 1840 520 {}
N 1880 520 1940 520 {}
N 2110 520 2170 520 {}
N 2335 520 2395 520 {}
N 2565 520 2625 520 {}
N 2790 520 2850 520 {}
N 2955 520 2985 520 {}
N 3045 520 3075 520 {}
N 2565 580 2790 580 {}
N -1190 720 90 720 {}
N 390 780 450 780 {}
N 490 780 520 780 {}
N 615 780 675 780 {}
N 715 780 775 780 {}
N -2270 920 3295 920 {}
C {devices/lab_wire.sym} -2270 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -2270 920 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -1170 60 2 0 {name=l2 lab=cmfb_out__bias}
C {devices/lab_wire.sym} 625 0 0 0 {name=l3 lab=cmfb_out__bias}
C {devices/lab_wire.sym} 725 170 0 1 {name=l4 lab=cmfb_out__bias}
C {devices/lab_wire.sym} -770 260 0 1 {name=l5 lab=cmfb_out__cm_sense}
C {devices/lab_wire.sym} 685 390 0 0 {name=l6 lab=cmfb_out__cm_sense}
C {devices/lab_wire.sym} 1345 450 2 0 {name=l7 lab=cmfb_out__cm_sense}
C {devices/lab_wire.sym} -1510 580 2 0 {name=l8 lab=cmfb_out__mirr}
C {devices/lab_wire.sym} -870 350 2 0 {name=l9 lab=cmfb_out__mirr}
C {devices/lab_wire.sym} -870 430 0 1 {name=l10 lab=cmfb_out__mirr}
C {devices/lab_wire.sym} -1550 170 0 1 {name=l11 lab=cmfb_out__ptail}
C {devices/lab_wire.sym} -1210 90 2 0 {name=l12 lab=cmfb_out__ptail}
C {devices/lab_wire.sym} -870 170 0 1 {name=l13 lab=cmfb_out__ptail}
C {devices/lab_wire.sym} -770 0 0 1 {name=l14 lab=cmfb_s1__bias}
C {devices/lab_wire.sym} 1100 0 0 0 {name=l15 lab=cmfb_s1__bias}
C {devices/lab_wire.sym} 1200 170 0 1 {name=l16 lab=cmfb_s1__bias}
C {devices/lab_wire.sym} -590 260 0 0 {name=l17 lab=cmfb_s1__cm_sense}
C {devices/lab_wire.sym} 40 610 2 0 {name=l18 lab=cmfb_s1__cm_sense}
C {devices/lab_wire.sym} 1360 580 2 0 {name=l19 lab=cmfb_s1__cm_sense}
C {devices/lab_wire.sym} -1170 580 2 0 {name=l20 lab=cmfb_s1__mirr}
C {devices/lab_wire.sym} -490 430 0 1 {name=l21 lab=cmfb_s1__mirr}
C {devices/lab_wire.sym} -490 350 2 0 {name=l22 lab=cmfb_s1__mirr}
C {devices/lab_wire.sym} -1210 170 0 1 {name=l23 lab=cmfb_s1__ptail}
C {devices/lab_wire.sym} -870 90 2 0 {name=l24 lab=cmfb_s1__ptail}
C {devices/lab_wire.sym} -490 170 0 1 {name=l25 lab=cmfb_s1__ptail}
C {devices/lab_wire.sym} 20 90 2 0 {name=l26 lab=core__casc_src_n}
C {devices/lab_wire.sym} 1540 90 2 0 {name=l27 lab=core__casc_src_p}
C {devices/lab_wire.sym} 1540 170 0 1 {name=l28 lab=core__casc_src_p}
C {devices/lab_wire.sym} 440 610 2 0 {name=l29 lab=core__fold_n}
C {devices/lab_wire.sym} 675 690 0 1 {name=l30 lab=core__fold_n}
C {devices/lab_wire.sym} 2700 350 2 0 {name=l31 lab=core__fold_n}
C {devices/lab_wire.sym} 450 350 2 0 {name=l32 lab=core__fold_p}
C {devices/lab_wire.sym} 450 690 0 1 {name=l33 lab=core__fold_p}
C {devices/lab_wire.sym} 1880 610 2 0 {name=l34 lab=core__fold_p}
C {devices/lab_wire.sym} -140 610 2 0 {name=l35 lab=core__g2_n}
C {devices/lab_wire.sym} 665 610 2 0 {name=l36 lab=core__g2_n}
C {devices/lab_wire.sym} 2275 260 0 0 {name=l37 lab=core__g2_n}
C {devices/lab_wire.sym} 2565 610 2 0 {name=l38 lab=core__g2_n}
C {devices/lab_wire.sym} 3045 580 2 0 {name=l39 lab=core__g2_n}
C {devices/lab_wire.sym} 895 610 2 0 {name=l40 lab=core__g2_p}
C {devices/lab_wire.sym} 1120 610 2 0 {name=l41 lab=core__g2_p}
C {devices/lab_wire.sym} 1640 580 2 0 {name=l42 lab=core__g2_p}
C {devices/lab_wire.sym} 1975 260 0 1 {name=l43 lab=core__g2_p}
C {devices/lab_wire.sym} 2110 610 2 0 {name=l44 lab=core__g2_p}
C {devices/lab_wire.sym} 2335 610 2 0 {name=l45 lab=core__g2_p}
C {devices/lab_wire.sym} 450 90 2 0 {name=l46 lab=core__tail}
C {devices/lab_wire.sym} 2700 170 0 1 {name=l47 lab=core__tail}
C {devices/lab_wire.sym} 490 840 2 0 {name=l48 lab=core__vb1}
C {devices/lab_wire.sym} 775 780 0 1 {name=l49 lab=core__vb1}
C {devices/lab_wire.sym} 480 580 2 0 {name=l50 lab=core__vb2}
C {devices/lab_wire.sym} 1840 460 0 1 {name=l51 lab=core__vb2}
C {devices/lab_wire.sym} 120 260 0 1 {name=l52 lab=core__vb3}
C {devices/lab_wire.sym} 1500 200 0 1 {name=l53 lab=core__vb3}
C {devices/lab_wire.sym} -140 430 0 1 {name=l54 lab=stg1_n}
C {devices/lab_wire.sym} 20 350 2 0 {name=l55 lab=stg1_n}
C {devices/lab_wire.sym} 1300 580 2 0 {name=l56 lab=stg1_p}
C {devices/lab_wire.sym} 1540 350 2 0 {name=l57 lab=stg1_p}
C {devices/lab_wire.sym} 1880 430 0 1 {name=l58 lab=stg1_p}
C {devices/lab_wire.sym} -1210 350 2 0 {name=l59 lab=vb4_ctl}
C {devices/lab_wire.sym} -1210 430 0 1 {name=l60 lab=vb4_ctl}
C {devices/lab_wire.sym} 120 0 0 1 {name=l61 lab=vb4_ctl}
C {devices/lab_wire.sym} 550 0 0 1 {name=l62 lab=vb4_ctl}
C {devices/lab_wire.sym} 1500 -60 0 1 {name=l63 lab=vb4_ctl}
C {devices/lab_wire.sym} -1550 350 2 0 {name=l64 lab=vb4o}
C {devices/lab_wire.sym} 1975 0 0 1 {name=l65 lab=vb4o}
C {devices/lab_wire.sym} 2800 260 0 1 {name=l66 lab=vinn}
C {devices/lab_wire.sym} 550 260 0 1 {name=l67 lab=vinp}
C {devices/lab_wire.sym} 805 450 2 0 {name=l68 lab=voutn}
C {devices/lab_wire.sym} 2375 90 2 0 {name=l69 lab=voutn}
C {devices/lab_wire.sym} 2375 170 0 1 {name=l70 lab=voutn}
C {devices/lab_wire.sym} 2985 460 0 1 {name=l71 lab=voutn}
C {devices/lab_wire.sym} 1225 390 0 0 {name=l72 lab=voutp}
C {devices/lab_wire.sym} 1580 460 0 1 {name=l73 lab=voutp}
C {devices/lab_wire.sym} 1875 90 2 0 {name=l74 lab=voutp}
C {devices/lab_wire.sym} 1875 170 0 1 {name=l75 lab=voutp}
C {devices/lab_wire.sym} -1510 320 2 0 {name=l76 lab=vref_out}
C {devices/lab_wire.sym} -1170 320 2 0 {name=l77 lab=vref_s1}
C {devices/lab_wire.sym} -40 354 2 0 {name=l78 lab=vdd}
C {devices/lab_wire.sym} 1600 354 2 0 {name=l79 lab=vdd}
C {devices/lab_wire.sym} 605 614 2 0 {name=l80 lab=vdd}
C {devices/lab_wire.sym} 2395 614 2 0 {name=l81 lab=vdd}
C {devices/lab_wire.sym} -1270 94 2 0 {name=l82 lab=vdd}
C {devices/lab_wire.sym} -930 94 2 0 {name=l83 lab=vdd}
C {devices/lab_wire.sym} 390 94 2 0 {name=l84 lab=vdd}
C {devices/lab_wire.sym} 2850 614 2 0 {name=l85 lab=vdd}
C {devices/lab_wire.sym} 1060 614 2 0 {name=l86 lab=vdd}
C {devices/lab_wire.sym} 390 354 2 0 {name=l87 lab=vdd}
C {devices/lab_wire.sym} 785 94 2 0 {name=l88 lab=vdd}
C {devices/lab_wire.sym} 1260 94 2 0 {name=l89 lab=vdd}
C {devices/lab_wire.sym} 2640 354 2 0 {name=l90 lab=vdd}
C {devices/lab_wire.sym} -930 354 2 0 {name=l91 lab=vdd}
C {devices/lab_wire.sym} -430 354 2 0 {name=l92 lab=vdd}
C {devices/lab_wire.sym} -1610 354 2 0 {name=l93 lab=vdd}
C {devices/lab_wire.sym} -1270 354 2 0 {name=l94 lab=vdd}
C {devices/lab_wire.sym} -40 94 2 0 {name=l95 lab=vdd}
C {devices/lab_wire.sym} 1600 94 2 0 {name=l96 lab=vdd}
C {devices/lab_wire.sym} 1815 94 2 0 {name=l97 lab=vdd}
C {devices/lab_wire.sym} 2435 94 2 0 {name=l98 lab=vdd}
C {devices/lab_wire.sym} 1940 614 2 0 {name=l99 lab=vss}
C {devices/lab_wire.sym} 380 614 2 0 {name=l100 lab=vss}
C {devices/lab_wire.sym} 1815 354 2 0 {name=l101 lab=vss}
C {devices/lab_wire.sym} 2435 354 2 0 {name=l102 lab=vss}
C {devices/lab_wire.sym} -200 614 2 0 {name=l103 lab=vss}
C {devices/lab_wire.sym} 2170 614 2 0 {name=l104 lab=vss}
C {devices/lab_wire.sym} 2625 614 2 0 {name=l105 lab=vss}
C {devices/lab_wire.sym} 835 614 2 0 {name=l106 lab=vss}
C {devices/lab_wire.sym} -1610 614 2 0 {name=l107 lab=vss}
C {devices/lab_wire.sym} -1270 614 2 0 {name=l108 lab=vss}
C {devices/lab_wire.sym} 390 874 2 0 {name=l109 lab=vss}
C {devices/lab_wire.sym} 615 874 2 0 {name=l110 lab=vss}
C {devices/lab_wire.sym} -930 614 2 0 {name=l111 lab=vss}
C {devices/lab_wire.sym} -430 614 2 0 {name=l112 lab=vss}
C {devices/lab_wire.sym} 785 354 2 0 {name=l113 lab=vss}
C {devices/lab_wire.sym} 1260 354 2 0 {name=l114 lab=vss}
C {devices/lab_wire.sym} -1870 870 2 0 {name=l115 lab=vss}
C {devices/lab_wire.sym} -1870 610 2 0 {name=l116 lab=vss}
C {devices/lab_wire.sym} -1870 350 2 0 {name=l117 lab=vss}
C {devices/lab_wire.sym} -1870 90 2 0 {name=l118 lab=vss}
C {devices/lab_wire.sym} -2210 870 2 0 {name=l119 lab=vss}
C {devices/lab_wire.sym} -1870 690 0 1 {name=l120 lab=core__vb1}
C {devices/lab_wire.sym} -1870 430 0 1 {name=l121 lab=core__vb2}
C {devices/lab_wire.sym} -1870 170 0 1 {name=l122 lab=core__vb3}
C {devices/lab_wire.sym} -1870 -90 0 1 {name=l123 lab=vref_out}
C {devices/lab_wire.sym} -2210 690 0 1 {name=l124 lab=vref_s1}
C {devices/lab_wire.sym} 1160 580 2 0 {name=l125 lab=vdd}
C {devices/ipin.sym} -2410 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -2410 380 0 0 {name=p1 lab=vinn}
C {devices/opin.sym} 3435 30 0 0 {name=p2 lab=voutp}
C {devices/opin.sym} 3435 150 0 0 {name=p3 lab=voutn}
