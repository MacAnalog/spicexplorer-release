v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_004_fan_chopper_rrl} -2800 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 915 650 0 0 {name=CAZ1_RRL value='x_dut_caz1_rrl_value'}
C {devices/capa_np.sym} 1175 650 0 0 {name=CAZ2_RRL value='x_dut_caz2_rrl_value'}
C {devices/capa_np.sym} 655 650 0 0 {name=CFB1_MAIN value='x_dut_cfb1_main_value'}
C {devices/capa_np.sym} 1435 650 0 0 {name=CFB2_MAIN value='x_dut_cfb2_main_value'}
C {devices/capa_np.sym} 2485 520 0 0 {name=CIN1_MAIN value='x_dut_cin1_main_value'}
C {devices/capa_np.sym} 2745 520 0 0 {name=CIN2_MAIN value='x_dut_cin2_main_value'}
C {devices/capa_np.sym} 915 910 0 0 {name=CINT1_RRL value='x_dut_cint1_rrl_value'}
C {devices/capa_np.sym} 1175 910 0 0 {name=CINT2_RRL value='x_dut_cint2_rrl_value'}
C {devices/capa_np.sym} 700 1040 0 0 {name=CIN_1_RRL value='cin_val_rrl'}
C {devices/capa_np.sym} 4810 520 0 0 {name=CM1_MAIN value='x_dut_cm1_main_value'}
C {devices/capa_np.sym} 5060 520 0 0 {name=CM2_MAIN value='x_dut_cm2_main_value'}
C {devices/capa_np.sym} 5310 520 1 0 {name=COUT_1_RRL value='cout_val_rrl'}
C {devices/capa_np.sym} 1705 650 0 0 {name=CS1_RRL value='x_dut_cs1_rrl_value'}
C {devices/capa_np.sym} 310 650 0 0 {name=CS2_RRL value='x_dut_cs2_rrl_value'}
C {devices/res_np.sym} 3005 520 0 0 {name=RB1_MAIN value='x_dut_rb1_main_value'}
C {devices/res_np.sym} 3280 520 0 0 {name=RB2_MAIN value='x_dut_rb2_main_value'}
C {devices/res_np.sym} 465 1040 0 0 {name=RIN_1_RRL value='rin_val_rrl'}
C {devices/res_np.sym} 5500 520 1 0 {name=ROUT_1_RRL value='rout_val_rrl'}
C {devices/vsource_np.sym} -2420 1040 0 0 {name=VB1_MAIN value="dc {vb1_main}"}
C {devices/vsource_np.sym} -2420 780 0 0 {name=VB1_RRL value="dc {vb1_rrl}"}
C {devices/vsource_np.sym} -2420 520 0 0 {name=VB2_MAIN value="dc {vb2_main}"}
C {devices/vsource_np.sym} -2420 260 0 0 {name=VB2_RRL value="dc {vb2_rrl}"}
C {devices/vsource_np.sym} -2420 0 0 0 {name=VB3_MAIN value="dc {vb3_main}"}
C {devices/vsource_np.sym} -2760 1040 0 0 {name=VB3_RRL value="dc {vb3_rrl}"}
C {devices/vsource_np.sym} -2760 780 0 0 {name=VB4_MAIN value="dc {vb4_main}"}
C {devices/vsource_np.sym} -2760 520 0 0 {name=VB4_RRL value="dc {vb4_rrl}"}
C {devices/sg13_lv_pmos_np.sym} 645 260 0 1 {name=M10_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_main_w l=x_dut_xm10_main_l m=x_dut_xm10_main_m}
C {devices/sg13_lv_pmos_np.sym} 155 520 0 1 {name=M10_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_rrl_w l=x_dut_xm10_opamp_rrl_l m=x_dut_xm10_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2260 260 0 0 {name=M11_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_main_w l=x_dut_xm11_main_l m=x_dut_xm11_main_m}
C {devices/sg13_lv_nmos_np.sym} -245 780 0 1 {name=M11_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_opamp_rrl_w l=x_dut_xm11_opamp_rrl_l m=x_dut_xm11_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 5690 520 0 0 {name=M12_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_main_w l=x_dut_xm12_main_l m=x_dut_xm12_main_m}
C {devices/sg13_lv_nmos_np.sym} 1185 780 0 0 {name=M12_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_opamp_rrl_w l=x_dut_xm12_opamp_rrl_l m=x_dut_xm12_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 645 520 0 1 {name=M13_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_main_w l=x_dut_xm13_main_l m=x_dut_xm13_main_m}
C {devices/sg13_lv_nmos_np.sym} -245 1040 0 1 {name=M13_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_opamp_rrl_w l=x_dut_xm13_opamp_rrl_l m=x_dut_xm13_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 915 260 0 1 {name=M14_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_main_w l=x_dut_xm14_main_l m=x_dut_xm14_main_m}
C {devices/sg13_lv_nmos_np.sym} 1185 1040 0 0 {name=M14_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_opamp_rrl_w l=x_dut_xm14_opamp_rrl_l m=x_dut_xm14_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1175 260 0 1 {name=M15_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_main_w l=x_dut_xm15_main_l m=x_dut_xm15_main_m}
C {devices/sg13_lv_nmos_np.sym} -1070 520 0 1 {name=M15_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_opamp_rrl_w l=x_dut_xm15_opamp_rrl_l m=x_dut_xm15_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 880 520 0 1 {name=M16_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_main_w l=x_dut_xm16_main_l m=x_dut_xm16_main_m}
C {devices/sg13_lv_nmos_np.sym} 3715 520 0 1 {name=M16_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_opamp_rrl_w l=x_dut_xm16_opamp_rrl_l m=x_dut_xm16_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 410 520 0 1 {name=M17_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_main_w l=x_dut_xm17_main_l m=x_dut_xm17_main_m}
C {devices/sg13_lv_nmos_np.sym} 5920 520 0 0 {name=M18_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_main_w l=x_dut_xm18_main_l m=x_dut_xm18_main_m}
C {devices/sg13_lv_pmos_np.sym} 6145 520 0 0 {name=M19_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_main_w l=x_dut_xm19_main_l m=x_dut_xm19_main_m}
C {devices/sg13_lv_nmos_np.sym} 1655 780 0 1 {name=M1_CHRRL_1_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_1_rrl_w l=x_dut_xm1_chrrl_1_rrl_l m=x_dut_xm1_chrrl_1_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1930 780 0 1 {name=M1_CHRRL_2_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_2_rrl_w l=x_dut_xm1_chrrl_2_rrl_l m=x_dut_xm1_chrrl_2_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2210 780 0 1 {name=M1_CHRRL_3_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_3_rrl_w l=x_dut_xm1_chrrl_3_rrl_l m=x_dut_xm1_chrrl_3_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2485 780 0 1 {name=M1_CHRRL_4_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_4_rrl_w l=x_dut_xm1_chrrl_4_rrl_l m=x_dut_xm1_chrrl_4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 915 0 0 1 {name=M1_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_main_w l=x_dut_xm1_main_l m=x_dut_xm1_main_m}
C {devices/sg13_lv_pmos_np.sym} 1175 0 0 1 {name=M1_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_opamp_rrl_w l=x_dut_xm1_opamp_rrl_l m=x_dut_xm1_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1655 1040 0 1 {name=M1_S1_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s1_rrl_w l=x_dut_xm1_s1_rrl_l m=x_dut_xm1_s1_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 260 1040 0 1 {name=M1_S2_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s2_rrl_w l=x_dut_xm1_s2_rrl_l m=x_dut_xm1_s2_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1120 520 0 1 {name=M1_S3_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s3_rrl_w l=x_dut_xm1_s3_rrl_l m=x_dut_xm1_s3_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1355 520 0 1 {name=M1_S4_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s4_rrl_w l=x_dut_xm1_s4_rrl_l m=x_dut_xm1_s4_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 645 780 0 1 {name=M1_S5_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s5_rrl_w l=x_dut_xm1_s5_rrl_l m=x_dut_xm1_s5_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 880 780 0 1 {name=M1_S6_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s6_rrl_w l=x_dut_xm1_s6_rrl_l m=x_dut_xm1_s6_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2745 780 0 1 {name=M20_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_main_w l=x_dut_xm20_main_l m=x_dut_xm20_main_m}
C {devices/sg13_lv_pmos_np.sym} -615 780 0 1 {name=M21_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_main_w l=x_dut_xm21_main_l m=x_dut_xm21_main_m}
C {devices/sg13_lv_nmos_np.sym} 3005 780 0 1 {name=M22_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_main_w l=x_dut_xm22_main_l m=x_dut_xm22_main_m}
C {devices/sg13_lv_pmos_np.sym} -845 780 0 1 {name=M23_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_main_w l=x_dut_xm23_main_l m=x_dut_xm23_main_m}
C {devices/sg13_lv_nmos_np.sym} -1350 520 0 1 {name=M24_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_main_w l=x_dut_xm24_main_l m=x_dut_xm24_main_m}
C {devices/sg13_lv_pmos_np.sym} 3945 520 0 1 {name=M25_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm25_main_w l=x_dut_xm25_main_l m=x_dut_xm25_main_m}
C {devices/sg13_lv_nmos_np.sym} -1625 520 0 1 {name=M26_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm26_main_w l=x_dut_xm26_main_l m=x_dut_xm26_main_m}
C {devices/sg13_lv_pmos_np.sym} 4170 520 0 1 {name=M27_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm27_main_w l=x_dut_xm27_main_l m=x_dut_xm27_main_m}
C {devices/sg13_lv_nmos_np.sym} -205 520 0 1 {name=M28_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm28_main_w l=x_dut_xm28_main_l m=x_dut_xm28_main_m}
C {devices/sg13_lv_pmos_np.sym} -465 520 0 1 {name=M29_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm29_main_w l=x_dut_xm29_main_l m=x_dut_xm29_main_m}
C {devices/sg13_lv_pmos_np.sym} 3280 780 0 1 {name=M2_CHRRL_1_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_1_rrl_w l=x_dut_xm2_chrrl_1_rrl_l m=x_dut_xm2_chrrl_1_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -1070 780 0 1 {name=M2_CHRRL_2_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_2_rrl_w l=x_dut_xm2_chrrl_2_rrl_l m=x_dut_xm2_chrrl_2_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 3715 780 0 1 {name=M2_CHRRL_3_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_3_rrl_w l=x_dut_xm2_chrrl_3_rrl_l m=x_dut_xm2_chrrl_3_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -1350 780 0 1 {name=M2_CHRRL_4_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_4_rrl_w l=x_dut_xm2_chrrl_4_rrl_l m=x_dut_xm2_chrrl_4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1435 260 0 1 {name=M2_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_main_w l=x_dut_xm2_main_l m=x_dut_xm2_main_m}
C {devices/sg13_lv_pmos_np.sym} 1685 260 0 0 {name=M2_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_rrl_w l=x_dut_xm2_opamp_rrl_l m=x_dut_xm2_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1930 1040 0 1 {name=M2_S1_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s1_rrl_w l=x_dut_xm2_s1_rrl_l m=x_dut_xm2_s1_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 25 1040 0 1 {name=M2_S2_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s2_rrl_w l=x_dut_xm2_s2_rrl_l m=x_dut_xm2_s2_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2100 520 0 1 {name=M2_S3_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s3_rrl_w l=x_dut_xm2_s3_rrl_l m=x_dut_xm2_s3_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -695 520 0 1 {name=M2_S4_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s4_rrl_w l=x_dut_xm2_s4_rrl_l m=x_dut_xm2_s4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 410 780 0 1 {name=M2_S5_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s5_rrl_w l=x_dut_xm2_s5_rrl_l m=x_dut_xm2_s5_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 175 780 0 1 {name=M2_S6_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s6_rrl_w l=x_dut_xm2_s6_rrl_l m=x_dut_xm2_s6_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 6375 520 0 0 {name=M30_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm30_main_w l=x_dut_xm30_main_l m=x_dut_xm30_main_m}
C {devices/sg13_lv_pmos_np.sym} 6600 520 0 0 {name=M31_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm31_main_w l=x_dut_xm31_main_l m=x_dut_xm31_main_m}
C {devices/sg13_lv_nmos_np.sym} -1850 520 0 1 {name=M32_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm32_main_w l=x_dut_xm32_main_l m=x_dut_xm32_main_m}
C {devices/sg13_lv_pmos_np.sym} 4400 520 0 1 {name=M33_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm33_main_w l=x_dut_xm33_main_l m=x_dut_xm33_main_m}
C {devices/sg13_lv_nmos_np.sym} -2080 520 0 1 {name=M34_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm34_main_w l=x_dut_xm34_main_l m=x_dut_xm34_main_m}
C {devices/sg13_lv_pmos_np.sym} 4630 520 0 1 {name=M35_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm35_main_w l=x_dut_xm35_main_l m=x_dut_xm35_main_m}
C {devices/sg13_lv_nmos_np.sym} 3945 780 0 1 {name=M36_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm36_main_w l=x_dut_xm36_main_l m=x_dut_xm36_main_m}
C {devices/sg13_lv_pmos_np.sym} -1625 780 0 1 {name=M37_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm37_main_w l=x_dut_xm37_main_l m=x_dut_xm37_main_m}
C {devices/sg13_lv_nmos_np.sym} 4170 780 0 1 {name=M38_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm38_main_w l=x_dut_xm38_main_l m=x_dut_xm38_main_m}
C {devices/sg13_lv_pmos_np.sym} -1850 780 0 1 {name=M39_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm39_main_w l=x_dut_xm39_main_l m=x_dut_xm39_main_m}
C {devices/sg13_lv_pmos_np.sym} -135 260 0 1 {name=M3_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_main_w l=x_dut_xm3_main_l m=x_dut_xm3_main_m}
C {devices/sg13_lv_pmos_np.sym} 155 260 0 1 {name=M3_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_rrl_w l=x_dut_xm3_opamp_rrl_l m=x_dut_xm3_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 4400 780 0 1 {name=M4_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_main_w l=x_dut_xm4_main_l m=x_dut_xm4_main_m}
C {devices/sg13_lv_pmos_np.sym} 1435 0 0 1 {name=M4_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_opamp_rrl_w l=x_dut_xm4_opamp_rrl_l m=x_dut_xm4_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} -2080 780 0 1 {name=M5_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_main_w l=x_dut_xm5_main_l m=x_dut_xm5_main_m}
C {devices/sg13_lv_pmos_np.sym} -355 260 0 1 {name=M5_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_opamp_rrl_w l=x_dut_xm5_opamp_rrl_l m=x_dut_xm5_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 645 0 0 1 {name=M6_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_main_w l=x_dut_xm6_main_l m=x_dut_xm6_main_m}
C {devices/sg13_lv_pmos_np.sym} 2745 260 0 1 {name=M6_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_opamp_rrl_w l=x_dut_xm6_opamp_rrl_l m=x_dut_xm6_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2260 0 0 0 {name=M7_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_main_w l=x_dut_xm7_main_l m=x_dut_xm7_main_m}
C {devices/sg13_lv_pmos_np.sym} -615 260 0 1 {name=M7_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_opamp_rrl_w l=x_dut_xm7_opamp_rrl_l m=x_dut_xm7_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1655 0 0 1 {name=M8_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_main_w l=x_dut_xm8_main_l m=x_dut_xm8_main_m}
C {devices/sg13_lv_pmos_np.sym} 3005 260 0 1 {name=M8_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_opamp_rrl_w l=x_dut_xm8_opamp_rrl_l m=x_dut_xm8_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 260 0 0 1 {name=M9_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_main_w l=x_dut_xm9_main_l m=x_dut_xm9_main_m}
C {devices/sg13_lv_pmos_np.sym} 1685 520 0 0 {name=M9_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_rrl_w l=x_dut_xm9_opamp_rrl_l m=x_dut_xm9_opamp_rrl_m}
N -2760 430 -2760 490 {}
N -2760 550 -2760 610 {}
N -2760 690 -2760 750 {}
N -2760 810 -2760 870 {}
N -2760 950 -2760 1010 {}
N -2760 1070 -2760 1130 {}
N -2420 -90 -2420 -30 {}
N -2420 30 -2420 90 {}
N -2420 170 -2420 230 {}
N -2420 290 -2420 350 {}
N -2420 430 -2420 490 {}
N -2420 550 -2420 610 {}
N -2420 690 -2420 750 {}
N -2420 810 -2420 870 {}
N -2420 950 -2420 1010 {}
N -2420 1070 -2420 1130 {}
N -2160 520 -2160 614 {}
N -2160 780 -2160 874 {}
N -2100 430 -2100 490 {}
N -2100 550 -2100 610 {}
N -2100 690 -2100 750 {}
N -2100 810 -2100 1180 {}
N -2060 520 -2060 580 {}
N -2060 780 -2060 840 {}
N -1930 520 -1930 614 {}
N -1930 780 -1930 874 {}
N -1870 430 -1870 490 {}
N -1870 550 -1870 610 {}
N -1870 690 -1870 750 {}
N -1870 810 -1870 870 {}
N -1830 520 -1830 580 {}
N -1830 780 -1830 840 {}
N -1705 520 -1705 614 {}
N -1705 780 -1705 874 {}
N -1645 430 -1645 490 {}
N -1645 550 -1645 610 {}
N -1645 690 -1645 750 {}
N -1645 810 -1645 870 {}
N -1605 520 -1605 580 {}
N -1605 780 -1605 840 {}
N -1430 520 -1430 614 {}
N -1430 780 -1430 874 {}
N -1370 430 -1370 490 {}
N -1370 550 -1370 610 {}
N -1370 690 -1370 750 {}
N -1370 810 -1370 870 {}
N -1330 520 -1330 580 {}
N -1330 780 -1330 840 {}
N -1150 520 -1150 614 {}
N -1150 780 -1150 874 {}
N -1090 430 -1090 490 {}
N -1090 550 -1090 610 {}
N -1090 690 -1090 750 {}
N -1090 810 -1090 870 {}
N -1050 450 -1050 520 {}
N -1050 780 -1050 840 {}
N -925 780 -925 874 {}
N -865 690 -865 750 {}
N -865 810 -865 870 {}
N -825 780 -825 840 {}
N -775 520 -775 614 {}
N -715 430 -715 490 {}
N -715 550 -715 610 {}
N -695 260 -695 354 {}
N -695 780 -695 874 {}
N -675 520 -675 580 {}
N -635 170 -635 230 {}
N -635 290 -635 350 {}
N -635 690 -635 750 {}
N -635 810 -635 870 {}
N -595 780 -595 840 {}
N -545 520 -545 614 {}
N -485 430 -485 490 {}
N -485 550 -485 610 {}
N -445 520 -445 580 {}
N -435 260 -435 354 {}
N -375 200 -375 230 {}
N -375 290 -375 320 {}
N -335 260 -335 320 {}
N -325 780 -325 874 {}
N -325 1040 -325 1134 {}
N -285 520 -285 614 {}
N -265 690 -265 750 {}
N -265 810 -265 870 {}
N -265 950 -265 1010 {}
N -265 1070 -265 1180 {}
N -225 430 -225 490 {}
N -225 550 -225 610 {}
N -225 1040 -225 1100 {}
N -215 260 -215 354 {}
N -185 520 -185 580 {}
N -155 170 -155 230 {}
N -155 290 -155 350 {}
N -115 260 -115 320 {}
N -55 1040 -55 1134 {}
N 5 950 5 1010 {}
N 5 1070 5 1180 {}
N 45 1040 45 1100 {}
N 75 260 75 354 {}
N 75 520 75 614 {}
N 95 780 95 874 {}
N 135 170 135 230 {}
N 135 290 135 350 {}
N 135 430 135 490 {}
N 135 550 135 610 {}
N 155 690 155 750 {}
N 155 810 155 870 {}
N 175 520 175 580 {}
N 180 0 180 94 {}
N 180 1040 180 1134 {}
N 195 780 195 840 {}
N 240 -140 240 -30 {}
N 240 30 240 90 {}
N 240 980 240 1010 {}
N 240 1070 240 1180 {}
N 310 60 310 620 {}
N 310 680 310 710 {}
N 330 520 330 614 {}
N 330 780 330 874 {}
N 390 430 390 490 {}
N 390 550 390 610 {}
N 390 690 390 750 {}
N 390 810 390 870 {}
N 430 460 430 520 {}
N 430 780 430 840 {}
N 465 950 465 1010 {}
N 465 1070 465 1100 {}
N 565 0 565 94 {}
N 565 260 565 354 {}
N 565 520 565 614 {}
N 565 780 565 874 {}
N 625 -140 625 -30 {}
N 625 30 625 90 {}
N 625 170 625 230 {}
N 625 290 625 350 {}
N 625 430 625 490 {}
N 625 550 625 610 {}
N 625 690 625 750 {}
N 625 810 625 870 {}
N 655 560 655 620 {}
N 655 680 655 740 {}
N 665 0 665 60 {}
N 665 260 665 320 {}
N 665 460 665 520 {}
N 665 780 665 840 {}
N 695 780 695 1040 {}
N 700 950 700 1010 {}
N 700 1070 700 1100 {}
N 800 520 800 614 {}
N 800 780 800 874 {}
N 835 0 835 94 {}
N 835 260 835 354 {}
N 860 430 860 490 {}
N 860 550 860 610 {}
N 860 690 860 750 {}
N 860 810 860 870 {}
N 895 -140 895 -30 {}
N 895 30 895 90 {}
N 895 170 895 230 {}
N 895 290 895 350 {}
N 900 460 900 520 {}
N 915 560 915 620 {}
N 915 680 915 740 {}
N 915 850 915 880 {}
N 915 940 915 1000 {}
N 935 0 935 60 {}
N 935 260 935 320 {}
N 1040 520 1040 614 {}
N 1095 0 1095 94 {}
N 1095 260 1095 354 {}
N 1100 430 1100 490 {}
N 1100 550 1100 610 {}
N 1140 460 1140 520 {}
N 1155 -140 1155 -30 {}
N 1155 30 1155 90 {}
N 1155 170 1155 230 {}
N 1155 290 1155 350 {}
N 1175 560 1175 620 {}
N 1175 680 1175 740 {}
N 1175 820 1175 880 {}
N 1175 940 1175 1100 {}
N 1195 0 1195 60 {}
N 1195 260 1195 320 {}
N 1205 690 1205 750 {}
N 1205 810 1205 870 {}
N 1205 950 1205 1010 {}
N 1205 1070 1205 1180 {}
N 1265 780 1265 874 {}
N 1265 1040 1265 1134 {}
N 1275 520 1275 614 {}
N 1335 430 1335 490 {}
N 1335 550 1335 610 {}
N 1355 0 1355 94 {}
N 1355 260 1355 354 {}
N 1405 520 1405 1040 {}
N 1415 -140 1415 -30 {}
N 1415 30 1415 90 {}
N 1415 170 1415 230 {}
N 1415 290 1415 350 {}
N 1435 560 1435 620 {}
N 1435 680 1435 740 {}
N 1455 0 1455 60 {}
N 1575 0 1575 94 {}
N 1575 780 1575 874 {}
N 1575 1040 1575 1134 {}
N 1635 -140 1635 -30 {}
N 1635 30 1635 90 {}
N 1635 690 1635 750 {}
N 1635 810 1635 870 {}
N 1635 950 1635 1010 {}
N 1635 1070 1635 1180 {}
N 1675 780 1675 840 {}
N 1675 1040 1675 1100 {}
N 1705 170 1705 230 {}
N 1705 290 1705 350 {}
N 1705 430 1705 490 {}
N 1705 590 1705 620 {}
N 1705 680 1705 740 {}
N 1765 260 1765 354 {}
N 1765 520 1765 614 {}
N 1850 780 1850 874 {}
N 1850 1040 1850 1134 {}
N 1910 690 1910 750 {}
N 1910 810 1910 870 {}
N 1910 950 1910 1010 {}
N 1910 1070 1910 1180 {}
N 1950 780 1950 840 {}
N 2020 520 2020 614 {}
N 2080 430 2080 490 {}
N 2080 550 2080 610 {}
N 2130 780 2130 874 {}
N 2190 690 2190 750 {}
N 2190 810 2190 870 {}
N 2230 780 2230 840 {}
N 2280 -140 2280 -30 {}
N 2280 30 2280 90 {}
N 2280 170 2280 230 {}
N 2280 290 2280 350 {}
N 2340 0 2340 94 {}
N 2340 260 2340 354 {}
N 2405 780 2405 874 {}
N 2465 690 2465 750 {}
N 2465 810 2465 870 {}
N 2485 430 2485 490 {}
N 2485 550 2485 610 {}
N 2505 780 2505 840 {}
N 2665 260 2665 354 {}
N 2665 780 2665 874 {}
N 2725 170 2725 230 {}
N 2725 290 2725 350 {}
N 2725 690 2725 750 {}
N 2725 810 2725 870 {}
N 2745 430 2745 490 {}
N 2745 550 2745 610 {}
N 2765 260 2765 320 {}
N 2765 780 2765 840 {}
N 2925 260 2925 354 {}
N 2925 780 2925 874 {}
N 2985 170 2985 230 {}
N 2985 290 2985 350 {}
N 2985 690 2985 750 {}
N 2985 810 2985 870 {}
N 3005 430 3005 490 {}
N 3005 550 3005 610 {}
N 3025 780 3025 840 {}
N 3200 780 3200 874 {}
N 3260 690 3260 750 {}
N 3260 810 3260 870 {}
N 3280 430 3280 490 {}
N 3280 550 3280 610 {}
N 3300 780 3300 840 {}
N 3635 520 3635 614 {}
N 3635 780 3635 874 {}
N 3695 430 3695 490 {}
N 3695 550 3695 610 {}
N 3695 690 3695 750 {}
N 3695 810 3695 870 {}
N 3735 450 3735 520 {}
N 3735 780 3735 840 {}
N 3865 520 3865 614 {}
N 3865 780 3865 874 {}
N 3925 430 3925 490 {}
N 3925 550 3925 610 {}
N 3925 690 3925 750 {}
N 3925 810 3925 870 {}
N 3965 520 3965 580 {}
N 3965 780 3965 840 {}
N 4090 520 4090 614 {}
N 4090 780 4090 874 {}
N 4150 430 4150 490 {}
N 4150 550 4150 610 {}
N 4150 690 4150 750 {}
N 4150 810 4150 870 {}
N 4190 520 4190 580 {}
N 4190 780 4190 840 {}
N 4320 520 4320 614 {}
N 4320 780 4320 874 {}
N 4380 430 4380 490 {}
N 4380 550 4380 610 {}
N 4380 690 4380 750 {}
N 4380 810 4380 1180 {}
N 4420 520 4420 580 {}
N 4550 520 4550 614 {}
N 4610 430 4610 490 {}
N 4610 550 4610 610 {}
N 4650 520 4650 580 {}
N 4810 430 4810 490 {}
N 4810 550 4810 610 {}
N 5060 430 5060 490 {}
N 5060 550 5060 610 {}
N 5250 460 5250 520 {}
N 5340 520 5340 580 {}
N 5370 320 5370 520 {}
N 5530 520 5530 580 {}
N 5670 460 5670 520 {}
N 5710 430 5710 490 {}
N 5710 550 5710 610 {}
N 5770 520 5770 614 {}
N 5940 460 5940 490 {}
N 5940 550 5940 610 {}
N 6000 520 6000 614 {}
N 6165 460 6165 490 {}
N 6165 550 6165 610 {}
N 6225 520 6225 614 {}
N 6395 460 6395 490 {}
N 6395 550 6395 610 {}
N 6455 520 6455 614 {}
N 6620 460 6620 490 {}
N 6620 550 6620 580 {}
N 6680 520 6680 614 {}
N -2820 -140 6855 -140 {}
N 180 0 240 0 {}
N 280 0 340 0 {}
N 565 0 625 0 {}
N 665 0 695 0 {}
N 835 0 895 0 {}
N 935 0 965 0 {}
N 1095 0 1155 0 {}
N 1195 0 1225 0 {}
N 1355 0 1415 0 {}
N 1455 0 1485 0 {}
N 1575 0 1635 0 {}
N 1675 0 2240 0 {}
N 2280 0 2340 0 {}
N 240 60 310 60 {}
N 1635 60 1705 60 {}
N -635 200 -375 200 {}
N -695 260 -635 260 {}
N -595 260 -565 260 {}
N -435 260 -375 260 {}
N -335 260 -265 260 {}
N -215 260 -155 260 {}
N -115 260 -85 260 {}
N 75 260 135 260 {}
N 175 260 235 260 {}
N 565 260 625 260 {}
N 665 260 695 260 {}
N 835 260 895 260 {}
N 935 260 965 260 {}
N 1095 260 1155 260 {}
N 1195 260 1225 260 {}
N 1355 260 1415 260 {}
N 1455 260 1515 260 {}
N 1605 260 1665 260 {}
N 1705 260 1765 260 {}
N 2180 260 2240 260 {}
N 2280 260 2340 260 {}
N 2665 260 2725 260 {}
N 2765 260 2795 260 {}
N 2925 260 2985 260 {}
N 3025 260 3085 260 {}
N -635 320 -375 320 {}
N -1090 450 -1050 450 {}
N 3695 450 3735 450 {}
N 5710 460 6620 460 {}
N -2160 520 -2100 520 {}
N -2060 520 -2030 520 {}
N -1930 520 -1870 520 {}
N -1830 520 -1800 520 {}
N -1705 520 -1645 520 {}
N -1605 520 -1575 520 {}
N -1430 520 -1370 520 {}
N -1330 520 -1300 520 {}
N -1150 520 -1090 520 {}
N -775 520 -715 520 {}
N -675 520 -645 520 {}
N -545 520 -485 520 {}
N -445 520 -415 520 {}
N -285 520 -225 520 {}
N 75 520 135 520 {}
N 175 520 205 520 {}
N 330 520 390 520 {}
N 430 520 460 520 {}
N 565 520 625 520 {}
N 665 520 695 520 {}
N 800 520 860 520 {}
N 900 520 930 520 {}
N 1040 520 1100 520 {}
N 1140 520 1170 520 {}
N 1275 520 1335 520 {}
N 1375 520 1435 520 {}
N 1605 520 1665 520 {}
N 1705 520 1765 520 {}
N 2020 520 2080 520 {}
N 2120 520 2180 520 {}
N 3635 520 3695 520 {}
N 3865 520 3925 520 {}
N 3965 520 3995 520 {}
N 4090 520 4150 520 {}
N 4190 520 4220 520 {}
N 4320 520 4380 520 {}
N 4420 520 4450 520 {}
N 4550 520 4610 520 {}
N 4650 520 4680 520 {}
N 5220 520 5280 520 {}
N 5340 520 5370 520 {}
N 5410 520 5470 520 {}
N 5530 520 5560 520 {}
N 5640 520 5670 520 {}
N 5710 520 5770 520 {}
N 5870 520 5900 520 {}
N 5940 520 6000 520 {}
N 6095 520 6125 520 {}
N 6165 520 6225 520 {}
N 6325 520 6355 520 {}
N 6395 520 6455 520 {}
N 6550 520 6580 520 {}
N 6620 520 6680 520 {}
N 6395 580 6620 580 {}
N 1705 590 4810 590 {}
N 250 680 310 680 {}
N 4380 720 5710 720 {}
N -2160 780 -2100 780 {}
N -2060 780 -2030 780 {}
N -1930 780 -1870 780 {}
N -1830 780 -1800 780 {}
N -1705 780 -1645 780 {}
N -1605 780 -1575 780 {}
N -1430 780 -1370 780 {}
N -1330 780 -1300 780 {}
N -1150 780 -1090 780 {}
N -1050 780 -1020 780 {}
N -925 780 -865 780 {}
N -825 780 -795 780 {}
N -695 780 -635 780 {}
N -595 780 -565 780 {}
N -325 780 -265 780 {}
N -225 780 -165 780 {}
N 95 780 155 780 {}
N 195 780 225 780 {}
N 330 780 390 780 {}
N 430 780 460 780 {}
N 565 780 625 780 {}
N 665 780 695 780 {}
N 800 780 860 780 {}
N 900 780 960 780 {}
N 1105 780 1165 780 {}
N 1205 780 1265 780 {}
N 1575 780 1635 780 {}
N 1850 780 1910 780 {}
N 2130 780 2190 780 {}
N 2230 780 2260 780 {}
N 2405 780 2465 780 {}
N 2505 780 2535 780 {}
N 2665 780 2725 780 {}
N 2765 780 2795 780 {}
N 2925 780 2985 780 {}
N 3025 780 3055 780 {}
N 3200 780 3260 780 {}
N 3300 780 3330 780 {}
N 3635 780 3695 780 {}
N 3735 780 3765 780 {}
N 3865 780 3925 780 {}
N 3965 780 3995 780 {}
N 4090 780 4150 780 {}
N 4190 780 4220 780 {}
N 4320 780 4380 780 {}
N 4420 780 4480 780 {}
N 855 880 915 880 {}
N 5 980 240 980 {}
N -325 1040 -265 1040 {}
N -225 1040 -195 1040 {}
N -55 1040 5 1040 {}
N 45 1040 75 1040 {}
N 180 1040 240 1040 {}
N 280 1040 340 1040 {}
N 1105 1040 1165 1040 {}
N 1205 1040 1265 1040 {}
N 1575 1040 1635 1040 {}
N 1675 1040 1705 1040 {}
N 1850 1040 1910 1040 {}
N 1950 1040 2010 1040 {}
N 465 1100 1175 1100 {}
N -2820 1180 6855 1180 {}
C {devices/lab_wire.sym} -2820 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -2820 1180 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -1830 840 2 0 {name=l2 lab=clk_chfb}
C {devices/lab_wire.sym} -1605 840 2 0 {name=l3 lab=clk_chfb}
C {devices/lab_wire.sym} 2765 840 2 0 {name=l4 lab=clk_chfb}
C {devices/lab_wire.sym} 3025 840 2 0 {name=l5 lab=clk_chfb}
C {devices/lab_wire.sym} -825 840 2 0 {name=l6 lab=clk_chfb_not}
C {devices/lab_wire.sym} -595 840 2 0 {name=l7 lab=clk_chfb_not}
C {devices/lab_wire.sym} 3965 840 2 0 {name=l8 lab=clk_chfb_not}
C {devices/lab_wire.sym} 4190 840 2 0 {name=l9 lab=clk_chfb_not}
C {devices/lab_wire.sym} -1605 580 2 0 {name=l10 lab=clk_chin}
C {devices/lab_wire.sym} -1330 580 2 0 {name=l11 lab=clk_chin}
C {devices/lab_wire.sym} 4420 580 2 0 {name=l12 lab=clk_chin}
C {devices/lab_wire.sym} 4650 580 2 0 {name=l13 lab=clk_chin}
C {devices/lab_wire.sym} -2060 580 2 0 {name=l14 lab=clk_chin_not}
C {devices/lab_wire.sym} -1830 580 2 0 {name=l15 lab=clk_chin_not}
C {devices/lab_wire.sym} 3965 580 2 0 {name=l16 lab=clk_chin_not}
C {devices/lab_wire.sym} 4190 580 2 0 {name=l17 lab=clk_chin_not}
C {devices/lab_wire.sym} -1330 840 2 0 {name=l18 lab=clk_chout}
C {devices/lab_wire.sym} -445 580 2 0 {name=l19 lab=clk_chout}
C {devices/lab_wire.sym} 900 460 0 1 {name=l20 lab=clk_chout}
C {devices/lab_wire.sym} 1675 840 2 0 {name=l21 lab=clk_chout}
C {devices/lab_wire.sym} 1950 840 2 0 {name=l22 lab=clk_chout}
C {devices/lab_wire.sym} 3735 840 2 0 {name=l23 lab=clk_chout}
C {devices/lab_wire.sym} 5900 520 0 0 {name=l24 lab=clk_chout}
C {devices/lab_wire.sym} 6580 520 0 0 {name=l25 lab=clk_chout}
C {devices/lab_wire.sym} -1050 840 2 0 {name=l26 lab=clk_chout_not}
C {devices/lab_wire.sym} -185 580 2 0 {name=l27 lab=clk_chout_not}
C {devices/lab_wire.sym} 430 460 0 1 {name=l28 lab=clk_chout_not}
C {devices/lab_wire.sym} 2230 840 2 0 {name=l29 lab=clk_chout_not}
C {devices/lab_wire.sym} 2505 840 2 0 {name=l30 lab=clk_chout_not}
C {devices/lab_wire.sym} 3300 840 2 0 {name=l31 lab=clk_chout_not}
C {devices/lab_wire.sym} 6125 520 0 0 {name=l32 lab=clk_chout_not}
C {devices/lab_wire.sym} 6355 520 0 0 {name=l33 lab=clk_chout_not}
C {devices/lab_wire.sym} -675 580 2 0 {name=l34 lab=clk_phi_1}
C {devices/lab_wire.sym} 45 1100 2 0 {name=l35 lab=clk_phi_1}
C {devices/lab_wire.sym} 665 840 2 0 {name=l36 lab=clk_phi_1}
C {devices/lab_wire.sym} 960 780 0 1 {name=l37 lab=clk_phi_1}
C {devices/lab_wire.sym} 2010 1040 0 1 {name=l38 lab=clk_phi_1}
C {devices/lab_wire.sym} 2180 520 0 1 {name=l39 lab=clk_phi_1}
C {devices/lab_wire.sym} 195 840 2 0 {name=l40 lab=clk_phi_2}
C {devices/lab_wire.sym} 340 1040 0 1 {name=l41 lab=clk_phi_2}
C {devices/lab_wire.sym} 430 840 2 0 {name=l42 lab=clk_phi_2}
C {devices/lab_wire.sym} 1140 460 0 1 {name=l43 lab=clk_phi_2}
C {devices/lab_wire.sym} 1435 520 0 1 {name=l44 lab=clk_phi_2}
C {devices/lab_wire.sym} 1675 1100 2 0 {name=l45 lab=clk_phi_2}
C {devices/lab_wire.sym} 625 90 2 0 {name=l46 lab=main__casc_src_n}
C {devices/lab_wire.sym} 625 170 0 1 {name=l47 lab=main__casc_src_n}
C {devices/lab_wire.sym} 2280 90 2 0 {name=l48 lab=main__casc_src_p}
C {devices/lab_wire.sym} 2280 170 0 1 {name=l49 lab=main__casc_src_p}
C {devices/lab_wire.sym} -1870 690 0 1 {name=l50 lab=main__fbch_n}
C {devices/lab_wire.sym} -865 690 0 1 {name=l51 lab=main__fbch_n}
C {devices/lab_wire.sym} 1435 560 0 1 {name=l52 lab=main__fbch_n}
C {devices/lab_wire.sym} 2985 690 0 1 {name=l53 lab=main__fbch_n}
C {devices/lab_wire.sym} 4150 690 0 1 {name=l54 lab=main__fbch_n}
C {devices/lab_wire.sym} -1645 690 0 1 {name=l55 lab=main__fbch_p}
C {devices/lab_wire.sym} -635 690 0 1 {name=l56 lab=main__fbch_p}
C {devices/lab_wire.sym} 655 560 0 1 {name=l57 lab=main__fbch_p}
C {devices/lab_wire.sym} 2725 690 0 1 {name=l58 lab=main__fbch_p}
C {devices/lab_wire.sym} 3925 690 0 1 {name=l59 lab=main__fbch_p}
C {devices/lab_wire.sym} -2100 690 0 1 {name=l60 lab=main__fold_n}
C {devices/lab_wire.sym} -155 350 2 0 {name=l61 lab=main__fold_n}
C {devices/lab_wire.sym} 625 610 2 0 {name=l62 lab=main__fold_n}
C {devices/lab_wire.sym} 1415 350 2 0 {name=l63 lab=main__fold_p}
C {devices/lab_wire.sym} 4380 690 0 1 {name=l64 lab=main__fold_p}
C {devices/lab_wire.sym} 5710 610 2 0 {name=l65 lab=main__fold_p}
C {devices/lab_wire.sym} 390 610 2 0 {name=l66 lab=main__g2_n}
C {devices/lab_wire.sym} 860 610 2 0 {name=l67 lab=main__g2_n}
C {devices/lab_wire.sym} 1195 320 2 0 {name=l68 lab=main__g2_n}
C {devices/lab_wire.sym} 5060 430 0 1 {name=l69 lab=main__g2_n}
C {devices/lab_wire.sym} 6395 610 2 0 {name=l70 lab=main__g2_n}
C {devices/lab_wire.sym} -485 610 2 0 {name=l71 lab=main__g2_p}
C {devices/lab_wire.sym} -225 610 2 0 {name=l72 lab=main__g2_p}
C {devices/lab_wire.sym} 935 320 2 0 {name=l73 lab=main__g2_p}
C {devices/lab_wire.sym} 4810 430 0 1 {name=l74 lab=main__g2_p}
C {devices/lab_wire.sym} 5940 610 2 0 {name=l75 lab=main__g2_p}
C {devices/lab_wire.sym} 6165 610 2 0 {name=l76 lab=main__g2_p}
C {devices/lab_wire.sym} -2100 610 2 0 {name=l77 lab=main__inch_n}
C {devices/lab_wire.sym} -1370 610 2 0 {name=l78 lab=main__inch_n}
C {devices/lab_wire.sym} 2485 610 2 0 {name=l79 lab=main__inch_n}
C {devices/lab_wire.sym} 3925 610 2 0 {name=l80 lab=main__inch_n}
C {devices/lab_wire.sym} 4610 610 2 0 {name=l81 lab=main__inch_n}
C {devices/lab_wire.sym} -1870 610 2 0 {name=l82 lab=main__inch_p}
C {devices/lab_wire.sym} -1645 610 2 0 {name=l83 lab=main__inch_p}
C {devices/lab_wire.sym} 2745 610 2 0 {name=l84 lab=main__inch_p}
C {devices/lab_wire.sym} 4150 610 2 0 {name=l85 lab=main__inch_p}
C {devices/lab_wire.sym} 4380 610 2 0 {name=l86 lab=main__inch_p}
C {devices/lab_wire.sym} -155 170 0 1 {name=l87 lab=main__tail}
C {devices/lab_wire.sym} 895 90 2 0 {name=l88 lab=main__tail}
C {devices/lab_wire.sym} 1415 170 0 1 {name=l89 lab=main__tail}
C {devices/lab_wire.sym} -2060 840 2 0 {name=l90 lab=main__vb1}
C {devices/lab_wire.sym} 4480 780 0 1 {name=l91 lab=main__vb1}
C {devices/lab_wire.sym} 665 460 0 1 {name=l92 lab=main__vb2}
C {devices/lab_wire.sym} 5670 460 0 1 {name=l93 lab=main__vb2}
C {devices/lab_wire.sym} 665 320 2 0 {name=l94 lab=main__vb3}
C {devices/lab_wire.sym} 2180 260 0 0 {name=l95 lab=main__vb3}
C {devices/lab_wire.sym} 340 0 0 1 {name=l96 lab=main__vb4}
C {devices/lab_wire.sym} 665 60 2 0 {name=l97 lab=main__vb4}
C {devices/lab_wire.sym} 935 60 2 0 {name=l98 lab=main__vb4}
C {devices/lab_wire.sym} 1735 0 0 1 {name=l99 lab=main__vb4}
C {devices/lab_wire.sym} -115 320 2 0 {name=l100 lab=main__vsum_n}
C {devices/lab_wire.sym} 655 740 2 0 {name=l101 lab=main__vsum_n}
C {devices/lab_wire.sym} 2485 430 0 1 {name=l102 lab=main__vsum_n}
C {devices/lab_wire.sym} 3005 430 0 1 {name=l103 lab=main__vsum_n}
C {devices/lab_wire.sym} 1435 740 2 0 {name=l104 lab=main__vsum_p}
C {devices/lab_wire.sym} 1515 260 0 1 {name=l105 lab=main__vsum_p}
C {devices/lab_wire.sym} 2745 430 0 1 {name=l106 lab=main__vsum_p}
C {devices/lab_wire.sym} 3280 430 0 1 {name=l107 lab=main__vsum_p}
C {devices/lab_wire.sym} -485 430 0 1 {name=l108 lab=out1_n}
C {devices/lab_wire.sym} -225 430 0 1 {name=l109 lab=out1_n}
C {devices/lab_wire.sym} 390 430 0 1 {name=l110 lab=out1_n}
C {devices/lab_wire.sym} 625 350 2 0 {name=l111 lab=out1_n}
C {devices/lab_wire.sym} 625 430 0 1 {name=l112 lab=out1_n}
C {devices/lab_wire.sym} 860 430 0 1 {name=l113 lab=out1_n}
C {devices/lab_wire.sym} 5220 520 0 0 {name=l114 lab=out1_n}
C {devices/lab_wire.sym} 5410 520 0 0 {name=l115 lab=out1_n}
C {devices/lab_wire.sym} 2280 350 2 0 {name=l116 lab=out1_p}
C {devices/lab_wire.sym} 5340 580 2 0 {name=l117 lab=out1_p}
C {devices/lab_wire.sym} 5530 580 2 0 {name=l118 lab=out1_p}
C {devices/lab_wire.sym} 5710 430 0 1 {name=l119 lab=out1_p}
C {devices/lab_wire.sym} 155 870 2 0 {name=l120 lab=rrl__int_n}
C {devices/lab_wire.sym} 1175 1000 2 0 {name=l121 lab=rrl__int_n}
C {devices/lab_wire.sym} 860 870 2 0 {name=l122 lab=rrl__int_n}
C {devices/lab_wire.sym} 390 870 2 0 {name=l123 lab=rrl__int_p}
C {devices/lab_wire.sym} 465 950 0 1 {name=l124 lab=rrl__int_p}
C {devices/lab_wire.sym} 625 870 2 0 {name=l125 lab=rrl__int_p}
C {devices/lab_wire.sym} 700 950 0 1 {name=l126 lab=rrl__int_p}
C {devices/lab_wire.sym} 915 1000 2 0 {name=l127 lab=rrl__int_p}
C {devices/lab_wire.sym} -1090 430 0 1 {name=l128 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} -225 1100 2 0 {name=l129 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 1105 1040 0 0 {name=l130 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 2725 350 2 0 {name=l131 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 2985 350 2 0 {name=l132 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} -635 350 2 0 {name=l133 lab=rrl__oa_cm_sense}
C {devices/lab_wire.sym} 3695 430 0 1 {name=l134 lab=rrl__oa_cm_sense}
C {devices/lab_wire.sym} -635 170 0 1 {name=l135 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} 1415 90 2 0 {name=l136 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} 2725 170 0 1 {name=l137 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} 2985 170 0 1 {name=l138 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} -265 870 2 0 {name=l139 lab=rrl__oa_csrc_n}
C {devices/lab_wire.sym} -265 950 0 1 {name=l140 lab=rrl__oa_csrc_n}
C {devices/lab_wire.sym} 1205 870 2 0 {name=l141 lab=rrl__oa_csrc_p}
C {devices/lab_wire.sym} 1205 950 0 1 {name=l142 lab=rrl__oa_csrc_p}
C {devices/lab_wire.sym} 1705 350 2 0 {name=l143 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 1705 430 0 1 {name=l144 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 135 350 2 0 {name=l145 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} 135 430 0 1 {name=l146 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} -715 430 0 1 {name=l147 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 235 260 0 1 {name=l148 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 1175 740 2 0 {name=l149 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 1335 430 0 1 {name=l150 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 915 740 2 0 {name=l151 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 1100 430 0 1 {name=l152 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 1605 260 0 0 {name=l153 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 2080 430 0 1 {name=l154 lab=rrl__oa_inp}
C {devices/lab_wire.sym} -335 320 2 0 {name=l155 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -265 690 0 1 {name=l156 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 390 690 0 1 {name=l157 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 625 690 0 1 {name=l158 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 1100 610 2 0 {name=l159 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 1705 550 0 0 {name=l160 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 2080 610 2 0 {name=l161 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -715 610 2 0 {name=l162 lab=rrl__oa_outp}
C {devices/lab_wire.sym} -595 260 0 0 {name=l163 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 135 610 2 0 {name=l164 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 155 690 0 1 {name=l165 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 860 690 0 1 {name=l166 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1205 690 0 1 {name=l167 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1335 610 2 0 {name=l168 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 135 170 0 1 {name=l169 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 1155 90 2 0 {name=l170 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 1705 170 0 1 {name=l171 lab=rrl__oa_tail}
C {devices/lab_wire.sym} -1090 870 2 0 {name=l172 lab=rrl__sc_n}
C {devices/lab_wire.sym} 250 680 0 0 {name=l173 lab=rrl__sc_n}
C {devices/lab_wire.sym} 1635 950 0 1 {name=l174 lab=rrl__sc_n}
C {devices/lab_wire.sym} 1910 870 2 0 {name=l175 lab=rrl__sc_n}
C {devices/lab_wire.sym} 1910 950 0 1 {name=l176 lab=rrl__sc_n}
C {devices/lab_wire.sym} 2190 870 2 0 {name=l177 lab=rrl__sc_n}
C {devices/lab_wire.sym} 3695 870 2 0 {name=l178 lab=rrl__sc_n}
C {devices/lab_wire.sym} -1370 870 2 0 {name=l179 lab=rrl__sc_p}
C {devices/lab_wire.sym} 5 950 0 1 {name=l180 lab=rrl__sc_p}
C {devices/lab_wire.sym} 1635 870 2 0 {name=l181 lab=rrl__sc_p}
C {devices/lab_wire.sym} 1705 740 2 0 {name=l182 lab=rrl__sc_p}
C {devices/lab_wire.sym} 2465 870 2 0 {name=l183 lab=rrl__sc_p}
C {devices/lab_wire.sym} 3260 870 2 0 {name=l184 lab=rrl__sc_p}
C {devices/lab_wire.sym} -1370 690 0 1 {name=l185 lab=rrl__sum_n}
C {devices/lab_wire.sym} -1090 690 0 1 {name=l186 lab=rrl__sum_n}
C {devices/lab_wire.sym} 1175 560 0 1 {name=l187 lab=rrl__sum_n}
C {devices/lab_wire.sym} 1175 820 0 1 {name=l188 lab=rrl__sum_n}
C {devices/lab_wire.sym} 1910 690 0 1 {name=l189 lab=rrl__sum_n}
C {devices/lab_wire.sym} 2465 690 0 1 {name=l190 lab=rrl__sum_n}
C {devices/lab_wire.sym} 915 560 0 1 {name=l191 lab=rrl__sum_p}
C {devices/lab_wire.sym} 855 880 0 0 {name=l192 lab=rrl__sum_p}
C {devices/lab_wire.sym} 1635 690 0 1 {name=l193 lab=rrl__sum_p}
C {devices/lab_wire.sym} 2190 690 0 1 {name=l194 lab=rrl__sum_p}
C {devices/lab_wire.sym} 3260 690 0 1 {name=l195 lab=rrl__sum_p}
C {devices/lab_wire.sym} 3695 690 0 1 {name=l196 lab=rrl__sum_p}
C {devices/lab_wire.sym} 175 580 2 0 {name=l197 lab=rrl__vb1}
C {devices/lab_wire.sym} 1605 520 0 0 {name=l198 lab=rrl__vb1}
C {devices/lab_wire.sym} -165 780 0 1 {name=l199 lab=rrl__vb2}
C {devices/lab_wire.sym} 1105 780 0 0 {name=l200 lab=rrl__vb2}
C {devices/lab_wire.sym} 1195 60 2 0 {name=l201 lab=rrl__vb3}
C {devices/lab_wire.sym} 1455 60 2 0 {name=l202 lab=rrl__vb3}
C {devices/lab_wire.sym} 2765 320 2 0 {name=l203 lab=rrl__vb4}
C {devices/lab_wire.sym} 3085 260 0 1 {name=l204 lab=rrl__vb4}
C {devices/lab_wire.sym} -1870 430 0 1 {name=l205 lab=vinn}
C {devices/lab_wire.sym} -1370 430 0 1 {name=l206 lab=vinn}
C {devices/lab_wire.sym} 3925 430 0 1 {name=l207 lab=vinn}
C {devices/lab_wire.sym} 4380 430 0 1 {name=l208 lab=vinn}
C {devices/lab_wire.sym} -2100 430 0 1 {name=l209 lab=vinp}
C {devices/lab_wire.sym} -1645 430 0 1 {name=l210 lab=vinp}
C {devices/lab_wire.sym} 4150 430 0 1 {name=l211 lab=vinp}
C {devices/lab_wire.sym} 4610 430 0 1 {name=l212 lab=vinp}
C {devices/lab_wire.sym} -1645 870 2 0 {name=l213 lab=voutn}
C {devices/lab_wire.sym} -865 870 2 0 {name=l214 lab=voutn}
C {devices/lab_wire.sym} 240 90 2 0 {name=l215 lab=voutn}
C {devices/lab_wire.sym} 1155 170 0 1 {name=l216 lab=voutn}
C {devices/lab_wire.sym} 2985 870 2 0 {name=l217 lab=voutn}
C {devices/lab_wire.sym} 3925 870 2 0 {name=l218 lab=voutn}
C {devices/lab_wire.sym} 5060 610 2 0 {name=l219 lab=voutn}
C {devices/lab_wire.sym} -1870 870 2 0 {name=l220 lab=voutp}
C {devices/lab_wire.sym} -635 870 2 0 {name=l221 lab=voutp}
C {devices/lab_wire.sym} 895 170 0 1 {name=l222 lab=voutp}
C {devices/lab_wire.sym} 1635 90 2 0 {name=l223 lab=voutp}
C {devices/lab_wire.sym} 1705 620 0 0 {name=l224 lab=voutp}
C {devices/lab_wire.sym} 2725 870 2 0 {name=l225 lab=voutp}
C {devices/lab_wire.sym} 4150 870 2 0 {name=l226 lab=voutp}
C {devices/lab_wire.sym} 4810 610 2 0 {name=l227 lab=voutp}
C {devices/lab_wire.sym} 3005 610 2 0 {name=l228 lab=vref}
C {devices/lab_wire.sym} 3280 610 2 0 {name=l229 lab=vref}
C {devices/lab_wire.sym} 565 354 2 0 {name=l230 lab=vdd}
C {devices/lab_wire.sym} 75 614 2 0 {name=l231 lab=vdd}
C {devices/lab_wire.sym} 2340 354 2 0 {name=l232 lab=vdd}
C {devices/lab_wire.sym} 330 614 2 0 {name=l233 lab=vdd}
C {devices/lab_wire.sym} 6225 614 2 0 {name=l234 lab=vdd}
C {devices/lab_wire.sym} 835 94 2 0 {name=l235 lab=vdd}
C {devices/lab_wire.sym} 1095 94 2 0 {name=l236 lab=vdd}
C {devices/lab_wire.sym} -695 874 2 0 {name=l237 lab=vdd}
C {devices/lab_wire.sym} -925 874 2 0 {name=l238 lab=vdd}
C {devices/lab_wire.sym} 3865 614 2 0 {name=l239 lab=vdd}
C {devices/lab_wire.sym} 4090 614 2 0 {name=l240 lab=vdd}
C {devices/lab_wire.sym} -545 614 2 0 {name=l241 lab=vdd}
C {devices/lab_wire.sym} 3200 874 2 0 {name=l242 lab=vdd}
C {devices/lab_wire.sym} -1150 874 2 0 {name=l243 lab=vdd}
C {devices/lab_wire.sym} 3635 874 2 0 {name=l244 lab=vdd}
C {devices/lab_wire.sym} -1430 874 2 0 {name=l245 lab=vdd}
C {devices/lab_wire.sym} 1355 354 2 0 {name=l246 lab=vdd}
C {devices/lab_wire.sym} 1765 354 2 0 {name=l247 lab=vdd}
C {devices/lab_wire.sym} 1850 1134 2 0 {name=l248 lab=vdd}
C {devices/lab_wire.sym} -55 1134 2 0 {name=l249 lab=vdd}
C {devices/lab_wire.sym} 2020 614 2 0 {name=l250 lab=vdd}
C {devices/lab_wire.sym} -775 614 2 0 {name=l251 lab=vdd}
C {devices/lab_wire.sym} 330 874 2 0 {name=l252 lab=vdd}
C {devices/lab_wire.sym} 95 874 2 0 {name=l253 lab=vdd}
C {devices/lab_wire.sym} 6680 614 2 0 {name=l254 lab=vdd}
C {devices/lab_wire.sym} 4320 614 2 0 {name=l255 lab=vdd}
C {devices/lab_wire.sym} 4550 614 2 0 {name=l256 lab=vdd}
C {devices/lab_wire.sym} -1705 874 2 0 {name=l257 lab=vdd}
C {devices/lab_wire.sym} -1930 874 2 0 {name=l258 lab=vdd}
C {devices/lab_wire.sym} -215 354 2 0 {name=l259 lab=vdd}
C {devices/lab_wire.sym} 75 354 2 0 {name=l260 lab=vdd}
C {devices/lab_wire.sym} 1355 94 2 0 {name=l261 lab=vdd}
C {devices/lab_wire.sym} -435 354 2 0 {name=l262 lab=vdd}
C {devices/lab_wire.sym} 565 94 2 0 {name=l263 lab=vdd}
C {devices/lab_wire.sym} 2665 354 2 0 {name=l264 lab=vdd}
C {devices/lab_wire.sym} 2340 94 2 0 {name=l265 lab=vdd}
C {devices/lab_wire.sym} -695 354 2 0 {name=l266 lab=vdd}
C {devices/lab_wire.sym} 1575 94 2 0 {name=l267 lab=vdd}
C {devices/lab_wire.sym} 2925 354 2 0 {name=l268 lab=vdd}
C {devices/lab_wire.sym} 180 94 2 0 {name=l269 lab=vdd}
C {devices/lab_wire.sym} 1765 614 2 0 {name=l270 lab=vdd}
C {devices/lab_wire.sym} -325 874 2 0 {name=l271 lab=vss}
C {devices/lab_wire.sym} 5770 614 2 0 {name=l272 lab=vss}
C {devices/lab_wire.sym} 1265 874 2 0 {name=l273 lab=vss}
C {devices/lab_wire.sym} 565 614 2 0 {name=l274 lab=vss}
C {devices/lab_wire.sym} -325 1134 2 0 {name=l275 lab=vss}
C {devices/lab_wire.sym} 835 354 2 0 {name=l276 lab=vss}
C {devices/lab_wire.sym} 1265 1134 2 0 {name=l277 lab=vss}
C {devices/lab_wire.sym} 1095 354 2 0 {name=l278 lab=vss}
C {devices/lab_wire.sym} -1150 614 2 0 {name=l279 lab=vss}
C {devices/lab_wire.sym} 800 614 2 0 {name=l280 lab=vss}
C {devices/lab_wire.sym} 3635 614 2 0 {name=l281 lab=vss}
C {devices/lab_wire.sym} 6000 614 2 0 {name=l282 lab=vss}
C {devices/lab_wire.sym} 1575 874 2 0 {name=l283 lab=vss}
C {devices/lab_wire.sym} 1850 874 2 0 {name=l284 lab=vss}
C {devices/lab_wire.sym} 2130 874 2 0 {name=l285 lab=vss}
C {devices/lab_wire.sym} 2405 874 2 0 {name=l286 lab=vss}
C {devices/lab_wire.sym} 1575 1134 2 0 {name=l287 lab=vss}
C {devices/lab_wire.sym} 180 1134 2 0 {name=l288 lab=vss}
C {devices/lab_wire.sym} 1040 614 2 0 {name=l289 lab=vss}
C {devices/lab_wire.sym} 1275 614 2 0 {name=l290 lab=vss}
C {devices/lab_wire.sym} 565 874 2 0 {name=l291 lab=vss}
C {devices/lab_wire.sym} 800 874 2 0 {name=l292 lab=vss}
C {devices/lab_wire.sym} 2665 874 2 0 {name=l293 lab=vss}
C {devices/lab_wire.sym} 2925 874 2 0 {name=l294 lab=vss}
C {devices/lab_wire.sym} -1430 614 2 0 {name=l295 lab=vss}
C {devices/lab_wire.sym} -1705 614 2 0 {name=l296 lab=vss}
C {devices/lab_wire.sym} -285 614 2 0 {name=l297 lab=vss}
C {devices/lab_wire.sym} 6455 614 2 0 {name=l298 lab=vss}
C {devices/lab_wire.sym} -1930 614 2 0 {name=l299 lab=vss}
C {devices/lab_wire.sym} -2160 614 2 0 {name=l300 lab=vss}
C {devices/lab_wire.sym} 3865 874 2 0 {name=l301 lab=vss}
C {devices/lab_wire.sym} 4090 874 2 0 {name=l302 lab=vss}
C {devices/lab_wire.sym} 4320 874 2 0 {name=l303 lab=vss}
C {devices/lab_wire.sym} -2160 874 2 0 {name=l304 lab=vss}
C {devices/lab_wire.sym} -2420 950 0 1 {name=l305 lab=main__vb1}
C {devices/lab_wire.sym} -2420 1130 2 0 {name=l306 lab=vss}
C {devices/lab_wire.sym} -2420 870 2 0 {name=l307 lab=vss}
C {devices/lab_wire.sym} -2420 610 2 0 {name=l308 lab=vss}
C {devices/lab_wire.sym} -2420 350 2 0 {name=l309 lab=vss}
C {devices/lab_wire.sym} -2420 90 2 0 {name=l310 lab=vss}
C {devices/lab_wire.sym} -2760 1130 2 0 {name=l311 lab=vss}
C {devices/lab_wire.sym} -2760 870 2 0 {name=l312 lab=vss}
C {devices/lab_wire.sym} -2760 610 2 0 {name=l313 lab=vss}
C {devices/lab_wire.sym} -2420 690 0 1 {name=l314 lab=rrl__vb1}
C {devices/lab_wire.sym} -2420 430 0 1 {name=l315 lab=main__vb2}
C {devices/lab_wire.sym} -2420 170 0 1 {name=l316 lab=rrl__vb2}
C {devices/lab_wire.sym} -2420 -90 0 1 {name=l317 lab=main__vb3}
C {devices/lab_wire.sym} -2760 950 0 1 {name=l318 lab=rrl__vb3}
C {devices/lab_wire.sym} -2760 690 0 1 {name=l319 lab=main__vb4}
C {devices/lab_wire.sym} -2760 430 0 1 {name=l320 lab=rrl__vb4}
C {devices/lab_wire.sym} 895 350 2 0 {name=l321 lab=vss}
C {devices/lab_wire.sym} 1155 350 2 0 {name=l322 lab=vss}
C {devices/lab_wire.sym} -1090 610 2 0 {name=l323 lab=vss}
C {devices/lab_wire.sym} 3695 610 2 0 {name=l324 lab=vss}
C {devices/ipin.sym} -2960 520 0 0 {name=p0 lab=clk_chin_not}
C {devices/ipin.sym} -2960 640 0 0 {name=p1 lab=clk_chin}
C {devices/ipin.sym} -2960 760 0 0 {name=p2 lab=clk_phi_1}
C {devices/ipin.sym} -2960 880 0 0 {name=p3 lab=clk_chout}
C {devices/ipin.sym} -2960 1000 0 0 {name=p4 lab=clk_chout_not}
C {devices/ipin.sym} -2960 1120 0 0 {name=p5 lab=clk_phi_2}
C {devices/ipin.sym} -2960 1240 0 0 {name=p6 lab=clk_chfb}
C {devices/ipin.sym} -2960 1360 0 0 {name=p7 lab=clk_chfb_not}
C {devices/iopin.sym} 3005 1320 0 0 {name=p8 lab=vref}
C {devices/opin.sym} 6995 30 0 0 {name=p9 lab=voutn}
C {devices/opin.sym} 6995 150 0 0 {name=p10 lab=voutp}
C {devices/opin.sym} 6995 490 0 0 {name=p11 lab=vinp}
C {devices/opin.sym} 6995 610 0 0 {name=p12 lab=vinn}
