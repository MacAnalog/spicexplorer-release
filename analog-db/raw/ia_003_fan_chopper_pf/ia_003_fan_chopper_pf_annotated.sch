v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_003_fan_chopper_pf} -3730 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1645 520 0 0 {name=CFB1 value='x_dut_cfb1_value'}
C {devices/capa_np.sym} 1905 520 0 0 {name=CFB2 value='x_dut_cfb2_value'}
C {devices/capa_np.sym} 2160 520 0 0 {name=CIN1 value='x_dut_cin1_value'}
C {devices/capa_np.sym} 2420 520 0 0 {name=CIN2 value='x_dut_cin2_value'}
C {devices/capa_np.sym} 180 520 0 0 {name=CM1 value='x_dut_cm1_value'}
C {devices/capa_np.sym} 2680 520 0 0 {name=CM2 value='x_dut_cm2_value'}
C {devices/capa_np.sym} -80 520 0 0 {name=CPF1 value='x_dut_cpf1_value'}
C {devices/capa_np.sym} 2930 520 0 0 {name=CPF2 value='x_dut_cpf2_value'}
C {devices/res_np.sym} -330 520 0 0 {name=RB1 value='x_dut_rb1_value'}
C {devices/res_np.sym} 3185 520 0 0 {name=RB2 value='x_dut_rb2_value'}
C {devices/vsource_np.sym} -3690 780 0 0 {name=VB1 value="dc \{vb1\}" savecurrent=false}
C {devices/vsource_np.sym} -3690 520 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -3690 260 0 0 {name=VB3 value="dc \{vb3\}" savecurrent=false}
C {devices/vsource_np.sym} -3690 0 0 0 {name=VB4 value="dc \{vb4\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 1260 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 1025 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 1495 260 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} 6150 520 0 0 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 1025 520 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 1260 260 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 1905 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 1250 520 0 1 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} 800 520 0 1 {name=M17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 6375 520 0 0 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_pmos_np.sym} 6600 520 0 0 {name=M19 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} 580 260 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} -555 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_pmos_np.sym} 3435 520 0 0 {name=M21 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} -780 520 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} 3660 520 0 0 {name=M23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_nmos_np.sym} -1005 520 0 0 {name=M24 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_pmos_np.sym} 3890 520 0 0 {name=M25 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
C {devices/sg13_lv_nmos_np.sym} -1230 520 0 0 {name=M26 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm26_w l=x_dut_xm26_l m=x_dut_xm26_m}
C {devices/sg13_lv_pmos_np.sym} 4115 520 0 0 {name=M27 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm27_w l=x_dut_xm27_l m=x_dut_xm27_m}
C {devices/sg13_lv_nmos_np.sym} -1460 520 0 0 {name=M28 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm28_w l=x_dut_xm28_l m=x_dut_xm28_m}
C {devices/sg13_lv_pmos_np.sym} 4340 520 0 0 {name=M29 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm29_w l=x_dut_xm29_l m=x_dut_xm29_m}
C {devices/sg13_lv_pmos_np.sym} 2160 260 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} -1685 520 0 0 {name=M30 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm30_w l=x_dut_xm30_l m=x_dut_xm30_m}
C {devices/sg13_lv_pmos_np.sym} 4565 520 0 0 {name=M31 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm31_w l=x_dut_xm31_l m=x_dut_xm31_m}
C {devices/sg13_lv_nmos_np.sym} 1475 520 0 1 {name=M32 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm32_w l=x_dut_xm32_l m=x_dut_xm32_m}
C {devices/sg13_lv_pmos_np.sym} 570 520 0 1 {name=M33 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm33_w l=x_dut_xm33_l m=x_dut_xm33_m}
C {devices/sg13_lv_nmos_np.sym} -3350 520 0 0 {name=M34 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm34_w l=x_dut_xm34_l m=x_dut_xm34_m}
C {devices/sg13_lv_pmos_np.sym} 6825 520 0 0 {name=M35 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm35_w l=x_dut_xm35_l m=x_dut_xm35_m}
C {devices/sg13_lv_nmos_np.sym} -1910 520 0 0 {name=M36 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm36_w l=x_dut_xm36_l m=x_dut_xm36_m}
C {devices/sg13_lv_pmos_np.sym} 4790 520 0 0 {name=M37 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm37_w l=x_dut_xm37_l m=x_dut_xm37_m}
C {devices/sg13_lv_nmos_np.sym} -2135 520 0 0 {name=M38 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm38_w l=x_dut_xm38_l m=x_dut_xm38_m}
C {devices/sg13_lv_pmos_np.sym} 5020 520 0 0 {name=M39 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm39_w l=x_dut_xm39_l m=x_dut_xm39_m}
C {devices/sg13_lv_nmos_np.sym} 1260 780 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} -2360 520 0 0 {name=M40 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm40_w l=x_dut_xm40_l m=x_dut_xm40_m}
C {devices/sg13_lv_pmos_np.sym} 5245 520 0 0 {name=M41 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm41_w l=x_dut_xm41_l m=x_dut_xm41_m}
C {devices/sg13_lv_nmos_np.sym} -2590 520 0 0 {name=M42 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm42_w l=x_dut_xm42_l m=x_dut_xm42_m}
C {devices/sg13_lv_pmos_np.sym} 5470 520 0 0 {name=M43 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm43_w l=x_dut_xm43_l m=x_dut_xm43_m}
C {devices/sg13_lv_nmos_np.sym} -2815 520 0 0 {name=M44 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm44_w l=x_dut_xm44_l m=x_dut_xm44_m}
C {devices/sg13_lv_pmos_np.sym} 5695 520 0 0 {name=M45 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm45_w l=x_dut_xm45_l m=x_dut_xm45_m}
C {devices/sg13_lv_nmos_np.sym} -3040 520 0 0 {name=M46 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm46_w l=x_dut_xm46_l m=x_dut_xm46_m}
C {devices/sg13_lv_pmos_np.sym} 5920 520 0 0 {name=M47 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm47_w l=x_dut_xm47_l m=x_dut_xm47_m}
C {devices/sg13_lv_nmos_np.sym} 1485 780 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 1025 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 1495 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 1905 0 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 580 0 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -3690 -90 -3690 -30 {}
N -3690 30 -3690 90 {}
N -3690 170 -3690 230 {}
N -3690 290 -3690 350 {}
N -3690 430 -3690 490 {}
N -3690 550 -3690 610 {}
N -3690 690 -3690 750 {}
N -3690 810 -3690 870 {}
N -3330 460 -3330 490 {}
N -3330 550 -3330 610 {}
N -3270 520 -3270 614 {}
N -3020 430 -3020 490 {}
N -3020 550 -3020 610 {}
N -2960 520 -2960 614 {}
N -2795 430 -2795 490 {}
N -2795 550 -2795 610 {}
N -2735 520 -2735 614 {}
N -2570 430 -2570 490 {}
N -2570 550 -2570 610 {}
N -2510 520 -2510 614 {}
N -2340 430 -2340 490 {}
N -2340 550 -2340 610 {}
N -2280 520 -2280 614 {}
N -2115 430 -2115 490 {}
N -2115 550 -2115 610 {}
N -2055 520 -2055 614 {}
N -1890 430 -1890 490 {}
N -1890 550 -1890 610 {}
N -1830 520 -1830 614 {}
N -1665 430 -1665 490 {}
N -1665 550 -1665 610 {}
N -1605 520 -1605 614 {}
N -1440 430 -1440 490 {}
N -1440 550 -1440 610 {}
N -1380 520 -1380 614 {}
N -1210 430 -1210 490 {}
N -1210 550 -1210 610 {}
N -1150 520 -1150 614 {}
N -985 430 -985 490 {}
N -985 550 -985 610 {}
N -925 520 -925 614 {}
N -760 430 -760 490 {}
N -760 550 -760 610 {}
N -700 520 -700 614 {}
N -535 430 -535 490 {}
N -535 550 -535 610 {}
N -475 520 -475 614 {}
N -330 430 -330 490 {}
N -330 550 -330 610 {}
N -80 430 -80 490 {}
N -80 550 -80 610 {}
N 180 430 180 490 {}
N 180 550 180 610 {}
N 490 520 490 614 {}
N 530 -60 530 0 {}
N 550 430 550 490 {}
N 550 550 550 610 {}
N 600 -140 600 -30 {}
N 600 30 600 60 {}
N 600 200 600 230 {}
N 600 290 600 350 {}
N 660 0 660 94 {}
N 660 260 660 354 {}
N 720 520 720 614 {}
N 780 430 780 490 {}
N 780 550 780 610 {}
N 945 0 945 94 {}
N 945 260 945 354 {}
N 945 520 945 614 {}
N 1005 -140 1005 -30 {}
N 1005 30 1005 90 {}
N 1005 290 1005 350 {}
N 1005 430 1005 490 {}
N 1005 550 1005 610 {}
N 1065 30 1065 230 {}
N 1075 -60 1075 0 {}
N 1170 520 1170 614 {}
N 1210 -60 1210 0 {}
N 1210 260 1210 610 {}
N 1210 780 1210 840 {}
N 1220 30 1220 200 {}
N 1230 430 1230 490 {}
N 1280 -140 1280 -30 {}
N 1280 30 1280 90 {}
N 1280 170 1280 230 {}
N 1280 290 1280 350 {}
N 1280 690 1280 750 {}
N 1280 810 1280 920 {}
N 1340 30 1340 200 {}
N 1340 260 1340 354 {}
N 1340 780 1340 874 {}
N 1395 520 1395 614 {}
N 1435 780 1435 840 {}
N 1445 -60 1445 0 {}
N 1455 320 1455 460 {}
N 1455 550 1455 610 {}
N 1495 520 1495 580 {}
N 1505 690 1505 750 {}
N 1505 810 1505 920 {}
N 1515 -140 1515 -30 {}
N 1515 30 1515 90 {}
N 1515 170 1515 230 {}
N 1515 290 1515 320 {}
N 1515 320 1515 350 {}
N 1565 780 1565 874 {}
N 1575 0 1575 94 {}
N 1575 320 1575 460 {}
N 1645 430 1645 490 {}
N 1645 550 1645 610 {}
N 1905 550 1905 610 {}
N 1925 -140 1925 -30 {}
N 1925 30 1925 90 {}
N 1925 170 1925 230 {}
N 1925 290 1925 920 {}
N 1985 0 1985 94 {}
N 1985 260 1985 354 {}
N 2160 550 2160 610 {}
N 2180 200 2180 230 {}
N 2180 290 2180 350 {}
N 2240 260 2240 354 {}
N 2420 550 2420 610 {}
N 2680 550 2680 610 {}
N 2930 550 2930 610 {}
N 3185 550 3185 610 {}
N 3455 430 3455 490 {}
N 3455 550 3455 610 {}
N 3515 520 3515 614 {}
N 3680 430 3680 490 {}
N 3680 550 3680 610 {}
N 3740 520 3740 614 {}
N 3910 430 3910 490 {}
N 3910 550 3910 610 {}
N 3970 520 3970 614 {}
N 4135 430 4135 490 {}
N 4135 550 4135 610 {}
N 4195 520 4195 614 {}
N 4360 430 4360 490 {}
N 4360 550 4360 610 {}
N 4420 520 4420 614 {}
N 4585 430 4585 490 {}
N 4585 550 4585 610 {}
N 4645 520 4645 614 {}
N 4810 430 4810 490 {}
N 4810 550 4810 610 {}
N 4870 520 4870 614 {}
N 5040 430 5040 490 {}
N 5040 550 5040 610 {}
N 5100 520 5100 614 {}
N 5265 430 5265 490 {}
N 5265 550 5265 610 {}
N 5325 520 5325 614 {}
N 5490 430 5490 490 {}
N 5490 550 5490 610 {}
N 5550 520 5550 614 {}
N 5715 430 5715 490 {}
N 5715 550 5715 610 {}
N 5775 520 5775 614 {}
N 5940 430 5940 490 {}
N 5940 550 5940 610 {}
N 6000 520 6000 614 {}
N 6170 460 6170 490 {}
N 6170 550 6170 610 {}
N 6230 520 6230 614 {}
N 6395 460 6395 490 {}
N 6395 550 6395 610 {}
N 6455 520 6455 614 {}
N 6620 460 6620 490 {}
N 6620 550 6620 610 {}
N 6680 520 6680 614 {}
N 6845 460 6845 490 {}
N 6845 550 6845 610 {}
N 6905 520 6905 614 {}
N -3750 -140 7325 -140 {}
N 530 -60 1075 -60 {}
N 1210 -60 1445 -60 {}
N 500 0 560 0 {}
N 600 0 660 0 {}
N 945 0 1005 0 {}
N 1045 0 1240 0 {}
N 1445 0 1475 0 {}
N 1515 0 1575 0 {}
N 1825 0 1885 0 {}
N 1925 0 1985 0 {}
N 1005 30 1065 30 {}
N 1220 30 1340 30 {}
N 600 200 2180 200 {}
N 1005 230 1065 230 {}
N 500 260 560 260 {}
N 600 260 660 260 {}
N 945 260 1005 260 {}
N 1045 260 1105 260 {}
N 1180 260 1240 260 {}
N 1280 260 1340 260 {}
N 1415 260 1475 260 {}
N 1825 260 1885 260 {}
N 1925 260 1985 260 {}
N 2080 260 2140 260 {}
N 2180 260 2240 260 {}
N 1455 320 1575 320 {}
N 1645 430 3455 430 {}
N -3330 460 6845 460 {}
N 1170 490 1455 490 {}
N -3460 520 -3370 520 {}
N -3330 520 -3270 520 {}
N -3150 520 -3060 520 {}
N -3020 520 -2960 520 {}
N -2895 520 -2835 520 {}
N -2795 520 -2735 520 {}
N -2700 520 -2610 520 {}
N -2570 520 -2510 520 {}
N -2440 520 -2380 520 {}
N -2340 520 -2280 520 {}
N -2245 520 -2155 520 {}
N -2115 520 -2055 520 {}
N -1990 520 -1930 520 {}
N -1890 520 -1830 520 {}
N -1795 520 -1705 520 {}
N -1665 520 -1605 520 {}
N -1540 520 -1480 520 {}
N -1440 520 -1380 520 {}
N -1340 520 -1250 520 {}
N -1210 520 -1150 520 {}
N -1085 520 -1025 520 {}
N -985 520 -925 520 {}
N -890 520 -800 520 {}
N -760 520 -700 520 {}
N -635 520 -575 520 {}
N -535 520 -475 520 {}
N 490 520 550 520 {}
N 590 520 620 520 {}
N 720 520 780 520 {}
N 820 520 880 520 {}
N 945 520 1005 520 {}
N 1045 520 1105 520 {}
N 1170 520 1230 520 {}
N 1270 520 1330 520 {}
N 1395 520 1455 520 {}
N 1495 520 1525 520 {}
N 3355 520 3415 520 {}
N 3455 520 3515 520 {}
N 3580 520 3640 520 {}
N 3680 520 3740 520 {}
N 3810 520 3870 520 {}
N 3910 520 3970 520 {}
N 4035 520 4095 520 {}
N 4135 520 4195 520 {}
N 4260 520 4320 520 {}
N 4360 520 4420 520 {}
N 4485 520 4545 520 {}
N 4585 520 4645 520 {}
N 4710 520 4770 520 {}
N 4810 520 4870 520 {}
N 4940 520 5000 520 {}
N 5040 520 5100 520 {}
N 5165 520 5225 520 {}
N 5265 520 5325 520 {}
N 5390 520 5450 520 {}
N 5490 520 5550 520 {}
N 5615 520 5675 520 {}
N 5715 520 5775 520 {}
N 5840 520 5900 520 {}
N 5940 520 6000 520 {}
N 6070 520 6130 520 {}
N 6170 520 6230 520 {}
N 6295 520 6355 520 {}
N 6395 520 6455 520 {}
N 6520 520 6580 520 {}
N 6620 520 6680 520 {}
N 6745 520 6805 520 {}
N 6845 520 6905 520 {}
N 1210 610 1455 610 {}
N 1180 780 1240 780 {}
N 1280 780 1340 780 {}
N 1435 780 1465 780 {}
N 1505 780 1565 780 {}
N 1210 840 1435 840 {}
N -3750 920 7325 920 {}
C {devices/lab_wire.sym} 1005 90 2 0 {name=l0 lab=casc_src_n}
C {devices/lab_wire.sym} 1515 90 2 0 {name=l1 lab=casc_src_p}
C {devices/lab_wire.sym} 1515 170 0 1 {name=l2 lab=casc_src_p}
C {devices/lab_wire.sym} -635 520 0 0 {name=l3 lab=clk_chfb}
C {devices/lab_wire.sym} 5165 520 0 0 {name=l4 lab=clk_chfb}
C {devices/lab_wire.sym} 5390 520 0 0 {name=l5 lab=clk_chfb}
C {devices/lab_wire.sym} -2440 520 0 0 {name=l6 lab=clk_chfb_not}
C {devices/lab_wire.sym} 3355 520 0 0 {name=l7 lab=clk_chfb_not}
C {devices/lab_wire.sym} 3580 520 0 0 {name=l8 lab=clk_chfb_not}
C {devices/lab_wire.sym} -1085 520 0 0 {name=l9 lab=clk_chin}
C {devices/lab_wire.sym} 4710 520 0 0 {name=l10 lab=clk_chin}
C {devices/lab_wire.sym} 4940 520 0 0 {name=l11 lab=clk_chin}
C {devices/lab_wire.sym} -1990 520 0 0 {name=l12 lab=clk_chin_not}
C {devices/lab_wire.sym} 3810 520 0 0 {name=l13 lab=clk_chin_not}
C {devices/lab_wire.sym} 4035 520 0 0 {name=l14 lab=clk_chin_not}
C {devices/lab_wire.sym} 1330 520 0 1 {name=l15 lab=clk_chout}
C {devices/lab_wire.sym} 6295 520 0 0 {name=l16 lab=clk_chout}
C {devices/lab_wire.sym} 6745 520 0 0 {name=l17 lab=clk_chout}
C {devices/lab_wire.sym} 880 520 0 1 {name=l18 lab=clk_chout_not}
C {devices/lab_wire.sym} 1495 580 2 0 {name=l19 lab=clk_chout_not}
C {devices/lab_wire.sym} 6520 520 0 0 {name=l20 lab=clk_chout_not}
C {devices/lab_wire.sym} -1540 520 0 0 {name=l21 lab=clk_chpf}
C {devices/lab_wire.sym} 5615 520 0 0 {name=l22 lab=clk_chpf}
C {devices/lab_wire.sym} 5840 520 0 0 {name=l23 lab=clk_chpf}
C {devices/lab_wire.sym} -2895 520 0 0 {name=l24 lab=clk_chpf_not}
C {devices/lab_wire.sym} 4260 520 0 0 {name=l25 lab=clk_chpf_not}
C {devices/lab_wire.sym} 4485 520 0 0 {name=l26 lab=clk_chpf_not}
C {devices/lab_wire.sym} -2570 430 0 1 {name=l27 lab=fbch_n}
C {devices/lab_wire.sym} -760 430 0 1 {name=l28 lab=fbch_n}
C {devices/lab_wire.sym} 1905 490 0 0 {name=l29 lab=fbch_n}
C {devices/lab_wire.sym} 3680 430 0 1 {name=l30 lab=fbch_n}
C {devices/lab_wire.sym} 5490 430 0 1 {name=l31 lab=fbch_n}
C {devices/lab_wire.sym} -2340 430 0 1 {name=l32 lab=fbch_p}
C {devices/lab_wire.sym} -535 430 0 1 {name=l33 lab=fbch_p}
C {devices/lab_wire.sym} 1645 430 0 1 {name=l34 lab=fbch_p}
C {devices/lab_wire.sym} 5265 430 0 1 {name=l35 lab=fbch_p}
C {devices/lab_wire.sym} 1005 610 2 0 {name=l36 lab=fold_n}
C {devices/lab_wire.sym} 1505 690 0 1 {name=l37 lab=fold_n}
C {devices/lab_wire.sym} 2180 350 2 0 {name=l38 lab=fold_n}
C {devices/lab_wire.sym} 600 350 2 0 {name=l39 lab=fold_p}
C {devices/lab_wire.sym} 1280 690 0 1 {name=l40 lab=fold_p}
C {devices/lab_wire.sym} 6170 610 2 0 {name=l41 lab=fold_p}
C {devices/lab_wire.sym} -3330 610 2 0 {name=l42 lab=g2_n}
C {devices/lab_wire.sym} 780 610 2 0 {name=l43 lab=g2_n}
C {devices/lab_wire.sym} 1230 550 0 0 {name=l44 lab=g2_n}
C {devices/lab_wire.sym} 1825 260 0 0 {name=l45 lab=g2_n}
C {devices/lab_wire.sym} 2680 490 0 0 {name=l46 lab=g2_n}
C {devices/lab_wire.sym} 6845 610 2 0 {name=l47 lab=g2_n}
C {devices/lab_wire.sym} 180 430 0 1 {name=l48 lab=g2_p}
C {devices/lab_wire.sym} 550 610 2 0 {name=l49 lab=g2_p}
C {devices/lab_wire.sym} 1180 260 0 0 {name=l50 lab=g2_p}
C {devices/lab_wire.sym} 6395 610 2 0 {name=l51 lab=g2_p}
C {devices/lab_wire.sym} 6620 610 2 0 {name=l52 lab=g2_p}
C {devices/lab_wire.sym} -2115 610 2 0 {name=l53 lab=inch_n}
C {devices/lab_wire.sym} -985 610 2 0 {name=l54 lab=inch_n}
C {devices/lab_wire.sym} 2160 610 2 0 {name=l55 lab=inch_n}
C {devices/lab_wire.sym} 2930 610 2 0 {name=l56 lab=inch_n}
C {devices/lab_wire.sym} 3910 610 2 0 {name=l57 lab=inch_n}
C {devices/lab_wire.sym} 5040 610 2 0 {name=l58 lab=inch_n}
C {devices/lab_wire.sym} -1890 610 2 0 {name=l59 lab=inch_p}
C {devices/lab_wire.sym} -1210 610 2 0 {name=l60 lab=inch_p}
C {devices/lab_wire.sym} -80 610 2 0 {name=l61 lab=inch_p}
C {devices/lab_wire.sym} 2420 610 2 0 {name=l62 lab=inch_p}
C {devices/lab_wire.sym} 4135 610 2 0 {name=l63 lab=inch_p}
C {devices/lab_wire.sym} 4810 610 2 0 {name=l64 lab=inch_p}
C {devices/lab_wire.sym} 550 430 0 1 {name=l65 lab=out1_n}
C {devices/lab_wire.sym} 780 430 0 1 {name=l66 lab=out1_n}
C {devices/lab_wire.sym} 1005 350 2 0 {name=l67 lab=out1_n}
C {devices/lab_wire.sym} 1005 430 0 1 {name=l68 lab=out1_n}
C {devices/lab_wire.sym} 1230 430 0 1 {name=l69 lab=out1_n}
C {devices/lab_wire.sym} 1515 350 2 0 {name=l70 lab=out1_p}
C {devices/lab_wire.sym} -3020 430 0 1 {name=l71 lab=pfch_n}
C {devices/lab_wire.sym} -1665 430 0 1 {name=l72 lab=pfch_n}
C {devices/lab_wire.sym} 2930 490 0 0 {name=l73 lab=pfch_n}
C {devices/lab_wire.sym} 4585 430 0 1 {name=l74 lab=pfch_n}
C {devices/lab_wire.sym} 5940 430 0 1 {name=l75 lab=pfch_n}
C {devices/lab_wire.sym} -2795 430 0 1 {name=l76 lab=pfch_p}
C {devices/lab_wire.sym} -1440 430 0 1 {name=l77 lab=pfch_p}
C {devices/lab_wire.sym} -80 430 0 1 {name=l78 lab=pfch_p}
C {devices/lab_wire.sym} 4360 430 0 1 {name=l79 lab=pfch_p}
C {devices/lab_wire.sym} 5715 430 0 1 {name=l80 lab=pfch_p}
C {devices/lab_wire.sym} 1280 90 2 0 {name=l81 lab=tail}
C {devices/lab_wire.sym} 1180 780 0 0 {name=l82 lab=vb1}
C {devices/lab_wire.sym} 1105 520 0 1 {name=l83 lab=vb2}
C {devices/lab_wire.sym} 6070 520 0 0 {name=l84 lab=vb2}
C {devices/lab_wire.sym} 1105 260 0 1 {name=l85 lab=vb3}
C {devices/lab_wire.sym} 1415 260 0 0 {name=l86 lab=vb3}
C {devices/lab_wire.sym} 500 0 0 0 {name=l87 lab=vb4}
C {devices/lab_wire.sym} 1825 0 0 0 {name=l88 lab=vb4}
C {devices/lab_wire.sym} -1890 430 0 1 {name=l89 lab=vinn}
C {devices/lab_wire.sym} -985 430 0 1 {name=l90 lab=vinn}
C {devices/lab_wire.sym} 3910 430 0 1 {name=l91 lab=vinn}
C {devices/lab_wire.sym} 4810 430 0 1 {name=l92 lab=vinn}
C {devices/lab_wire.sym} -2115 430 0 1 {name=l93 lab=vinp}
C {devices/lab_wire.sym} -1210 430 0 1 {name=l94 lab=vinp}
C {devices/lab_wire.sym} 4135 430 0 1 {name=l95 lab=vinp}
C {devices/lab_wire.sym} 5040 430 0 1 {name=l96 lab=vinp}
C {devices/lab_wire.sym} -2795 610 2 0 {name=l97 lab=voutn}
C {devices/lab_wire.sym} -2340 610 2 0 {name=l98 lab=voutn}
C {devices/lab_wire.sym} -1665 610 2 0 {name=l99 lab=voutn}
C {devices/lab_wire.sym} -760 610 2 0 {name=l100 lab=voutn}
C {devices/lab_wire.sym} 1925 170 0 1 {name=l101 lab=voutn}
C {devices/lab_wire.sym} 2680 610 2 0 {name=l102 lab=voutn}
C {devices/lab_wire.sym} 3680 610 2 0 {name=l103 lab=voutn}
C {devices/lab_wire.sym} 4585 610 2 0 {name=l104 lab=voutn}
C {devices/lab_wire.sym} 5265 610 2 0 {name=l105 lab=voutn}
C {devices/lab_wire.sym} 5715 610 2 0 {name=l106 lab=voutn}
C {devices/lab_wire.sym} -3020 610 2 0 {name=l107 lab=voutp}
C {devices/lab_wire.sym} -2570 610 2 0 {name=l108 lab=voutp}
C {devices/lab_wire.sym} -1440 610 2 0 {name=l109 lab=voutp}
C {devices/lab_wire.sym} -535 610 2 0 {name=l110 lab=voutp}
C {devices/lab_wire.sym} 180 610 2 0 {name=l111 lab=voutp}
C {devices/lab_wire.sym} 1280 170 0 1 {name=l112 lab=voutp}
C {devices/lab_wire.sym} 1925 90 2 0 {name=l113 lab=voutp}
C {devices/lab_wire.sym} 3455 610 2 0 {name=l114 lab=voutp}
C {devices/lab_wire.sym} 4360 610 2 0 {name=l115 lab=voutp}
C {devices/lab_wire.sym} 5490 610 2 0 {name=l116 lab=voutp}
C {devices/lab_wire.sym} 5940 610 2 0 {name=l117 lab=voutp}
C {devices/lab_wire.sym} -330 610 2 0 {name=l118 lab=vref}
C {devices/lab_wire.sym} 3185 610 2 0 {name=l119 lab=vref}
C {devices/lab_wire.sym} -330 430 0 1 {name=l120 lab=vsum_n}
C {devices/lab_wire.sym} 1645 610 2 0 {name=l121 lab=vsum_n}
C {devices/lab_wire.sym} 2080 260 0 0 {name=l122 lab=vsum_n}
C {devices/lab_wire.sym} 2160 490 0 0 {name=l123 lab=vsum_n}
C {devices/lab_wire.sym} 500 260 0 0 {name=l124 lab=vsum_p}
C {devices/lab_wire.sym} 1905 610 2 0 {name=l125 lab=vsum_p}
C {devices/lab_wire.sym} 2420 490 0 0 {name=l126 lab=vsum_p}
C {devices/lab_wire.sym} 3185 490 0 0 {name=l127 lab=vsum_p}
C {devices/lab_wire.sym} 1280 0 0 0 {name=l128 lab=vdd}
C {devices/lab_wire.sym} 945 354 2 0 {name=l129 lab=vdd}
C {devices/lab_wire.sym} 1515 260 0 0 {name=l130 lab=vdd}
C {devices/lab_wire.sym} 720 614 2 0 {name=l131 lab=vdd}
C {devices/lab_wire.sym} 6680 614 2 0 {name=l132 lab=vdd}
C {devices/lab_wire.sym} 660 354 2 0 {name=l133 lab=vdd}
C {devices/lab_wire.sym} 3515 614 2 0 {name=l134 lab=vdd}
C {devices/lab_wire.sym} 3740 614 2 0 {name=l135 lab=vdd}
C {devices/lab_wire.sym} 3970 614 2 0 {name=l136 lab=vdd}
C {devices/lab_wire.sym} 4195 614 2 0 {name=l137 lab=vdd}
C {devices/lab_wire.sym} 4420 614 2 0 {name=l138 lab=vdd}
C {devices/lab_wire.sym} 2240 354 2 0 {name=l139 lab=vdd}
C {devices/lab_wire.sym} 4645 614 2 0 {name=l140 lab=vdd}
C {devices/lab_wire.sym} 490 614 2 0 {name=l141 lab=vdd}
C {devices/lab_wire.sym} 6905 614 2 0 {name=l142 lab=vdd}
C {devices/lab_wire.sym} 4870 614 2 0 {name=l143 lab=vdd}
C {devices/lab_wire.sym} 5100 614 2 0 {name=l144 lab=vdd}
C {devices/lab_wire.sym} 5325 614 2 0 {name=l145 lab=vdd}
C {devices/lab_wire.sym} 5550 614 2 0 {name=l146 lab=vdd}
C {devices/lab_wire.sym} 5775 614 2 0 {name=l147 lab=vdd}
C {devices/lab_wire.sym} 6000 614 2 0 {name=l148 lab=vdd}
C {devices/lab_wire.sym} 945 94 2 0 {name=l149 lab=vdd}
C {devices/lab_wire.sym} 1575 94 2 0 {name=l150 lab=vdd}
C {devices/lab_wire.sym} 1985 94 2 0 {name=l151 lab=vdd}
C {devices/lab_wire.sym} 660 94 2 0 {name=l152 lab=vdd}
C {devices/lab_wire.sym} 6230 614 2 0 {name=l153 lab=vss}
C {devices/lab_wire.sym} 945 614 2 0 {name=l154 lab=vss}
C {devices/lab_wire.sym} 1340 354 2 0 {name=l155 lab=vss}
C {devices/lab_wire.sym} 1985 354 2 0 {name=l156 lab=vss}
C {devices/lab_wire.sym} 1170 614 2 0 {name=l157 lab=vss}
C {devices/lab_wire.sym} 6455 614 2 0 {name=l158 lab=vss}
C {devices/lab_wire.sym} -475 614 2 0 {name=l159 lab=vss}
C {devices/lab_wire.sym} -700 614 2 0 {name=l160 lab=vss}
C {devices/lab_wire.sym} -925 614 2 0 {name=l161 lab=vss}
C {devices/lab_wire.sym} -1150 614 2 0 {name=l162 lab=vss}
C {devices/lab_wire.sym} -1380 614 2 0 {name=l163 lab=vss}
C {devices/lab_wire.sym} -1605 614 2 0 {name=l164 lab=vss}
C {devices/lab_wire.sym} 1395 614 2 0 {name=l165 lab=vss}
C {devices/lab_wire.sym} -3270 614 2 0 {name=l166 lab=vss}
C {devices/lab_wire.sym} -1830 614 2 0 {name=l167 lab=vss}
C {devices/lab_wire.sym} -2055 614 2 0 {name=l168 lab=vss}
C {devices/lab_wire.sym} 1340 874 2 0 {name=l169 lab=vss}
C {devices/lab_wire.sym} -2280 614 2 0 {name=l170 lab=vss}
C {devices/lab_wire.sym} -2510 614 2 0 {name=l171 lab=vss}
C {devices/lab_wire.sym} -2735 614 2 0 {name=l172 lab=vss}
C {devices/lab_wire.sym} -2960 614 2 0 {name=l173 lab=vss}
C {devices/lab_wire.sym} 1565 874 2 0 {name=l174 lab=vss}
C {devices/lab_wire.sym} -3690 690 0 1 {name=l175 lab=vb1}
C {devices/lab_wire.sym} -3690 870 2 0 {name=l176 lab=vss}
C {devices/lab_wire.sym} -3690 610 2 0 {name=l177 lab=vss}
C {devices/lab_wire.sym} -3690 350 2 0 {name=l178 lab=vss}
C {devices/lab_wire.sym} -3690 90 2 0 {name=l179 lab=vss}
C {devices/lab_wire.sym} -3690 430 0 1 {name=l180 lab=vb2}
C {devices/lab_wire.sym} -3690 170 0 1 {name=l181 lab=vb3}
C {devices/lab_wire.sym} -3690 -90 0 1 {name=l182 lab=vb4}
C {devices/lab_wire.sym} 1280 350 2 0 {name=l183 lab=vss}
C {devices/ipin.sym} -3460 520 0 0 {name=p0 lab=clk_chout_not}
C {devices/ipin.sym} -3150 520 0 0 {name=p1 lab=clk_chpf_not}
C {devices/ipin.sym} -2700 520 0 0 {name=p2 lab=clk_chfb_not}
C {devices/ipin.sym} -2245 520 0 0 {name=p3 lab=clk_chin_not}
C {devices/ipin.sym} -1795 520 0 0 {name=p4 lab=clk_chpf}
C {devices/ipin.sym} -1340 520 0 0 {name=p5 lab=clk_chin}
C {devices/ipin.sym} -890 520 0 0 {name=p6 lab=clk_chfb}
C {devices/ipin.sym} 620 520 0 0 {name=p7 lab=clk_chout}
C {devices/iopin.sym} -3750 -140 0 0 {name=p8 lab=vdd}
C {devices/iopin.sym} -3750 920 0 0 {name=p9 lab=vss}
C {devices/opin.sym} 600 60 0 0 {name=p10 lab=voutn}
C {devices/iopin.sym} -330 1060 0 0 {name=p11 lab=vref}
C {devices/opin.sym} 7465 30 0 0 {name=p12 lab=voutp}
C {devices/opin.sym} 7465 490 0 0 {name=p13 lab=vinp}
C {devices/opin.sym} 7465 610 0 0 {name=p14 lab=vinn}
B 8 320 442 1320 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 320 424 0 0 0.3 0.3 {layer=8}
B 10 6305 442 7080 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 6305 424 0 0 0.3 0.3 {layer=10}
B 12 510 182 2616 338 {fill=0}
T {PMOS Differential Pair} 510 164 0 0 0.3 0.3 {layer=12}
B 21 -625 442 3915 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -625 424 0 0 0.3 0.3 {layer=21}
B 15 -1530 442 -75 598 {fill=0}
T {NMOS Differential Pair} -1530 424 0 0 0.3 0.3 {layer=15}
B 13 -2660 442 -75 598 {fill=0}
T {NMOS Differential Pair} -2660 424 0 0 0.3 0.3 {layer=13}
B 18 -3110 442 -75 598 {fill=0}
T {NMOS Differential Pair} -3110 424 0 0 0.3 0.3 {layer=18}
B 20 -850 442 4140 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -850 424 0 0 0.3 0.3 {layer=20}
B 8 -1755 442 -300 598 {fill=0}
T {NMOS Differential Pair} -1755 424 0 0 0.3 0.3 {layer=8}
B 10 -2430 442 -300 598 {fill=0}
T {NMOS Differential Pair} -2430 424 0 0 0.3 0.3 {layer=10}
B 12 -2885 442 -300 598 {fill=0}
T {NMOS Differential Pair} -2885 424 0 0 0.3 0.3 {layer=12}
B 21 -1075 442 4370 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1075 424 0 0 0.3 0.3 {layer=21}
B 15 -1300 442 4595 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1300 424 0 0 0.3 0.3 {layer=15}
B 13 -1530 442 4820 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1530 400 0 0 0.3 0.3 {layer=13}
B 18 -2660 442 -980 598 {fill=0}
T {NMOS Differential Pair} -2660 400 0 0 0.3 0.3 {layer=18}
B 20 -3110 442 -980 598 {fill=0}
T {NMOS Differential Pair} -3110 400 0 0 0.3 0.3 {layer=20}
B 8 -1755 442 5045 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1755 400 0 0 0.3 0.3 {layer=8}
B 10 -2430 442 -1205 598 {fill=0}
T {NMOS Differential Pair} -2430 400 0 0 0.3 0.3 {layer=10}
B 12 -2885 442 -1205 598 {fill=0}
T {NMOS Differential Pair} -2885 400 0 0 0.3 0.3 {layer=12}
B 21 90 442 1545 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 90 424 0 0 0.3 0.3 {layer=21}
B 15 -3420 442 7305 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -3420 424 0 0 0.3 0.3 {layer=15}
B 13 -1980 442 5270 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1980 424 0 0 0.3 0.3 {layer=13}
B 18 -2205 442 5500 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2205 424 0 0 0.3 0.3 {layer=18}
B 20 -2430 442 5725 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2430 376 0 0 0.3 0.3 {layer=20}
B 8 -2885 442 -1880 598 {fill=0}
T {NMOS Differential Pair} -2885 376 0 0 0.3 0.3 {layer=8}
B 10 -2660 442 5950 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2660 376 0 0 0.3 0.3 {layer=10}
B 12 -3110 442 -2110 598 {fill=0}
T {NMOS Differential Pair} -3110 376 0 0 0.3 0.3 {layer=12}
B 21 -2885 442 6175 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2885 352 0 0 0.3 0.3 {layer=21}
B 15 -3110 442 6400 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -3110 352 0 0 0.3 0.3 {layer=15}
