v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sup_003_rrl_sc_integrator} -1815 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 645 650 0 0 {name=CAZ1 value='x_dut_caz1_value'}
C {devices/capa_np.sym} 920 650 0 0 {name=CAZ2 value='x_dut_caz2_value'}
C {devices/capa_np.sym} 645 910 0 0 {name=CINT1 value='x_dut_cint1_value'}
C {devices/capa_np.sym} 920 910 0 0 {name=CINT2 value='x_dut_cint2_value'}
C {devices/capa_np.sym} 645 1040 0 0 {name=CIN_1 value='cin_val'}
C {devices/capa_np.sym} 2125 520 0 0 {name=COUT_1 value='cout_val'}
C {devices/capa_np.sym} 2925 780 0 0 {name=CS1 value='x_dut_cs1_value'}
C {devices/capa_np.sym} -1435 780 0 0 {name=CS2 value='x_dut_cs2_value'}
C {devices/vccs.sym} 3175 780 0 0 {name=GM_1 value="\{gm_val\}"}
C {devices/res_np.sym} 365 1040 0 0 {name=RIN_1 value='rin_val'}
C {devices/res_np.sym} -875 520 0 0 {name=ROUT_1 value='rout_val'}
C {devices/vsource_np.sym} -1775 1040 0 0 {name=VB1 value="dc \{vb1\}" savecurrent=false}
C {devices/vsource_np.sym} -1775 780 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -1775 520 0 0 {name=VB3 value="dc \{vb3\}" savecurrent=false}
C {devices/vsource_np.sym} -1775 260 0 0 {name=VB4 value="dc \{vb4\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 355 520 0 1 {name=M10_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_w l=x_dut_xm10_opamp_l m=x_dut_xm10_opamp_m}
C {devices/sg13_lv_nmos_np.sym} -125 780 0 1 {name=M11_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_opamp_w l=x_dut_xm11_opamp_l m=x_dut_xm11_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 930 780 0 0 {name=M12_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_opamp_w l=x_dut_xm12_opamp_l m=x_dut_xm12_opamp_m}
C {devices/sg13_lv_nmos_np.sym} -125 1040 0 1 {name=M13_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_opamp_w l=x_dut_xm13_opamp_l m=x_dut_xm13_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 930 1040 0 0 {name=M14_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_opamp_w l=x_dut_xm14_opamp_l m=x_dut_xm14_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 645 520 0 0 {name=M15_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_opamp_w l=x_dut_xm15_opamp_l m=x_dut_xm15_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 920 520 0 0 {name=M16_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_opamp_w l=x_dut_xm16_opamp_l m=x_dut_xm16_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 645 780 0 0 {name=M1_CHRRL_1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_1_w l=x_dut_xm1_chrrl_1_l m=x_dut_xm1_chrrl_1_m}
C {devices/sg13_lv_nmos_np.sym} 365 780 0 0 {name=M1_CHRRL_2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_2_w l=x_dut_xm1_chrrl_2_l m=x_dut_xm1_chrrl_2_m}
C {devices/sg13_lv_nmos_np.sym} 65 780 0 0 {name=M1_CHRRL_3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_3_w l=x_dut_xm1_chrrl_3_l m=x_dut_xm1_chrrl_3_m}
C {devices/sg13_lv_nmos_np.sym} 1355 780 0 0 {name=M1_CHRRL_4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_4_w l=x_dut_xm1_chrrl_4_l m=x_dut_xm1_chrrl_4_m}
C {devices/sg13_lv_pmos_np.sym} 930 0 0 0 {name=M1_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_opamp_w l=x_dut_xm1_opamp_l m=x_dut_xm1_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 65 1040 0 0 {name=M1_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s1_w l=x_dut_xm1_s1_l m=x_dut_xm1_s1_m}
C {devices/sg13_lv_nmos_np.sym} 1355 1040 0 0 {name=M1_S2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s2_w l=x_dut_xm1_s2_l m=x_dut_xm1_s2_m}
C {devices/sg13_lv_nmos_np.sym} 1195 520 0 0 {name=M1_S3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s3_w l=x_dut_xm1_s3_l m=x_dut_xm1_s3_m}
C {devices/sg13_lv_nmos_np.sym} -95 520 0 0 {name=M1_S4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s4_w l=x_dut_xm1_s4_l m=x_dut_xm1_s4_m}
C {devices/sg13_lv_nmos_np.sym} 1635 780 0 0 {name=M1_S5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s5_w l=x_dut_xm1_s5_l m=x_dut_xm1_s5_m}
C {devices/sg13_lv_nmos_np.sym} 1880 780 0 0 {name=M1_S6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s6_w l=x_dut_xm1_s6_l m=x_dut_xm1_s6_m}
C {devices/sg13_lv_pmos_np.sym} -595 780 0 0 {name=M2_CHRRL_1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_1_w l=x_dut_xm2_chrrl_1_l m=x_dut_xm2_chrrl_1_m}
C {devices/sg13_lv_pmos_np.sym} 2120 780 0 0 {name=M2_CHRRL_2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_2_w l=x_dut_xm2_chrrl_2_l m=x_dut_xm2_chrrl_2_m}
C {devices/sg13_lv_pmos_np.sym} -880 780 0 0 {name=M2_CHRRL_3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_3_w l=x_dut_xm2_chrrl_3_l m=x_dut_xm2_chrrl_3_m}
C {devices/sg13_lv_pmos_np.sym} 2400 780 0 0 {name=M2_CHRRL_4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_4_w l=x_dut_xm2_chrrl_4_l m=x_dut_xm2_chrrl_4_m}
C {devices/sg13_lv_pmos_np.sym} 1460 260 0 0 {name=M2_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_w l=x_dut_xm2_opamp_l m=x_dut_xm2_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 1635 1040 0 0 {name=M2_S1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s1_w l=x_dut_xm2_s1_l m=x_dut_xm2_s1_m}
C {devices/sg13_lv_pmos_np.sym} 1880 1040 0 0 {name=M2_S2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s2_w l=x_dut_xm2_s2_l m=x_dut_xm2_s2_m}
C {devices/sg13_lv_pmos_np.sym} -435 520 0 0 {name=M2_S3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s3_w l=x_dut_xm2_s3_l m=x_dut_xm2_s3_m}
C {devices/sg13_lv_pmos_np.sym} 1880 520 0 0 {name=M2_S4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s4_w l=x_dut_xm2_s4_l m=x_dut_xm2_s4_m}
C {devices/sg13_lv_pmos_np.sym} -1120 780 0 0 {name=M2_S5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s5_w l=x_dut_xm2_s5_l m=x_dut_xm2_s5_m}
C {devices/sg13_lv_pmos_np.sym} 2685 780 0 0 {name=M2_S6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s6_w l=x_dut_xm2_s6_l m=x_dut_xm2_s6_m}
C {devices/sg13_lv_pmos_np.sym} 355 260 0 1 {name=M3_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_w l=x_dut_xm3_opamp_l m=x_dut_xm3_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 645 0 0 0 {name=M4_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_opamp_w l=x_dut_xm4_opamp_l m=x_dut_xm4_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 645 260 0 0 {name=M5_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_opamp_w l=x_dut_xm5_opamp_l m=x_dut_xm5_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 920 260 0 0 {name=M6_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_opamp_w l=x_dut_xm6_opamp_l m=x_dut_xm6_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 1195 260 0 0 {name=M7_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_opamp_w l=x_dut_xm7_opamp_l m=x_dut_xm7_opamp_m}
C {devices/sg13_lv_pmos_np.sym} -95 260 0 0 {name=M8_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_opamp_w l=x_dut_xm8_opamp_l m=x_dut_xm8_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 1460 520 0 0 {name=M9_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_w l=x_dut_xm9_opamp_l m=x_dut_xm9_opamp_m}
N -1775 170 -1775 230 {}
N -1775 290 -1775 350 {}
N -1775 430 -1775 490 {}
N -1775 550 -1775 610 {}
N -1775 690 -1775 750 {}
N -1775 810 -1775 870 {}
N -1775 950 -1775 1010 {}
N -1775 1070 -1775 1130 {}
N -1435 720 -1435 750 {}
N -1435 810 -1435 870 {}
N -1100 720 -1100 750 {}
N -1100 810 -1100 870 {}
N -1040 780 -1040 874 {}
N -875 460 -875 490 {}
N -875 550 -875 580 {}
N -860 690 -860 750 {}
N -860 810 -860 870 {}
N -800 780 -800 874 {}
N -575 690 -575 750 {}
N -575 810 -575 870 {}
N -515 780 -515 874 {}
N -475 490 -475 710 {}
N -415 430 -415 490 {}
N -415 550 -415 610 {}
N -355 550 -355 720 {}
N -205 780 -205 874 {}
N -205 1040 -205 1134 {}
N -145 690 -145 750 {}
N -145 810 -145 870 {}
N -145 950 -145 1010 {}
N -145 1070 -145 1180 {}
N -135 60 -135 200 {}
N -105 1040 -105 1100 {}
N -75 200 -75 230 {}
N -75 290 -75 350 {}
N -75 430 -75 490 {}
N -75 550 -75 610 {}
N -15 260 -15 354 {}
N -15 520 -15 614 {}
N 25 590 25 750 {}
N 25 810 25 980 {}
N 45 720 45 780 {}
N 85 810 85 870 {}
N 85 980 85 1010 {}
N 85 1070 85 1180 {}
N 145 780 145 874 {}
N 145 1040 145 1134 {}
N 275 260 275 354 {}
N 275 520 275 614 {}
N 335 170 335 230 {}
N 335 290 335 350 {}
N 335 430 335 490 {}
N 335 550 335 610 {}
N 365 950 365 1010 {}
N 365 1070 365 1130 {}
N 385 690 385 750 {}
N 385 810 385 870 {}
N 445 780 445 874 {}
N 585 970 585 1010 {}
N 595 -60 595 0 {}
N 605 60 605 230 {}
N 625 450 625 520 {}
N 645 590 645 620 {}
N 645 680 645 710 {}
N 645 850 645 880 {}
N 645 940 645 970 {}
N 645 1070 645 1100 {}
N 665 -140 665 -30 {}
N 665 30 665 90 {}
N 665 290 665 350 {}
N 665 430 665 490 {}
N 665 550 665 610 {}
N 665 690 665 750 {}
N 665 810 665 870 {}
N 725 0 725 94 {}
N 725 260 725 354 {}
N 725 520 725 614 {}
N 725 780 725 874 {}
N 880 -60 880 0 {}
N 890 60 890 200 {}
N 900 450 900 520 {}
N 910 1040 910 1100 {}
N 920 560 920 620 {}
N 920 680 920 740 {}
N 920 820 920 880 {}
N 920 940 920 1000 {}
N 940 290 940 350 {}
N 940 430 940 490 {}
N 940 550 940 1180 {}
N 950 -140 950 -30 {}
N 950 30 950 90 {}
N 950 690 950 750 {}
N 950 810 950 870 {}
N 950 950 950 1010 {}
N 950 1070 950 1180 {}
N 1000 260 1000 354 {}
N 1000 520 1000 614 {}
N 1010 0 1010 94 {}
N 1010 780 1010 874 {}
N 1010 1040 1010 1134 {}
N 1215 170 1215 230 {}
N 1215 290 1215 350 {}
N 1215 430 1215 490 {}
N 1215 550 1215 610 {}
N 1275 260 1275 354 {}
N 1275 520 1275 614 {}
N 1375 690 1375 750 {}
N 1375 810 1375 870 {}
N 1375 950 1375 1010 {}
N 1375 1070 1375 1180 {}
N 1435 780 1435 874 {}
N 1435 1040 1435 1134 {}
N 1480 200 1480 230 {}
N 1480 290 1480 350 {}
N 1480 430 1480 490 {}
N 1480 550 1480 610 {}
N 1540 260 1540 354 {}
N 1540 520 1540 614 {}
N 1585 780 1585 1040 {}
N 1655 690 1655 750 {}
N 1655 810 1655 870 {}
N 1655 950 1655 1010 {}
N 1655 1070 1655 1180 {}
N 1715 780 1715 874 {}
N 1715 1040 1715 1134 {}
N 1830 520 1830 1040 {}
N 1900 430 1900 490 {}
N 1900 550 1900 610 {}
N 1900 690 1900 750 {}
N 1900 810 1900 870 {}
N 1900 950 1900 1010 {}
N 1900 1070 1900 1180 {}
N 1960 520 1960 614 {}
N 1960 780 1960 874 {}
N 1960 1040 1960 1134 {}
N 2125 460 2125 490 {}
N 2125 550 2125 580 {}
N 2140 690 2140 750 {}
N 2140 810 2140 870 {}
N 2200 780 2200 874 {}
N 2420 690 2420 750 {}
N 2420 810 2420 870 {}
N 2480 780 2480 874 {}
N 2705 690 2705 750 {}
N 2705 810 2705 870 {}
N 2765 780 2765 874 {}
N 2925 720 2925 750 {}
N 2925 810 2925 870 {}
N 3175 460 3175 750 {}
N 3175 810 3175 840 {}
N 3235 580 3235 840 {}
N -1835 -140 3420 -140 {}
N 595 -60 880 -60 {}
N 565 0 625 0 {}
N 665 0 725 0 {}
N 880 0 910 0 {}
N 950 0 1010 0 {}
N -135 60 665 60 {}
N 890 60 950 60 {}
N -135 200 -75 200 {}
N 890 200 1480 200 {}
N 605 230 940 230 {}
N -175 260 -115 260 {}
N -75 260 -15 260 {}
N 275 260 335 260 {}
N 375 260 435 260 {}
N 565 260 625 260 {}
N 665 260 725 260 {}
N 840 260 900 260 {}
N 940 260 1000 260 {}
N 1115 260 1175 260 {}
N 1215 260 1275 260 {}
N 1380 260 1440 260 {}
N 1480 260 1540 260 {}
N 625 450 665 450 {}
N 900 450 940 450 {}
N -935 460 3175 460 {}
N -475 490 -415 490 {}
N -545 520 -455 520 {}
N -175 520 -115 520 {}
N -75 520 -15 520 {}
N 275 520 335 520 {}
N 375 520 435 520 {}
N 665 520 725 520 {}
N 940 520 1000 520 {}
N 1115 520 1175 520 {}
N 1215 520 1275 520 {}
N 1380 520 1440 520 {}
N 1480 520 1540 520 {}
N 1800 520 1860 520 {}
N 1900 520 1960 520 {}
N -415 550 -355 550 {}
N -935 580 3235 580 {}
N 25 590 645 590 {}
N 585 620 645 620 {}
N -475 710 645 710 {}
N -1100 720 -355 720 {}
N 25 750 85 750 {}
N 3075 760 3135 760 {}
N -1230 780 -1140 780 {}
N -1100 780 -1040 780 {}
N -990 780 -900 780 {}
N -860 780 -800 780 {}
N -705 780 -615 780 {}
N -575 780 -515 780 {}
N -205 780 -145 780 {}
N -105 780 -45 780 {}
N 15 780 45 780 {}
N 85 780 145 780 {}
N 285 780 345 780 {}
N 385 780 445 780 {}
N 565 780 625 780 {}
N 665 780 725 780 {}
N 850 780 910 780 {}
N 950 780 1010 780 {}
N 1275 780 1335 780 {}
N 1375 780 1435 780 {}
N 1555 780 1615 780 {}
N 1655 780 1715 780 {}
N 1830 780 1860 780 {}
N 1900 780 1960 780 {}
N 2040 780 2100 780 {}
N 2140 780 2200 780 {}
N 2320 780 2380 780 {}
N 2420 780 2480 780 {}
N 2605 780 2665 780 {}
N 2705 780 2765 780 {}
N 3075 800 3135 800 {}
N 25 810 85 810 {}
N 3175 840 3235 840 {}
N 585 880 645 880 {}
N 585 940 645 940 {}
N 585 970 645 970 {}
N 25 980 85 980 {}
N 585 1010 645 1010 {}
N -205 1040 -145 1040 {}
N -105 1040 -75 1040 {}
N 15 1040 45 1040 {}
N 85 1040 145 1040 {}
N 880 1040 910 1040 {}
N 950 1040 1010 1040 {}
N 1275 1040 1335 1040 {}
N 1375 1040 1435 1040 {}
N 1585 1040 1615 1040 {}
N 1655 1040 1715 1040 {}
N 1830 1040 1860 1040 {}
N 1900 1040 1960 1040 {}
N 365 1100 645 1100 {}
N -1835 1180 3420 1180 {}
C {devices/lab_wire.sym} 285 780 0 0 {name=l0 lab=clk_ch_rrl}
C {devices/lab_wire.sym} 565 780 0 0 {name=l1 lab=clk_ch_rrl}
C {devices/lab_wire.sym} 2320 780 0 0 {name=l2 lab=clk_ch_rrl}
C {devices/lab_wire.sym} 45 720 0 1 {name=l3 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} 1275 780 0 0 {name=l4 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} 2040 780 0 0 {name=l5 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} 1555 780 0 0 {name=l6 lab=clk_phi_1}
C {devices/lab_wire.sym} 1800 520 0 0 {name=l7 lab=clk_phi_1}
C {devices/lab_wire.sym} -175 520 0 0 {name=l8 lab=clk_phi_2}
C {devices/lab_wire.sym} 45 1040 0 0 {name=l9 lab=clk_phi_2}
C {devices/lab_wire.sym} 1115 520 0 0 {name=l10 lab=clk_phi_2}
C {devices/lab_wire.sym} 1275 1040 0 0 {name=l11 lab=clk_phi_2}
C {devices/lab_wire.sym} 2605 780 0 0 {name=l12 lab=clk_phi_2}
C {devices/lab_wire.sym} 365 1130 2 0 {name=l13 lab=int_n}
C {devices/lab_wire.sym} 920 1000 2 0 {name=l14 lab=int_n}
C {devices/lab_wire.sym} 1900 870 2 0 {name=l15 lab=int_n}
C {devices/lab_wire.sym} 2705 870 2 0 {name=l16 lab=int_n}
C {devices/lab_wire.sym} 3075 800 0 0 {name=l17 lab=int_n}
C {devices/lab_wire.sym} -1100 870 2 0 {name=l18 lab=int_p}
C {devices/lab_wire.sym} 365 950 0 1 {name=l19 lab=int_p}
C {devices/lab_wire.sym} 585 940 0 0 {name=l20 lab=int_p}
C {devices/lab_wire.sym} 1655 870 2 0 {name=l21 lab=int_p}
C {devices/lab_wire.sym} 3075 760 0 0 {name=l22 lab=int_p}
C {devices/lab_wire.sym} -105 1100 2 0 {name=l23 lab=oa_cm_bias}
C {devices/lab_wire.sym} -75 350 2 0 {name=l24 lab=oa_cm_bias}
C {devices/lab_wire.sym} 665 430 0 1 {name=l25 lab=oa_cm_bias}
C {devices/lab_wire.sym} 910 1100 2 0 {name=l26 lab=oa_cm_bias}
C {devices/lab_wire.sym} 940 350 2 0 {name=l27 lab=oa_cm_bias}
C {devices/lab_wire.sym} 665 350 2 0 {name=l28 lab=oa_cm_sense}
C {devices/lab_wire.sym} 940 430 0 1 {name=l29 lab=oa_cm_sense}
C {devices/lab_wire.sym} 1215 350 2 0 {name=l30 lab=oa_cm_sense}
C {devices/lab_wire.sym} 665 90 2 0 {name=l31 lab=oa_cm_tail}
C {devices/lab_wire.sym} 1215 170 0 1 {name=l32 lab=oa_cm_tail}
C {devices/lab_wire.sym} -145 870 2 0 {name=l33 lab=oa_csrc_n}
C {devices/lab_wire.sym} -145 950 0 1 {name=l34 lab=oa_csrc_n}
C {devices/lab_wire.sym} 950 870 2 0 {name=l35 lab=oa_csrc_p}
C {devices/lab_wire.sym} 950 950 0 1 {name=l36 lab=oa_csrc_p}
C {devices/lab_wire.sym} 1480 350 2 0 {name=l37 lab=oa_d1n}
C {devices/lab_wire.sym} 1480 430 0 1 {name=l38 lab=oa_d1n}
C {devices/lab_wire.sym} 335 350 2 0 {name=l39 lab=oa_d1p}
C {devices/lab_wire.sym} 335 430 0 1 {name=l40 lab=oa_d1p}
C {devices/lab_wire.sym} -75 430 0 1 {name=l41 lab=oa_inn}
C {devices/lab_wire.sym} 435 260 0 1 {name=l42 lab=oa_inn}
C {devices/lab_wire.sym} 920 740 2 0 {name=l43 lab=oa_inn}
C {devices/lab_wire.sym} 1900 430 0 1 {name=l44 lab=oa_inn}
C {devices/lab_wire.sym} -415 430 0 1 {name=l45 lab=oa_inp}
C {devices/lab_wire.sym} 1215 430 0 1 {name=l46 lab=oa_inp}
C {devices/lab_wire.sym} 1380 260 0 0 {name=l47 lab=oa_inp}
C {devices/lab_wire.sym} -415 610 2 0 {name=l48 lab=oa_outn}
C {devices/lab_wire.sym} -145 690 0 1 {name=l49 lab=oa_outn}
C {devices/lab_wire.sym} 565 260 0 0 {name=l50 lab=oa_outn}
C {devices/lab_wire.sym} 1215 610 2 0 {name=l51 lab=oa_outn}
C {devices/lab_wire.sym} 1480 610 2 0 {name=l52 lab=oa_outn}
C {devices/lab_wire.sym} 1655 690 0 1 {name=l53 lab=oa_outn}
C {devices/lab_wire.sym} -75 610 2 0 {name=l54 lab=oa_outp}
C {devices/lab_wire.sym} 335 610 2 0 {name=l55 lab=oa_outp}
C {devices/lab_wire.sym} 950 690 0 1 {name=l56 lab=oa_outp}
C {devices/lab_wire.sym} 1115 260 0 0 {name=l57 lab=oa_outp}
C {devices/lab_wire.sym} 1900 610 2 0 {name=l58 lab=oa_outp}
C {devices/lab_wire.sym} 1900 690 0 1 {name=l59 lab=oa_outp}
C {devices/lab_wire.sym} 2705 690 0 1 {name=l60 lab=oa_outp}
C {devices/lab_wire.sym} 335 170 0 1 {name=l61 lab=oa_tail}
C {devices/lab_wire.sym} 950 90 2 0 {name=l62 lab=oa_tail}
C {devices/lab_wire.sym} -1435 870 2 0 {name=l63 lab=sc_n}
C {devices/lab_wire.sym} -860 870 2 0 {name=l64 lab=sc_n}
C {devices/lab_wire.sym} 85 870 2 0 {name=l65 lab=sc_n}
C {devices/lab_wire.sym} 385 870 2 0 {name=l66 lab=sc_n}
C {devices/lab_wire.sym} 1655 950 0 1 {name=l67 lab=sc_n}
C {devices/lab_wire.sym} 2140 870 2 0 {name=l68 lab=sc_n}
C {devices/lab_wire.sym} -575 870 2 0 {name=l69 lab=sc_p}
C {devices/lab_wire.sym} 665 870 2 0 {name=l70 lab=sc_p}
C {devices/lab_wire.sym} 1375 870 2 0 {name=l71 lab=sc_p}
C {devices/lab_wire.sym} 1375 950 0 1 {name=l72 lab=sc_p}
C {devices/lab_wire.sym} 1900 950 0 1 {name=l73 lab=sc_p}
C {devices/lab_wire.sym} 2420 870 2 0 {name=l74 lab=sc_p}
C {devices/lab_wire.sym} 2925 870 2 0 {name=l75 lab=sc_p}
C {devices/lab_wire.sym} 385 690 0 1 {name=l76 lab=sum_n}
C {devices/lab_wire.sym} 920 560 0 1 {name=l77 lab=sum_n}
C {devices/lab_wire.sym} 920 820 0 1 {name=l78 lab=sum_n}
C {devices/lab_wire.sym} 1375 690 0 1 {name=l79 lab=sum_n}
C {devices/lab_wire.sym} 2140 690 0 1 {name=l80 lab=sum_n}
C {devices/lab_wire.sym} 2420 690 0 1 {name=l81 lab=sum_n}
C {devices/lab_wire.sym} -860 690 0 1 {name=l82 lab=sum_p}
C {devices/lab_wire.sym} -575 690 0 1 {name=l83 lab=sum_p}
C {devices/lab_wire.sym} 585 620 0 0 {name=l84 lab=sum_p}
C {devices/lab_wire.sym} 585 880 0 0 {name=l85 lab=sum_p}
C {devices/lab_wire.sym} 665 690 0 1 {name=l86 lab=sum_p}
C {devices/lab_wire.sym} 435 520 0 1 {name=l87 lab=vb1}
C {devices/lab_wire.sym} 1380 520 0 0 {name=l88 lab=vb1}
C {devices/lab_wire.sym} -45 780 0 1 {name=l89 lab=vb2}
C {devices/lab_wire.sym} 850 780 0 0 {name=l90 lab=vb2}
C {devices/lab_wire.sym} 565 0 0 0 {name=l91 lab=vb3}
C {devices/lab_wire.sym} -175 260 0 0 {name=l92 lab=vb4}
C {devices/lab_wire.sym} 840 260 0 0 {name=l93 lab=vb4}
C {devices/lab_wire.sym} 275 614 2 0 {name=l94 lab=vdd}
C {devices/lab_wire.sym} 1010 94 2 0 {name=l95 lab=vdd}
C {devices/lab_wire.sym} -515 874 2 0 {name=l96 lab=vdd}
C {devices/lab_wire.sym} 2200 874 2 0 {name=l97 lab=vdd}
C {devices/lab_wire.sym} -800 874 2 0 {name=l98 lab=vdd}
C {devices/lab_wire.sym} 2480 874 2 0 {name=l99 lab=vdd}
C {devices/lab_wire.sym} 1540 354 2 0 {name=l100 lab=vdd}
C {devices/lab_wire.sym} 1715 1134 2 0 {name=l101 lab=vdd}
C {devices/lab_wire.sym} 1960 1134 2 0 {name=l102 lab=vdd}
C {devices/lab_wire.sym} -415 520 0 0 {name=l103 lab=vdd}
C {devices/lab_wire.sym} 1960 614 2 0 {name=l104 lab=vdd}
C {devices/lab_wire.sym} -1040 874 2 0 {name=l105 lab=vdd}
C {devices/lab_wire.sym} 2765 874 2 0 {name=l106 lab=vdd}
C {devices/lab_wire.sym} 275 354 2 0 {name=l107 lab=vdd}
C {devices/lab_wire.sym} 725 94 2 0 {name=l108 lab=vdd}
C {devices/lab_wire.sym} 725 354 2 0 {name=l109 lab=vdd}
C {devices/lab_wire.sym} 1000 354 2 0 {name=l110 lab=vdd}
C {devices/lab_wire.sym} 1275 354 2 0 {name=l111 lab=vdd}
C {devices/lab_wire.sym} -15 354 2 0 {name=l112 lab=vdd}
C {devices/lab_wire.sym} 1540 614 2 0 {name=l113 lab=vdd}
C {devices/lab_wire.sym} -205 874 2 0 {name=l114 lab=vss}
C {devices/lab_wire.sym} 1010 874 2 0 {name=l115 lab=vss}
C {devices/lab_wire.sym} -205 1134 2 0 {name=l116 lab=vss}
C {devices/lab_wire.sym} 1010 1134 2 0 {name=l117 lab=vss}
C {devices/lab_wire.sym} 725 614 2 0 {name=l118 lab=vss}
C {devices/lab_wire.sym} 1000 614 2 0 {name=l119 lab=vss}
C {devices/lab_wire.sym} 725 874 2 0 {name=l120 lab=vss}
C {devices/lab_wire.sym} 445 874 2 0 {name=l121 lab=vss}
C {devices/lab_wire.sym} 145 874 2 0 {name=l122 lab=vss}
C {devices/lab_wire.sym} 1435 874 2 0 {name=l123 lab=vss}
C {devices/lab_wire.sym} 145 1134 2 0 {name=l124 lab=vss}
C {devices/lab_wire.sym} 1435 1134 2 0 {name=l125 lab=vss}
C {devices/lab_wire.sym} 1275 614 2 0 {name=l126 lab=vss}
C {devices/lab_wire.sym} -15 614 2 0 {name=l127 lab=vss}
C {devices/lab_wire.sym} 1715 874 2 0 {name=l128 lab=vss}
C {devices/lab_wire.sym} 1960 874 2 0 {name=l129 lab=vss}
C {devices/lab_wire.sym} -1775 950 0 1 {name=l130 lab=vb1}
C {devices/lab_wire.sym} -1775 1130 2 0 {name=l131 lab=vss}
C {devices/lab_wire.sym} -1775 870 2 0 {name=l132 lab=vss}
C {devices/lab_wire.sym} -1775 610 2 0 {name=l133 lab=vss}
C {devices/lab_wire.sym} -1775 350 2 0 {name=l134 lab=vss}
C {devices/lab_wire.sym} -1775 690 0 1 {name=l135 lab=vb2}
C {devices/lab_wire.sym} -1775 430 0 1 {name=l136 lab=vb3}
C {devices/lab_wire.sym} -1775 170 0 1 {name=l137 lab=vb4}
C {devices/lab_wire.sym} 665 610 2 0 {name=l138 lab=vss}
C {devices/ipin.sym} -545 520 0 0 {name=p0 lab=clk_phi_1}
C {devices/ipin.sym} -1230 780 0 0 {name=p1 lab=clk_phi_2}
C {devices/ipin.sym} -990 780 0 0 {name=p2 lab=clk_ch_rrl}
C {devices/ipin.sym} -705 780 0 0 {name=p3 lab=clk_ch_rrl_not}
C {devices/iopin.sym} -1835 -140 0 0 {name=p4 lab=vdd}
C {devices/iopin.sym} -1835 1180 0 0 {name=p5 lab=vss}
C {devices/iopin.sym} 3175 720 0 0 {name=p6 lab=voutn}
C {devices/iopin.sym} 3175 840 0 0 {name=p7 lab=voutp}
C {devices/iopin.sym} -1435 720 0 0 {name=p8 lab=vinn}
C {devices/iopin.sym} 2925 720 0 0 {name=p9 lab=vinp}
