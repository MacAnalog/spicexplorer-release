v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_004_fan_chopper_rrl} -3270 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1210 650 0 0 {name=CAZ1_RRL value='x_dut_caz1_rrl_value'}
C {devices/capa_np.sym} 1470 650 0 0 {name=CAZ2_RRL value='x_dut_caz2_rrl_value'}
C {devices/capa_np.sym} 950 650 0 0 {name=CFB1_MAIN value='x_dut_cfb1_main_value'}
C {devices/capa_np.sym} 1720 650 0 0 {name=CFB2_MAIN value='x_dut_cfb2_main_value'}
C {devices/capa_np.sym} 2940 520 0 0 {name=CIN1_MAIN value='x_dut_cin1_main_value'}
C {devices/capa_np.sym} -535 520 0 0 {name=CIN2_MAIN value='x_dut_cin2_main_value'}
C {devices/capa_np.sym} 1210 910 0 0 {name=CINT1_RRL value='x_dut_cint1_rrl_value'}
C {devices/capa_np.sym} 1470 910 0 0 {name=CINT2_RRL value='x_dut_cint2_rrl_value'}
C {devices/capa_np.sym} 1210 1040 0 0 {name=CIN_1_RRL value='cin_val_rrl'}
C {devices/capa_np.sym} 5000 520 0 0 {name=CIN_SERVO_CMFB value='cin_val_cmfb'}
C {devices/capa_np.sym} 5190 520 0 0 {name=CM1_MAIN value='x_dut_cm1_main_value'}
C {devices/capa_np.sym} 5440 520 0 0 {name=CM2_MAIN value='x_dut_cm2_main_value'}
C {devices/capa_np.sym} 5690 520 1 0 {name=COUT_1_RRL value='cout_val_rrl'}
C {devices/capa_np.sym} 1730 910 0 0 {name=COUT_SERVO_CMFB value='cout_val_cmfb'}
C {devices/capa_np.sym} 1980 650 0 0 {name=CS1_RRL value='x_dut_cs1_rrl_value'}
C {devices/capa_np.sym} 415 650 0 0 {name=CS2_RRL value='x_dut_cs2_rrl_value'}
C {devices/res_np.sym} 3200 520 0 0 {name=RB1_MAIN value='x_dut_rb1_main_value'}
C {devices/res_np.sym} -785 520 0 0 {name=RB2_MAIN value='x_dut_rb2_main_value'}
C {devices/res_np.sym} 950 1040 0 0 {name=RIN_1_RRL value='rin_val_rrl'}
C {devices/res_np.sym} -2360 520 0 0 {name=RIN_SERVO_CMFB value='rin_val_cmfb'}
C {devices/res_np.sym} 1495 390 0 0 {name=RMN_CMFB value='x_dut_rmn_cmfb_value'}
C {devices/res_np.sym} 1225 390 0 0 {name=RMP_CMFB value='x_dut_rmp_cmfb_value'}
C {devices/res_np.sym} -2550 520 1 0 {name=ROUT_1_RRL value='rout_val_rrl'}
C {devices/res_np.sym} 635 910 0 0 {name=ROUT_SERVO_CMFB value='rout_val_cmfb'}
C {devices/vsource_np.sym} -2890 1040 0 0 {name=VB1_MAIN value="dc {vb1_main}"}
C {devices/vsource_np.sym} -2890 780 0 0 {name=VB1_RRL value="dc {vb1_rrl}"}
C {devices/vsource_np.sym} -2890 520 0 0 {name=VB2_MAIN value="dc {vb2_main}"}
C {devices/vsource_np.sym} -2890 260 0 0 {name=VB2_RRL value="dc {vb2_rrl}"}
C {devices/vsource_np.sym} -2890 0 0 0 {name=VB3_MAIN value="dc {vb3_main}"}
C {devices/vsource_np.sym} -3230 1040 0 0 {name=VB3_RRL value="dc {vb3_rrl}"}
C {devices/vsource_np.sym} -3230 780 0 0 {name=VB40 value="dc {vb40}"}
C {devices/vsource_np.sym} -3230 520 0 0 {name=VB4_RRL value="dc {vb4_rrl}"}
C {devices/vsource_np.sym} -3230 260 0 0 {name=VREFCM value="dc {vcm_ref}"}
C {devices/sg13_lv_pmos_np.sym} 940 260 0 1 {name=M10_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_main_w l=x_dut_xm10_main_l m=x_dut_xm10_main_m}
C {devices/sg13_lv_pmos_np.sym} 240 520 0 1 {name=M10_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_rrl_w l=x_dut_xm10_opamp_rrl_l m=x_dut_xm10_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1985 260 0 0 {name=M11_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_main_w l=x_dut_xm11_main_l m=x_dut_xm11_main_m}
C {devices/sg13_lv_nmos_np.sym} -165 780 0 1 {name=M11_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_opamp_rrl_w l=x_dut_xm11_opamp_rrl_l m=x_dut_xm11_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 5880 520 0 0 {name=M12_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_main_w l=x_dut_xm12_main_l m=x_dut_xm12_main_m}
C {devices/sg13_lv_nmos_np.sym} 1480 780 0 0 {name=M12_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_opamp_rrl_w l=x_dut_xm12_opamp_rrl_l m=x_dut_xm12_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 940 520 0 1 {name=M13_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_main_w l=x_dut_xm13_main_l m=x_dut_xm13_main_m}
C {devices/sg13_lv_nmos_np.sym} -165 1040 0 1 {name=M13_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_opamp_rrl_w l=x_dut_xm13_opamp_rrl_l m=x_dut_xm13_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1210 260 0 1 {name=M14_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_main_w l=x_dut_xm14_main_l m=x_dut_xm14_main_m}
C {devices/sg13_lv_nmos_np.sym} 1480 1040 0 0 {name=M14_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_opamp_rrl_w l=x_dut_xm14_opamp_rrl_l m=x_dut_xm14_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1470 260 0 1 {name=M15_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_main_w l=x_dut_xm15_main_l m=x_dut_xm15_main_m}
C {devices/sg13_lv_nmos_np.sym} 530 520 0 0 {name=M15_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_opamp_rrl_w l=x_dut_xm15_opamp_rrl_l m=x_dut_xm15_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1175 520 0 1 {name=M16_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_main_w l=x_dut_xm16_main_l m=x_dut_xm16_main_m}
C {devices/sg13_lv_nmos_np.sym} 3635 520 0 1 {name=M16_OPAMP_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_opamp_rrl_w l=x_dut_xm16_opamp_rrl_l m=x_dut_xm16_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1405 520 0 1 {name=M17_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_main_w l=x_dut_xm17_main_l m=x_dut_xm17_main_m}
C {devices/sg13_lv_nmos_np.sym} 6110 520 0 0 {name=M18_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_main_w l=x_dut_xm18_main_l m=x_dut_xm18_main_m}
C {devices/sg13_lv_pmos_np.sym} 6335 520 0 0 {name=M19_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_main_w l=x_dut_xm19_main_l m=x_dut_xm19_main_m}
C {devices/sg13_lv_nmos_np.sym} 1940 780 0 1 {name=M1_CHRRL_1_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_1_rrl_w l=x_dut_xm1_chrrl_1_rrl_l m=x_dut_xm1_chrrl_1_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 390 780 0 1 {name=M1_CHRRL_2_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_2_rrl_w l=x_dut_xm1_chrrl_2_rrl_l m=x_dut_xm1_chrrl_2_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2215 780 0 1 {name=M1_CHRRL_3_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_3_rrl_w l=x_dut_xm1_chrrl_3_rrl_l m=x_dut_xm1_chrrl_3_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 110 780 0 1 {name=M1_CHRRL_4_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_4_rrl_w l=x_dut_xm1_chrrl_4_rrl_l m=x_dut_xm1_chrrl_4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1210 0 0 1 {name=M1_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_main_w l=x_dut_xm1_main_l m=x_dut_xm1_main_m}
C {devices/sg13_lv_pmos_np.sym} 2460 0 0 0 {name=M1_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_opamp_rrl_w l=x_dut_xm1_opamp_rrl_l m=x_dut_xm1_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 625 1040 0 1 {name=M1_S1_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s1_rrl_w l=x_dut_xm1_s1_rrl_l m=x_dut_xm1_s1_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1940 1040 0 1 {name=M1_S2_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s2_rrl_w l=x_dut_xm1_s2_rrl_l m=x_dut_xm1_s2_rrl_m}
C {devices/sg13_lv_nmos_np.sym} -1060 520 0 1 {name=M1_S3_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s3_rrl_w l=x_dut_xm1_s3_rrl_l m=x_dut_xm1_s3_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 1640 520 0 1 {name=M1_S4_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s4_rrl_w l=x_dut_xm1_s4_rrl_l m=x_dut_xm1_s4_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2450 780 0 1 {name=M1_S5_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s5_rrl_w l=x_dut_xm1_s5_rrl_l m=x_dut_xm1_s5_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 940 780 0 1 {name=M1_S6_RRL model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s6_rrl_w l=x_dut_xm1_s6_rrl_l m=x_dut_xm1_s6_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 2680 780 0 1 {name=M20_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_main_w l=x_dut_xm20_main_l m=x_dut_xm20_main_m}
C {devices/sg13_lv_pmos_np.sym} 2940 780 0 1 {name=M21_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_main_w l=x_dut_xm21_main_l m=x_dut_xm21_main_m}
C {devices/sg13_lv_nmos_np.sym} -535 780 0 1 {name=M22_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_main_w l=x_dut_xm22_main_l m=x_dut_xm22_main_m}
C {devices/sg13_lv_pmos_np.sym} 3200 780 0 1 {name=M23_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_main_w l=x_dut_xm23_main_l m=x_dut_xm23_main_m}
C {devices/sg13_lv_nmos_np.sym} 3910 520 0 1 {name=M24_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_main_w l=x_dut_xm24_main_l m=x_dut_xm24_main_m}
C {devices/sg13_lv_pmos_np.sym} -1340 520 0 1 {name=M25_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm25_main_w l=x_dut_xm25_main_l m=x_dut_xm25_main_m}
C {devices/sg13_lv_nmos_np.sym} 4140 520 0 1 {name=M26_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm26_main_w l=x_dut_xm26_main_l m=x_dut_xm26_main_m}
C {devices/sg13_lv_pmos_np.sym} -1575 520 0 1 {name=M27_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm27_main_w l=x_dut_xm27_main_l m=x_dut_xm27_main_m}
C {devices/sg13_lv_nmos_np.sym} 1870 520 0 1 {name=M28_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm28_main_w l=x_dut_xm28_main_l m=x_dut_xm28_main_m}
C {devices/sg13_lv_pmos_np.sym} -125 520 0 1 {name=M29_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm29_main_w l=x_dut_xm29_main_l m=x_dut_xm29_main_m}
C {devices/sg13_lv_pmos_np.sym} -785 780 0 1 {name=M2_CHRRL_1_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_1_rrl_w l=x_dut_xm2_chrrl_1_rrl_l m=x_dut_xm2_chrrl_1_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 3635 780 0 1 {name=M2_CHRRL_2_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_2_rrl_w l=x_dut_xm2_chrrl_2_rrl_l m=x_dut_xm2_chrrl_2_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -1060 780 0 1 {name=M2_CHRRL_3_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_3_rrl_w l=x_dut_xm2_chrrl_3_rrl_l m=x_dut_xm2_chrrl_3_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 3910 780 0 1 {name=M2_CHRRL_4_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_4_rrl_w l=x_dut_xm2_chrrl_4_rrl_l m=x_dut_xm2_chrrl_4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1720 260 0 1 {name=M2_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_main_w l=x_dut_xm2_main_l m=x_dut_xm2_main_m}
C {devices/sg13_lv_pmos_np.sym} 2500 260 0 0 {name=M2_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_rrl_w l=x_dut_xm2_opamp_rrl_l m=x_dut_xm2_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 390 1040 0 1 {name=M2_S1_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s1_rrl_w l=x_dut_xm2_s1_rrl_l m=x_dut_xm2_s1_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2215 1040 0 1 {name=M2_S2_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s2_rrl_w l=x_dut_xm2_s2_rrl_l m=x_dut_xm2_s2_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 4375 520 0 1 {name=M2_S3_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s3_rrl_w l=x_dut_xm2_s3_rrl_l m=x_dut_xm2_s3_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 2110 520 0 1 {name=M2_S4_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s4_rrl_w l=x_dut_xm2_s4_rrl_l m=x_dut_xm2_s4_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -1340 780 0 1 {name=M2_S5_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s5_rrl_w l=x_dut_xm2_s5_rrl_l m=x_dut_xm2_s5_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1175 780 0 1 {name=M2_S6_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s6_rrl_w l=x_dut_xm2_s6_rrl_l m=x_dut_xm2_s6_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 6565 520 0 0 {name=M30_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm30_main_w l=x_dut_xm30_main_l m=x_dut_xm30_main_m}
C {devices/sg13_lv_pmos_np.sym} 6790 520 0 0 {name=M31_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm31_main_w l=x_dut_xm31_main_l m=x_dut_xm31_main_m}
C {devices/sg13_lv_nmos_np.sym} -1800 520 0 1 {name=M32_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm32_main_w l=x_dut_xm32_main_l m=x_dut_xm32_main_m}
C {devices/sg13_lv_pmos_np.sym} 4600 520 0 1 {name=M33_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm33_main_w l=x_dut_xm33_main_l m=x_dut_xm33_main_m}
C {devices/sg13_lv_nmos_np.sym} -2030 520 0 1 {name=M34_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm34_main_w l=x_dut_xm34_main_l m=x_dut_xm34_main_m}
C {devices/sg13_lv_pmos_np.sym} 4830 520 0 1 {name=M35_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm35_main_w l=x_dut_xm35_main_l m=x_dut_xm35_main_m}
C {devices/sg13_lv_nmos_np.sym} 4140 780 0 1 {name=M36_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm36_main_w l=x_dut_xm36_main_l m=x_dut_xm36_main_m}
C {devices/sg13_lv_pmos_np.sym} -1575 780 0 1 {name=M37_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm37_main_w l=x_dut_xm37_main_l m=x_dut_xm37_main_m}
C {devices/sg13_lv_nmos_np.sym} 4375 780 0 1 {name=M38_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm38_main_w l=x_dut_xm38_main_l m=x_dut_xm38_main_m}
C {devices/sg13_lv_pmos_np.sym} -1800 780 0 1 {name=M39_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm39_main_w l=x_dut_xm39_main_l m=x_dut_xm39_main_m}
C {devices/sg13_lv_pmos_np.sym} -55 260 0 1 {name=M3_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_main_w l=x_dut_xm3_main_l m=x_dut_xm3_main_m}
C {devices/sg13_lv_pmos_np.sym} 240 260 0 1 {name=M3_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_rrl_w l=x_dut_xm3_opamp_rrl_l m=x_dut_xm3_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} 4600 780 0 1 {name=M4_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_main_w l=x_dut_xm4_main_l m=x_dut_xm4_main_m}
C {devices/sg13_lv_pmos_np.sym} 1470 0 0 1 {name=M4_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_opamp_rrl_w l=x_dut_xm4_opamp_rrl_l m=x_dut_xm4_opamp_rrl_m}
C {devices/sg13_lv_nmos_np.sym} -2030 780 0 1 {name=M5_MAIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_main_w l=x_dut_xm5_main_l m=x_dut_xm5_main_m}
C {devices/sg13_lv_pmos_np.sym} -275 260 0 1 {name=M5_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_opamp_rrl_w l=x_dut_xm5_opamp_rrl_l m=x_dut_xm5_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 940 0 0 1 {name=M6_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_main_w l=x_dut_xm6_main_l m=x_dut_xm6_main_m}
C {devices/sg13_lv_pmos_np.sym} 2940 260 0 1 {name=M6_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_opamp_rrl_w l=x_dut_xm6_opamp_rrl_l m=x_dut_xm6_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1985 0 0 0 {name=M7_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_main_w l=x_dut_xm7_main_l m=x_dut_xm7_main_m}
C {devices/sg13_lv_pmos_np.sym} -535 260 0 1 {name=M7_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_opamp_rrl_w l=x_dut_xm7_opamp_rrl_l m=x_dut_xm7_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 1720 0 0 1 {name=M8_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_main_w l=x_dut_xm8_main_l m=x_dut_xm8_main_m}
C {devices/sg13_lv_pmos_np.sym} 3200 260 0 1 {name=M8_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_opamp_rrl_w l=x_dut_xm8_opamp_rrl_l m=x_dut_xm8_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 390 0 0 1 {name=M9_MAIN model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_main_w l=x_dut_xm9_main_l m=x_dut_xm9_main_m}
C {devices/sg13_lv_pmos_np.sym} 2500 520 0 0 {name=M9_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_rrl_w l=x_dut_xm9_opamp_rrl_l m=x_dut_xm9_opamp_rrl_m}
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
N -2520 520 -2520 580 {}
N -2360 430 -2360 490 {}
N -2360 550 -2360 610 {}
N -2110 520 -2110 614 {}
N -2110 780 -2110 874 {}
N -2050 430 -2050 490 {}
N -2050 550 -2050 610 {}
N -2050 690 -2050 750 {}
N -2050 810 -2050 1180 {}
N -2010 520 -2010 580 {}
N -2010 780 -2010 840 {}
N -1880 520 -1880 614 {}
N -1880 780 -1880 874 {}
N -1820 430 -1820 490 {}
N -1820 550 -1820 610 {}
N -1820 690 -1820 750 {}
N -1820 810 -1820 870 {}
N -1780 520 -1780 580 {}
N -1780 780 -1780 840 {}
N -1655 520 -1655 614 {}
N -1655 780 -1655 874 {}
N -1595 430 -1595 490 {}
N -1595 550 -1595 610 {}
N -1595 690 -1595 750 {}
N -1595 810 -1595 870 {}
N -1555 520 -1555 580 {}
N -1555 780 -1555 840 {}
N -1420 520 -1420 614 {}
N -1420 780 -1420 874 {}
N -1360 430 -1360 490 {}
N -1360 550 -1360 610 {}
N -1360 690 -1360 750 {}
N -1360 810 -1360 870 {}
N -1320 520 -1320 580 {}
N -1320 780 -1320 840 {}
N -1140 520 -1140 614 {}
N -1140 780 -1140 874 {}
N -1080 430 -1080 490 {}
N -1080 550 -1080 610 {}
N -1080 690 -1080 750 {}
N -1080 810 -1080 870 {}
N -1040 780 -1040 840 {}
N -865 780 -865 874 {}
N -805 690 -805 750 {}
N -805 810 -805 870 {}
N -785 430 -785 490 {}
N -785 550 -785 610 {}
N -765 780 -765 840 {}
N -615 260 -615 354 {}
N -615 780 -615 874 {}
N -555 170 -555 230 {}
N -555 290 -555 350 {}
N -555 690 -555 750 {}
N -555 810 -555 870 {}
N -535 430 -535 490 {}
N -535 550 -535 610 {}
N -515 780 -515 840 {}
N -355 260 -355 354 {}
N -295 200 -295 230 {}
N -295 290 -295 320 {}
N -255 260 -255 320 {}
N -245 780 -245 874 {}
N -245 1040 -245 1134 {}
N -205 520 -205 614 {}
N -185 690 -185 750 {}
N -185 810 -185 870 {}
N -185 950 -185 1010 {}
N -185 1070 -185 1180 {}
N -145 430 -145 490 {}
N -145 550 -145 610 {}
N -145 780 -145 840 {}
N -135 260 -135 354 {}
N -105 520 -105 580 {}
N -75 170 -75 230 {}
N -75 290 -75 350 {}
N -35 260 -35 320 {}
N 30 780 30 874 {}
N 90 690 90 750 {}
N 90 810 90 870 {}
N 130 780 130 840 {}
N 160 260 160 354 {}
N 160 520 160 614 {}
N 220 170 220 230 {}
N 220 290 220 350 {}
N 220 430 220 490 {}
N 220 550 220 610 {}
N 310 0 310 94 {}
N 310 780 310 874 {}
N 310 1040 310 1134 {}
N 370 -140 370 -30 {}
N 370 30 370 90 {}
N 370 690 370 750 {}
N 370 810 370 870 {}
N 370 950 370 1010 {}
N 370 1070 370 1180 {}
N 410 1040 410 1100 {}
N 415 60 415 620 {}
N 415 680 415 710 {}
N 510 450 510 520 {}
N 545 1040 545 1134 {}
N 550 430 550 490 {}
N 550 550 550 1180 {}
N 605 980 605 1010 {}
N 605 1070 605 1180 {}
N 610 520 610 614 {}
N 635 820 635 880 {}
N 635 940 635 970 {}
N 860 0 860 94 {}
N 860 260 860 354 {}
N 860 520 860 614 {}
N 860 780 860 874 {}
N 920 -140 920 -30 {}
N 920 30 920 90 {}
N 920 170 920 230 {}
N 920 290 920 350 {}
N 920 430 920 490 {}
N 920 550 920 610 {}
N 920 690 920 750 {}
N 920 810 920 870 {}
N 950 680 950 710 {}
N 950 950 950 1010 {}
N 950 1070 950 1130 {}
N 960 0 960 60 {}
N 960 260 960 320 {}
N 960 460 960 520 {}
N 960 780 960 840 {}
N 1095 520 1095 614 {}
N 1095 780 1095 874 {}
N 1130 0 1130 94 {}
N 1130 260 1130 354 {}
N 1155 430 1155 490 {}
N 1155 550 1155 610 {}
N 1155 690 1155 750 {}
N 1155 810 1155 870 {}
N 1190 -140 1190 -30 {}
N 1190 30 1190 90 {}
N 1190 170 1190 230 {}
N 1190 290 1190 350 {}
N 1210 560 1210 620 {}
N 1210 680 1210 740 {}
N 1210 850 1210 880 {}
N 1210 980 1210 1010 {}
N 1210 1070 1210 1100 {}
N 1225 330 1225 360 {}
N 1225 420 1225 450 {}
N 1230 0 1230 60 {}
N 1230 200 1230 260 {}
N 1325 520 1325 614 {}
N 1385 430 1385 490 {}
N 1385 550 1385 610 {}
N 1390 0 1390 94 {}
N 1390 260 1390 354 {}
N 1450 -140 1450 -30 {}
N 1450 30 1450 90 {}
N 1450 170 1450 230 {}
N 1450 290 1450 350 {}
N 1470 560 1470 620 {}
N 1470 680 1470 740 {}
N 1470 820 1470 880 {}
N 1470 940 1470 1000 {}
N 1490 0 1490 60 {}
N 1490 200 1490 260 {}
N 1495 300 1495 360 {}
N 1495 420 1495 480 {}
N 1500 690 1500 750 {}
N 1500 810 1500 870 {}
N 1500 950 1500 1010 {}
N 1500 1070 1500 1180 {}
N 1560 520 1560 614 {}
N 1560 780 1560 874 {}
N 1560 1040 1560 1134 {}
N 1620 430 1620 490 {}
N 1620 550 1620 610 {}
N 1640 0 1640 94 {}
N 1640 260 1640 354 {}
N 1700 -140 1700 -30 {}
N 1700 30 1700 90 {}
N 1700 170 1700 230 {}
N 1700 290 1700 350 {}
N 1720 560 1720 620 {}
N 1720 680 1720 740 {}
N 1730 820 1730 880 {}
N 1730 940 1730 1000 {}
N 1790 520 1790 614 {}
N 1850 430 1850 490 {}
N 1850 550 1850 610 {}
N 1860 780 1860 874 {}
N 1860 1040 1860 1134 {}
N 1890 460 1890 520 {}
N 1920 690 1920 750 {}
N 1920 810 1920 870 {}
N 1920 950 1920 1010 {}
N 1920 1070 1920 1180 {}
N 1960 780 1960 840 {}
N 1960 1040 1960 1100 {}
N 1980 60 1980 620 {}
N 1980 680 1980 740 {}
N 2005 -140 2005 -30 {}
N 2005 30 2005 90 {}
N 2005 170 2005 230 {}
N 2005 290 2005 350 {}
N 2030 520 2030 614 {}
N 2065 0 2065 94 {}
N 2065 260 2065 354 {}
N 2090 430 2090 490 {}
N 2090 550 2090 610 {}
N 2135 1040 2135 1134 {}
N 2160 520 2160 780 {}
N 2195 690 2195 750 {}
N 2195 810 2195 870 {}
N 2195 980 2195 1010 {}
N 2195 1070 2195 1180 {}
N 2235 780 2235 840 {}
N 2370 780 2370 874 {}
N 2430 690 2430 750 {}
N 2430 810 2430 870 {}
N 2470 780 2470 840 {}
N 2480 -140 2480 -30 {}
N 2480 30 2480 90 {}
N 2500 780 2500 1040 {}
N 2520 170 2520 230 {}
N 2520 290 2520 350 {}
N 2520 430 2520 490 {}
N 2520 550 2520 610 {}
N 2540 0 2540 94 {}
N 2580 260 2580 354 {}
N 2580 520 2580 614 {}
N 2600 780 2600 874 {}
N 2660 690 2660 750 {}
N 2660 810 2660 870 {}
N 2700 780 2700 840 {}
N 2860 260 2860 354 {}
N 2860 780 2860 874 {}
N 2920 170 2920 230 {}
N 2920 290 2920 350 {}
N 2920 690 2920 750 {}
N 2920 810 2920 870 {}
N 2940 430 2940 490 {}
N 2940 550 2940 610 {}
N 2960 260 2960 320 {}
N 2960 780 2960 840 {}
N 3120 260 3120 354 {}
N 3120 780 3120 874 {}
N 3180 200 3180 230 {}
N 3180 290 3180 350 {}
N 3180 690 3180 750 {}
N 3180 810 3180 870 {}
N 3200 430 3200 490 {}
N 3200 550 3200 610 {}
N 3555 520 3555 614 {}
N 3555 780 3555 874 {}
N 3615 430 3615 490 {}
N 3615 550 3615 610 {}
N 3615 690 3615 750 {}
N 3615 810 3615 870 {}
N 3655 450 3655 520 {}
N 3655 780 3655 840 {}
N 3830 520 3830 614 {}
N 3830 780 3830 874 {}
N 3890 430 3890 490 {}
N 3890 550 3890 610 {}
N 3890 690 3890 750 {}
N 3890 810 3890 870 {}
N 3930 520 3930 580 {}
N 3930 780 3930 840 {}
N 4060 520 4060 614 {}
N 4060 780 4060 874 {}
N 4120 430 4120 490 {}
N 4120 550 4120 610 {}
N 4120 690 4120 750 {}
N 4120 810 4120 870 {}
N 4160 520 4160 580 {}
N 4160 780 4160 840 {}
N 4295 520 4295 614 {}
N 4295 780 4295 874 {}
N 4355 430 4355 490 {}
N 4355 550 4355 610 {}
N 4355 690 4355 750 {}
N 4355 810 4355 870 {}
N 4395 520 4395 580 {}
N 4395 780 4395 840 {}
N 4520 520 4520 614 {}
N 4520 780 4520 874 {}
N 4580 430 4580 490 {}
N 4580 550 4580 610 {}
N 4580 690 4580 750 {}
N 4580 810 4580 1180 {}
N 4620 520 4620 580 {}
N 4750 520 4750 614 {}
N 4810 430 4810 490 {}
N 4810 550 4810 610 {}
N 4850 520 4850 580 {}
N 5000 430 5000 490 {}
N 5000 550 5000 610 {}
N 5190 260 5190 490 {}
N 5190 550 5190 610 {}
N 5440 430 5440 490 {}
N 5440 550 5440 610 {}
N 5720 520 5720 580 {}
N 5860 460 5860 520 {}
N 5900 320 5900 490 {}
N 5900 550 5900 610 {}
N 5960 520 5960 614 {}
N 6130 460 6130 490 {}
N 6130 550 6130 610 {}
N 6190 520 6190 614 {}
N 6355 460 6355 490 {}
N 6355 550 6355 610 {}
N 6415 520 6415 614 {}
N 6585 460 6585 490 {}
N 6585 550 6585 610 {}
N 6645 520 6645 614 {}
N 6810 460 6810 490 {}
N 6810 550 6810 580 {}
N 6870 520 6870 614 {}
N -3290 -140 7045 -140 {}
N 310 0 370 0 {}
N 410 0 470 0 {}
N 860 0 920 0 {}
N 960 0 990 0 {}
N 1130 0 1190 0 {}
N 1230 0 1260 0 {}
N 1390 0 1450 0 {}
N 1490 0 1520 0 {}
N 1640 0 1700 0 {}
N 1740 0 1965 0 {}
N 2005 0 2065 0 {}
N 2380 0 2440 0 {}
N 2480 0 2540 0 {}
N 370 60 415 60 {}
N 1700 60 1980 60 {}
N -555 200 -295 200 {}
N 2920 200 3180 200 {}
N -615 260 -555 260 {}
N -515 260 -485 260 {}
N -355 260 -295 260 {}
N -255 260 -225 260 {}
N -135 260 -75 260 {}
N -35 260 -5 260 {}
N 160 260 220 260 {}
N 260 260 320 260 {}
N 860 260 920 260 {}
N 960 260 990 260 {}
N 1130 260 1190 260 {}
N 1230 260 1260 260 {}
N 1390 260 1450 260 {}
N 1490 260 1520 260 {}
N 1640 260 1700 260 {}
N 1740 260 1800 260 {}
N 1905 260 1965 260 {}
N 2005 260 2065 260 {}
N 2420 260 2480 260 {}
N 2520 260 2580 260 {}
N 2860 260 2920 260 {}
N 2960 260 2990 260 {}
N 3120 260 3180 260 {}
N 3220 260 3280 260 {}
N -555 320 -295 320 {}
N 1165 360 1225 360 {}
N 1165 420 1225 420 {}
N 510 450 550 450 {}
N 3615 450 3655 450 {}
N 5900 460 6810 460 {}
N -2640 520 -2580 520 {}
N -2520 520 -2490 520 {}
N -2110 520 -2050 520 {}
N -2010 520 -1980 520 {}
N -1880 520 -1820 520 {}
N -1780 520 -1750 520 {}
N -1655 520 -1595 520 {}
N -1555 520 -1525 520 {}
N -1420 520 -1360 520 {}
N -1320 520 -1290 520 {}
N -1140 520 -1080 520 {}
N -1040 520 -980 520 {}
N -205 520 -145 520 {}
N 160 520 220 520 {}
N 260 520 320 520 {}
N 550 520 610 520 {}
N 860 520 920 520 {}
N 960 520 990 520 {}
N 1095 520 1155 520 {}
N 1195 520 1255 520 {}
N 1325 520 1385 520 {}
N 1425 520 1485 520 {}
N 1560 520 1620 520 {}
N 1660 520 1720 520 {}
N 1790 520 1850 520 {}
N 1890 520 1920 520 {}
N 2030 520 2090 520 {}
N 2130 520 2190 520 {}
N 2420 520 2480 520 {}
N 2520 520 2580 520 {}
N 3555 520 3615 520 {}
N 3830 520 3890 520 {}
N 3930 520 3960 520 {}
N 4060 520 4120 520 {}
N 4160 520 4190 520 {}
N 4295 520 4355 520 {}
N 4395 520 4425 520 {}
N 4520 520 4580 520 {}
N 4620 520 4650 520 {}
N 4750 520 4810 520 {}
N 4850 520 4880 520 {}
N 5600 520 5660 520 {}
N 5720 520 5750 520 {}
N 5830 520 5860 520 {}
N 5900 520 5960 520 {}
N 6060 520 6090 520 {}
N 6130 520 6190 520 {}
N 6285 520 6315 520 {}
N 6355 520 6415 520 {}
N 6515 520 6545 520 {}
N 6585 520 6645 520 {}
N 6740 520 6770 520 {}
N 6810 520 6870 520 {}
N 6585 580 6810 580 {}
N 1980 590 5190 590 {}
N 890 620 950 620 {}
N 355 680 415 680 {}
N 890 680 950 680 {}
N 4580 720 5900 720 {}
N -2110 780 -2050 780 {}
N -2010 780 -1980 780 {}
N -1880 780 -1820 780 {}
N -1780 780 -1750 780 {}
N -1655 780 -1595 780 {}
N -1555 780 -1525 780 {}
N -1420 780 -1360 780 {}
N -1320 780 -1290 780 {}
N -1140 780 -1080 780 {}
N -865 780 -805 780 {}
N -765 780 -735 780 {}
N -615 780 -555 780 {}
N -515 780 -485 780 {}
N -245 780 -185 780 {}
N -145 780 -115 780 {}
N 30 780 90 780 {}
N 130 780 160 780 {}
N 310 780 370 780 {}
N 410 780 470 780 {}
N 860 780 920 780 {}
N 960 780 990 780 {}
N 1095 780 1155 780 {}
N 1195 780 1255 780 {}
N 1400 780 1460 780 {}
N 1500 780 1560 780 {}
N 1860 780 1920 780 {}
N 2235 780 2265 780 {}
N 2370 780 2430 780 {}
N 2470 780 2500 780 {}
N 2600 780 2660 780 {}
N 2700 780 2730 780 {}
N 2860 780 2920 780 {}
N 2960 780 2990 780 {}
N 3120 780 3180 780 {}
N 3220 780 3280 780 {}
N 3555 780 3615 780 {}
N 3655 780 3685 780 {}
N 3830 780 3890 780 {}
N 3930 780 3960 780 {}
N 4060 780 4120 780 {}
N 4160 780 4190 780 {}
N 4295 780 4355 780 {}
N 4395 780 4425 780 {}
N 4520 780 4580 780 {}
N 4620 780 4680 780 {}
N 1150 880 1210 880 {}
N 575 940 635 940 {}
N 1150 940 1210 940 {}
N 370 980 605 980 {}
N 950 980 1210 980 {}
N 1920 980 2195 980 {}
N -245 1040 -185 1040 {}
N -145 1040 -85 1040 {}
N 310 1040 370 1040 {}
N 410 1040 440 1040 {}
N 545 1040 605 1040 {}
N 645 1040 705 1040 {}
N 1430 1040 1460 1040 {}
N 1500 1040 1560 1040 {}
N 1860 1040 1920 1040 {}
N 1960 1040 1990 1040 {}
N 2135 1040 2195 1040 {}
N 2235 1040 2500 1040 {}
N 950 1100 1470 1100 {}
N -3290 1180 7045 1180 {}
C {devices/lab_wire.sym} -3290 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -3290 1180 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -1780 840 2 0 {name=l2 lab=clk_chfb}
C {devices/lab_wire.sym} -1555 840 2 0 {name=l3 lab=clk_chfb}
C {devices/lab_wire.sym} -515 840 2 0 {name=l4 lab=clk_chfb}
C {devices/lab_wire.sym} 2700 840 2 0 {name=l5 lab=clk_chfb}
C {devices/lab_wire.sym} 2960 840 2 0 {name=l6 lab=clk_chfb_not}
C {devices/lab_wire.sym} 3280 780 0 1 {name=l7 lab=clk_chfb_not}
C {devices/lab_wire.sym} 4160 840 2 0 {name=l8 lab=clk_chfb_not}
C {devices/lab_wire.sym} 4395 840 2 0 {name=l9 lab=clk_chfb_not}
C {devices/lab_wire.sym} 3930 580 2 0 {name=l10 lab=clk_chin}
C {devices/lab_wire.sym} 4160 580 2 0 {name=l11 lab=clk_chin}
C {devices/lab_wire.sym} 4620 580 2 0 {name=l12 lab=clk_chin}
C {devices/lab_wire.sym} 4850 580 2 0 {name=l13 lab=clk_chin}
C {devices/lab_wire.sym} -2010 580 2 0 {name=l14 lab=clk_chin_not}
C {devices/lab_wire.sym} -1780 580 2 0 {name=l15 lab=clk_chin_not}
C {devices/lab_wire.sym} -1555 580 2 0 {name=l16 lab=clk_chin_not}
C {devices/lab_wire.sym} -1320 580 2 0 {name=l17 lab=clk_chin_not}
C {devices/lab_wire.sym} -1040 840 2 0 {name=l18 lab=clk_chout}
C {devices/lab_wire.sym} -105 580 2 0 {name=l19 lab=clk_chout}
C {devices/lab_wire.sym} 470 780 0 1 {name=l20 lab=clk_chout}
C {devices/lab_wire.sym} 1255 520 0 1 {name=l21 lab=clk_chout}
C {devices/lab_wire.sym} 1960 840 2 0 {name=l22 lab=clk_chout}
C {devices/lab_wire.sym} 3930 840 2 0 {name=l23 lab=clk_chout}
C {devices/lab_wire.sym} 6090 520 0 0 {name=l24 lab=clk_chout}
C {devices/lab_wire.sym} 6770 520 0 0 {name=l25 lab=clk_chout}
C {devices/lab_wire.sym} -765 840 2 0 {name=l26 lab=clk_chout_not}
C {devices/lab_wire.sym} 130 840 2 0 {name=l27 lab=clk_chout_not}
C {devices/lab_wire.sym} 1485 520 0 1 {name=l28 lab=clk_chout_not}
C {devices/lab_wire.sym} 1890 460 0 1 {name=l29 lab=clk_chout_not}
C {devices/lab_wire.sym} 2235 840 2 0 {name=l30 lab=clk_chout_not}
C {devices/lab_wire.sym} 3655 840 2 0 {name=l31 lab=clk_chout_not}
C {devices/lab_wire.sym} 6315 520 0 0 {name=l32 lab=clk_chout_not}
C {devices/lab_wire.sym} 6545 520 0 0 {name=l33 lab=clk_chout_not}
C {devices/lab_wire.sym} 410 1100 2 0 {name=l34 lab=clk_phi_1}
C {devices/lab_wire.sym} 960 840 2 0 {name=l35 lab=clk_phi_1}
C {devices/lab_wire.sym} 2190 520 0 1 {name=l36 lab=clk_phi_1}
C {devices/lab_wire.sym} 2470 840 2 0 {name=l37 lab=clk_phi_1}
C {devices/lab_wire.sym} 4395 580 2 0 {name=l38 lab=clk_phi_1}
C {devices/lab_wire.sym} -1320 840 2 0 {name=l39 lab=clk_phi_2}
C {devices/lab_wire.sym} -980 520 0 1 {name=l40 lab=clk_phi_2}
C {devices/lab_wire.sym} 705 1040 0 1 {name=l41 lab=clk_phi_2}
C {devices/lab_wire.sym} 1255 780 0 1 {name=l42 lab=clk_phi_2}
C {devices/lab_wire.sym} 1720 520 0 1 {name=l43 lab=clk_phi_2}
C {devices/lab_wire.sym} 1960 1100 2 0 {name=l44 lab=clk_phi_2}
C {devices/lab_wire.sym} -2360 430 0 1 {name=l45 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 1165 360 0 0 {name=l46 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 1495 480 2 0 {name=l47 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 5000 430 0 1 {name=l48 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 920 90 2 0 {name=l49 lab=main__casc_src_n}
C {devices/lab_wire.sym} 920 170 0 1 {name=l50 lab=main__casc_src_n}
C {devices/lab_wire.sym} 2005 90 2 0 {name=l51 lab=main__casc_src_p}
C {devices/lab_wire.sym} 2005 170 0 1 {name=l52 lab=main__casc_src_p}
C {devices/lab_wire.sym} -1820 690 0 1 {name=l53 lab=main__fbch_n}
C {devices/lab_wire.sym} -555 690 0 1 {name=l54 lab=main__fbch_n}
C {devices/lab_wire.sym} 1720 560 0 1 {name=l55 lab=main__fbch_n}
C {devices/lab_wire.sym} 3180 690 0 1 {name=l56 lab=main__fbch_n}
C {devices/lab_wire.sym} 4355 690 0 1 {name=l57 lab=main__fbch_n}
C {devices/lab_wire.sym} -1595 690 0 1 {name=l58 lab=main__fbch_p}
C {devices/lab_wire.sym} 890 620 0 0 {name=l59 lab=main__fbch_p}
C {devices/lab_wire.sym} 2660 690 0 1 {name=l60 lab=main__fbch_p}
C {devices/lab_wire.sym} 2920 690 0 1 {name=l61 lab=main__fbch_p}
C {devices/lab_wire.sym} 4120 690 0 1 {name=l62 lab=main__fbch_p}
C {devices/lab_wire.sym} -2050 690 0 1 {name=l63 lab=main__fold_n}
C {devices/lab_wire.sym} -75 350 2 0 {name=l64 lab=main__fold_n}
C {devices/lab_wire.sym} 920 610 2 0 {name=l65 lab=main__fold_n}
C {devices/lab_wire.sym} 1700 350 2 0 {name=l66 lab=main__fold_p}
C {devices/lab_wire.sym} 4580 690 0 1 {name=l67 lab=main__fold_p}
C {devices/lab_wire.sym} 5900 610 2 0 {name=l68 lab=main__fold_p}
C {devices/lab_wire.sym} 1155 610 2 0 {name=l69 lab=main__g2_n}
C {devices/lab_wire.sym} 1385 610 2 0 {name=l70 lab=main__g2_n}
C {devices/lab_wire.sym} 1490 200 0 1 {name=l71 lab=main__g2_n}
C {devices/lab_wire.sym} 5440 430 0 1 {name=l72 lab=main__g2_n}
C {devices/lab_wire.sym} 6585 610 2 0 {name=l73 lab=main__g2_n}
C {devices/lab_wire.sym} -145 610 2 0 {name=l74 lab=main__g2_p}
C {devices/lab_wire.sym} 1230 200 0 1 {name=l75 lab=main__g2_p}
C {devices/lab_wire.sym} 1850 610 2 0 {name=l76 lab=main__g2_p}
C {devices/lab_wire.sym} 5190 430 0 1 {name=l77 lab=main__g2_p}
C {devices/lab_wire.sym} 6130 610 2 0 {name=l78 lab=main__g2_p}
C {devices/lab_wire.sym} 6355 610 2 0 {name=l79 lab=main__g2_p}
C {devices/lab_wire.sym} -2050 610 2 0 {name=l80 lab=main__inch_n}
C {devices/lab_wire.sym} -1360 610 2 0 {name=l81 lab=main__inch_n}
C {devices/lab_wire.sym} 2940 610 2 0 {name=l82 lab=main__inch_n}
C {devices/lab_wire.sym} 3890 610 2 0 {name=l83 lab=main__inch_n}
C {devices/lab_wire.sym} 4810 610 2 0 {name=l84 lab=main__inch_n}
C {devices/lab_wire.sym} -1820 610 2 0 {name=l85 lab=main__inch_p}
C {devices/lab_wire.sym} -1595 610 2 0 {name=l86 lab=main__inch_p}
C {devices/lab_wire.sym} -535 610 2 0 {name=l87 lab=main__inch_p}
C {devices/lab_wire.sym} 4120 610 2 0 {name=l88 lab=main__inch_p}
C {devices/lab_wire.sym} 4580 610 2 0 {name=l89 lab=main__inch_p}
C {devices/lab_wire.sym} -75 170 0 1 {name=l90 lab=main__tail}
C {devices/lab_wire.sym} 1190 90 2 0 {name=l91 lab=main__tail}
C {devices/lab_wire.sym} 1700 170 0 1 {name=l92 lab=main__tail}
C {devices/lab_wire.sym} -2010 840 2 0 {name=l93 lab=main__vb1}
C {devices/lab_wire.sym} 4680 780 0 1 {name=l94 lab=main__vb1}
C {devices/lab_wire.sym} 960 460 0 1 {name=l95 lab=main__vb2}
C {devices/lab_wire.sym} 5860 460 0 1 {name=l96 lab=main__vb2}
C {devices/lab_wire.sym} 960 320 2 0 {name=l97 lab=main__vb3}
C {devices/lab_wire.sym} 1905 260 0 0 {name=l98 lab=main__vb3}
C {devices/lab_wire.sym} -35 320 2 0 {name=l99 lab=main__vsum_n}
C {devices/lab_wire.sym} 890 680 0 0 {name=l100 lab=main__vsum_n}
C {devices/lab_wire.sym} 2940 430 0 1 {name=l101 lab=main__vsum_n}
C {devices/lab_wire.sym} 3200 430 0 1 {name=l102 lab=main__vsum_n}
C {devices/lab_wire.sym} -785 430 0 1 {name=l103 lab=main__vsum_p}
C {devices/lab_wire.sym} -535 430 0 1 {name=l104 lab=main__vsum_p}
C {devices/lab_wire.sym} 1720 740 2 0 {name=l105 lab=main__vsum_p}
C {devices/lab_wire.sym} 1800 260 0 1 {name=l106 lab=main__vsum_p}
C {devices/lab_wire.sym} -2640 520 0 0 {name=l107 lab=out1_n}
C {devices/lab_wire.sym} -145 430 0 1 {name=l108 lab=out1_n}
C {devices/lab_wire.sym} 920 350 2 0 {name=l109 lab=out1_n}
C {devices/lab_wire.sym} 920 430 0 1 {name=l110 lab=out1_n}
C {devices/lab_wire.sym} 1155 430 0 1 {name=l111 lab=out1_n}
C {devices/lab_wire.sym} 1385 430 0 1 {name=l112 lab=out1_n}
C {devices/lab_wire.sym} 1850 430 0 1 {name=l113 lab=out1_n}
C {devices/lab_wire.sym} 5600 520 0 0 {name=l114 lab=out1_n}
C {devices/lab_wire.sym} -2520 580 2 0 {name=l115 lab=out1_p}
C {devices/lab_wire.sym} 2005 350 2 0 {name=l116 lab=out1_p}
C {devices/lab_wire.sym} 5720 580 2 0 {name=l117 lab=out1_p}
C {devices/lab_wire.sym} 5900 430 0 1 {name=l118 lab=out1_p}
C {devices/lab_wire.sym} 920 870 2 0 {name=l119 lab=rrl__int_n}
C {devices/lab_wire.sym} 950 1130 2 0 {name=l120 lab=rrl__int_n}
C {devices/lab_wire.sym} 1155 870 2 0 {name=l121 lab=rrl__int_n}
C {devices/lab_wire.sym} 1470 1000 2 0 {name=l122 lab=rrl__int_n}
C {devices/lab_wire.sym} -1360 870 2 0 {name=l123 lab=rrl__int_p}
C {devices/lab_wire.sym} 950 950 0 1 {name=l124 lab=rrl__int_p}
C {devices/lab_wire.sym} 1150 940 0 0 {name=l125 lab=rrl__int_p}
C {devices/lab_wire.sym} 2430 870 2 0 {name=l126 lab=rrl__int_p}
C {devices/lab_wire.sym} -85 1040 0 1 {name=l127 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 550 430 0 1 {name=l128 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 1460 1040 0 0 {name=l129 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 2920 350 2 0 {name=l130 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} 3180 350 2 0 {name=l131 lab=rrl__oa_cm_bias}
C {devices/lab_wire.sym} -555 350 2 0 {name=l132 lab=rrl__oa_cm_sense}
C {devices/lab_wire.sym} 3615 430 0 1 {name=l133 lab=rrl__oa_cm_sense}
C {devices/lab_wire.sym} -555 170 0 1 {name=l134 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} 1450 90 2 0 {name=l135 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} 2920 170 0 1 {name=l136 lab=rrl__oa_cm_tail}
C {devices/lab_wire.sym} -185 870 2 0 {name=l137 lab=rrl__oa_csrc_n}
C {devices/lab_wire.sym} -185 950 0 1 {name=l138 lab=rrl__oa_csrc_n}
C {devices/lab_wire.sym} 1500 870 2 0 {name=l139 lab=rrl__oa_csrc_p}
C {devices/lab_wire.sym} 1500 950 0 1 {name=l140 lab=rrl__oa_csrc_p}
C {devices/lab_wire.sym} 2520 350 2 0 {name=l141 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 2520 430 0 1 {name=l142 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 220 350 2 0 {name=l143 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} 220 430 0 1 {name=l144 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} 320 260 0 1 {name=l145 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 1470 740 2 0 {name=l146 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 1620 430 0 1 {name=l147 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 2090 430 0 1 {name=l148 lab=rrl__oa_inn}
C {devices/lab_wire.sym} -1080 430 0 1 {name=l149 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 1210 740 2 0 {name=l150 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 2420 260 0 0 {name=l151 lab=rrl__oa_inp}
C {devices/lab_wire.sym} 4355 430 0 1 {name=l152 lab=rrl__oa_inp}
C {devices/lab_wire.sym} -1360 690 0 1 {name=l153 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -1080 610 2 0 {name=l154 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -255 320 2 0 {name=l155 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -185 690 0 1 {name=l156 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 2430 690 0 1 {name=l157 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 2520 610 2 0 {name=l158 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 4355 610 2 0 {name=l159 lab=rrl__oa_outn}
C {devices/lab_wire.sym} -515 260 0 0 {name=l160 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 220 610 2 0 {name=l161 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 920 690 0 1 {name=l162 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1155 690 0 1 {name=l163 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1500 690 0 1 {name=l164 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 1620 610 2 0 {name=l165 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 2090 610 2 0 {name=l166 lab=rrl__oa_outp}
C {devices/lab_wire.sym} 220 170 0 1 {name=l167 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 2480 90 2 0 {name=l168 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 2520 170 0 1 {name=l169 lab=rrl__oa_tail}
C {devices/lab_wire.sym} -1080 870 2 0 {name=l170 lab=rrl__sc_n}
C {devices/lab_wire.sym} 370 870 2 0 {name=l171 lab=rrl__sc_n}
C {devices/lab_wire.sym} 370 950 0 1 {name=l172 lab=rrl__sc_n}
C {devices/lab_wire.sym} 355 680 0 0 {name=l173 lab=rrl__sc_n}
C {devices/lab_wire.sym} 2195 870 2 0 {name=l174 lab=rrl__sc_n}
C {devices/lab_wire.sym} 3615 870 2 0 {name=l175 lab=rrl__sc_n}
C {devices/lab_wire.sym} -805 870 2 0 {name=l176 lab=rrl__sc_p}
C {devices/lab_wire.sym} 90 870 2 0 {name=l177 lab=rrl__sc_p}
C {devices/lab_wire.sym} 1920 870 2 0 {name=l178 lab=rrl__sc_p}
C {devices/lab_wire.sym} 1920 950 0 1 {name=l179 lab=rrl__sc_p}
C {devices/lab_wire.sym} 1980 740 2 0 {name=l180 lab=rrl__sc_p}
C {devices/lab_wire.sym} 3890 870 2 0 {name=l181 lab=rrl__sc_p}
C {devices/lab_wire.sym} 90 690 0 1 {name=l182 lab=rrl__sum_n}
C {devices/lab_wire.sym} 370 690 0 1 {name=l183 lab=rrl__sum_n}
C {devices/lab_wire.sym} 1470 560 0 1 {name=l184 lab=rrl__sum_n}
C {devices/lab_wire.sym} 1470 820 0 1 {name=l185 lab=rrl__sum_n}
C {devices/lab_wire.sym} 3615 690 0 1 {name=l186 lab=rrl__sum_n}
C {devices/lab_wire.sym} 3890 690 0 1 {name=l187 lab=rrl__sum_n}
C {devices/lab_wire.sym} -1080 690 0 1 {name=l188 lab=rrl__sum_p}
C {devices/lab_wire.sym} -805 690 0 1 {name=l189 lab=rrl__sum_p}
C {devices/lab_wire.sym} 1210 560 0 1 {name=l190 lab=rrl__sum_p}
C {devices/lab_wire.sym} 1150 880 0 0 {name=l191 lab=rrl__sum_p}
C {devices/lab_wire.sym} 1920 690 0 1 {name=l192 lab=rrl__sum_p}
C {devices/lab_wire.sym} 2195 690 0 1 {name=l193 lab=rrl__sum_p}
C {devices/lab_wire.sym} 320 520 0 1 {name=l194 lab=rrl__vb1}
C {devices/lab_wire.sym} 2420 520 0 0 {name=l195 lab=rrl__vb1}
C {devices/lab_wire.sym} -145 840 2 0 {name=l196 lab=rrl__vb2}
C {devices/lab_wire.sym} 1400 780 0 0 {name=l197 lab=rrl__vb2}
C {devices/lab_wire.sym} 1490 60 2 0 {name=l198 lab=rrl__vb3}
C {devices/lab_wire.sym} 2380 0 0 0 {name=l199 lab=rrl__vb3}
C {devices/lab_wire.sym} 2960 320 2 0 {name=l200 lab=rrl__vb4}
C {devices/lab_wire.sym} 3280 260 0 1 {name=l201 lab=rrl__vb4}
C {devices/lab_wire.sym} 470 0 0 1 {name=l202 lab=vb4_ctl}
C {devices/lab_wire.sym} 960 60 2 0 {name=l203 lab=vb4_ctl}
C {devices/lab_wire.sym} 1230 60 2 0 {name=l204 lab=vb4_ctl}
C {devices/lab_wire.sym} 1800 0 0 1 {name=l205 lab=vb4_ctl}
C {devices/lab_wire.sym} 575 940 0 0 {name=l206 lab=vcmfb_raw}
C {devices/lab_wire.sym} 1730 1000 2 0 {name=l207 lab=vcmfb_raw}
C {devices/lab_wire.sym} -1820 430 0 1 {name=l208 lab=vinn}
C {devices/lab_wire.sym} -1360 430 0 1 {name=l209 lab=vinn}
C {devices/lab_wire.sym} 3890 430 0 1 {name=l210 lab=vinn}
C {devices/lab_wire.sym} 4580 430 0 1 {name=l211 lab=vinn}
C {devices/lab_wire.sym} -2050 430 0 1 {name=l212 lab=vinp}
C {devices/lab_wire.sym} -1595 430 0 1 {name=l213 lab=vinp}
C {devices/lab_wire.sym} 4120 430 0 1 {name=l214 lab=vinp}
C {devices/lab_wire.sym} 4810 430 0 1 {name=l215 lab=vinp}
C {devices/lab_wire.sym} -1595 870 2 0 {name=l216 lab=voutn}
C {devices/lab_wire.sym} -555 870 2 0 {name=l217 lab=voutn}
C {devices/lab_wire.sym} 370 90 2 0 {name=l218 lab=voutn}
C {devices/lab_wire.sym} 1450 170 0 1 {name=l219 lab=voutn}
C {devices/lab_wire.sym} 1495 300 0 1 {name=l220 lab=voutn}
C {devices/lab_wire.sym} 3180 870 2 0 {name=l221 lab=voutn}
C {devices/lab_wire.sym} 4120 870 2 0 {name=l222 lab=voutn}
C {devices/lab_wire.sym} 5440 610 2 0 {name=l223 lab=voutn}
C {devices/lab_wire.sym} -1820 870 2 0 {name=l224 lab=voutp}
C {devices/lab_wire.sym} 1190 170 0 1 {name=l225 lab=voutp}
C {devices/lab_wire.sym} 1165 420 0 0 {name=l226 lab=voutp}
C {devices/lab_wire.sym} 1700 90 2 0 {name=l227 lab=voutp}
C {devices/lab_wire.sym} 2660 870 2 0 {name=l228 lab=voutp}
C {devices/lab_wire.sym} 2920 870 2 0 {name=l229 lab=voutp}
C {devices/lab_wire.sym} 4355 870 2 0 {name=l230 lab=voutp}
C {devices/lab_wire.sym} 5190 610 2 0 {name=l231 lab=voutp}
C {devices/lab_wire.sym} -785 610 2 0 {name=l232 lab=vref}
C {devices/lab_wire.sym} 3200 610 2 0 {name=l233 lab=vref}
C {devices/lab_wire.sym} -2360 610 2 0 {name=l234 lab=vref_cm}
C {devices/lab_wire.sym} 5000 610 2 0 {name=l235 lab=vref_cm}
C {devices/lab_wire.sym} 860 354 2 0 {name=l236 lab=vdd}
C {devices/lab_wire.sym} 160 614 2 0 {name=l237 lab=vdd}
C {devices/lab_wire.sym} 2065 354 2 0 {name=l238 lab=vdd}
C {devices/lab_wire.sym} 1325 614 2 0 {name=l239 lab=vdd}
C {devices/lab_wire.sym} 6415 614 2 0 {name=l240 lab=vdd}
C {devices/lab_wire.sym} 1130 94 2 0 {name=l241 lab=vdd}
C {devices/lab_wire.sym} 2540 94 2 0 {name=l242 lab=vdd}
C {devices/lab_wire.sym} 2860 874 2 0 {name=l243 lab=vdd}
C {devices/lab_wire.sym} 3120 874 2 0 {name=l244 lab=vdd}
C {devices/lab_wire.sym} -1420 614 2 0 {name=l245 lab=vdd}
C {devices/lab_wire.sym} -1655 614 2 0 {name=l246 lab=vdd}
C {devices/lab_wire.sym} -205 614 2 0 {name=l247 lab=vdd}
C {devices/lab_wire.sym} -865 874 2 0 {name=l248 lab=vdd}
C {devices/lab_wire.sym} 3555 874 2 0 {name=l249 lab=vdd}
C {devices/lab_wire.sym} -1140 874 2 0 {name=l250 lab=vdd}
C {devices/lab_wire.sym} 3830 874 2 0 {name=l251 lab=vdd}
C {devices/lab_wire.sym} 1640 354 2 0 {name=l252 lab=vdd}
C {devices/lab_wire.sym} 2580 354 2 0 {name=l253 lab=vdd}
C {devices/lab_wire.sym} 310 1134 2 0 {name=l254 lab=vdd}
C {devices/lab_wire.sym} 2135 1134 2 0 {name=l255 lab=vdd}
C {devices/lab_wire.sym} 4295 614 2 0 {name=l256 lab=vdd}
C {devices/lab_wire.sym} 2030 614 2 0 {name=l257 lab=vdd}
C {devices/lab_wire.sym} -1420 874 2 0 {name=l258 lab=vdd}
C {devices/lab_wire.sym} 1095 874 2 0 {name=l259 lab=vdd}
C {devices/lab_wire.sym} 6870 614 2 0 {name=l260 lab=vdd}
C {devices/lab_wire.sym} 4520 614 2 0 {name=l261 lab=vdd}
C {devices/lab_wire.sym} 4750 614 2 0 {name=l262 lab=vdd}
C {devices/lab_wire.sym} -1655 874 2 0 {name=l263 lab=vdd}
C {devices/lab_wire.sym} -1880 874 2 0 {name=l264 lab=vdd}
C {devices/lab_wire.sym} -135 354 2 0 {name=l265 lab=vdd}
C {devices/lab_wire.sym} 160 354 2 0 {name=l266 lab=vdd}
C {devices/lab_wire.sym} 1390 94 2 0 {name=l267 lab=vdd}
C {devices/lab_wire.sym} -355 354 2 0 {name=l268 lab=vdd}
C {devices/lab_wire.sym} 860 94 2 0 {name=l269 lab=vdd}
C {devices/lab_wire.sym} 2860 354 2 0 {name=l270 lab=vdd}
C {devices/lab_wire.sym} 2065 94 2 0 {name=l271 lab=vdd}
C {devices/lab_wire.sym} -615 354 2 0 {name=l272 lab=vdd}
C {devices/lab_wire.sym} 1640 94 2 0 {name=l273 lab=vdd}
C {devices/lab_wire.sym} 3120 354 2 0 {name=l274 lab=vdd}
C {devices/lab_wire.sym} 310 94 2 0 {name=l275 lab=vdd}
C {devices/lab_wire.sym} 2580 614 2 0 {name=l276 lab=vdd}
C {devices/lab_wire.sym} -245 874 2 0 {name=l277 lab=vss}
C {devices/lab_wire.sym} 5960 614 2 0 {name=l278 lab=vss}
C {devices/lab_wire.sym} 1560 874 2 0 {name=l279 lab=vss}
C {devices/lab_wire.sym} 860 614 2 0 {name=l280 lab=vss}
C {devices/lab_wire.sym} -245 1134 2 0 {name=l281 lab=vss}
C {devices/lab_wire.sym} 1130 354 2 0 {name=l282 lab=vss}
C {devices/lab_wire.sym} 1560 1134 2 0 {name=l283 lab=vss}
C {devices/lab_wire.sym} 1390 354 2 0 {name=l284 lab=vss}
C {devices/lab_wire.sym} 610 614 2 0 {name=l285 lab=vss}
C {devices/lab_wire.sym} 1095 614 2 0 {name=l286 lab=vss}
C {devices/lab_wire.sym} 3555 614 2 0 {name=l287 lab=vss}
C {devices/lab_wire.sym} 6190 614 2 0 {name=l288 lab=vss}
C {devices/lab_wire.sym} 1860 874 2 0 {name=l289 lab=vss}
C {devices/lab_wire.sym} 310 874 2 0 {name=l290 lab=vss}
C {devices/lab_wire.sym} 2195 780 0 0 {name=l291 lab=vss}
C {devices/lab_wire.sym} 30 874 2 0 {name=l292 lab=vss}
C {devices/lab_wire.sym} 545 1134 2 0 {name=l293 lab=vss}
C {devices/lab_wire.sym} 1860 1134 2 0 {name=l294 lab=vss}
C {devices/lab_wire.sym} -1140 614 2 0 {name=l295 lab=vss}
C {devices/lab_wire.sym} 1560 614 2 0 {name=l296 lab=vss}
C {devices/lab_wire.sym} 2370 874 2 0 {name=l297 lab=vss}
C {devices/lab_wire.sym} 860 874 2 0 {name=l298 lab=vss}
C {devices/lab_wire.sym} 2600 874 2 0 {name=l299 lab=vss}
C {devices/lab_wire.sym} -615 874 2 0 {name=l300 lab=vss}
C {devices/lab_wire.sym} 3830 614 2 0 {name=l301 lab=vss}
C {devices/lab_wire.sym} 4060 614 2 0 {name=l302 lab=vss}
C {devices/lab_wire.sym} 1790 614 2 0 {name=l303 lab=vss}
C {devices/lab_wire.sym} 6645 614 2 0 {name=l304 lab=vss}
C {devices/lab_wire.sym} -1880 614 2 0 {name=l305 lab=vss}
C {devices/lab_wire.sym} -2110 614 2 0 {name=l306 lab=vss}
C {devices/lab_wire.sym} 4060 874 2 0 {name=l307 lab=vss}
C {devices/lab_wire.sym} 4295 874 2 0 {name=l308 lab=vss}
C {devices/lab_wire.sym} 4520 874 2 0 {name=l309 lab=vss}
C {devices/lab_wire.sym} -2110 874 2 0 {name=l310 lab=vss}
C {devices/lab_wire.sym} -3230 170 0 1 {name=l311 lab=vref_cm}
C {devices/lab_wire.sym} -2890 1130 2 0 {name=l312 lab=vss}
C {devices/lab_wire.sym} -2890 870 2 0 {name=l313 lab=vss}
C {devices/lab_wire.sym} -2890 610 2 0 {name=l314 lab=vss}
C {devices/lab_wire.sym} -2890 350 2 0 {name=l315 lab=vss}
C {devices/lab_wire.sym} -2890 90 2 0 {name=l316 lab=vss}
C {devices/lab_wire.sym} -3230 1130 2 0 {name=l317 lab=vss}
C {devices/lab_wire.sym} -3230 610 2 0 {name=l318 lab=vss}
C {devices/lab_wire.sym} -3230 350 2 0 {name=l319 lab=vss}
C {devices/lab_wire.sym} -3230 870 2 0 {name=l320 lab=vcmfb_raw}
C {devices/lab_wire.sym} -2890 950 0 1 {name=l321 lab=main__vb1}
C {devices/lab_wire.sym} -2890 690 0 1 {name=l322 lab=rrl__vb1}
C {devices/lab_wire.sym} -2890 430 0 1 {name=l323 lab=main__vb2}
C {devices/lab_wire.sym} -2890 170 0 1 {name=l324 lab=rrl__vb2}
C {devices/lab_wire.sym} -2890 -90 0 1 {name=l325 lab=main__vb3}
C {devices/lab_wire.sym} -3230 950 0 1 {name=l326 lab=rrl__vb3}
C {devices/lab_wire.sym} -3230 690 0 1 {name=l327 lab=vb4_ctl}
C {devices/lab_wire.sym} -3230 430 0 1 {name=l328 lab=rrl__vb4}
C {devices/lab_wire.sym} 1730 820 0 1 {name=l329 lab=vss}
C {devices/lab_wire.sym} 635 820 0 1 {name=l330 lab=vss}
C {devices/lab_wire.sym} 1190 350 2 0 {name=l331 lab=vss}
C {devices/lab_wire.sym} 1450 350 2 0 {name=l332 lab=vss}
C {devices/lab_wire.sym} 3615 610 2 0 {name=l333 lab=vss}
C {devices/ipin.sym} -3430 520 0 0 {name=p0 lab=clk_chin_not}
C {devices/ipin.sym} -3430 640 0 0 {name=p1 lab=clk_phi_2}
C {devices/ipin.sym} -3430 760 0 0 {name=p2 lab=clk_chout}
C {devices/ipin.sym} -3430 880 0 0 {name=p3 lab=clk_chout_not}
C {devices/ipin.sym} -3430 1000 0 0 {name=p4 lab=clk_phi_1}
C {devices/ipin.sym} -3430 1120 0 0 {name=p5 lab=clk_chin}
C {devices/ipin.sym} -3430 1240 0 0 {name=p6 lab=clk_chfb}
C {devices/ipin.sym} -3430 1360 0 0 {name=p7 lab=clk_chfb_not}
C {devices/iopin.sym} -785 1320 0 0 {name=p8 lab=vref}
C {devices/opin.sym} 7185 30 0 0 {name=p9 lab=voutn}
C {devices/opin.sym} 7185 150 0 0 {name=p10 lab=voutp}
C {devices/opin.sym} 7185 490 0 0 {name=p11 lab=vinp}
C {devices/opin.sym} 7185 610 0 0 {name=p12 lab=vinn}
B 8 -441 442 1756 1118 {fill=0}
T {NMOS Simple Current Mirror (2 outputs)} -441 424 0 0 0.3 0.3 {layer=8}
B 10 -36 182 2768 598 {fill=0}
T {PMOS Cascode Differential Pair Differential Pair} -36 164 0 0 0.3 0.3 {layer=10}
B 12 939 442 1475 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 939 424 0 0 0.3 0.3 {layer=12}
B 21 6040 442 6571 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 6040 424 0 0 0.3 0.3 {layer=21}
B 15 -174 702 2010 858 {fill=0}
T {NMOS Differential Pair} -174 684 0 0 0.3 0.3 {layer=15}
B 13 -1069 702 2010 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1069 684 0 0 0.3 0.3 {layer=13}
B 18 106 702 2285 858 {fill=0}
T {NMOS Differential Pair} 106 684 0 0 0.3 0.3 {layer=18}
B 20 106 702 3705 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 106 660 0 0 0.3 0.3 {layer=20}
B 8 -1344 702 2285 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1344 684 0 0 0.3 0.3 {layer=8}
B 10 -174 702 3980 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -174 660 0 0 0.3 0.3 {layer=10}
B 12 -1304 442 4445 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1304 424 0 0 0.3 0.3 {layer=12}
B 21 1396 442 2180 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1396 424 0 0 0.3 0.3 {layer=21}
B 15 -1584 702 2520 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1584 684 0 0 0.3 0.3 {layer=15}
B 13 696 702 1245 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 696 684 0 0 0.3 0.3 {layer=13}
B 18 2444 702 3010 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 2444 684 0 0 0.3 0.3 {layer=18}
B 20 2444 702 4445 858 {fill=0}
T {NMOS Differential Pair} 2444 660 0 0 0.3 0.3 {layer=20}
B 8 -771 702 3270 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -771 684 0 0 0.3 0.3 {layer=8}
B 10 -771 702 4210 858 {fill=0}
T {NMOS Differential Pair} -771 660 0 0 0.3 0.3 {layer=10}
B 12 -1576 442 3980 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1576 424 0 0 0.3 0.3 {layer=12}
B 21 -1811 442 4210 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1811 424 0 0 0.3 0.3 {layer=21}
B 15 -361 442 1940 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -361 424 0 0 0.3 0.3 {layer=15}
B 13 -283 182 1790 338 {fill=0}
T {PMOS Differential Pair} -283 164 0 0 0.3 0.3 {layer=13}
B 18 6495 442 7026 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 6495 424 0 0 0.3 0.3 {layer=18}
B 20 -2036 442 4670 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2036 424 0 0 0.3 0.3 {layer=20}
B 8 -2266 442 4900 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2266 424 0 0 0.3 0.3 {layer=8}
B 10 -1811 702 4210 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1811 684 0 0 0.3 0.3 {layer=10}
B 12 -2036 702 4445 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -2036 684 0 0 0.3 0.3 {layer=12}
B 21 -543 182 3010 338 {fill=0}
T {PMOS Differential Pair} -543 164 0 0 0.3 0.3 {layer=21}
B 15 -543 182 3270 338 {fill=0}
T {PMOS Differential Pair} -543 140 0 0 0.3 0.3 {layer=15}
B 13 -803 182 3010 338 {fill=0}
T {PMOS Differential Pair} -803 164 0 0 0.3 0.3 {layer=13}
B 18 -803 182 3270 338 {fill=0}
T {PMOS Differential Pair} -803 140 0 0 0.3 0.3 {layer=18}
B 20 -6 204 2746 316 {fill=0 dash=4}
T {PMOS Differential Pair} -6 186 0 0 0.3 0.3 {layer=20}
