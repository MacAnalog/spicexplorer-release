v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_004_fan_chopper_rrl} -3095 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 955 650 0 0 {name=CAZ1_RRL value='x_dut_caz1_rrl_value'}
C {devices/capa_np.sym} 1215 650 0 0 {name=CAZ2_RRL value='x_dut_caz2_rrl_value'}
C {devices/capa_np.sym} 695 650 0 0 {name=CFB1_MAIN value='x_dut_cfb1_main_value'}
C {devices/capa_np.sym} 1475 650 0 0 {name=CFB2_MAIN value='x_dut_cfb2_main_value'}
C {devices/capa_np.sym} 2520 520 0 0 {name=CIN1_MAIN value='x_dut_cin1_main_value'}
C {devices/capa_np.sym} 2780 520 0 0 {name=CIN2_MAIN value='x_dut_cin2_main_value'}
C {devices/capa_np.sym} 955 910 0 0 {name=CINT1_RRL value='x_dut_cint1_rrl_value'}
C {devices/capa_np.sym} 1215 910 0 0 {name=CINT2_RRL value='x_dut_cint2_rrl_value'}
C {devices/capa_np.sym} 740 1040 0 0 {name=CIN_1_RRL value='cin_val_rrl'}
C {devices/capa_np.sym} 4850 520 0 0 {name=CIN_SERVO_CMFB value='cin_val_cmfb'}
C {devices/capa_np.sym} 5165 520 0 0 {name=CM1_MAIN value='x_dut_cm1_main_value'}
C {devices/capa_np.sym} 5415 520 0 0 {name=CM2_MAIN value='x_dut_cm2_main_value'}
C {devices/capa_np.sym} 5670 520 1 0 {name=COUT_1_RRL value='cout_val_rrl'}
C {devices/capa_np.sym} 1500 910 0 0 {name=COUT_SERVO_CMFB value='cout_val_cmfb'}
C {devices/capa_np.sym} 1745 650 0 0 {name=CS1_RRL value='x_dut_cs1_rrl_value'}
C {devices/capa_np.sym} 345 650 0 0 {name=CS2_RRL value='x_dut_cs2_rrl_value'}
C {devices/res_np.sym} 3040 520 0 0 {name=RB1_MAIN value='x_dut_rb1_main_value'}
C {devices/res_np.sym} 3315 520 0 0 {name=RB2_MAIN value='x_dut_rb2_main_value'}
C {devices/res_np.sym} 500 1040 0 0 {name=RIN_1_RRL value='rin_val_rrl'}
C {devices/res_np.sym} -2375 520 0 0 {name=RIN_SERVO_CMFB value='rin_val_cmfb'}
C {devices/res_np.sym} 1265 390 0 0 {name=RMN_CMFB value='x_dut_rmn_cmfb_value'}
C {devices/res_np.sym} 990 390 0 0 {name=RMP_CMFB value='x_dut_rmp_cmfb_value'}
C {devices/res_np.sym} 5855 520 1 0 {name=ROUT_1_RRL value='rout_val_rrl'}
C {devices/res_np.sym} 480 910 0 0 {name=ROUT_SERVO_CMFB value='rout_val_cmfb'}
C {devices/vsource_np.sym} -2715 1040 0 0 {name=VB1_MAIN value="dc {vb1_main}"}
C {devices/vsource_np.sym} -2715 780 0 0 {name=VB1_RRL value="dc {vb1_rrl}"}
C {devices/vsource_np.sym} -2715 520 0 0 {name=VB2_MAIN value="dc {vb2_main}"}
C {devices/vsource_np.sym} -2715 260 0 0 {name=VB2_RRL value="dc {vb2_rrl}"}
C {devices/vsource_np.sym} -2715 0 0 0 {name=VB3_MAIN value="dc {vb3_main}"}
C {devices/vsource_np.sym} -3055 1040 0 0 {name=VB3_RRL value="dc {vb3_rrl}"}
C {devices/vsource_np.sym} -3055 780 0 0 {name=VB40 value="dc {vb40}"}
C {devices/vsource_np.sym} -3055 520 0 0 {name=VB4_RRL value="dc {vb4_rrl}"}
C {devices/vsource_np.sym} -3055 260 0 0 {name=VREFCM value="dc {vcm_ref}"}
C {devices/sg13_lv_pmos_np.sym} 685 260 0 1 {name=M10_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_main_w l=x_dut_xm10_main_l m=x_dut_xm10_main_m}
C {devices/sg13_lv_pmos_np.sym} 190 520 0 1 {name=M10_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_rrl_w l=x_dut_xm10_opamp_rrl_l m=x_dut_xm10_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2295 260 0 0 {name=M11_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_main_w l=x_dut_xm11_main_l m=x_dut_xm11_main_m}
C {devices/sg13_lv_nmos_np.sym} -210 780 0 1 {name=M11_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_opamp_rrl_w l=x_dut_xm11_opamp_rrl_l m=x_dut_xm11_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 6045 520 0 0 {name=M12_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_main_w l=x_dut_xm12_main_l m=x_dut_xm12_main_m}
C {devices/sg13_lv_nmos_np.sym} 1225 780 0 0 {name=M12_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_opamp_rrl_w l=x_dut_xm12_opamp_rrl_l m=x_dut_xm12_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 685 520 0 1 {name=M13_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_main_w l=x_dut_xm13_main_l m=x_dut_xm13_main_m}
C {devices/sg13_lv_nmos_np.sym} -210 1040 0 1 {name=M13_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_opamp_rrl_w l=x_dut_xm13_opamp_rrl_l m=x_dut_xm13_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 955 260 0 1 {name=M14_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_main_w l=x_dut_xm14_main_l m=x_dut_xm14_main_m}
C {devices/sg13_lv_nmos_np.sym} 1225 1040 0 0 {name=M14_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_opamp_rrl_w l=x_dut_xm14_opamp_rrl_l m=x_dut_xm14_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1215 260 0 1 {name=M15_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_main_w l=x_dut_xm15_main_l m=x_dut_xm15_main_m}
C {devices/sg13_lv_nmos_np.sym} -1035 520 0 1 {name=M15_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_opamp_rrl_w l=x_dut_xm15_opamp_rrl_l m=x_dut_xm15_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 920 520 0 1 {name=M16_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_main_w l=x_dut_xm16_main_l m=x_dut_xm16_main_m}
C {devices/sg13_lv_nmos_np.sym} 3755 520 0 1 {name=M16_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_opamp_rrl_w l=x_dut_xm16_opamp_rrl_l m=x_dut_xm16_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 445 520 0 1 {name=M17_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_main_w l=x_dut_xm17_main_l m=x_dut_xm17_main_m}
C {devices/sg13_lv_nmos_np.sym} 6275 520 0 0 {name=M18_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_main_w l=x_dut_xm18_main_l m=x_dut_xm18_main_m}
C {devices/sg13_lv_pmos_np.sym} 6505 520 0 0 {name=M19_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_main_w l=x_dut_xm19_main_l m=x_dut_xm19_main_m}
C {devices/sg13_lv_nmos_np.sym} 1695 780 0 1 {name=M1_CHRRL_1_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_1_rrl_w l=x_dut_xm1_chrrl_1_rrl_l m=x_dut_xm1_chrrl_1_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1970 780 0 1 {name=M1_CHRRL_2_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_2_rrl_w l=x_dut_xm1_chrrl_2_rrl_l m=x_dut_xm1_chrrl_2_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2245 780 0 1 {name=M1_CHRRL_3_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_3_rrl_w l=x_dut_xm1_chrrl_3_rrl_l m=x_dut_xm1_chrrl_3_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2520 780 0 1 {name=M1_CHRRL_4_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_4_rrl_w l=x_dut_xm1_chrrl_4_rrl_l m=x_dut_xm1_chrrl_4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 955 0 0 1 {name=M1_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_main_w l=x_dut_xm1_main_l m=x_dut_xm1_main_m}
C {devices/sg13_lv_pmos_np.sym} 1215 0 0 1 {name=M1_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_opamp_rrl_w l=x_dut_xm1_opamp_rrl_l m=x_dut_xm1_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1695 1040 0 1 {name=M1_S1_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s1_rrl_w l=x_dut_xm1_s1_rrl_l m=x_dut_xm1_s1_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 295 1040 0 1 {name=M1_S2_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s2_rrl_w l=x_dut_xm1_s2_rrl_l m=x_dut_xm1_s2_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1155 520 0 1 {name=M1_S3_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s3_rrl_w l=x_dut_xm1_s3_rrl_l m=x_dut_xm1_s3_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1390 520 0 1 {name=M1_S4_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s4_rrl_w l=x_dut_xm1_s4_rrl_l m=x_dut_xm1_s4_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 685 780 0 1 {name=M1_S5_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s5_rrl_w l=x_dut_xm1_s5_rrl_l m=x_dut_xm1_s5_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 920 780 0 1 {name=M1_S6_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s6_rrl_w l=x_dut_xm1_s6_rrl_l m=x_dut_xm1_s6_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2780 780 0 1 {name=M20_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_main_w l=x_dut_xm20_main_l m=x_dut_xm20_main_m}
C {devices/sg13_lv_pmos_np.sym} -580 780 0 1 {name=M21_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_main_w l=x_dut_xm21_main_l m=x_dut_xm21_main_m}
C {devices/sg13_lv_nmos_np.sym} 3040 780 0 1 {name=M22_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_main_w l=x_dut_xm22_main_l m=x_dut_xm22_main_m}
C {devices/sg13_lv_pmos_np.sym} -805 780 0 1 {name=M23_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_main_w l=x_dut_xm23_main_l m=x_dut_xm23_main_m}
C {devices/sg13_lv_nmos_np.sym} -1310 520 0 1 {name=M24_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_main_w l=x_dut_xm24_main_l m=x_dut_xm24_main_m}
C {devices/sg13_lv_pmos_np.sym} 3980 520 0 1 {name=M25_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm25_main_w l=x_dut_xm25_main_l m=x_dut_xm25_main_m}
C {devices/sg13_lv_nmos_np.sym} -1585 520 0 1 {name=M26_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm26_main_w l=x_dut_xm26_main_l m=x_dut_xm26_main_m}
C {devices/sg13_lv_pmos_np.sym} 4210 520 0 1 {name=M27_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm27_main_w l=x_dut_xm27_main_l m=x_dut_xm27_main_m}
C {devices/sg13_lv_nmos_np.sym} -170 520 0 1 {name=M28_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm28_main_w l=x_dut_xm28_main_l m=x_dut_xm28_main_m}
C {devices/sg13_lv_pmos_np.sym} -430 520 0 1 {name=M29_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm29_main_w l=x_dut_xm29_main_l m=x_dut_xm29_main_m}
C {devices/sg13_lv_pmos_np.sym} 3315 780 0 1 {name=M2_CHRRL_1_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_1_rrl_w l=x_dut_xm2_chrrl_1_rrl_l m=x_dut_xm2_chrrl_1_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -1035 780 0 1 {name=M2_CHRRL_2_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_2_rrl_w l=x_dut_xm2_chrrl_2_rrl_l m=x_dut_xm2_chrrl_2_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 3755 780 0 1 {name=M2_CHRRL_3_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_3_rrl_w l=x_dut_xm2_chrrl_3_rrl_l m=x_dut_xm2_chrrl_3_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -1310 780 0 1 {name=M2_CHRRL_4_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_4_rrl_w l=x_dut_xm2_chrrl_4_rrl_l m=x_dut_xm2_chrrl_4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1475 260 0 1 {name=M2_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_main_w l=x_dut_xm2_main_l m=x_dut_xm2_main_m}
C {devices/sg13_lv_pmos_np.sym} 1725 260 0 0 {name=M2_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_rrl_w l=x_dut_xm2_opamp_rrl_l m=x_dut_xm2_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1970 1040 0 1 {name=M2_S1_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s1_rrl_w l=x_dut_xm2_s1_rrl_l m=x_dut_xm2_s1_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 60 1040 0 1 {name=M2_S2_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s2_rrl_w l=x_dut_xm2_s2_rrl_l m=x_dut_xm2_s2_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2135 520 0 1 {name=M2_S3_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s3_rrl_w l=x_dut_xm2_s3_rrl_l m=x_dut_xm2_s3_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -655 520 0 1 {name=M2_S4_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s4_rrl_w l=x_dut_xm2_s4_rrl_l m=x_dut_xm2_s4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 445 780 0 1 {name=M2_S5_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s5_rrl_w l=x_dut_xm2_s5_rrl_l m=x_dut_xm2_s5_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 210 780 0 1 {name=M2_S6_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s6_rrl_w l=x_dut_xm2_s6_rrl_l m=x_dut_xm2_s6_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 6730 520 0 0 {name=M30_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm30_main_w l=x_dut_xm30_main_l m=x_dut_xm30_main_m}
C {devices/sg13_lv_pmos_np.sym} 6960 520 0 0 {name=M31_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm31_main_w l=x_dut_xm31_main_l m=x_dut_xm31_main_m}
C {devices/sg13_lv_nmos_np.sym} -1815 520 0 1 {name=M32_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm32_main_w l=x_dut_xm32_main_l m=x_dut_xm32_main_m}
C {devices/sg13_lv_pmos_np.sym} 4435 520 0 1 {name=M33_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm33_main_w l=x_dut_xm33_main_l m=x_dut_xm33_main_m}
C {devices/sg13_lv_nmos_np.sym} -2045 520 0 1 {name=M34_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm34_main_w l=x_dut_xm34_main_l m=x_dut_xm34_main_m}
C {devices/sg13_lv_pmos_np.sym} 4665 520 0 1 {name=M35_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm35_main_w l=x_dut_xm35_main_l m=x_dut_xm35_main_m}
C {devices/sg13_lv_nmos_np.sym} 3980 780 0 1 {name=M36_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm36_main_w l=x_dut_xm36_main_l m=x_dut_xm36_main_m}
C {devices/sg13_lv_pmos_np.sym} -1585 780 0 1 {name=M37_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm37_main_w l=x_dut_xm37_main_l m=x_dut_xm37_main_m}
C {devices/sg13_lv_nmos_np.sym} 4210 780 0 1 {name=M38_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm38_main_w l=x_dut_xm38_main_l m=x_dut_xm38_main_m}
C {devices/sg13_lv_pmos_np.sym} -1815 780 0 1 {name=M39_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm39_main_w l=x_dut_xm39_main_l m=x_dut_xm39_main_m}
C {devices/sg13_lv_pmos_np.sym} -100 260 0 1 {name=M3_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_main_w l=x_dut_xm3_main_l m=x_dut_xm3_main_m}
C {devices/sg13_lv_pmos_np.sym} 190 260 0 1 {name=M3_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_rrl_w l=x_dut_xm3_opamp_rrl_l m=x_dut_xm3_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 4435 780 0 1 {name=M4_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_main_w l=x_dut_xm4_main_l m=x_dut_xm4_main_m}
C {devices/sg13_lv_pmos_np.sym} 1475 0 0 1 {name=M4_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_opamp_rrl_w l=x_dut_xm4_opamp_rrl_l m=x_dut_xm4_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} -2045 780 0 1 {name=M5_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_main_w l=x_dut_xm5_main_l m=x_dut_xm5_main_m}
C {devices/sg13_lv_pmos_np.sym} -320 260 0 1 {name=M5_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_opamp_rrl_w l=x_dut_xm5_opamp_rrl_l m=x_dut_xm5_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 685 0 0 1 {name=M6_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_main_w l=x_dut_xm6_main_l m=x_dut_xm6_main_m}
C {devices/sg13_lv_pmos_np.sym} 2780 260 0 1 {name=M6_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_opamp_rrl_w l=x_dut_xm6_opamp_rrl_l m=x_dut_xm6_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2295 0 0 0 {name=M7_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_main_w l=x_dut_xm7_main_l m=x_dut_xm7_main_m}
C {devices/sg13_lv_pmos_np.sym} -580 260 0 1 {name=M7_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_opamp_rrl_w l=x_dut_xm7_opamp_rrl_l m=x_dut_xm7_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1695 0 0 1 {name=M8_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_main_w l=x_dut_xm8_main_l m=x_dut_xm8_main_m}
C {devices/sg13_lv_pmos_np.sym} 3040 260 0 1 {name=M8_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_opamp_rrl_w l=x_dut_xm8_opamp_rrl_l m=x_dut_xm8_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 295 0 0 1 {name=M9_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_main_w l=x_dut_xm9_main_l m=x_dut_xm9_main_m}
C {devices/sg13_lv_pmos_np.sym} 1725 520 0 0 {name=M9_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_rrl_w l=x_dut_xm9_opamp_rrl_l m=x_dut_xm9_opamp_rrl_m}
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
N -2375 430 -2375 490 {}
N -2375 550 -2375 610 {}
N -2125 520 -2125 614 {}
N -2125 780 -2125 874 {}
N -2065 430 -2065 490 {}
N -2065 550 -2065 610 {}
N -2065 690 -2065 750 {}
N -2065 810 -2065 1180 {}
N -2025 520 -2025 580 {}
N -2025 780 -2025 840 {}
N -1895 520 -1895 614 {}
N -1895 780 -1895 874 {}
N -1835 430 -1835 490 {}
N -1835 550 -1835 610 {}
N -1835 690 -1835 750 {}
N -1835 810 -1835 870 {}
N -1795 520 -1795 580 {}
N -1795 780 -1795 840 {}
N -1665 520 -1665 614 {}
N -1665 780 -1665 874 {}
N -1605 430 -1605 490 {}
N -1605 550 -1605 610 {}
N -1605 690 -1605 750 {}
N -1605 810 -1605 870 {}
N -1565 520 -1565 580 {}
N -1565 780 -1565 840 {}
N -1390 520 -1390 614 {}
N -1390 780 -1390 874 {}
N -1330 430 -1330 490 {}
N -1330 550 -1330 610 {}
N -1330 690 -1330 750 {}
N -1330 810 -1330 870 {}
N -1290 520 -1290 580 {}
N -1290 780 -1290 840 {}
N -1115 520 -1115 614 {}
N -1115 780 -1115 874 {}
N -1055 430 -1055 490 {}
N -1055 550 -1055 610 {}
N -1055 690 -1055 750 {}
N -1055 810 -1055 870 {}
N -1015 450 -1015 520 {}
N -1015 780 -1015 840 {}
N -885 780 -885 874 {}
N -825 690 -825 750 {}
N -825 810 -825 870 {}
N -785 780 -785 840 {}
N -735 520 -735 614 {}
N -675 430 -675 490 {}
N -675 550 -675 610 {}
N -660 260 -660 354 {}
N -660 780 -660 874 {}
N -635 520 -635 580 {}
N -600 170 -600 230 {}
N -600 290 -600 350 {}
N -600 690 -600 750 {}
N -600 810 -600 870 {}
N -560 780 -560 840 {}
N -510 520 -510 614 {}
N -450 430 -450 490 {}
N -450 550 -450 610 {}
N -410 520 -410 580 {}
N -400 260 -400 354 {}
N -340 200 -340 230 {}
N -340 290 -340 320 {}
N -300 260 -300 320 {}
N -290 780 -290 874 {}
N -290 1040 -290 1134 {}
N -250 520 -250 614 {}
N -230 690 -230 750 {}
N -230 810 -230 870 {}
N -230 950 -230 1010 {}
N -230 1070 -230 1180 {}
N -190 430 -190 490 {}
N -190 550 -190 610 {}
N -190 1040 -190 1100 {}
N -180 260 -180 354 {}
N -150 520 -150 580 {}
N -120 170 -120 230 {}
N -120 290 -120 350 {}
N -80 260 -80 320 {}
N -20 1040 -20 1134 {}
N 40 950 40 1010 {}
N 40 1070 40 1180 {}
N 80 1040 80 1100 {}
N 110 260 110 354 {}
N 110 520 110 614 {}
N 130 780 130 874 {}
N 170 170 170 230 {}
N 170 290 170 350 {}
N 170 430 170 490 {}
N 170 550 170 610 {}
N 190 690 190 750 {}
N 190 810 190 870 {}
N 210 520 210 580 {}
N 215 0 215 94 {}
N 215 1040 215 1134 {}
N 230 780 230 840 {}
N 275 -140 275 -30 {}
N 275 30 275 90 {}
N 275 980 275 1010 {}
N 275 1070 275 1180 {}
N 345 60 345 620 {}
N 345 680 345 710 {}
N 365 520 365 614 {}
N 365 780 365 874 {}
N 425 430 425 490 {}
N 425 550 425 610 {}
N 425 690 425 750 {}
N 425 810 425 870 {}
N 465 460 465 520 {}
N 480 940 480 970 {}
N 500 1070 500 1130 {}
N 605 0 605 94 {}
N 605 260 605 354 {}
N 605 520 605 614 {}
N 605 780 605 874 {}
N 665 -140 665 -30 {}
N 665 30 665 90 {}
N 665 170 665 230 {}
N 665 290 665 350 {}
N 665 430 665 490 {}
N 665 550 665 610 {}
N 665 690 665 750 {}
N 665 810 665 870 {}
N 695 560 695 620 {}
N 695 680 695 740 {}
N 705 0 705 60 {}
N 705 260 705 320 {}
N 705 460 705 520 {}
N 705 780 705 840 {}
N 735 780 735 1040 {}
N 740 950 740 1010 {}
N 740 1070 740 1100 {}
N 840 520 840 614 {}
N 840 780 840 874 {}
N 875 0 875 94 {}
N 875 260 875 354 {}
N 900 430 900 490 {}
N 900 550 900 610 {}
N 900 690 900 750 {}
N 900 810 900 870 {}
N 935 -140 935 -30 {}
N 935 30 935 90 {}
N 935 170 935 230 {}
N 935 290 935 350 {}
N 955 560 955 620 {}
N 955 680 955 740 {}
N 955 850 955 880 {}
N 955 940 955 1000 {}
N 975 0 975 60 {}
N 975 200 975 260 {}
N 990 330 990 360 {}
N 990 420 990 450 {}
N 1075 520 1075 614 {}
N 1135 0 1135 94 {}
N 1135 260 1135 354 {}
N 1135 430 1135 490 {}
N 1135 550 1135 610 {}
N 1195 -140 1195 -30 {}
N 1195 30 1195 90 {}
N 1195 170 1195 230 {}
N 1195 290 1195 350 {}
N 1215 560 1215 620 {}
N 1215 680 1215 740 {}
N 1215 820 1215 880 {}
N 1215 940 1215 1000 {}
N 1235 0 1235 60 {}
N 1235 200 1235 260 {}
N 1245 690 1245 750 {}
N 1245 810 1245 870 {}
N 1245 950 1245 1010 {}
N 1245 1070 1245 1180 {}
N 1265 300 1265 360 {}
N 1265 420 1265 480 {}
N 1305 780 1305 874 {}
N 1305 1040 1305 1134 {}
N 1310 520 1310 614 {}
N 1370 430 1370 490 {}
N 1370 550 1370 610 {}
N 1395 0 1395 94 {}
N 1395 260 1395 354 {}
N 1440 520 1440 1040 {}
N 1455 -140 1455 -30 {}
N 1455 30 1455 90 {}
N 1455 170 1455 230 {}
N 1455 290 1455 350 {}
N 1475 560 1475 620 {}
N 1475 680 1475 740 {}
N 1495 0 1495 60 {}
N 1500 820 1500 880 {}
N 1500 940 1500 1000 {}
N 1615 0 1615 94 {}
N 1615 780 1615 874 {}
N 1615 1040 1615 1134 {}
N 1675 -140 1675 -30 {}
N 1675 30 1675 90 {}
N 1675 690 1675 750 {}
N 1675 810 1675 870 {}
N 1675 950 1675 1010 {}
N 1675 1070 1675 1180 {}
N 1715 780 1715 840 {}
N 1715 1040 1715 1100 {}
N 1745 170 1745 230 {}
N 1745 290 1745 350 {}
N 1745 430 1745 490 {}
N 1745 590 1745 620 {}
N 1745 680 1745 740 {}
N 1805 260 1805 354 {}
N 1805 520 1805 614 {}
N 1890 780 1890 874 {}
N 1890 1040 1890 1134 {}
N 1950 690 1950 750 {}
N 1950 810 1950 870 {}
N 1950 950 1950 1010 {}
N 1950 1070 1950 1180 {}
N 1990 780 1990 840 {}
N 2055 520 2055 614 {}
N 2115 430 2115 490 {}
N 2115 550 2115 610 {}
N 2165 780 2165 874 {}
N 2225 690 2225 750 {}
N 2225 810 2225 870 {}
N 2265 780 2265 840 {}
N 2315 -140 2315 -30 {}
N 2315 30 2315 90 {}
N 2315 170 2315 230 {}
N 2315 290 2315 350 {}
N 2375 0 2375 94 {}
N 2375 260 2375 354 {}
N 2440 780 2440 874 {}
N 2500 690 2500 750 {}
N 2500 810 2500 870 {}
N 2520 430 2520 490 {}
N 2520 550 2520 610 {}
N 2540 780 2540 840 {}
N 2700 260 2700 354 {}
N 2700 780 2700 874 {}
N 2760 170 2760 230 {}
N 2760 290 2760 350 {}
N 2760 690 2760 750 {}
N 2760 810 2760 870 {}
N 2780 430 2780 490 {}
N 2780 550 2780 610 {}
N 2800 260 2800 320 {}
N 2800 780 2800 840 {}
N 2960 260 2960 354 {}
N 2960 780 2960 874 {}
N 3020 200 3020 230 {}
N 3020 290 3020 350 {}
N 3020 690 3020 750 {}
N 3020 810 3020 870 {}
N 3040 430 3040 490 {}
N 3040 550 3040 610 {}
N 3060 780 3060 840 {}
N 3235 780 3235 874 {}
N 3295 690 3295 750 {}
N 3295 810 3295 870 {}
N 3315 430 3315 490 {}
N 3315 550 3315 610 {}
N 3675 520 3675 614 {}
N 3675 780 3675 874 {}
N 3735 430 3735 490 {}
N 3735 550 3735 610 {}
N 3735 690 3735 750 {}
N 3735 810 3735 870 {}
N 3775 450 3775 520 {}
N 3775 780 3775 840 {}
N 3900 520 3900 614 {}
N 3900 780 3900 874 {}
N 3960 430 3960 490 {}
N 3960 550 3960 610 {}
N 3960 690 3960 750 {}
N 3960 810 3960 870 {}
N 4000 520 4000 580 {}
N 4000 780 4000 840 {}
N 4130 520 4130 614 {}
N 4130 780 4130 874 {}
N 4190 430 4190 490 {}
N 4190 550 4190 610 {}
N 4190 690 4190 750 {}
N 4190 810 4190 870 {}
N 4230 520 4230 580 {}
N 4230 780 4230 840 {}
N 4355 520 4355 614 {}
N 4355 780 4355 874 {}
N 4415 430 4415 490 {}
N 4415 550 4415 610 {}
N 4415 690 4415 750 {}
N 4415 810 4415 1180 {}
N 4455 520 4455 580 {}
N 4585 520 4585 614 {}
N 4645 430 4645 490 {}
N 4645 550 4645 610 {}
N 4685 520 4685 580 {}
N 4850 430 4850 490 {}
N 4850 550 4850 610 {}
N 5165 430 5165 490 {}
N 5165 550 5165 610 {}
N 5415 430 5415 490 {}
N 5415 550 5415 610 {}
N 5610 460 5610 520 {}
N 5640 460 5640 520 {}
N 5700 520 5700 580 {}
N 5730 320 5730 520 {}
N 5885 520 5885 580 {}
N 6025 460 6025 520 {}
N 6065 430 6065 490 {}
N 6065 550 6065 610 {}
N 6125 520 6125 614 {}
N 6295 460 6295 490 {}
N 6295 550 6295 610 {}
N 6355 520 6355 614 {}
N 6525 460 6525 490 {}
N 6525 550 6525 610 {}
N 6585 520 6585 614 {}
N 6750 460 6750 490 {}
N 6750 550 6750 610 {}
N 6810 520 6810 614 {}
N 6980 460 6980 490 {}
N 6980 550 6980 580 {}
N 7040 520 7040 614 {}
N -3115 -140 7215 -140 {}
N 215 0 275 0 {}
N 315 0 375 0 {}
N 605 0 665 0 {}
N 705 0 735 0 {}
N 875 0 935 0 {}
N 975 0 1005 0 {}
N 1135 0 1195 0 {}
N 1235 0 1265 0 {}
N 1395 0 1455 0 {}
N 1495 0 1525 0 {}
N 1615 0 1675 0 {}
N 1715 0 2275 0 {}
N 2315 0 2375 0 {}
N 275 60 345 60 {}
N 1675 60 1745 60 {}
N -600 200 -340 200 {}
N 2760 200 3020 200 {}
N -660 260 -600 260 {}
N -560 260 -530 260 {}
N -400 260 -340 260 {}
N -300 260 -230 260 {}
N -180 260 -120 260 {}
N -80 260 -50 260 {}
N 110 260 170 260 {}
N 210 260 270 260 {}
N 605 260 665 260 {}
N 705 260 735 260 {}
N 875 260 935 260 {}
N 975 260 1005 260 {}
N 1135 260 1195 260 {}
N 1395 260 1455 260 {}
N 1495 260 1555 260 {}
N 1645 260 1705 260 {}
N 1745 260 1805 260 {}
N 2215 260 2275 260 {}
N 2315 260 2375 260 {}
N 2700 260 2760 260 {}
N 2800 260 2830 260 {}
N 2960 260 3020 260 {}
N 3060 260 3120 260 {}
N -600 320 -340 320 {}
N 930 360 990 360 {}
N 930 420 990 420 {}
N -1055 450 -1015 450 {}
N 3735 450 3775 450 {}
N 6065 460 6980 460 {}
N -2125 520 -2065 520 {}
N -2025 520 -1995 520 {}
N -1895 520 -1835 520 {}
N -1795 520 -1765 520 {}
N -1665 520 -1605 520 {}
N -1565 520 -1535 520 {}
N -1390 520 -1330 520 {}
N -1290 520 -1260 520 {}
N -1115 520 -1055 520 {}
N -735 520 -675 520 {}
N -635 520 -605 520 {}
N -510 520 -450 520 {}
N -410 520 -380 520 {}
N -250 520 -190 520 {}
N 110 520 170 520 {}
N 210 520 240 520 {}
N 365 520 425 520 {}
N 465 520 495 520 {}
N 605 520 665 520 {}
N 705 520 735 520 {}
N 840 520 900 520 {}
N 940 520 1000 520 {}
N 1075 520 1135 520 {}
N 1175 520 1235 520 {}
N 1310 520 1370 520 {}
N 1410 520 1470 520 {}
N 1645 520 1705 520 {}
N 1745 520 1805 520 {}
N 2055 520 2115 520 {}
N 2155 520 2215 520 {}
N 3675 520 3735 520 {}
N 3900 520 3960 520 {}
N 4000 520 4030 520 {}
N 4130 520 4190 520 {}
N 4230 520 4260 520 {}
N 4355 520 4415 520 {}
N 4455 520 4485 520 {}
N 4585 520 4645 520 {}
N 4685 520 4715 520 {}
N 5610 520 5640 520 {}
N 5700 520 5730 520 {}
N 5765 520 5825 520 {}
N 5885 520 5915 520 {}
N 5995 520 6025 520 {}
N 6065 520 6125 520 {}
N 6225 520 6255 520 {}
N 6295 520 6355 520 {}
N 6455 520 6485 520 {}
N 6525 520 6585 520 {}
N 6680 520 6710 520 {}
N 6750 520 6810 520 {}
N 6910 520 6940 520 {}
N 6980 520 7040 520 {}
N 6750 580 6980 580 {}
N 1745 590 5165 590 {}
N 285 680 345 680 {}
N 4415 720 6065 720 {}
N -2125 780 -2065 780 {}
N -2025 780 -1995 780 {}
N -1895 780 -1835 780 {}
N -1795 780 -1765 780 {}
N -1665 780 -1605 780 {}
N -1565 780 -1535 780 {}
N -1390 780 -1330 780 {}
N -1290 780 -1260 780 {}
N -1115 780 -1055 780 {}
N -1015 780 -985 780 {}
N -885 780 -825 780 {}
N -785 780 -755 780 {}
N -660 780 -600 780 {}
N -560 780 -530 780 {}
N -290 780 -230 780 {}
N -190 780 -130 780 {}
N 130 780 190 780 {}
N 230 780 260 780 {}
N 365 780 425 780 {}
N 465 780 525 780 {}
N 605 780 665 780 {}
N 705 780 735 780 {}
N 840 780 900 780 {}
N 940 780 1000 780 {}
N 1145 780 1205 780 {}
N 1245 780 1305 780 {}
N 1615 780 1675 780 {}
N 1890 780 1950 780 {}
N 2165 780 2225 780 {}
N 2265 780 2295 780 {}
N 2440 780 2500 780 {}
N 2540 780 2570 780 {}
N 2700 780 2760 780 {}
N 2800 780 2830 780 {}
N 2960 780 3020 780 {}
N 3060 780 3090 780 {}
N 3235 780 3295 780 {}
N 3335 780 3395 780 {}
N 3675 780 3735 780 {}
N 3775 780 3805 780 {}
N 3900 780 3960 780 {}
N 4000 780 4030 780 {}
N 4130 780 4190 780 {}
N 4230 780 4260 780 {}
N 4355 780 4415 780 {}
N 4455 780 4515 780 {}
N 420 880 480 880 {}
N 895 880 955 880 {}
N 420 940 480 940 {}
N 40 980 275 980 {}
N 440 1010 500 1010 {}
N -290 1040 -230 1040 {}
N -190 1040 -160 1040 {}
N -20 1040 40 1040 {}
N 80 1040 110 1040 {}
N 215 1040 275 1040 {}
N 315 1040 375 1040 {}
N 1145 1040 1205 1040 {}
N 1245 1040 1305 1040 {}
N 1615 1040 1675 1040 {}
N 1715 1040 1745 1040 {}
N 1890 1040 1950 1040 {}
N 1990 1040 2050 1040 {}
N 500 1100 1215 1100 {}
N -3115 1180 7215 1180 {}
C {devices/lab_wire.sym} -3115 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -3115 1180 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -1795 840 2 0 {name=l2 lab=clk_chfb}
C {devices/lab_wire.sym} -1565 840 2 0 {name=l3 lab=clk_chfb}
C {devices/lab_wire.sym} 2800 840 2 0 {name=l4 lab=clk_chfb}
C {devices/lab_wire.sym} 3060 840 2 0 {name=l5 lab=clk_chfb}
C {devices/lab_wire.sym} -785 840 2 0 {name=l6 lab=clk_chfb_not}
C {devices/lab_wire.sym} -560 840 2 0 {name=l7 lab=clk_chfb_not}
C {devices/lab_wire.sym} 4000 840 2 0 {name=l8 lab=clk_chfb_not}
C {devices/lab_wire.sym} 4230 840 2 0 {name=l9 lab=clk_chfb_not}
C {devices/lab_wire.sym} -1565 580 2 0 {name=l10 lab=clk_chin}
C {devices/lab_wire.sym} -1290 580 2 0 {name=l11 lab=clk_chin}
C {devices/lab_wire.sym} 4455 580 2 0 {name=l12 lab=clk_chin}
C {devices/lab_wire.sym} 4685 580 2 0 {name=l13 lab=clk_chin}
C {devices/lab_wire.sym} -2025 580 2 0 {name=l14 lab=clk_chin_not}
C {devices/lab_wire.sym} -1795 580 2 0 {name=l15 lab=clk_chin_not}
C {devices/lab_wire.sym} 4000 580 2 0 {name=l16 lab=clk_chin_not}
C {devices/lab_wire.sym} 4230 580 2 0 {name=l17 lab=clk_chin_not}
C {devices/lab_wire.sym} -1290 840 2 0 {name=l18 lab=clk_chout}
C {devices/lab_wire.sym} -410 580 2 0 {name=l19 lab=clk_chout}
C {devices/lab_wire.sym} 1000 520 0 1 {name=l20 lab=clk_chout}
C {devices/lab_wire.sym} 1715 840 2 0 {name=l21 lab=clk_chout}
C {devices/lab_wire.sym} 1990 840 2 0 {name=l22 lab=clk_chout}
C {devices/lab_wire.sym} 3775 840 2 0 {name=l23 lab=clk_chout}
C {devices/lab_wire.sym} 6255 520 0 0 {name=l24 lab=clk_chout}
C {devices/lab_wire.sym} 6940 520 0 0 {name=l25 lab=clk_chout}
C {devices/lab_wire.sym} -1015 840 2 0 {name=l26 lab=clk_chout_not}
C {devices/lab_wire.sym} -150 580 2 0 {name=l27 lab=clk_chout_not}
C {devices/lab_wire.sym} 465 460 0 1 {name=l28 lab=clk_chout_not}
C {devices/lab_wire.sym} 2265 840 2 0 {name=l29 lab=clk_chout_not}
C {devices/lab_wire.sym} 2540 840 2 0 {name=l30 lab=clk_chout_not}
C {devices/lab_wire.sym} 3395 780 0 1 {name=l31 lab=clk_chout_not}
C {devices/lab_wire.sym} 6485 520 0 0 {name=l32 lab=clk_chout_not}
C {devices/lab_wire.sym} 6710 520 0 0 {name=l33 lab=clk_chout_not}
C {devices/lab_wire.sym} -635 580 2 0 {name=l34 lab=clk_phi_1}
C {devices/lab_wire.sym} 80 1100 2 0 {name=l35 lab=clk_phi_1}
C {devices/lab_wire.sym} 705 840 2 0 {name=l36 lab=clk_phi_1}
C {devices/lab_wire.sym} 1000 780 0 1 {name=l37 lab=clk_phi_1}
C {devices/lab_wire.sym} 2050 1040 0 1 {name=l38 lab=clk_phi_1}
C {devices/lab_wire.sym} 2215 520 0 1 {name=l39 lab=clk_phi_1}
C {devices/lab_wire.sym} 230 840 2 0 {name=l40 lab=clk_phi_2}
C {devices/lab_wire.sym} 375 1040 0 1 {name=l41 lab=clk_phi_2}
C {devices/lab_wire.sym} 525 780 0 1 {name=l42 lab=clk_phi_2}
C {devices/lab_wire.sym} 1235 520 0 1 {name=l43 lab=clk_phi_2}
C {devices/lab_wire.sym} 1470 520 0 1 {name=l44 lab=clk_phi_2}
C {devices/lab_wire.sym} 1715 1100 2 0 {name=l45 lab=clk_phi_2}
C {devices/lab_wire.sym} -2375 430 0 1 {name=l46 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 930 360 0 0 {name=l47 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 1265 480 2 0 {name=l48 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 4850 430 0 1 {name=l49 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 665 90 2 0 {name=l50 lab=main__casc_src_n}
C {devices/lab_wire.sym} 665 170 0 1 {name=l51 lab=main__casc_src_n}
C {devices/lab_wire.sym} 2315 90 2 0 {name=l52 lab=main__casc_src_p}
C {devices/lab_wire.sym} 2315 170 0 1 {name=l53 lab=main__casc_src_p}
C {devices/lab_wire.sym} -1835 690 0 1 {name=l54 lab=main__fbch_n}
C {devices/lab_wire.sym} -825 690 0 1 {name=l55 lab=main__fbch_n}
C {devices/lab_wire.sym} 1475 560 0 1 {name=l56 lab=main__fbch_n}
C {devices/lab_wire.sym} 3020 690 0 1 {name=l57 lab=main__fbch_n}
C {devices/lab_wire.sym} 4190 690 0 1 {name=l58 lab=main__fbch_n}
C {devices/lab_wire.sym} -1605 690 0 1 {name=l59 lab=main__fbch_p}
C {devices/lab_wire.sym} -600 690 0 1 {name=l60 lab=main__fbch_p}
C {devices/lab_wire.sym} 695 560 0 1 {name=l61 lab=main__fbch_p}
C {devices/lab_wire.sym} 2760 690 0 1 {name=l62 lab=main__fbch_p}
C {devices/lab_wire.sym} 3960 690 0 1 {name=l63 lab=main__fbch_p}
C {devices/lab_wire.sym} -2065 690 0 1 {name=l64 lab=main__fold_n}
C {devices/lab_wire.sym} -120 350 2 0 {name=l65 lab=main__fold_n}
C {devices/lab_wire.sym} 665 610 2 0 {name=l66 lab=main__fold_n}
C {devices/lab_wire.sym} 1455 350 2 0 {name=l67 lab=main__fold_p}
C {devices/lab_wire.sym} 4415 690 0 1 {name=l68 lab=main__fold_p}
C {devices/lab_wire.sym} 6065 610 2 0 {name=l69 lab=main__fold_p}
C {devices/lab_wire.sym} 425 610 2 0 {name=l70 lab=main__g2_n}
C {devices/lab_wire.sym} 900 610 2 0 {name=l71 lab=main__g2_n}
C {devices/lab_wire.sym} 1235 200 0 1 {name=l72 lab=main__g2_n}
C {devices/lab_wire.sym} 5415 430 0 1 {name=l73 lab=main__g2_n}
C {devices/lab_wire.sym} 6750 610 2 0 {name=l74 lab=main__g2_n}
C {devices/lab_wire.sym} -450 610 2 0 {name=l75 lab=main__g2_p}
C {devices/lab_wire.sym} -190 610 2 0 {name=l76 lab=main__g2_p}
C {devices/lab_wire.sym} 975 200 0 1 {name=l77 lab=main__g2_p}
C {devices/lab_wire.sym} 5165 430 0 1 {name=l78 lab=main__g2_p}
C {devices/lab_wire.sym} 6295 610 2 0 {name=l79 lab=main__g2_p}
C {devices/lab_wire.sym} 6525 610 2 0 {name=l80 lab=main__g2_p}
C {devices/lab_wire.sym} -2065 610 2 0 {name=l81 lab=main__inch_n}
C {devices/lab_wire.sym} -1330 610 2 0 {name=l82 lab=main__inch_n}
C {devices/lab_wire.sym} 2520 610 2 0 {name=l83 lab=main__inch_n}
C {devices/lab_wire.sym} 3960 610 2 0 {name=l84 lab=main__inch_n}
C {devices/lab_wire.sym} 4645 610 2 0 {name=l85 lab=main__inch_n}
C {devices/lab_wire.sym} -1835 610 2 0 {name=l86 lab=main__inch_p}
C {devices/lab_wire.sym} -1605 610 2 0 {name=l87 lab=main__inch_p}
C {devices/lab_wire.sym} 2780 610 2 0 {name=l88 lab=main__inch_p}
C {devices/lab_wire.sym} 4190 610 2 0 {name=l89 lab=main__inch_p}
C {devices/lab_wire.sym} 4415 610 2 0 {name=l90 lab=main__inch_p}
C {devices/lab_wire.sym} -120 170 0 1 {name=l91 lab=main__tail}
C {devices/lab_wire.sym} 935 90 2 0 {name=l92 lab=main__tail}
C {devices/lab_wire.sym} 1455 170 0 1 {name=l93 lab=main__tail}
C {devices/lab_wire.sym} -2025 840 2 0 {name=l94 lab=main__vb1}
C {devices/lab_wire.sym} 4515 780 0 1 {name=l95 lab=main__vb1}
C {devices/lab_wire.sym} 705 460 0 1 {name=l96 lab=main__vb2}
C {devices/lab_wire.sym} 6025 460 0 1 {name=l97 lab=main__vb2}
C {devices/lab_wire.sym} 705 320 2 0 {name=l98 lab=main__vb3}
C {devices/lab_wire.sym} 2215 260 0 0 {name=l99 lab=main__vb3}
C {devices/lab_wire.sym} -80 320 2 0 {name=l100 lab=main__vsum_n}
C {devices/lab_wire.sym} 695 740 2 0 {name=l101 lab=main__vsum_n}
C {devices/lab_wire.sym} 2520 430 0 1 {name=l102 lab=main__vsum_n}
C {devices/lab_wire.sym} 3040 430 0 1 {name=l103 lab=main__vsum_n}
C {devices/lab_wire.sym} 1475 740 2 0 {name=l104 lab=main__vsum_p}
C {devices/lab_wire.sym} 1555 260 0 1 {name=l105 lab=main__vsum_p}
C {devices/lab_wire.sym} 2780 430 0 1 {name=l106 lab=main__vsum_p}
C {devices/lab_wire.sym} 3315 430 0 1 {name=l107 lab=main__vsum_p}
C {devices/lab_wire.sym} -450 430 0 1 {name=l108 lab=out1_n}
C {devices/lab_wire.sym} -190 430 0 1 {name=l109 lab=out1_n}
C {devices/lab_wire.sym} 425 430 0 1 {name=l110 lab=out1_n}
C {devices/lab_wire.sym} 665 350 2 0 {name=l111 lab=out1_n}
C {devices/lab_wire.sym} 665 430 0 1 {name=l112 lab=out1_n}
C {devices/lab_wire.sym} 900 430 0 1 {name=l113 lab=out1_n}
C {devices/lab_wire.sym} 5640 460 0 1 {name=l114 lab=out1_n}
C {devices/lab_wire.sym} 5765 520 0 0 {name=l115 lab=out1_n}
C {devices/lab_wire.sym} 2315 350 2 0 {name=l116 lab=out1_p}
C {devices/lab_wire.sym} 5700 580 2 0 {name=l117 lab=out1_p}
C {devices/lab_wire.sym} 5885 580 2 0 {name=l118 lab=out1_p}
C {devices/lab_wire.sym} 6065 430 0 1 {name=l119 lab=out1_p}
C {devices/lab_wire.sym} 190 870 2 0 {name=l120 lab=rrl__int_n}
C {devices/lab_wire.sym} 500 1130 2 0 {name=l121 lab=rrl__int_n}
C {devices/lab_wire.sym} 900 870 2 0 {name=l122 lab=rrl__int_n}
C {devices/lab_wire.sym} 1215 1000 2 0 {name=l123 lab=rrl__int_n}
C {devices/lab_wire.sym} 425 870 2 0 {name=l124 lab=rrl__int_p}
C {devices/lab_wire.sym} 440 1010 0 0 {name=l125 lab=rrl__int_p}
C {devices/lab_wire.sym} 665 870 2 0 {name=l126 lab=rrl__int_p}
C {devices/lab_wire.sym} 740 950 0 1 {name=l127 lab=rrl__int_p}
C {devices/lab_wire.sym} 955 1000 2 0 {name=l128 lab=rrl__int_p}
C {devices/lab_wire.sym} -1055 430 0 1 {name=l129 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} -190 1100 2 0 {name=l130 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 1145 1040 0 0 {name=l131 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 2760 350 2 0 {name=l132 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 3020 350 2 0 {name=l133 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} -600 350 2 0 {name=l134 lab=rrl__oa_cm_sense}
C {devices/lab_wire.sym} 3735 430 0 1 {name=l135 lab=rrl__oa_cm_sense}
C {devices/lab_wire.sym} -600 170 0 1 {name=l136 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} 1455 90 2 0 {name=l137 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} 2760 170 0 1 {name=l138 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} -230 870 2 0 {name=l139 lab=rrl__oa_csrc_n}
C {devices/lab_wire.sym} -230 950 0 1 {name=l140 lab=rrl__oa_csrc_n}
C {devices/lab_wire.sym} 1245 870 2 0 {name=l141 lab=rrl__oa_csrc_p}
C {devices/lab_wire.sym} 1245 950 0 1 {name=l142 lab=rrl__oa_csrc_p}
C {devices/lab_wire.sym} 1745 350 2 0 {name=l143 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 1745 430 0 1 {name=l144 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 170 350 2 0 {name=l145 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} 170 430 0 1 {name=l146 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} -675 430 0 1 {name=l147 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 270 260 0 1 {name=l148 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 1215 740 2 0 {name=l149 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 1370 430 0 1 {name=l150 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 955 740 2 0 {name=l151 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 1135 430 0 1 {name=l152 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 1645 260 0 0 {name=l153 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 2115 430 0 1 {name=l154 lab=rrl__oa_inp}
C {devices/lab_wire.sym} -300 320 2 0 {name=l155 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -230 690 0 1 {name=l156 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 425 690 0 1 {name=l157 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 665 690 0 1 {name=l158 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 1135 610 2 0 {name=l159 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 1745 550 0 0 {name=l160 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 2115 610 2 0 {name=l161 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -675 610 2 0 {name=l162 lab=rrl__oa_outp}
C {devices/lab_wire.sym} -560 260 0 0 {name=l163 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 170 610 2 0 {name=l164 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 190 690 0 1 {name=l165 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 900 690 0 1 {name=l166 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1245 690 0 1 {name=l167 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1370 610 2 0 {name=l168 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 170 170 0 1 {name=l169 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 1195 90 2 0 {name=l170 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 1745 170 0 1 {name=l171 lab=rrl__oa_tail}
C {devices/lab_wire.sym} -1055 870 2 0 {name=l172 lab=rrl__sc_n}
C {devices/lab_wire.sym} 285 680 0 0 {name=l173 lab=rrl__sc_n}
C {devices/lab_wire.sym} 1675 950 0 1 {name=l174 lab=rrl__sc_n}
C {devices/lab_wire.sym} 1950 870 2 0 {name=l175 lab=rrl__sc_n}
C {devices/lab_wire.sym} 1950 950 0 1 {name=l176 lab=rrl__sc_n}
C {devices/lab_wire.sym} 2225 870 2 0 {name=l177 lab=rrl__sc_n}
C {devices/lab_wire.sym} 3735 870 2 0 {name=l178 lab=rrl__sc_n}
C {devices/lab_wire.sym} -1330 870 2 0 {name=l179 lab=rrl__sc_p}
C {devices/lab_wire.sym} 40 950 0 1 {name=l180 lab=rrl__sc_p}
C {devices/lab_wire.sym} 1675 870 2 0 {name=l181 lab=rrl__sc_p}
C {devices/lab_wire.sym} 1745 740 2 0 {name=l182 lab=rrl__sc_p}
C {devices/lab_wire.sym} 2500 870 2 0 {name=l183 lab=rrl__sc_p}
C {devices/lab_wire.sym} 3295 870 2 0 {name=l184 lab=rrl__sc_p}
C {devices/lab_wire.sym} -1330 690 0 1 {name=l185 lab=rrl__sum_n}
C {devices/lab_wire.sym} -1055 690 0 1 {name=l186 lab=rrl__sum_n}
C {devices/lab_wire.sym} 1215 560 0 1 {name=l187 lab=rrl__sum_n}
C {devices/lab_wire.sym} 1215 820 0 1 {name=l188 lab=rrl__sum_n}
C {devices/lab_wire.sym} 1950 690 0 1 {name=l189 lab=rrl__sum_n}
C {devices/lab_wire.sym} 2500 690 0 1 {name=l190 lab=rrl__sum_n}
C {devices/lab_wire.sym} 955 560 0 1 {name=l191 lab=rrl__sum_p}
C {devices/lab_wire.sym} 895 880 0 0 {name=l192 lab=rrl__sum_p}
C {devices/lab_wire.sym} 1675 690 0 1 {name=l193 lab=rrl__sum_p}
C {devices/lab_wire.sym} 2225 690 0 1 {name=l194 lab=rrl__sum_p}
C {devices/lab_wire.sym} 3295 690 0 1 {name=l195 lab=rrl__sum_p}
C {devices/lab_wire.sym} 3735 690 0 1 {name=l196 lab=rrl__sum_p}
C {devices/lab_wire.sym} 210 580 2 0 {name=l197 lab=rrl__vb1}
C {devices/lab_wire.sym} 1645 520 0 0 {name=l198 lab=rrl__vb1}
C {devices/lab_wire.sym} -130 780 0 1 {name=l199 lab=rrl__vb2}
C {devices/lab_wire.sym} 1145 780 0 0 {name=l200 lab=rrl__vb2}
C {devices/lab_wire.sym} 1235 60 2 0 {name=l201 lab=rrl__vb3}
C {devices/lab_wire.sym} 1495 60 2 0 {name=l202 lab=rrl__vb3}
C {devices/lab_wire.sym} 2800 320 2 0 {name=l203 lab=rrl__vb4}
C {devices/lab_wire.sym} 3120 260 0 1 {name=l204 lab=rrl__vb4}
C {devices/lab_wire.sym} 375 0 0 1 {name=l205 lab=vb4_ctl}
C {devices/lab_wire.sym} 705 60 2 0 {name=l206 lab=vb4_ctl}
C {devices/lab_wire.sym} 975 60 2 0 {name=l207 lab=vb4_ctl}
C {devices/lab_wire.sym} 1775 0 0 1 {name=l208 lab=vb4_ctl}
C {devices/lab_wire.sym} 420 940 0 0 {name=l209 lab=vcmfb_raw}
C {devices/lab_wire.sym} 1500 1000 2 0 {name=l210 lab=vcmfb_raw}
C {devices/lab_wire.sym} -1835 430 0 1 {name=l211 lab=vinn}
C {devices/lab_wire.sym} -1330 430 0 1 {name=l212 lab=vinn}
C {devices/lab_wire.sym} 3960 430 0 1 {name=l213 lab=vinn}
C {devices/lab_wire.sym} 4415 430 0 1 {name=l214 lab=vinn}
C {devices/lab_wire.sym} -2065 430 0 1 {name=l215 lab=vinp}
C {devices/lab_wire.sym} -1605 430 0 1 {name=l216 lab=vinp}
C {devices/lab_wire.sym} 4190 430 0 1 {name=l217 lab=vinp}
C {devices/lab_wire.sym} 4645 430 0 1 {name=l218 lab=vinp}
C {devices/lab_wire.sym} -1605 870 2 0 {name=l219 lab=voutn}
C {devices/lab_wire.sym} -825 870 2 0 {name=l220 lab=voutn}
C {devices/lab_wire.sym} 275 90 2 0 {name=l221 lab=voutn}
C {devices/lab_wire.sym} 1195 170 0 1 {name=l222 lab=voutn}
C {devices/lab_wire.sym} 1265 300 0 1 {name=l223 lab=voutn}
C {devices/lab_wire.sym} 3020 870 2 0 {name=l224 lab=voutn}
C {devices/lab_wire.sym} 3960 870 2 0 {name=l225 lab=voutn}
C {devices/lab_wire.sym} 5415 610 2 0 {name=l226 lab=voutn}
C {devices/lab_wire.sym} -1835 870 2 0 {name=l227 lab=voutp}
C {devices/lab_wire.sym} -600 870 2 0 {name=l228 lab=voutp}
C {devices/lab_wire.sym} 935 170 0 1 {name=l229 lab=voutp}
C {devices/lab_wire.sym} 930 420 0 0 {name=l230 lab=voutp}
C {devices/lab_wire.sym} 1675 90 2 0 {name=l231 lab=voutp}
C {devices/lab_wire.sym} 1745 620 0 0 {name=l232 lab=voutp}
C {devices/lab_wire.sym} 2760 870 2 0 {name=l233 lab=voutp}
C {devices/lab_wire.sym} 4190 870 2 0 {name=l234 lab=voutp}
C {devices/lab_wire.sym} 5165 610 2 0 {name=l235 lab=voutp}
C {devices/lab_wire.sym} 3040 610 2 0 {name=l236 lab=vref}
C {devices/lab_wire.sym} 3315 610 2 0 {name=l237 lab=vref}
C {devices/lab_wire.sym} -2375 610 2 0 {name=l238 lab=vref_cm}
C {devices/lab_wire.sym} 4850 610 2 0 {name=l239 lab=vref_cm}
C {devices/lab_wire.sym} 605 354 2 0 {name=l240 lab=vdd}
C {devices/lab_wire.sym} 110 614 2 0 {name=l241 lab=vdd}
C {devices/lab_wire.sym} 2375 354 2 0 {name=l242 lab=vdd}
C {devices/lab_wire.sym} 365 614 2 0 {name=l243 lab=vdd}
C {devices/lab_wire.sym} 6585 614 2 0 {name=l244 lab=vdd}
C {devices/lab_wire.sym} 875 94 2 0 {name=l245 lab=vdd}
C {devices/lab_wire.sym} 1135 94 2 0 {name=l246 lab=vdd}
C {devices/lab_wire.sym} -660 874 2 0 {name=l247 lab=vdd}
C {devices/lab_wire.sym} -885 874 2 0 {name=l248 lab=vdd}
C {devices/lab_wire.sym} 3900 614 2 0 {name=l249 lab=vdd}
C {devices/lab_wire.sym} 4130 614 2 0 {name=l250 lab=vdd}
C {devices/lab_wire.sym} -510 614 2 0 {name=l251 lab=vdd}
C {devices/lab_wire.sym} 3235 874 2 0 {name=l252 lab=vdd}
C {devices/lab_wire.sym} -1115 874 2 0 {name=l253 lab=vdd}
C {devices/lab_wire.sym} 3675 874 2 0 {name=l254 lab=vdd}
C {devices/lab_wire.sym} -1390 874 2 0 {name=l255 lab=vdd}
C {devices/lab_wire.sym} 1395 354 2 0 {name=l256 lab=vdd}
C {devices/lab_wire.sym} 1805 354 2 0 {name=l257 lab=vdd}
C {devices/lab_wire.sym} 1890 1134 2 0 {name=l258 lab=vdd}
C {devices/lab_wire.sym} -20 1134 2 0 {name=l259 lab=vdd}
C {devices/lab_wire.sym} 2055 614 2 0 {name=l260 lab=vdd}
C {devices/lab_wire.sym} -735 614 2 0 {name=l261 lab=vdd}
C {devices/lab_wire.sym} 365 874 2 0 {name=l262 lab=vdd}
C {devices/lab_wire.sym} 130 874 2 0 {name=l263 lab=vdd}
C {devices/lab_wire.sym} 7040 614 2 0 {name=l264 lab=vdd}
C {devices/lab_wire.sym} 4355 614 2 0 {name=l265 lab=vdd}
C {devices/lab_wire.sym} 4585 614 2 0 {name=l266 lab=vdd}
C {devices/lab_wire.sym} -1665 874 2 0 {name=l267 lab=vdd}
C {devices/lab_wire.sym} -1895 874 2 0 {name=l268 lab=vdd}
C {devices/lab_wire.sym} -180 354 2 0 {name=l269 lab=vdd}
C {devices/lab_wire.sym} 110 354 2 0 {name=l270 lab=vdd}
C {devices/lab_wire.sym} 1395 94 2 0 {name=l271 lab=vdd}
C {devices/lab_wire.sym} -400 354 2 0 {name=l272 lab=vdd}
C {devices/lab_wire.sym} 605 94 2 0 {name=l273 lab=vdd}
C {devices/lab_wire.sym} 2700 354 2 0 {name=l274 lab=vdd}
C {devices/lab_wire.sym} 2375 94 2 0 {name=l275 lab=vdd}
C {devices/lab_wire.sym} -660 354 2 0 {name=l276 lab=vdd}
C {devices/lab_wire.sym} 1615 94 2 0 {name=l277 lab=vdd}
C {devices/lab_wire.sym} 2960 354 2 0 {name=l278 lab=vdd}
C {devices/lab_wire.sym} 215 94 2 0 {name=l279 lab=vdd}
C {devices/lab_wire.sym} 1805 614 2 0 {name=l280 lab=vdd}
C {devices/lab_wire.sym} -290 874 2 0 {name=l281 lab=vss}
C {devices/lab_wire.sym} 6125 614 2 0 {name=l282 lab=vss}
C {devices/lab_wire.sym} 1305 874 2 0 {name=l283 lab=vss}
C {devices/lab_wire.sym} 605 614 2 0 {name=l284 lab=vss}
C {devices/lab_wire.sym} -290 1134 2 0 {name=l285 lab=vss}
C {devices/lab_wire.sym} 875 354 2 0 {name=l286 lab=vss}
C {devices/lab_wire.sym} 1305 1134 2 0 {name=l287 lab=vss}
C {devices/lab_wire.sym} 1135 354 2 0 {name=l288 lab=vss}
C {devices/lab_wire.sym} -1115 614 2 0 {name=l289 lab=vss}
C {devices/lab_wire.sym} 840 614 2 0 {name=l290 lab=vss}
C {devices/lab_wire.sym} 3675 614 2 0 {name=l291 lab=vss}
C {devices/lab_wire.sym} 6355 614 2 0 {name=l292 lab=vss}
C {devices/lab_wire.sym} 1615 874 2 0 {name=l293 lab=vss}
C {devices/lab_wire.sym} 1890 874 2 0 {name=l294 lab=vss}
C {devices/lab_wire.sym} 2165 874 2 0 {name=l295 lab=vss}
C {devices/lab_wire.sym} 2440 874 2 0 {name=l296 lab=vss}
C {devices/lab_wire.sym} 1615 1134 2 0 {name=l297 lab=vss}
C {devices/lab_wire.sym} 215 1134 2 0 {name=l298 lab=vss}
C {devices/lab_wire.sym} 1075 614 2 0 {name=l299 lab=vss}
C {devices/lab_wire.sym} 1310 614 2 0 {name=l300 lab=vss}
C {devices/lab_wire.sym} 605 874 2 0 {name=l301 lab=vss}
C {devices/lab_wire.sym} 840 874 2 0 {name=l302 lab=vss}
C {devices/lab_wire.sym} 2700 874 2 0 {name=l303 lab=vss}
C {devices/lab_wire.sym} 2960 874 2 0 {name=l304 lab=vss}
C {devices/lab_wire.sym} -1390 614 2 0 {name=l305 lab=vss}
C {devices/lab_wire.sym} -1665 614 2 0 {name=l306 lab=vss}
C {devices/lab_wire.sym} -250 614 2 0 {name=l307 lab=vss}
C {devices/lab_wire.sym} 6810 614 2 0 {name=l308 lab=vss}
C {devices/lab_wire.sym} -1895 614 2 0 {name=l309 lab=vss}
C {devices/lab_wire.sym} -2125 614 2 0 {name=l310 lab=vss}
C {devices/lab_wire.sym} 3900 874 2 0 {name=l311 lab=vss}
C {devices/lab_wire.sym} 4130 874 2 0 {name=l312 lab=vss}
C {devices/lab_wire.sym} 4355 874 2 0 {name=l313 lab=vss}
C {devices/lab_wire.sym} -2125 874 2 0 {name=l314 lab=vss}
C {devices/lab_wire.sym} -3055 170 0 1 {name=l315 lab=vref_cm}
C {devices/lab_wire.sym} -2715 1130 2 0 {name=l316 lab=vss}
C {devices/lab_wire.sym} -2715 870 2 0 {name=l317 lab=vss}
C {devices/lab_wire.sym} -2715 610 2 0 {name=l318 lab=vss}
C {devices/lab_wire.sym} -2715 350 2 0 {name=l319 lab=vss}
C {devices/lab_wire.sym} -2715 90 2 0 {name=l320 lab=vss}
C {devices/lab_wire.sym} -3055 1130 2 0 {name=l321 lab=vss}
C {devices/lab_wire.sym} -3055 610 2 0 {name=l322 lab=vss}
C {devices/lab_wire.sym} -3055 350 2 0 {name=l323 lab=vss}
C {devices/lab_wire.sym} -3055 870 2 0 {name=l324 lab=vcmfb_raw}
C {devices/lab_wire.sym} -2715 950 0 1 {name=l325 lab=main__vb1}
C {devices/lab_wire.sym} -2715 690 0 1 {name=l326 lab=rrl__vb1}
C {devices/lab_wire.sym} -2715 430 0 1 {name=l327 lab=main__vb2}
C {devices/lab_wire.sym} -2715 170 0 1 {name=l328 lab=rrl__vb2}
C {devices/lab_wire.sym} -2715 -90 0 1 {name=l329 lab=main__vb3}
C {devices/lab_wire.sym} -3055 950 0 1 {name=l330 lab=rrl__vb3}
C {devices/lab_wire.sym} -3055 690 0 1 {name=l331 lab=vb4_ctl}
C {devices/lab_wire.sym} -3055 430 0 1 {name=l332 lab=rrl__vb4}
C {devices/lab_wire.sym} 1500 820 0 1 {name=l333 lab=vss}
C {devices/lab_wire.sym} 420 880 0 0 {name=l334 lab=vss}
C {devices/lab_wire.sym} 935 350 2 0 {name=l335 lab=vss}
C {devices/lab_wire.sym} 1195 350 2 0 {name=l336 lab=vss}
C {devices/lab_wire.sym} -1055 610 2 0 {name=l337 lab=vss}
C {devices/lab_wire.sym} 3735 610 2 0 {name=l338 lab=vss}
C {devices/ipin.sym} -3255 520 0 0 {name=p0 lab=clk_chin_not}
C {devices/ipin.sym} -3255 640 0 0 {name=p1 lab=clk_chin}
C {devices/ipin.sym} -3255 760 0 0 {name=p2 lab=clk_phi_1}
C {devices/ipin.sym} -3255 880 0 0 {name=p3 lab=clk_chout}
C {devices/ipin.sym} -3255 1000 0 0 {name=p4 lab=clk_chout_not}
C {devices/ipin.sym} -3255 1120 0 0 {name=p5 lab=clk_phi_2}
C {devices/ipin.sym} -3255 1240 0 0 {name=p6 lab=clk_chfb}
C {devices/ipin.sym} -3255 1360 0 0 {name=p7 lab=clk_chfb_not}
C {devices/iopin.sym} 3040 1320 0 0 {name=p8 lab=vref}
C {devices/opin.sym} 7355 30 0 0 {name=p9 lab=voutn}
C {devices/opin.sym} 7355 150 0 0 {name=p10 lab=voutp}
C {devices/opin.sym} 7355 490 0 0 {name=p11 lab=vinp}
C {devices/opin.sym} 7355 610 0 0 {name=p12 lab=vinn}
