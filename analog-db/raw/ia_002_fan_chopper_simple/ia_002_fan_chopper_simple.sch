v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_002_fan_chopper_simple} -2930 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 715 520 0 0 {name=CFB1 value='x_dut_cfb1_value'}
C {devices/capa_np.sym} 935 520 0 0 {name=CFB2 value='x_dut_cfb2_value'}
C {devices/capa_np.sym} 1155 520 0 0 {name=CIN1 value='x_dut_cin1_value'}
C {devices/capa_np.sym} 1375 520 0 0 {name=CIN2 value='x_dut_cin2_value'}
C {devices/capa_np.sym} -525 520 0 0 {name=CM1 value='x_dut_cm1_value'}
C {devices/capa_np.sym} 1595 520 0 0 {name=CM2 value='x_dut_cm2_value'}
C {devices/res_np.sym} -735 520 0 0 {name=RB1 value='x_dut_rb1_value'}
C {devices/res_np.sym} 1805 520 0 0 {name=RB2 value='x_dut_rb2_value'}
C {devices/vsource_np.sym} -2890 780 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -2890 520 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -2890 260 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -2890 0 0 0 {name=VB4 value="dc {vb4}"}
C {devices/sg13_lv_pmos_np.sym} 365 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 170 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 565 260 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} 3520 520 0 0 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 170 520 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 365 260 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 935 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 355 520 0 1 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} -20 520 0 1 {name=M17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 3710 520 0 0 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_pmos_np.sym} 3900 520 0 0 {name=M19 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} -200 260 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} -925 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_pmos_np.sym} 2020 520 0 0 {name=M21 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} -1110 520 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} 2205 520 0 0 {name=M23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_nmos_np.sym} -1300 520 0 0 {name=M24 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_pmos_np.sym} 2395 520 0 0 {name=M25 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
C {devices/sg13_lv_nmos_np.sym} -1490 520 0 0 {name=M26 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm26_w l=x_dut_xm26_l m=x_dut_xm26_m}
C {devices/sg13_lv_pmos_np.sym} 2580 520 0 0 {name=M27 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm27_w l=x_dut_xm27_l m=x_dut_xm27_m}
C {devices/sg13_lv_nmos_np.sym} 545 520 0 1 {name=M28 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm28_w l=x_dut_xm28_l m=x_dut_xm28_m}
C {devices/sg13_lv_pmos_np.sym} -210 520 0 1 {name=M29 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm29_w l=x_dut_xm29_l m=x_dut_xm29_m}
C {devices/sg13_lv_pmos_np.sym} 1155 260 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} -2550 520 0 0 {name=M30 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm30_w l=x_dut_xm30_l m=x_dut_xm30_m}
C {devices/sg13_lv_pmos_np.sym} 4085 520 0 0 {name=M31 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm31_w l=x_dut_xm31_l m=x_dut_xm31_m}
C {devices/sg13_lv_nmos_np.sym} -1675 520 0 0 {name=M32 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm32_w l=x_dut_xm32_l m=x_dut_xm32_m}
C {devices/sg13_lv_pmos_np.sym} 2770 520 0 0 {name=M33 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm33_w l=x_dut_xm33_l m=x_dut_xm33_m}
C {devices/sg13_lv_nmos_np.sym} -1865 520 0 0 {name=M34 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm34_w l=x_dut_xm34_l m=x_dut_xm34_m}
C {devices/sg13_lv_pmos_np.sym} 2960 520 0 0 {name=M35 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm35_w l=x_dut_xm35_l m=x_dut_xm35_m}
C {devices/sg13_lv_nmos_np.sym} -2050 520 0 0 {name=M36 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm36_w l=x_dut_xm36_l m=x_dut_xm36_m}
C {devices/sg13_lv_pmos_np.sym} 3145 520 0 0 {name=M37 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm37_w l=x_dut_xm37_l m=x_dut_xm37_m}
C {devices/sg13_lv_nmos_np.sym} -2240 520 0 0 {name=M38 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm38_w l=x_dut_xm38_l m=x_dut_xm38_m}
C {devices/sg13_lv_pmos_np.sym} 3335 520 0 0 {name=M39 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm39_w l=x_dut_xm39_l m=x_dut_xm39_m}
C {devices/sg13_lv_nmos_np.sym} 365 780 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 555 780 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 565 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 935 0 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} -200 0 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -2890 -90 -2890 -30 {}
N -2890 30 -2890 90 {}
N -2890 170 -2890 230 {}
N -2890 290 -2890 350 {}
N -2890 430 -2890 490 {}
N -2890 550 -2890 610 {}
N -2890 690 -2890 750 {}
N -2890 810 -2890 870 {}
N -2530 430 -2530 490 {}
N -2530 550 -2530 610 {}
N -2470 520 -2470 614 {}
N -2260 460 -2260 520 {}
N -2220 430 -2220 490 {}
N -2220 550 -2220 610 {}
N -2160 520 -2160 614 {}
N -2070 460 -2070 520 {}
N -2030 430 -2030 490 {}
N -2030 550 -2030 610 {}
N -1970 520 -1970 614 {}
N -1885 460 -1885 520 {}
N -1845 430 -1845 490 {}
N -1845 550 -1845 610 {}
N -1785 520 -1785 614 {}
N -1695 460 -1695 520 {}
N -1655 430 -1655 490 {}
N -1655 550 -1655 610 {}
N -1595 520 -1595 614 {}
N -1510 460 -1510 520 {}
N -1470 430 -1470 490 {}
N -1470 550 -1470 610 {}
N -1410 520 -1410 614 {}
N -1320 460 -1320 520 {}
N -1280 430 -1280 490 {}
N -1280 550 -1280 610 {}
N -1220 520 -1220 614 {}
N -1130 460 -1130 520 {}
N -1090 430 -1090 490 {}
N -1090 550 -1090 610 {}
N -1030 520 -1030 614 {}
N -945 460 -945 520 {}
N -905 430 -905 490 {}
N -905 550 -905 610 {}
N -845 520 -845 614 {}
N -735 430 -735 490 {}
N -735 550 -735 610 {}
N -525 430 -525 490 {}
N -525 550 -525 610 {}
N -290 520 -290 614 {}
N -230 430 -230 490 {}
N -230 550 -230 610 {}
N -190 520 -190 580 {}
N -180 -140 -180 -30 {}
N -180 30 -180 90 {}
N -180 170 -180 230 {}
N -180 290 -180 350 {}
N -120 0 -120 94 {}
N -120 260 -120 354 {}
N -100 520 -100 614 {}
N -40 430 -40 490 {}
N -40 550 -40 610 {}
N 0 520 0 580 {}
N 90 0 90 94 {}
N 90 260 90 354 {}
N 90 520 90 614 {}
N 150 -140 150 -30 {}
N 150 30 150 90 {}
N 150 170 150 230 {}
N 150 290 150 350 {}
N 150 430 150 490 {}
N 150 550 150 610 {}
N 190 520 190 580 {}
N 275 520 275 614 {}
N 335 430 335 490 {}
N 335 550 335 610 {}
N 375 520 375 580 {}
N 385 -140 385 -30 {}
N 385 30 385 90 {}
N 385 170 385 230 {}
N 385 290 385 350 {}
N 385 690 385 750 {}
N 385 810 385 920 {}
N 445 0 445 94 {}
N 445 260 445 354 {}
N 445 780 445 874 {}
N 465 520 465 614 {}
N 525 430 525 490 {}
N 525 550 525 610 {}
N 535 720 535 780 {}
N 545 -60 545 0 {}
N 545 200 545 260 {}
N 565 520 565 580 {}
N 575 690 575 750 {}
N 575 810 575 920 {}
N 585 -140 585 -30 {}
N 585 30 585 90 {}
N 585 170 585 230 {}
N 585 290 585 350 {}
N 635 780 635 874 {}
N 645 0 645 94 {}
N 645 260 645 354 {}
N 715 430 715 490 {}
N 715 550 715 610 {}
N 935 430 935 490 {}
N 935 550 935 610 {}
N 955 -140 955 -30 {}
N 955 30 955 90 {}
N 955 170 955 230 {}
N 955 290 955 920 {}
N 1015 0 1015 94 {}
N 1015 260 1015 354 {}
N 1135 200 1135 260 {}
N 1155 430 1155 490 {}
N 1155 550 1155 610 {}
N 1175 170 1175 230 {}
N 1175 290 1175 350 {}
N 1235 260 1235 354 {}
N 1375 430 1375 490 {}
N 1375 550 1375 610 {}
N 1595 430 1595 490 {}
N 1595 550 1595 610 {}
N 1805 430 1805 490 {}
N 1805 550 1805 610 {}
N 2000 460 2000 520 {}
N 2040 430 2040 490 {}
N 2040 550 2040 610 {}
N 2100 520 2100 614 {}
N 2185 460 2185 520 {}
N 2225 430 2225 490 {}
N 2225 550 2225 610 {}
N 2285 520 2285 614 {}
N 2375 460 2375 520 {}
N 2415 430 2415 490 {}
N 2415 550 2415 610 {}
N 2475 520 2475 614 {}
N 2560 460 2560 520 {}
N 2600 430 2600 490 {}
N 2600 550 2600 610 {}
N 2660 520 2660 614 {}
N 2750 460 2750 520 {}
N 2790 430 2790 490 {}
N 2790 550 2790 610 {}
N 2850 520 2850 614 {}
N 2940 460 2940 520 {}
N 2980 430 2980 490 {}
N 2980 550 2980 610 {}
N 3040 520 3040 614 {}
N 3125 460 3125 520 {}
N 3165 430 3165 490 {}
N 3165 550 3165 610 {}
N 3225 520 3225 614 {}
N 3315 460 3315 520 {}
N 3355 430 3355 490 {}
N 3355 550 3355 610 {}
N 3415 520 3415 614 {}
N 3500 460 3500 520 {}
N 3540 430 3540 490 {}
N 3540 550 3540 610 {}
N 3600 520 3600 614 {}
N 3730 460 3730 490 {}
N 3730 550 3730 610 {}
N 3790 520 3790 614 {}
N 3920 460 3920 490 {}
N 3920 550 3920 610 {}
N 3980 520 3980 614 {}
N 4105 460 4105 490 {}
N 4105 550 4105 610 {}
N 4165 520 4165 614 {}
N -2950 -140 4300 -140 {}
N -280 0 -220 0 {}
N -180 0 -120 0 {}
N 90 0 150 0 {}
N 190 0 345 0 {}
N 385 0 445 0 {}
N 515 0 545 0 {}
N 585 0 645 0 {}
N 855 0 915 0 {}
N 955 0 1015 0 {}
N -280 260 -220 260 {}
N -180 260 -120 260 {}
N 90 260 150 260 {}
N 190 260 250 260 {}
N 285 260 345 260 {}
N 385 260 445 260 {}
N 515 260 545 260 {}
N 585 260 645 260 {}
N 855 260 915 260 {}
N 955 260 1015 260 {}
N 1105 260 1135 260 {}
N 1175 260 1235 260 {}
N 3540 460 4105 460 {}
N -2630 520 -2570 520 {}
N -2530 520 -2470 520 {}
N -2290 520 -2260 520 {}
N -2220 520 -2160 520 {}
N -2100 520 -2070 520 {}
N -2030 520 -1970 520 {}
N -1915 520 -1885 520 {}
N -1845 520 -1785 520 {}
N -1725 520 -1695 520 {}
N -1655 520 -1595 520 {}
N -1540 520 -1510 520 {}
N -1470 520 -1410 520 {}
N -1350 520 -1320 520 {}
N -1280 520 -1220 520 {}
N -1160 520 -1130 520 {}
N -1090 520 -1030 520 {}
N -975 520 -945 520 {}
N -905 520 -845 520 {}
N -290 520 -230 520 {}
N -190 520 -160 520 {}
N -100 520 -40 520 {}
N 0 520 30 520 {}
N 90 520 150 520 {}
N 190 520 220 520 {}
N 275 520 335 520 {}
N 375 520 405 520 {}
N 465 520 525 520 {}
N 565 520 595 520 {}
N 1970 520 2000 520 {}
N 2040 520 2100 520 {}
N 2155 520 2185 520 {}
N 2225 520 2285 520 {}
N 2345 520 2375 520 {}
N 2415 520 2475 520 {}
N 2530 520 2560 520 {}
N 2600 520 2660 520 {}
N 2720 520 2750 520 {}
N 2790 520 2850 520 {}
N 2910 520 2940 520 {}
N 2980 520 3040 520 {}
N 3095 520 3125 520 {}
N 3165 520 3225 520 {}
N 3285 520 3315 520 {}
N 3355 520 3415 520 {}
N 3470 520 3500 520 {}
N 3540 520 3600 520 {}
N 3660 520 3690 520 {}
N 3730 520 3790 520 {}
N 3850 520 3880 520 {}
N 3920 520 3980 520 {}
N 4035 520 4065 520 {}
N 4105 520 4165 520 {}
N 285 780 345 780 {}
N 385 780 445 780 {}
N 505 780 535 780 {}
N 575 780 635 780 {}
N -2950 920 4300 920 {}
C {devices/lab_wire.sym} -2950 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -2950 920 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 150 90 2 0 {name=l2 lab=casc_src_n}
C {devices/lab_wire.sym} 150 170 0 1 {name=l3 lab=casc_src_n}
C {devices/lab_wire.sym} 585 90 2 0 {name=l4 lab=casc_src_p}
C {devices/lab_wire.sym} 585 170 0 1 {name=l5 lab=casc_src_p}
C {devices/lab_wire.sym} -1130 460 0 1 {name=l6 lab=clk_chfb}
C {devices/lab_wire.sym} -945 460 0 1 {name=l7 lab=clk_chfb}
C {devices/lab_wire.sym} 3125 460 0 1 {name=l8 lab=clk_chfb}
C {devices/lab_wire.sym} 3315 460 0 1 {name=l9 lab=clk_chfb}
C {devices/lab_wire.sym} -2260 460 0 1 {name=l10 lab=clk_chfb_not}
C {devices/lab_wire.sym} -2070 460 0 1 {name=l11 lab=clk_chfb_not}
C {devices/lab_wire.sym} 2000 460 0 1 {name=l12 lab=clk_chfb_not}
C {devices/lab_wire.sym} 2185 460 0 1 {name=l13 lab=clk_chfb_not}
C {devices/lab_wire.sym} -1510 460 0 1 {name=l14 lab=clk_chin}
C {devices/lab_wire.sym} -1320 460 0 1 {name=l15 lab=clk_chin}
C {devices/lab_wire.sym} 2750 460 0 1 {name=l16 lab=clk_chin}
C {devices/lab_wire.sym} 2940 460 0 1 {name=l17 lab=clk_chin}
C {devices/lab_wire.sym} -1885 460 0 1 {name=l18 lab=clk_chin_not}
C {devices/lab_wire.sym} -1695 460 0 1 {name=l19 lab=clk_chin_not}
C {devices/lab_wire.sym} 2375 460 0 1 {name=l20 lab=clk_chin_not}
C {devices/lab_wire.sym} 2560 460 0 1 {name=l21 lab=clk_chin_not}
C {devices/lab_wire.sym} -190 580 2 0 {name=l22 lab=clk_chout}
C {devices/lab_wire.sym} 375 580 2 0 {name=l23 lab=clk_chout}
C {devices/lab_wire.sym} 3690 520 0 0 {name=l24 lab=clk_chout}
C {devices/lab_wire.sym} 4065 520 0 0 {name=l25 lab=clk_chout}
C {devices/lab_wire.sym} -2630 520 0 0 {name=l26 lab=clk_chout_not}
C {devices/lab_wire.sym} 0 580 2 0 {name=l27 lab=clk_chout_not}
C {devices/lab_wire.sym} 565 580 2 0 {name=l28 lab=clk_chout_not}
C {devices/lab_wire.sym} 3880 520 0 0 {name=l29 lab=clk_chout_not}
C {devices/lab_wire.sym} -2220 430 0 1 {name=l30 lab=fbch_n}
C {devices/lab_wire.sym} -1090 430 0 1 {name=l31 lab=fbch_n}
C {devices/lab_wire.sym} 935 430 0 1 {name=l32 lab=fbch_n}
C {devices/lab_wire.sym} 2225 430 0 1 {name=l33 lab=fbch_n}
C {devices/lab_wire.sym} 3355 430 0 1 {name=l34 lab=fbch_n}
C {devices/lab_wire.sym} -2030 430 0 1 {name=l35 lab=fbch_p}
C {devices/lab_wire.sym} -905 430 0 1 {name=l36 lab=fbch_p}
C {devices/lab_wire.sym} 715 430 0 1 {name=l37 lab=fbch_p}
C {devices/lab_wire.sym} 2040 430 0 1 {name=l38 lab=fbch_p}
C {devices/lab_wire.sym} 3165 430 0 1 {name=l39 lab=fbch_p}
C {devices/lab_wire.sym} 150 610 2 0 {name=l40 lab=fold_n}
C {devices/lab_wire.sym} 575 690 0 1 {name=l41 lab=fold_n}
C {devices/lab_wire.sym} 1175 350 2 0 {name=l42 lab=fold_n}
C {devices/lab_wire.sym} -180 350 2 0 {name=l43 lab=fold_p}
C {devices/lab_wire.sym} 385 690 0 1 {name=l44 lab=fold_p}
C {devices/lab_wire.sym} 3540 610 2 0 {name=l45 lab=fold_p}
C {devices/lab_wire.sym} -2530 610 2 0 {name=l46 lab=g2_n}
C {devices/lab_wire.sym} -40 610 2 0 {name=l47 lab=g2_n}
C {devices/lab_wire.sym} 335 610 2 0 {name=l48 lab=g2_n}
C {devices/lab_wire.sym} 855 260 0 0 {name=l49 lab=g2_n}
C {devices/lab_wire.sym} 1595 430 0 1 {name=l50 lab=g2_n}
C {devices/lab_wire.sym} 4105 610 2 0 {name=l51 lab=g2_n}
C {devices/lab_wire.sym} -525 430 0 1 {name=l52 lab=g2_p}
C {devices/lab_wire.sym} -230 610 2 0 {name=l53 lab=g2_p}
C {devices/lab_wire.sym} 285 260 0 0 {name=l54 lab=g2_p}
C {devices/lab_wire.sym} 525 610 2 0 {name=l55 lab=g2_p}
C {devices/lab_wire.sym} 3730 610 2 0 {name=l56 lab=g2_p}
C {devices/lab_wire.sym} 3920 610 2 0 {name=l57 lab=g2_p}
C {devices/lab_wire.sym} -1845 610 2 0 {name=l58 lab=inch_n}
C {devices/lab_wire.sym} -1280 610 2 0 {name=l59 lab=inch_n}
C {devices/lab_wire.sym} 1155 610 2 0 {name=l60 lab=inch_n}
C {devices/lab_wire.sym} 2415 610 2 0 {name=l61 lab=inch_n}
C {devices/lab_wire.sym} 2980 610 2 0 {name=l62 lab=inch_n}
C {devices/lab_wire.sym} -1655 610 2 0 {name=l63 lab=inch_p}
C {devices/lab_wire.sym} -1470 610 2 0 {name=l64 lab=inch_p}
C {devices/lab_wire.sym} 1375 610 2 0 {name=l65 lab=inch_p}
C {devices/lab_wire.sym} 2600 610 2 0 {name=l66 lab=inch_p}
C {devices/lab_wire.sym} 2790 610 2 0 {name=l67 lab=inch_p}
C {devices/lab_wire.sym} -230 430 0 1 {name=l68 lab=out1_n}
C {devices/lab_wire.sym} -40 430 0 1 {name=l69 lab=out1_n}
C {devices/lab_wire.sym} 150 350 2 0 {name=l70 lab=out1_n}
C {devices/lab_wire.sym} 150 430 0 1 {name=l71 lab=out1_n}
C {devices/lab_wire.sym} 335 430 0 1 {name=l72 lab=out1_n}
C {devices/lab_wire.sym} 525 430 0 1 {name=l73 lab=out1_n}
C {devices/lab_wire.sym} -2530 430 0 1 {name=l74 lab=out1_p}
C {devices/lab_wire.sym} 585 350 2 0 {name=l75 lab=out1_p}
C {devices/lab_wire.sym} 3540 430 0 1 {name=l76 lab=out1_p}
C {devices/lab_wire.sym} -180 170 0 1 {name=l77 lab=tail}
C {devices/lab_wire.sym} 385 90 2 0 {name=l78 lab=tail}
C {devices/lab_wire.sym} 1175 170 0 1 {name=l79 lab=tail}
C {devices/lab_wire.sym} 285 780 0 0 {name=l80 lab=vb1}
C {devices/lab_wire.sym} 535 720 0 1 {name=l81 lab=vb1}
C {devices/lab_wire.sym} 190 580 2 0 {name=l82 lab=vb2}
C {devices/lab_wire.sym} 3500 460 0 1 {name=l83 lab=vb2}
C {devices/lab_wire.sym} 250 260 0 1 {name=l84 lab=vb3}
C {devices/lab_wire.sym} 545 200 0 1 {name=l85 lab=vb3}
C {devices/lab_wire.sym} -280 0 0 0 {name=l86 lab=vb4}
C {devices/lab_wire.sym} 250 0 0 1 {name=l87 lab=vb4}
C {devices/lab_wire.sym} 545 -60 0 1 {name=l88 lab=vb4}
C {devices/lab_wire.sym} 855 0 0 0 {name=l89 lab=vb4}
C {devices/lab_wire.sym} -1655 430 0 1 {name=l90 lab=vinn}
C {devices/lab_wire.sym} -1280 430 0 1 {name=l91 lab=vinn}
C {devices/lab_wire.sym} 2415 430 0 1 {name=l92 lab=vinn}
C {devices/lab_wire.sym} 2790 430 0 1 {name=l93 lab=vinn}
C {devices/lab_wire.sym} -1845 430 0 1 {name=l94 lab=vinp}
C {devices/lab_wire.sym} -1470 430 0 1 {name=l95 lab=vinp}
C {devices/lab_wire.sym} 2600 430 0 1 {name=l96 lab=vinp}
C {devices/lab_wire.sym} 2980 430 0 1 {name=l97 lab=vinp}
C {devices/lab_wire.sym} -2030 610 2 0 {name=l98 lab=voutn}
C {devices/lab_wire.sym} -1090 610 2 0 {name=l99 lab=voutn}
C {devices/lab_wire.sym} -180 90 2 0 {name=l100 lab=voutn}
C {devices/lab_wire.sym} 955 170 0 1 {name=l101 lab=voutn}
C {devices/lab_wire.sym} 1595 610 2 0 {name=l102 lab=voutn}
C {devices/lab_wire.sym} 2225 610 2 0 {name=l103 lab=voutn}
C {devices/lab_wire.sym} 3165 610 2 0 {name=l104 lab=voutn}
C {devices/lab_wire.sym} -2220 610 2 0 {name=l105 lab=voutp}
C {devices/lab_wire.sym} -905 610 2 0 {name=l106 lab=voutp}
C {devices/lab_wire.sym} -525 610 2 0 {name=l107 lab=voutp}
C {devices/lab_wire.sym} 385 170 0 1 {name=l108 lab=voutp}
C {devices/lab_wire.sym} 955 90 2 0 {name=l109 lab=voutp}
C {devices/lab_wire.sym} 2040 610 2 0 {name=l110 lab=voutp}
C {devices/lab_wire.sym} 3355 610 2 0 {name=l111 lab=voutp}
C {devices/lab_wire.sym} -735 610 2 0 {name=l112 lab=vref}
C {devices/lab_wire.sym} 1805 610 2 0 {name=l113 lab=vref}
C {devices/lab_wire.sym} -735 430 0 1 {name=l114 lab=vsum_n}
C {devices/lab_wire.sym} 715 610 2 0 {name=l115 lab=vsum_n}
C {devices/lab_wire.sym} 1135 200 0 1 {name=l116 lab=vsum_n}
C {devices/lab_wire.sym} 1155 430 0 1 {name=l117 lab=vsum_n}
C {devices/lab_wire.sym} -280 260 0 0 {name=l118 lab=vsum_p}
C {devices/lab_wire.sym} 935 610 2 0 {name=l119 lab=vsum_p}
C {devices/lab_wire.sym} 1375 430 0 1 {name=l120 lab=vsum_p}
C {devices/lab_wire.sym} 1805 430 0 1 {name=l121 lab=vsum_p}
C {devices/lab_wire.sym} 445 94 2 0 {name=l122 lab=vdd}
C {devices/lab_wire.sym} 90 354 2 0 {name=l123 lab=vdd}
C {devices/lab_wire.sym} 645 354 2 0 {name=l124 lab=vdd}
C {devices/lab_wire.sym} -100 614 2 0 {name=l125 lab=vdd}
C {devices/lab_wire.sym} 3980 614 2 0 {name=l126 lab=vdd}
C {devices/lab_wire.sym} -120 354 2 0 {name=l127 lab=vdd}
C {devices/lab_wire.sym} 2100 614 2 0 {name=l128 lab=vdd}
C {devices/lab_wire.sym} 2285 614 2 0 {name=l129 lab=vdd}
C {devices/lab_wire.sym} 2475 614 2 0 {name=l130 lab=vdd}
C {devices/lab_wire.sym} 2660 614 2 0 {name=l131 lab=vdd}
C {devices/lab_wire.sym} -290 614 2 0 {name=l132 lab=vdd}
C {devices/lab_wire.sym} 1235 354 2 0 {name=l133 lab=vdd}
C {devices/lab_wire.sym} 4165 614 2 0 {name=l134 lab=vdd}
C {devices/lab_wire.sym} 2850 614 2 0 {name=l135 lab=vdd}
C {devices/lab_wire.sym} 3040 614 2 0 {name=l136 lab=vdd}
C {devices/lab_wire.sym} 3225 614 2 0 {name=l137 lab=vdd}
C {devices/lab_wire.sym} 3415 614 2 0 {name=l138 lab=vdd}
C {devices/lab_wire.sym} 90 94 2 0 {name=l139 lab=vdd}
C {devices/lab_wire.sym} 645 94 2 0 {name=l140 lab=vdd}
C {devices/lab_wire.sym} 1015 94 2 0 {name=l141 lab=vdd}
C {devices/lab_wire.sym} -120 94 2 0 {name=l142 lab=vdd}
C {devices/lab_wire.sym} 3600 614 2 0 {name=l143 lab=vss}
C {devices/lab_wire.sym} 90 614 2 0 {name=l144 lab=vss}
C {devices/lab_wire.sym} 445 354 2 0 {name=l145 lab=vss}
C {devices/lab_wire.sym} 1015 354 2 0 {name=l146 lab=vss}
C {devices/lab_wire.sym} 275 614 2 0 {name=l147 lab=vss}
C {devices/lab_wire.sym} 3790 614 2 0 {name=l148 lab=vss}
C {devices/lab_wire.sym} -845 614 2 0 {name=l149 lab=vss}
C {devices/lab_wire.sym} -1030 614 2 0 {name=l150 lab=vss}
C {devices/lab_wire.sym} -1220 614 2 0 {name=l151 lab=vss}
C {devices/lab_wire.sym} -1410 614 2 0 {name=l152 lab=vss}
C {devices/lab_wire.sym} 465 614 2 0 {name=l153 lab=vss}
C {devices/lab_wire.sym} -2470 614 2 0 {name=l154 lab=vss}
C {devices/lab_wire.sym} -1595 614 2 0 {name=l155 lab=vss}
C {devices/lab_wire.sym} -1785 614 2 0 {name=l156 lab=vss}
C {devices/lab_wire.sym} -1970 614 2 0 {name=l157 lab=vss}
C {devices/lab_wire.sym} -2160 614 2 0 {name=l158 lab=vss}
C {devices/lab_wire.sym} 445 874 2 0 {name=l159 lab=vss}
C {devices/lab_wire.sym} 635 874 2 0 {name=l160 lab=vss}
C {devices/lab_wire.sym} -2890 690 0 1 {name=l161 lab=vb1}
C {devices/lab_wire.sym} -2890 870 2 0 {name=l162 lab=vss}
C {devices/lab_wire.sym} -2890 610 2 0 {name=l163 lab=vss}
C {devices/lab_wire.sym} -2890 350 2 0 {name=l164 lab=vss}
C {devices/lab_wire.sym} -2890 90 2 0 {name=l165 lab=vss}
C {devices/lab_wire.sym} -2890 430 0 1 {name=l166 lab=vb2}
C {devices/lab_wire.sym} -2890 170 0 1 {name=l167 lab=vb3}
C {devices/lab_wire.sym} -2890 -90 0 1 {name=l168 lab=vb4}
C {devices/lab_wire.sym} 385 350 2 0 {name=l169 lab=vss}
C {devices/ipin.sym} -3090 520 0 0 {name=p0 lab=clk_chout_not}
C {devices/ipin.sym} -3090 640 0 0 {name=p1 lab=clk_chfb_not}
C {devices/ipin.sym} -3090 760 0 0 {name=p2 lab=clk_chin_not}
C {devices/ipin.sym} -3090 880 0 0 {name=p3 lab=clk_chin}
C {devices/ipin.sym} -3090 1000 0 0 {name=p4 lab=clk_chfb}
C {devices/ipin.sym} -3090 1120 0 0 {name=p5 lab=clk_chout}
C {devices/iopin.sym} -735 1060 0 0 {name=p6 lab=vref}
C {devices/opin.sym} 4440 30 0 0 {name=p7 lab=voutn}
C {devices/opin.sym} 4440 150 0 0 {name=p8 lab=voutp}
C {devices/opin.sym} 4440 490 0 0 {name=p9 lab=vinp}
C {devices/opin.sym} 4440 610 0 0 {name=p10 lab=vinn}
