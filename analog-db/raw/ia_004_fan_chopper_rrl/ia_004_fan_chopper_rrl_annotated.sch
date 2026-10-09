v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_004_fan_chopper_rrl} -3270 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1780 650 0 0 {name=CAZ1_RRL value='x_dut_caz1_rrl_value'}
C {devices/capa_np.sym} 2080 650 0 0 {name=CAZ2_RRL value='x_dut_caz2_rrl_value'}
C {devices/capa_np.sym} 1480 650 0 0 {name=CFB1_MAIN value='x_dut_cfb1_main_value'}
C {devices/capa_np.sym} 2370 650 0 0 {name=CFB2_MAIN value='x_dut_cfb2_main_value'}
C {devices/capa_np.sym} 3775 520 0 0 {name=CIN1_MAIN value='x_dut_cin1_main_value'}
C {devices/capa_np.sym} -190 520 0 0 {name=CIN2_MAIN value='x_dut_cin2_main_value'}
C {devices/capa_np.sym} 1780 910 0 0 {name=CINT1_RRL value='x_dut_cint1_rrl_value'}
C {devices/capa_np.sym} 2080 910 0 0 {name=CINT2_RRL value='x_dut_cint2_rrl_value'}
C {devices/capa_np.sym} 1780 1040 0 0 {name=CIN_1_RRL value='cin_val_rrl'}
C {devices/capa_np.sym} 6140 520 0 0 {name=CIN_SERVO_CMFB value='cin_val_cmfb'}
C {devices/capa_np.sym} 6365 520 0 0 {name=CM1_MAIN value='x_dut_cm1_main_value'}
C {devices/capa_np.sym} 6655 520 0 0 {name=CM2_MAIN value='x_dut_cm2_main_value'}
C {devices/capa_np.sym} 6945 520 1 0 {name=COUT_1_RRL value='cout_val_rrl'}
C {devices/capa_np.sym} 2380 910 0 0 {name=COUT_SERVO_CMFB value='cout_val_cmfb'}
C {devices/capa_np.sym} 2665 650 0 0 {name=CS1_RRL value='x_dut_cs1_rrl_value'}
C {devices/capa_np.sym} 870 650 0 0 {name=CS2_RRL value='x_dut_cs2_rrl_value'}
C {devices/vccs.sym} 5980 780 1 0 {name=GM_1_RRL value="\{gm_val_rrl\}"}
C {devices/vccs.sym} 1790 715 0 0 {name=GM_SERVO_CMFB value="\{gm_val_cmfb\}"}
C {devices/res_np.sym} 4070 520 0 0 {name=RB1_MAIN value='x_dut_rb1_main_value'}
C {devices/res_np.sym} -480 520 0 0 {name=RB2_MAIN value='x_dut_rb2_main_value'}
C {devices/res_np.sym} 2975 1040 0 0 {name=RIN_1_RRL value='rin_val_rrl'}
C {devices/res_np.sym} -2325 520 0 0 {name=RIN_SERVO_CMFB value='rin_val_cmfb'}
C {devices/res_np.sym} 2105 390 0 0 {name=RMN_CMFB value='x_dut_rmn_cmfb_value'}
C {devices/res_np.sym} 1795 390 0 0 {name=RMP_CMFB value='x_dut_rmp_cmfb_value'}
C {devices/res_np.sym} -2550 520 1 0 {name=ROUT_1_RRL value='rout_val_rrl'}
C {devices/res_np.sym} 1130 910 0 0 {name=ROUT_SERVO_CMFB value='rout_val_cmfb'}
C {devices/vsource_np.sym} -2890 1040 0 0 {name=VB1_MAIN value="dc \{vb1_main\}" savecurrent=false}
C {devices/vsource_np.sym} -2890 780 0 0 {name=VB1_RRL value="dc \{vb1_rrl\}" savecurrent=false}
C {devices/vsource_np.sym} -2890 520 0 0 {name=VB2_MAIN value="dc \{vb2_main\}" savecurrent=false}
C {devices/vsource_np.sym} -2890 260 0 0 {name=VB2_RRL value="dc \{vb2_rrl\}" savecurrent=false}
C {devices/vsource_np.sym} -2890 0 0 0 {name=VB3_MAIN value="dc \{vb3_main\}" savecurrent=false}
C {devices/vsource_np.sym} -3230 1040 0 0 {name=VB3_RRL value="dc \{vb3_rrl\}" savecurrent=false}
C {devices/vsource_np.sym} -3230 780 0 0 {name=VB40 value="dc \{vb40\}" savecurrent=false}
C {devices/vsource_np.sym} -3230 520 0 0 {name=VB4_RRL value="dc \{vb4_rrl\}" savecurrent=false}
C {devices/vsource_np.sym} -3230 260 0 0 {name=VREFCM value="dc \{vcm_ref\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 1470 260 0 1 {name=M10_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_main_w l=x_dut_xm10_main_l m=x_dut_xm10_main_m}
C {devices/sg13_lv_pmos_np.sym} 660 520 0 1 {name=M10_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_rrl_w l=x_dut_xm10_opamp_rrl_l m=x_dut_xm10_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2670 260 0 0 {name=M11_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_main_w l=x_dut_xm11_main_l m=x_dut_xm11_main_m}
C {devices/sg13_lv_nmos_np.sym} 215 780 0 1 {name=M11_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_opamp_rrl_w l=x_dut_xm11_opamp_rrl_l m=x_dut_xm11_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 7170 520 0 0 {name=M12_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_main_w l=x_dut_xm12_main_l m=x_dut_xm12_main_m}
C {devices/sg13_lv_nmos_np.sym} 2090 780 0 0 {name=M12_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_opamp_rrl_w l=x_dut_xm12_opamp_rrl_l m=x_dut_xm12_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1470 520 0 1 {name=M13_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_main_w l=x_dut_xm13_main_l m=x_dut_xm13_main_m}
C {devices/sg13_lv_nmos_np.sym} 215 1040 0 1 {name=M13_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_opamp_rrl_w l=x_dut_xm13_opamp_rrl_l m=x_dut_xm13_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1780 260 0 1 {name=M14_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_main_w l=x_dut_xm14_main_l m=x_dut_xm14_main_m}
C {devices/sg13_lv_nmos_np.sym} 2090 1040 0 0 {name=M14_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_opamp_rrl_w l=x_dut_xm14_opamp_rrl_l m=x_dut_xm14_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2080 260 0 1 {name=M15_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_main_w l=x_dut_xm15_main_l m=x_dut_xm15_main_m}
C {devices/sg13_lv_nmos_np.sym} 985 520 0 0 {name=M15_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_opamp_rrl_w l=x_dut_xm15_opamp_rrl_l m=x_dut_xm15_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1745 520 0 1 {name=M16_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_main_w l=x_dut_xm16_main_l m=x_dut_xm16_main_m}
C {devices/sg13_lv_nmos_np.sym} 4585 520 0 1 {name=M16_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_opamp_rrl_w l=x_dut_xm16_opamp_rrl_l m=x_dut_xm16_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2010 520 0 1 {name=M17_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_main_w l=x_dut_xm17_main_l m=x_dut_xm17_main_m}
C {devices/sg13_lv_nmos_np.sym} 7440 520 0 0 {name=M18_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_main_w l=x_dut_xm18_main_l m=x_dut_xm18_main_m}
C {devices/sg13_lv_pmos_np.sym} 7705 520 0 0 {name=M19_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_main_w l=x_dut_xm19_main_l m=x_dut_xm19_main_m}
C {devices/sg13_lv_nmos_np.sym} 2625 780 0 1 {name=M1_CHRRL_1_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_1_rrl_w l=x_dut_xm1_chrrl_1_rrl_l m=x_dut_xm1_chrrl_1_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 845 780 0 1 {name=M1_CHRRL_2_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_2_rrl_w l=x_dut_xm1_chrrl_2_rrl_l m=x_dut_xm1_chrrl_2_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2940 780 0 1 {name=M1_CHRRL_3_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_3_rrl_w l=x_dut_xm1_chrrl_3_rrl_l m=x_dut_xm1_chrrl_3_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 530 780 0 1 {name=M1_CHRRL_4_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_4_rrl_w l=x_dut_xm1_chrrl_4_rrl_l m=x_dut_xm1_chrrl_4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1780 0 0 1 {name=M1_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_main_w l=x_dut_xm1_main_l m=x_dut_xm1_main_m}
C {devices/sg13_lv_pmos_np.sym} 3220 0 0 0 {name=M1_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_opamp_rrl_w l=x_dut_xm1_opamp_rrl_l m=x_dut_xm1_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1480 1040 0 1 {name=M1_S1_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s1_rrl_w l=x_dut_xm1_s1_rrl_l m=x_dut_xm1_s1_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1120 1040 0 1 {name=M1_S2_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s2_rrl_w l=x_dut_xm1_s2_rrl_l m=x_dut_xm1_s2_rrl_m}
C {devices/sg13_lv_nmos_np.sym} -795 520 0 1 {name=M1_S3_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s3_rrl_w l=x_dut_xm1_s3_rrl_l m=x_dut_xm1_s3_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2285 520 0 1 {name=M1_S4_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s4_rrl_w l=x_dut_xm1_s4_rrl_l m=x_dut_xm1_s4_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 3210 780 0 1 {name=M1_S5_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s5_rrl_w l=x_dut_xm1_s5_rrl_l m=x_dut_xm1_s5_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1470 780 0 1 {name=M1_S6_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s6_rrl_w l=x_dut_xm1_s6_rrl_l m=x_dut_xm1_s6_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 3480 780 0 1 {name=M20_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_main_w l=x_dut_xm20_main_l m=x_dut_xm20_main_m}
C {devices/sg13_lv_pmos_np.sym} 3775 780 0 1 {name=M21_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_main_w l=x_dut_xm21_main_l m=x_dut_xm21_main_m}
C {devices/sg13_lv_nmos_np.sym} -190 780 0 1 {name=M22_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_main_w l=x_dut_xm22_main_l m=x_dut_xm22_main_m}
C {devices/sg13_lv_pmos_np.sym} 4070 780 0 1 {name=M23_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_main_w l=x_dut_xm23_main_l m=x_dut_xm23_main_m}
C {devices/sg13_lv_nmos_np.sym} 4900 520 0 1 {name=M24_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_main_w l=x_dut_xm24_main_l m=x_dut_xm24_main_m}
C {devices/sg13_lv_pmos_np.sym} -1110 520 0 1 {name=M25_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm25_main_w l=x_dut_xm25_main_l m=x_dut_xm25_main_m}
C {devices/sg13_lv_nmos_np.sym} 5165 520 0 1 {name=M26_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm26_main_w l=x_dut_xm26_main_l m=x_dut_xm26_main_m}
C {devices/sg13_lv_pmos_np.sym} -1385 520 0 1 {name=M27_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm27_main_w l=x_dut_xm27_main_l m=x_dut_xm27_main_m}
C {devices/sg13_lv_nmos_np.sym} 2550 520 0 1 {name=M28_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm28_main_w l=x_dut_xm28_main_l m=x_dut_xm28_main_m}
C {devices/sg13_lv_pmos_np.sym} 290 520 0 1 {name=M29_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm29_main_w l=x_dut_xm29_main_l m=x_dut_xm29_main_m}
C {devices/sg13_lv_pmos_np.sym} -480 780 0 1 {name=M2_CHRRL_1_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_1_rrl_w l=x_dut_xm2_chrrl_1_rrl_l m=x_dut_xm2_chrrl_1_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 4585 780 0 1 {name=M2_CHRRL_2_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_2_rrl_w l=x_dut_xm2_chrrl_2_rrl_l m=x_dut_xm2_chrrl_2_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -795 780 0 1 {name=M2_CHRRL_3_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_3_rrl_w l=x_dut_xm2_chrrl_3_rrl_l m=x_dut_xm2_chrrl_3_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 4900 780 0 1 {name=M2_CHRRL_4_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_4_rrl_w l=x_dut_xm2_chrrl_4_rrl_l m=x_dut_xm2_chrrl_4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2370 260 0 1 {name=M2_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_main_w l=x_dut_xm2_main_l m=x_dut_xm2_main_m}
C {devices/sg13_lv_pmos_np.sym} 3260 260 0 0 {name=M2_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_rrl_w l=x_dut_xm2_opamp_rrl_l m=x_dut_xm2_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2625 1040 0 1 {name=M2_S1_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s1_rrl_w l=x_dut_xm2_s1_rrl_l m=x_dut_xm2_s1_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 845 1040 0 1 {name=M2_S2_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s2_rrl_w l=x_dut_xm2_s2_rrl_l m=x_dut_xm2_s2_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 5440 520 0 1 {name=M2_S3_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s3_rrl_w l=x_dut_xm2_s3_rrl_l m=x_dut_xm2_s3_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2825 520 0 1 {name=M2_S4_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s4_rrl_w l=x_dut_xm2_s4_rrl_l m=x_dut_xm2_s4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -1110 780 0 1 {name=M2_S5_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s5_rrl_w l=x_dut_xm2_s5_rrl_l m=x_dut_xm2_s5_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1745 780 0 1 {name=M2_S6_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s6_rrl_w l=x_dut_xm2_s6_rrl_l m=x_dut_xm2_s6_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 7970 520 0 0 {name=M30_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm30_main_w l=x_dut_xm30_main_l m=x_dut_xm30_main_m}
C {devices/sg13_lv_pmos_np.sym} 8235 520 0 0 {name=M31_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm31_main_w l=x_dut_xm31_main_l m=x_dut_xm31_main_m}
C {devices/sg13_lv_nmos_np.sym} -1650 520 0 1 {name=M32_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm32_main_w l=x_dut_xm32_main_l m=x_dut_xm32_main_m}
C {devices/sg13_lv_pmos_np.sym} 5705 520 0 1 {name=M33_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm33_main_w l=x_dut_xm33_main_l m=x_dut_xm33_main_m}
C {devices/sg13_lv_nmos_np.sym} -1915 520 0 1 {name=M34_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm34_main_w l=x_dut_xm34_main_l m=x_dut_xm34_main_m}
C {devices/sg13_lv_pmos_np.sym} 5970 520 0 1 {name=M35_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm35_main_w l=x_dut_xm35_main_l m=x_dut_xm35_main_m}
C {devices/sg13_lv_nmos_np.sym} 5165 780 0 1 {name=M36_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm36_main_w l=x_dut_xm36_main_l m=x_dut_xm36_main_m}
C {devices/sg13_lv_pmos_np.sym} -1385 780 0 1 {name=M37_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm37_main_w l=x_dut_xm37_main_l m=x_dut_xm37_main_m}
C {devices/sg13_lv_nmos_np.sym} 5440 780 0 1 {name=M38_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm38_main_w l=x_dut_xm38_main_l m=x_dut_xm38_main_m}
C {devices/sg13_lv_pmos_np.sym} -1650 780 0 1 {name=M39_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm39_main_w l=x_dut_xm39_main_l m=x_dut_xm39_main_m}
C {devices/sg13_lv_pmos_np.sym} 365 260 0 1 {name=M3_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_main_w l=x_dut_xm3_main_l m=x_dut_xm3_main_m}
C {devices/sg13_lv_pmos_np.sym} 660 260 0 1 {name=M3_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_rrl_w l=x_dut_xm3_opamp_rrl_l m=x_dut_xm3_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 5705 780 0 1 {name=M4_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_main_w l=x_dut_xm4_main_l m=x_dut_xm4_main_m}
C {devices/sg13_lv_pmos_np.sym} 2080 0 0 1 {name=M4_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_opamp_rrl_w l=x_dut_xm4_opamp_rrl_l m=x_dut_xm4_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} -1915 780 0 1 {name=M5_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_main_w l=x_dut_xm5_main_l m=x_dut_xm5_main_m}
C {devices/sg13_lv_pmos_np.sym} 105 260 0 1 {name=M5_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_opamp_rrl_w l=x_dut_xm5_opamp_rrl_l m=x_dut_xm5_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1470 0 0 1 {name=M6_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_main_w l=x_dut_xm6_main_l m=x_dut_xm6_main_m}
C {devices/sg13_lv_pmos_np.sym} 3775 260 0 1 {name=M6_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_opamp_rrl_w l=x_dut_xm6_opamp_rrl_l m=x_dut_xm6_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2670 0 0 0 {name=M7_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_main_w l=x_dut_xm7_main_l m=x_dut_xm7_main_m}
C {devices/sg13_lv_pmos_np.sym} -190 260 0 1 {name=M7_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_opamp_rrl_w l=x_dut_xm7_opamp_rrl_l m=x_dut_xm7_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2370 0 0 1 {name=M8_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_main_w l=x_dut_xm8_main_l m=x_dut_xm8_main_m}
C {devices/sg13_lv_pmos_np.sym} 4070 260 0 1 {name=M8_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_opamp_rrl_w l=x_dut_xm8_opamp_rrl_l m=x_dut_xm8_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 845 0 0 1 {name=M9_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_main_w l=x_dut_xm9_main_l m=x_dut_xm9_main_m}
C {devices/sg13_lv_pmos_np.sym} 3260 520 0 0 {name=M9_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_rrl_w l=x_dut_xm9_opamp_rrl_l m=x_dut_xm9_opamp_rrl_m}
N -3230 170 -3230 230 {}
N -3230 290 -3230 350 {}
N -3230 430 -3230 490 {}
N -3230 550 -3230 610 {}
N -3230 690 -3230 750 {}
N -3230 810 -3230 870 {}
N -3230 950 -3230 1010 {}
N -3230 1070 -3230 1130 {}
N -2890 -90 -2890 -30 {}
N -2890 30 -2890 90 {}
N -2890 170 -2890 230 {}
N -2890 290 -2890 350 {}
N -2890 430 -2890 490 {}
N -2890 550 -2890 610 {}
N -2890 690 -2890 750 {}
N -2890 810 -2890 870 {}
N -2890 950 -2890 1010 {}
N -2890 1070 -2890 1130 {}
N -2645 460 -2645 735 {}
N -2520 520 -2520 580 {}
N -2385 580 -2385 695 {}
N -2325 430 -2325 490 {}
N -2325 550 -2325 610 {}
N -1995 520 -1995 614 {}
N -1995 780 -1995 874 {}
N -1935 430 -1935 490 {}
N -1935 550 -1935 610 {}
N -1935 690 -1935 750 {}
N -1935 810 -1935 1180 {}
N -1730 520 -1730 614 {}
N -1730 780 -1730 874 {}
N -1670 430 -1670 490 {}
N -1670 550 -1670 610 {}
N -1670 690 -1670 750 {}
N -1670 810 -1670 870 {}
N -1465 520 -1465 614 {}
N -1465 780 -1465 874 {}
N -1405 430 -1405 490 {}
N -1405 550 -1405 610 {}
N -1405 690 -1405 750 {}
N -1405 810 -1405 870 {}
N -1190 520 -1190 614 {}
N -1190 780 -1190 874 {}
N -1130 430 -1130 490 {}
N -1130 550 -1130 610 {}
N -1130 690 -1130 750 {}
N -1130 810 -1130 870 {}
N -875 520 -875 614 {}
N -875 780 -875 874 {}
N -815 430 -815 490 {}
N -815 550 -815 610 {}
N -815 690 -815 750 {}
N -815 810 -815 870 {}
N -560 780 -560 874 {}
N -500 690 -500 750 {}
N -500 810 -500 870 {}
N -480 430 -480 490 {}
N -480 550 -480 610 {}
N -270 260 -270 354 {}
N -270 780 -270 874 {}
N -210 200 -210 230 {}
N -210 290 -210 350 {}
N -210 690 -210 750 {}
N -210 810 -210 870 {}
N -190 430 -190 490 {}
N -190 550 -190 610 {}
N 25 260 25 354 {}
N 85 200 85 230 {}
N 85 290 85 320 {}
N 135 780 135 874 {}
N 135 1040 135 1134 {}
N 195 690 195 750 {}
N 195 810 195 870 {}
N 195 950 195 1010 {}
N 195 1070 195 1180 {}
N 210 520 210 614 {}
N 235 1040 235 1100 {}
N 270 430 270 490 {}
N 270 550 270 610 {}
N 285 260 285 354 {}
N 345 170 345 230 {}
N 345 290 345 350 {}
N 450 780 450 874 {}
N 510 690 510 750 {}
N 510 810 510 870 {}
N 580 290 580 490 {}
N 580 520 580 614 {}
N 640 170 640 230 {}
N 640 290 640 350 {}
N 640 550 640 610 {}
N 710 460 710 520 {}
N 765 0 765 94 {}
N 765 710 765 810 {}
N 765 1040 765 1134 {}
N 825 -140 825 -30 {}
N 825 30 825 90 {}
N 825 950 825 1010 {}
N 825 1070 825 1180 {}
N 865 780 865 840 {}
N 870 60 870 620 {}
N 870 680 870 710 {}
N 965 450 965 520 {}
N 1005 430 1005 490 {}
N 1005 550 1005 1180 {}
N 1040 1040 1040 1134 {}
N 1065 520 1065 614 {}
N 1100 980 1100 1010 {}
N 1100 1070 1100 1180 {}
N 1130 940 1130 970 {}
N 1170 980 1170 1040 {}
N 1390 0 1390 94 {}
N 1390 260 1390 354 {}
N 1390 520 1390 614 {}
N 1400 1040 1400 1134 {}
N 1450 -140 1450 -30 {}
N 1450 30 1450 90 {}
N 1450 170 1450 230 {}
N 1450 290 1450 350 {}
N 1450 430 1450 490 {}
N 1450 550 1450 610 {}
N 1450 690 1450 750 {}
N 1450 810 1450 870 {}
N 1460 950 1460 1010 {}
N 1460 1070 1460 1180 {}
N 1480 590 1480 620 {}
N 1480 680 1480 710 {}
N 1530 980 1530 1040 {}
N 1665 520 1665 614 {}
N 1665 810 1665 1100 {}
N 1700 0 1700 94 {}
N 1700 260 1700 354 {}
N 1720 940 1720 1010 {}
N 1725 430 1725 490 {}
N 1725 550 1725 610 {}
N 1760 -140 1760 -30 {}
N 1760 30 1760 90 {}
N 1760 170 1760 230 {}
N 1760 290 1760 1180 {}
N 1780 560 1780 620 {}
N 1780 680 1780 740 {}
N 1780 850 1780 880 {}
N 1780 1070 1780 1100 {}
N 1790 625 1790 685 {}
N 1790 745 1790 805 {}
N 1795 330 1795 360 {}
N 1795 420 1795 450 {}
N 1840 590 1840 850 {}
N 1930 520 1930 614 {}
N 1990 430 1990 490 {}
N 1990 550 1990 610 {}
N 2000 60 2000 200 {}
N 2000 260 2000 354 {}
N 2060 -140 2060 -30 {}
N 2060 30 2060 60 {}
N 2060 60 2060 90 {}
N 2060 170 2060 230 {}
N 2060 290 2060 350 {}
N 2080 560 2080 620 {}
N 2080 680 2080 740 {}
N 2080 820 2080 880 {}
N 2080 940 2080 1000 {}
N 2105 330 2105 360 {}
N 2105 390 2105 480 {}
N 2110 690 2110 750 {}
N 2110 810 2110 870 {}
N 2110 950 2110 1010 {}
N 2110 1070 2110 1180 {}
N 2120 60 2120 200 {}
N 2170 780 2170 874 {}
N 2170 1040 2170 1134 {}
N 2205 520 2205 614 {}
N 2265 430 2265 490 {}
N 2265 550 2265 610 {}
N 2290 0 2290 94 {}
N 2290 260 2290 354 {}
N 2350 -140 2350 -30 {}
N 2350 30 2350 90 {}
N 2350 170 2350 230 {}
N 2350 290 2350 350 {}
N 2370 560 2370 620 {}
N 2370 680 2370 740 {}
N 2380 820 2380 880 {}
N 2380 940 2380 1000 {}
N 2470 520 2470 614 {}
N 2530 430 2530 490 {}
N 2530 550 2530 610 {}
N 2545 780 2545 874 {}
N 2545 1040 2545 1134 {}
N 2605 690 2605 750 {}
N 2605 810 2605 870 {}
N 2605 950 2605 1010 {}
N 2605 1070 2605 1180 {}
N 2665 60 2665 620 {}
N 2665 680 2665 740 {}
N 2690 -140 2690 -30 {}
N 2690 30 2690 90 {}
N 2690 290 2690 350 {}
N 2745 520 2745 614 {}
N 2750 60 2750 230 {}
N 2750 260 2750 354 {}
N 2805 430 2805 490 {}
N 2805 550 2805 610 {}
N 2860 780 2860 874 {}
N 2920 690 2920 750 {}
N 2920 810 2920 870 {}
N 2975 980 2975 1010 {}
N 2975 1070 2975 1100 {}
N 3130 780 3130 874 {}
N 3190 690 3190 750 {}
N 3190 810 3190 870 {}
N 3240 -140 3240 -30 {}
N 3240 30 3240 90 {}
N 3240 460 3240 520 {}
N 3260 780 3260 1040 {}
N 3280 170 3280 230 {}
N 3280 290 3280 350 {}
N 3280 430 3280 490 {}
N 3280 550 3280 610 {}
N 3300 0 3300 94 {}
N 3340 260 3340 354 {}
N 3340 520 3340 614 {}
N 3400 780 3400 874 {}
N 3460 690 3460 750 {}
N 3460 810 3460 870 {}
N 3695 260 3695 354 {}
N 3695 780 3695 874 {}
N 3755 200 3755 230 {}
N 3755 290 3755 350 {}
N 3755 690 3755 750 {}
N 3755 810 3755 870 {}
N 3775 430 3775 490 {}
N 3775 550 3775 610 {}
N 3990 260 3990 354 {}
N 3990 780 3990 874 {}
N 4050 200 4050 230 {}
N 4050 290 4050 350 {}
N 4050 690 4050 750 {}
N 4050 810 4050 870 {}
N 4070 430 4070 490 {}
N 4070 550 4070 610 {}
N 4505 520 4505 614 {}
N 4505 780 4505 874 {}
N 4565 430 4565 490 {}
N 4565 550 4565 610 {}
N 4565 690 4565 750 {}
N 4565 810 4565 870 {}
N 4605 450 4605 520 {}
N 4820 520 4820 614 {}
N 4820 780 4820 874 {}
N 4880 430 4880 490 {}
N 4880 550 4880 610 {}
N 4880 690 4880 750 {}
N 4880 810 4880 870 {}
N 5085 520 5085 614 {}
N 5085 780 5085 874 {}
N 5145 430 5145 490 {}
N 5145 550 5145 610 {}
N 5145 690 5145 750 {}
N 5145 810 5145 870 {}
N 5360 520 5360 614 {}
N 5360 780 5360 874 {}
N 5420 430 5420 490 {}
N 5420 550 5420 610 {}
N 5420 690 5420 750 {}
N 5420 810 5420 840 {}
N 5625 520 5625 614 {}
N 5625 780 5625 874 {}
N 5685 430 5685 490 {}
N 5685 550 5685 610 {}
N 5685 720 5685 750 {}
N 5685 810 5685 1180 {}
N 5755 460 5755 520 {}
N 5890 520 5890 614 {}
N 5950 430 5950 490 {}
N 5950 550 5950 610 {}
N 5960 680 5960 740 {}
N 6000 680 6000 980 {}
N 6020 460 6020 520 {}
N 6140 390 6140 490 {}
N 6200 550 6200 695 {}
N 6365 430 6365 490 {}
N 6365 550 6365 610 {}
N 6655 430 6655 490 {}
N 6655 550 6655 610 {}
N 7005 400 7005 520 {}
N 7065 520 7065 780 {}
N 7190 400 7190 490 {}
N 7190 550 7190 610 {}
N 7250 550 7250 720 {}
N 7460 460 7460 490 {}
N 7460 550 7460 610 {}
N 7520 520 7520 614 {}
N 7725 460 7725 490 {}
N 7725 550 7725 610 {}
N 7785 520 7785 614 {}
N 7990 460 7990 490 {}
N 7990 550 7990 610 {}
N 8050 520 8050 614 {}
N 8255 460 8255 490 {}
N 8255 550 8255 580 {}
N 8315 520 8315 614 {}
N -3290 -140 8855 -140 {}
N 765 0 825 0 {}
N 865 0 895 0 {}
N 1390 0 1450 0 {}
N 1490 0 1550 0 {}
N 1700 0 1760 0 {}
N 1800 0 1860 0 {}
N 2100 0 2160 0 {}
N 2290 0 2350 0 {}
N 2390 0 2650 0 {}
N 3140 0 3200 0 {}
N 3240 0 3300 0 {}
N 825 60 870 60 {}
N 2000 60 2120 60 {}
N 2350 60 2665 60 {}
N 2690 60 2750 60 {}
N -210 200 4050 200 {}
N 2690 230 2750 230 {}
N -270 260 -210 260 {}
N -170 260 -110 260 {}
N 25 260 85 260 {}
N 125 260 185 260 {}
N 285 260 345 260 {}
N 385 260 445 260 {}
N 680 260 740 260 {}
N 1390 260 1450 260 {}
N 1490 260 1550 260 {}
N 1700 260 1760 260 {}
N 1800 260 1860 260 {}
N 2000 260 2060 260 {}
N 2100 260 2160 260 {}
N 2290 260 2350 260 {}
N 2390 260 2450 260 {}
N 2590 260 2650 260 {}
N 2690 260 2750 260 {}
N 3180 260 3240 260 {}
N 3280 260 3340 260 {}
N 3695 260 3755 260 {}
N 3795 260 3855 260 {}
N 3990 260 4050 260 {}
N 4090 260 4150 260 {}
N 580 290 640 290 {}
N -210 320 85 320 {}
N 1735 360 1795 360 {}
N 2105 390 6140 390 {}
N 7005 400 7190 400 {}
N 1735 420 1795 420 {}
N 965 450 1005 450 {}
N 4565 450 4605 450 {}
N -2645 460 -2325 460 {}
N 710 460 3240 460 {}
N 5755 460 6020 460 {}
N 7190 460 8255 460 {}
N 580 490 640 490 {}
N -2610 520 -2580 520 {}
N -2520 520 -2490 520 {}
N -1995 520 -1935 520 {}
N -1895 520 -1865 520 {}
N -1730 520 -1670 520 {}
N -1630 520 -1570 520 {}
N -1465 520 -1405 520 {}
N -1365 520 -1305 520 {}
N -1190 520 -1130 520 {}
N -1090 520 -1030 520 {}
N -875 520 -815 520 {}
N -775 520 -715 520 {}
N 210 520 270 520 {}
N 310 520 370 520 {}
N 580 520 640 520 {}
N 680 520 740 520 {}
N 1005 520 1065 520 {}
N 1390 520 1450 520 {}
N 1490 520 1550 520 {}
N 1665 520 1725 520 {}
N 1765 520 1825 520 {}
N 1930 520 1990 520 {}
N 2030 520 2090 520 {}
N 2205 520 2265 520 {}
N 2305 520 2365 520 {}
N 2470 520 2530 520 {}
N 2570 520 2630 520 {}
N 2745 520 2805 520 {}
N 2845 520 2905 520 {}
N 3280 520 3340 520 {}
N 4505 520 4565 520 {}
N 4820 520 4880 520 {}
N 4920 520 4950 520 {}
N 5085 520 5145 520 {}
N 5185 520 5245 520 {}
N 5360 520 5420 520 {}
N 5460 520 5520 520 {}
N 5625 520 5685 520 {}
N 5725 520 5785 520 {}
N 5890 520 5950 520 {}
N 5990 520 6020 520 {}
N 6855 520 6915 520 {}
N 6975 520 7065 520 {}
N 7090 520 7150 520 {}
N 7360 520 7420 520 {}
N 7460 520 7520 520 {}
N 7625 520 7685 520 {}
N 7725 520 7785 520 {}
N 7890 520 7950 520 {}
N 7990 520 8050 520 {}
N 8155 520 8215 520 {}
N 8255 520 8315 520 {}
N 6140 550 6200 550 {}
N 7190 550 7250 550 {}
N -2385 580 -2325 580 {}
N 7990 580 8255 580 {}
N 1780 590 1840 590 {}
N 1420 620 1480 620 {}
N 810 680 870 680 {}
N 1420 680 1480 680 {}
N -2385 695 6200 695 {}
N 765 710 870 710 {}
N 5685 720 7250 720 {}
N -2645 735 1750 735 {}
N 450 750 825 750 {}
N 1390 750 1725 750 {}
N -1995 780 -1935 780 {}
N -1895 780 -1835 780 {}
N -1730 780 -1670 780 {}
N -1630 780 -1600 780 {}
N -1465 780 -1405 780 {}
N -1365 780 -1305 780 {}
N -1190 780 -1130 780 {}
N -1090 780 -1060 780 {}
N -875 780 -815 780 {}
N -775 780 -745 780 {}
N -560 780 -500 780 {}
N -460 780 -430 780 {}
N -270 780 -210 780 {}
N -170 780 -110 780 {}
N 135 780 195 780 {}
N 235 780 295 780 {}
N 450 780 510 780 {}
N 550 780 610 780 {}
N 865 780 895 780 {}
N 1490 780 1550 780 {}
N 1765 780 1825 780 {}
N 2010 780 2070 780 {}
N 2110 780 2170 780 {}
N 2545 780 2605 780 {}
N 2645 780 2705 780 {}
N 2860 780 2920 780 {}
N 2960 780 3020 780 {}
N 3130 780 3190 780 {}
N 3230 780 3290 780 {}
N 3400 780 3460 780 {}
N 3500 780 3560 780 {}
N 3695 780 3755 780 {}
N 3795 780 3825 780 {}
N 3990 780 4050 780 {}
N 4090 780 4150 780 {}
N 4505 780 4565 780 {}
N 4605 780 4665 780 {}
N 4820 780 4880 780 {}
N 4920 780 4980 780 {}
N 5085 780 5145 780 {}
N 5185 780 5245 780 {}
N 5360 780 5420 780 {}
N 5460 780 5520 780 {}
N 5625 780 5685 780 {}
N 5725 780 5785 780 {}
N 5890 780 5950 780 {}
N 6010 780 7065 780 {}
N 765 810 825 810 {}
N 1390 810 1725 810 {}
N 1780 850 1840 850 {}
N 1070 880 1130 880 {}
N 1070 940 1130 940 {}
N 1720 940 1780 940 {}
N 825 980 1100 980 {}
N 1170 980 1530 980 {}
N 1720 980 6000 980 {}
N 1720 1010 1780 1010 {}
N 135 1040 195 1040 {}
N 235 1040 265 1040 {}
N 765 1040 825 1040 {}
N 865 1040 895 1040 {}
N 1040 1040 1100 1040 {}
N 1140 1040 1200 1040 {}
N 1400 1040 1460 1040 {}
N 1500 1040 1530 1040 {}
N 2010 1040 2070 1040 {}
N 2110 1040 2170 1040 {}
N 2545 1040 2605 1040 {}
N 2645 1040 3260 1040 {}
N 1665 1100 2975 1100 {}
N -3290 1180 8855 1180 {}
C {devices/lab_wire.sym} -1305 780 0 1 {name=l0 lab=clk_chfb}
C {devices/lab_wire.sym} -110 780 0 1 {name=l1 lab=clk_chfb}
C {devices/lab_wire.sym} 3560 780 0 1 {name=l2 lab=clk_chfb}
C {devices/lab_wire.sym} 4150 780 0 1 {name=l3 lab=clk_chfb_not}
C {devices/lab_wire.sym} 5245 780 0 1 {name=l4 lab=clk_chfb_not}
C {devices/lab_wire.sym} 5520 780 0 1 {name=l5 lab=clk_chfb_not}
C {devices/lab_wire.sym} 5245 520 0 1 {name=l6 lab=clk_chin}
C {devices/lab_wire.sym} 5785 520 0 1 {name=l7 lab=clk_chin}
C {devices/lab_wire.sym} -1570 520 0 1 {name=l8 lab=clk_chin_not}
C {devices/lab_wire.sym} -1305 520 0 1 {name=l9 lab=clk_chin_not}
C {devices/lab_wire.sym} -1030 520 0 1 {name=l10 lab=clk_chin_not}
C {devices/lab_wire.sym} 370 520 0 1 {name=l11 lab=clk_chout}
C {devices/lab_wire.sym} 865 840 2 0 {name=l12 lab=clk_chout}
C {devices/lab_wire.sym} 1825 520 0 1 {name=l13 lab=clk_chout}
C {devices/lab_wire.sym} 2705 780 0 1 {name=l14 lab=clk_chout}
C {devices/lab_wire.sym} 4980 780 0 1 {name=l15 lab=clk_chout}
C {devices/lab_wire.sym} 7360 520 0 0 {name=l16 lab=clk_chout}
C {devices/lab_wire.sym} 8155 520 0 0 {name=l17 lab=clk_chout}
C {devices/lab_wire.sym} 610 780 0 1 {name=l18 lab=clk_chout_not}
C {devices/lab_wire.sym} 2090 520 0 1 {name=l19 lab=clk_chout_not}
C {devices/lab_wire.sym} 2630 520 0 1 {name=l20 lab=clk_chout_not}
C {devices/lab_wire.sym} 3020 780 0 1 {name=l21 lab=clk_chout_not}
C {devices/lab_wire.sym} 4665 780 0 1 {name=l22 lab=clk_chout_not}
C {devices/lab_wire.sym} 7625 520 0 0 {name=l23 lab=clk_chout_not}
C {devices/lab_wire.sym} 7890 520 0 0 {name=l24 lab=clk_chout_not}
C {devices/lab_wire.sym} 1550 780 0 1 {name=l25 lab=clk_phi_1}
C {devices/lab_wire.sym} 3290 780 0 1 {name=l26 lab=clk_phi_1}
C {devices/lab_wire.sym} 2905 520 0 1 {name=l27 lab=clk_phi_1}
C {devices/lab_wire.sym} 5520 520 0 1 {name=l28 lab=clk_phi_1}
C {devices/lab_wire.sym} -715 520 0 1 {name=l29 lab=clk_phi_2}
C {devices/lab_wire.sym} 1200 1040 0 1 {name=l30 lab=clk_phi_2}
C {devices/lab_wire.sym} 1825 780 0 1 {name=l31 lab=clk_phi_2}
C {devices/lab_wire.sym} 2365 520 0 1 {name=l32 lab=clk_phi_2}
C {devices/lab_wire.sym} -2325 430 0 1 {name=l33 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 1735 360 0 0 {name=l34 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 2105 480 2 0 {name=l35 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 1450 90 2 0 {name=l36 lab=main__casc_src_n}
C {devices/lab_wire.sym} 1450 170 0 1 {name=l37 lab=main__casc_src_n}
C {devices/lab_wire.sym} 2690 90 2 0 {name=l38 lab=main__casc_src_p}
C {devices/lab_wire.sym} -1670 690 0 1 {name=l39 lab=main__fbch_n}
C {devices/lab_wire.sym} -210 690 0 1 {name=l40 lab=main__fbch_n}
C {devices/lab_wire.sym} 2370 560 0 1 {name=l41 lab=main__fbch_n}
C {devices/lab_wire.sym} 4050 690 0 1 {name=l42 lab=main__fbch_n}
C {devices/lab_wire.sym} 5420 690 0 1 {name=l43 lab=main__fbch_n}
C {devices/lab_wire.sym} -1405 690 0 1 {name=l44 lab=main__fbch_p}
C {devices/lab_wire.sym} 1420 620 0 0 {name=l45 lab=main__fbch_p}
C {devices/lab_wire.sym} 3460 690 0 1 {name=l46 lab=main__fbch_p}
C {devices/lab_wire.sym} 3755 690 0 1 {name=l47 lab=main__fbch_p}
C {devices/lab_wire.sym} 5145 690 0 1 {name=l48 lab=main__fbch_p}
C {devices/lab_wire.sym} -1935 690 0 1 {name=l49 lab=main__fold_n}
C {devices/lab_wire.sym} 345 350 2 0 {name=l50 lab=main__fold_n}
C {devices/lab_wire.sym} 1450 610 2 0 {name=l51 lab=main__fold_n}
C {devices/lab_wire.sym} 2350 350 2 0 {name=l52 lab=main__fold_p}
C {devices/lab_wire.sym} 7190 610 2 0 {name=l53 lab=main__fold_p}
C {devices/lab_wire.sym} 1725 610 2 0 {name=l54 lab=main__g2_n}
C {devices/lab_wire.sym} 1990 610 2 0 {name=l55 lab=main__g2_n}
C {devices/lab_wire.sym} 2160 260 0 1 {name=l56 lab=main__g2_n}
C {devices/lab_wire.sym} 6655 430 0 1 {name=l57 lab=main__g2_n}
C {devices/lab_wire.sym} 7990 610 2 0 {name=l58 lab=main__g2_n}
C {devices/lab_wire.sym} 270 610 2 0 {name=l59 lab=main__g2_p}
C {devices/lab_wire.sym} 1860 260 0 1 {name=l60 lab=main__g2_p}
C {devices/lab_wire.sym} 2530 610 2 0 {name=l61 lab=main__g2_p}
C {devices/lab_wire.sym} 6365 430 0 1 {name=l62 lab=main__g2_p}
C {devices/lab_wire.sym} 7460 610 2 0 {name=l63 lab=main__g2_p}
C {devices/lab_wire.sym} 7725 610 2 0 {name=l64 lab=main__g2_p}
C {devices/lab_wire.sym} -1935 610 2 0 {name=l65 lab=main__inch_n}
C {devices/lab_wire.sym} -1130 610 2 0 {name=l66 lab=main__inch_n}
C {devices/lab_wire.sym} 3775 610 2 0 {name=l67 lab=main__inch_n}
C {devices/lab_wire.sym} 4880 610 2 0 {name=l68 lab=main__inch_n}
C {devices/lab_wire.sym} 5950 610 2 0 {name=l69 lab=main__inch_n}
C {devices/lab_wire.sym} -1670 610 2 0 {name=l70 lab=main__inch_p}
C {devices/lab_wire.sym} -1405 610 2 0 {name=l71 lab=main__inch_p}
C {devices/lab_wire.sym} -190 610 2 0 {name=l72 lab=main__inch_p}
C {devices/lab_wire.sym} 5145 610 2 0 {name=l73 lab=main__inch_p}
C {devices/lab_wire.sym} 5685 610 2 0 {name=l74 lab=main__inch_p}
C {devices/lab_wire.sym} 345 170 0 1 {name=l75 lab=main__tail}
C {devices/lab_wire.sym} 1760 90 2 0 {name=l76 lab=main__tail}
C {devices/lab_wire.sym} 2350 170 0 1 {name=l77 lab=main__tail}
C {devices/lab_wire.sym} -1835 780 0 1 {name=l78 lab=main__vb1}
C {devices/lab_wire.sym} 5785 780 0 1 {name=l79 lab=main__vb1}
C {devices/lab_wire.sym} 1550 520 0 1 {name=l80 lab=main__vb2}
C {devices/lab_wire.sym} 7090 520 0 0 {name=l81 lab=main__vb2}
C {devices/lab_wire.sym} 1550 260 0 1 {name=l82 lab=main__vb3}
C {devices/lab_wire.sym} 2590 260 0 0 {name=l83 lab=main__vb3}
C {devices/lab_wire.sym} 445 260 0 1 {name=l84 lab=main__vsum_n}
C {devices/lab_wire.sym} 1420 680 0 0 {name=l85 lab=main__vsum_n}
C {devices/lab_wire.sym} 3775 430 0 1 {name=l86 lab=main__vsum_n}
C {devices/lab_wire.sym} 4070 430 0 1 {name=l87 lab=main__vsum_n}
C {devices/lab_wire.sym} -480 430 0 1 {name=l88 lab=main__vsum_p}
C {devices/lab_wire.sym} -190 430 0 1 {name=l89 lab=main__vsum_p}
C {devices/lab_wire.sym} 2370 740 2 0 {name=l90 lab=main__vsum_p}
C {devices/lab_wire.sym} 2450 260 0 1 {name=l91 lab=main__vsum_p}
C {devices/lab_wire.sym} -2580 520 0 0 {name=l92 lab=out1_n}
C {devices/lab_wire.sym} 270 430 0 1 {name=l93 lab=out1_n}
C {devices/lab_wire.sym} 1450 350 2 0 {name=l94 lab=out1_n}
C {devices/lab_wire.sym} 1450 430 0 1 {name=l95 lab=out1_n}
C {devices/lab_wire.sym} 1725 430 0 1 {name=l96 lab=out1_n}
C {devices/lab_wire.sym} 1990 430 0 1 {name=l97 lab=out1_n}
C {devices/lab_wire.sym} 2530 430 0 1 {name=l98 lab=out1_n}
C {devices/lab_wire.sym} 5890 780 0 0 {name=l99 lab=out1_n}
C {devices/lab_wire.sym} 6855 520 0 0 {name=l100 lab=out1_n}
C {devices/lab_wire.sym} -2520 580 2 0 {name=l101 lab=out1_p}
C {devices/lab_wire.sym} 2690 350 2 0 {name=l102 lab=out1_p}
C {devices/lab_wire.sym} 7190 430 0 1 {name=l103 lab=out1_p}
C {devices/lab_wire.sym} 1450 870 2 0 {name=l104 lab=rrl__int_n}
C {devices/lab_wire.sym} 2080 1000 2 0 {name=l105 lab=rrl__int_n}
C {devices/lab_wire.sym} 5960 680 0 1 {name=l106 lab=rrl__int_n}
C {devices/lab_wire.sym} -1130 870 2 0 {name=l107 lab=rrl__int_p}
C {devices/lab_wire.sym} 6000 680 0 1 {name=l108 lab=rrl__int_p}
C {devices/lab_wire.sym} 3190 870 2 0 {name=l109 lab=rrl__int_p}
C {devices/lab_wire.sym} 235 1100 2 0 {name=l110 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 1005 430 0 1 {name=l111 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 2010 1040 0 0 {name=l112 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 3755 350 2 0 {name=l113 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 4050 350 2 0 {name=l114 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} -210 350 2 0 {name=l115 lab=rrl__oa_cm_sense}
C {devices/lab_wire.sym} 4565 430 0 1 {name=l116 lab=rrl__oa_cm_sense}
C {devices/lab_wire.sym} 2060 90 2 0 {name=l117 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} 195 870 2 0 {name=l118 lab=rrl__oa_csrc_n}
C {devices/lab_wire.sym} 195 950 0 1 {name=l119 lab=rrl__oa_csrc_n}
C {devices/lab_wire.sym} 2110 870 2 0 {name=l120 lab=rrl__oa_csrc_p}
C {devices/lab_wire.sym} 2110 950 0 1 {name=l121 lab=rrl__oa_csrc_p}
C {devices/lab_wire.sym} 3280 350 2 0 {name=l122 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 3280 430 0 1 {name=l123 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 640 350 2 0 {name=l124 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} 740 260 0 1 {name=l125 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 2080 740 2 0 {name=l126 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 2265 430 0 1 {name=l127 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 2805 430 0 1 {name=l128 lab=rrl__oa_inn}
C {devices/lab_wire.sym} -815 430 0 1 {name=l129 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 1780 740 2 0 {name=l130 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 3180 260 0 0 {name=l131 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 5420 430 0 1 {name=l132 lab=rrl__oa_inp}
C {devices/lab_wire.sym} -1130 690 0 1 {name=l133 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -815 610 2 0 {name=l134 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 185 260 0 1 {name=l135 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 195 690 0 1 {name=l136 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 3190 690 0 1 {name=l137 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 3280 610 2 0 {name=l138 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 5420 610 2 0 {name=l139 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -110 260 0 1 {name=l140 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 640 610 2 0 {name=l141 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1450 690 0 1 {name=l142 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 2110 690 0 1 {name=l143 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 2265 610 2 0 {name=l144 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 2805 610 2 0 {name=l145 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 640 170 0 1 {name=l146 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 3240 90 2 0 {name=l147 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 3280 170 0 1 {name=l148 lab=rrl__oa_tail}
C {devices/lab_wire.sym} -815 870 2 0 {name=l149 lab=rrl__sc_n}
C {devices/lab_wire.sym} 810 680 0 0 {name=l150 lab=rrl__sc_n}
C {devices/lab_wire.sym} 1460 950 0 1 {name=l151 lab=rrl__sc_n}
C {devices/lab_wire.sym} 2605 950 0 1 {name=l152 lab=rrl__sc_n}
C {devices/lab_wire.sym} 2920 870 2 0 {name=l153 lab=rrl__sc_n}
C {devices/lab_wire.sym} 4565 870 2 0 {name=l154 lab=rrl__sc_n}
C {devices/lab_wire.sym} -500 870 2 0 {name=l155 lab=rrl__sc_p}
C {devices/lab_wire.sym} 510 870 2 0 {name=l156 lab=rrl__sc_p}
C {devices/lab_wire.sym} 825 950 0 1 {name=l157 lab=rrl__sc_p}
C {devices/lab_wire.sym} 2605 870 2 0 {name=l158 lab=rrl__sc_p}
C {devices/lab_wire.sym} 2665 740 2 0 {name=l159 lab=rrl__sc_p}
C {devices/lab_wire.sym} 4880 870 2 0 {name=l160 lab=rrl__sc_p}
C {devices/lab_wire.sym} 510 690 0 1 {name=l161 lab=rrl__sum_n}
C {devices/lab_wire.sym} 2080 560 0 1 {name=l162 lab=rrl__sum_n}
C {devices/lab_wire.sym} 2080 820 0 1 {name=l163 lab=rrl__sum_n}
C {devices/lab_wire.sym} 4565 690 0 1 {name=l164 lab=rrl__sum_n}
C {devices/lab_wire.sym} 4880 690 0 1 {name=l165 lab=rrl__sum_n}
C {devices/lab_wire.sym} -815 690 0 1 {name=l166 lab=rrl__sum_p}
C {devices/lab_wire.sym} -500 690 0 1 {name=l167 lab=rrl__sum_p}
C {devices/lab_wire.sym} 1780 560 0 1 {name=l168 lab=rrl__sum_p}
C {devices/lab_wire.sym} 2605 690 0 1 {name=l169 lab=rrl__sum_p}
C {devices/lab_wire.sym} 2920 690 0 1 {name=l170 lab=rrl__sum_p}
C {devices/lab_wire.sym} 740 520 0 1 {name=l171 lab=rrl__vb1}
C {devices/lab_wire.sym} 295 780 0 1 {name=l172 lab=rrl__vb2}
C {devices/lab_wire.sym} 2010 780 0 0 {name=l173 lab=rrl__vb2}
C {devices/lab_wire.sym} 2160 0 0 1 {name=l174 lab=rrl__vb3}
C {devices/lab_wire.sym} 3140 0 0 0 {name=l175 lab=rrl__vb3}
C {devices/lab_wire.sym} 3855 260 0 1 {name=l176 lab=rrl__vb4}
C {devices/lab_wire.sym} 4150 260 0 1 {name=l177 lab=rrl__vb4}
C {devices/lab_wire.sym} 865 0 0 0 {name=l178 lab=vb4_ctl}
C {devices/lab_wire.sym} 1550 0 0 1 {name=l179 lab=vb4_ctl}
C {devices/lab_wire.sym} 1860 0 0 1 {name=l180 lab=vb4_ctl}
C {devices/lab_wire.sym} 2450 0 0 1 {name=l181 lab=vb4_ctl}
C {devices/lab_wire.sym} 1070 940 0 0 {name=l182 lab=vcmfb_raw}
C {devices/lab_wire.sym} 1790 805 2 0 {name=l183 lab=vcmfb_raw}
C {devices/lab_wire.sym} 2380 1000 2 0 {name=l184 lab=vcmfb_raw}
C {devices/lab_wire.sym} -1670 430 0 1 {name=l185 lab=vinn}
C {devices/lab_wire.sym} -1130 430 0 1 {name=l186 lab=vinn}
C {devices/lab_wire.sym} 4880 430 0 1 {name=l187 lab=vinn}
C {devices/lab_wire.sym} 5685 430 0 1 {name=l188 lab=vinn}
C {devices/lab_wire.sym} -1935 430 0 1 {name=l189 lab=vinp}
C {devices/lab_wire.sym} -1405 430 0 1 {name=l190 lab=vinp}
C {devices/lab_wire.sym} 5145 430 0 1 {name=l191 lab=vinp}
C {devices/lab_wire.sym} 5950 430 0 1 {name=l192 lab=vinp}
C {devices/lab_wire.sym} -1405 870 2 0 {name=l193 lab=voutn}
C {devices/lab_wire.sym} -210 870 2 0 {name=l194 lab=voutn}
C {devices/lab_wire.sym} 825 90 2 0 {name=l195 lab=voutn}
C {devices/lab_wire.sym} 2060 170 0 1 {name=l196 lab=voutn}
C {devices/lab_wire.sym} 4050 870 2 0 {name=l197 lab=voutn}
C {devices/lab_wire.sym} 5145 870 2 0 {name=l198 lab=voutn}
C {devices/lab_wire.sym} 6655 610 2 0 {name=l199 lab=voutn}
C {devices/lab_wire.sym} -1670 870 2 0 {name=l200 lab=voutp}
C {devices/lab_wire.sym} 1760 170 0 1 {name=l201 lab=voutp}
C {devices/lab_wire.sym} 1735 420 0 0 {name=l202 lab=voutp}
C {devices/lab_wire.sym} 2350 90 2 0 {name=l203 lab=voutp}
C {devices/lab_wire.sym} 3460 870 2 0 {name=l204 lab=voutp}
C {devices/lab_wire.sym} 3755 870 2 0 {name=l205 lab=voutp}
C {devices/lab_wire.sym} 6365 610 2 0 {name=l206 lab=voutp}
C {devices/lab_wire.sym} -480 610 2 0 {name=l207 lab=vref}
C {devices/lab_wire.sym} 4070 610 2 0 {name=l208 lab=vref}
C {devices/lab_wire.sym} -2325 610 2 0 {name=l209 lab=vref_cm}
C {devices/lab_wire.sym} 1390 354 2 0 {name=l210 lab=vdd}
C {devices/lab_wire.sym} 580 614 2 0 {name=l211 lab=vdd}
C {devices/lab_wire.sym} 2750 354 2 0 {name=l212 lab=vdd}
C {devices/lab_wire.sym} 1930 614 2 0 {name=l213 lab=vdd}
C {devices/lab_wire.sym} 7785 614 2 0 {name=l214 lab=vdd}
C {devices/lab_wire.sym} 1700 94 2 0 {name=l215 lab=vdd}
C {devices/lab_wire.sym} 3300 94 2 0 {name=l216 lab=vdd}
C {devices/lab_wire.sym} 3695 874 2 0 {name=l217 lab=vdd}
C {devices/lab_wire.sym} 3990 874 2 0 {name=l218 lab=vdd}
C {devices/lab_wire.sym} -1190 614 2 0 {name=l219 lab=vdd}
C {devices/lab_wire.sym} -1465 614 2 0 {name=l220 lab=vdd}
C {devices/lab_wire.sym} 210 614 2 0 {name=l221 lab=vdd}
C {devices/lab_wire.sym} -560 874 2 0 {name=l222 lab=vdd}
C {devices/lab_wire.sym} 4505 874 2 0 {name=l223 lab=vdd}
C {devices/lab_wire.sym} -875 874 2 0 {name=l224 lab=vdd}
C {devices/lab_wire.sym} 4820 874 2 0 {name=l225 lab=vdd}
C {devices/lab_wire.sym} 2290 354 2 0 {name=l226 lab=vdd}
C {devices/lab_wire.sym} 3340 354 2 0 {name=l227 lab=vdd}
C {devices/lab_wire.sym} 2545 1134 2 0 {name=l228 lab=vdd}
C {devices/lab_wire.sym} 765 1134 2 0 {name=l229 lab=vdd}
C {devices/lab_wire.sym} 5360 614 2 0 {name=l230 lab=vdd}
C {devices/lab_wire.sym} 2745 614 2 0 {name=l231 lab=vdd}
C {devices/lab_wire.sym} -1190 874 2 0 {name=l232 lab=vdd}
C {devices/lab_wire.sym} 1725 780 0 0 {name=l233 lab=vdd}
C {devices/lab_wire.sym} 8315 614 2 0 {name=l234 lab=vdd}
C {devices/lab_wire.sym} 5625 614 2 0 {name=l235 lab=vdd}
C {devices/lab_wire.sym} 5890 614 2 0 {name=l236 lab=vdd}
C {devices/lab_wire.sym} -1465 874 2 0 {name=l237 lab=vdd}
C {devices/lab_wire.sym} -1730 874 2 0 {name=l238 lab=vdd}
C {devices/lab_wire.sym} 285 354 2 0 {name=l239 lab=vdd}
C {devices/lab_wire.sym} 640 260 0 0 {name=l240 lab=vdd}
C {devices/lab_wire.sym} 2060 0 0 0 {name=l241 lab=vdd}
C {devices/lab_wire.sym} 25 354 2 0 {name=l242 lab=vdd}
C {devices/lab_wire.sym} 1390 94 2 0 {name=l243 lab=vdd}
C {devices/lab_wire.sym} 3695 354 2 0 {name=l244 lab=vdd}
C {devices/lab_wire.sym} 2690 0 0 0 {name=l245 lab=vdd}
C {devices/lab_wire.sym} -270 354 2 0 {name=l246 lab=vdd}
C {devices/lab_wire.sym} 2290 94 2 0 {name=l247 lab=vdd}
C {devices/lab_wire.sym} 3990 354 2 0 {name=l248 lab=vdd}
C {devices/lab_wire.sym} 765 94 2 0 {name=l249 lab=vdd}
C {devices/lab_wire.sym} 3340 614 2 0 {name=l250 lab=vdd}
C {devices/lab_wire.sym} 135 874 2 0 {name=l251 lab=vss}
C {devices/lab_wire.sym} 7190 520 0 0 {name=l252 lab=vss}
C {devices/lab_wire.sym} 2170 874 2 0 {name=l253 lab=vss}
C {devices/lab_wire.sym} 1390 614 2 0 {name=l254 lab=vss}
C {devices/lab_wire.sym} 135 1134 2 0 {name=l255 lab=vss}
C {devices/lab_wire.sym} 1700 354 2 0 {name=l256 lab=vss}
C {devices/lab_wire.sym} 2170 1134 2 0 {name=l257 lab=vss}
C {devices/lab_wire.sym} 2000 354 2 0 {name=l258 lab=vss}
C {devices/lab_wire.sym} 1065 614 2 0 {name=l259 lab=vss}
C {devices/lab_wire.sym} 1665 614 2 0 {name=l260 lab=vss}
C {devices/lab_wire.sym} 4505 614 2 0 {name=l261 lab=vss}
C {devices/lab_wire.sym} 7520 614 2 0 {name=l262 lab=vss}
C {devices/lab_wire.sym} 2545 874 2 0 {name=l263 lab=vss}
C {devices/lab_wire.sym} 825 780 0 0 {name=l264 lab=vss}
C {devices/lab_wire.sym} 2860 874 2 0 {name=l265 lab=vss}
C {devices/lab_wire.sym} 450 874 2 0 {name=l266 lab=vss}
C {devices/lab_wire.sym} 1400 1134 2 0 {name=l267 lab=vss}
C {devices/lab_wire.sym} 1040 1134 2 0 {name=l268 lab=vss}
C {devices/lab_wire.sym} -875 614 2 0 {name=l269 lab=vss}
C {devices/lab_wire.sym} 2205 614 2 0 {name=l270 lab=vss}
C {devices/lab_wire.sym} 3130 874 2 0 {name=l271 lab=vss}
C {devices/lab_wire.sym} 1450 780 0 0 {name=l272 lab=vss}
C {devices/lab_wire.sym} 3400 874 2 0 {name=l273 lab=vss}
C {devices/lab_wire.sym} -270 874 2 0 {name=l274 lab=vss}
C {devices/lab_wire.sym} 4820 614 2 0 {name=l275 lab=vss}
C {devices/lab_wire.sym} 5085 614 2 0 {name=l276 lab=vss}
C {devices/lab_wire.sym} 2470 614 2 0 {name=l277 lab=vss}
C {devices/lab_wire.sym} 8050 614 2 0 {name=l278 lab=vss}
C {devices/lab_wire.sym} -1730 614 2 0 {name=l279 lab=vss}
C {devices/lab_wire.sym} -1995 614 2 0 {name=l280 lab=vss}
C {devices/lab_wire.sym} 5085 874 2 0 {name=l281 lab=vss}
C {devices/lab_wire.sym} 5360 874 2 0 {name=l282 lab=vss}
C {devices/lab_wire.sym} 5625 874 2 0 {name=l283 lab=vss}
C {devices/lab_wire.sym} -1995 874 2 0 {name=l284 lab=vss}
C {devices/lab_wire.sym} -3230 170 0 1 {name=l285 lab=vref_cm}
C {devices/lab_wire.sym} -2890 1130 2 0 {name=l286 lab=vss}
C {devices/lab_wire.sym} -2890 870 2 0 {name=l287 lab=vss}
C {devices/lab_wire.sym} -2890 610 2 0 {name=l288 lab=vss}
C {devices/lab_wire.sym} -2890 350 2 0 {name=l289 lab=vss}
C {devices/lab_wire.sym} -2890 90 2 0 {name=l290 lab=vss}
C {devices/lab_wire.sym} -3230 1130 2 0 {name=l291 lab=vss}
C {devices/lab_wire.sym} -3230 610 2 0 {name=l292 lab=vss}
C {devices/lab_wire.sym} -3230 350 2 0 {name=l293 lab=vss}
C {devices/lab_wire.sym} -3230 870 2 0 {name=l294 lab=vcmfb_raw}
C {devices/lab_wire.sym} -2890 950 0 1 {name=l295 lab=main__vb1}
C {devices/lab_wire.sym} -2890 690 0 1 {name=l296 lab=rrl__vb1}
C {devices/lab_wire.sym} -2890 430 0 1 {name=l297 lab=main__vb2}
C {devices/lab_wire.sym} -2890 170 0 1 {name=l298 lab=rrl__vb2}
C {devices/lab_wire.sym} -2890 -90 0 1 {name=l299 lab=main__vb3}
C {devices/lab_wire.sym} -3230 950 0 1 {name=l300 lab=rrl__vb3}
C {devices/lab_wire.sym} -3230 690 0 1 {name=l301 lab=vb4_ctl}
C {devices/lab_wire.sym} -3230 430 0 1 {name=l302 lab=rrl__vb4}
C {devices/lab_wire.sym} 2380 820 0 1 {name=l303 lab=vss}
C {devices/lab_wire.sym} 1790 625 0 1 {name=l304 lab=vss}
C {devices/lab_wire.sym} 1070 880 0 0 {name=l305 lab=vss}
C {devices/lab_wire.sym} 2060 350 2 0 {name=l306 lab=vss}
C {devices/lab_wire.sym} 4565 610 2 0 {name=l307 lab=vss}
C {devices/ipin.sym} -1865 520 0 0 {name=p0 lab=clk_chin_not}
C {devices/ipin.sym} -1060 780 0 0 {name=p1 lab=clk_phi_2}
C {devices/ipin.sym} -745 780 0 0 {name=p2 lab=clk_chout}
C {devices/ipin.sym} -430 780 0 0 {name=p3 lab=clk_chout_not}
C {devices/ipin.sym} 895 1040 0 0 {name=p4 lab=clk_phi_1}
C {devices/ipin.sym} 4950 520 0 0 {name=p5 lab=clk_chin}
C {devices/ipin.sym} -1600 780 0 0 {name=p6 lab=clk_chfb}
C {devices/ipin.sym} 3825 780 0 0 {name=p7 lab=clk_chfb_not}
C {devices/iopin.sym} -3290 -140 0 0 {name=p8 lab=vdd}
C {devices/iopin.sym} -3290 1180 0 0 {name=p9 lab=vss}
C {devices/opin.sym} 2105 330 0 0 {name=p10 lab=voutn}
C {devices/opin.sym} 5420 840 0 0 {name=p11 lab=voutp}
C {devices/iopin.sym} -480 1320 0 0 {name=p12 lab=vref}
C {devices/opin.sym} 8995 490 0 0 {name=p13 lab=vinp}
C {devices/opin.sym} 8995 610 0 0 {name=p14 lab=vinn}
B 8 -505 442 2810 1118 {fill=0}
T {NMOS Simple Current Mirror (2 outputs)} -505 424 0 0 0.3 0.3 {layer=8}
B 10 -60 182 3956 598 {fill=0}
T {PMOS Cascode Differential Pair Differential Pair} -60 164 0 0 0.3 0.3 {layer=10}
B 12 1145 442 2080 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1145 424 0 0 0.3 0.3 {layer=12}
B 21 7370 442 8305 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 7370 424 0 0 0.3 0.3 {layer=21}
B 15 -214 702 2695 858 {fill=0}
T {NMOS Differential Pair} -214 684 0 0 0.3 0.3 {layer=15}
B 13 -1224 702 2695 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1224 684 0 0 0.3 0.3 {layer=13}
B 18 101 702 3010 858 {fill=0}
T {NMOS Differential Pair} 101 684 0 0 0.3 0.3 {layer=18}
B 20 101 702 4655 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 101 660 0 0 0.3 0.3 {layer=20}
B 8 -1539 702 3010 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1539 684 0 0 0.3 0.3 {layer=8}
B 10 -214 702 4970 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -214 660 0 0 0.3 0.3 {layer=10}
B 12 -1419 442 5510 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1419 424 0 0 0.3 0.3 {layer=12}
B 21 1661 442 2895 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1661 424 0 0 0.3 0.3 {layer=21}
B 15 -1734 702 3280 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1734 684 0 0 0.3 0.3 {layer=15}
B 13 846 702 1815 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 846 684 0 0 0.3 0.3 {layer=13}
B 18 2880 702 3845 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 2880 684 0 0 0.3 0.3 {layer=18}
B 20 2880 702 5510 858 {fill=0}
T {NMOS Differential Pair} 2880 660 0 0 0.3 0.3 {layer=20}
B 8 -790 702 4140 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -790 684 0 0 0.3 0.3 {layer=8}
B 10 -790 702 5235 858 {fill=0}
T {NMOS Differential Pair} -790 660 0 0 0.3 0.3 {layer=10}
B 12 -1710 442 4970 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1710 424 0 0 0.3 0.3 {layer=12}
B 21 -1985 442 5235 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1985 424 0 0 0.3 0.3 {layer=21}
B 15 -310 442 2620 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -310 424 0 0 0.3 0.3 {layer=15}
B 13 -211 182 2440 338 {fill=0}
T {PMOS Differential Pair} -211 164 0 0 0.3 0.3 {layer=13}
B 18 7900 442 8835 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 7900 424 0 0 0.3 0.3 {layer=18}
B 20 -2250 442 5775 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2250 424 0 0 0.3 0.3 {layer=20}
B 8 -2515 442 6040 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2515 424 0 0 0.3 0.3 {layer=8}
B 10 -1985 702 5235 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1985 684 0 0 0.3 0.3 {layer=10}
B 12 -2250 702 5510 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2250 684 0 0 0.3 0.3 {layer=12}
B 21 -591 182 3845 338 {fill=0}
T {PMOS Differential Pair} -591 164 0 0 0.3 0.3 {layer=21}
B 15 -591 182 4140 338 {fill=0}
T {PMOS Differential Pair} -591 140 0 0 0.3 0.3 {layer=15}
B 13 -886 182 3845 338 {fill=0}
T {PMOS Differential Pair} -886 164 0 0 0.3 0.3 {layer=13}
B 18 -886 182 4140 338 {fill=0}
T {PMOS Differential Pair} -886 140 0 0 0.3 0.3 {layer=18}
B 20 -14 204 3934 316 {fill=0 dash=4}
T {PMOS Differential Pair} -14 186 0 0 0.3 0.3 {layer=20}
