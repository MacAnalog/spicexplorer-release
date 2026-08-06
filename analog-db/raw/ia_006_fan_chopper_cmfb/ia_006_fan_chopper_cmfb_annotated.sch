v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_006_fan_chopper_cmfb} -3120 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -70 780 0 0 {name=CCM value='c_cm'}
C {devices/capa_np.sym} 895 520 0 0 {name=CFB1_CORE value='x_dut_cfb1_core_value'}
C {devices/capa_np.sym} 1155 520 0 0 {name=CFB2_CORE value='x_dut_cfb2_core_value'}
C {devices/capa_np.sym} 635 520 0 0 {name=CIN1_CORE value='x_dut_cin1_core_value'}
C {devices/capa_np.sym} 1415 520 0 0 {name=CIN2_CORE value='x_dut_cin2_core_value'}
C {devices/capa_np.sym} 4785 520 0 0 {name=CM1_CORE value='x_dut_cm1_core_value'}
C {devices/capa_np.sym} 5035 520 0 0 {name=CM2_CORE value='x_dut_cm2_core_value'}
C {devices/res_np.sym} 1675 520 0 0 {name=RB1_CORE value='x_dut_rb1_core_value'}
C {devices/res_np.sym} 1930 520 0 0 {name=RB2_CORE value='x_dut_rb2_core_value'}
C {devices/res_np.sym} 650 390 1 0 {name=RMN_CMFB value='x_dut_rmn_cmfb_value'}
C {devices/res_np.sym} 910 390 0 0 {name=RMP_CMFB value='x_dut_rmp_cmfb_value'}
C {devices/vsource_np.sym} -2740 780 0 0 {name=VB1_CORE value="dc {vb1_core}"}
C {devices/vsource_np.sym} -2740 520 0 0 {name=VB2_CORE value="dc {vb2_core}"}
C {devices/vsource_np.sym} -2740 260 0 0 {name=VB3_CORE value="dc {vb3_core}"}
C {devices/vsource_np.sym} -2740 0 0 0 {name=VB4_CORE value="dc {vb4_core}"}
C {devices/vsource_np.sym} -3080 780 0 0 {name=VREFCM value="dc {vcm_ref}"}
C {devices/sg13_lv_pmos_np.sym} 895 260 0 1 {name=M10_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_core_w l=x_dut_xm10_core_l m=x_dut_xm10_core_m}
C {devices/sg13_lv_pmos_np.sym} 1970 260 0 0 {name=M11_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_core_w l=x_dut_xm11_core_l m=x_dut_xm11_core_m}
C {devices/sg13_lv_nmos_np.sym} 5290 520 0 0 {name=M12_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_core_w l=x_dut_xm12_core_l m=x_dut_xm12_core_m}
C {devices/sg13_lv_nmos_np.sym} 2325 520 0 1 {name=M13_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_core_w l=x_dut_xm13_core_l m=x_dut_xm13_core_m}
C {devices/sg13_lv_nmos_np.sym} 1155 260 0 1 {name=M14_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_core_w l=x_dut_xm14_core_l m=x_dut_xm14_core_m}
C {devices/sg13_lv_nmos_np.sym} 635 260 0 1 {name=M15_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_core_w l=x_dut_xm15_core_l m=x_dut_xm15_core_m}
C {devices/sg13_lv_nmos_np.sym} 2550 520 0 1 {name=M16_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_core_w l=x_dut_xm16_core_l m=x_dut_xm16_core_m}
C {devices/sg13_lv_pmos_np.sym} -350 520 0 1 {name=M17_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_core_w l=x_dut_xm17_core_l m=x_dut_xm17_core_m}
C {devices/sg13_lv_nmos_np.sym} 5515 520 0 0 {name=M18_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_core_w l=x_dut_xm18_core_l m=x_dut_xm18_core_m}
C {devices/sg13_lv_pmos_np.sym} 5745 520 0 0 {name=M19_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_core_w l=x_dut_xm19_core_l m=x_dut_xm19_core_m}
C {devices/sg13_lv_pmos_np.sym} 100 0 0 1 {name=M1_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_cmfb_w l=x_dut_xm1_cmfb_l m=x_dut_xm1_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 1155 0 0 1 {name=M1_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_core_w l=x_dut_xm1_core_l m=x_dut_xm1_core_m}
C {devices/sg13_lv_nmos_np.sym} 2780 520 0 1 {name=M20_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_core_w l=x_dut_xm20_core_l m=x_dut_xm20_core_m}
C {devices/sg13_lv_pmos_np.sym} -575 520 0 1 {name=M21_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_core_w l=x_dut_xm21_core_l m=x_dut_xm21_core_m}
C {devices/sg13_lv_nmos_np.sym} 3010 520 0 1 {name=M22_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_core_w l=x_dut_xm22_core_l m=x_dut_xm22_core_m}
C {devices/sg13_lv_pmos_np.sym} -805 520 0 1 {name=M23_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_core_w l=x_dut_xm23_core_l m=x_dut_xm23_core_m}
C {devices/sg13_lv_nmos_np.sym} 3235 520 0 1 {name=M24_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_core_w l=x_dut_xm24_core_l m=x_dut_xm24_core_m}
C {devices/sg13_lv_pmos_np.sym} -1030 520 0 1 {name=M25_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm25_core_w l=x_dut_xm25_core_l m=x_dut_xm25_core_m}
C {devices/sg13_lv_nmos_np.sym} 3465 520 0 1 {name=M26_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm26_core_w l=x_dut_xm26_core_l m=x_dut_xm26_core_m}
C {devices/sg13_lv_pmos_np.sym} -1260 520 0 1 {name=M27_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm27_core_w l=x_dut_xm27_core_l m=x_dut_xm27_core_m}
C {devices/sg13_lv_nmos_np.sym} 3690 520 0 1 {name=M28_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm28_core_w l=x_dut_xm28_core_l m=x_dut_xm28_core_m}
C {devices/sg13_lv_pmos_np.sym} -1490 520 0 1 {name=M29_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm29_core_w l=x_dut_xm29_core_l m=x_dut_xm29_core_m}
C {devices/sg13_lv_nmos_np.sym} -70 520 0 1 {name=M2_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_cmfb_w l=x_dut_xm2_cmfb_l m=x_dut_xm2_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 2550 260 0 1 {name=M2_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_core_w l=x_dut_xm2_core_l m=x_dut_xm2_core_m}
C {devices/sg13_lv_nmos_np.sym} 5970 520 0 0 {name=M30_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm30_core_w l=x_dut_xm30_core_l m=x_dut_xm30_core_m}
C {devices/sg13_lv_pmos_np.sym} 6200 520 0 0 {name=M31_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm31_core_w l=x_dut_xm31_core_l m=x_dut_xm31_core_m}
C {devices/sg13_lv_nmos_np.sym} 3920 520 0 1 {name=M32_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm32_core_w l=x_dut_xm32_core_l m=x_dut_xm32_core_m}
C {devices/sg13_lv_pmos_np.sym} -1715 520 0 1 {name=M33_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm33_core_w l=x_dut_xm33_core_l m=x_dut_xm33_core_m}
C {devices/sg13_lv_nmos_np.sym} 4150 520 0 1 {name=M34_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm34_core_w l=x_dut_xm34_core_l m=x_dut_xm34_core_m}
C {devices/sg13_lv_pmos_np.sym} -1945 520 0 1 {name=M35_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm35_core_w l=x_dut_xm35_core_l m=x_dut_xm35_core_m}
C {devices/sg13_lv_nmos_np.sym} 4375 520 0 1 {name=M36_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm36_core_w l=x_dut_xm36_core_l m=x_dut_xm36_core_m}
C {devices/sg13_lv_pmos_np.sym} -2170 520 0 1 {name=M37_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm37_core_w l=x_dut_xm37_core_l m=x_dut_xm37_core_m}
C {devices/sg13_lv_nmos_np.sym} 4605 520 0 1 {name=M38_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm38_core_w l=x_dut_xm38_core_l m=x_dut_xm38_core_m}
C {devices/sg13_lv_pmos_np.sym} -2400 520 0 1 {name=M39_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm39_core_w l=x_dut_xm39_core_l m=x_dut_xm39_core_m}
C {devices/sg13_lv_pmos_np.sym} 1435 0 0 0 {name=M3_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_cmfb_w l=x_dut_xm3_cmfb_l m=x_dut_xm3_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} -350 260 0 1 {name=M3_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_core_w l=x_dut_xm3_core_l m=x_dut_xm3_core_m}
C {devices/sg13_lv_pmos_np.sym} 270 260 0 0 {name=M4_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_cmfb_w l=x_dut_xm4_cmfb_l m=x_dut_xm4_cmfb_m}
C {devices/sg13_lv_nmos_np.sym} 895 780 0 1 {name=M4_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_core_w l=x_dut_xm4_core_l m=x_dut_xm4_core_m}
C {devices/sg13_lv_pmos_np.sym} -70 260 0 1 {name=M5_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_cmfb_w l=x_dut_xm5_cmfb_l m=x_dut_xm5_cmfb_m}
C {devices/sg13_lv_nmos_np.sym} 1155 780 0 1 {name=M5_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_core_w l=x_dut_xm5_core_l m=x_dut_xm5_core_m}
C {devices/sg13_lv_nmos_np.sym} 270 520 0 0 {name=M6_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_cmfb_w l=x_dut_xm6_cmfb_l m=x_dut_xm6_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 895 0 0 1 {name=M6_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_core_w l=x_dut_xm6_core_l m=x_dut_xm6_core_m}
C {devices/sg13_lv_nmos_np.sym} 1435 260 0 0 {name=M7_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_cmfb_w l=x_dut_xm7_cmfb_l m=x_dut_xm7_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 1970 0 0 0 {name=M7_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_core_w l=x_dut_xm7_core_l m=x_dut_xm7_core_m}
C {devices/sg13_lv_pmos_np.sym} 635 0 0 1 {name=M8O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8o_w l=x_dut_xm8o_l m=x_dut_xm8o_m}
C {devices/sg13_lv_pmos_np.sym} 290 0 0 1 {name=M9O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9o_w l=x_dut_xm9o_l m=x_dut_xm9o_m}
N -3080 690 -3080 750 {}
N -3080 810 -3080 870 {}
N -2740 -90 -2740 -30 {}
N -2740 30 -2740 90 {}
N -2740 170 -2740 230 {}
N -2740 290 -2740 350 {}
N -2740 430 -2740 490 {}
N -2740 550 -2740 610 {}
N -2740 690 -2740 750 {}
N -2740 810 -2740 870 {}
N -2480 520 -2480 614 {}
N -2420 430 -2420 490 {}
N -2420 550 -2420 610 {}
N -2380 520 -2380 580 {}
N -2250 520 -2250 614 {}
N -2190 430 -2190 490 {}
N -2190 550 -2190 610 {}
N -2150 520 -2150 580 {}
N -2025 520 -2025 614 {}
N -1965 430 -1965 490 {}
N -1965 550 -1965 610 {}
N -1925 520 -1925 580 {}
N -1795 520 -1795 614 {}
N -1735 430 -1735 490 {}
N -1735 550 -1735 610 {}
N -1695 520 -1695 580 {}
N -1570 520 -1570 614 {}
N -1510 430 -1510 490 {}
N -1510 550 -1510 610 {}
N -1470 520 -1470 580 {}
N -1340 520 -1340 614 {}
N -1280 430 -1280 490 {}
N -1280 550 -1280 610 {}
N -1240 520 -1240 580 {}
N -1110 520 -1110 614 {}
N -1050 430 -1050 490 {}
N -1050 550 -1050 610 {}
N -1010 520 -1010 580 {}
N -885 520 -885 614 {}
N -825 430 -825 490 {}
N -825 550 -825 610 {}
N -785 520 -785 580 {}
N -655 520 -655 614 {}
N -595 430 -595 490 {}
N -595 550 -595 610 {}
N -555 520 -555 580 {}
N -430 260 -430 354 {}
N -430 520 -430 614 {}
N -370 170 -370 230 {}
N -370 290 -370 350 {}
N -370 430 -370 490 {}
N -370 550 -370 610 {}
N -330 260 -330 320 {}
N -330 520 -330 580 {}
N -150 260 -150 354 {}
N -150 520 -150 614 {}
N -90 170 -90 230 {}
N -90 290 -90 350 {}
N -90 430 -90 490 {}
N -90 550 -90 920 {}
N -70 720 -70 750 {}
N -70 810 -70 920 {}
N 20 0 20 94 {}
N 80 -140 80 -30 {}
N 80 30 80 90 {}
N 120 0 120 60 {}
N 210 0 210 94 {}
N 250 450 250 520 {}
N 270 -140 270 -30 {}
N 270 30 270 90 {}
N 290 170 290 230 {}
N 290 290 290 350 {}
N 290 430 290 490 {}
N 290 550 290 920 {}
N 340 0 340 720 {}
N 350 260 350 354 {}
N 350 520 350 614 {}
N 555 0 555 94 {}
N 590 260 590 390 {}
N 615 -140 615 -30 {}
N 615 30 615 90 {}
N 615 170 615 230 {}
N 615 290 615 350 {}
N 635 550 635 610 {}
N 655 0 655 60 {}
N 655 200 655 260 {}
N 680 390 680 450 {}
N 815 0 815 94 {}
N 815 260 815 354 {}
N 815 780 815 874 {}
N 875 -140 875 -30 {}
N 875 30 875 90 {}
N 875 170 875 230 {}
N 875 290 875 350 {}
N 875 690 875 750 {}
N 875 810 875 920 {}
N 895 430 895 490 {}
N 895 550 895 610 {}
N 910 300 910 390 {}
N 910 420 910 480 {}
N 915 0 915 60 {}
N 915 200 915 260 {}
N 915 780 915 840 {}
N 1075 0 1075 94 {}
N 1075 260 1075 354 {}
N 1075 780 1075 874 {}
N 1135 -140 1135 -30 {}
N 1135 30 1135 90 {}
N 1135 170 1135 230 {}
N 1135 290 1135 350 {}
N 1135 690 1135 750 {}
N 1135 810 1135 920 {}
N 1155 430 1155 490 {}
N 1155 550 1155 610 {}
N 1415 0 1415 70 {}
N 1415 190 1415 260 {}
N 1415 430 1415 490 {}
N 1415 550 1415 610 {}
N 1455 -140 1455 -30 {}
N 1455 30 1455 70 {}
N 1455 170 1455 230 {}
N 1455 290 1455 920 {}
N 1515 0 1515 94 {}
N 1515 260 1515 354 {}
N 1675 430 1675 490 {}
N 1675 550 1675 610 {}
N 1930 430 1930 490 {}
N 1930 550 1930 610 {}
N 1990 -140 1990 -30 {}
N 1990 30 1990 90 {}
N 1990 170 1990 230 {}
N 1990 290 1990 350 {}
N 2050 0 2050 94 {}
N 2050 260 2050 354 {}
N 2245 520 2245 614 {}
N 2305 430 2305 490 {}
N 2305 550 2305 610 {}
N 2345 520 2345 580 {}
N 2470 260 2470 354 {}
N 2470 520 2470 614 {}
N 2530 170 2530 230 {}
N 2530 290 2530 350 {}
N 2530 430 2530 490 {}
N 2530 550 2530 610 {}
N 2570 520 2570 580 {}
N 2700 520 2700 614 {}
N 2760 430 2760 490 {}
N 2760 550 2760 610 {}
N 2800 520 2800 580 {}
N 2930 520 2930 614 {}
N 2990 430 2990 490 {}
N 2990 550 2990 610 {}
N 3030 520 3030 580 {}
N 3155 520 3155 614 {}
N 3215 430 3215 490 {}
N 3215 550 3215 610 {}
N 3255 520 3255 580 {}
N 3385 520 3385 614 {}
N 3445 430 3445 490 {}
N 3445 550 3445 610 {}
N 3485 520 3485 580 {}
N 3610 520 3610 614 {}
N 3670 430 3670 490 {}
N 3670 550 3670 610 {}
N 3710 520 3710 580 {}
N 3840 520 3840 614 {}
N 3900 430 3900 490 {}
N 3900 550 3900 610 {}
N 3940 520 3940 580 {}
N 4070 520 4070 614 {}
N 4130 430 4130 490 {}
N 4130 550 4130 610 {}
N 4170 520 4170 580 {}
N 4295 520 4295 614 {}
N 4355 430 4355 490 {}
N 4355 550 4355 610 {}
N 4395 520 4395 580 {}
N 4525 520 4525 614 {}
N 4585 430 4585 490 {}
N 4585 550 4585 610 {}
N 4625 520 4625 580 {}
N 4785 260 4785 490 {}
N 4785 550 4785 610 {}
N 5035 260 5035 490 {}
N 5035 550 5035 610 {}
N 5270 460 5270 520 {}
N 5310 430 5310 490 {}
N 5310 550 5310 610 {}
N 5370 520 5370 614 {}
N 5535 460 5535 490 {}
N 5535 550 5535 610 {}
N 5595 520 5595 614 {}
N 5765 460 5765 490 {}
N 5765 550 5765 610 {}
N 5825 520 5825 614 {}
N 5990 460 5990 490 {}
N 5990 550 5990 610 {}
N 6050 520 6050 614 {}
N 6220 460 6220 490 {}
N 6220 550 6220 580 {}
N 6280 520 6280 614 {}
N -3140 -140 6455 -140 {}
N 20 0 80 0 {}
N 120 0 150 0 {}
N 210 0 270 0 {}
N 310 0 370 0 {}
N 555 0 615 0 {}
N 655 0 685 0 {}
N 815 0 875 0 {}
N 915 0 945 0 {}
N 1075 0 1135 0 {}
N 1175 0 1235 0 {}
N 1355 0 1415 0 {}
N 1455 0 1515 0 {}
N 1890 0 1950 0 {}
N 1990 0 2050 0 {}
N 1415 70 1455 70 {}
N 1415 190 1455 190 {}
N -430 260 -370 260 {}
N -330 260 -300 260 {}
N -150 260 -90 260 {}
N -50 260 10 260 {}
N 190 260 250 260 {}
N 290 260 350 260 {}
N 655 260 685 260 {}
N 815 260 875 260 {}
N 915 260 945 260 {}
N 1075 260 1135 260 {}
N 1175 260 1235 260 {}
N 1455 260 1515 260 {}
N 1890 260 1950 260 {}
N 1990 260 2050 260 {}
N 2470 260 2530 260 {}
N 2570 260 2630 260 {}
N 560 390 620 390 {}
N 680 390 710 390 {}
N 250 450 290 450 {}
N 5310 460 6220 460 {}
N 575 490 635 490 {}
N -2480 520 -2420 520 {}
N -2380 520 -2350 520 {}
N -2250 520 -2190 520 {}
N -2150 520 -2120 520 {}
N -2025 520 -1965 520 {}
N -1925 520 -1895 520 {}
N -1795 520 -1735 520 {}
N -1695 520 -1665 520 {}
N -1570 520 -1510 520 {}
N -1470 520 -1440 520 {}
N -1340 520 -1280 520 {}
N -1240 520 -1210 520 {}
N -1110 520 -1050 520 {}
N -1010 520 -980 520 {}
N -885 520 -825 520 {}
N -785 520 -755 520 {}
N -655 520 -595 520 {}
N -555 520 -525 520 {}
N -430 520 -370 520 {}
N -330 520 -300 520 {}
N -150 520 -90 520 {}
N -50 520 10 520 {}
N 290 520 350 520 {}
N 2245 520 2305 520 {}
N 2345 520 2375 520 {}
N 2470 520 2530 520 {}
N 2570 520 2600 520 {}
N 2700 520 2760 520 {}
N 2800 520 2830 520 {}
N 2930 520 2990 520 {}
N 3030 520 3060 520 {}
N 3155 520 3215 520 {}
N 3255 520 3285 520 {}
N 3385 520 3445 520 {}
N 3485 520 3515 520 {}
N 3610 520 3670 520 {}
N 3710 520 3740 520 {}
N 3840 520 3900 520 {}
N 3940 520 3970 520 {}
N 4070 520 4130 520 {}
N 4170 520 4200 520 {}
N 4295 520 4355 520 {}
N 4395 520 4425 520 {}
N 4525 520 4585 520 {}
N 4625 520 4655 520 {}
N 5240 520 5270 520 {}
N 5310 520 5370 520 {}
N 5465 520 5495 520 {}
N 5535 520 5595 520 {}
N 5695 520 5725 520 {}
N 5765 520 5825 520 {}
N 5920 520 5950 520 {}
N 5990 520 6050 520 {}
N 6150 520 6180 520 {}
N 6220 520 6280 520 {}
N 5990 580 6220 580 {}
N -70 720 340 720 {}
N 815 780 875 780 {}
N 915 780 945 780 {}
N 1075 780 1135 780 {}
N 1175 780 1235 780 {}
N -3140 920 6455 920 {}
C {devices/lab_wire.sym} -3140 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -3140 920 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -2380 580 2 0 {name=l2 lab=clk_chfb}
C {devices/lab_wire.sym} -2150 580 2 0 {name=l3 lab=clk_chfb}
C {devices/lab_wire.sym} 2800 580 2 0 {name=l4 lab=clk_chfb}
C {devices/lab_wire.sym} 3030 580 2 0 {name=l5 lab=clk_chfb}
C {devices/lab_wire.sym} -785 580 2 0 {name=l6 lab=clk_chfb_not}
C {devices/lab_wire.sym} -555 580 2 0 {name=l7 lab=clk_chfb_not}
C {devices/lab_wire.sym} 4395 580 2 0 {name=l8 lab=clk_chfb_not}
C {devices/lab_wire.sym} 4625 580 2 0 {name=l9 lab=clk_chfb_not}
C {devices/lab_wire.sym} -1925 580 2 0 {name=l10 lab=clk_chin}
C {devices/lab_wire.sym} -1695 580 2 0 {name=l11 lab=clk_chin}
C {devices/lab_wire.sym} 3255 580 2 0 {name=l12 lab=clk_chin}
C {devices/lab_wire.sym} 3485 580 2 0 {name=l13 lab=clk_chin}
C {devices/lab_wire.sym} -1240 580 2 0 {name=l14 lab=clk_chin_not}
C {devices/lab_wire.sym} -1010 580 2 0 {name=l15 lab=clk_chin_not}
C {devices/lab_wire.sym} 3940 580 2 0 {name=l16 lab=clk_chin_not}
C {devices/lab_wire.sym} 4170 580 2 0 {name=l17 lab=clk_chin_not}
C {devices/lab_wire.sym} -1470 580 2 0 {name=l18 lab=clk_chout}
C {devices/lab_wire.sym} 2570 580 2 0 {name=l19 lab=clk_chout}
C {devices/lab_wire.sym} 5495 520 0 0 {name=l20 lab=clk_chout}
C {devices/lab_wire.sym} 6180 520 0 0 {name=l21 lab=clk_chout}
C {devices/lab_wire.sym} -330 580 2 0 {name=l22 lab=clk_chout_not}
C {devices/lab_wire.sym} 3710 580 2 0 {name=l23 lab=clk_chout_not}
C {devices/lab_wire.sym} 5725 520 0 0 {name=l24 lab=clk_chout_not}
C {devices/lab_wire.sym} 5950 520 0 0 {name=l25 lab=clk_chout_not}
C {devices/lab_wire.sym} 120 60 2 0 {name=l26 lab=cmfb__bias}
C {devices/lab_wire.sym} 1355 0 0 0 {name=l27 lab=cmfb__bias}
C {devices/lab_wire.sym} 1455 170 0 1 {name=l28 lab=cmfb__bias}
C {devices/lab_wire.sym} 190 260 0 0 {name=l29 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 560 390 0 0 {name=l30 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 910 300 0 1 {name=l31 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 10 520 0 1 {name=l32 lab=cmfb__mirr}
C {devices/lab_wire.sym} 290 430 0 1 {name=l33 lab=cmfb__mirr}
C {devices/lab_wire.sym} 290 350 2 0 {name=l34 lab=cmfb__mirr}
C {devices/lab_wire.sym} -90 170 0 1 {name=l35 lab=cmfb__ptail}
C {devices/lab_wire.sym} 80 90 2 0 {name=l36 lab=cmfb__ptail}
C {devices/lab_wire.sym} 290 170 0 1 {name=l37 lab=cmfb__ptail}
C {devices/lab_wire.sym} 875 90 2 0 {name=l38 lab=core__casc_src_n}
C {devices/lab_wire.sym} 875 170 0 1 {name=l39 lab=core__casc_src_n}
C {devices/lab_wire.sym} 1990 90 2 0 {name=l40 lab=core__casc_src_p}
C {devices/lab_wire.sym} 1990 170 0 1 {name=l41 lab=core__casc_src_p}
C {devices/lab_wire.sym} -2420 430 0 1 {name=l42 lab=core__fbch_n}
C {devices/lab_wire.sym} -825 430 0 1 {name=l43 lab=core__fbch_n}
C {devices/lab_wire.sym} 1155 430 0 1 {name=l44 lab=core__fbch_n}
C {devices/lab_wire.sym} 2990 430 0 1 {name=l45 lab=core__fbch_n}
C {devices/lab_wire.sym} 4585 430 0 1 {name=l46 lab=core__fbch_n}
C {devices/lab_wire.sym} -2190 430 0 1 {name=l47 lab=core__fbch_p}
C {devices/lab_wire.sym} -595 430 0 1 {name=l48 lab=core__fbch_p}
C {devices/lab_wire.sym} 895 430 0 1 {name=l49 lab=core__fbch_p}
C {devices/lab_wire.sym} 2760 430 0 1 {name=l50 lab=core__fbch_p}
C {devices/lab_wire.sym} 4355 430 0 1 {name=l51 lab=core__fbch_p}
C {devices/lab_wire.sym} -370 350 2 0 {name=l52 lab=core__fold_n}
C {devices/lab_wire.sym} 1135 690 0 1 {name=l53 lab=core__fold_n}
C {devices/lab_wire.sym} 2305 610 2 0 {name=l54 lab=core__fold_n}
C {devices/lab_wire.sym} 875 690 0 1 {name=l55 lab=core__fold_p}
C {devices/lab_wire.sym} 2530 350 2 0 {name=l56 lab=core__fold_p}
C {devices/lab_wire.sym} 5310 610 2 0 {name=l57 lab=core__fold_p}
C {devices/lab_wire.sym} -370 610 2 0 {name=l58 lab=core__g2_n}
C {devices/lab_wire.sym} 655 200 0 1 {name=l59 lab=core__g2_n}
C {devices/lab_wire.sym} 2530 610 2 0 {name=l60 lab=core__g2_n}
C {devices/lab_wire.sym} 5035 430 0 1 {name=l61 lab=core__g2_n}
C {devices/lab_wire.sym} 5990 610 2 0 {name=l62 lab=core__g2_n}
C {devices/lab_wire.sym} -1510 610 2 0 {name=l63 lab=core__g2_p}
C {devices/lab_wire.sym} 1235 260 0 1 {name=l64 lab=core__g2_p}
C {devices/lab_wire.sym} 3670 610 2 0 {name=l65 lab=core__g2_p}
C {devices/lab_wire.sym} 4785 430 0 1 {name=l66 lab=core__g2_p}
C {devices/lab_wire.sym} 5535 610 2 0 {name=l67 lab=core__g2_p}
C {devices/lab_wire.sym} 5765 610 2 0 {name=l68 lab=core__g2_p}
C {devices/lab_wire.sym} -1965 610 2 0 {name=l69 lab=core__inch_n}
C {devices/lab_wire.sym} -1050 610 2 0 {name=l70 lab=core__inch_n}
C {devices/lab_wire.sym} 635 610 2 0 {name=l71 lab=core__inch_n}
C {devices/lab_wire.sym} 3215 610 2 0 {name=l72 lab=core__inch_n}
C {devices/lab_wire.sym} 4130 610 2 0 {name=l73 lab=core__inch_n}
C {devices/lab_wire.sym} -1735 610 2 0 {name=l74 lab=core__inch_p}
C {devices/lab_wire.sym} -1280 610 2 0 {name=l75 lab=core__inch_p}
C {devices/lab_wire.sym} 1415 610 2 0 {name=l76 lab=core__inch_p}
C {devices/lab_wire.sym} 3445 610 2 0 {name=l77 lab=core__inch_p}
C {devices/lab_wire.sym} 3900 610 2 0 {name=l78 lab=core__inch_p}
C {devices/lab_wire.sym} -1510 430 0 1 {name=l79 lab=core__out1_n}
C {devices/lab_wire.sym} -370 430 0 1 {name=l80 lab=core__out1_n}
C {devices/lab_wire.sym} 875 350 2 0 {name=l81 lab=core__out1_n}
C {devices/lab_wire.sym} 2305 430 0 1 {name=l82 lab=core__out1_n}
C {devices/lab_wire.sym} 2530 430 0 1 {name=l83 lab=core__out1_n}
C {devices/lab_wire.sym} 3670 430 0 1 {name=l84 lab=core__out1_n}
C {devices/lab_wire.sym} 1990 350 2 0 {name=l85 lab=core__out1_p}
C {devices/lab_wire.sym} 5310 430 0 1 {name=l86 lab=core__out1_p}
C {devices/lab_wire.sym} -370 170 0 1 {name=l87 lab=core__tail}
C {devices/lab_wire.sym} 1135 90 2 0 {name=l88 lab=core__tail}
C {devices/lab_wire.sym} 2530 170 0 1 {name=l89 lab=core__tail}
C {devices/lab_wire.sym} 915 840 2 0 {name=l90 lab=core__vb1}
C {devices/lab_wire.sym} 1235 780 0 1 {name=l91 lab=core__vb1}
C {devices/lab_wire.sym} 2345 580 2 0 {name=l92 lab=core__vb2}
C {devices/lab_wire.sym} 5270 460 0 1 {name=l93 lab=core__vb2}
C {devices/lab_wire.sym} 915 200 0 1 {name=l94 lab=core__vb3}
C {devices/lab_wire.sym} 1890 260 0 0 {name=l95 lab=core__vb3}
C {devices/lab_wire.sym} 915 60 2 0 {name=l96 lab=core__vb4}
C {devices/lab_wire.sym} 1235 0 0 1 {name=l97 lab=core__vb4}
C {devices/lab_wire.sym} 1890 0 0 0 {name=l98 lab=core__vb4}
C {devices/lab_wire.sym} -330 320 2 0 {name=l99 lab=core__vsum_n}
C {devices/lab_wire.sym} 575 490 0 0 {name=l100 lab=core__vsum_n}
C {devices/lab_wire.sym} 895 610 2 0 {name=l101 lab=core__vsum_n}
C {devices/lab_wire.sym} 1675 430 0 1 {name=l102 lab=core__vsum_n}
C {devices/lab_wire.sym} 1155 610 2 0 {name=l103 lab=core__vsum_p}
C {devices/lab_wire.sym} 1415 430 0 1 {name=l104 lab=core__vsum_p}
C {devices/lab_wire.sym} 1930 430 0 1 {name=l105 lab=core__vsum_p}
C {devices/lab_wire.sym} 2630 260 0 1 {name=l106 lab=core__vsum_p}
C {devices/lab_wire.sym} -90 350 2 0 {name=l107 lab=vb4o}
C {devices/lab_wire.sym} -90 430 0 1 {name=l108 lab=vb4o}
C {devices/lab_wire.sym} 370 0 0 1 {name=l109 lab=vb4o}
C {devices/lab_wire.sym} 655 60 2 0 {name=l110 lab=vb4o}
C {devices/lab_wire.sym} -1735 430 0 1 {name=l111 lab=vinn}
C {devices/lab_wire.sym} -1050 430 0 1 {name=l112 lab=vinn}
C {devices/lab_wire.sym} 3215 430 0 1 {name=l113 lab=vinn}
C {devices/lab_wire.sym} 3900 430 0 1 {name=l114 lab=vinn}
C {devices/lab_wire.sym} -1965 430 0 1 {name=l115 lab=vinp}
C {devices/lab_wire.sym} -1280 430 0 1 {name=l116 lab=vinp}
C {devices/lab_wire.sym} 3445 430 0 1 {name=l117 lab=vinp}
C {devices/lab_wire.sym} 4130 430 0 1 {name=l118 lab=vinp}
C {devices/lab_wire.sym} -2190 610 2 0 {name=l119 lab=voutn}
C {devices/lab_wire.sym} -825 610 2 0 {name=l120 lab=voutn}
C {devices/lab_wire.sym} 270 90 2 0 {name=l121 lab=voutn}
C {devices/lab_wire.sym} 615 170 0 1 {name=l122 lab=voutn}
C {devices/lab_wire.sym} 680 450 2 0 {name=l123 lab=voutn}
C {devices/lab_wire.sym} 2990 610 2 0 {name=l124 lab=voutn}
C {devices/lab_wire.sym} 4355 610 2 0 {name=l125 lab=voutn}
C {devices/lab_wire.sym} 5035 610 2 0 {name=l126 lab=voutn}
C {devices/lab_wire.sym} -2420 610 2 0 {name=l127 lab=voutp}
C {devices/lab_wire.sym} -595 610 2 0 {name=l128 lab=voutp}
C {devices/lab_wire.sym} 615 90 2 0 {name=l129 lab=voutp}
C {devices/lab_wire.sym} 910 480 2 0 {name=l130 lab=voutp}
C {devices/lab_wire.sym} 1135 170 0 1 {name=l131 lab=voutp}
C {devices/lab_wire.sym} 2760 610 2 0 {name=l132 lab=voutp}
C {devices/lab_wire.sym} 4585 610 2 0 {name=l133 lab=voutp}
C {devices/lab_wire.sym} 4785 610 2 0 {name=l134 lab=voutp}
C {devices/lab_wire.sym} 1675 610 2 0 {name=l135 lab=vref}
C {devices/lab_wire.sym} 1930 610 2 0 {name=l136 lab=vref}
C {devices/lab_wire.sym} 10 260 0 1 {name=l137 lab=vref_cm}
C {devices/lab_wire.sym} 815 354 2 0 {name=l138 lab=vdd}
C {devices/lab_wire.sym} 2050 354 2 0 {name=l139 lab=vdd}
C {devices/lab_wire.sym} -430 614 2 0 {name=l140 lab=vdd}
C {devices/lab_wire.sym} 5825 614 2 0 {name=l141 lab=vdd}
C {devices/lab_wire.sym} 20 94 2 0 {name=l142 lab=vdd}
C {devices/lab_wire.sym} 1075 94 2 0 {name=l143 lab=vdd}
C {devices/lab_wire.sym} -655 614 2 0 {name=l144 lab=vdd}
C {devices/lab_wire.sym} -885 614 2 0 {name=l145 lab=vdd}
C {devices/lab_wire.sym} -1110 614 2 0 {name=l146 lab=vdd}
C {devices/lab_wire.sym} -1340 614 2 0 {name=l147 lab=vdd}
C {devices/lab_wire.sym} -1570 614 2 0 {name=l148 lab=vdd}
C {devices/lab_wire.sym} 2470 354 2 0 {name=l149 lab=vdd}
C {devices/lab_wire.sym} 6280 614 2 0 {name=l150 lab=vdd}
C {devices/lab_wire.sym} -1795 614 2 0 {name=l151 lab=vdd}
C {devices/lab_wire.sym} -2025 614 2 0 {name=l152 lab=vdd}
C {devices/lab_wire.sym} -2250 614 2 0 {name=l153 lab=vdd}
C {devices/lab_wire.sym} -2480 614 2 0 {name=l154 lab=vdd}
C {devices/lab_wire.sym} 1515 94 2 0 {name=l155 lab=vdd}
C {devices/lab_wire.sym} -430 354 2 0 {name=l156 lab=vdd}
C {devices/lab_wire.sym} 350 354 2 0 {name=l157 lab=vdd}
C {devices/lab_wire.sym} -150 354 2 0 {name=l158 lab=vdd}
C {devices/lab_wire.sym} 815 94 2 0 {name=l159 lab=vdd}
C {devices/lab_wire.sym} 2050 94 2 0 {name=l160 lab=vdd}
C {devices/lab_wire.sym} 555 94 2 0 {name=l161 lab=vdd}
C {devices/lab_wire.sym} 210 94 2 0 {name=l162 lab=vdd}
C {devices/lab_wire.sym} 5370 614 2 0 {name=l163 lab=vss}
C {devices/lab_wire.sym} 2245 614 2 0 {name=l164 lab=vss}
C {devices/lab_wire.sym} 1075 354 2 0 {name=l165 lab=vss}
C {devices/lab_wire.sym} 615 260 0 0 {name=l166 lab=vss}
C {devices/lab_wire.sym} 2470 614 2 0 {name=l167 lab=vss}
C {devices/lab_wire.sym} 5595 614 2 0 {name=l168 lab=vss}
C {devices/lab_wire.sym} 2700 614 2 0 {name=l169 lab=vss}
C {devices/lab_wire.sym} 2930 614 2 0 {name=l170 lab=vss}
C {devices/lab_wire.sym} 3155 614 2 0 {name=l171 lab=vss}
C {devices/lab_wire.sym} 3385 614 2 0 {name=l172 lab=vss}
C {devices/lab_wire.sym} 3610 614 2 0 {name=l173 lab=vss}
C {devices/lab_wire.sym} -150 614 2 0 {name=l174 lab=vss}
C {devices/lab_wire.sym} 6050 614 2 0 {name=l175 lab=vss}
C {devices/lab_wire.sym} 3840 614 2 0 {name=l176 lab=vss}
C {devices/lab_wire.sym} 4070 614 2 0 {name=l177 lab=vss}
C {devices/lab_wire.sym} 4295 614 2 0 {name=l178 lab=vss}
C {devices/lab_wire.sym} 4525 614 2 0 {name=l179 lab=vss}
C {devices/lab_wire.sym} 815 874 2 0 {name=l180 lab=vss}
C {devices/lab_wire.sym} 1075 874 2 0 {name=l181 lab=vss}
C {devices/lab_wire.sym} 350 614 2 0 {name=l182 lab=vss}
C {devices/lab_wire.sym} 1515 354 2 0 {name=l183 lab=vss}
C {devices/lab_wire.sym} -2740 870 2 0 {name=l184 lab=vss}
C {devices/lab_wire.sym} -2740 610 2 0 {name=l185 lab=vss}
C {devices/lab_wire.sym} -2740 350 2 0 {name=l186 lab=vss}
C {devices/lab_wire.sym} -2740 90 2 0 {name=l187 lab=vss}
C {devices/lab_wire.sym} -3080 870 2 0 {name=l188 lab=vss}
C {devices/lab_wire.sym} -2740 690 0 1 {name=l189 lab=core__vb1}
C {devices/lab_wire.sym} -2740 430 0 1 {name=l190 lab=core__vb2}
C {devices/lab_wire.sym} -2740 170 0 1 {name=l191 lab=core__vb3}
C {devices/lab_wire.sym} -2740 -90 0 1 {name=l192 lab=core__vb4}
C {devices/lab_wire.sym} -3080 690 0 1 {name=l193 lab=vref_cm}
C {devices/lab_wire.sym} 1135 350 2 0 {name=l194 lab=vss}
C {devices/lab_wire.sym} 615 350 2 0 {name=l195 lab=vss}
C {devices/ipin.sym} -3280 520 0 0 {name=p0 lab=clk_chfb}
C {devices/ipin.sym} -3280 640 0 0 {name=p1 lab=clk_chin}
C {devices/ipin.sym} -3280 760 0 0 {name=p2 lab=clk_chout}
C {devices/ipin.sym} -3280 880 0 0 {name=p3 lab=clk_chin_not}
C {devices/ipin.sym} -3280 1000 0 0 {name=p4 lab=clk_chfb_not}
C {devices/ipin.sym} -3280 1120 0 0 {name=p5 lab=clk_chout_not}
C {devices/iopin.sym} 1675 1060 0 0 {name=p6 lab=vref}
C {devices/opin.sym} 6595 30 0 0 {name=p7 lab=voutn}
C {devices/opin.sym} 6595 150 0 0 {name=p8 lab=voutp}
C {devices/opin.sym} 6595 490 0 0 {name=p9 lab=vinp}
C {devices/opin.sym} 6595 610 0 0 {name=p10 lab=vinn}
B 8 -128 -78 1663 78 {fill=0}
T {PMOS Simple Current Mirror} -128 -96 0 0 0.3 0.3 {layer=8}
B 10 -298 442 498 598 {fill=0}
T {NMOS Simple Current Mirror} -298 424 0 0 0.3 0.3 {layer=10}
B 12 -586 442 2620 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -586 424 0 0 0.3 0.3 {layer=12}
B 21 5445 442 5981 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 5445 424 0 0 0.3 0.3 {layer=21}
B 15 -811 442 2850 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -811 424 0 0 0.3 0.3 {layer=15}
B 13 2544 442 4675 598 {fill=0}
T {NMOS Differential Pair} 2544 424 0 0 0.3 0.3 {layer=13}
B 18 -1041 442 3080 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1041 424 0 0 0.3 0.3 {layer=18}
B 20 2774 442 4445 598 {fill=0}
T {NMOS Differential Pair} 2774 424 0 0 0.3 0.3 {layer=20}
B 8 -1266 442 3305 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1266 424 0 0 0.3 0.3 {layer=8}
B 10 -1496 442 3535 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1496 424 0 0 0.3 0.3 {layer=10}
B 12 -1726 442 3760 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1726 424 0 0 0.3 0.3 {layer=12}
B 21 -578 182 2620 338 {fill=0}
T {PMOS Differential Pair} -578 164 0 0 0.3 0.3 {layer=21}
B 15 5900 442 6436 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 5900 424 0 0 0.3 0.3 {layer=15}
B 13 -1951 442 3990 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1951 424 0 0 0.3 0.3 {layer=13}
B 18 -2181 442 4220 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2181 424 0 0 0.3 0.3 {layer=18}
B 20 -2406 442 4445 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2406 424 0 0 0.3 0.3 {layer=20}
B 8 -2636 442 4675 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2636 424 0 0 0.3 0.3 {layer=8}
B 10 -298 182 498 338 {fill=0}
T {PMOS Differential Pair} -298 164 0 0 0.3 0.3 {layer=10}
