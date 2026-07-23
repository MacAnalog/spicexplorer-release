v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_004_fan_chopper_rrl} -3110 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1180 650 0 0 {name=CAZ1_RRL value='x_dut_caz1_rrl_value'}
C {devices/capa_np.sym} 1440 650 0 0 {name=CAZ2_RRL value='x_dut_caz2_rrl_value'}
C {devices/capa_np.sym} 920 650 0 0 {name=CFB1_MAIN value='x_dut_cfb1_main_value'}
C {devices/capa_np.sym} 1695 650 0 0 {name=CFB2_MAIN value='x_dut_cfb2_main_value'}
C {devices/capa_np.sym} 2910 520 0 0 {name=CIN1_MAIN value='x_dut_cin1_main_value'}
C {devices/capa_np.sym} -560 520 0 0 {name=CIN2_MAIN value='x_dut_cin2_main_value'}
C {devices/capa_np.sym} 1180 910 0 0 {name=CINT1_RRL value='x_dut_cint1_rrl_value'}
C {devices/capa_np.sym} 1440 910 0 0 {name=CINT2_RRL value='x_dut_cint2_rrl_value'}
C {devices/capa_np.sym} 1180 1040 0 0 {name=CIN_1_RRL value='cin_val_rrl'}
C {devices/capa_np.sym} 4970 520 0 0 {name=CM1_MAIN value='x_dut_cm1_main_value'}
C {devices/capa_np.sym} 5225 520 0 0 {name=CM2_MAIN value='x_dut_cm2_main_value'}
C {devices/capa_np.sym} 5475 520 1 0 {name=COUT_1_RRL value='cout_val_rrl'}
C {devices/capa_np.sym} 1955 650 0 0 {name=CS1_RRL value='x_dut_cs1_rrl_value'}
C {devices/capa_np.sym} 385 650 0 0 {name=CS2_RRL value='x_dut_cs2_rrl_value'}
C {devices/res_np.sym} 3170 520 0 0 {name=RB1_MAIN value='x_dut_rb1_main_value'}
C {devices/res_np.sym} -815 520 0 0 {name=RB2_MAIN value='x_dut_rb2_main_value'}
C {devices/res_np.sym} 920 1040 0 0 {name=RIN_1_RRL value='rin_val_rrl'}
C {devices/res_np.sym} -2390 520 1 0 {name=ROUT_1_RRL value='rout_val_rrl'}
C {devices/vsource_np.sym} -2730 1040 0 0 {name=VB1_MAIN value="dc {vb1_main}"}
C {devices/vsource_np.sym} -2730 780 0 0 {name=VB1_RRL value="dc {vb1_rrl}"}
C {devices/vsource_np.sym} -2730 520 0 0 {name=VB2_MAIN value="dc {vb2_main}"}
C {devices/vsource_np.sym} -2730 260 0 0 {name=VB2_RRL value="dc {vb2_rrl}"}
C {devices/vsource_np.sym} -2730 0 0 0 {name=VB3_MAIN value="dc {vb3_main}"}
C {devices/vsource_np.sym} -3070 1040 0 0 {name=VB3_RRL value="dc {vb3_rrl}"}
C {devices/vsource_np.sym} -3070 780 0 0 {name=VB4_MAIN value="dc {vb4_main}"}
C {devices/vsource_np.sym} -3070 520 0 0 {name=VB4_RRL value="dc {vb4_rrl}"}
C {devices/sg13_lv_pmos_np.sym} 910 260 0 1 {name=M10_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_main_w l=x_dut_xm10_main_l m=x_dut_xm10_main_m}
C {devices/sg13_lv_pmos_np.sym} 215 520 0 1 {name=M10_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_rrl_w l=x_dut_xm10_opamp_rrl_l m=x_dut_xm10_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1960 260 0 0 {name=M11_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_main_w l=x_dut_xm11_main_l m=x_dut_xm11_main_m}
C {devices/sg13_lv_nmos_np.sym} -190 780 0 1 {name=M11_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_opamp_rrl_w l=x_dut_xm11_opamp_rrl_l m=x_dut_xm11_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 5665 520 0 0 {name=M12_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_main_w l=x_dut_xm12_main_l m=x_dut_xm12_main_m}
C {devices/sg13_lv_nmos_np.sym} 1450 780 0 0 {name=M12_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_opamp_rrl_w l=x_dut_xm12_opamp_rrl_l m=x_dut_xm12_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 910 520 0 1 {name=M13_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_main_w l=x_dut_xm13_main_l m=x_dut_xm13_main_m}
C {devices/sg13_lv_nmos_np.sym} -190 1040 0 1 {name=M13_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_opamp_rrl_w l=x_dut_xm13_opamp_rrl_l m=x_dut_xm13_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1180 260 0 1 {name=M14_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_main_w l=x_dut_xm14_main_l m=x_dut_xm14_main_m}
C {devices/sg13_lv_nmos_np.sym} 1450 1040 0 0 {name=M14_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_opamp_rrl_w l=x_dut_xm14_opamp_rrl_l m=x_dut_xm14_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1440 260 0 1 {name=M15_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_main_w l=x_dut_xm15_main_l m=x_dut_xm15_main_m}
C {devices/sg13_lv_nmos_np.sym} 500 520 0 0 {name=M15_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_opamp_rrl_w l=x_dut_xm15_opamp_rrl_l m=x_dut_xm15_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1150 520 0 1 {name=M16_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_main_w l=x_dut_xm16_main_l m=x_dut_xm16_main_m}
C {devices/sg13_lv_nmos_np.sym} 3605 520 0 1 {name=M16_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_opamp_rrl_w l=x_dut_xm16_opamp_rrl_l m=x_dut_xm16_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1375 520 0 1 {name=M17_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_main_w l=x_dut_xm17_main_l m=x_dut_xm17_main_m}
C {devices/sg13_lv_nmos_np.sym} 5890 520 0 0 {name=M18_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_main_w l=x_dut_xm18_main_l m=x_dut_xm18_main_m}
C {devices/sg13_lv_pmos_np.sym} 6120 520 0 0 {name=M19_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_main_w l=x_dut_xm19_main_l m=x_dut_xm19_main_m}
C {devices/sg13_lv_nmos_np.sym} 1910 780 0 1 {name=M1_CHRRL_1_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_1_rrl_w l=x_dut_xm1_chrrl_1_rrl_l m=x_dut_xm1_chrrl_1_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 360 780 0 1 {name=M1_CHRRL_2_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_2_rrl_w l=x_dut_xm1_chrrl_2_rrl_l m=x_dut_xm1_chrrl_2_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2190 780 0 1 {name=M1_CHRRL_3_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_3_rrl_w l=x_dut_xm1_chrrl_3_rrl_l m=x_dut_xm1_chrrl_3_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 85 780 0 1 {name=M1_CHRRL_4_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_4_rrl_w l=x_dut_xm1_chrrl_4_rrl_l m=x_dut_xm1_chrrl_4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1180 0 0 1 {name=M1_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_main_w l=x_dut_xm1_main_l m=x_dut_xm1_main_m}
C {devices/sg13_lv_pmos_np.sym} 2435 0 0 0 {name=M1_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_opamp_rrl_w l=x_dut_xm1_opamp_rrl_l m=x_dut_xm1_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 595 1040 0 1 {name=M1_S1_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s1_rrl_w l=x_dut_xm1_s1_rrl_l m=x_dut_xm1_s1_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1910 1040 0 1 {name=M1_S2_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s2_rrl_w l=x_dut_xm1_s2_rrl_l m=x_dut_xm1_s2_rrl_m}
C {devices/sg13_lv_nmos_np.sym} -1090 520 0 1 {name=M1_S3_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s3_rrl_w l=x_dut_xm1_s3_rrl_l m=x_dut_xm1_s3_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1610 520 0 1 {name=M1_S4_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s4_rrl_w l=x_dut_xm1_s4_rrl_l m=x_dut_xm1_s4_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2425 780 0 1 {name=M1_S5_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s5_rrl_w l=x_dut_xm1_s5_rrl_l m=x_dut_xm1_s5_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 910 780 0 1 {name=M1_S6_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s6_rrl_w l=x_dut_xm1_s6_rrl_l m=x_dut_xm1_s6_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2650 780 0 1 {name=M20_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_main_w l=x_dut_xm20_main_l m=x_dut_xm20_main_m}
C {devices/sg13_lv_pmos_np.sym} 2910 780 0 1 {name=M21_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_main_w l=x_dut_xm21_main_l m=x_dut_xm21_main_m}
C {devices/sg13_lv_nmos_np.sym} -560 780 0 1 {name=M22_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_main_w l=x_dut_xm22_main_l m=x_dut_xm22_main_m}
C {devices/sg13_lv_pmos_np.sym} 3170 780 0 1 {name=M23_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_main_w l=x_dut_xm23_main_l m=x_dut_xm23_main_m}
C {devices/sg13_lv_nmos_np.sym} 3880 520 0 1 {name=M24_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_main_w l=x_dut_xm24_main_l m=x_dut_xm24_main_m}
C {devices/sg13_lv_pmos_np.sym} -1365 520 0 1 {name=M25_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm25_main_w l=x_dut_xm25_main_l m=x_dut_xm25_main_m}
C {devices/sg13_lv_nmos_np.sym} 4110 520 0 1 {name=M26_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm26_main_w l=x_dut_xm26_main_l m=x_dut_xm26_main_m}
C {devices/sg13_lv_pmos_np.sym} -1600 520 0 1 {name=M27_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm27_main_w l=x_dut_xm27_main_l m=x_dut_xm27_main_m}
C {devices/sg13_lv_nmos_np.sym} 1845 520 0 1 {name=M28_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm28_main_w l=x_dut_xm28_main_l m=x_dut_xm28_main_m}
C {devices/sg13_lv_pmos_np.sym} -150 520 0 1 {name=M29_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm29_main_w l=x_dut_xm29_main_l m=x_dut_xm29_main_m}
C {devices/sg13_lv_pmos_np.sym} -815 780 0 1 {name=M2_CHRRL_1_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_1_rrl_w l=x_dut_xm2_chrrl_1_rrl_l m=x_dut_xm2_chrrl_1_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 3605 780 0 1 {name=M2_CHRRL_2_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_2_rrl_w l=x_dut_xm2_chrrl_2_rrl_l m=x_dut_xm2_chrrl_2_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -1090 780 0 1 {name=M2_CHRRL_3_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_3_rrl_w l=x_dut_xm2_chrrl_3_rrl_l m=x_dut_xm2_chrrl_3_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 3880 780 0 1 {name=M2_CHRRL_4_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_4_rrl_w l=x_dut_xm2_chrrl_4_rrl_l m=x_dut_xm2_chrrl_4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1695 260 0 1 {name=M2_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_main_w l=x_dut_xm2_main_l m=x_dut_xm2_main_m}
C {devices/sg13_lv_pmos_np.sym} 2475 260 0 0 {name=M2_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_rrl_w l=x_dut_xm2_opamp_rrl_l m=x_dut_xm2_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 360 1040 0 1 {name=M2_S1_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s1_rrl_w l=x_dut_xm2_s1_rrl_l m=x_dut_xm2_s1_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2190 1040 0 1 {name=M2_S2_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s2_rrl_w l=x_dut_xm2_s2_rrl_l m=x_dut_xm2_s2_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 4345 520 0 1 {name=M2_S3_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s3_rrl_w l=x_dut_xm2_s3_rrl_l m=x_dut_xm2_s3_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2080 520 0 1 {name=M2_S4_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s4_rrl_w l=x_dut_xm2_s4_rrl_l m=x_dut_xm2_s4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -1365 780 0 1 {name=M2_S5_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s5_rrl_w l=x_dut_xm2_s5_rrl_l m=x_dut_xm2_s5_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1150 780 0 1 {name=M2_S6_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s6_rrl_w l=x_dut_xm2_s6_rrl_l m=x_dut_xm2_s6_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 6350 520 0 0 {name=M30_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm30_main_w l=x_dut_xm30_main_l m=x_dut_xm30_main_m}
C {devices/sg13_lv_pmos_np.sym} 6575 520 0 0 {name=M31_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm31_main_w l=x_dut_xm31_main_l m=x_dut_xm31_main_m}
C {devices/sg13_lv_nmos_np.sym} -1830 520 0 1 {name=M32_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm32_main_w l=x_dut_xm32_main_l m=x_dut_xm32_main_m}
C {devices/sg13_lv_pmos_np.sym} 4575 520 0 1 {name=M33_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm33_main_w l=x_dut_xm33_main_l m=x_dut_xm33_main_m}
C {devices/sg13_lv_nmos_np.sym} -2060 520 0 1 {name=M34_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm34_main_w l=x_dut_xm34_main_l m=x_dut_xm34_main_m}
C {devices/sg13_lv_pmos_np.sym} 4800 520 0 1 {name=M35_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm35_main_w l=x_dut_xm35_main_l m=x_dut_xm35_main_m}
C {devices/sg13_lv_nmos_np.sym} 4110 780 0 1 {name=M36_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm36_main_w l=x_dut_xm36_main_l m=x_dut_xm36_main_m}
C {devices/sg13_lv_pmos_np.sym} -1600 780 0 1 {name=M37_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm37_main_w l=x_dut_xm37_main_l m=x_dut_xm37_main_m}
C {devices/sg13_lv_nmos_np.sym} 4345 780 0 1 {name=M38_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm38_main_w l=x_dut_xm38_main_l m=x_dut_xm38_main_m}
C {devices/sg13_lv_pmos_np.sym} -1830 780 0 1 {name=M39_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm39_main_w l=x_dut_xm39_main_l m=x_dut_xm39_main_m}
C {devices/sg13_lv_pmos_np.sym} -80 260 0 1 {name=M3_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_main_w l=x_dut_xm3_main_l m=x_dut_xm3_main_m}
C {devices/sg13_lv_pmos_np.sym} 215 260 0 1 {name=M3_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_rrl_w l=x_dut_xm3_opamp_rrl_l m=x_dut_xm3_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 4575 780 0 1 {name=M4_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_main_w l=x_dut_xm4_main_l m=x_dut_xm4_main_m}
C {devices/sg13_lv_pmos_np.sym} 1440 0 0 1 {name=M4_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_opamp_rrl_w l=x_dut_xm4_opamp_rrl_l m=x_dut_xm4_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} -2060 780 0 1 {name=M5_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_main_w l=x_dut_xm5_main_l m=x_dut_xm5_main_m}
C {devices/sg13_lv_pmos_np.sym} -300 260 0 1 {name=M5_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_opamp_rrl_w l=x_dut_xm5_opamp_rrl_l m=x_dut_xm5_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 910 0 0 1 {name=M6_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_main_w l=x_dut_xm6_main_l m=x_dut_xm6_main_m}
C {devices/sg13_lv_pmos_np.sym} 2910 260 0 1 {name=M6_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_opamp_rrl_w l=x_dut_xm6_opamp_rrl_l m=x_dut_xm6_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1960 0 0 0 {name=M7_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_main_w l=x_dut_xm7_main_l m=x_dut_xm7_main_m}
C {devices/sg13_lv_pmos_np.sym} -560 260 0 1 {name=M7_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_opamp_rrl_w l=x_dut_xm7_opamp_rrl_l m=x_dut_xm7_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1695 0 0 1 {name=M8_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_main_w l=x_dut_xm8_main_l m=x_dut_xm8_main_m}
C {devices/sg13_lv_pmos_np.sym} 3170 260 0 1 {name=M8_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_opamp_rrl_w l=x_dut_xm8_opamp_rrl_l m=x_dut_xm8_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 360 0 0 1 {name=M9_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_main_w l=x_dut_xm9_main_l m=x_dut_xm9_main_m}
C {devices/sg13_lv_pmos_np.sym} 2475 520 0 0 {name=M9_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_rrl_w l=x_dut_xm9_opamp_rrl_l m=x_dut_xm9_opamp_rrl_m}
N -3070 430 -3070 490 {}
N -3070 550 -3070 610 {}
N -3070 690 -3070 750 {}
N -3070 810 -3070 870 {}
N -3070 950 -3070 1010 {}
N -3070 1070 -3070 1130 {}
N -2730 -90 -2730 -30 {}
N -2730 30 -2730 90 {}
N -2730 170 -2730 230 {}
N -2730 290 -2730 350 {}
N -2730 430 -2730 490 {}
N -2730 550 -2730 610 {}
N -2730 690 -2730 750 {}
N -2730 810 -2730 870 {}
N -2730 950 -2730 1010 {}
N -2730 1070 -2730 1130 {}
N -2360 520 -2360 580 {}
N -2140 520 -2140 614 {}
N -2140 780 -2140 874 {}
N -2080 430 -2080 490 {}
N -2080 550 -2080 610 {}
N -2080 690 -2080 750 {}
N -2080 810 -2080 1180 {}
N -2040 520 -2040 580 {}
N -2040 780 -2040 840 {}
N -1910 520 -1910 614 {}
N -1910 780 -1910 874 {}
N -1850 430 -1850 490 {}
N -1850 550 -1850 610 {}
N -1850 690 -1850 750 {}
N -1850 810 -1850 870 {}
N -1810 520 -1810 580 {}
N -1810 780 -1810 840 {}
N -1680 520 -1680 614 {}
N -1680 780 -1680 874 {}
N -1620 430 -1620 490 {}
N -1620 550 -1620 610 {}
N -1620 690 -1620 750 {}
N -1620 810 -1620 870 {}
N -1580 520 -1580 580 {}
N -1580 780 -1580 840 {}
N -1445 520 -1445 614 {}
N -1445 780 -1445 874 {}
N -1385 430 -1385 490 {}
N -1385 550 -1385 610 {}
N -1385 690 -1385 750 {}
N -1385 810 -1385 870 {}
N -1345 520 -1345 580 {}
N -1345 780 -1345 840 {}
N -1170 520 -1170 614 {}
N -1170 780 -1170 874 {}
N -1110 430 -1110 490 {}
N -1110 550 -1110 610 {}
N -1110 690 -1110 750 {}
N -1110 810 -1110 870 {}
N -1070 780 -1070 840 {}
N -895 780 -895 874 {}
N -835 690 -835 750 {}
N -835 810 -835 870 {}
N -815 430 -815 490 {}
N -815 550 -815 610 {}
N -795 780 -795 840 {}
N -640 260 -640 354 {}
N -640 780 -640 874 {}
N -580 170 -580 230 {}
N -580 290 -580 350 {}
N -580 690 -580 750 {}
N -580 810 -580 870 {}
N -560 430 -560 490 {}
N -560 550 -560 610 {}
N -540 780 -540 840 {}
N -380 260 -380 354 {}
N -320 200 -320 230 {}
N -320 290 -320 320 {}
N -280 260 -280 320 {}
N -270 780 -270 874 {}
N -270 1040 -270 1134 {}
N -230 520 -230 614 {}
N -210 690 -210 750 {}
N -210 810 -210 870 {}
N -210 950 -210 1010 {}
N -210 1070 -210 1180 {}
N -170 430 -170 490 {}
N -170 550 -170 610 {}
N -170 780 -170 840 {}
N -160 260 -160 354 {}
N -130 520 -130 580 {}
N -100 170 -100 230 {}
N -100 290 -100 350 {}
N -60 260 -60 320 {}
N 5 780 5 874 {}
N 65 690 65 750 {}
N 65 810 65 870 {}
N 105 780 105 840 {}
N 135 260 135 354 {}
N 135 520 135 614 {}
N 195 170 195 230 {}
N 195 290 195 350 {}
N 195 430 195 490 {}
N 195 550 195 610 {}
N 280 0 280 94 {}
N 280 780 280 874 {}
N 280 1040 280 1134 {}
N 340 -140 340 -30 {}
N 340 30 340 90 {}
N 340 690 340 750 {}
N 340 810 340 870 {}
N 340 950 340 1010 {}
N 340 1070 340 1180 {}
N 380 1040 380 1100 {}
N 385 60 385 620 {}
N 385 680 385 710 {}
N 480 450 480 520 {}
N 515 1040 515 1134 {}
N 520 430 520 490 {}
N 520 550 520 1180 {}
N 575 980 575 1010 {}
N 575 1070 575 1180 {}
N 580 520 580 614 {}
N 830 0 830 94 {}
N 830 260 830 354 {}
N 830 520 830 614 {}
N 830 780 830 874 {}
N 890 -140 890 -30 {}
N 890 30 890 90 {}
N 890 170 890 230 {}
N 890 290 890 350 {}
N 890 430 890 490 {}
N 890 550 890 610 {}
N 890 690 890 750 {}
N 890 810 890 870 {}
N 920 680 920 710 {}
N 920 980 920 1010 {}
N 920 1070 920 1100 {}
N 930 0 930 60 {}
N 930 260 930 320 {}
N 930 460 930 520 {}
N 930 780 930 840 {}
N 1070 520 1070 614 {}
N 1070 780 1070 874 {}
N 1100 0 1100 94 {}
N 1100 260 1100 354 {}
N 1130 430 1130 490 {}
N 1130 550 1130 610 {}
N 1130 690 1130 750 {}
N 1130 810 1130 870 {}
N 1160 -140 1160 -30 {}
N 1160 30 1160 90 {}
N 1160 170 1160 230 {}
N 1160 290 1160 350 {}
N 1170 460 1170 520 {}
N 1180 560 1180 620 {}
N 1180 680 1180 740 {}
N 1180 850 1180 880 {}
N 1180 940 1180 1010 {}
N 1180 1070 1180 1100 {}
N 1200 0 1200 60 {}
N 1200 260 1200 320 {}
N 1295 520 1295 614 {}
N 1355 430 1355 490 {}
N 1355 550 1355 610 {}
N 1360 0 1360 94 {}
N 1360 260 1360 354 {}
N 1395 460 1395 520 {}
N 1420 -140 1420 -30 {}
N 1420 30 1420 90 {}
N 1420 170 1420 230 {}
N 1420 290 1420 350 {}
N 1440 560 1440 620 {}
N 1440 680 1440 740 {}
N 1440 820 1440 880 {}
N 1440 940 1440 1100 {}
N 1460 0 1460 60 {}
N 1460 260 1460 320 {}
N 1470 690 1470 750 {}
N 1470 810 1470 870 {}
N 1470 950 1470 1010 {}
N 1470 1070 1470 1180 {}
N 1530 520 1530 614 {}
N 1530 780 1530 874 {}
N 1530 1040 1530 1134 {}
N 1590 430 1590 490 {}
N 1590 550 1590 610 {}
N 1615 0 1615 94 {}
N 1615 260 1615 354 {}
N 1630 460 1630 520 {}
N 1675 -140 1675 -30 {}
N 1675 30 1675 90 {}
N 1675 170 1675 230 {}
N 1675 290 1675 350 {}
N 1695 560 1695 620 {}
N 1695 680 1695 740 {}
N 1765 520 1765 614 {}
N 1825 430 1825 490 {}
N 1825 550 1825 610 {}
N 1830 780 1830 874 {}
N 1830 1040 1830 1134 {}
N 1865 460 1865 520 {}
N 1890 690 1890 750 {}
N 1890 810 1890 870 {}
N 1890 950 1890 1010 {}
N 1890 1070 1890 1180 {}
N 1895 520 1895 780 {}
N 1930 780 1930 840 {}
N 1930 1040 1930 1100 {}
N 1955 60 1955 620 {}
N 1955 680 1955 740 {}
N 1980 -140 1980 -30 {}
N 1980 30 1980 90 {}
N 1980 170 1980 230 {}
N 1980 290 1980 350 {}
N 2000 520 2000 614 {}
N 2040 0 2040 94 {}
N 2040 260 2040 354 {}
N 2060 430 2060 490 {}
N 2060 550 2060 610 {}
N 2110 1040 2110 1134 {}
N 2130 520 2130 780 {}
N 2170 690 2170 750 {}
N 2170 810 2170 870 {}
N 2170 980 2170 1010 {}
N 2170 1070 2170 1180 {}
N 2210 780 2210 840 {}
N 2345 780 2345 874 {}
N 2405 690 2405 750 {}
N 2405 810 2405 870 {}
N 2445 780 2445 840 {}
N 2455 -140 2455 -30 {}
N 2455 30 2455 90 {}
N 2475 780 2475 1040 {}
N 2495 170 2495 230 {}
N 2495 290 2495 350 {}
N 2495 430 2495 490 {}
N 2495 550 2495 610 {}
N 2515 0 2515 94 {}
N 2555 260 2555 354 {}
N 2555 520 2555 614 {}
N 2570 780 2570 874 {}
N 2630 690 2630 750 {}
N 2630 810 2630 870 {}
N 2670 780 2670 840 {}
N 2830 260 2830 354 {}
N 2830 780 2830 874 {}
N 2890 170 2890 230 {}
N 2890 290 2890 350 {}
N 2890 690 2890 750 {}
N 2890 810 2890 870 {}
N 2910 430 2910 490 {}
N 2910 550 2910 610 {}
N 2930 260 2930 320 {}
N 2930 780 2930 840 {}
N 3090 260 3090 354 {}
N 3090 780 3090 874 {}
N 3150 170 3150 230 {}
N 3150 290 3150 350 {}
N 3150 690 3150 750 {}
N 3150 810 3150 870 {}
N 3170 430 3170 490 {}
N 3170 550 3170 610 {}
N 3525 520 3525 614 {}
N 3525 780 3525 874 {}
N 3585 430 3585 490 {}
N 3585 550 3585 610 {}
N 3585 690 3585 750 {}
N 3585 810 3585 870 {}
N 3625 450 3625 520 {}
N 3625 780 3625 840 {}
N 3800 520 3800 614 {}
N 3800 780 3800 874 {}
N 3860 430 3860 490 {}
N 3860 550 3860 610 {}
N 3860 690 3860 750 {}
N 3860 810 3860 870 {}
N 3900 520 3900 580 {}
N 3900 780 3900 840 {}
N 4030 520 4030 614 {}
N 4030 780 4030 874 {}
N 4090 430 4090 490 {}
N 4090 550 4090 610 {}
N 4090 690 4090 750 {}
N 4090 810 4090 870 {}
N 4130 520 4130 580 {}
N 4130 780 4130 840 {}
N 4265 520 4265 614 {}
N 4265 780 4265 874 {}
N 4325 430 4325 490 {}
N 4325 550 4325 610 {}
N 4325 690 4325 750 {}
N 4325 810 4325 870 {}
N 4365 520 4365 580 {}
N 4365 780 4365 840 {}
N 4495 520 4495 614 {}
N 4495 780 4495 874 {}
N 4555 430 4555 490 {}
N 4555 550 4555 610 {}
N 4555 690 4555 750 {}
N 4555 810 4555 1180 {}
N 4595 520 4595 580 {}
N 4720 520 4720 614 {}
N 4780 430 4780 490 {}
N 4780 550 4780 610 {}
N 4820 520 4820 580 {}
N 4970 260 4970 490 {}
N 4970 550 4970 610 {}
N 5225 260 5225 490 {}
N 5225 550 5225 610 {}
N 5505 520 5505 580 {}
N 5645 460 5645 520 {}
N 5685 320 5685 490 {}
N 5685 550 5685 610 {}
N 5745 520 5745 614 {}
N 5910 460 5910 490 {}
N 5910 550 5910 610 {}
N 5970 520 5970 614 {}
N 6140 460 6140 490 {}
N 6140 550 6140 610 {}
N 6200 520 6200 614 {}
N 6370 460 6370 490 {}
N 6370 550 6370 610 {}
N 6430 520 6430 614 {}
N 6595 460 6595 490 {}
N 6595 550 6595 580 {}
N 6655 520 6655 614 {}
N -3130 -140 6830 -140 {}
N 280 0 340 0 {}
N 380 0 440 0 {}
N 830 0 890 0 {}
N 930 0 960 0 {}
N 1100 0 1160 0 {}
N 1200 0 1230 0 {}
N 1360 0 1420 0 {}
N 1460 0 1490 0 {}
N 1615 0 1675 0 {}
N 1715 0 1940 0 {}
N 1980 0 2040 0 {}
N 2355 0 2415 0 {}
N 2455 0 2515 0 {}
N 340 60 385 60 {}
N 1675 60 1955 60 {}
N -580 200 -320 200 {}
N -640 260 -580 260 {}
N -540 260 -510 260 {}
N -380 260 -320 260 {}
N -280 260 -250 260 {}
N -160 260 -100 260 {}
N -60 260 -30 260 {}
N 135 260 195 260 {}
N 235 260 295 260 {}
N 830 260 890 260 {}
N 930 260 960 260 {}
N 1100 260 1160 260 {}
N 1200 260 1230 260 {}
N 1360 260 1420 260 {}
N 1460 260 1490 260 {}
N 1615 260 1675 260 {}
N 1715 260 1775 260 {}
N 1880 260 1940 260 {}
N 1980 260 2040 260 {}
N 2395 260 2455 260 {}
N 2495 260 2555 260 {}
N 2830 260 2890 260 {}
N 2930 260 2960 260 {}
N 3090 260 3150 260 {}
N 3190 260 3250 260 {}
N -580 320 -320 320 {}
N 480 450 520 450 {}
N 3585 450 3625 450 {}
N 5685 460 6595 460 {}
N -2480 520 -2420 520 {}
N -2360 520 -2330 520 {}
N -2140 520 -2080 520 {}
N -2040 520 -2010 520 {}
N -1910 520 -1850 520 {}
N -1810 520 -1780 520 {}
N -1680 520 -1620 520 {}
N -1580 520 -1550 520 {}
N -1445 520 -1385 520 {}
N -1345 520 -1315 520 {}
N -1170 520 -1110 520 {}
N -1070 520 -1010 520 {}
N -230 520 -170 520 {}
N 135 520 195 520 {}
N 235 520 295 520 {}
N 520 520 580 520 {}
N 830 520 890 520 {}
N 930 520 960 520 {}
N 1070 520 1130 520 {}
N 1170 520 1200 520 {}
N 1295 520 1355 520 {}
N 1395 520 1425 520 {}
N 1530 520 1590 520 {}
N 1630 520 1660 520 {}
N 1765 520 1825 520 {}
N 1865 520 1895 520 {}
N 2000 520 2060 520 {}
N 2100 520 2160 520 {}
N 2395 520 2455 520 {}
N 2495 520 2555 520 {}
N 3525 520 3585 520 {}
N 3800 520 3860 520 {}
N 3900 520 3930 520 {}
N 4030 520 4090 520 {}
N 4130 520 4160 520 {}
N 4265 520 4325 520 {}
N 4365 520 4395 520 {}
N 4495 520 4555 520 {}
N 4595 520 4625 520 {}
N 4720 520 4780 520 {}
N 4820 520 4850 520 {}
N 5385 520 5445 520 {}
N 5505 520 5535 520 {}
N 5615 520 5645 520 {}
N 5685 520 5745 520 {}
N 5840 520 5870 520 {}
N 5910 520 5970 520 {}
N 6070 520 6100 520 {}
N 6140 520 6200 520 {}
N 6300 520 6330 520 {}
N 6370 520 6430 520 {}
N 6525 520 6555 520 {}
N 6595 520 6655 520 {}
N 6370 580 6595 580 {}
N 1955 590 4970 590 {}
N 860 620 920 620 {}
N 325 680 385 680 {}
N 860 680 920 680 {}
N 4555 720 5685 720 {}
N -2140 780 -2080 780 {}
N -2040 780 -2010 780 {}
N -1910 780 -1850 780 {}
N -1810 780 -1780 780 {}
N -1680 780 -1620 780 {}
N -1580 780 -1550 780 {}
N -1445 780 -1385 780 {}
N -1345 780 -1315 780 {}
N -1170 780 -1110 780 {}
N -895 780 -835 780 {}
N -795 780 -765 780 {}
N -640 780 -580 780 {}
N -540 780 -510 780 {}
N -270 780 -210 780 {}
N -170 780 -140 780 {}
N 5 780 65 780 {}
N 105 780 135 780 {}
N 280 780 340 780 {}
N 380 780 440 780 {}
N 830 780 890 780 {}
N 930 780 960 780 {}
N 1070 780 1130 780 {}
N 1170 780 1230 780 {}
N 1370 780 1430 780 {}
N 1470 780 1530 780 {}
N 1830 780 1890 780 {}
N 2210 780 2240 780 {}
N 2345 780 2405 780 {}
N 2445 780 2475 780 {}
N 2570 780 2630 780 {}
N 2670 780 2700 780 {}
N 2830 780 2890 780 {}
N 2930 780 2960 780 {}
N 3090 780 3150 780 {}
N 3190 780 3250 780 {}
N 3525 780 3585 780 {}
N 3625 780 3655 780 {}
N 3800 780 3860 780 {}
N 3900 780 3930 780 {}
N 4030 780 4090 780 {}
N 4130 780 4160 780 {}
N 4265 780 4325 780 {}
N 4365 780 4395 780 {}
N 4495 780 4555 780 {}
N 4595 780 4655 780 {}
N 1120 880 1180 880 {}
N 1120 940 1180 940 {}
N 340 980 575 980 {}
N 920 980 1180 980 {}
N 1890 980 2170 980 {}
N -270 1040 -210 1040 {}
N -170 1040 -110 1040 {}
N 280 1040 340 1040 {}
N 380 1040 410 1040 {}
N 515 1040 575 1040 {}
N 615 1040 675 1040 {}
N 1400 1040 1430 1040 {}
N 1470 1040 1530 1040 {}
N 1830 1040 1890 1040 {}
N 1930 1040 1960 1040 {}
N 2110 1040 2170 1040 {}
N 2210 1040 2475 1040 {}
N 920 1100 1440 1100 {}
N -3130 1180 6830 1180 {}
C {devices/lab_wire.sym} -3130 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -3130 1180 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -1810 840 2 0 {name=l2 lab=clk_chfb}
C {devices/lab_wire.sym} -1580 840 2 0 {name=l3 lab=clk_chfb}
C {devices/lab_wire.sym} -540 840 2 0 {name=l4 lab=clk_chfb}
C {devices/lab_wire.sym} 2670 840 2 0 {name=l5 lab=clk_chfb}
C {devices/lab_wire.sym} 2930 840 2 0 {name=l6 lab=clk_chfb_not}
C {devices/lab_wire.sym} 3250 780 0 1 {name=l7 lab=clk_chfb_not}
C {devices/lab_wire.sym} 4130 840 2 0 {name=l8 lab=clk_chfb_not}
C {devices/lab_wire.sym} 4365 840 2 0 {name=l9 lab=clk_chfb_not}
C {devices/lab_wire.sym} 3900 580 2 0 {name=l10 lab=clk_chin}
C {devices/lab_wire.sym} 4130 580 2 0 {name=l11 lab=clk_chin}
C {devices/lab_wire.sym} 4595 580 2 0 {name=l12 lab=clk_chin}
C {devices/lab_wire.sym} 4820 580 2 0 {name=l13 lab=clk_chin}
C {devices/lab_wire.sym} -2040 580 2 0 {name=l14 lab=clk_chin_not}
C {devices/lab_wire.sym} -1810 580 2 0 {name=l15 lab=clk_chin_not}
C {devices/lab_wire.sym} -1580 580 2 0 {name=l16 lab=clk_chin_not}
C {devices/lab_wire.sym} -1345 580 2 0 {name=l17 lab=clk_chin_not}
C {devices/lab_wire.sym} -1070 840 2 0 {name=l18 lab=clk_chout}
C {devices/lab_wire.sym} -130 580 2 0 {name=l19 lab=clk_chout}
C {devices/lab_wire.sym} 440 780 0 1 {name=l20 lab=clk_chout}
C {devices/lab_wire.sym} 1170 460 0 1 {name=l21 lab=clk_chout}
C {devices/lab_wire.sym} 1930 840 2 0 {name=l22 lab=clk_chout}
C {devices/lab_wire.sym} 3900 840 2 0 {name=l23 lab=clk_chout}
C {devices/lab_wire.sym} 5870 520 0 0 {name=l24 lab=clk_chout}
C {devices/lab_wire.sym} 6555 520 0 0 {name=l25 lab=clk_chout}
C {devices/lab_wire.sym} -795 840 2 0 {name=l26 lab=clk_chout_not}
C {devices/lab_wire.sym} 105 840 2 0 {name=l27 lab=clk_chout_not}
C {devices/lab_wire.sym} 1395 460 0 1 {name=l28 lab=clk_chout_not}
C {devices/lab_wire.sym} 1865 460 0 1 {name=l29 lab=clk_chout_not}
C {devices/lab_wire.sym} 2210 840 2 0 {name=l30 lab=clk_chout_not}
C {devices/lab_wire.sym} 3625 840 2 0 {name=l31 lab=clk_chout_not}
C {devices/lab_wire.sym} 6100 520 0 0 {name=l32 lab=clk_chout_not}
C {devices/lab_wire.sym} 6330 520 0 0 {name=l33 lab=clk_chout_not}
C {devices/lab_wire.sym} 380 1100 2 0 {name=l34 lab=clk_phi_1}
C {devices/lab_wire.sym} 930 840 2 0 {name=l35 lab=clk_phi_1}
C {devices/lab_wire.sym} 2160 520 0 1 {name=l36 lab=clk_phi_1}
C {devices/lab_wire.sym} 2445 840 2 0 {name=l37 lab=clk_phi_1}
C {devices/lab_wire.sym} 4365 580 2 0 {name=l38 lab=clk_phi_1}
C {devices/lab_wire.sym} -1345 840 2 0 {name=l39 lab=clk_phi_2}
C {devices/lab_wire.sym} -1010 520 0 1 {name=l40 lab=clk_phi_2}
C {devices/lab_wire.sym} 675 1040 0 1 {name=l41 lab=clk_phi_2}
C {devices/lab_wire.sym} 1230 780 0 1 {name=l42 lab=clk_phi_2}
C {devices/lab_wire.sym} 1630 460 0 1 {name=l43 lab=clk_phi_2}
C {devices/lab_wire.sym} 1930 1100 2 0 {name=l44 lab=clk_phi_2}
C {devices/lab_wire.sym} 890 90 2 0 {name=l45 lab=main__casc_src_n}
C {devices/lab_wire.sym} 890 170 0 1 {name=l46 lab=main__casc_src_n}
C {devices/lab_wire.sym} 1980 90 2 0 {name=l47 lab=main__casc_src_p}
C {devices/lab_wire.sym} 1980 170 0 1 {name=l48 lab=main__casc_src_p}
C {devices/lab_wire.sym} -1850 690 0 1 {name=l49 lab=main__fbch_n}
C {devices/lab_wire.sym} -580 690 0 1 {name=l50 lab=main__fbch_n}
C {devices/lab_wire.sym} 1695 560 0 1 {name=l51 lab=main__fbch_n}
C {devices/lab_wire.sym} 3150 690 0 1 {name=l52 lab=main__fbch_n}
C {devices/lab_wire.sym} 4325 690 0 1 {name=l53 lab=main__fbch_n}
C {devices/lab_wire.sym} -1620 690 0 1 {name=l54 lab=main__fbch_p}
C {devices/lab_wire.sym} 860 620 0 0 {name=l55 lab=main__fbch_p}
C {devices/lab_wire.sym} 2630 690 0 1 {name=l56 lab=main__fbch_p}
C {devices/lab_wire.sym} 2890 690 0 1 {name=l57 lab=main__fbch_p}
C {devices/lab_wire.sym} 4090 690 0 1 {name=l58 lab=main__fbch_p}
C {devices/lab_wire.sym} -2080 690 0 1 {name=l59 lab=main__fold_n}
C {devices/lab_wire.sym} -100 350 2 0 {name=l60 lab=main__fold_n}
C {devices/lab_wire.sym} 890 610 2 0 {name=l61 lab=main__fold_n}
C {devices/lab_wire.sym} 1675 350 2 0 {name=l62 lab=main__fold_p}
C {devices/lab_wire.sym} 4555 690 0 1 {name=l63 lab=main__fold_p}
C {devices/lab_wire.sym} 5685 610 2 0 {name=l64 lab=main__fold_p}
C {devices/lab_wire.sym} 1130 610 2 0 {name=l65 lab=main__g2_n}
C {devices/lab_wire.sym} 1355 610 2 0 {name=l66 lab=main__g2_n}
C {devices/lab_wire.sym} 1460 320 2 0 {name=l67 lab=main__g2_n}
C {devices/lab_wire.sym} 5225 430 0 1 {name=l68 lab=main__g2_n}
C {devices/lab_wire.sym} 6370 610 2 0 {name=l69 lab=main__g2_n}
C {devices/lab_wire.sym} -170 610 2 0 {name=l70 lab=main__g2_p}
C {devices/lab_wire.sym} 1200 320 2 0 {name=l71 lab=main__g2_p}
C {devices/lab_wire.sym} 1825 610 2 0 {name=l72 lab=main__g2_p}
C {devices/lab_wire.sym} 4970 430 0 1 {name=l73 lab=main__g2_p}
C {devices/lab_wire.sym} 5910 610 2 0 {name=l74 lab=main__g2_p}
C {devices/lab_wire.sym} 6140 610 2 0 {name=l75 lab=main__g2_p}
C {devices/lab_wire.sym} -2080 610 2 0 {name=l76 lab=main__inch_n}
C {devices/lab_wire.sym} -1385 610 2 0 {name=l77 lab=main__inch_n}
C {devices/lab_wire.sym} 2910 610 2 0 {name=l78 lab=main__inch_n}
C {devices/lab_wire.sym} 3860 610 2 0 {name=l79 lab=main__inch_n}
C {devices/lab_wire.sym} 4780 610 2 0 {name=l80 lab=main__inch_n}
C {devices/lab_wire.sym} -1850 610 2 0 {name=l81 lab=main__inch_p}
C {devices/lab_wire.sym} -1620 610 2 0 {name=l82 lab=main__inch_p}
C {devices/lab_wire.sym} -560 610 2 0 {name=l83 lab=main__inch_p}
C {devices/lab_wire.sym} 4090 610 2 0 {name=l84 lab=main__inch_p}
C {devices/lab_wire.sym} 4555 610 2 0 {name=l85 lab=main__inch_p}
C {devices/lab_wire.sym} -100 170 0 1 {name=l86 lab=main__tail}
C {devices/lab_wire.sym} 1160 90 2 0 {name=l87 lab=main__tail}
C {devices/lab_wire.sym} 1675 170 0 1 {name=l88 lab=main__tail}
C {devices/lab_wire.sym} -2040 840 2 0 {name=l89 lab=main__vb1}
C {devices/lab_wire.sym} 4655 780 0 1 {name=l90 lab=main__vb1}
C {devices/lab_wire.sym} 930 460 0 1 {name=l91 lab=main__vb2}
C {devices/lab_wire.sym} 5645 460 0 1 {name=l92 lab=main__vb2}
C {devices/lab_wire.sym} 930 320 2 0 {name=l93 lab=main__vb3}
C {devices/lab_wire.sym} 1880 260 0 0 {name=l94 lab=main__vb3}
C {devices/lab_wire.sym} 440 0 0 1 {name=l95 lab=main__vb4}
C {devices/lab_wire.sym} 930 60 2 0 {name=l96 lab=main__vb4}
C {devices/lab_wire.sym} 1200 60 2 0 {name=l97 lab=main__vb4}
C {devices/lab_wire.sym} 1775 0 0 1 {name=l98 lab=main__vb4}
C {devices/lab_wire.sym} -60 320 2 0 {name=l99 lab=main__vsum_n}
C {devices/lab_wire.sym} 860 680 0 0 {name=l100 lab=main__vsum_n}
C {devices/lab_wire.sym} 2910 430 0 1 {name=l101 lab=main__vsum_n}
C {devices/lab_wire.sym} 3170 430 0 1 {name=l102 lab=main__vsum_n}
C {devices/lab_wire.sym} -815 430 0 1 {name=l103 lab=main__vsum_p}
C {devices/lab_wire.sym} -560 430 0 1 {name=l104 lab=main__vsum_p}
C {devices/lab_wire.sym} 1695 740 2 0 {name=l105 lab=main__vsum_p}
C {devices/lab_wire.sym} 1775 260 0 1 {name=l106 lab=main__vsum_p}
C {devices/lab_wire.sym} -2480 520 0 0 {name=l107 lab=out1_n}
C {devices/lab_wire.sym} -170 430 0 1 {name=l108 lab=out1_n}
C {devices/lab_wire.sym} 890 350 2 0 {name=l109 lab=out1_n}
C {devices/lab_wire.sym} 890 430 0 1 {name=l110 lab=out1_n}
C {devices/lab_wire.sym} 1130 430 0 1 {name=l111 lab=out1_n}
C {devices/lab_wire.sym} 1355 430 0 1 {name=l112 lab=out1_n}
C {devices/lab_wire.sym} 1825 430 0 1 {name=l113 lab=out1_n}
C {devices/lab_wire.sym} 5385 520 0 0 {name=l114 lab=out1_n}
C {devices/lab_wire.sym} -2360 580 2 0 {name=l115 lab=out1_p}
C {devices/lab_wire.sym} 1980 350 2 0 {name=l116 lab=out1_p}
C {devices/lab_wire.sym} 5505 580 2 0 {name=l117 lab=out1_p}
C {devices/lab_wire.sym} 5685 430 0 1 {name=l118 lab=out1_p}
C {devices/lab_wire.sym} 890 870 2 0 {name=l119 lab=rrl__int_n}
C {devices/lab_wire.sym} 1440 1000 2 0 {name=l120 lab=rrl__int_n}
C {devices/lab_wire.sym} 1130 870 2 0 {name=l121 lab=rrl__int_n}
C {devices/lab_wire.sym} -1385 870 2 0 {name=l122 lab=rrl__int_p}
C {devices/lab_wire.sym} 1120 940 0 0 {name=l123 lab=rrl__int_p}
C {devices/lab_wire.sym} 2405 870 2 0 {name=l124 lab=rrl__int_p}
C {devices/lab_wire.sym} -110 1040 0 1 {name=l125 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 520 430 0 1 {name=l126 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 1430 1040 0 0 {name=l127 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 2890 350 2 0 {name=l128 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 3150 350 2 0 {name=l129 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} -580 350 2 0 {name=l130 lab=rrl__oa_cm_sense}
C {devices/lab_wire.sym} 3585 430 0 1 {name=l131 lab=rrl__oa_cm_sense}
C {devices/lab_wire.sym} -580 170 0 1 {name=l132 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} 1420 90 2 0 {name=l133 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} 2890 170 0 1 {name=l134 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} 3150 170 0 1 {name=l135 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} -210 870 2 0 {name=l136 lab=rrl__oa_csrc_n}
C {devices/lab_wire.sym} -210 950 0 1 {name=l137 lab=rrl__oa_csrc_n}
C {devices/lab_wire.sym} 1470 870 2 0 {name=l138 lab=rrl__oa_csrc_p}
C {devices/lab_wire.sym} 1470 950 0 1 {name=l139 lab=rrl__oa_csrc_p}
C {devices/lab_wire.sym} 2495 350 2 0 {name=l140 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 2495 430 0 1 {name=l141 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 195 350 2 0 {name=l142 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} 195 430 0 1 {name=l143 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} 295 260 0 1 {name=l144 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 1440 740 2 0 {name=l145 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 1590 430 0 1 {name=l146 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 2060 430 0 1 {name=l147 lab=rrl__oa_inn}
C {devices/lab_wire.sym} -1110 430 0 1 {name=l148 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 1180 740 2 0 {name=l149 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 2395 260 0 0 {name=l150 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 4325 430 0 1 {name=l151 lab=rrl__oa_inp}
C {devices/lab_wire.sym} -1385 690 0 1 {name=l152 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -1110 610 2 0 {name=l153 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -280 320 2 0 {name=l154 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -210 690 0 1 {name=l155 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 2405 690 0 1 {name=l156 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 2495 610 2 0 {name=l157 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 4325 610 2 0 {name=l158 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -540 260 0 0 {name=l159 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 195 610 2 0 {name=l160 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 890 690 0 1 {name=l161 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1130 690 0 1 {name=l162 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1470 690 0 1 {name=l163 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1590 610 2 0 {name=l164 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 2060 610 2 0 {name=l165 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 195 170 0 1 {name=l166 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 2455 90 2 0 {name=l167 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 2495 170 0 1 {name=l168 lab=rrl__oa_tail}
C {devices/lab_wire.sym} -1110 870 2 0 {name=l169 lab=rrl__sc_n}
C {devices/lab_wire.sym} 340 870 2 0 {name=l170 lab=rrl__sc_n}
C {devices/lab_wire.sym} 340 950 0 1 {name=l171 lab=rrl__sc_n}
C {devices/lab_wire.sym} 325 680 0 0 {name=l172 lab=rrl__sc_n}
C {devices/lab_wire.sym} 2170 870 2 0 {name=l173 lab=rrl__sc_n}
C {devices/lab_wire.sym} 3585 870 2 0 {name=l174 lab=rrl__sc_n}
C {devices/lab_wire.sym} -835 870 2 0 {name=l175 lab=rrl__sc_p}
C {devices/lab_wire.sym} 65 870 2 0 {name=l176 lab=rrl__sc_p}
C {devices/lab_wire.sym} 1890 870 2 0 {name=l177 lab=rrl__sc_p}
C {devices/lab_wire.sym} 1890 950 0 1 {name=l178 lab=rrl__sc_p}
C {devices/lab_wire.sym} 1955 740 2 0 {name=l179 lab=rrl__sc_p}
C {devices/lab_wire.sym} 3860 870 2 0 {name=l180 lab=rrl__sc_p}
C {devices/lab_wire.sym} 65 690 0 1 {name=l181 lab=rrl__sum_n}
C {devices/lab_wire.sym} 340 690 0 1 {name=l182 lab=rrl__sum_n}
C {devices/lab_wire.sym} 1440 560 0 1 {name=l183 lab=rrl__sum_n}
C {devices/lab_wire.sym} 1440 820 0 1 {name=l184 lab=rrl__sum_n}
C {devices/lab_wire.sym} 3585 690 0 1 {name=l185 lab=rrl__sum_n}
C {devices/lab_wire.sym} 3860 690 0 1 {name=l186 lab=rrl__sum_n}
C {devices/lab_wire.sym} -1110 690 0 1 {name=l187 lab=rrl__sum_p}
C {devices/lab_wire.sym} -835 690 0 1 {name=l188 lab=rrl__sum_p}
C {devices/lab_wire.sym} 1180 560 0 1 {name=l189 lab=rrl__sum_p}
C {devices/lab_wire.sym} 1120 880 0 0 {name=l190 lab=rrl__sum_p}
C {devices/lab_wire.sym} 1890 690 0 1 {name=l191 lab=rrl__sum_p}
C {devices/lab_wire.sym} 2170 690 0 1 {name=l192 lab=rrl__sum_p}
C {devices/lab_wire.sym} 295 520 0 1 {name=l193 lab=rrl__vb1}
C {devices/lab_wire.sym} 2395 520 0 0 {name=l194 lab=rrl__vb1}
C {devices/lab_wire.sym} -170 840 2 0 {name=l195 lab=rrl__vb2}
C {devices/lab_wire.sym} 1370 780 0 0 {name=l196 lab=rrl__vb2}
C {devices/lab_wire.sym} 1460 60 2 0 {name=l197 lab=rrl__vb3}
C {devices/lab_wire.sym} 2355 0 0 0 {name=l198 lab=rrl__vb3}
C {devices/lab_wire.sym} 2930 320 2 0 {name=l199 lab=rrl__vb4}
C {devices/lab_wire.sym} 3250 260 0 1 {name=l200 lab=rrl__vb4}
C {devices/lab_wire.sym} -1850 430 0 1 {name=l201 lab=vinn}
C {devices/lab_wire.sym} -1385 430 0 1 {name=l202 lab=vinn}
C {devices/lab_wire.sym} 3860 430 0 1 {name=l203 lab=vinn}
C {devices/lab_wire.sym} 4555 430 0 1 {name=l204 lab=vinn}
C {devices/lab_wire.sym} -2080 430 0 1 {name=l205 lab=vinp}
C {devices/lab_wire.sym} -1620 430 0 1 {name=l206 lab=vinp}
C {devices/lab_wire.sym} 4090 430 0 1 {name=l207 lab=vinp}
C {devices/lab_wire.sym} 4780 430 0 1 {name=l208 lab=vinp}
C {devices/lab_wire.sym} -1620 870 2 0 {name=l209 lab=voutn}
C {devices/lab_wire.sym} -580 870 2 0 {name=l210 lab=voutn}
C {devices/lab_wire.sym} 340 90 2 0 {name=l211 lab=voutn}
C {devices/lab_wire.sym} 1420 170 0 1 {name=l212 lab=voutn}
C {devices/lab_wire.sym} 3150 870 2 0 {name=l213 lab=voutn}
C {devices/lab_wire.sym} 4090 870 2 0 {name=l214 lab=voutn}
C {devices/lab_wire.sym} 5225 610 2 0 {name=l215 lab=voutn}
C {devices/lab_wire.sym} -1850 870 2 0 {name=l216 lab=voutp}
C {devices/lab_wire.sym} 1160 170 0 1 {name=l217 lab=voutp}
C {devices/lab_wire.sym} 1675 90 2 0 {name=l218 lab=voutp}
C {devices/lab_wire.sym} 2630 870 2 0 {name=l219 lab=voutp}
C {devices/lab_wire.sym} 2890 870 2 0 {name=l220 lab=voutp}
C {devices/lab_wire.sym} 4325 870 2 0 {name=l221 lab=voutp}
C {devices/lab_wire.sym} 4970 610 2 0 {name=l222 lab=voutp}
C {devices/lab_wire.sym} -815 610 2 0 {name=l223 lab=vref}
C {devices/lab_wire.sym} 3170 610 2 0 {name=l224 lab=vref}
C {devices/lab_wire.sym} 830 354 2 0 {name=l225 lab=vdd}
C {devices/lab_wire.sym} 135 614 2 0 {name=l226 lab=vdd}
C {devices/lab_wire.sym} 2040 354 2 0 {name=l227 lab=vdd}
C {devices/lab_wire.sym} 1295 614 2 0 {name=l228 lab=vdd}
C {devices/lab_wire.sym} 6200 614 2 0 {name=l229 lab=vdd}
C {devices/lab_wire.sym} 1100 94 2 0 {name=l230 lab=vdd}
C {devices/lab_wire.sym} 2515 94 2 0 {name=l231 lab=vdd}
C {devices/lab_wire.sym} 2830 874 2 0 {name=l232 lab=vdd}
C {devices/lab_wire.sym} 3090 874 2 0 {name=l233 lab=vdd}
C {devices/lab_wire.sym} -1445 614 2 0 {name=l234 lab=vdd}
C {devices/lab_wire.sym} -1680 614 2 0 {name=l235 lab=vdd}
C {devices/lab_wire.sym} -230 614 2 0 {name=l236 lab=vdd}
C {devices/lab_wire.sym} -895 874 2 0 {name=l237 lab=vdd}
C {devices/lab_wire.sym} 3525 874 2 0 {name=l238 lab=vdd}
C {devices/lab_wire.sym} -1170 874 2 0 {name=l239 lab=vdd}
C {devices/lab_wire.sym} 3800 874 2 0 {name=l240 lab=vdd}
C {devices/lab_wire.sym} 1615 354 2 0 {name=l241 lab=vdd}
C {devices/lab_wire.sym} 2555 354 2 0 {name=l242 lab=vdd}
C {devices/lab_wire.sym} 280 1134 2 0 {name=l243 lab=vdd}
C {devices/lab_wire.sym} 2110 1134 2 0 {name=l244 lab=vdd}
C {devices/lab_wire.sym} 4265 614 2 0 {name=l245 lab=vdd}
C {devices/lab_wire.sym} 2000 614 2 0 {name=l246 lab=vdd}
C {devices/lab_wire.sym} -1445 874 2 0 {name=l247 lab=vdd}
C {devices/lab_wire.sym} 1070 874 2 0 {name=l248 lab=vdd}
C {devices/lab_wire.sym} 6655 614 2 0 {name=l249 lab=vdd}
C {devices/lab_wire.sym} 4495 614 2 0 {name=l250 lab=vdd}
C {devices/lab_wire.sym} 4720 614 2 0 {name=l251 lab=vdd}
C {devices/lab_wire.sym} -1680 874 2 0 {name=l252 lab=vdd}
C {devices/lab_wire.sym} -1910 874 2 0 {name=l253 lab=vdd}
C {devices/lab_wire.sym} -160 354 2 0 {name=l254 lab=vdd}
C {devices/lab_wire.sym} 135 354 2 0 {name=l255 lab=vdd}
C {devices/lab_wire.sym} 1360 94 2 0 {name=l256 lab=vdd}
C {devices/lab_wire.sym} -380 354 2 0 {name=l257 lab=vdd}
C {devices/lab_wire.sym} 830 94 2 0 {name=l258 lab=vdd}
C {devices/lab_wire.sym} 2830 354 2 0 {name=l259 lab=vdd}
C {devices/lab_wire.sym} 2040 94 2 0 {name=l260 lab=vdd}
C {devices/lab_wire.sym} -640 354 2 0 {name=l261 lab=vdd}
C {devices/lab_wire.sym} 1615 94 2 0 {name=l262 lab=vdd}
C {devices/lab_wire.sym} 3090 354 2 0 {name=l263 lab=vdd}
C {devices/lab_wire.sym} 280 94 2 0 {name=l264 lab=vdd}
C {devices/lab_wire.sym} 2555 614 2 0 {name=l265 lab=vdd}
C {devices/lab_wire.sym} -270 874 2 0 {name=l266 lab=vss}
C {devices/lab_wire.sym} 5745 614 2 0 {name=l267 lab=vss}
C {devices/lab_wire.sym} 1530 874 2 0 {name=l268 lab=vss}
C {devices/lab_wire.sym} 830 614 2 0 {name=l269 lab=vss}
C {devices/lab_wire.sym} -270 1134 2 0 {name=l270 lab=vss}
C {devices/lab_wire.sym} 1100 354 2 0 {name=l271 lab=vss}
C {devices/lab_wire.sym} 1530 1134 2 0 {name=l272 lab=vss}
C {devices/lab_wire.sym} 1360 354 2 0 {name=l273 lab=vss}
C {devices/lab_wire.sym} 580 614 2 0 {name=l274 lab=vss}
C {devices/lab_wire.sym} 1070 614 2 0 {name=l275 lab=vss}
C {devices/lab_wire.sym} 3525 614 2 0 {name=l276 lab=vss}
C {devices/lab_wire.sym} 5970 614 2 0 {name=l277 lab=vss}
C {devices/lab_wire.sym} 1830 874 2 0 {name=l278 lab=vss}
C {devices/lab_wire.sym} 280 874 2 0 {name=l279 lab=vss}
C {devices/lab_wire.sym} 2170 780 0 0 {name=l280 lab=vss}
C {devices/lab_wire.sym} 5 874 2 0 {name=l281 lab=vss}
C {devices/lab_wire.sym} 515 1134 2 0 {name=l282 lab=vss}
C {devices/lab_wire.sym} 1830 1134 2 0 {name=l283 lab=vss}
C {devices/lab_wire.sym} -1170 614 2 0 {name=l284 lab=vss}
C {devices/lab_wire.sym} 1530 614 2 0 {name=l285 lab=vss}
C {devices/lab_wire.sym} 2345 874 2 0 {name=l286 lab=vss}
C {devices/lab_wire.sym} 830 874 2 0 {name=l287 lab=vss}
C {devices/lab_wire.sym} 2570 874 2 0 {name=l288 lab=vss}
C {devices/lab_wire.sym} -640 874 2 0 {name=l289 lab=vss}
C {devices/lab_wire.sym} 3800 614 2 0 {name=l290 lab=vss}
C {devices/lab_wire.sym} 4030 614 2 0 {name=l291 lab=vss}
C {devices/lab_wire.sym} 1765 614 2 0 {name=l292 lab=vss}
C {devices/lab_wire.sym} 6430 614 2 0 {name=l293 lab=vss}
C {devices/lab_wire.sym} -1910 614 2 0 {name=l294 lab=vss}
C {devices/lab_wire.sym} -2140 614 2 0 {name=l295 lab=vss}
C {devices/lab_wire.sym} 4030 874 2 0 {name=l296 lab=vss}
C {devices/lab_wire.sym} 4265 874 2 0 {name=l297 lab=vss}
C {devices/lab_wire.sym} 4495 874 2 0 {name=l298 lab=vss}
C {devices/lab_wire.sym} -2140 874 2 0 {name=l299 lab=vss}
C {devices/lab_wire.sym} -2730 950 0 1 {name=l300 lab=main__vb1}
C {devices/lab_wire.sym} -2730 1130 2 0 {name=l301 lab=vss}
C {devices/lab_wire.sym} -2730 870 2 0 {name=l302 lab=vss}
C {devices/lab_wire.sym} -2730 610 2 0 {name=l303 lab=vss}
C {devices/lab_wire.sym} -2730 350 2 0 {name=l304 lab=vss}
C {devices/lab_wire.sym} -2730 90 2 0 {name=l305 lab=vss}
C {devices/lab_wire.sym} -3070 1130 2 0 {name=l306 lab=vss}
C {devices/lab_wire.sym} -3070 870 2 0 {name=l307 lab=vss}
C {devices/lab_wire.sym} -3070 610 2 0 {name=l308 lab=vss}
C {devices/lab_wire.sym} -2730 690 0 1 {name=l309 lab=rrl__vb1}
C {devices/lab_wire.sym} -2730 430 0 1 {name=l310 lab=main__vb2}
C {devices/lab_wire.sym} -2730 170 0 1 {name=l311 lab=rrl__vb2}
C {devices/lab_wire.sym} -2730 -90 0 1 {name=l312 lab=main__vb3}
C {devices/lab_wire.sym} -3070 950 0 1 {name=l313 lab=rrl__vb3}
C {devices/lab_wire.sym} -3070 690 0 1 {name=l314 lab=main__vb4}
C {devices/lab_wire.sym} -3070 430 0 1 {name=l315 lab=rrl__vb4}
C {devices/lab_wire.sym} 1160 350 2 0 {name=l316 lab=vss}
C {devices/lab_wire.sym} 1420 350 2 0 {name=l317 lab=vss}
C {devices/lab_wire.sym} 3585 610 2 0 {name=l318 lab=vss}
C {devices/ipin.sym} -3270 520 0 0 {name=p0 lab=clk_chin_not}
C {devices/ipin.sym} -3270 640 0 0 {name=p1 lab=clk_phi_2}
C {devices/ipin.sym} -3270 760 0 0 {name=p2 lab=clk_chout}
C {devices/ipin.sym} -3270 880 0 0 {name=p3 lab=clk_chout_not}
C {devices/ipin.sym} -3270 1000 0 0 {name=p4 lab=clk_phi_1}
C {devices/ipin.sym} -3270 1120 0 0 {name=p5 lab=clk_chin}
C {devices/ipin.sym} -3270 1240 0 0 {name=p6 lab=clk_chfb}
C {devices/ipin.sym} -3270 1360 0 0 {name=p7 lab=clk_chfb_not}
C {devices/iopin.sym} -815 1320 0 0 {name=p8 lab=vref}
C {devices/opin.sym} 6970 30 0 0 {name=p9 lab=voutn}
C {devices/opin.sym} 6970 150 0 0 {name=p10 lab=voutp}
C {devices/opin.sym} 6970 490 0 0 {name=p11 lab=vinp}
C {devices/opin.sym} 6970 610 0 0 {name=p12 lab=vinn}
B 8 -466 442 1726 1118 {fill=0}
T {NMOS Simple Current Mirror (2 outputs)} -466 424 0 0 0.3 0.3 {layer=8}
B 10 -61 182 2743 598 {fill=0}
T {PMOS Cascode Differential Pair Differential Pair} -61 164 0 0 0.3 0.3 {layer=10}
B 12 914 442 1445 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 914 424 0 0 0.3 0.3 {layer=12}
B 21 5820 442 6356 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 5820 424 0 0 0.3 0.3 {layer=21}
B 15 -199 702 1980 858 {fill=0}
T {NMOS Differential Pair} -199 684 0 0 0.3 0.3 {layer=15}
B 13 -1099 702 1980 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1099 684 0 0 0.3 0.3 {layer=13}
B 18 76 702 2260 858 {fill=0}
T {NMOS Differential Pair} 76 684 0 0 0.3 0.3 {layer=18}
B 20 76 702 3675 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 76 660 0 0 0.3 0.3 {layer=20}
B 8 -1374 702 2260 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1374 684 0 0 0.3 0.3 {layer=8}
B 10 -199 702 3950 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -199 660 0 0 0.3 0.3 {layer=10}
B 12 -1334 442 4415 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1334 424 0 0 0.3 0.3 {layer=12}
B 21 1366 442 2150 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1366 424 0 0 0.3 0.3 {layer=21}
B 15 -1609 702 2495 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1609 684 0 0 0.3 0.3 {layer=15}
B 13 666 702 1220 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 666 684 0 0 0.3 0.3 {layer=13}
B 18 2414 702 2980 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 2414 684 0 0 0.3 0.3 {layer=18}
B 20 2414 702 4415 858 {fill=0}
T {NMOS Differential Pair} 2414 660 0 0 0.3 0.3 {layer=20}
B 8 -796 702 3240 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -796 684 0 0 0.3 0.3 {layer=8}
B 10 -796 702 4180 858 {fill=0}
T {NMOS Differential Pair} -796 660 0 0 0.3 0.3 {layer=10}
B 12 -1601 442 3950 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1601 424 0 0 0.3 0.3 {layer=12}
B 21 -1836 442 4180 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1836 424 0 0 0.3 0.3 {layer=21}
B 15 -386 442 1915 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -386 424 0 0 0.3 0.3 {layer=15}
B 13 -308 182 1765 338 {fill=0}
T {PMOS Differential Pair} -308 164 0 0 0.3 0.3 {layer=13}
B 18 6280 442 6811 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 6280 424 0 0 0.3 0.3 {layer=18}
B 20 -2066 442 4645 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2066 424 0 0 0.3 0.3 {layer=20}
B 8 -2296 442 4870 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2296 424 0 0 0.3 0.3 {layer=8}
B 10 -1836 702 4180 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1836 684 0 0 0.3 0.3 {layer=10}
B 12 -2066 702 4415 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2066 684 0 0 0.3 0.3 {layer=12}
B 21 -568 182 2980 338 {fill=0}
T {PMOS Differential Pair} -568 164 0 0 0.3 0.3 {layer=21}
B 15 -568 182 3240 338 {fill=0}
T {PMOS Differential Pair} -568 140 0 0 0.3 0.3 {layer=15}
B 13 -828 182 2980 338 {fill=0}
T {PMOS Differential Pair} -828 164 0 0 0.3 0.3 {layer=13}
B 18 -828 182 3240 338 {fill=0}
T {PMOS Differential Pair} -828 140 0 0 0.3 0.3 {layer=18}
B 20 -31 204 2721 316 {fill=0 dash=4}
T {PMOS Differential Pair} -31 138 0 0 0.3 0.3 {layer=20}
