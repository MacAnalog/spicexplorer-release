v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_002_fan_chopper_simple} -2930 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1285 520 0 0 {name=CFB1 value='x_dut_cfb1_value'}
C {devices/capa_np.sym} 1540 520 0 0 {name=CFB2 value='x_dut_cfb2_value'}
C {devices/capa_np.sym} 1800 520 0 0 {name=CIN1 value='x_dut_cin1_value'}
C {devices/capa_np.sym} 2060 520 0 0 {name=CIN2 value='x_dut_cin2_value'}
C {devices/capa_np.sym} -180 520 0 0 {name=CM1 value='x_dut_cm1_value'}
C {devices/capa_np.sym} 2315 520 0 0 {name=CM2 value='x_dut_cm2_value'}
C {devices/res_np.sym} -430 520 0 0 {name=RB1 value='x_dut_rb1_value'}
C {devices/res_np.sym} 2565 520 0 0 {name=RB2 value='x_dut_rb2_value'}
C {devices/vsource_np.sym} -2890 780 0 0 {name=VB1 value="dc \{vb1\}" savecurrent=false}
C {devices/vsource_np.sym} -2890 520 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -2890 260 0 0 {name=VB3 value="dc \{vb3\}" savecurrent=false}
C {devices/vsource_np.sym} -2890 0 0 0 {name=VB4 value="dc \{vb4\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 900 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 660 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 1135 260 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} 4625 520 0 0 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 660 520 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 900 260 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 1540 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 890 520 0 1 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} 435 520 0 1 {name=M17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 4850 520 0 0 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_pmos_np.sym} 5075 520 0 0 {name=M19 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} 220 260 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} -660 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_pmos_np.sym} 2815 520 0 0 {name=M21 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} -885 520 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} 3040 520 0 0 {name=M23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_nmos_np.sym} -1110 520 0 0 {name=M24 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_pmos_np.sym} 3270 520 0 0 {name=M25 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
C {devices/sg13_lv_nmos_np.sym} -1335 520 0 0 {name=M26 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm26_w l=x_dut_xm26_l m=x_dut_xm26_m}
C {devices/sg13_lv_pmos_np.sym} 3495 520 0 0 {name=M27 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm27_w l=x_dut_xm27_l m=x_dut_xm27_m}
C {devices/sg13_lv_nmos_np.sym} 1115 520 0 1 {name=M28 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm28_w l=x_dut_xm28_l m=x_dut_xm28_m}
C {devices/sg13_lv_pmos_np.sym} 210 520 0 1 {name=M29 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm29_w l=x_dut_xm29_l m=x_dut_xm29_m}
C {devices/sg13_lv_pmos_np.sym} 1800 260 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} -2550 520 0 0 {name=M30 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm30_w l=x_dut_xm30_l m=x_dut_xm30_m}
C {devices/sg13_lv_pmos_np.sym} 5300 520 0 0 {name=M31 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm31_w l=x_dut_xm31_l m=x_dut_xm31_m}
C {devices/sg13_lv_nmos_np.sym} -1560 520 0 0 {name=M32 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm32_w l=x_dut_xm32_l m=x_dut_xm32_m}
C {devices/sg13_lv_pmos_np.sym} 3720 520 0 0 {name=M33 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm33_w l=x_dut_xm33_l m=x_dut_xm33_m}
C {devices/sg13_lv_nmos_np.sym} -1790 520 0 0 {name=M34 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm34_w l=x_dut_xm34_l m=x_dut_xm34_m}
C {devices/sg13_lv_pmos_np.sym} 3945 520 0 0 {name=M35 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm35_w l=x_dut_xm35_l m=x_dut_xm35_m}
C {devices/sg13_lv_nmos_np.sym} -2015 520 0 0 {name=M36 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm36_w l=x_dut_xm36_l m=x_dut_xm36_m}
C {devices/sg13_lv_pmos_np.sym} 4170 520 0 0 {name=M37 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm37_w l=x_dut_xm37_l m=x_dut_xm37_m}
C {devices/sg13_lv_nmos_np.sym} -2240 520 0 0 {name=M38 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm38_w l=x_dut_xm38_l m=x_dut_xm38_m}
C {devices/sg13_lv_pmos_np.sym} 4400 520 0 0 {name=M39 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm39_w l=x_dut_xm39_l m=x_dut_xm39_m}
C {devices/sg13_lv_nmos_np.sym} 900 780 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 1125 780 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 660 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 1135 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 1540 0 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 220 0 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -2890 -90 -2890 -30 {}
N -2890 30 -2890 90 {}
N -2890 170 -2890 230 {}
N -2890 290 -2890 350 {}
N -2890 430 -2890 490 {}
N -2890 550 -2890 610 {}
N -2890 690 -2890 750 {}
N -2890 810 -2890 870 {}
N -2530 460 -2530 490 {}
N -2530 550 -2530 610 {}
N -2470 520 -2470 614 {}
N -2220 430 -2220 490 {}
N -2220 550 -2220 610 {}
N -2160 520 -2160 614 {}
N -1995 430 -1995 490 {}
N -1995 550 -1995 610 {}
N -1935 520 -1935 614 {}
N -1770 430 -1770 490 {}
N -1770 550 -1770 610 {}
N -1710 520 -1710 614 {}
N -1540 430 -1540 490 {}
N -1540 550 -1540 610 {}
N -1480 520 -1480 614 {}
N -1315 430 -1315 490 {}
N -1315 550 -1315 610 {}
N -1255 520 -1255 614 {}
N -1090 430 -1090 490 {}
N -1090 550 -1090 610 {}
N -1030 520 -1030 614 {}
N -865 430 -865 490 {}
N -865 550 -865 610 {}
N -805 520 -805 614 {}
N -640 430 -640 490 {}
N -640 550 -640 610 {}
N -580 520 -580 614 {}
N -430 430 -430 490 {}
N -430 550 -430 610 {}
N -180 430 -180 490 {}
N -180 550 -180 610 {}
N 130 520 130 614 {}
N 170 -60 170 0 {}
N 190 430 190 490 {}
N 190 550 190 610 {}
N 240 -140 240 -30 {}
N 240 30 240 60 {}
N 240 200 240 230 {}
N 240 290 240 350 {}
N 300 0 300 94 {}
N 300 260 300 354 {}
N 355 520 355 614 {}
N 415 430 415 490 {}
N 415 550 415 610 {}
N 580 0 580 94 {}
N 580 260 580 354 {}
N 580 520 580 614 {}
N 640 -140 640 -30 {}
N 640 30 640 90 {}
N 640 170 640 230 {}
N 640 290 640 350 {}
N 640 430 640 490 {}
N 640 550 640 610 {}
N 710 -60 710 0 {}
N 810 520 810 614 {}
N 850 -60 850 0 {}
N 850 260 850 610 {}
N 850 780 850 840 {}
N 860 30 860 200 {}
N 870 430 870 490 {}
N 920 -140 920 -30 {}
N 920 30 920 90 {}
N 920 170 920 230 {}
N 920 290 920 350 {}
N 920 690 920 750 {}
N 920 810 920 920 {}
N 980 30 980 200 {}
N 980 260 980 354 {}
N 980 780 980 874 {}
N 1035 520 1035 614 {}
N 1075 780 1075 840 {}
N 1085 -60 1085 0 {}
N 1095 320 1095 460 {}
N 1095 550 1095 610 {}
N 1135 520 1135 580 {}
N 1145 690 1145 750 {}
N 1145 810 1145 920 {}
N 1155 -140 1155 -30 {}
N 1155 30 1155 90 {}
N 1155 170 1155 230 {}
N 1155 290 1155 320 {}
N 1155 320 1155 350 {}
N 1205 780 1205 874 {}
N 1215 0 1215 94 {}
N 1215 320 1215 460 {}
N 1285 430 1285 490 {}
N 1285 550 1285 610 {}
N 1540 550 1540 610 {}
N 1560 -140 1560 -30 {}
N 1560 170 1560 230 {}
N 1560 290 1560 920 {}
N 1620 0 1620 94 {}
N 1620 260 1620 354 {}
N 1800 550 1800 610 {}
N 1820 200 1820 230 {}
N 1820 290 1820 350 {}
N 1880 260 1880 354 {}
N 2060 550 2060 610 {}
N 2315 550 2315 610 {}
N 2565 550 2565 610 {}
N 2835 430 2835 490 {}
N 2895 30 2895 550 {}
N 3060 430 3060 490 {}
N 3060 550 3060 610 {}
N 3120 520 3120 614 {}
N 3290 430 3290 490 {}
N 3290 550 3290 610 {}
N 3350 520 3350 614 {}
N 3515 430 3515 490 {}
N 3515 550 3515 610 {}
N 3575 520 3575 614 {}
N 3740 430 3740 490 {}
N 3740 550 3740 610 {}
N 3800 520 3800 614 {}
N 3965 430 3965 490 {}
N 3965 550 3965 610 {}
N 4025 520 4025 614 {}
N 4190 430 4190 490 {}
N 4190 550 4190 610 {}
N 4250 520 4250 614 {}
N 4420 430 4420 490 {}
N 4420 550 4420 610 {}
N 4480 520 4480 614 {}
N 4645 460 4645 490 {}
N 4645 550 4645 610 {}
N 4705 520 4705 614 {}
N 4870 460 4870 490 {}
N 4870 550 4870 610 {}
N 4930 520 4930 614 {}
N 5095 460 5095 490 {}
N 5095 550 5095 610 {}
N 5155 520 5155 614 {}
N 5320 460 5320 490 {}
N 5320 550 5320 610 {}
N 5380 520 5380 614 {}
N -2950 -140 5800 -140 {}
N 170 -60 710 -60 {}
N 850 -60 1085 -60 {}
N 140 0 200 0 {}
N 240 0 300 0 {}
N 580 0 640 0 {}
N 680 0 880 0 {}
N 1085 0 1115 0 {}
N 1155 0 1215 0 {}
N 1460 0 1520 0 {}
N 1560 0 1620 0 {}
N 860 30 980 30 {}
N 1560 30 2895 30 {}
N 240 200 1820 200 {}
N 140 260 200 260 {}
N 240 260 300 260 {}
N 580 260 640 260 {}
N 680 260 740 260 {}
N 820 260 880 260 {}
N 920 260 980 260 {}
N 1055 260 1115 260 {}
N 1460 260 1520 260 {}
N 1560 260 1620 260 {}
N 1720 260 1780 260 {}
N 1820 260 1880 260 {}
N 1095 320 1215 320 {}
N 1285 430 2835 430 {}
N -2530 460 5320 460 {}
N 810 490 1095 490 {}
N -2660 520 -2570 520 {}
N -2530 520 -2470 520 {}
N -2350 520 -2260 520 {}
N -2220 520 -2160 520 {}
N -2095 520 -2035 520 {}
N -1995 520 -1935 520 {}
N -1900 520 -1810 520 {}
N -1770 520 -1710 520 {}
N -1640 520 -1580 520 {}
N -1540 520 -1480 520 {}
N -1445 520 -1355 520 {}
N -1315 520 -1255 520 {}
N -1190 520 -1130 520 {}
N -1090 520 -1030 520 {}
N -995 520 -905 520 {}
N -865 520 -805 520 {}
N -740 520 -680 520 {}
N -640 520 -580 520 {}
N 130 520 190 520 {}
N 230 520 260 520 {}
N 355 520 415 520 {}
N 455 520 515 520 {}
N 580 520 640 520 {}
N 680 520 740 520 {}
N 810 520 870 520 {}
N 910 520 970 520 {}
N 1035 520 1095 520 {}
N 1135 520 1165 520 {}
N 2735 520 2795 520 {}
N 2960 520 3020 520 {}
N 3060 520 3120 520 {}
N 3190 520 3250 520 {}
N 3290 520 3350 520 {}
N 3415 520 3475 520 {}
N 3515 520 3575 520 {}
N 3640 520 3700 520 {}
N 3740 520 3800 520 {}
N 3865 520 3925 520 {}
N 3965 520 4025 520 {}
N 4090 520 4150 520 {}
N 4190 520 4250 520 {}
N 4320 520 4380 520 {}
N 4420 520 4480 520 {}
N 4545 520 4605 520 {}
N 4645 520 4705 520 {}
N 4770 520 4830 520 {}
N 4870 520 4930 520 {}
N 4995 520 5055 520 {}
N 5095 520 5155 520 {}
N 5220 520 5280 520 {}
N 5320 520 5380 520 {}
N 2835 550 2895 550 {}
N 850 610 1095 610 {}
N 820 780 880 780 {}
N 920 780 980 780 {}
N 1075 780 1105 780 {}
N 1145 780 1205 780 {}
N 850 840 1075 840 {}
N -2950 920 5800 920 {}
C {devices/lab_wire.sym} 640 90 2 0 {name=l0 lab=casc_src_n}
C {devices/lab_wire.sym} 640 170 0 1 {name=l1 lab=casc_src_n}
C {devices/lab_wire.sym} 1155 90 2 0 {name=l2 lab=casc_src_p}
C {devices/lab_wire.sym} 1155 170 0 1 {name=l3 lab=casc_src_p}
C {devices/lab_wire.sym} -740 520 0 0 {name=l4 lab=clk_chfb}
C {devices/lab_wire.sym} 4090 520 0 0 {name=l5 lab=clk_chfb}
C {devices/lab_wire.sym} 4320 520 0 0 {name=l6 lab=clk_chfb}
C {devices/lab_wire.sym} -2095 520 0 0 {name=l7 lab=clk_chfb_not}
C {devices/lab_wire.sym} 2735 520 0 0 {name=l8 lab=clk_chfb_not}
C {devices/lab_wire.sym} 2960 520 0 0 {name=l9 lab=clk_chfb_not}
C {devices/lab_wire.sym} -1190 520 0 0 {name=l10 lab=clk_chin}
C {devices/lab_wire.sym} 3640 520 0 0 {name=l11 lab=clk_chin}
C {devices/lab_wire.sym} 3865 520 0 0 {name=l12 lab=clk_chin}
C {devices/lab_wire.sym} -1640 520 0 0 {name=l13 lab=clk_chin_not}
C {devices/lab_wire.sym} 3190 520 0 0 {name=l14 lab=clk_chin_not}
C {devices/lab_wire.sym} 3415 520 0 0 {name=l15 lab=clk_chin_not}
C {devices/lab_wire.sym} 970 520 0 1 {name=l16 lab=clk_chout}
C {devices/lab_wire.sym} 4770 520 0 0 {name=l17 lab=clk_chout}
C {devices/lab_wire.sym} 5220 520 0 0 {name=l18 lab=clk_chout}
C {devices/lab_wire.sym} 515 520 0 1 {name=l19 lab=clk_chout_not}
C {devices/lab_wire.sym} 1135 580 2 0 {name=l20 lab=clk_chout_not}
C {devices/lab_wire.sym} 4995 520 0 0 {name=l21 lab=clk_chout_not}
C {devices/lab_wire.sym} -2220 430 0 1 {name=l22 lab=fbch_n}
C {devices/lab_wire.sym} -865 430 0 1 {name=l23 lab=fbch_n}
C {devices/lab_wire.sym} 1540 490 0 0 {name=l24 lab=fbch_n}
C {devices/lab_wire.sym} 3060 430 0 1 {name=l25 lab=fbch_n}
C {devices/lab_wire.sym} 4420 430 0 1 {name=l26 lab=fbch_n}
C {devices/lab_wire.sym} -1995 430 0 1 {name=l27 lab=fbch_p}
C {devices/lab_wire.sym} -640 430 0 1 {name=l28 lab=fbch_p}
C {devices/lab_wire.sym} 1285 430 0 1 {name=l29 lab=fbch_p}
C {devices/lab_wire.sym} 4190 430 0 1 {name=l30 lab=fbch_p}
C {devices/lab_wire.sym} 640 610 2 0 {name=l31 lab=fold_n}
C {devices/lab_wire.sym} 1145 690 0 1 {name=l32 lab=fold_n}
C {devices/lab_wire.sym} 1820 350 2 0 {name=l33 lab=fold_n}
C {devices/lab_wire.sym} 240 350 2 0 {name=l34 lab=fold_p}
C {devices/lab_wire.sym} 920 690 0 1 {name=l35 lab=fold_p}
C {devices/lab_wire.sym} 4645 610 2 0 {name=l36 lab=fold_p}
C {devices/lab_wire.sym} -2530 610 2 0 {name=l37 lab=g2_n}
C {devices/lab_wire.sym} 415 610 2 0 {name=l38 lab=g2_n}
C {devices/lab_wire.sym} 870 550 0 0 {name=l39 lab=g2_n}
C {devices/lab_wire.sym} 1460 260 0 0 {name=l40 lab=g2_n}
C {devices/lab_wire.sym} 2315 490 0 0 {name=l41 lab=g2_n}
C {devices/lab_wire.sym} 5320 610 2 0 {name=l42 lab=g2_n}
C {devices/lab_wire.sym} -180 430 0 1 {name=l43 lab=g2_p}
C {devices/lab_wire.sym} 190 610 2 0 {name=l44 lab=g2_p}
C {devices/lab_wire.sym} 820 260 0 0 {name=l45 lab=g2_p}
C {devices/lab_wire.sym} 4870 610 2 0 {name=l46 lab=g2_p}
C {devices/lab_wire.sym} 5095 610 2 0 {name=l47 lab=g2_p}
C {devices/lab_wire.sym} -1770 610 2 0 {name=l48 lab=inch_n}
C {devices/lab_wire.sym} -1090 610 2 0 {name=l49 lab=inch_n}
C {devices/lab_wire.sym} 1800 610 2 0 {name=l50 lab=inch_n}
C {devices/lab_wire.sym} 3290 610 2 0 {name=l51 lab=inch_n}
C {devices/lab_wire.sym} 3965 610 2 0 {name=l52 lab=inch_n}
C {devices/lab_wire.sym} -1540 610 2 0 {name=l53 lab=inch_p}
C {devices/lab_wire.sym} -1315 610 2 0 {name=l54 lab=inch_p}
C {devices/lab_wire.sym} 2060 610 2 0 {name=l55 lab=inch_p}
C {devices/lab_wire.sym} 3515 610 2 0 {name=l56 lab=inch_p}
C {devices/lab_wire.sym} 3740 610 2 0 {name=l57 lab=inch_p}
C {devices/lab_wire.sym} 190 430 0 1 {name=l58 lab=out1_n}
C {devices/lab_wire.sym} 415 430 0 1 {name=l59 lab=out1_n}
C {devices/lab_wire.sym} 640 350 2 0 {name=l60 lab=out1_n}
C {devices/lab_wire.sym} 640 430 0 1 {name=l61 lab=out1_n}
C {devices/lab_wire.sym} 870 430 0 1 {name=l62 lab=out1_n}
C {devices/lab_wire.sym} 1155 350 2 0 {name=l63 lab=out1_p}
C {devices/lab_wire.sym} 920 90 2 0 {name=l64 lab=tail}
C {devices/lab_wire.sym} 820 780 0 0 {name=l65 lab=vb1}
C {devices/lab_wire.sym} 740 520 0 1 {name=l66 lab=vb2}
C {devices/lab_wire.sym} 4545 520 0 0 {name=l67 lab=vb2}
C {devices/lab_wire.sym} 740 260 0 1 {name=l68 lab=vb3}
C {devices/lab_wire.sym} 1055 260 0 0 {name=l69 lab=vb3}
C {devices/lab_wire.sym} 140 0 0 0 {name=l70 lab=vb4}
C {devices/lab_wire.sym} 1460 0 0 0 {name=l71 lab=vb4}
C {devices/lab_wire.sym} -1540 430 0 1 {name=l72 lab=vinn}
C {devices/lab_wire.sym} -1090 430 0 1 {name=l73 lab=vinn}
C {devices/lab_wire.sym} 3290 430 0 1 {name=l74 lab=vinn}
C {devices/lab_wire.sym} 3740 430 0 1 {name=l75 lab=vinn}
C {devices/lab_wire.sym} -1770 430 0 1 {name=l76 lab=vinp}
C {devices/lab_wire.sym} -1315 430 0 1 {name=l77 lab=vinp}
C {devices/lab_wire.sym} 3515 430 0 1 {name=l78 lab=vinp}
C {devices/lab_wire.sym} 3965 430 0 1 {name=l79 lab=vinp}
C {devices/lab_wire.sym} -1995 610 2 0 {name=l80 lab=voutn}
C {devices/lab_wire.sym} -865 610 2 0 {name=l81 lab=voutn}
C {devices/lab_wire.sym} 1560 170 0 1 {name=l82 lab=voutn}
C {devices/lab_wire.sym} 2315 610 2 0 {name=l83 lab=voutn}
C {devices/lab_wire.sym} 3060 610 2 0 {name=l84 lab=voutn}
C {devices/lab_wire.sym} 4190 610 2 0 {name=l85 lab=voutn}
C {devices/lab_wire.sym} -2220 610 2 0 {name=l86 lab=voutp}
C {devices/lab_wire.sym} -640 610 2 0 {name=l87 lab=voutp}
C {devices/lab_wire.sym} -180 610 2 0 {name=l88 lab=voutp}
C {devices/lab_wire.sym} 920 170 0 1 {name=l89 lab=voutp}
C {devices/lab_wire.sym} 4420 610 2 0 {name=l90 lab=voutp}
C {devices/lab_wire.sym} -430 610 2 0 {name=l91 lab=vref}
C {devices/lab_wire.sym} 2565 610 2 0 {name=l92 lab=vref}
C {devices/lab_wire.sym} -430 430 0 1 {name=l93 lab=vsum_n}
C {devices/lab_wire.sym} 1285 610 2 0 {name=l94 lab=vsum_n}
C {devices/lab_wire.sym} 1720 260 0 0 {name=l95 lab=vsum_n}
C {devices/lab_wire.sym} 1800 490 0 0 {name=l96 lab=vsum_n}
C {devices/lab_wire.sym} 140 260 0 0 {name=l97 lab=vsum_p}
C {devices/lab_wire.sym} 1540 610 2 0 {name=l98 lab=vsum_p}
C {devices/lab_wire.sym} 2060 490 0 0 {name=l99 lab=vsum_p}
C {devices/lab_wire.sym} 2565 490 0 0 {name=l100 lab=vsum_p}
C {devices/lab_wire.sym} 920 0 0 0 {name=l101 lab=vdd}
C {devices/lab_wire.sym} 580 354 2 0 {name=l102 lab=vdd}
C {devices/lab_wire.sym} 1155 260 0 0 {name=l103 lab=vdd}
C {devices/lab_wire.sym} 355 614 2 0 {name=l104 lab=vdd}
C {devices/lab_wire.sym} 5155 614 2 0 {name=l105 lab=vdd}
C {devices/lab_wire.sym} 300 354 2 0 {name=l106 lab=vdd}
C {devices/lab_wire.sym} 2835 520 0 0 {name=l107 lab=vdd}
C {devices/lab_wire.sym} 3120 614 2 0 {name=l108 lab=vdd}
C {devices/lab_wire.sym} 3350 614 2 0 {name=l109 lab=vdd}
C {devices/lab_wire.sym} 3575 614 2 0 {name=l110 lab=vdd}
C {devices/lab_wire.sym} 130 614 2 0 {name=l111 lab=vdd}
C {devices/lab_wire.sym} 1880 354 2 0 {name=l112 lab=vdd}
C {devices/lab_wire.sym} 5380 614 2 0 {name=l113 lab=vdd}
C {devices/lab_wire.sym} 3800 614 2 0 {name=l114 lab=vdd}
C {devices/lab_wire.sym} 4025 614 2 0 {name=l115 lab=vdd}
C {devices/lab_wire.sym} 4250 614 2 0 {name=l116 lab=vdd}
C {devices/lab_wire.sym} 4480 614 2 0 {name=l117 lab=vdd}
C {devices/lab_wire.sym} 580 94 2 0 {name=l118 lab=vdd}
C {devices/lab_wire.sym} 1215 94 2 0 {name=l119 lab=vdd}
C {devices/lab_wire.sym} 1620 94 2 0 {name=l120 lab=vdd}
C {devices/lab_wire.sym} 300 94 2 0 {name=l121 lab=vdd}
C {devices/lab_wire.sym} 4705 614 2 0 {name=l122 lab=vss}
C {devices/lab_wire.sym} 580 614 2 0 {name=l123 lab=vss}
C {devices/lab_wire.sym} 980 354 2 0 {name=l124 lab=vss}
C {devices/lab_wire.sym} 1620 354 2 0 {name=l125 lab=vss}
C {devices/lab_wire.sym} 810 614 2 0 {name=l126 lab=vss}
C {devices/lab_wire.sym} 4930 614 2 0 {name=l127 lab=vss}
C {devices/lab_wire.sym} -580 614 2 0 {name=l128 lab=vss}
C {devices/lab_wire.sym} -805 614 2 0 {name=l129 lab=vss}
C {devices/lab_wire.sym} -1030 614 2 0 {name=l130 lab=vss}
C {devices/lab_wire.sym} -1255 614 2 0 {name=l131 lab=vss}
C {devices/lab_wire.sym} 1035 614 2 0 {name=l132 lab=vss}
C {devices/lab_wire.sym} -2470 614 2 0 {name=l133 lab=vss}
C {devices/lab_wire.sym} -1480 614 2 0 {name=l134 lab=vss}
C {devices/lab_wire.sym} -1710 614 2 0 {name=l135 lab=vss}
C {devices/lab_wire.sym} -1935 614 2 0 {name=l136 lab=vss}
C {devices/lab_wire.sym} -2160 614 2 0 {name=l137 lab=vss}
C {devices/lab_wire.sym} 980 874 2 0 {name=l138 lab=vss}
C {devices/lab_wire.sym} 1205 874 2 0 {name=l139 lab=vss}
C {devices/lab_wire.sym} -2890 690 0 1 {name=l140 lab=vb1}
C {devices/lab_wire.sym} -2890 870 2 0 {name=l141 lab=vss}
C {devices/lab_wire.sym} -2890 610 2 0 {name=l142 lab=vss}
C {devices/lab_wire.sym} -2890 350 2 0 {name=l143 lab=vss}
C {devices/lab_wire.sym} -2890 90 2 0 {name=l144 lab=vss}
C {devices/lab_wire.sym} -2890 430 0 1 {name=l145 lab=vb2}
C {devices/lab_wire.sym} -2890 170 0 1 {name=l146 lab=vb3}
C {devices/lab_wire.sym} -2890 -90 0 1 {name=l147 lab=vb4}
C {devices/lab_wire.sym} 920 350 2 0 {name=l148 lab=vss}
C {devices/ipin.sym} -2660 520 0 0 {name=p0 lab=clk_chout_not}
C {devices/ipin.sym} -2350 520 0 0 {name=p1 lab=clk_chfb_not}
C {devices/ipin.sym} -1900 520 0 0 {name=p2 lab=clk_chin_not}
C {devices/ipin.sym} -1445 520 0 0 {name=p3 lab=clk_chin}
C {devices/ipin.sym} -995 520 0 0 {name=p4 lab=clk_chfb}
C {devices/ipin.sym} 260 520 0 0 {name=p5 lab=clk_chout}
C {devices/iopin.sym} -2950 -140 0 0 {name=p6 lab=vdd}
C {devices/iopin.sym} -2950 920 0 0 {name=p7 lab=vss}
C {devices/opin.sym} 240 60 0 0 {name=p8 lab=voutn}
C {devices/opin.sym} 2895 30 0 0 {name=p9 lab=voutp}
C {devices/iopin.sym} -430 1060 0 0 {name=p10 lab=vref}
C {devices/opin.sym} 5940 490 0 0 {name=p11 lab=vinp}
C {devices/opin.sym} 5940 610 0 0 {name=p12 lab=vinn}
