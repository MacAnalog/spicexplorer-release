v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_006_fan_chopper_cmfb} -3180 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 275 780 0 0 {name=CCM value='c_cm'}
C {devices/capa_np.sym} 1350 520 0 0 {name=CFB1_CORE value='x_dut_cfb1_core_value'}
C {devices/capa_np.sym} 1650 520 0 0 {name=CFB2_CORE value='x_dut_cfb2_core_value'}
C {devices/capa_np.sym} 1055 520 0 0 {name=CIN1_CORE value='x_dut_cin1_core_value'}
C {devices/capa_np.sym} 1950 520 0 0 {name=CIN2_CORE value='x_dut_cin2_core_value'}
C {devices/capa_np.sym} 5850 520 0 0 {name=CM1_CORE value='x_dut_cm1_core_value'}
C {devices/capa_np.sym} 6140 520 0 0 {name=CM2_CORE value='x_dut_cm2_core_value'}
C {devices/res_np.sym} 2245 520 0 0 {name=RB1_CORE value='x_dut_rb1_core_value'}
C {devices/res_np.sym} 2535 520 0 0 {name=RB2_CORE value='x_dut_rb2_core_value'}
C {devices/res_np.sym} 1070 390 1 0 {name=RMN_CMFB value='x_dut_rmn_cmfb_value'}
C {devices/res_np.sym} 1365 390 0 0 {name=RMP_CMFB value='x_dut_rmp_cmfb_value'}
C {devices/vsource_np.sym} -2800 780 0 0 {name=VB1_CORE value="dc \{vb1_core\}" savecurrent=false}
C {devices/vsource_np.sym} -2800 520 0 0 {name=VB2_CORE value="dc \{vb2_core\}" savecurrent=false}
C {devices/vsource_np.sym} -2800 260 0 0 {name=VB3_CORE value="dc \{vb3_core\}" savecurrent=false}
C {devices/vsource_np.sym} -2800 0 0 0 {name=VB4_CORE value="dc \{vb4_core\}" savecurrent=false}
C {devices/vsource_np.sym} -3140 780 0 0 {name=VREFCM value="dc \{vcm_ref\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 1350 260 0 1 {name=M10_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_core_w l=x_dut_xm10_core_l m=x_dut_xm10_core_m}
C {devices/sg13_lv_pmos_np.sym} 2575 260 0 0 {name=M11_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_core_w l=x_dut_xm11_core_l m=x_dut_xm11_core_m}
C {devices/sg13_lv_nmos_np.sym} 6430 520 0 0 {name=M12_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_core_w l=x_dut_xm12_core_l m=x_dut_xm12_core_m}
C {devices/sg13_lv_nmos_np.sym} 3010 520 0 1 {name=M13_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_core_w l=x_dut_xm13_core_l m=x_dut_xm13_core_m}
C {devices/sg13_lv_nmos_np.sym} 1650 260 0 1 {name=M14_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_core_w l=x_dut_xm14_core_l m=x_dut_xm14_core_m}
C {devices/sg13_lv_nmos_np.sym} 1055 260 0 1 {name=M15_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_core_w l=x_dut_xm15_core_l m=x_dut_xm15_core_m}
C {devices/sg13_lv_nmos_np.sym} 3275 520 0 1 {name=M16_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_core_w l=x_dut_xm16_core_l m=x_dut_xm16_core_m}
C {devices/sg13_lv_pmos_np.sym} -5 520 0 1 {name=M17_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_core_w l=x_dut_xm17_core_l m=x_dut_xm17_core_m}
C {devices/sg13_lv_nmos_np.sym} 6695 520 0 0 {name=M18_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_core_w l=x_dut_xm18_core_l m=x_dut_xm18_core_m}
C {devices/sg13_lv_pmos_np.sym} 6960 520 0 0 {name=M19_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_core_w l=x_dut_xm19_core_l m=x_dut_xm19_core_m}
C {devices/sg13_lv_pmos_np.sym} 445 0 0 1 {name=M1_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_cmfb_w l=x_dut_xm1_cmfb_l m=x_dut_xm1_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 1650 0 0 1 {name=M1_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_core_w l=x_dut_xm1_core_l m=x_dut_xm1_core_m}
C {devices/sg13_lv_nmos_np.sym} 3540 520 0 1 {name=M20_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_core_w l=x_dut_xm20_core_l m=x_dut_xm20_core_m}
C {devices/sg13_lv_pmos_np.sym} -270 520 0 1 {name=M21_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_core_w l=x_dut_xm21_core_l m=x_dut_xm21_core_m}
C {devices/sg13_lv_nmos_np.sym} 3805 520 0 1 {name=M22_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_core_w l=x_dut_xm22_core_l m=x_dut_xm22_core_m}
C {devices/sg13_lv_pmos_np.sym} -540 520 0 1 {name=M23_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_core_w l=x_dut_xm23_core_l m=x_dut_xm23_core_m}
C {devices/sg13_lv_nmos_np.sym} 4070 520 0 1 {name=M24_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_core_w l=x_dut_xm24_core_l m=x_dut_xm24_core_m}
C {devices/sg13_lv_pmos_np.sym} -805 520 0 1 {name=M25_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm25_core_w l=x_dut_xm25_core_l m=x_dut_xm25_core_m}
C {devices/sg13_lv_nmos_np.sym} 4340 520 0 1 {name=M26_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm26_core_w l=x_dut_xm26_core_l m=x_dut_xm26_core_m}
C {devices/sg13_lv_pmos_np.sym} -1070 520 0 1 {name=M27_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm27_core_w l=x_dut_xm27_core_l m=x_dut_xm27_core_m}
C {devices/sg13_lv_nmos_np.sym} 4605 520 0 1 {name=M28_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm28_core_w l=x_dut_xm28_core_l m=x_dut_xm28_core_m}
C {devices/sg13_lv_pmos_np.sym} -1335 520 0 1 {name=M29_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm29_core_w l=x_dut_xm29_core_l m=x_dut_xm29_core_m}
C {devices/sg13_lv_nmos_np.sym} 275 520 0 1 {name=M2_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_cmfb_w l=x_dut_xm2_cmfb_l m=x_dut_xm2_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 3275 260 0 1 {name=M2_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_core_w l=x_dut_xm2_core_l m=x_dut_xm2_core_m}
C {devices/sg13_lv_nmos_np.sym} 7225 520 0 0 {name=M30_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm30_core_w l=x_dut_xm30_core_l m=x_dut_xm30_core_m}
C {devices/sg13_lv_pmos_np.sym} 7490 520 0 0 {name=M31_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm31_core_w l=x_dut_xm31_core_l m=x_dut_xm31_core_m}
C {devices/sg13_lv_nmos_np.sym} 4870 520 0 1 {name=M32_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm32_core_w l=x_dut_xm32_core_l m=x_dut_xm32_core_m}
C {devices/sg13_lv_pmos_np.sym} -1600 520 0 1 {name=M33_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm33_core_w l=x_dut_xm33_core_l m=x_dut_xm33_core_m}
C {devices/sg13_lv_nmos_np.sym} 5135 520 0 1 {name=M34_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm34_core_w l=x_dut_xm34_core_l m=x_dut_xm34_core_m}
C {devices/sg13_lv_pmos_np.sym} -1870 520 0 1 {name=M35_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm35_core_w l=x_dut_xm35_core_l m=x_dut_xm35_core_m}
C {devices/sg13_lv_nmos_np.sym} 5400 520 0 1 {name=M36_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm36_core_w l=x_dut_xm36_core_l m=x_dut_xm36_core_m}
C {devices/sg13_lv_pmos_np.sym} -2135 520 0 1 {name=M37_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm37_core_w l=x_dut_xm37_core_l m=x_dut_xm37_core_m}
C {devices/sg13_lv_nmos_np.sym} 5670 520 0 1 {name=M38_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm38_core_w l=x_dut_xm38_core_l m=x_dut_xm38_core_m}
C {devices/sg13_lv_pmos_np.sym} -2400 520 0 1 {name=M39_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm39_core_w l=x_dut_xm39_core_l m=x_dut_xm39_core_m}
C {devices/sg13_lv_pmos_np.sym} 1970 0 0 0 {name=M3_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_cmfb_w l=x_dut_xm3_cmfb_l m=x_dut_xm3_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} -5 260 0 1 {name=M3_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_core_w l=x_dut_xm3_core_l m=x_dut_xm3_core_m}
C {devices/sg13_lv_pmos_np.sym} 615 260 0 0 {name=M4_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_cmfb_w l=x_dut_xm4_cmfb_l m=x_dut_xm4_cmfb_m}
C {devices/sg13_lv_nmos_np.sym} 1350 780 0 1 {name=M4_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_core_w l=x_dut_xm4_core_l m=x_dut_xm4_core_m}
C {devices/sg13_lv_pmos_np.sym} 275 260 0 1 {name=M5_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_cmfb_w l=x_dut_xm5_cmfb_l m=x_dut_xm5_cmfb_m}
C {devices/sg13_lv_nmos_np.sym} 1650 780 0 1 {name=M5_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_core_w l=x_dut_xm5_core_l m=x_dut_xm5_core_m}
C {devices/sg13_lv_nmos_np.sym} 615 520 0 0 {name=M6_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_cmfb_w l=x_dut_xm6_cmfb_l m=x_dut_xm6_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 1350 0 0 1 {name=M6_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_core_w l=x_dut_xm6_core_l m=x_dut_xm6_core_m}
C {devices/sg13_lv_nmos_np.sym} 1970 260 0 0 {name=M7_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_cmfb_w l=x_dut_xm7_cmfb_l m=x_dut_xm7_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 2575 0 0 0 {name=M7_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_core_w l=x_dut_xm7_core_l m=x_dut_xm7_core_m}
C {devices/sg13_lv_pmos_np.sym} 1055 0 0 1 {name=M8O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8o_w l=x_dut_xm8o_l m=x_dut_xm8o_m}
C {devices/sg13_lv_pmos_np.sym} 670 0 0 1 {name=M9O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9o_w l=x_dut_xm9o_l m=x_dut_xm9o_m}
N -3140 690 -3140 750 {}
N -3140 810 -3140 870 {}
N -2800 -90 -2800 -30 {}
N -2800 30 -2800 90 {}
N -2800 170 -2800 230 {}
N -2800 290 -2800 350 {}
N -2800 430 -2800 490 {}
N -2800 550 -2800 610 {}
N -2800 690 -2800 750 {}
N -2800 810 -2800 870 {}
N -2480 520 -2480 614 {}
N -2420 430 -2420 490 {}
N -2420 550 -2420 580 {}
N -2215 520 -2215 614 {}
N -2155 430 -2155 490 {}
N -2155 550 -2155 610 {}
N -1950 520 -1950 614 {}
N -1890 430 -1890 490 {}
N -1890 550 -1890 610 {}
N -1680 520 -1680 614 {}
N -1620 430 -1620 490 {}
N -1620 550 -1620 610 {}
N -1415 520 -1415 614 {}
N -1355 430 -1355 490 {}
N -1355 550 -1355 610 {}
N -1150 520 -1150 614 {}
N -1090 430 -1090 490 {}
N -1090 550 -1090 610 {}
N -885 520 -885 614 {}
N -825 430 -825 490 {}
N -825 550 -825 610 {}
N -620 520 -620 614 {}
N -560 430 -560 490 {}
N -560 550 -560 610 {}
N -350 520 -350 614 {}
N -290 430 -290 490 {}
N -290 550 -290 610 {}
N -85 260 -85 354 {}
N -85 520 -85 614 {}
N -25 200 -25 230 {}
N -25 290 -25 350 {}
N -25 430 -25 490 {}
N -25 550 -25 610 {}
N 195 60 195 230 {}
N 195 290 195 720 {}
N 255 550 255 920 {}
N 275 720 275 750 {}
N 275 810 275 920 {}
N 365 0 365 94 {}
N 425 -140 425 -30 {}
N 425 30 425 90 {}
N 590 0 590 94 {}
N 595 450 595 520 {}
N 635 170 635 230 {}
N 635 290 635 350 {}
N 635 430 635 490 {}
N 635 550 635 920 {}
N 650 -140 650 -30 {}
N 650 30 650 90 {}
N 695 260 695 354 {}
N 695 520 695 614 {}
N 720 0 720 720 {}
N 950 330 950 390 {}
N 975 0 975 94 {}
N 975 260 975 354 {}
N 1035 -140 1035 -30 {}
N 1035 30 1035 90 {}
N 1035 170 1035 230 {}
N 1035 290 1035 920 {}
N 1055 430 1055 490 {}
N 1055 550 1055 610 {}
N 1270 0 1270 94 {}
N 1270 260 1270 354 {}
N 1270 780 1270 874 {}
N 1330 -140 1330 -30 {}
N 1330 30 1330 90 {}
N 1330 170 1330 230 {}
N 1330 290 1330 350 {}
N 1330 690 1330 750 {}
N 1330 810 1330 920 {}
N 1350 430 1350 490 {}
N 1350 550 1350 610 {}
N 1365 300 1365 360 {}
N 1365 420 1365 450 {}
N 1400 -60 1400 0 {}
N 1400 780 1400 840 {}
N 1570 60 1570 200 {}
N 1570 260 1570 354 {}
N 1570 780 1570 874 {}
N 1630 -140 1630 -30 {}
N 1630 30 1630 60 {}
N 1630 60 1630 90 {}
N 1630 170 1630 230 {}
N 1630 290 1630 350 {}
N 1630 720 1630 750 {}
N 1630 810 1630 920 {}
N 1650 430 1650 490 {}
N 1650 550 1650 610 {}
N 1690 60 1690 200 {}
N 1690 320 1690 720 {}
N 1700 -60 1700 0 {}
N 1700 780 1700 840 {}
N 1750 230 1750 450 {}
N 1930 60 1930 230 {}
N 1950 0 1950 70 {}
N 1950 190 1950 260 {}
N 1950 430 1950 490 {}
N 1950 550 1950 610 {}
N 1990 -140 1990 -30 {}
N 1990 30 1990 70 {}
N 1990 190 1990 230 {}
N 1990 290 1990 920 {}
N 2050 0 2050 94 {}
N 2050 260 2050 354 {}
N 2245 430 2245 490 {}
N 2245 550 2245 610 {}
N 2525 -60 2525 0 {}
N 2535 60 2535 230 {}
N 2535 430 2535 490 {}
N 2535 550 2535 610 {}
N 2595 -140 2595 -30 {}
N 2595 30 2595 90 {}
N 2595 290 2595 350 {}
N 2655 0 2655 94 {}
N 2655 260 2655 354 {}
N 2930 520 2930 614 {}
N 2990 430 2990 490 {}
N 2990 550 2990 610 {}
N 3195 260 3195 354 {}
N 3195 520 3195 614 {}
N 3255 200 3255 230 {}
N 3255 290 3255 350 {}
N 3255 430 3255 490 {}
N 3255 550 3255 610 {}
N 3460 520 3460 614 {}
N 3520 430 3520 490 {}
N 3520 550 3520 610 {}
N 3725 520 3725 614 {}
N 3785 430 3785 490 {}
N 3785 550 3785 610 {}
N 3990 520 3990 614 {}
N 4050 430 4050 490 {}
N 4050 550 4050 610 {}
N 4260 520 4260 614 {}
N 4320 430 4320 490 {}
N 4320 550 4320 610 {}
N 4525 520 4525 614 {}
N 4585 430 4585 490 {}
N 4585 550 4585 610 {}
N 4790 520 4790 614 {}
N 4850 430 4850 490 {}
N 4850 550 4850 610 {}
N 5055 520 5055 614 {}
N 5115 430 5115 490 {}
N 5115 550 5115 610 {}
N 5320 520 5320 614 {}
N 5380 430 5380 490 {}
N 5380 550 5380 610 {}
N 5450 520 5450 580 {}
N 5650 430 5650 490 {}
N 5650 550 5650 610 {}
N 5720 520 5720 580 {}
N 5850 430 5850 490 {}
N 6140 430 6140 490 {}
N 6140 550 6140 610 {}
N 6450 460 6450 490 {}
N 6510 290 6510 550 {}
N 6570 320 6570 460 {}
N 6715 460 6715 490 {}
N 6715 550 6715 610 {}
N 6775 520 6775 614 {}
N 6980 460 6980 490 {}
N 6980 550 6980 610 {}
N 7040 520 7040 614 {}
N 7245 460 7245 490 {}
N 7245 550 7245 610 {}
N 7305 520 7305 614 {}
N 7510 460 7510 490 {}
N 7510 550 7510 580 {}
N 7570 520 7570 614 {}
N -3200 -140 8110 -140 {}
N 1400 -60 2525 -60 {}
N 365 0 425 0 {}
N 465 0 525 0 {}
N 590 0 650 0 {}
N 690 0 750 0 {}
N 975 0 1035 0 {}
N 1075 0 1135 0 {}
N 1270 0 1330 0 {}
N 1370 0 1430 0 {}
N 1670 0 1700 0 {}
N 1890 0 1950 0 {}
N 1990 0 2050 0 {}
N 2525 0 2555 0 {}
N 2595 0 2655 0 {}
N 195 60 425 60 {}
N 1570 60 1690 60 {}
N 1930 60 1990 60 {}
N 2535 60 2595 60 {}
N 1950 70 1990 70 {}
N 1950 190 1990 190 {}
N -25 200 3255 200 {}
N 195 230 255 230 {}
N 1630 230 1750 230 {}
N 1930 230 1990 230 {}
N 2535 230 2595 230 {}
N -85 260 -25 260 {}
N 15 260 75 260 {}
N 295 260 355 260 {}
N 535 260 595 260 {}
N 635 260 695 260 {}
N 975 260 1035 260 {}
N 1075 260 1135 260 {}
N 1270 260 1330 260 {}
N 1370 260 1430 260 {}
N 1570 260 1630 260 {}
N 1670 260 1730 260 {}
N 1990 260 2050 260 {}
N 2525 260 2555 260 {}
N 2595 260 2655 260 {}
N 3195 260 3255 260 {}
N 3295 260 3355 260 {}
N 195 290 255 290 {}
N 3255 290 6510 290 {}
N -25 320 1690 320 {}
N 2595 320 6570 320 {}
N 950 330 1365 330 {}
N 950 390 1040 390 {}
N 1100 390 1190 390 {}
N 595 450 635 450 {}
N 1365 450 1750 450 {}
N 6450 460 7510 460 {}
N 195 490 255 490 {}
N -2480 520 -2420 520 {}
N -2380 520 -2350 520 {}
N -2215 520 -2155 520 {}
N -2115 520 -2055 520 {}
N -1950 520 -1890 520 {}
N -1850 520 -1820 520 {}
N -1680 520 -1620 520 {}
N -1580 520 -1520 520 {}
N -1415 520 -1355 520 {}
N -1315 520 -1285 520 {}
N -1150 520 -1090 520 {}
N -1050 520 -1020 520 {}
N -885 520 -825 520 {}
N -785 520 -725 520 {}
N -620 520 -560 520 {}
N -520 520 -490 520 {}
N -350 520 -290 520 {}
N -250 520 -190 520 {}
N -85 520 -25 520 {}
N 15 520 45 520 {}
N 265 520 595 520 {}
N 635 520 695 520 {}
N 2930 520 2990 520 {}
N 3030 520 3090 520 {}
N 3195 520 3255 520 {}
N 3295 520 3355 520 {}
N 3460 520 3520 520 {}
N 3560 520 3620 520 {}
N 3725 520 3785 520 {}
N 3825 520 3885 520 {}
N 3990 520 4050 520 {}
N 4090 520 4150 520 {}
N 4260 520 4320 520 {}
N 4360 520 4420 520 {}
N 4525 520 4585 520 {}
N 4625 520 4685 520 {}
N 4790 520 4850 520 {}
N 4890 520 4950 520 {}
N 5055 520 5115 520 {}
N 5155 520 5215 520 {}
N 5320 520 5380 520 {}
N 5420 520 5480 520 {}
N 5690 520 5720 520 {}
N 6350 520 6410 520 {}
N 6615 520 6675 520 {}
N 6715 520 6775 520 {}
N 6880 520 6940 520 {}
N 6980 520 7040 520 {}
N 7145 520 7205 520 {}
N 7245 520 7305 520 {}
N 7410 520 7470 520 {}
N 7510 520 7570 520 {}
N 5590 550 5850 550 {}
N 6450 550 6510 550 {}
N 5450 580 5720 580 {}
N 7245 580 7510 580 {}
N 195 720 720 720 {}
N 1630 720 1690 720 {}
N 1270 780 1330 780 {}
N 1370 780 1430 780 {}
N 1570 780 1630 780 {}
N 1670 780 1700 780 {}
N 1400 840 1700 840 {}
N -3200 920 8110 920 {}
C {devices/lab_wire.sym} -2055 520 0 1 {name=l0 lab=clk_chfb}
C {devices/lab_wire.sym} 3620 520 0 1 {name=l1 lab=clk_chfb}
C {devices/lab_wire.sym} 3885 520 0 1 {name=l2 lab=clk_chfb}
C {devices/lab_wire.sym} -190 520 0 1 {name=l3 lab=clk_chfb_not}
C {devices/lab_wire.sym} 5480 520 0 1 {name=l4 lab=clk_chfb_not}
C {devices/lab_wire.sym} -1520 520 0 1 {name=l5 lab=clk_chin}
C {devices/lab_wire.sym} 4150 520 0 1 {name=l6 lab=clk_chin}
C {devices/lab_wire.sym} 4420 520 0 1 {name=l7 lab=clk_chin}
C {devices/lab_wire.sym} -725 520 0 1 {name=l8 lab=clk_chin_not}
C {devices/lab_wire.sym} 4950 520 0 1 {name=l9 lab=clk_chin_not}
C {devices/lab_wire.sym} 5215 520 0 1 {name=l10 lab=clk_chin_not}
C {devices/lab_wire.sym} 3355 520 0 1 {name=l11 lab=clk_chout}
C {devices/lab_wire.sym} 6615 520 0 0 {name=l12 lab=clk_chout}
C {devices/lab_wire.sym} 7410 520 0 0 {name=l13 lab=clk_chout}
C {devices/lab_wire.sym} 4685 520 0 1 {name=l14 lab=clk_chout_not}
C {devices/lab_wire.sym} 6880 520 0 0 {name=l15 lab=clk_chout_not}
C {devices/lab_wire.sym} 7145 520 0 0 {name=l16 lab=clk_chout_not}
C {devices/lab_wire.sym} 525 0 0 1 {name=l17 lab=cmfb__bias}
C {devices/lab_wire.sym} 1890 0 0 0 {name=l18 lab=cmfb__bias}
C {devices/lab_wire.sym} 535 260 0 0 {name=l19 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 1365 300 0 1 {name=l20 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 635 430 0 1 {name=l21 lab=cmfb__mirr}
C {devices/lab_wire.sym} 635 350 2 0 {name=l22 lab=cmfb__mirr}
C {devices/lab_wire.sym} 425 90 2 0 {name=l23 lab=cmfb__ptail}
C {devices/lab_wire.sym} 635 170 0 1 {name=l24 lab=cmfb__ptail}
C {devices/lab_wire.sym} 1330 90 2 0 {name=l25 lab=core__casc_src_n}
C {devices/lab_wire.sym} 1330 170 0 1 {name=l26 lab=core__casc_src_n}
C {devices/lab_wire.sym} 2595 90 2 0 {name=l27 lab=core__casc_src_p}
C {devices/lab_wire.sym} -2420 430 0 1 {name=l28 lab=core__fbch_n}
C {devices/lab_wire.sym} -560 430 0 1 {name=l29 lab=core__fbch_n}
C {devices/lab_wire.sym} 1650 430 0 1 {name=l30 lab=core__fbch_n}
C {devices/lab_wire.sym} 3785 430 0 1 {name=l31 lab=core__fbch_n}
C {devices/lab_wire.sym} 5650 430 0 1 {name=l32 lab=core__fbch_n}
C {devices/lab_wire.sym} -2155 430 0 1 {name=l33 lab=core__fbch_p}
C {devices/lab_wire.sym} -290 430 0 1 {name=l34 lab=core__fbch_p}
C {devices/lab_wire.sym} 1350 430 0 1 {name=l35 lab=core__fbch_p}
C {devices/lab_wire.sym} 3520 430 0 1 {name=l36 lab=core__fbch_p}
C {devices/lab_wire.sym} 5380 430 0 1 {name=l37 lab=core__fbch_p}
C {devices/lab_wire.sym} -25 350 2 0 {name=l38 lab=core__fold_n}
C {devices/lab_wire.sym} 2990 610 2 0 {name=l39 lab=core__fold_n}
C {devices/lab_wire.sym} 1330 690 0 1 {name=l40 lab=core__fold_p}
C {devices/lab_wire.sym} 3255 350 2 0 {name=l41 lab=core__fold_p}
C {devices/lab_wire.sym} -25 610 2 0 {name=l42 lab=core__g2_n}
C {devices/lab_wire.sym} 1135 260 0 1 {name=l43 lab=core__g2_n}
C {devices/lab_wire.sym} 3255 610 2 0 {name=l44 lab=core__g2_n}
C {devices/lab_wire.sym} 6140 430 0 1 {name=l45 lab=core__g2_n}
C {devices/lab_wire.sym} 7245 610 2 0 {name=l46 lab=core__g2_n}
C {devices/lab_wire.sym} -1355 610 2 0 {name=l47 lab=core__g2_p}
C {devices/lab_wire.sym} 1730 260 0 1 {name=l48 lab=core__g2_p}
C {devices/lab_wire.sym} 4585 610 2 0 {name=l49 lab=core__g2_p}
C {devices/lab_wire.sym} 5850 430 0 1 {name=l50 lab=core__g2_p}
C {devices/lab_wire.sym} 6715 610 2 0 {name=l51 lab=core__g2_p}
C {devices/lab_wire.sym} 6980 610 2 0 {name=l52 lab=core__g2_p}
C {devices/lab_wire.sym} -1890 610 2 0 {name=l53 lab=core__inch_n}
C {devices/lab_wire.sym} -825 610 2 0 {name=l54 lab=core__inch_n}
C {devices/lab_wire.sym} 1055 610 2 0 {name=l55 lab=core__inch_n}
C {devices/lab_wire.sym} 4050 610 2 0 {name=l56 lab=core__inch_n}
C {devices/lab_wire.sym} 5115 610 2 0 {name=l57 lab=core__inch_n}
C {devices/lab_wire.sym} -1620 610 2 0 {name=l58 lab=core__inch_p}
C {devices/lab_wire.sym} -1090 610 2 0 {name=l59 lab=core__inch_p}
C {devices/lab_wire.sym} 1950 610 2 0 {name=l60 lab=core__inch_p}
C {devices/lab_wire.sym} 4320 610 2 0 {name=l61 lab=core__inch_p}
C {devices/lab_wire.sym} 4850 610 2 0 {name=l62 lab=core__inch_p}
C {devices/lab_wire.sym} -1355 430 0 1 {name=l63 lab=core__out1_n}
C {devices/lab_wire.sym} -25 430 0 1 {name=l64 lab=core__out1_n}
C {devices/lab_wire.sym} 1330 350 2 0 {name=l65 lab=core__out1_n}
C {devices/lab_wire.sym} 2990 430 0 1 {name=l66 lab=core__out1_n}
C {devices/lab_wire.sym} 3255 430 0 1 {name=l67 lab=core__out1_n}
C {devices/lab_wire.sym} 4585 430 0 1 {name=l68 lab=core__out1_n}
C {devices/lab_wire.sym} 2595 350 2 0 {name=l69 lab=core__out1_p}
C {devices/lab_wire.sym} 1630 90 2 0 {name=l70 lab=core__tail}
C {devices/lab_wire.sym} 1430 780 0 1 {name=l71 lab=core__vb1}
C {devices/lab_wire.sym} 3090 520 0 1 {name=l72 lab=core__vb2}
C {devices/lab_wire.sym} 6350 520 0 0 {name=l73 lab=core__vb2}
C {devices/lab_wire.sym} 1430 260 0 1 {name=l74 lab=core__vb3}
C {devices/lab_wire.sym} 2555 260 0 0 {name=l75 lab=core__vb3}
C {devices/lab_wire.sym} 1430 0 0 1 {name=l76 lab=core__vb4}
C {devices/lab_wire.sym} 75 260 0 1 {name=l77 lab=core__vsum_n}
C {devices/lab_wire.sym} 1055 430 0 1 {name=l78 lab=core__vsum_n}
C {devices/lab_wire.sym} 1350 610 2 0 {name=l79 lab=core__vsum_n}
C {devices/lab_wire.sym} 2245 430 0 1 {name=l80 lab=core__vsum_n}
C {devices/lab_wire.sym} 1650 610 2 0 {name=l81 lab=core__vsum_p}
C {devices/lab_wire.sym} 1950 430 0 1 {name=l82 lab=core__vsum_p}
C {devices/lab_wire.sym} 2535 430 0 1 {name=l83 lab=core__vsum_p}
C {devices/lab_wire.sym} 3355 260 0 1 {name=l84 lab=core__vsum_p}
C {devices/lab_wire.sym} 750 0 0 1 {name=l85 lab=vb4o}
C {devices/lab_wire.sym} 1135 0 0 1 {name=l86 lab=vb4o}
C {devices/lab_wire.sym} -1620 430 0 1 {name=l87 lab=vinn}
C {devices/lab_wire.sym} -825 430 0 1 {name=l88 lab=vinn}
C {devices/lab_wire.sym} 4050 430 0 1 {name=l89 lab=vinn}
C {devices/lab_wire.sym} 4850 430 0 1 {name=l90 lab=vinn}
C {devices/lab_wire.sym} -1890 430 0 1 {name=l91 lab=vinp}
C {devices/lab_wire.sym} -1090 430 0 1 {name=l92 lab=vinp}
C {devices/lab_wire.sym} 4320 430 0 1 {name=l93 lab=vinp}
C {devices/lab_wire.sym} 5115 430 0 1 {name=l94 lab=vinp}
C {devices/lab_wire.sym} -2155 610 2 0 {name=l95 lab=voutn}
C {devices/lab_wire.sym} -560 610 2 0 {name=l96 lab=voutn}
C {devices/lab_wire.sym} 650 90 2 0 {name=l97 lab=voutn}
C {devices/lab_wire.sym} 1035 170 0 1 {name=l98 lab=voutn}
C {devices/lab_wire.sym} 3785 610 2 0 {name=l99 lab=voutn}
C {devices/lab_wire.sym} 5380 610 2 0 {name=l100 lab=voutn}
C {devices/lab_wire.sym} 6140 610 2 0 {name=l101 lab=voutn}
C {devices/lab_wire.sym} -290 610 2 0 {name=l102 lab=voutp}
C {devices/lab_wire.sym} 1035 90 2 0 {name=l103 lab=voutp}
C {devices/lab_wire.sym} 1630 170 0 1 {name=l104 lab=voutp}
C {devices/lab_wire.sym} 3520 610 2 0 {name=l105 lab=voutp}
C {devices/lab_wire.sym} 5650 610 2 0 {name=l106 lab=voutp}
C {devices/lab_wire.sym} 2245 610 2 0 {name=l107 lab=vref}
C {devices/lab_wire.sym} 2535 610 2 0 {name=l108 lab=vref}
C {devices/lab_wire.sym} 355 260 0 1 {name=l109 lab=vref_cm}
C {devices/lab_wire.sym} 1270 354 2 0 {name=l110 lab=vdd}
C {devices/lab_wire.sym} 2655 354 2 0 {name=l111 lab=vdd}
C {devices/lab_wire.sym} -85 614 2 0 {name=l112 lab=vdd}
C {devices/lab_wire.sym} 7040 614 2 0 {name=l113 lab=vdd}
C {devices/lab_wire.sym} 365 94 2 0 {name=l114 lab=vdd}
C {devices/lab_wire.sym} 1630 0 0 0 {name=l115 lab=vdd}
C {devices/lab_wire.sym} -350 614 2 0 {name=l116 lab=vdd}
C {devices/lab_wire.sym} -620 614 2 0 {name=l117 lab=vdd}
C {devices/lab_wire.sym} -885 614 2 0 {name=l118 lab=vdd}
C {devices/lab_wire.sym} -1150 614 2 0 {name=l119 lab=vdd}
C {devices/lab_wire.sym} -1415 614 2 0 {name=l120 lab=vdd}
C {devices/lab_wire.sym} 3195 354 2 0 {name=l121 lab=vdd}
C {devices/lab_wire.sym} 7570 614 2 0 {name=l122 lab=vdd}
C {devices/lab_wire.sym} -1680 614 2 0 {name=l123 lab=vdd}
C {devices/lab_wire.sym} -1950 614 2 0 {name=l124 lab=vdd}
C {devices/lab_wire.sym} -2215 614 2 0 {name=l125 lab=vdd}
C {devices/lab_wire.sym} -2480 614 2 0 {name=l126 lab=vdd}
C {devices/lab_wire.sym} 2050 94 2 0 {name=l127 lab=vdd}
C {devices/lab_wire.sym} -85 354 2 0 {name=l128 lab=vdd}
C {devices/lab_wire.sym} 695 354 2 0 {name=l129 lab=vdd}
C {devices/lab_wire.sym} 255 260 0 0 {name=l130 lab=vdd}
C {devices/lab_wire.sym} 1270 94 2 0 {name=l131 lab=vdd}
C {devices/lab_wire.sym} 2655 94 2 0 {name=l132 lab=vdd}
C {devices/lab_wire.sym} 975 94 2 0 {name=l133 lab=vdd}
C {devices/lab_wire.sym} 590 94 2 0 {name=l134 lab=vdd}
C {devices/lab_wire.sym} 6450 520 0 0 {name=l135 lab=vss}
C {devices/lab_wire.sym} 2930 614 2 0 {name=l136 lab=vss}
C {devices/lab_wire.sym} 1570 354 2 0 {name=l137 lab=vss}
C {devices/lab_wire.sym} 975 354 2 0 {name=l138 lab=vss}
C {devices/lab_wire.sym} 3195 614 2 0 {name=l139 lab=vss}
C {devices/lab_wire.sym} 6775 614 2 0 {name=l140 lab=vss}
C {devices/lab_wire.sym} 3460 614 2 0 {name=l141 lab=vss}
C {devices/lab_wire.sym} 3725 614 2 0 {name=l142 lab=vss}
C {devices/lab_wire.sym} 3990 614 2 0 {name=l143 lab=vss}
C {devices/lab_wire.sym} 4260 614 2 0 {name=l144 lab=vss}
C {devices/lab_wire.sym} 4525 614 2 0 {name=l145 lab=vss}
C {devices/lab_wire.sym} 255 520 0 0 {name=l146 lab=vss}
C {devices/lab_wire.sym} 7305 614 2 0 {name=l147 lab=vss}
C {devices/lab_wire.sym} 4790 614 2 0 {name=l148 lab=vss}
C {devices/lab_wire.sym} 5055 614 2 0 {name=l149 lab=vss}
C {devices/lab_wire.sym} 5320 614 2 0 {name=l150 lab=vss}
C {devices/lab_wire.sym} 5650 520 0 0 {name=l151 lab=vss}
C {devices/lab_wire.sym} 1270 874 2 0 {name=l152 lab=vss}
C {devices/lab_wire.sym} 1570 874 2 0 {name=l153 lab=vss}
C {devices/lab_wire.sym} 695 614 2 0 {name=l154 lab=vss}
C {devices/lab_wire.sym} 2050 354 2 0 {name=l155 lab=vss}
C {devices/lab_wire.sym} -2800 870 2 0 {name=l156 lab=vss}
C {devices/lab_wire.sym} -2800 610 2 0 {name=l157 lab=vss}
C {devices/lab_wire.sym} -2800 350 2 0 {name=l158 lab=vss}
C {devices/lab_wire.sym} -2800 90 2 0 {name=l159 lab=vss}
C {devices/lab_wire.sym} -3140 870 2 0 {name=l160 lab=vss}
C {devices/lab_wire.sym} -2800 690 0 1 {name=l161 lab=core__vb1}
C {devices/lab_wire.sym} -2800 430 0 1 {name=l162 lab=core__vb2}
C {devices/lab_wire.sym} -2800 170 0 1 {name=l163 lab=core__vb3}
C {devices/lab_wire.sym} -2800 -90 0 1 {name=l164 lab=core__vb4}
C {devices/lab_wire.sym} -3140 690 0 1 {name=l165 lab=vref_cm}
C {devices/lab_wire.sym} 1630 350 2 0 {name=l166 lab=vss}
C {devices/ipin.sym} -2350 520 0 0 {name=p0 lab=clk_chfb}
C {devices/ipin.sym} -1820 520 0 0 {name=p1 lab=clk_chin}
C {devices/ipin.sym} -1285 520 0 0 {name=p2 lab=clk_chout}
C {devices/ipin.sym} -1020 520 0 0 {name=p3 lab=clk_chin_not}
C {devices/ipin.sym} -490 520 0 0 {name=p4 lab=clk_chfb_not}
C {devices/ipin.sym} 45 520 0 0 {name=p5 lab=clk_chout_not}
C {devices/iopin.sym} -3200 -140 0 0 {name=p6 lab=vdd}
C {devices/iopin.sym} -3200 920 0 0 {name=p7 lab=vss}
C {devices/opin.sym} 1190 390 0 0 {name=p8 lab=voutn}
C {devices/opin.sym} -2420 580 0 0 {name=p9 lab=voutp}
C {devices/iopin.sym} 2245 1060 0 0 {name=p10 lab=vref}
C {devices/opin.sym} 8250 490 0 0 {name=p11 lab=vinp}
C {devices/opin.sym} 8250 610 0 0 {name=p12 lab=vinn}
