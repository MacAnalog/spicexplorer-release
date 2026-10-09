v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_004_fan_chopper_rrl} -3095 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1455 650 0 0 {name=CAZ1_RRL value='x_dut_caz1_rrl_value'}
C {devices/capa_np.sym} 1755 650 0 0 {name=CAZ2_RRL value='x_dut_caz2_rrl_value'}
C {devices/capa_np.sym} 1155 650 0 0 {name=CFB1_MAIN value='x_dut_cfb1_main_value'}
C {devices/capa_np.sym} 2050 650 0 0 {name=CFB2_MAIN value='x_dut_cfb2_main_value'}
C {devices/capa_np.sym} 3250 520 0 0 {name=CIN1_MAIN value='x_dut_cin1_main_value'}
C {devices/capa_np.sym} 3550 520 0 0 {name=CIN2_MAIN value='x_dut_cin2_main_value'}
C {devices/capa_np.sym} 1455 910 0 0 {name=CINT1_RRL value='x_dut_cint1_rrl_value'}
C {devices/capa_np.sym} 1755 910 0 0 {name=CINT2_RRL value='x_dut_cint2_rrl_value'}
C {devices/capa_np.sym} 1200 1040 0 0 {name=CIN_1_RRL value='cin_val_rrl'}
C {devices/capa_np.sym} 5920 520 0 0 {name=CIN_SERVO_CMFB value='cin_val_cmfb'}
C {devices/capa_np.sym} 6235 520 0 0 {name=CM1_MAIN value='x_dut_cm1_main_value'}
C {devices/capa_np.sym} 6525 520 0 0 {name=CM2_MAIN value='x_dut_cm2_main_value'}
C {devices/capa_np.sym} 6815 520 1 0 {name=COUT_1_RRL value='cout_val_rrl'}
C {devices/capa_np.sym} 2075 910 0 0 {name=COUT_SERVO_CMFB value='cout_val_cmfb'}
C {devices/capa_np.sym} 2360 650 0 0 {name=CS1_RRL value='x_dut_cs1_rrl_value'}
C {devices/capa_np.sym} 660 650 0 0 {name=CS2_RRL value='x_dut_cs2_rrl_value'}
C {devices/vccs.sym} 5745 780 1 0 {name=GM_1_RRL value="\{gm_val_rrl\}"}
C {devices/vccs.sym} 1480 715 0 0 {name=GM_SERVO_CMFB value="\{gm_val_cmfb\}"}
C {devices/res_np.sym} 3845 520 0 0 {name=RB1_MAIN value='x_dut_rb1_main_value'}
C {devices/res_np.sym} 4160 520 0 0 {name=RB2_MAIN value='x_dut_rb2_main_value'}
C {devices/res_np.sym} 745 1040 0 0 {name=RIN_1_RRL value='rin_val_rrl'}
C {devices/res_np.sym} -2375 520 0 0 {name=RIN_SERVO_CMFB value='rin_val_cmfb'}
C {devices/res_np.sym} 1805 390 0 0 {name=RMN_CMFB value='x_dut_rmn_cmfb_value'}
C {devices/res_np.sym} 1485 390 0 0 {name=RMP_CMFB value='x_dut_rmp_cmfb_value'}
C {devices/res_np.sym} 7045 520 1 0 {name=ROUT_1_RRL value='rout_val_rrl'}
C {devices/res_np.sym} 910 910 0 0 {name=ROUT_SERVO_CMFB value='rout_val_cmfb'}
C {devices/vsource_np.sym} -2715 1040 0 0 {name=VB1_MAIN value="dc \{vb1_main\}" savecurrent=false}
C {devices/vsource_np.sym} -2715 780 0 0 {name=VB1_RRL value="dc \{vb1_rrl\}" savecurrent=false}
C {devices/vsource_np.sym} -2715 520 0 0 {name=VB2_MAIN value="dc \{vb2_main\}" savecurrent=false}
C {devices/vsource_np.sym} -2715 260 0 0 {name=VB2_RRL value="dc \{vb2_rrl\}" savecurrent=false}
C {devices/vsource_np.sym} -2715 0 0 0 {name=VB3_MAIN value="dc \{vb3_main\}" savecurrent=false}
C {devices/vsource_np.sym} -3055 1040 0 0 {name=VB3_RRL value="dc \{vb3_rrl\}" savecurrent=false}
C {devices/vsource_np.sym} -3055 780 0 0 {name=VB40 value="dc \{vb40\}" savecurrent=false}
C {devices/vsource_np.sym} -3055 520 0 0 {name=VB4_RRL value="dc \{vb4_rrl\}" savecurrent=false}
C {devices/vsource_np.sym} -3055 260 0 0 {name=VREFCM value="dc \{vcm_ref\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 1145 260 0 1 {name=M10_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_main_w l=x_dut_xm10_main_l m=x_dut_xm10_main_m}
C {devices/sg13_lv_pmos_np.sym} 580 520 0 1 {name=M10_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_rrl_w l=x_dut_xm10_opamp_rrl_l m=x_dut_xm10_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2985 260 0 0 {name=M11_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_main_w l=x_dut_xm11_main_l m=x_dut_xm11_main_m}
C {devices/sg13_lv_nmos_np.sym} 135 780 0 1 {name=M11_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_opamp_rrl_w l=x_dut_xm11_opamp_rrl_l m=x_dut_xm11_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 7270 520 0 0 {name=M12_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_main_w l=x_dut_xm12_main_l m=x_dut_xm12_main_m}
C {devices/sg13_lv_nmos_np.sym} 1765 780 0 0 {name=M12_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_opamp_rrl_w l=x_dut_xm12_opamp_rrl_l m=x_dut_xm12_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1145 520 0 1 {name=M13_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_main_w l=x_dut_xm13_main_l m=x_dut_xm13_main_m}
C {devices/sg13_lv_nmos_np.sym} 135 1040 0 1 {name=M13_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_opamp_rrl_w l=x_dut_xm13_opamp_rrl_l m=x_dut_xm13_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1455 260 0 1 {name=M14_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_main_w l=x_dut_xm14_main_l m=x_dut_xm14_main_m}
C {devices/sg13_lv_nmos_np.sym} 1765 1040 0 0 {name=M14_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_opamp_rrl_w l=x_dut_xm14_opamp_rrl_l m=x_dut_xm14_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1755 260 0 1 {name=M15_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_main_w l=x_dut_xm15_main_l m=x_dut_xm15_main_m}
C {devices/sg13_lv_nmos_np.sym} -805 520 0 1 {name=M15_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_opamp_rrl_w l=x_dut_xm15_opamp_rrl_l m=x_dut_xm15_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1420 520 0 1 {name=M16_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_main_w l=x_dut_xm16_main_l m=x_dut_xm16_main_m}
C {devices/sg13_lv_nmos_np.sym} 4675 520 0 1 {name=M16_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_opamp_rrl_w l=x_dut_xm16_opamp_rrl_l m=x_dut_xm16_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 875 520 0 1 {name=M17_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_main_w l=x_dut_xm17_main_l m=x_dut_xm17_main_m}
C {devices/sg13_lv_nmos_np.sym} 7535 520 0 0 {name=M18_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_main_w l=x_dut_xm18_main_l m=x_dut_xm18_main_m}
C {devices/sg13_lv_pmos_np.sym} 7800 520 0 0 {name=M19_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_main_w l=x_dut_xm19_main_l m=x_dut_xm19_main_m}
C {devices/sg13_lv_nmos_np.sym} 2310 780 0 1 {name=M1_CHRRL_1_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_1_rrl_w l=x_dut_xm1_chrrl_1_rrl_l m=x_dut_xm1_chrrl_1_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2625 780 0 1 {name=M1_CHRRL_2_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_2_rrl_w l=x_dut_xm1_chrrl_2_rrl_l m=x_dut_xm1_chrrl_2_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2935 780 0 1 {name=M1_CHRRL_3_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_3_rrl_w l=x_dut_xm1_chrrl_3_rrl_l m=x_dut_xm1_chrrl_3_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 3250 780 0 1 {name=M1_CHRRL_4_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_4_rrl_w l=x_dut_xm1_chrrl_4_rrl_l m=x_dut_xm1_chrrl_4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1455 0 0 1 {name=M1_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_main_w l=x_dut_xm1_main_l m=x_dut_xm1_main_m}
C {devices/sg13_lv_pmos_np.sym} 1755 0 0 1 {name=M1_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_opamp_rrl_w l=x_dut_xm1_opamp_rrl_l m=x_dut_xm1_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2310 1040 0 1 {name=M1_S1_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s1_rrl_w l=x_dut_xm1_s1_rrl_l m=x_dut_xm1_s1_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2625 1040 0 1 {name=M1_S2_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s2_rrl_w l=x_dut_xm1_s2_rrl_l m=x_dut_xm1_s2_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1695 520 0 1 {name=M1_S3_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s3_rrl_w l=x_dut_xm1_s3_rrl_l m=x_dut_xm1_s3_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1970 520 0 1 {name=M1_S4_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s4_rrl_w l=x_dut_xm1_s4_rrl_l m=x_dut_xm1_s4_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1145 780 0 1 {name=M1_S5_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s5_rrl_w l=x_dut_xm1_s5_rrl_l m=x_dut_xm1_s5_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1420 780 0 1 {name=M1_S6_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s6_rrl_w l=x_dut_xm1_s6_rrl_l m=x_dut_xm1_s6_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 3550 780 0 1 {name=M20_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_main_w l=x_dut_xm20_main_l m=x_dut_xm20_main_m}
C {devices/sg13_lv_pmos_np.sym} -275 780 0 1 {name=M21_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_main_w l=x_dut_xm21_main_l m=x_dut_xm21_main_m}
C {devices/sg13_lv_nmos_np.sym} 3845 780 0 1 {name=M22_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_main_w l=x_dut_xm22_main_l m=x_dut_xm22_main_m}
C {devices/sg13_lv_pmos_np.sym} -540 780 0 1 {name=M23_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_main_w l=x_dut_xm23_main_l m=x_dut_xm23_main_m}
C {devices/sg13_lv_nmos_np.sym} -1120 520 0 1 {name=M24_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_main_w l=x_dut_xm24_main_l m=x_dut_xm24_main_m}
C {devices/sg13_lv_pmos_np.sym} 4940 520 0 1 {name=M25_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm25_main_w l=x_dut_xm25_main_l m=x_dut_xm25_main_m}
C {devices/sg13_lv_nmos_np.sym} -1435 520 0 1 {name=M26_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm26_main_w l=x_dut_xm26_main_l m=x_dut_xm26_main_m}
C {devices/sg13_lv_pmos_np.sym} 5205 520 0 1 {name=M27_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm27_main_w l=x_dut_xm27_main_l m=x_dut_xm27_main_m}
C {devices/sg13_lv_nmos_np.sym} 175 520 0 1 {name=M28_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm28_main_w l=x_dut_xm28_main_l m=x_dut_xm28_main_m}
C {devices/sg13_lv_pmos_np.sym} -125 520 0 1 {name=M29_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm29_main_w l=x_dut_xm29_main_l m=x_dut_xm29_main_m}
C {devices/sg13_lv_pmos_np.sym} 4160 780 0 1 {name=M2_CHRRL_1_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_1_rrl_w l=x_dut_xm2_chrrl_1_rrl_l m=x_dut_xm2_chrrl_1_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -805 780 0 1 {name=M2_CHRRL_2_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_2_rrl_w l=x_dut_xm2_chrrl_2_rrl_l m=x_dut_xm2_chrrl_2_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 4675 780 0 1 {name=M2_CHRRL_3_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_3_rrl_w l=x_dut_xm2_chrrl_3_rrl_l m=x_dut_xm2_chrrl_3_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -1120 780 0 1 {name=M2_CHRRL_4_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_4_rrl_w l=x_dut_xm2_chrrl_4_rrl_l m=x_dut_xm2_chrrl_4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2050 260 0 1 {name=M2_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_main_w l=x_dut_xm2_main_l m=x_dut_xm2_main_m}
C {devices/sg13_lv_pmos_np.sym} 2340 260 0 0 {name=M2_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_rrl_w l=x_dut_xm2_opamp_rrl_l m=x_dut_xm2_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 440 1040 0 1 {name=M2_S1_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s1_rrl_w l=x_dut_xm2_s1_rrl_l m=x_dut_xm2_s1_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2935 1040 0 1 {name=M2_S2_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s2_rrl_w l=x_dut_xm2_s2_rrl_l m=x_dut_xm2_s2_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2825 520 0 1 {name=M2_S3_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s3_rrl_w l=x_dut_xm2_s3_rrl_l m=x_dut_xm2_s3_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -390 520 0 1 {name=M2_S4_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s4_rrl_w l=x_dut_xm2_s4_rrl_l m=x_dut_xm2_s4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 875 780 0 1 {name=M2_S5_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s5_rrl_w l=x_dut_xm2_s5_rrl_l m=x_dut_xm2_s5_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 600 780 0 1 {name=M2_S6_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s6_rrl_w l=x_dut_xm2_s6_rrl_l m=x_dut_xm2_s6_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 8065 520 0 0 {name=M30_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm30_main_w l=x_dut_xm30_main_l m=x_dut_xm30_main_m}
C {devices/sg13_lv_pmos_np.sym} 8335 520 0 0 {name=M31_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm31_main_w l=x_dut_xm31_main_l m=x_dut_xm31_main_m}
C {devices/sg13_lv_nmos_np.sym} -1700 520 0 1 {name=M32_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm32_main_w l=x_dut_xm32_main_l m=x_dut_xm32_main_m}
C {devices/sg13_lv_pmos_np.sym} 5470 520 0 1 {name=M33_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm33_main_w l=x_dut_xm33_main_l m=x_dut_xm33_main_m}
C {devices/sg13_lv_nmos_np.sym} -1965 520 0 1 {name=M34_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm34_main_w l=x_dut_xm34_main_l m=x_dut_xm34_main_m}
C {devices/sg13_lv_pmos_np.sym} 5735 520 0 1 {name=M35_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm35_main_w l=x_dut_xm35_main_l m=x_dut_xm35_main_m}
C {devices/sg13_lv_nmos_np.sym} 4940 780 0 1 {name=M36_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm36_main_w l=x_dut_xm36_main_l m=x_dut_xm36_main_m}
C {devices/sg13_lv_pmos_np.sym} -1435 780 0 1 {name=M37_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm37_main_w l=x_dut_xm37_main_l m=x_dut_xm37_main_m}
C {devices/sg13_lv_nmos_np.sym} 5205 780 0 1 {name=M38_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm38_main_w l=x_dut_xm38_main_l m=x_dut_xm38_main_m}
C {devices/sg13_lv_pmos_np.sym} -1700 780 0 1 {name=M39_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm39_main_w l=x_dut_xm39_main_l m=x_dut_xm39_main_m}
C {devices/sg13_lv_pmos_np.sym} 280 260 0 1 {name=M3_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_main_w l=x_dut_xm3_main_l m=x_dut_xm3_main_m}
C {devices/sg13_lv_pmos_np.sym} 580 260 0 1 {name=M3_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_rrl_w l=x_dut_xm3_opamp_rrl_l m=x_dut_xm3_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 5470 780 0 1 {name=M4_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_main_w l=x_dut_xm4_main_l m=x_dut_xm4_main_m}
C {devices/sg13_lv_pmos_np.sym} 2050 0 0 1 {name=M4_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_opamp_rrl_w l=x_dut_xm4_opamp_rrl_l m=x_dut_xm4_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} -1965 780 0 1 {name=M5_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_main_w l=x_dut_xm5_main_l m=x_dut_xm5_main_m}
C {devices/sg13_lv_pmos_np.sym} 25 260 0 1 {name=M5_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_opamp_rrl_w l=x_dut_xm5_opamp_rrl_l m=x_dut_xm5_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1145 0 0 1 {name=M6_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_main_w l=x_dut_xm6_main_l m=x_dut_xm6_main_m}
C {devices/sg13_lv_pmos_np.sym} 3550 260 0 1 {name=M6_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_opamp_rrl_w l=x_dut_xm6_opamp_rrl_l m=x_dut_xm6_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2985 0 0 0 {name=M7_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_main_w l=x_dut_xm7_main_l m=x_dut_xm7_main_m}
C {devices/sg13_lv_pmos_np.sym} -275 260 0 1 {name=M7_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_opamp_rrl_w l=x_dut_xm7_opamp_rrl_l m=x_dut_xm7_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2310 0 0 1 {name=M8_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_main_w l=x_dut_xm8_main_l m=x_dut_xm8_main_m}
C {devices/sg13_lv_pmos_np.sym} 3845 260 0 1 {name=M8_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_opamp_rrl_w l=x_dut_xm8_opamp_rrl_l m=x_dut_xm8_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 610 0 0 1 {name=M9_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_main_w l=x_dut_xm9_main_l m=x_dut_xm9_main_m}
C {devices/sg13_lv_pmos_np.sym} 2340 520 0 0 {name=M9_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_rrl_w l=x_dut_xm9_opamp_rrl_l m=x_dut_xm9_opamp_rrl_m}
N -3055 170 -3055 230 {}
N -3055 290 -3055 350 {}
N -3055 430 -3055 490 {}
N -3055 550 -3055 610 {}
N -3055 690 -3055 750 {}
N -3055 810 -3055 870 {}
N -3055 950 -3055 1010 {}
N -3055 1070 -3055 1130 {}
N -2715 -90 -2715 -30 {}
N -2715 30 -2715 90 {}
N -2715 170 -2715 230 {}
N -2715 290 -2715 350 {}
N -2715 430 -2715 490 {}
N -2715 550 -2715 610 {}
N -2715 690 -2715 750 {}
N -2715 810 -2715 870 {}
N -2715 950 -2715 1010 {}
N -2715 1070 -2715 1130 {}
N -2435 580 -2435 695 {}
N -2375 430 -2375 490 {}
N -2375 550 -2375 610 {}
N -2045 520 -2045 614 {}
N -2045 780 -2045 874 {}
N -1985 430 -1985 490 {}
N -1985 550 -1985 610 {}
N -1985 690 -1985 750 {}
N -1985 810 -1985 1180 {}
N -1780 520 -1780 614 {}
N -1780 780 -1780 874 {}
N -1720 430 -1720 490 {}
N -1720 550 -1720 610 {}
N -1720 690 -1720 750 {}
N -1720 810 -1720 870 {}
N -1515 520 -1515 614 {}
N -1515 780 -1515 874 {}
N -1455 430 -1455 490 {}
N -1455 550 -1455 610 {}
N -1455 690 -1455 750 {}
N -1455 810 -1455 870 {}
N -1200 520 -1200 614 {}
N -1200 780 -1200 874 {}
N -1140 430 -1140 490 {}
N -1140 550 -1140 610 {}
N -1140 690 -1140 750 {}
N -1140 810 -1140 870 {}
N -885 520 -885 614 {}
N -885 780 -885 874 {}
N -825 430 -825 490 {}
N -825 550 -825 610 {}
N -825 690 -825 750 {}
N -825 810 -825 870 {}
N -785 450 -785 520 {}
N -620 780 -620 874 {}
N -560 690 -560 750 {}
N -560 810 -560 870 {}
N -470 520 -470 614 {}
N -410 430 -410 490 {}
N -410 550 -410 610 {}
N -355 260 -355 354 {}
N -355 780 -355 874 {}
N -295 200 -295 230 {}
N -295 290 -295 350 {}
N -295 690 -295 750 {}
N -295 810 -295 870 {}
N -205 520 -205 614 {}
N -145 430 -145 490 {}
N -145 550 -145 610 {}
N -55 260 -55 354 {}
N 5 200 5 230 {}
N 5 290 5 320 {}
N 55 780 55 874 {}
N 55 1040 55 1134 {}
N 95 520 95 614 {}
N 115 690 115 750 {}
N 115 810 115 870 {}
N 115 950 115 1010 {}
N 115 1070 115 1180 {}
N 155 430 155 490 {}
N 155 550 155 610 {}
N 200 260 200 354 {}
N 260 170 260 230 {}
N 260 290 260 350 {}
N 360 1040 360 1134 {}
N 420 980 420 1010 {}
N 420 1070 420 1180 {}
N 500 260 500 354 {}
N 500 520 500 614 {}
N 520 780 520 874 {}
N 530 0 530 94 {}
N 560 170 560 230 {}
N 560 290 560 350 {}
N 560 430 560 490 {}
N 560 550 560 610 {}
N 580 690 580 750 {}
N 580 810 580 870 {}
N 590 -140 590 -30 {}
N 590 30 590 90 {}
N 660 60 660 620 {}
N 660 680 660 980 {}
N 745 950 745 1010 {}
N 745 1070 745 1100 {}
N 795 520 795 614 {}
N 795 780 795 874 {}
N 855 430 855 490 {}
N 855 550 855 610 {}
N 855 690 855 750 {}
N 855 810 855 870 {}
N 910 940 910 970 {}
N 1065 0 1065 94 {}
N 1065 260 1065 354 {}
N 1065 520 1065 614 {}
N 1065 780 1065 874 {}
N 1125 -140 1125 -30 {}
N 1125 30 1125 90 {}
N 1125 170 1125 230 {}
N 1125 290 1125 350 {}
N 1125 430 1125 490 {}
N 1125 550 1125 610 {}
N 1125 690 1125 750 {}
N 1125 810 1125 870 {}
N 1155 590 1155 620 {}
N 1155 680 1155 710 {}
N 1195 780 1195 1040 {}
N 1200 1070 1200 1160 {}
N 1340 520 1340 614 {}
N 1340 780 1340 874 {}
N 1375 0 1375 94 {}
N 1375 260 1375 354 {}
N 1400 430 1400 490 {}
N 1400 550 1400 610 {}
N 1400 690 1400 750 {}
N 1400 810 1400 1160 {}
N 1435 -140 1435 -30 {}
N 1435 30 1435 90 {}
N 1435 170 1435 230 {}
N 1435 290 1435 1180 {}
N 1455 560 1455 620 {}
N 1455 680 1455 740 {}
N 1455 850 1455 880 {}
N 1455 940 1455 1140 {}
N 1470 780 1470 840 {}
N 1480 625 1480 685 {}
N 1480 745 1480 805 {}
N 1485 330 1485 360 {}
N 1485 420 1485 450 {}
N 1515 590 1515 850 {}
N 1515 940 1515 1010 {}
N 1615 520 1615 614 {}
N 1675 0 1675 94 {}
N 1675 260 1675 354 {}
N 1675 430 1675 490 {}
N 1675 550 1675 610 {}
N 1735 -140 1735 -30 {}
N 1735 30 1735 90 {}
N 1735 170 1735 230 {}
N 1735 290 1735 1180 {}
N 1745 460 1745 520 {}
N 1755 560 1755 620 {}
N 1755 680 1755 710 {}
N 1755 820 1755 880 {}
N 1755 940 1755 1000 {}
N 1785 690 1785 750 {}
N 1785 810 1785 870 {}
N 1785 950 1785 1010 {}
N 1785 1070 1785 1180 {}
N 1805 330 1805 360 {}
N 1805 420 1805 480 {}
N 1845 780 1845 874 {}
N 1845 1040 1845 1134 {}
N 1890 520 1890 614 {}
N 1950 430 1950 490 {}
N 1950 550 1950 610 {}
N 1970 60 1970 200 {}
N 1970 260 1970 354 {}
N 2010 490 2010 710 {}
N 2020 460 2020 520 {}
N 2030 -140 2030 -30 {}
N 2030 30 2030 60 {}
N 2030 60 2030 90 {}
N 2030 170 2030 230 {}
N 2030 290 2030 350 {}
N 2050 560 2050 620 {}
N 2050 680 2050 710 {}
N 2075 820 2075 880 {}
N 2075 940 2075 1000 {}
N 2090 60 2090 200 {}
N 2100 260 2100 710 {}
N 2230 0 2230 94 {}
N 2230 780 2230 874 {}
N 2230 1040 2230 1134 {}
N 2290 -140 2290 -30 {}
N 2290 30 2290 90 {}
N 2290 690 2290 750 {}
N 2290 810 2290 870 {}
N 2290 980 2290 1010 {}
N 2290 1070 2290 1180 {}
N 2360 170 2360 230 {}
N 2360 290 2360 350 {}
N 2360 430 2360 490 {}
N 2360 590 2360 620 {}
N 2360 680 2360 740 {}
N 2420 260 2420 354 {}
N 2420 520 2420 614 {}
N 2545 780 2545 874 {}
N 2545 1040 2545 1134 {}
N 2605 690 2605 750 {}
N 2605 810 2605 870 {}
N 2605 950 2605 1010 {}
N 2605 1070 2605 1180 {}
N 2745 520 2745 614 {}
N 2805 430 2805 490 {}
N 2855 780 2855 874 {}
N 2855 1040 2855 1134 {}
N 2915 690 2915 750 {}
N 2915 810 2915 870 {}
N 2915 980 2915 1010 {}
N 2915 1070 2915 1180 {}
N 3005 -140 3005 -30 {}
N 3005 30 3005 90 {}
N 3005 170 3005 230 {}
N 3005 290 3005 350 {}
N 3065 0 3065 94 {}
N 3065 260 3065 354 {}
N 3170 780 3170 874 {}
N 3230 690 3230 750 {}
N 3230 810 3230 870 {}
N 3250 430 3250 490 {}
N 3250 550 3250 610 {}
N 3470 260 3470 354 {}
N 3470 780 3470 874 {}
N 3530 200 3530 230 {}
N 3530 290 3530 350 {}
N 3530 690 3530 750 {}
N 3530 810 3530 870 {}
N 3550 430 3550 490 {}
N 3550 550 3550 610 {}
N 3600 260 3600 320 {}
N 3765 260 3765 354 {}
N 3765 780 3765 874 {}
N 3825 200 3825 230 {}
N 3825 290 3825 350 {}
N 3825 690 3825 750 {}
N 3825 810 3825 870 {}
N 3845 430 3845 490 {}
N 3845 550 3845 610 {}
N 3895 260 3895 320 {}
N 4080 780 4080 874 {}
N 4140 690 4140 750 {}
N 4140 810 4140 870 {}
N 4160 430 4160 490 {}
N 4160 550 4160 610 {}
N 4595 520 4595 614 {}
N 4595 780 4595 874 {}
N 4655 430 4655 490 {}
N 4655 550 4655 610 {}
N 4655 690 4655 750 {}
N 4655 810 4655 870 {}
N 4695 450 4695 520 {}
N 4860 520 4860 614 {}
N 4860 780 4860 874 {}
N 4920 430 4920 490 {}
N 4920 550 4920 610 {}
N 4920 690 4920 750 {}
N 4920 810 4920 870 {}
N 5125 520 5125 614 {}
N 5125 780 5125 874 {}
N 5185 430 5185 490 {}
N 5185 550 5185 610 {}
N 5185 690 5185 750 {}
N 5185 810 5185 840 {}
N 5390 520 5390 614 {}
N 5390 780 5390 874 {}
N 5450 430 5450 490 {}
N 5450 550 5450 610 {}
N 5450 720 5450 750 {}
N 5450 810 5450 1180 {}
N 5520 460 5520 520 {}
N 5655 520 5655 614 {}
N 5715 430 5715 490 {}
N 5715 550 5715 610 {}
N 5725 680 5725 740 {}
N 5765 680 5765 1140 {}
N 5785 460 5785 520 {}
N 5920 460 5920 490 {}
N 5980 420 5980 460 {}
N 5980 550 5980 695 {}
N 6235 430 6235 490 {}
N 6235 550 6235 610 {}
N 6525 430 6525 490 {}
N 6525 550 6525 610 {}
N 6875 460 6875 780 {}
N 7105 400 7105 520 {}
N 7290 400 7290 490 {}
N 7290 550 7290 610 {}
N 7350 550 7350 720 {}
N 7555 460 7555 490 {}
N 7555 550 7555 610 {}
N 7615 520 7615 614 {}
N 7820 460 7820 490 {}
N 7820 550 7820 610 {}
N 7880 520 7880 614 {}
N 8085 460 8085 490 {}
N 8085 550 8085 610 {}
N 8145 520 8145 614 {}
N 8355 460 8355 490 {}
N 8355 550 8355 580 {}
N 8415 520 8415 614 {}
N -3115 -140 8955 -140 {}
N 530 0 590 0 {}
N 630 0 690 0 {}
N 1065 0 1125 0 {}
N 1165 0 1225 0 {}
N 1375 0 1435 0 {}
N 1475 0 1535 0 {}
N 1675 0 1735 0 {}
N 1775 0 1835 0 {}
N 2070 0 2130 0 {}
N 2230 0 2290 0 {}
N 2330 0 2965 0 {}
N 3005 0 3065 0 {}
N 590 60 660 60 {}
N 1970 60 2090 60 {}
N -295 200 3825 200 {}
N -355 260 -295 260 {}
N -255 260 -195 260 {}
N -55 260 5 260 {}
N 45 260 105 260 {}
N 200 260 260 260 {}
N 300 260 360 260 {}
N 500 260 560 260 {}
N 600 260 630 260 {}
N 1065 260 1125 260 {}
N 1165 260 1225 260 {}
N 1375 260 1435 260 {}
N 1475 260 1535 260 {}
N 1675 260 1735 260 {}
N 1775 260 1835 260 {}
N 1970 260 2030 260 {}
N 2070 260 2130 260 {}
N 2260 260 2320 260 {}
N 2360 260 2420 260 {}
N 2905 260 2965 260 {}
N 3005 260 3065 260 {}
N 3470 260 3530 260 {}
N 3570 260 3630 260 {}
N 3765 260 3825 260 {}
N 3865 260 3895 260 {}
N -295 320 5 320 {}
N 3600 320 3895 320 {}
N 1425 360 1485 360 {}
N 7105 400 7290 400 {}
N 1425 420 1485 420 {}
N 1805 420 5980 420 {}
N -825 450 -785 450 {}
N 4655 450 4695 450 {}
N 1745 460 2020 460 {}
N 5520 460 5785 460 {}
N 5920 460 5980 460 {}
N 6875 460 7105 460 {}
N 7290 460 8355 460 {}
N 1950 490 2010 490 {}
N -2045 520 -1985 520 {}
N -1945 520 -1915 520 {}
N -1780 520 -1720 520 {}
N -1680 520 -1620 520 {}
N -1515 520 -1455 520 {}
N -1415 520 -1385 520 {}
N -1200 520 -1140 520 {}
N -1100 520 -1040 520 {}
N -885 520 -825 520 {}
N -470 520 -410 520 {}
N -370 520 -340 520 {}
N -205 520 -145 520 {}
N -105 520 -45 520 {}
N 95 520 155 520 {}
N 195 520 255 520 {}
N 500 520 560 520 {}
N 600 520 630 520 {}
N 795 520 855 520 {}
N 895 520 955 520 {}
N 1065 520 1125 520 {}
N 1165 520 1225 520 {}
N 1340 520 1400 520 {}
N 1440 520 1500 520 {}
N 1615 520 1675 520 {}
N 1715 520 1775 520 {}
N 1890 520 1950 520 {}
N 1990 520 2020 520 {}
N 2260 520 2320 520 {}
N 2360 520 2420 520 {}
N 2745 520 2805 520 {}
N 2845 520 2905 520 {}
N 4595 520 4655 520 {}
N 4860 520 4920 520 {}
N 4960 520 5020 520 {}
N 5125 520 5185 520 {}
N 5225 520 5285 520 {}
N 5390 520 5450 520 {}
N 5490 520 5550 520 {}
N 5655 520 5715 520 {}
N 5755 520 5785 520 {}
N 6725 520 6785 520 {}
N 6845 520 6875 520 {}
N 6955 520 7015 520 {}
N 7075 520 7105 520 {}
N 7190 520 7250 520 {}
N 7455 520 7515 520 {}
N 7555 520 7615 520 {}
N 7720 520 7780 520 {}
N 7820 520 7880 520 {}
N 7985 520 8045 520 {}
N 8085 520 8145 520 {}
N 8255 520 8315 520 {}
N 8355 520 8415 520 {}
N 2300 550 2805 550 {}
N 5920 550 5980 550 {}
N 7290 550 7350 550 {}
N -2435 580 -2375 580 {}
N 8085 580 8355 580 {}
N 1455 590 1515 590 {}
N 1095 620 1155 620 {}
N 600 680 660 680 {}
N 1095 680 1155 680 {}
N -2435 695 5980 695 {}
N 1755 710 2010 710 {}
N 2050 710 2100 710 {}
N 5450 720 7350 720 {}
N 1380 735 1440 735 {}
N -2045 780 -1985 780 {}
N -1945 780 -1885 780 {}
N -1780 780 -1720 780 {}
N -1680 780 -1650 780 {}
N -1515 780 -1455 780 {}
N -1415 780 -1355 780 {}
N -1200 780 -1140 780 {}
N -1100 780 -1070 780 {}
N -885 780 -825 780 {}
N -785 780 -755 780 {}
N -620 780 -560 780 {}
N -520 780 -490 780 {}
N -355 780 -295 780 {}
N -255 780 -195 780 {}
N 55 780 115 780 {}
N 155 780 215 780 {}
N 520 780 580 780 {}
N 620 780 650 780 {}
N 795 780 855 780 {}
N 895 780 955 780 {}
N 1065 780 1125 780 {}
N 1165 780 1225 780 {}
N 1340 780 1400 780 {}
N 1440 780 1470 780 {}
N 1685 780 1745 780 {}
N 1785 780 1845 780 {}
N 2230 780 2290 780 {}
N 2330 780 2390 780 {}
N 2545 780 2605 780 {}
N 2645 780 2705 780 {}
N 2855 780 2915 780 {}
N 2955 780 3015 780 {}
N 3170 780 3230 780 {}
N 3270 780 3330 780 {}
N 3470 780 3530 780 {}
N 3570 780 3630 780 {}
N 3765 780 3825 780 {}
N 3865 780 3925 780 {}
N 4080 780 4140 780 {}
N 4180 780 4240 780 {}
N 4595 780 4655 780 {}
N 4695 780 4755 780 {}
N 4860 780 4920 780 {}
N 4960 780 5020 780 {}
N 5125 780 5185 780 {}
N 5225 780 5285 780 {}
N 5390 780 5450 780 {}
N 5490 780 5550 780 {}
N 5655 780 5715 780 {}
N 5775 780 6875 780 {}
N 1195 840 1470 840 {}
N 1455 850 1515 850 {}
N 850 880 910 880 {}
N 850 940 910 940 {}
N 1455 940 1515 940 {}
N 360 980 2290 980 {}
N 2605 980 2915 980 {}
N 1200 1010 1515 1010 {}
N 55 1040 115 1040 {}
N 155 1040 215 1040 {}
N 360 1040 420 1040 {}
N 460 1040 1195 1040 {}
N 1685 1040 1745 1040 {}
N 1785 1040 1845 1040 {}
N 2230 1040 2290 1040 {}
N 2330 1040 2390 1040 {}
N 2545 1040 2605 1040 {}
N 2645 1040 2705 1040 {}
N 2855 1040 2915 1040 {}
N 2955 1040 3015 1040 {}
N 745 1100 1200 1100 {}
N 1455 1140 5765 1140 {}
N 1200 1160 1400 1160 {}
N -3115 1180 8955 1180 {}
C {devices/lab_wire.sym} -1355 780 0 1 {name=l0 lab=clk_chfb}
C {devices/lab_wire.sym} 3630 780 0 1 {name=l1 lab=clk_chfb}
C {devices/lab_wire.sym} 3925 780 0 1 {name=l2 lab=clk_chfb}
C {devices/lab_wire.sym} -195 780 0 1 {name=l3 lab=clk_chfb_not}
C {devices/lab_wire.sym} 5020 780 0 1 {name=l4 lab=clk_chfb_not}
C {devices/lab_wire.sym} 5285 780 0 1 {name=l5 lab=clk_chfb_not}
C {devices/lab_wire.sym} -1040 520 0 1 {name=l6 lab=clk_chin}
C {devices/lab_wire.sym} 5550 520 0 1 {name=l7 lab=clk_chin}
C {devices/lab_wire.sym} -1620 520 0 1 {name=l8 lab=clk_chin_not}
C {devices/lab_wire.sym} 5020 520 0 1 {name=l9 lab=clk_chin_not}
C {devices/lab_wire.sym} 5285 520 0 1 {name=l10 lab=clk_chin_not}
C {devices/lab_wire.sym} -45 520 0 1 {name=l11 lab=clk_chout}
C {devices/lab_wire.sym} 1500 520 0 1 {name=l12 lab=clk_chout}
C {devices/lab_wire.sym} 2390 780 0 1 {name=l13 lab=clk_chout}
C {devices/lab_wire.sym} 2705 780 0 1 {name=l14 lab=clk_chout}
C {devices/lab_wire.sym} 4755 780 0 1 {name=l15 lab=clk_chout}
C {devices/lab_wire.sym} 7455 520 0 0 {name=l16 lab=clk_chout}
C {devices/lab_wire.sym} 8255 520 0 0 {name=l17 lab=clk_chout}
C {devices/lab_wire.sym} 255 520 0 1 {name=l18 lab=clk_chout_not}
C {devices/lab_wire.sym} 955 520 0 1 {name=l19 lab=clk_chout_not}
C {devices/lab_wire.sym} 3015 780 0 1 {name=l20 lab=clk_chout_not}
C {devices/lab_wire.sym} 3330 780 0 1 {name=l21 lab=clk_chout_not}
C {devices/lab_wire.sym} 4240 780 0 1 {name=l22 lab=clk_chout_not}
C {devices/lab_wire.sym} 7720 520 0 0 {name=l23 lab=clk_chout_not}
C {devices/lab_wire.sym} 7985 520 0 0 {name=l24 lab=clk_chout_not}
C {devices/lab_wire.sym} 1225 780 0 1 {name=l25 lab=clk_phi_1}
C {devices/lab_wire.sym} 2905 520 0 1 {name=l26 lab=clk_phi_1}
C {devices/lab_wire.sym} 3015 1040 0 1 {name=l27 lab=clk_phi_1}
C {devices/lab_wire.sym} 955 780 0 1 {name=l28 lab=clk_phi_2}
C {devices/lab_wire.sym} 1775 520 0 1 {name=l29 lab=clk_phi_2}
C {devices/lab_wire.sym} 2390 1040 0 1 {name=l30 lab=clk_phi_2}
C {devices/lab_wire.sym} 2705 1040 0 1 {name=l31 lab=clk_phi_2}
C {devices/lab_wire.sym} -2375 430 0 1 {name=l32 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 1380 735 0 0 {name=l33 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 1425 360 0 0 {name=l34 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 1805 480 2 0 {name=l35 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 1125 90 2 0 {name=l36 lab=main__casc_src_n}
C {devices/lab_wire.sym} 1125 170 0 1 {name=l37 lab=main__casc_src_n}
C {devices/lab_wire.sym} 3005 90 2 0 {name=l38 lab=main__casc_src_p}
C {devices/lab_wire.sym} 3005 170 0 1 {name=l39 lab=main__casc_src_p}
C {devices/lab_wire.sym} -1720 690 0 1 {name=l40 lab=main__fbch_n}
C {devices/lab_wire.sym} -560 690 0 1 {name=l41 lab=main__fbch_n}
C {devices/lab_wire.sym} 2050 560 0 1 {name=l42 lab=main__fbch_n}
C {devices/lab_wire.sym} 3825 690 0 1 {name=l43 lab=main__fbch_n}
C {devices/lab_wire.sym} 5185 690 0 1 {name=l44 lab=main__fbch_n}
C {devices/lab_wire.sym} -1455 690 0 1 {name=l45 lab=main__fbch_p}
C {devices/lab_wire.sym} -295 690 0 1 {name=l46 lab=main__fbch_p}
C {devices/lab_wire.sym} 1095 620 0 0 {name=l47 lab=main__fbch_p}
C {devices/lab_wire.sym} 3530 690 0 1 {name=l48 lab=main__fbch_p}
C {devices/lab_wire.sym} 4920 690 0 1 {name=l49 lab=main__fbch_p}
C {devices/lab_wire.sym} -1985 690 0 1 {name=l50 lab=main__fold_n}
C {devices/lab_wire.sym} 260 350 2 0 {name=l51 lab=main__fold_n}
C {devices/lab_wire.sym} 1125 610 2 0 {name=l52 lab=main__fold_n}
C {devices/lab_wire.sym} 2030 350 2 0 {name=l53 lab=main__fold_p}
C {devices/lab_wire.sym} 7290 610 2 0 {name=l54 lab=main__fold_p}
C {devices/lab_wire.sym} 855 610 2 0 {name=l55 lab=main__g2_n}
C {devices/lab_wire.sym} 1400 610 2 0 {name=l56 lab=main__g2_n}
C {devices/lab_wire.sym} 1835 260 0 1 {name=l57 lab=main__g2_n}
C {devices/lab_wire.sym} 6525 430 0 1 {name=l58 lab=main__g2_n}
C {devices/lab_wire.sym} 8085 610 2 0 {name=l59 lab=main__g2_n}
C {devices/lab_wire.sym} -145 610 2 0 {name=l60 lab=main__g2_p}
C {devices/lab_wire.sym} 155 610 2 0 {name=l61 lab=main__g2_p}
C {devices/lab_wire.sym} 1535 260 0 1 {name=l62 lab=main__g2_p}
C {devices/lab_wire.sym} 6235 430 0 1 {name=l63 lab=main__g2_p}
C {devices/lab_wire.sym} 7555 610 2 0 {name=l64 lab=main__g2_p}
C {devices/lab_wire.sym} 7820 610 2 0 {name=l65 lab=main__g2_p}
C {devices/lab_wire.sym} -1985 610 2 0 {name=l66 lab=main__inch_n}
C {devices/lab_wire.sym} -1140 610 2 0 {name=l67 lab=main__inch_n}
C {devices/lab_wire.sym} 3250 610 2 0 {name=l68 lab=main__inch_n}
C {devices/lab_wire.sym} 4920 610 2 0 {name=l69 lab=main__inch_n}
C {devices/lab_wire.sym} 5715 610 2 0 {name=l70 lab=main__inch_n}
C {devices/lab_wire.sym} -1720 610 2 0 {name=l71 lab=main__inch_p}
C {devices/lab_wire.sym} -1455 610 2 0 {name=l72 lab=main__inch_p}
C {devices/lab_wire.sym} 3550 610 2 0 {name=l73 lab=main__inch_p}
C {devices/lab_wire.sym} 5185 610 2 0 {name=l74 lab=main__inch_p}
C {devices/lab_wire.sym} 5450 610 2 0 {name=l75 lab=main__inch_p}
C {devices/lab_wire.sym} 260 170 0 1 {name=l76 lab=main__tail}
C {devices/lab_wire.sym} 1435 90 2 0 {name=l77 lab=main__tail}
C {devices/lab_wire.sym} 2030 170 0 1 {name=l78 lab=main__tail}
C {devices/lab_wire.sym} -1885 780 0 1 {name=l79 lab=main__vb1}
C {devices/lab_wire.sym} 5550 780 0 1 {name=l80 lab=main__vb1}
C {devices/lab_wire.sym} 1225 520 0 1 {name=l81 lab=main__vb2}
C {devices/lab_wire.sym} 7190 520 0 0 {name=l82 lab=main__vb2}
C {devices/lab_wire.sym} 1225 260 0 1 {name=l83 lab=main__vb3}
C {devices/lab_wire.sym} 2905 260 0 0 {name=l84 lab=main__vb3}
C {devices/lab_wire.sym} 360 260 0 1 {name=l85 lab=main__vsum_n}
C {devices/lab_wire.sym} 1095 680 0 0 {name=l86 lab=main__vsum_n}
C {devices/lab_wire.sym} 3250 430 0 1 {name=l87 lab=main__vsum_n}
C {devices/lab_wire.sym} 3845 430 0 1 {name=l88 lab=main__vsum_n}
C {devices/lab_wire.sym} 2130 260 0 1 {name=l89 lab=main__vsum_p}
C {devices/lab_wire.sym} 3550 430 0 1 {name=l90 lab=main__vsum_p}
C {devices/lab_wire.sym} 4160 430 0 1 {name=l91 lab=main__vsum_p}
C {devices/lab_wire.sym} -145 430 0 1 {name=l92 lab=out1_n}
C {devices/lab_wire.sym} 155 430 0 1 {name=l93 lab=out1_n}
C {devices/lab_wire.sym} 855 430 0 1 {name=l94 lab=out1_n}
C {devices/lab_wire.sym} 1125 350 2 0 {name=l95 lab=out1_n}
C {devices/lab_wire.sym} 1125 430 0 1 {name=l96 lab=out1_n}
C {devices/lab_wire.sym} 1400 430 0 1 {name=l97 lab=out1_n}
C {devices/lab_wire.sym} 5655 780 0 0 {name=l98 lab=out1_n}
C {devices/lab_wire.sym} 6725 520 0 0 {name=l99 lab=out1_n}
C {devices/lab_wire.sym} 6955 520 0 0 {name=l100 lab=out1_n}
C {devices/lab_wire.sym} 3005 350 2 0 {name=l101 lab=out1_p}
C {devices/lab_wire.sym} 7290 430 0 1 {name=l102 lab=out1_p}
C {devices/lab_wire.sym} 580 870 2 0 {name=l103 lab=rrl__int_n}
C {devices/lab_wire.sym} 1400 870 2 0 {name=l104 lab=rrl__int_n}
C {devices/lab_wire.sym} 1755 1000 2 0 {name=l105 lab=rrl__int_n}
C {devices/lab_wire.sym} 5725 680 0 1 {name=l106 lab=rrl__int_n}
C {devices/lab_wire.sym} 745 950 0 1 {name=l107 lab=rrl__int_p}
C {devices/lab_wire.sym} 855 870 2 0 {name=l108 lab=rrl__int_p}
C {devices/lab_wire.sym} 1125 870 2 0 {name=l109 lab=rrl__int_p}
C {devices/lab_wire.sym} 5765 680 0 1 {name=l110 lab=rrl__int_p}
C {devices/lab_wire.sym} -825 430 0 1 {name=l111 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 215 1040 0 1 {name=l112 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 1685 1040 0 0 {name=l113 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 3530 350 2 0 {name=l114 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 3825 350 2 0 {name=l115 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} -295 350 2 0 {name=l116 lab=rrl__oa_cm_sense}
C {devices/lab_wire.sym} 4655 430 0 1 {name=l117 lab=rrl__oa_cm_sense}
C {devices/lab_wire.sym} 2030 90 2 0 {name=l118 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} 115 870 2 0 {name=l119 lab=rrl__oa_csrc_n}
C {devices/lab_wire.sym} 115 950 0 1 {name=l120 lab=rrl__oa_csrc_n}
C {devices/lab_wire.sym} 1785 870 2 0 {name=l121 lab=rrl__oa_csrc_p}
C {devices/lab_wire.sym} 1785 950 0 1 {name=l122 lab=rrl__oa_csrc_p}
C {devices/lab_wire.sym} 2360 350 2 0 {name=l123 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 2360 430 0 1 {name=l124 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 560 350 2 0 {name=l125 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} 560 430 0 1 {name=l126 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} -410 430 0 1 {name=l127 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 600 260 0 0 {name=l128 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 1950 430 0 1 {name=l129 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 1455 740 2 0 {name=l130 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 1675 430 0 1 {name=l131 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 2260 260 0 0 {name=l132 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 2805 430 0 1 {name=l133 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 105 260 0 1 {name=l134 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 115 690 0 1 {name=l135 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 855 690 0 1 {name=l136 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 1125 690 0 1 {name=l137 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 1675 610 2 0 {name=l138 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 2360 550 0 0 {name=l139 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -410 610 2 0 {name=l140 lab=rrl__oa_outp}
C {devices/lab_wire.sym} -195 260 0 1 {name=l141 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 560 610 2 0 {name=l142 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 580 690 0 1 {name=l143 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1400 690 0 1 {name=l144 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1785 690 0 1 {name=l145 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1950 610 2 0 {name=l146 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 560 170 0 1 {name=l147 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 1735 90 2 0 {name=l148 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 2360 170 0 1 {name=l149 lab=rrl__oa_tail}
C {devices/lab_wire.sym} -825 870 2 0 {name=l150 lab=rrl__sc_n}
C {devices/lab_wire.sym} 600 680 0 0 {name=l151 lab=rrl__sc_n}
C {devices/lab_wire.sym} 2605 870 2 0 {name=l152 lab=rrl__sc_n}
C {devices/lab_wire.sym} 2915 870 2 0 {name=l153 lab=rrl__sc_n}
C {devices/lab_wire.sym} 4655 870 2 0 {name=l154 lab=rrl__sc_n}
C {devices/lab_wire.sym} -1140 870 2 0 {name=l155 lab=rrl__sc_p}
C {devices/lab_wire.sym} 2290 870 2 0 {name=l156 lab=rrl__sc_p}
C {devices/lab_wire.sym} 2360 740 2 0 {name=l157 lab=rrl__sc_p}
C {devices/lab_wire.sym} 2605 950 0 1 {name=l158 lab=rrl__sc_p}
C {devices/lab_wire.sym} 3230 870 2 0 {name=l159 lab=rrl__sc_p}
C {devices/lab_wire.sym} 4140 870 2 0 {name=l160 lab=rrl__sc_p}
C {devices/lab_wire.sym} -1140 690 0 1 {name=l161 lab=rrl__sum_n}
C {devices/lab_wire.sym} -825 690 0 1 {name=l162 lab=rrl__sum_n}
C {devices/lab_wire.sym} 1755 560 0 1 {name=l163 lab=rrl__sum_n}
C {devices/lab_wire.sym} 1755 820 0 1 {name=l164 lab=rrl__sum_n}
C {devices/lab_wire.sym} 2605 690 0 1 {name=l165 lab=rrl__sum_n}
C {devices/lab_wire.sym} 3230 690 0 1 {name=l166 lab=rrl__sum_n}
C {devices/lab_wire.sym} 1455 560 0 1 {name=l167 lab=rrl__sum_p}
C {devices/lab_wire.sym} 2290 690 0 1 {name=l168 lab=rrl__sum_p}
C {devices/lab_wire.sym} 2915 690 0 1 {name=l169 lab=rrl__sum_p}
C {devices/lab_wire.sym} 4140 690 0 1 {name=l170 lab=rrl__sum_p}
C {devices/lab_wire.sym} 4655 690 0 1 {name=l171 lab=rrl__sum_p}
C {devices/lab_wire.sym} 600 520 0 0 {name=l172 lab=rrl__vb1}
C {devices/lab_wire.sym} 2260 520 0 0 {name=l173 lab=rrl__vb1}
C {devices/lab_wire.sym} 215 780 0 1 {name=l174 lab=rrl__vb2}
C {devices/lab_wire.sym} 1685 780 0 0 {name=l175 lab=rrl__vb2}
C {devices/lab_wire.sym} 1835 0 0 1 {name=l176 lab=rrl__vb3}
C {devices/lab_wire.sym} 2130 0 0 1 {name=l177 lab=rrl__vb3}
C {devices/lab_wire.sym} 3630 260 0 1 {name=l178 lab=rrl__vb4}
C {devices/lab_wire.sym} 690 0 0 1 {name=l179 lab=vb4_ctl}
C {devices/lab_wire.sym} 1225 0 0 1 {name=l180 lab=vb4_ctl}
C {devices/lab_wire.sym} 1535 0 0 1 {name=l181 lab=vb4_ctl}
C {devices/lab_wire.sym} 2390 0 0 1 {name=l182 lab=vb4_ctl}
C {devices/lab_wire.sym} 850 940 0 0 {name=l183 lab=vcmfb_raw}
C {devices/lab_wire.sym} 1480 805 2 0 {name=l184 lab=vcmfb_raw}
C {devices/lab_wire.sym} 2075 1000 2 0 {name=l185 lab=vcmfb_raw}
C {devices/lab_wire.sym} -1720 430 0 1 {name=l186 lab=vinn}
C {devices/lab_wire.sym} -1140 430 0 1 {name=l187 lab=vinn}
C {devices/lab_wire.sym} 4920 430 0 1 {name=l188 lab=vinn}
C {devices/lab_wire.sym} 5450 430 0 1 {name=l189 lab=vinn}
C {devices/lab_wire.sym} -1985 430 0 1 {name=l190 lab=vinp}
C {devices/lab_wire.sym} -1455 430 0 1 {name=l191 lab=vinp}
C {devices/lab_wire.sym} 5185 430 0 1 {name=l192 lab=vinp}
C {devices/lab_wire.sym} 5715 430 0 1 {name=l193 lab=vinp}
C {devices/lab_wire.sym} -1455 870 2 0 {name=l194 lab=voutn}
C {devices/lab_wire.sym} -560 870 2 0 {name=l195 lab=voutn}
C {devices/lab_wire.sym} 590 90 2 0 {name=l196 lab=voutn}
C {devices/lab_wire.sym} 1735 170 0 1 {name=l197 lab=voutn}
C {devices/lab_wire.sym} 3825 870 2 0 {name=l198 lab=voutn}
C {devices/lab_wire.sym} 4920 870 2 0 {name=l199 lab=voutn}
C {devices/lab_wire.sym} 6525 610 2 0 {name=l200 lab=voutn}
C {devices/lab_wire.sym} -1720 870 2 0 {name=l201 lab=voutp}
C {devices/lab_wire.sym} -295 870 2 0 {name=l202 lab=voutp}
C {devices/lab_wire.sym} 1435 170 0 1 {name=l203 lab=voutp}
C {devices/lab_wire.sym} 1425 420 0 0 {name=l204 lab=voutp}
C {devices/lab_wire.sym} 2290 90 2 0 {name=l205 lab=voutp}
C {devices/lab_wire.sym} 2360 620 0 0 {name=l206 lab=voutp}
C {devices/lab_wire.sym} 3530 870 2 0 {name=l207 lab=voutp}
C {devices/lab_wire.sym} 6235 610 2 0 {name=l208 lab=voutp}
C {devices/lab_wire.sym} 3845 610 2 0 {name=l209 lab=vref}
C {devices/lab_wire.sym} 4160 610 2 0 {name=l210 lab=vref}
C {devices/lab_wire.sym} -2375 610 2 0 {name=l211 lab=vref_cm}
C {devices/lab_wire.sym} 1065 354 2 0 {name=l212 lab=vdd}
C {devices/lab_wire.sym} 500 614 2 0 {name=l213 lab=vdd}
C {devices/lab_wire.sym} 3065 354 2 0 {name=l214 lab=vdd}
C {devices/lab_wire.sym} 795 614 2 0 {name=l215 lab=vdd}
C {devices/lab_wire.sym} 7880 614 2 0 {name=l216 lab=vdd}
C {devices/lab_wire.sym} 1375 94 2 0 {name=l217 lab=vdd}
C {devices/lab_wire.sym} 1675 94 2 0 {name=l218 lab=vdd}
C {devices/lab_wire.sym} -355 874 2 0 {name=l219 lab=vdd}
C {devices/lab_wire.sym} -620 874 2 0 {name=l220 lab=vdd}
C {devices/lab_wire.sym} 4860 614 2 0 {name=l221 lab=vdd}
C {devices/lab_wire.sym} 5125 614 2 0 {name=l222 lab=vdd}
C {devices/lab_wire.sym} -205 614 2 0 {name=l223 lab=vdd}
C {devices/lab_wire.sym} 4080 874 2 0 {name=l224 lab=vdd}
C {devices/lab_wire.sym} -885 874 2 0 {name=l225 lab=vdd}
C {devices/lab_wire.sym} 4595 874 2 0 {name=l226 lab=vdd}
C {devices/lab_wire.sym} -1200 874 2 0 {name=l227 lab=vdd}
C {devices/lab_wire.sym} 1970 354 2 0 {name=l228 lab=vdd}
C {devices/lab_wire.sym} 2420 354 2 0 {name=l229 lab=vdd}
C {devices/lab_wire.sym} 360 1134 2 0 {name=l230 lab=vdd}
C {devices/lab_wire.sym} 2855 1134 2 0 {name=l231 lab=vdd}
C {devices/lab_wire.sym} 2745 614 2 0 {name=l232 lab=vdd}
C {devices/lab_wire.sym} -470 614 2 0 {name=l233 lab=vdd}
C {devices/lab_wire.sym} 795 874 2 0 {name=l234 lab=vdd}
C {devices/lab_wire.sym} 520 874 2 0 {name=l235 lab=vdd}
C {devices/lab_wire.sym} 8415 614 2 0 {name=l236 lab=vdd}
C {devices/lab_wire.sym} 5390 614 2 0 {name=l237 lab=vdd}
C {devices/lab_wire.sym} 5655 614 2 0 {name=l238 lab=vdd}
C {devices/lab_wire.sym} -1515 874 2 0 {name=l239 lab=vdd}
C {devices/lab_wire.sym} -1780 874 2 0 {name=l240 lab=vdd}
C {devices/lab_wire.sym} 200 354 2 0 {name=l241 lab=vdd}
C {devices/lab_wire.sym} 500 354 2 0 {name=l242 lab=vdd}
C {devices/lab_wire.sym} 2030 0 0 0 {name=l243 lab=vdd}
C {devices/lab_wire.sym} -55 354 2 0 {name=l244 lab=vdd}
C {devices/lab_wire.sym} 1065 94 2 0 {name=l245 lab=vdd}
C {devices/lab_wire.sym} 3470 354 2 0 {name=l246 lab=vdd}
C {devices/lab_wire.sym} 3065 94 2 0 {name=l247 lab=vdd}
C {devices/lab_wire.sym} -355 354 2 0 {name=l248 lab=vdd}
C {devices/lab_wire.sym} 2230 94 2 0 {name=l249 lab=vdd}
C {devices/lab_wire.sym} 3765 354 2 0 {name=l250 lab=vdd}
C {devices/lab_wire.sym} 530 94 2 0 {name=l251 lab=vdd}
C {devices/lab_wire.sym} 2420 614 2 0 {name=l252 lab=vdd}
C {devices/lab_wire.sym} 55 874 2 0 {name=l253 lab=vss}
C {devices/lab_wire.sym} 7290 520 0 0 {name=l254 lab=vss}
C {devices/lab_wire.sym} 1845 874 2 0 {name=l255 lab=vss}
C {devices/lab_wire.sym} 1065 614 2 0 {name=l256 lab=vss}
C {devices/lab_wire.sym} 55 1134 2 0 {name=l257 lab=vss}
C {devices/lab_wire.sym} 1375 354 2 0 {name=l258 lab=vss}
C {devices/lab_wire.sym} 1845 1134 2 0 {name=l259 lab=vss}
C {devices/lab_wire.sym} 1675 354 2 0 {name=l260 lab=vss}
C {devices/lab_wire.sym} -885 614 2 0 {name=l261 lab=vss}
C {devices/lab_wire.sym} 1340 614 2 0 {name=l262 lab=vss}
C {devices/lab_wire.sym} 4595 614 2 0 {name=l263 lab=vss}
C {devices/lab_wire.sym} 7615 614 2 0 {name=l264 lab=vss}
C {devices/lab_wire.sym} 2230 874 2 0 {name=l265 lab=vss}
C {devices/lab_wire.sym} 2545 874 2 0 {name=l266 lab=vss}
C {devices/lab_wire.sym} 2855 874 2 0 {name=l267 lab=vss}
C {devices/lab_wire.sym} 3170 874 2 0 {name=l268 lab=vss}
C {devices/lab_wire.sym} 2230 1134 2 0 {name=l269 lab=vss}
C {devices/lab_wire.sym} 2545 1134 2 0 {name=l270 lab=vss}
C {devices/lab_wire.sym} 1615 614 2 0 {name=l271 lab=vss}
C {devices/lab_wire.sym} 1890 614 2 0 {name=l272 lab=vss}
C {devices/lab_wire.sym} 1065 874 2 0 {name=l273 lab=vss}
C {devices/lab_wire.sym} 1340 874 2 0 {name=l274 lab=vss}
C {devices/lab_wire.sym} 3470 874 2 0 {name=l275 lab=vss}
C {devices/lab_wire.sym} 3765 874 2 0 {name=l276 lab=vss}
C {devices/lab_wire.sym} -1200 614 2 0 {name=l277 lab=vss}
C {devices/lab_wire.sym} -1515 614 2 0 {name=l278 lab=vss}
C {devices/lab_wire.sym} 95 614 2 0 {name=l279 lab=vss}
C {devices/lab_wire.sym} 8145 614 2 0 {name=l280 lab=vss}
C {devices/lab_wire.sym} -1780 614 2 0 {name=l281 lab=vss}
C {devices/lab_wire.sym} -2045 614 2 0 {name=l282 lab=vss}
C {devices/lab_wire.sym} 4860 874 2 0 {name=l283 lab=vss}
C {devices/lab_wire.sym} 5125 874 2 0 {name=l284 lab=vss}
C {devices/lab_wire.sym} 5390 874 2 0 {name=l285 lab=vss}
C {devices/lab_wire.sym} -2045 874 2 0 {name=l286 lab=vss}
C {devices/lab_wire.sym} -3055 170 0 1 {name=l287 lab=vref_cm}
C {devices/lab_wire.sym} -2715 1130 2 0 {name=l288 lab=vss}
C {devices/lab_wire.sym} -2715 870 2 0 {name=l289 lab=vss}
C {devices/lab_wire.sym} -2715 610 2 0 {name=l290 lab=vss}
C {devices/lab_wire.sym} -2715 350 2 0 {name=l291 lab=vss}
C {devices/lab_wire.sym} -2715 90 2 0 {name=l292 lab=vss}
C {devices/lab_wire.sym} -3055 1130 2 0 {name=l293 lab=vss}
C {devices/lab_wire.sym} -3055 610 2 0 {name=l294 lab=vss}
C {devices/lab_wire.sym} -3055 350 2 0 {name=l295 lab=vss}
C {devices/lab_wire.sym} -3055 870 2 0 {name=l296 lab=vcmfb_raw}
C {devices/lab_wire.sym} -2715 950 0 1 {name=l297 lab=main__vb1}
C {devices/lab_wire.sym} -2715 690 0 1 {name=l298 lab=rrl__vb1}
C {devices/lab_wire.sym} -2715 430 0 1 {name=l299 lab=main__vb2}
C {devices/lab_wire.sym} -2715 170 0 1 {name=l300 lab=rrl__vb2}
C {devices/lab_wire.sym} -2715 -90 0 1 {name=l301 lab=main__vb3}
C {devices/lab_wire.sym} -3055 950 0 1 {name=l302 lab=rrl__vb3}
C {devices/lab_wire.sym} -3055 690 0 1 {name=l303 lab=vb4_ctl}
C {devices/lab_wire.sym} -3055 430 0 1 {name=l304 lab=rrl__vb4}
C {devices/lab_wire.sym} 2075 820 0 1 {name=l305 lab=vss}
C {devices/lab_wire.sym} 1480 625 0 1 {name=l306 lab=vss}
C {devices/lab_wire.sym} 850 880 0 0 {name=l307 lab=vss}
C {devices/lab_wire.sym} -825 610 2 0 {name=l308 lab=vss}
C {devices/lab_wire.sym} 4655 610 2 0 {name=l309 lab=vss}
C {devices/ipin.sym} -1915 520 0 0 {name=p0 lab=clk_chin_not}
C {devices/ipin.sym} -1385 520 0 0 {name=p1 lab=clk_chin}
C {devices/ipin.sym} -340 520 0 0 {name=p2 lab=clk_phi_1}
C {devices/ipin.sym} -1070 780 0 0 {name=p3 lab=clk_chout}
C {devices/ipin.sym} -755 780 0 0 {name=p4 lab=clk_chout_not}
C {devices/ipin.sym} 650 780 0 0 {name=p5 lab=clk_phi_2}
C {devices/ipin.sym} -1650 780 0 0 {name=p6 lab=clk_chfb}
C {devices/ipin.sym} -490 780 0 0 {name=p7 lab=clk_chfb_not}
C {devices/iopin.sym} -3115 -140 0 0 {name=p8 lab=vdd}
C {devices/iopin.sym} -3115 1180 0 0 {name=p9 lab=vss}
C {devices/opin.sym} 1805 330 0 0 {name=p10 lab=voutn}
C {devices/opin.sym} 5185 840 0 0 {name=p11 lab=voutp}
C {devices/iopin.sym} 3845 1320 0 0 {name=p12 lab=vref}
C {devices/opin.sym} 9095 490 0 0 {name=p13 lab=vinp}
C {devices/opin.sym} 9095 610 0 0 {name=p14 lab=vinn}
