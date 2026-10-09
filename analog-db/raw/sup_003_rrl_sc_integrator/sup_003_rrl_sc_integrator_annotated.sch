v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sup_003_rrl_sc_integrator} -1820 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 760 650 0 0 {name=CAZ1 value='x_dut_caz1_value'}
C {devices/capa_np.sym} 1025 650 0 0 {name=CAZ2 value='x_dut_caz2_value'}
C {devices/capa_np.sym} 760 910 0 0 {name=CINT1 value='x_dut_cint1_value'}
C {devices/capa_np.sym} 1025 910 0 0 {name=CINT2 value='x_dut_cint2_value'}
C {devices/capa_np.sym} 760 1040 0 0 {name=CIN_1 value='cin_val'}
C {devices/capa_np.sym} 1025 520 0 0 {name=COUT_1 value='cout_val'}
C {devices/capa_np.sym} 760 780 0 0 {name=CS1 value='x_dut_cs1_value'}
C {devices/capa_np.sym} 500 780 0 0 {name=CS2 value='x_dut_cs2_value'}
C {devices/vccs.sym} 325 780 0 0 {name=GM_1 value="\{gm_val\}"}
C {devices/res_np.sym} 500 1040 0 0 {name=RIN_1 value='rin_val'}
C {devices/res_np.sym} 1290 520 0 0 {name=ROUT_1 value='rout_val'}
C {devices/vsource_np.sym} -1780 1040 0 0 {name=VB1 value="dc \{vb1\}" savecurrent=false}
C {devices/vsource_np.sym} -1780 780 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -1780 520 0 0 {name=VB3 value="dc \{vb3\}" savecurrent=false}
C {devices/vsource_np.sym} -1780 260 0 0 {name=VB4 value="dc \{vb4\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 475 520 0 1 {name=M10_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_w l=x_dut_xm10_opamp_l m=x_dut_xm10_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 20 780 0 1 {name=M11_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_opamp_w l=x_dut_xm11_opamp_l m=x_dut_xm11_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 1035 780 0 0 {name=M12_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_opamp_w l=x_dut_xm12_opamp_l m=x_dut_xm12_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 20 1040 0 1 {name=M13_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_opamp_w l=x_dut_xm13_opamp_l m=x_dut_xm13_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 1035 1040 0 0 {name=M14_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_opamp_w l=x_dut_xm14_opamp_l m=x_dut_xm14_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 750 520 0 1 {name=M15_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_opamp_w l=x_dut_xm15_opamp_l m=x_dut_xm15_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 165 520 0 1 {name=M16_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_opamp_w l=x_dut_xm16_opamp_l m=x_dut_xm16_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 1505 780 0 1 {name=M1_CHRRL_1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_1_w l=x_dut_xm1_chrrl_1_l m=x_dut_xm1_chrrl_1_m}
C {devices/sg13_lv_nmos_np.sym} 1790 780 0 1 {name=M1_CHRRL_2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_2_w l=x_dut_xm1_chrrl_2_l m=x_dut_xm1_chrrl_2_m}
C {devices/sg13_lv_nmos_np.sym} 2070 780 0 1 {name=M1_CHRRL_3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_3_w l=x_dut_xm1_chrrl_3_l m=x_dut_xm1_chrrl_3_m}
C {devices/sg13_lv_nmos_np.sym} -350 780 0 1 {name=M1_CHRRL_4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_4_w l=x_dut_xm1_chrrl_4_l m=x_dut_xm1_chrrl_4_m}
C {devices/sg13_lv_pmos_np.sym} 1035 0 0 0 {name=M1_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_opamp_w l=x_dut_xm1_opamp_l m=x_dut_xm1_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 325 1040 0 1 {name=M1_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s1_w l=x_dut_xm1_s1_l m=x_dut_xm1_s1_m}
C {devices/sg13_lv_nmos_np.sym} 1505 1040 0 1 {name=M1_S2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s2_w l=x_dut_xm1_s2_l m=x_dut_xm1_s2_m}
C {devices/sg13_lv_nmos_np.sym} -110 520 0 1 {name=M1_S3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s3_w l=x_dut_xm1_s3_l m=x_dut_xm1_s3_m}
C {devices/sg13_lv_nmos_np.sym} 2070 520 0 1 {name=M1_S4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s4_w l=x_dut_xm1_s4_l m=x_dut_xm1_s4_m}
C {devices/sg13_lv_nmos_np.sym} 2310 780 0 1 {name=M1_S5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s5_w l=x_dut_xm1_s5_l m=x_dut_xm1_s5_m}
C {devices/sg13_lv_nmos_np.sym} -635 780 0 1 {name=M1_S6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s6_w l=x_dut_xm1_s6_l m=x_dut_xm1_s6_m}
C {devices/sg13_lv_pmos_np.sym} 2595 780 0 1 {name=M2_CHRRL_1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_1_w l=x_dut_xm2_chrrl_1_l m=x_dut_xm2_chrrl_1_m}
C {devices/sg13_lv_pmos_np.sym} -875 780 0 1 {name=M2_CHRRL_2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_2_w l=x_dut_xm2_chrrl_2_l m=x_dut_xm2_chrrl_2_m}
C {devices/sg13_lv_pmos_np.sym} 2875 780 0 1 {name=M2_CHRRL_3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_3_w l=x_dut_xm2_chrrl_3_l m=x_dut_xm2_chrrl_3_m}
C {devices/sg13_lv_pmos_np.sym} -1160 780 0 1 {name=M2_CHRRL_4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_4_w l=x_dut_xm2_chrrl_4_l m=x_dut_xm2_chrrl_4_m}
C {devices/sg13_lv_pmos_np.sym} 1535 260 0 0 {name=M2_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_w l=x_dut_xm2_opamp_l m=x_dut_xm2_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 1790 1040 0 1 {name=M2_S1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s1_w l=x_dut_xm2_s1_l m=x_dut_xm2_s1_m}
C {devices/sg13_lv_pmos_np.sym} 2070 1040 0 1 {name=M2_S2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s2_w l=x_dut_xm2_s2_l m=x_dut_xm2_s2_m}
C {devices/sg13_lv_pmos_np.sym} -350 520 0 1 {name=M2_S3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s3_w l=x_dut_xm2_s3_l m=x_dut_xm2_s3_m}
C {devices/sg13_lv_pmos_np.sym} 2310 520 0 1 {name=M2_S4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s4_w l=x_dut_xm2_s4_l m=x_dut_xm2_s4_m}
C {devices/sg13_lv_pmos_np.sym} 3120 780 0 1 {name=M2_S5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s5_w l=x_dut_xm2_s5_l m=x_dut_xm2_s5_m}
C {devices/sg13_lv_pmos_np.sym} -1440 780 0 1 {name=M2_S6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s6_w l=x_dut_xm2_s6_l m=x_dut_xm2_s6_m}
C {devices/sg13_lv_pmos_np.sym} 475 260 0 1 {name=M3_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_w l=x_dut_xm3_opamp_l m=x_dut_xm3_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 760 0 0 1 {name=M4_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_opamp_w l=x_dut_xm4_opamp_l m=x_dut_xm4_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 760 260 0 1 {name=M5_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_opamp_w l=x_dut_xm5_opamp_l m=x_dut_xm5_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 1025 260 0 1 {name=M6_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_opamp_w l=x_dut_xm6_opamp_l m=x_dut_xm6_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 1290 260 0 1 {name=M7_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_opamp_w l=x_dut_xm7_opamp_l m=x_dut_xm7_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 165 260 0 1 {name=M8_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_opamp_w l=x_dut_xm8_opamp_l m=x_dut_xm8_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 1535 520 0 0 {name=M9_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_w l=x_dut_xm9_opamp_l m=x_dut_xm9_opamp_m}
N -1780 170 -1780 230 {}
N -1780 290 -1780 350 {}
N -1780 430 -1780 490 {}
N -1780 550 -1780 610 {}
N -1780 690 -1780 750 {}
N -1780 810 -1780 870 {}
N -1780 950 -1780 1010 {}
N -1780 1070 -1780 1130 {}
N -1520 780 -1520 874 {}
N -1460 690 -1460 750 {}
N -1460 810 -1460 870 {}
N -1240 780 -1240 874 {}
N -1180 690 -1180 750 {}
N -1180 810 -1180 870 {}
N -955 780 -955 874 {}
N -895 690 -895 750 {}
N -895 810 -895 870 {}
N -715 780 -715 874 {}
N -655 690 -655 750 {}
N -655 810 -655 870 {}
N -430 520 -430 614 {}
N -430 780 -430 874 {}
N -370 430 -370 490 {}
N -370 550 -370 610 {}
N -370 690 -370 750 {}
N -370 810 -370 870 {}
N -190 580 -190 750 {}
N -130 460 -130 490 {}
N -130 550 -130 580 {}
N -60 810 -60 980 {}
N -60 1040 -60 1134 {}
N 0 810 0 870 {}
N 0 980 0 1010 {}
N 0 1070 0 1180 {}
N 85 60 85 200 {}
N 85 260 85 354 {}
N 85 520 85 614 {}
N 145 200 145 230 {}
N 145 290 145 350 {}
N 145 430 145 490 {}
N 145 550 145 1180 {}
N 185 450 185 520 {}
N 245 1040 245 1134 {}
N 305 950 305 1010 {}
N 305 1070 305 1180 {}
N 325 690 325 750 {}
N 325 810 325 870 {}
N 345 1040 345 1100 {}
N 395 260 395 354 {}
N 395 520 395 614 {}
N 440 970 440 1010 {}
N 455 170 455 230 {}
N 455 290 455 350 {}
N 455 430 455 490 {}
N 455 550 455 610 {}
N 500 690 500 750 {}
N 500 810 500 870 {}
N 500 1070 500 1130 {}
N 670 520 670 614 {}
N 680 0 680 94 {}
N 680 260 680 354 {}
N 700 970 700 1010 {}
N 730 450 730 490 {}
N 730 550 730 1180 {}
N 740 -140 740 -30 {}
N 740 30 740 90 {}
N 740 170 740 230 {}
N 740 290 740 350 {}
N 760 590 760 620 {}
N 760 680 760 710 {}
N 760 850 760 880 {}
N 760 940 760 970 {}
N 760 1070 760 1100 {}
N 770 450 770 520 {}
N 790 320 790 490 {}
N 945 260 945 354 {}
N 995 60 995 200 {}
N 1005 170 1005 230 {}
N 1005 290 1005 350 {}
N 1025 460 1025 490 {}
N 1025 560 1025 620 {}
N 1025 680 1025 740 {}
N 1025 820 1025 880 {}
N 1025 940 1025 1000 {}
N 1055 -140 1055 -30 {}
N 1055 30 1055 90 {}
N 1055 690 1055 750 {}
N 1055 810 1055 870 {}
N 1055 950 1055 1010 {}
N 1055 1070 1055 1180 {}
N 1115 0 1115 94 {}
N 1115 780 1115 874 {}
N 1115 1040 1115 1134 {}
N 1210 260 1210 354 {}
N 1270 290 1270 350 {}
N 1290 460 1290 490 {}
N 1340 260 1340 640 {}
N 1425 780 1425 874 {}
N 1425 1040 1425 1134 {}
N 1485 690 1485 750 {}
N 1485 810 1485 870 {}
N 1485 950 1485 1010 {}
N 1485 1070 1485 1180 {}
N 1515 460 1515 520 {}
N 1555 200 1555 230 {}
N 1555 290 1555 490 {}
N 1555 550 1555 610 {}
N 1615 260 1615 354 {}
N 1615 520 1615 614 {}
N 1710 780 1710 874 {}
N 1710 1040 1710 1134 {}
N 1770 690 1770 750 {}
N 1770 810 1770 870 {}
N 1770 950 1770 1010 {}
N 1770 1070 1770 1180 {}
N 1840 1040 1840 1100 {}
N 1990 520 1990 614 {}
N 1990 780 1990 874 {}
N 1990 1040 1990 1134 {}
N 2050 430 2050 490 {}
N 2050 550 2050 640 {}
N 2050 690 2050 750 {}
N 2050 810 2050 870 {}
N 2050 950 2050 1010 {}
N 2050 1070 2050 1180 {}
N 2120 1040 2120 1100 {}
N 2230 520 2230 614 {}
N 2230 780 2230 874 {}
N 2290 460 2290 490 {}
N 2290 550 2290 580 {}
N 2290 690 2290 750 {}
N 2290 810 2290 870 {}
N 2360 520 2360 780 {}
N 2515 780 2515 874 {}
N 2575 690 2575 750 {}
N 2575 810 2575 870 {}
N 2795 780 2795 874 {}
N 2855 690 2855 750 {}
N 2855 810 2855 870 {}
N 3040 780 3040 874 {}
N 3100 690 3100 750 {}
N 3100 810 3100 870 {}
N -1990 -140 3230 -140 {}
N 680 0 740 0 {}
N 780 0 1015 0 {}
N 1055 0 1115 0 {}
N 85 60 740 60 {}
N 995 60 1055 60 {}
N 85 200 145 200 {}
N 995 200 1555 200 {}
N 945 230 1270 230 {}
N 85 260 145 260 {}
N 185 260 245 260 {}
N 395 260 455 260 {}
N 495 260 555 260 {}
N 680 260 740 260 {}
N 780 260 840 260 {}
N 945 260 1005 260 {}
N 1045 260 1105 260 {}
N 1210 260 1270 260 {}
N 1310 260 1370 260 {}
N 1455 260 1515 260 {}
N 1555 260 1615 260 {}
N 145 320 790 320 {}
N 145 450 185 450 {}
N 730 450 770 450 {}
N -370 460 -130 460 {}
N 1025 460 1290 460 {}
N 2050 460 2290 460 {}
N 730 490 790 490 {}
N -430 520 -370 520 {}
N -330 520 -270 520 {}
N -90 520 -30 520 {}
N 85 520 145 520 {}
N 395 520 455 520 {}
N 495 520 555 520 {}
N 670 520 730 520 {}
N 1555 520 1615 520 {}
N 1990 520 2050 520 {}
N 2090 520 2150 520 {}
N 2230 520 2290 520 {}
N 2330 520 2390 520 {}
N 965 550 1290 550 {}
N -370 580 -130 580 {}
N 2050 580 2290 580 {}
N 700 620 760 620 {}
N 1340 640 2050 640 {}
N 700 680 760 680 {}
N -190 750 0 750 {}
N 225 760 285 760 {}
N -1520 780 -1460 780 {}
N -1420 780 -1390 780 {}
N -1240 780 -1180 780 {}
N -1140 780 -1110 780 {}
N -955 780 -895 780 {}
N -855 780 -825 780 {}
N -715 780 -655 780 {}
N -615 780 -585 780 {}
N -430 780 -370 780 {}
N -330 780 -270 780 {}
N 40 780 1015 780 {}
N 1055 780 1115 780 {}
N 1425 780 1485 780 {}
N 1525 780 1585 780 {}
N 1710 780 1770 780 {}
N 1810 780 1870 780 {}
N 1990 780 2050 780 {}
N 2090 780 2150 780 {}
N 2230 780 2290 780 {}
N 2330 780 2360 780 {}
N 2515 780 2575 780 {}
N 2615 780 2675 780 {}
N 2795 780 2855 780 {}
N 2895 780 2955 780 {}
N 3040 780 3100 780 {}
N 3140 780 3200 780 {}
N 225 800 285 800 {}
N -60 810 0 810 {}
N 700 880 760 880 {}
N 700 940 760 940 {}
N 440 970 760 970 {}
N -60 980 0 980 {}
N 440 1010 500 1010 {}
N 700 1010 760 1010 {}
N -60 1040 0 1040 {}
N 40 1040 100 1040 {}
N 245 1040 305 1040 {}
N 345 1040 375 1040 {}
N 955 1040 1015 1040 {}
N 1055 1040 1115 1040 {}
N 1425 1040 1485 1040 {}
N 1525 1040 1585 1040 {}
N 1710 1040 1770 1040 {}
N 1810 1040 1870 1040 {}
N 1990 1040 2050 1040 {}
N 2090 1040 2120 1040 {}
N 500 1100 760 1100 {}
N 1840 1100 2120 1100 {}
N -1990 1180 3230 1180 {}
C {devices/lab_wire.sym} 1585 780 0 1 {name=l0 lab=clk_ch_rrl}
C {devices/lab_wire.sym} 1870 780 0 1 {name=l1 lab=clk_ch_rrl}
C {devices/lab_wire.sym} 2955 780 0 1 {name=l2 lab=clk_ch_rrl}
C {devices/lab_wire.sym} -270 780 0 1 {name=l3 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} 2150 780 0 1 {name=l4 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} 2675 780 0 1 {name=l5 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} -270 520 0 1 {name=l6 lab=clk_phi_1}
C {devices/lab_wire.sym} 1870 1040 0 1 {name=l7 lab=clk_phi_1}
C {devices/lab_wire.sym} 2390 520 0 1 {name=l8 lab=clk_phi_1}
C {devices/lab_wire.sym} -30 520 0 1 {name=l9 lab=clk_phi_2}
C {devices/lab_wire.sym} 345 1100 2 0 {name=l10 lab=clk_phi_2}
C {devices/lab_wire.sym} 1585 1040 0 1 {name=l11 lab=clk_phi_2}
C {devices/lab_wire.sym} 2150 520 0 1 {name=l12 lab=clk_phi_2}
C {devices/lab_wire.sym} 3200 780 0 1 {name=l13 lab=clk_phi_2}
C {devices/lab_wire.sym} -1460 870 2 0 {name=l14 lab=int_n}
C {devices/lab_wire.sym} -655 870 2 0 {name=l15 lab=int_n}
C {devices/lab_wire.sym} 225 800 0 0 {name=l16 lab=int_n}
C {devices/lab_wire.sym} 500 1130 2 0 {name=l17 lab=int_n}
C {devices/lab_wire.sym} 1025 1000 2 0 {name=l18 lab=int_n}
C {devices/lab_wire.sym} 225 760 0 0 {name=l19 lab=int_p}
C {devices/lab_wire.sym} 700 940 0 0 {name=l20 lab=int_p}
C {devices/lab_wire.sym} 2290 870 2 0 {name=l21 lab=int_p}
C {devices/lab_wire.sym} 3100 870 2 0 {name=l22 lab=int_p}
C {devices/lab_wire.sym} 100 1040 0 1 {name=l23 lab=oa_cm_bias}
C {devices/lab_wire.sym} 145 350 2 0 {name=l24 lab=oa_cm_bias}
C {devices/lab_wire.sym} 1005 350 2 0 {name=l25 lab=oa_cm_bias}
C {devices/lab_wire.sym} 955 1040 0 0 {name=l26 lab=oa_cm_bias}
C {devices/lab_wire.sym} 145 430 0 1 {name=l27 lab=oa_cm_sense}
C {devices/lab_wire.sym} 740 350 2 0 {name=l28 lab=oa_cm_sense}
C {devices/lab_wire.sym} 1270 350 2 0 {name=l29 lab=oa_cm_sense}
C {devices/lab_wire.sym} 740 90 2 0 {name=l30 lab=oa_cm_tail}
C {devices/lab_wire.sym} 740 170 0 1 {name=l31 lab=oa_cm_tail}
C {devices/lab_wire.sym} 1005 170 0 1 {name=l32 lab=oa_cm_tail}
C {devices/lab_wire.sym} 0 870 2 0 {name=l33 lab=oa_csrc_n}
C {devices/lab_wire.sym} 1055 870 2 0 {name=l34 lab=oa_csrc_p}
C {devices/lab_wire.sym} 1055 950 0 1 {name=l35 lab=oa_csrc_p}
C {devices/lab_wire.sym} 1555 350 2 0 {name=l36 lab=oa_d1n}
C {devices/lab_wire.sym} 455 350 2 0 {name=l37 lab=oa_d1p}
C {devices/lab_wire.sym} 455 430 0 1 {name=l38 lab=oa_d1p}
C {devices/lab_wire.sym} 555 260 0 1 {name=l39 lab=oa_inn}
C {devices/lab_wire.sym} 1025 740 2 0 {name=l40 lab=oa_inn}
C {devices/lab_wire.sym} 2050 430 0 1 {name=l41 lab=oa_inn}
C {devices/lab_wire.sym} -370 430 0 1 {name=l42 lab=oa_inp}
C {devices/lab_wire.sym} 700 680 0 0 {name=l43 lab=oa_inp}
C {devices/lab_wire.sym} 1455 260 0 0 {name=l44 lab=oa_inp}
C {devices/lab_wire.sym} -370 610 2 0 {name=l45 lab=oa_outn}
C {devices/lab_wire.sym} 840 260 0 1 {name=l46 lab=oa_outn}
C {devices/lab_wire.sym} 1555 610 2 0 {name=l47 lab=oa_outn}
C {devices/lab_wire.sym} 2290 690 0 1 {name=l48 lab=oa_outn}
C {devices/lab_wire.sym} 3100 690 0 1 {name=l49 lab=oa_outn}
C {devices/lab_wire.sym} -1460 690 0 1 {name=l50 lab=oa_outp}
C {devices/lab_wire.sym} -655 690 0 1 {name=l51 lab=oa_outp}
C {devices/lab_wire.sym} 455 610 2 0 {name=l52 lab=oa_outp}
C {devices/lab_wire.sym} 1055 690 0 1 {name=l53 lab=oa_outp}
C {devices/lab_wire.sym} 1370 260 0 1 {name=l54 lab=oa_outp}
C {devices/lab_wire.sym} 455 170 0 1 {name=l55 lab=oa_tail}
C {devices/lab_wire.sym} 1055 90 2 0 {name=l56 lab=oa_tail}
C {devices/lab_wire.sym} -895 870 2 0 {name=l57 lab=sc_n}
C {devices/lab_wire.sym} 305 950 0 1 {name=l58 lab=sc_n}
C {devices/lab_wire.sym} 500 870 2 0 {name=l59 lab=sc_n}
C {devices/lab_wire.sym} 1770 870 2 0 {name=l60 lab=sc_n}
C {devices/lab_wire.sym} 1770 950 0 1 {name=l61 lab=sc_n}
C {devices/lab_wire.sym} 2050 870 2 0 {name=l62 lab=sc_n}
C {devices/lab_wire.sym} 2855 870 2 0 {name=l63 lab=sc_n}
C {devices/lab_wire.sym} -1180 870 2 0 {name=l64 lab=sc_p}
C {devices/lab_wire.sym} -370 870 2 0 {name=l65 lab=sc_p}
C {devices/lab_wire.sym} 760 810 0 0 {name=l66 lab=sc_p}
C {devices/lab_wire.sym} 1485 870 2 0 {name=l67 lab=sc_p}
C {devices/lab_wire.sym} 1485 950 0 1 {name=l68 lab=sc_p}
C {devices/lab_wire.sym} 2050 950 0 1 {name=l69 lab=sc_p}
C {devices/lab_wire.sym} 2575 870 2 0 {name=l70 lab=sc_p}
C {devices/lab_wire.sym} -1180 690 0 1 {name=l71 lab=sum_n}
C {devices/lab_wire.sym} -895 690 0 1 {name=l72 lab=sum_n}
C {devices/lab_wire.sym} -370 690 0 1 {name=l73 lab=sum_n}
C {devices/lab_wire.sym} 1025 560 0 1 {name=l74 lab=sum_n}
C {devices/lab_wire.sym} 1025 820 0 1 {name=l75 lab=sum_n}
C {devices/lab_wire.sym} 1770 690 0 1 {name=l76 lab=sum_n}
C {devices/lab_wire.sym} 700 620 0 0 {name=l77 lab=sum_p}
C {devices/lab_wire.sym} 700 880 0 0 {name=l78 lab=sum_p}
C {devices/lab_wire.sym} 1485 690 0 1 {name=l79 lab=sum_p}
C {devices/lab_wire.sym} 2050 690 0 1 {name=l80 lab=sum_p}
C {devices/lab_wire.sym} 2575 690 0 1 {name=l81 lab=sum_p}
C {devices/lab_wire.sym} 2855 690 0 1 {name=l82 lab=sum_p}
C {devices/lab_wire.sym} 555 520 0 1 {name=l83 lab=vb1}
C {devices/lab_wire.sym} 1515 460 0 1 {name=l84 lab=vb1}
C {devices/lab_wire.sym} 100 780 0 1 {name=l85 lab=vb2}
C {devices/lab_wire.sym} 840 0 0 1 {name=l86 lab=vb3}
C {devices/lab_wire.sym} 245 260 0 1 {name=l87 lab=vb4}
C {devices/lab_wire.sym} 1105 260 0 1 {name=l88 lab=vb4}
C {devices/lab_wire.sym} 500 690 0 1 {name=l89 lab=vinn}
C {devices/lab_wire.sym} 760 750 0 0 {name=l90 lab=vinp}
C {devices/lab_wire.sym} 325 690 0 1 {name=l91 lab=voutn}
C {devices/lab_wire.sym} 325 870 2 0 {name=l92 lab=voutp}
C {devices/lab_wire.sym} 395 614 2 0 {name=l93 lab=vdd}
C {devices/lab_wire.sym} 1115 94 2 0 {name=l94 lab=vdd}
C {devices/lab_wire.sym} 2515 874 2 0 {name=l95 lab=vdd}
C {devices/lab_wire.sym} -955 874 2 0 {name=l96 lab=vdd}
C {devices/lab_wire.sym} 2795 874 2 0 {name=l97 lab=vdd}
C {devices/lab_wire.sym} -1240 874 2 0 {name=l98 lab=vdd}
C {devices/lab_wire.sym} 1615 354 2 0 {name=l99 lab=vdd}
C {devices/lab_wire.sym} 1710 1134 2 0 {name=l100 lab=vdd}
C {devices/lab_wire.sym} 1990 1134 2 0 {name=l101 lab=vdd}
C {devices/lab_wire.sym} -430 614 2 0 {name=l102 lab=vdd}
C {devices/lab_wire.sym} 2230 614 2 0 {name=l103 lab=vdd}
C {devices/lab_wire.sym} 3040 874 2 0 {name=l104 lab=vdd}
C {devices/lab_wire.sym} -1520 874 2 0 {name=l105 lab=vdd}
C {devices/lab_wire.sym} 395 354 2 0 {name=l106 lab=vdd}
C {devices/lab_wire.sym} 680 94 2 0 {name=l107 lab=vdd}
C {devices/lab_wire.sym} 680 354 2 0 {name=l108 lab=vdd}
C {devices/lab_wire.sym} 945 354 2 0 {name=l109 lab=vdd}
C {devices/lab_wire.sym} 1210 354 2 0 {name=l110 lab=vdd}
C {devices/lab_wire.sym} 85 354 2 0 {name=l111 lab=vdd}
C {devices/lab_wire.sym} 1615 614 2 0 {name=l112 lab=vdd}
C {devices/lab_wire.sym} 0 780 0 0 {name=l113 lab=vss}
C {devices/lab_wire.sym} 1115 874 2 0 {name=l114 lab=vss}
C {devices/lab_wire.sym} -60 1134 2 0 {name=l115 lab=vss}
C {devices/lab_wire.sym} 1115 1134 2 0 {name=l116 lab=vss}
C {devices/lab_wire.sym} 670 614 2 0 {name=l117 lab=vss}
C {devices/lab_wire.sym} 85 614 2 0 {name=l118 lab=vss}
C {devices/lab_wire.sym} 1425 874 2 0 {name=l119 lab=vss}
C {devices/lab_wire.sym} 1710 874 2 0 {name=l120 lab=vss}
C {devices/lab_wire.sym} 1990 874 2 0 {name=l121 lab=vss}
C {devices/lab_wire.sym} -430 874 2 0 {name=l122 lab=vss}
C {devices/lab_wire.sym} 245 1134 2 0 {name=l123 lab=vss}
C {devices/lab_wire.sym} 1425 1134 2 0 {name=l124 lab=vss}
C {devices/lab_wire.sym} -130 520 0 0 {name=l125 lab=vss}
C {devices/lab_wire.sym} 1990 614 2 0 {name=l126 lab=vss}
C {devices/lab_wire.sym} 2230 874 2 0 {name=l127 lab=vss}
C {devices/lab_wire.sym} -715 874 2 0 {name=l128 lab=vss}
C {devices/lab_wire.sym} -1780 950 0 1 {name=l129 lab=vb1}
C {devices/lab_wire.sym} -1780 1130 2 0 {name=l130 lab=vss}
C {devices/lab_wire.sym} -1780 870 2 0 {name=l131 lab=vss}
C {devices/lab_wire.sym} -1780 610 2 0 {name=l132 lab=vss}
C {devices/lab_wire.sym} -1780 350 2 0 {name=l133 lab=vss}
C {devices/lab_wire.sym} -1780 690 0 1 {name=l134 lab=vb2}
C {devices/lab_wire.sym} -1780 430 0 1 {name=l135 lab=vb3}
C {devices/lab_wire.sym} -1780 170 0 1 {name=l136 lab=vb4}
C {devices/ipin.sym} -585 780 0 0 {name=p0 lab=clk_phi_1}
C {devices/ipin.sym} -1390 780 0 0 {name=p1 lab=clk_phi_2}
C {devices/ipin.sym} -1110 780 0 0 {name=p2 lab=clk_ch_rrl}
C {devices/ipin.sym} -825 780 0 0 {name=p3 lab=clk_ch_rrl_not}
C {devices/iopin.sym} -1990 -140 0 0 {name=p4 lab=vdd}
C {devices/iopin.sym} -1990 1180 0 0 {name=p5 lab=vss}
C {devices/iopin.sym} 1025 460 0 0 {name=p6 lab=voutn}
C {devices/iopin.sym} 965 550 0 0 {name=p7 lab=voutp}
C {devices/iopin.sym} 500 1320 0 0 {name=p8 lab=vinn}
C {devices/iopin.sym} 760 1320 0 0 {name=p9 lab=vinp}
B 8 -604 442 1659 1118 {fill=0}
T {NMOS Simple Current Mirror (2 outputs)} -604 424 0 0 0.3 0.3 {layer=8}
B 10 -149 182 2135 598 {fill=0}
T {PMOS Cascode Differential Pair Differential Pair} -149 164 0 0 0.3 0.3 {layer=10}
B 12 -998 702 1575 858 {fill=0}
T {NMOS Differential Pair} -998 684 0 0 0.3 0.3 {layer=12}
B 21 857 702 2665 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 857 684 0 0 0.3 0.3 {layer=21}
B 15 1142 702 2140 858 {fill=0}
T {NMOS Differential Pair} 1142 684 0 0 0.3 0.3 {layer=15}
B 13 -1523 702 1860 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1523 684 0 0 0.3 0.3 {layer=13}
B 18 1422 702 2945 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1422 684 0 0 0.3 0.3 {layer=18}
B 20 -1808 702 -280 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1808 684 0 0 0.3 0.3 {layer=20}
B 8 -878 442 -40 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -878 424 0 0 0.3 0.3 {layer=8}
B 10 1542 442 2380 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1542 424 0 0 0.3 0.3 {layer=10}
B 12 1782 702 3190 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1782 684 0 0 0.3 0.3 {layer=12}
B 21 -1968 702 -565 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1968 684 0 0 0.3 0.3 {layer=21}
B 15 160 182 1095 338 {fill=0}
T {PMOS Differential Pair} 160 164 0 0 0.3 0.3 {layer=15}
B 13 -435 182 830 338 {fill=0}
T {PMOS Differential Pair} -435 164 0 0 0.3 0.3 {layer=13}
B 18 425 182 1360 338 {fill=0}
T {PMOS Differential Pair} 425 164 0 0 0.3 0.3 {layer=18}
B 20 -435 182 1360 338 {fill=0}
T {PMOS Differential Pair} -435 140 0 0 0.3 0.3 {layer=20}
B 8 -103 204 2113 316 {fill=0 dash=4}
T {PMOS Differential Pair} -103 138 0 0 0.3 0.3 {layer=8}
