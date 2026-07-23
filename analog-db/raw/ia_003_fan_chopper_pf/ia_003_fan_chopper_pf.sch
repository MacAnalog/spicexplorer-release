v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_003_fan_chopper_pf} -3730 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 885 520 0 0 {name=CFB1 value='x_dut_cfb1_value'}
C {devices/capa_np.sym} 1105 520 0 0 {name=CFB2 value='x_dut_cfb2_value'}
C {devices/capa_np.sym} 1325 520 0 0 {name=CIN1 value='x_dut_cin1_value'}
C {devices/capa_np.sym} 1545 520 0 0 {name=CIN2 value='x_dut_cin2_value'}
C {devices/capa_np.sym} -350 520 0 0 {name=CM1 value='x_dut_cm1_value'}
C {devices/capa_np.sym} 1765 520 0 0 {name=CM2 value='x_dut_cm2_value'}
C {devices/capa_np.sym} -570 520 0 0 {name=CPF1 value='x_dut_cpf1_value'}
C {devices/capa_np.sym} 1980 520 0 0 {name=CPF2 value='x_dut_cpf2_value'}
C {devices/res_np.sym} -785 520 0 0 {name=RB1 value='x_dut_rb1_value'}
C {devices/res_np.sym} 2200 520 0 0 {name=RB2 value='x_dut_rb2_value'}
C {devices/vsource_np.sym} -3690 780 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -3690 520 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -3690 260 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -3690 0 0 0 {name=VB4 value="dc {vb4}"}
C {devices/sg13_lv_pmos_np.sym} 540 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 340 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 735 260 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} 4665 520 0 0 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 340 520 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 540 260 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 1105 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 530 520 0 1 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} 150 520 0 1 {name=M17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 4855 520 0 0 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_pmos_np.sym} 5040 520 0 0 {name=M19 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} -25 260 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} -970 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_pmos_np.sym} 2410 520 0 0 {name=M21 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} -1160 520 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} 2600 520 0 0 {name=M23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_nmos_np.sym} -1350 520 0 0 {name=M24 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_pmos_np.sym} 2785 520 0 0 {name=M25 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
C {devices/sg13_lv_nmos_np.sym} -1535 520 0 0 {name=M26 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm26_w l=x_dut_xm26_l m=x_dut_xm26_m}
C {devices/sg13_lv_pmos_np.sym} 2975 520 0 0 {name=M27 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm27_w l=x_dut_xm27_l m=x_dut_xm27_m}
C {devices/sg13_lv_nmos_np.sym} -1725 520 0 0 {name=M28 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm28_w l=x_dut_xm28_l m=x_dut_xm28_m}
C {devices/sg13_lv_pmos_np.sym} 3160 520 0 0 {name=M29 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm29_w l=x_dut_xm29_l m=x_dut_xm29_m}
C {devices/sg13_lv_pmos_np.sym} 1325 260 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} -1910 520 0 0 {name=M30 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm30_w l=x_dut_xm30_l m=x_dut_xm30_m}
C {devices/sg13_lv_pmos_np.sym} 3350 520 0 0 {name=M31 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm31_w l=x_dut_xm31_l m=x_dut_xm31_m}
C {devices/sg13_lv_nmos_np.sym} 715 520 0 1 {name=M32 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm32_w l=x_dut_xm32_l m=x_dut_xm32_m}
C {devices/sg13_lv_pmos_np.sym} -35 520 0 1 {name=M33 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm33_w l=x_dut_xm33_l m=x_dut_xm33_m}
C {devices/sg13_lv_nmos_np.sym} -3350 520 0 0 {name=M34 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm34_w l=x_dut_xm34_l m=x_dut_xm34_m}
C {devices/sg13_lv_pmos_np.sym} 5230 520 0 0 {name=M35 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm35_w l=x_dut_xm35_l m=x_dut_xm35_m}
C {devices/sg13_lv_nmos_np.sym} -2100 520 0 0 {name=M36 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm36_w l=x_dut_xm36_l m=x_dut_xm36_m}
C {devices/sg13_lv_pmos_np.sym} 3540 520 0 0 {name=M37 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm37_w l=x_dut_xm37_l m=x_dut_xm37_m}
C {devices/sg13_lv_nmos_np.sym} -2290 520 0 0 {name=M38 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm38_w l=x_dut_xm38_l m=x_dut_xm38_m}
C {devices/sg13_lv_pmos_np.sym} 3725 520 0 0 {name=M39 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm39_w l=x_dut_xm39_l m=x_dut_xm39_m}
C {devices/sg13_lv_nmos_np.sym} 540 780 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} -2475 520 0 0 {name=M40 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm40_w l=x_dut_xm40_l m=x_dut_xm40_m}
C {devices/sg13_lv_pmos_np.sym} 3915 520 0 0 {name=M41 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm41_w l=x_dut_xm41_l m=x_dut_xm41_m}
C {devices/sg13_lv_nmos_np.sym} -2665 520 0 0 {name=M42 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm42_w l=x_dut_xm42_l m=x_dut_xm42_m}
C {devices/sg13_lv_pmos_np.sym} 4100 520 0 0 {name=M43 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm43_w l=x_dut_xm43_l m=x_dut_xm43_m}
C {devices/sg13_lv_nmos_np.sym} -2850 520 0 0 {name=M44 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm44_w l=x_dut_xm44_l m=x_dut_xm44_m}
C {devices/sg13_lv_pmos_np.sym} 4290 520 0 0 {name=M45 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm45_w l=x_dut_xm45_l m=x_dut_xm45_m}
C {devices/sg13_lv_nmos_np.sym} -3040 520 0 0 {name=M46 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm46_w l=x_dut_xm46_l m=x_dut_xm46_m}
C {devices/sg13_lv_pmos_np.sym} 4480 520 0 0 {name=M47 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm47_w l=x_dut_xm47_l m=x_dut_xm47_m}
C {devices/sg13_lv_nmos_np.sym} 725 780 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 735 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 1105 0 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} -25 0 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -3690 -90 -3690 -30 {}
N -3690 30 -3690 90 {}
N -3690 170 -3690 230 {}
N -3690 290 -3690 350 {}
N -3690 430 -3690 490 {}
N -3690 550 -3690 610 {}
N -3690 690 -3690 750 {}
N -3690 810 -3690 870 {}
N -3330 430 -3330 490 {}
N -3330 550 -3330 610 {}
N -3270 520 -3270 614 {}
N -3060 460 -3060 520 {}
N -3020 430 -3020 490 {}
N -3020 550 -3020 610 {}
N -2960 520 -2960 614 {}
N -2870 460 -2870 520 {}
N -2830 430 -2830 490 {}
N -2830 550 -2830 610 {}
N -2770 520 -2770 614 {}
N -2685 460 -2685 520 {}
N -2645 430 -2645 490 {}
N -2645 550 -2645 610 {}
N -2585 520 -2585 614 {}
N -2495 460 -2495 520 {}
N -2455 430 -2455 490 {}
N -2455 550 -2455 610 {}
N -2395 520 -2395 614 {}
N -2310 460 -2310 520 {}
N -2270 430 -2270 490 {}
N -2270 550 -2270 610 {}
N -2210 520 -2210 614 {}
N -2120 460 -2120 520 {}
N -2080 430 -2080 490 {}
N -2080 550 -2080 610 {}
N -2020 520 -2020 614 {}
N -1930 460 -1930 520 {}
N -1890 430 -1890 490 {}
N -1890 550 -1890 610 {}
N -1830 520 -1830 614 {}
N -1745 460 -1745 520 {}
N -1705 430 -1705 490 {}
N -1705 550 -1705 610 {}
N -1645 520 -1645 614 {}
N -1555 460 -1555 520 {}
N -1515 430 -1515 490 {}
N -1515 550 -1515 610 {}
N -1455 520 -1455 614 {}
N -1370 460 -1370 520 {}
N -1330 430 -1330 490 {}
N -1330 550 -1330 610 {}
N -1270 520 -1270 614 {}
N -1180 460 -1180 520 {}
N -1140 430 -1140 490 {}
N -1140 550 -1140 610 {}
N -1080 520 -1080 614 {}
N -990 460 -990 520 {}
N -950 430 -950 490 {}
N -950 550 -950 610 {}
N -890 520 -890 614 {}
N -785 430 -785 490 {}
N -785 550 -785 610 {}
N -570 430 -570 490 {}
N -570 550 -570 610 {}
N -350 430 -350 490 {}
N -350 550 -350 610 {}
N -115 520 -115 614 {}
N -55 430 -55 490 {}
N -55 550 -55 610 {}
N -15 520 -15 580 {}
N -5 -140 -5 -30 {}
N -5 30 -5 90 {}
N -5 170 -5 230 {}
N -5 290 -5 350 {}
N 55 0 55 94 {}
N 55 260 55 354 {}
N 70 520 70 614 {}
N 130 430 130 490 {}
N 130 550 130 610 {}
N 170 520 170 580 {}
N 260 0 260 94 {}
N 260 260 260 354 {}
N 260 520 260 614 {}
N 320 -140 320 -30 {}
N 320 30 320 90 {}
N 320 170 320 230 {}
N 320 290 320 350 {}
N 320 430 320 490 {}
N 320 550 320 610 {}
N 360 520 360 580 {}
N 450 520 450 614 {}
N 510 430 510 490 {}
N 510 550 510 610 {}
N 550 520 550 580 {}
N 560 -140 560 -30 {}
N 560 30 560 90 {}
N 560 170 560 230 {}
N 560 290 560 350 {}
N 560 690 560 750 {}
N 560 810 560 920 {}
N 620 0 620 94 {}
N 620 260 620 354 {}
N 620 780 620 874 {}
N 635 520 635 614 {}
N 695 430 695 490 {}
N 695 550 695 610 {}
N 705 720 705 780 {}
N 715 -60 715 0 {}
N 715 200 715 260 {}
N 735 520 735 580 {}
N 745 690 745 750 {}
N 745 810 745 920 {}
N 755 -140 755 -30 {}
N 755 30 755 90 {}
N 755 170 755 230 {}
N 755 290 755 350 {}
N 805 780 805 874 {}
N 815 0 815 94 {}
N 815 260 815 354 {}
N 885 430 885 490 {}
N 885 550 885 610 {}
N 1105 430 1105 490 {}
N 1105 550 1105 610 {}
N 1125 -140 1125 -30 {}
N 1125 30 1125 90 {}
N 1125 170 1125 230 {}
N 1125 290 1125 920 {}
N 1185 0 1185 94 {}
N 1185 260 1185 354 {}
N 1305 200 1305 260 {}
N 1325 430 1325 490 {}
N 1325 550 1325 610 {}
N 1345 170 1345 230 {}
N 1345 290 1345 350 {}
N 1405 260 1405 354 {}
N 1545 430 1545 490 {}
N 1545 550 1545 610 {}
N 1765 430 1765 490 {}
N 1765 550 1765 610 {}
N 1980 430 1980 490 {}
N 1980 550 1980 610 {}
N 2200 430 2200 490 {}
N 2200 550 2200 610 {}
N 2390 460 2390 520 {}
N 2430 430 2430 490 {}
N 2430 550 2430 610 {}
N 2490 520 2490 614 {}
N 2580 460 2580 520 {}
N 2620 430 2620 490 {}
N 2620 550 2620 610 {}
N 2680 520 2680 614 {}
N 2765 460 2765 520 {}
N 2805 430 2805 490 {}
N 2805 550 2805 610 {}
N 2865 520 2865 614 {}
N 2955 460 2955 520 {}
N 2995 430 2995 490 {}
N 2995 550 2995 610 {}
N 3055 520 3055 614 {}
N 3140 460 3140 520 {}
N 3180 430 3180 490 {}
N 3180 550 3180 610 {}
N 3240 520 3240 614 {}
N 3330 460 3330 520 {}
N 3370 430 3370 490 {}
N 3370 550 3370 610 {}
N 3430 520 3430 614 {}
N 3520 460 3520 520 {}
N 3560 430 3560 490 {}
N 3560 550 3560 610 {}
N 3620 520 3620 614 {}
N 3705 460 3705 520 {}
N 3745 430 3745 490 {}
N 3745 550 3745 610 {}
N 3805 520 3805 614 {}
N 3895 460 3895 520 {}
N 3935 430 3935 490 {}
N 3935 550 3935 610 {}
N 3995 520 3995 614 {}
N 4080 460 4080 520 {}
N 4120 430 4120 490 {}
N 4120 550 4120 610 {}
N 4180 520 4180 614 {}
N 4270 460 4270 520 {}
N 4310 430 4310 490 {}
N 4310 550 4310 610 {}
N 4370 520 4370 614 {}
N 4460 460 4460 520 {}
N 4500 430 4500 490 {}
N 4500 550 4500 610 {}
N 4560 520 4560 614 {}
N 4645 460 4645 520 {}
N 4685 430 4685 490 {}
N 4685 550 4685 610 {}
N 4745 520 4745 614 {}
N 4875 460 4875 490 {}
N 4875 550 4875 610 {}
N 4935 520 4935 614 {}
N 5060 460 5060 490 {}
N 5060 550 5060 610 {}
N 5120 520 5120 614 {}
N 5250 460 5250 490 {}
N 5250 550 5250 610 {}
N 5310 520 5310 614 {}
N -3750 -140 5445 -140 {}
N -105 0 -45 0 {}
N -5 0 55 0 {}
N 260 0 320 0 {}
N 360 0 520 0 {}
N 560 0 620 0 {}
N 685 0 715 0 {}
N 755 0 815 0 {}
N 1025 0 1085 0 {}
N 1125 0 1185 0 {}
N -105 260 -45 260 {}
N -5 260 55 260 {}
N 260 260 320 260 {}
N 360 260 420 260 {}
N 460 260 520 260 {}
N 560 260 620 260 {}
N 685 260 715 260 {}
N 755 260 815 260 {}
N 1025 260 1085 260 {}
N 1125 260 1185 260 {}
N 1275 260 1305 260 {}
N 1345 260 1405 260 {}
N 4685 460 5250 460 {}
N -3430 520 -3370 520 {}
N -3330 520 -3270 520 {}
N -3090 520 -3060 520 {}
N -3020 520 -2960 520 {}
N -2900 520 -2870 520 {}
N -2830 520 -2770 520 {}
N -2715 520 -2685 520 {}
N -2645 520 -2585 520 {}
N -2525 520 -2495 520 {}
N -2455 520 -2395 520 {}
N -2340 520 -2310 520 {}
N -2270 520 -2210 520 {}
N -2150 520 -2120 520 {}
N -2080 520 -2020 520 {}
N -1960 520 -1930 520 {}
N -1890 520 -1830 520 {}
N -1775 520 -1745 520 {}
N -1705 520 -1645 520 {}
N -1585 520 -1555 520 {}
N -1515 520 -1455 520 {}
N -1400 520 -1370 520 {}
N -1330 520 -1270 520 {}
N -1210 520 -1180 520 {}
N -1140 520 -1080 520 {}
N -1020 520 -990 520 {}
N -950 520 -890 520 {}
N -115 520 -55 520 {}
N -15 520 15 520 {}
N 70 520 130 520 {}
N 170 520 200 520 {}
N 260 520 320 520 {}
N 360 520 390 520 {}
N 450 520 510 520 {}
N 550 520 580 520 {}
N 635 520 695 520 {}
N 735 520 765 520 {}
N 2360 520 2390 520 {}
N 2430 520 2490 520 {}
N 2550 520 2580 520 {}
N 2620 520 2680 520 {}
N 2735 520 2765 520 {}
N 2805 520 2865 520 {}
N 2925 520 2955 520 {}
N 2995 520 3055 520 {}
N 3110 520 3140 520 {}
N 3180 520 3240 520 {}
N 3300 520 3330 520 {}
N 3370 520 3430 520 {}
N 3490 520 3520 520 {}
N 3560 520 3620 520 {}
N 3675 520 3705 520 {}
N 3745 520 3805 520 {}
N 3865 520 3895 520 {}
N 3935 520 3995 520 {}
N 4050 520 4080 520 {}
N 4120 520 4180 520 {}
N 4240 520 4270 520 {}
N 4310 520 4370 520 {}
N 4430 520 4460 520 {}
N 4500 520 4560 520 {}
N 4615 520 4645 520 {}
N 4685 520 4745 520 {}
N 4805 520 4835 520 {}
N 4875 520 4935 520 {}
N 4990 520 5020 520 {}
N 5060 520 5120 520 {}
N 5180 520 5210 520 {}
N 5250 520 5310 520 {}
N 460 780 520 780 {}
N 560 780 620 780 {}
N 675 780 705 780 {}
N 745 780 805 780 {}
N -3750 920 5445 920 {}
C {devices/lab_wire.sym} -3750 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -3750 920 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 320 90 2 0 {name=l2 lab=casc_src_n}
C {devices/lab_wire.sym} 320 170 0 1 {name=l3 lab=casc_src_n}
C {devices/lab_wire.sym} 755 90 2 0 {name=l4 lab=casc_src_p}
C {devices/lab_wire.sym} 755 170 0 1 {name=l5 lab=casc_src_p}
C {devices/lab_wire.sym} -1180 460 0 1 {name=l6 lab=clk_chfb}
C {devices/lab_wire.sym} -990 460 0 1 {name=l7 lab=clk_chfb}
C {devices/lab_wire.sym} 3895 460 0 1 {name=l8 lab=clk_chfb}
C {devices/lab_wire.sym} 4080 460 0 1 {name=l9 lab=clk_chfb}
C {devices/lab_wire.sym} -2685 460 0 1 {name=l10 lab=clk_chfb_not}
C {devices/lab_wire.sym} -2495 460 0 1 {name=l11 lab=clk_chfb_not}
C {devices/lab_wire.sym} 2390 460 0 1 {name=l12 lab=clk_chfb_not}
C {devices/lab_wire.sym} 2580 460 0 1 {name=l13 lab=clk_chfb_not}
C {devices/lab_wire.sym} -1555 460 0 1 {name=l14 lab=clk_chin}
C {devices/lab_wire.sym} -1370 460 0 1 {name=l15 lab=clk_chin}
C {devices/lab_wire.sym} 3520 460 0 1 {name=l16 lab=clk_chin}
C {devices/lab_wire.sym} 3705 460 0 1 {name=l17 lab=clk_chin}
C {devices/lab_wire.sym} -2310 460 0 1 {name=l18 lab=clk_chin_not}
C {devices/lab_wire.sym} -2120 460 0 1 {name=l19 lab=clk_chin_not}
C {devices/lab_wire.sym} 2765 460 0 1 {name=l20 lab=clk_chin_not}
C {devices/lab_wire.sym} 2955 460 0 1 {name=l21 lab=clk_chin_not}
C {devices/lab_wire.sym} -15 580 2 0 {name=l22 lab=clk_chout}
C {devices/lab_wire.sym} 550 580 2 0 {name=l23 lab=clk_chout}
C {devices/lab_wire.sym} 4835 520 0 0 {name=l24 lab=clk_chout}
C {devices/lab_wire.sym} 5210 520 0 0 {name=l25 lab=clk_chout}
C {devices/lab_wire.sym} -3430 520 0 0 {name=l26 lab=clk_chout_not}
C {devices/lab_wire.sym} 170 580 2 0 {name=l27 lab=clk_chout_not}
C {devices/lab_wire.sym} 735 580 2 0 {name=l28 lab=clk_chout_not}
C {devices/lab_wire.sym} 5020 520 0 0 {name=l29 lab=clk_chout_not}
C {devices/lab_wire.sym} -1930 460 0 1 {name=l30 lab=clk_chpf}
C {devices/lab_wire.sym} -1745 460 0 1 {name=l31 lab=clk_chpf}
C {devices/lab_wire.sym} 4270 460 0 1 {name=l32 lab=clk_chpf}
C {devices/lab_wire.sym} 4460 460 0 1 {name=l33 lab=clk_chpf}
C {devices/lab_wire.sym} -3060 460 0 1 {name=l34 lab=clk_chpf_not}
C {devices/lab_wire.sym} -2870 460 0 1 {name=l35 lab=clk_chpf_not}
C {devices/lab_wire.sym} 3140 460 0 1 {name=l36 lab=clk_chpf_not}
C {devices/lab_wire.sym} 3330 460 0 1 {name=l37 lab=clk_chpf_not}
C {devices/lab_wire.sym} -2645 430 0 1 {name=l38 lab=fbch_n}
C {devices/lab_wire.sym} -1140 430 0 1 {name=l39 lab=fbch_n}
C {devices/lab_wire.sym} 1105 430 0 1 {name=l40 lab=fbch_n}
C {devices/lab_wire.sym} 2620 430 0 1 {name=l41 lab=fbch_n}
C {devices/lab_wire.sym} 4120 430 0 1 {name=l42 lab=fbch_n}
C {devices/lab_wire.sym} -2455 430 0 1 {name=l43 lab=fbch_p}
C {devices/lab_wire.sym} -950 430 0 1 {name=l44 lab=fbch_p}
C {devices/lab_wire.sym} 885 430 0 1 {name=l45 lab=fbch_p}
C {devices/lab_wire.sym} 2430 430 0 1 {name=l46 lab=fbch_p}
C {devices/lab_wire.sym} 3935 430 0 1 {name=l47 lab=fbch_p}
C {devices/lab_wire.sym} 320 610 2 0 {name=l48 lab=fold_n}
C {devices/lab_wire.sym} 745 690 0 1 {name=l49 lab=fold_n}
C {devices/lab_wire.sym} 1345 350 2 0 {name=l50 lab=fold_n}
C {devices/lab_wire.sym} -5 350 2 0 {name=l51 lab=fold_p}
C {devices/lab_wire.sym} 560 690 0 1 {name=l52 lab=fold_p}
C {devices/lab_wire.sym} 4685 610 2 0 {name=l53 lab=fold_p}
C {devices/lab_wire.sym} -3330 610 2 0 {name=l54 lab=g2_n}
C {devices/lab_wire.sym} 130 610 2 0 {name=l55 lab=g2_n}
C {devices/lab_wire.sym} 510 610 2 0 {name=l56 lab=g2_n}
C {devices/lab_wire.sym} 1025 260 0 0 {name=l57 lab=g2_n}
C {devices/lab_wire.sym} 1765 430 0 1 {name=l58 lab=g2_n}
C {devices/lab_wire.sym} 5250 610 2 0 {name=l59 lab=g2_n}
C {devices/lab_wire.sym} -350 430 0 1 {name=l60 lab=g2_p}
C {devices/lab_wire.sym} -55 610 2 0 {name=l61 lab=g2_p}
C {devices/lab_wire.sym} 460 260 0 0 {name=l62 lab=g2_p}
C {devices/lab_wire.sym} 695 610 2 0 {name=l63 lab=g2_p}
C {devices/lab_wire.sym} 4875 610 2 0 {name=l64 lab=g2_p}
C {devices/lab_wire.sym} 5060 610 2 0 {name=l65 lab=g2_p}
C {devices/lab_wire.sym} -2270 610 2 0 {name=l66 lab=inch_n}
C {devices/lab_wire.sym} -1330 610 2 0 {name=l67 lab=inch_n}
C {devices/lab_wire.sym} 1325 610 2 0 {name=l68 lab=inch_n}
C {devices/lab_wire.sym} 1980 610 2 0 {name=l69 lab=inch_n}
C {devices/lab_wire.sym} 2805 610 2 0 {name=l70 lab=inch_n}
C {devices/lab_wire.sym} 3745 610 2 0 {name=l71 lab=inch_n}
C {devices/lab_wire.sym} -2080 610 2 0 {name=l72 lab=inch_p}
C {devices/lab_wire.sym} -1515 610 2 0 {name=l73 lab=inch_p}
C {devices/lab_wire.sym} -570 610 2 0 {name=l74 lab=inch_p}
C {devices/lab_wire.sym} 1545 610 2 0 {name=l75 lab=inch_p}
C {devices/lab_wire.sym} 2995 610 2 0 {name=l76 lab=inch_p}
C {devices/lab_wire.sym} 3560 610 2 0 {name=l77 lab=inch_p}
C {devices/lab_wire.sym} -55 430 0 1 {name=l78 lab=out1_n}
C {devices/lab_wire.sym} 130 430 0 1 {name=l79 lab=out1_n}
C {devices/lab_wire.sym} 320 350 2 0 {name=l80 lab=out1_n}
C {devices/lab_wire.sym} 320 430 0 1 {name=l81 lab=out1_n}
C {devices/lab_wire.sym} 510 430 0 1 {name=l82 lab=out1_n}
C {devices/lab_wire.sym} 695 430 0 1 {name=l83 lab=out1_n}
C {devices/lab_wire.sym} -3330 430 0 1 {name=l84 lab=out1_p}
C {devices/lab_wire.sym} 755 350 2 0 {name=l85 lab=out1_p}
C {devices/lab_wire.sym} 4685 430 0 1 {name=l86 lab=out1_p}
C {devices/lab_wire.sym} -3020 430 0 1 {name=l87 lab=pfch_n}
C {devices/lab_wire.sym} -1890 430 0 1 {name=l88 lab=pfch_n}
C {devices/lab_wire.sym} 1980 430 0 1 {name=l89 lab=pfch_n}
C {devices/lab_wire.sym} 3370 430 0 1 {name=l90 lab=pfch_n}
C {devices/lab_wire.sym} 4500 430 0 1 {name=l91 lab=pfch_n}
C {devices/lab_wire.sym} -2830 430 0 1 {name=l92 lab=pfch_p}
C {devices/lab_wire.sym} -1705 430 0 1 {name=l93 lab=pfch_p}
C {devices/lab_wire.sym} -570 430 0 1 {name=l94 lab=pfch_p}
C {devices/lab_wire.sym} 3180 430 0 1 {name=l95 lab=pfch_p}
C {devices/lab_wire.sym} 4310 430 0 1 {name=l96 lab=pfch_p}
C {devices/lab_wire.sym} -5 170 0 1 {name=l97 lab=tail}
C {devices/lab_wire.sym} 560 90 2 0 {name=l98 lab=tail}
C {devices/lab_wire.sym} 1345 170 0 1 {name=l99 lab=tail}
C {devices/lab_wire.sym} 460 780 0 0 {name=l100 lab=vb1}
C {devices/lab_wire.sym} 705 720 0 1 {name=l101 lab=vb1}
C {devices/lab_wire.sym} 360 580 2 0 {name=l102 lab=vb2}
C {devices/lab_wire.sym} 4645 460 0 1 {name=l103 lab=vb2}
C {devices/lab_wire.sym} 420 260 0 1 {name=l104 lab=vb3}
C {devices/lab_wire.sym} 715 200 0 1 {name=l105 lab=vb3}
C {devices/lab_wire.sym} -105 0 0 0 {name=l106 lab=vb4}
C {devices/lab_wire.sym} 420 0 0 1 {name=l107 lab=vb4}
C {devices/lab_wire.sym} 715 -60 0 1 {name=l108 lab=vb4}
C {devices/lab_wire.sym} 1025 0 0 0 {name=l109 lab=vb4}
C {devices/lab_wire.sym} -2080 430 0 1 {name=l110 lab=vinn}
C {devices/lab_wire.sym} -1330 430 0 1 {name=l111 lab=vinn}
C {devices/lab_wire.sym} 2805 430 0 1 {name=l112 lab=vinn}
C {devices/lab_wire.sym} 3560 430 0 1 {name=l113 lab=vinn}
C {devices/lab_wire.sym} -2270 430 0 1 {name=l114 lab=vinp}
C {devices/lab_wire.sym} -1515 430 0 1 {name=l115 lab=vinp}
C {devices/lab_wire.sym} 2995 430 0 1 {name=l116 lab=vinp}
C {devices/lab_wire.sym} 3745 430 0 1 {name=l117 lab=vinp}
C {devices/lab_wire.sym} -2830 610 2 0 {name=l118 lab=voutn}
C {devices/lab_wire.sym} -2455 610 2 0 {name=l119 lab=voutn}
C {devices/lab_wire.sym} -1890 610 2 0 {name=l120 lab=voutn}
C {devices/lab_wire.sym} -1140 610 2 0 {name=l121 lab=voutn}
C {devices/lab_wire.sym} -5 90 2 0 {name=l122 lab=voutn}
C {devices/lab_wire.sym} 1125 170 0 1 {name=l123 lab=voutn}
C {devices/lab_wire.sym} 1765 610 2 0 {name=l124 lab=voutn}
C {devices/lab_wire.sym} 2620 610 2 0 {name=l125 lab=voutn}
C {devices/lab_wire.sym} 3370 610 2 0 {name=l126 lab=voutn}
C {devices/lab_wire.sym} 3935 610 2 0 {name=l127 lab=voutn}
C {devices/lab_wire.sym} 4310 610 2 0 {name=l128 lab=voutn}
C {devices/lab_wire.sym} -3020 610 2 0 {name=l129 lab=voutp}
C {devices/lab_wire.sym} -2645 610 2 0 {name=l130 lab=voutp}
C {devices/lab_wire.sym} -1705 610 2 0 {name=l131 lab=voutp}
C {devices/lab_wire.sym} -950 610 2 0 {name=l132 lab=voutp}
C {devices/lab_wire.sym} -350 610 2 0 {name=l133 lab=voutp}
C {devices/lab_wire.sym} 560 170 0 1 {name=l134 lab=voutp}
C {devices/lab_wire.sym} 1125 90 2 0 {name=l135 lab=voutp}
C {devices/lab_wire.sym} 2430 610 2 0 {name=l136 lab=voutp}
C {devices/lab_wire.sym} 3180 610 2 0 {name=l137 lab=voutp}
C {devices/lab_wire.sym} 4120 610 2 0 {name=l138 lab=voutp}
C {devices/lab_wire.sym} 4500 610 2 0 {name=l139 lab=voutp}
C {devices/lab_wire.sym} -785 610 2 0 {name=l140 lab=vref}
C {devices/lab_wire.sym} 2200 610 2 0 {name=l141 lab=vref}
C {devices/lab_wire.sym} -785 430 0 1 {name=l142 lab=vsum_n}
C {devices/lab_wire.sym} 885 610 2 0 {name=l143 lab=vsum_n}
C {devices/lab_wire.sym} 1305 200 0 1 {name=l144 lab=vsum_n}
C {devices/lab_wire.sym} 1325 430 0 1 {name=l145 lab=vsum_n}
C {devices/lab_wire.sym} -105 260 0 0 {name=l146 lab=vsum_p}
C {devices/lab_wire.sym} 1105 610 2 0 {name=l147 lab=vsum_p}
C {devices/lab_wire.sym} 1545 430 0 1 {name=l148 lab=vsum_p}
C {devices/lab_wire.sym} 2200 430 0 1 {name=l149 lab=vsum_p}
C {devices/lab_wire.sym} 620 94 2 0 {name=l150 lab=vdd}
C {devices/lab_wire.sym} 260 354 2 0 {name=l151 lab=vdd}
C {devices/lab_wire.sym} 815 354 2 0 {name=l152 lab=vdd}
C {devices/lab_wire.sym} 70 614 2 0 {name=l153 lab=vdd}
C {devices/lab_wire.sym} 5120 614 2 0 {name=l154 lab=vdd}
C {devices/lab_wire.sym} 55 354 2 0 {name=l155 lab=vdd}
C {devices/lab_wire.sym} 2490 614 2 0 {name=l156 lab=vdd}
C {devices/lab_wire.sym} 2680 614 2 0 {name=l157 lab=vdd}
C {devices/lab_wire.sym} 2865 614 2 0 {name=l158 lab=vdd}
C {devices/lab_wire.sym} 3055 614 2 0 {name=l159 lab=vdd}
C {devices/lab_wire.sym} 3240 614 2 0 {name=l160 lab=vdd}
C {devices/lab_wire.sym} 1405 354 2 0 {name=l161 lab=vdd}
C {devices/lab_wire.sym} 3430 614 2 0 {name=l162 lab=vdd}
C {devices/lab_wire.sym} -115 614 2 0 {name=l163 lab=vdd}
C {devices/lab_wire.sym} 5310 614 2 0 {name=l164 lab=vdd}
C {devices/lab_wire.sym} 3620 614 2 0 {name=l165 lab=vdd}
C {devices/lab_wire.sym} 3805 614 2 0 {name=l166 lab=vdd}
C {devices/lab_wire.sym} 3995 614 2 0 {name=l167 lab=vdd}
C {devices/lab_wire.sym} 4180 614 2 0 {name=l168 lab=vdd}
C {devices/lab_wire.sym} 4370 614 2 0 {name=l169 lab=vdd}
C {devices/lab_wire.sym} 4560 614 2 0 {name=l170 lab=vdd}
C {devices/lab_wire.sym} 260 94 2 0 {name=l171 lab=vdd}
C {devices/lab_wire.sym} 815 94 2 0 {name=l172 lab=vdd}
C {devices/lab_wire.sym} 1185 94 2 0 {name=l173 lab=vdd}
C {devices/lab_wire.sym} 55 94 2 0 {name=l174 lab=vdd}
C {devices/lab_wire.sym} 4745 614 2 0 {name=l175 lab=vss}
C {devices/lab_wire.sym} 260 614 2 0 {name=l176 lab=vss}
C {devices/lab_wire.sym} 620 354 2 0 {name=l177 lab=vss}
C {devices/lab_wire.sym} 1185 354 2 0 {name=l178 lab=vss}
C {devices/lab_wire.sym} 450 614 2 0 {name=l179 lab=vss}
C {devices/lab_wire.sym} 4935 614 2 0 {name=l180 lab=vss}
C {devices/lab_wire.sym} -890 614 2 0 {name=l181 lab=vss}
C {devices/lab_wire.sym} -1080 614 2 0 {name=l182 lab=vss}
C {devices/lab_wire.sym} -1270 614 2 0 {name=l183 lab=vss}
C {devices/lab_wire.sym} -1455 614 2 0 {name=l184 lab=vss}
C {devices/lab_wire.sym} -1645 614 2 0 {name=l185 lab=vss}
C {devices/lab_wire.sym} -1830 614 2 0 {name=l186 lab=vss}
C {devices/lab_wire.sym} 635 614 2 0 {name=l187 lab=vss}
C {devices/lab_wire.sym} -3270 614 2 0 {name=l188 lab=vss}
C {devices/lab_wire.sym} -2020 614 2 0 {name=l189 lab=vss}
C {devices/lab_wire.sym} -2210 614 2 0 {name=l190 lab=vss}
C {devices/lab_wire.sym} 620 874 2 0 {name=l191 lab=vss}
C {devices/lab_wire.sym} -2395 614 2 0 {name=l192 lab=vss}
C {devices/lab_wire.sym} -2585 614 2 0 {name=l193 lab=vss}
C {devices/lab_wire.sym} -2770 614 2 0 {name=l194 lab=vss}
C {devices/lab_wire.sym} -2960 614 2 0 {name=l195 lab=vss}
C {devices/lab_wire.sym} 805 874 2 0 {name=l196 lab=vss}
C {devices/lab_wire.sym} -3690 690 0 1 {name=l197 lab=vb1}
C {devices/lab_wire.sym} -3690 870 2 0 {name=l198 lab=vss}
C {devices/lab_wire.sym} -3690 610 2 0 {name=l199 lab=vss}
C {devices/lab_wire.sym} -3690 350 2 0 {name=l200 lab=vss}
C {devices/lab_wire.sym} -3690 90 2 0 {name=l201 lab=vss}
C {devices/lab_wire.sym} -3690 430 0 1 {name=l202 lab=vb2}
C {devices/lab_wire.sym} -3690 170 0 1 {name=l203 lab=vb3}
C {devices/lab_wire.sym} -3690 -90 0 1 {name=l204 lab=vb4}
C {devices/lab_wire.sym} 560 350 2 0 {name=l205 lab=vss}
C {devices/ipin.sym} -3890 520 0 0 {name=p0 lab=clk_chout_not}
C {devices/ipin.sym} -3890 640 0 0 {name=p1 lab=clk_chpf_not}
C {devices/ipin.sym} -3890 760 0 0 {name=p2 lab=clk_chfb_not}
C {devices/ipin.sym} -3890 880 0 0 {name=p3 lab=clk_chin_not}
C {devices/ipin.sym} -3890 1000 0 0 {name=p4 lab=clk_chpf}
C {devices/ipin.sym} -3890 1120 0 0 {name=p5 lab=clk_chin}
C {devices/ipin.sym} -3890 1240 0 0 {name=p6 lab=clk_chfb}
C {devices/ipin.sym} -3890 1360 0 0 {name=p7 lab=clk_chout}
C {devices/iopin.sym} -785 1060 0 0 {name=p8 lab=vref}
C {devices/opin.sym} 5585 30 0 0 {name=p9 lab=voutn}
C {devices/opin.sym} 5585 150 0 0 {name=p10 lab=voutp}
C {devices/opin.sym} 5585 490 0 0 {name=p11 lab=vinp}
C {devices/opin.sym} 5585 610 0 0 {name=p12 lab=vinn}
