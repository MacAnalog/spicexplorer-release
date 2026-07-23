v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sup_003_rrl_sc_integrator} -1660 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 410 650 0 0 {name=CAZ1 value='x_dut_caz1_value'}
C {devices/capa_np.sym} 635 650 0 0 {name=CAZ2 value='x_dut_caz2_value'}
C {devices/capa_np.sym} 410 910 0 0 {name=CINT1 value='x_dut_cint1_value'}
C {devices/capa_np.sym} 635 910 0 0 {name=CINT2 value='x_dut_cint2_value'}
C {devices/capa_np.sym} 410 1040 0 0 {name=CIN_1 value='cin_val'}
C {devices/capa_np.sym} 635 520 0 0 {name=COUT_1 value='cout_val'}
C {devices/capa_np.sym} 410 780 0 0 {name=CS1 value='x_dut_cs1_value'}
C {devices/capa_np.sym} 170 780 0 0 {name=CS2 value='x_dut_cs2_value'}
C {devices/res_np.sym} 170 1040 0 0 {name=RIN_1 value='rin_val'}
C {devices/res_np.sym} 865 520 0 0 {name=ROUT_1 value='rout_val'}
C {devices/vsource_np.sym} -1620 1040 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -1620 780 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -1620 520 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -1620 260 0 0 {name=VB4 value="dc {vb4}"}
C {devices/sg13_lv_pmos_np.sym} 160 520 0 1 {name=M10_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_w l=x_dut_xm10_opamp_l m=x_dut_xm10_opamp_m}
C {devices/sg13_lv_nmos_np.sym} -255 780 0 1 {name=M11_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_opamp_w l=x_dut_xm11_opamp_l m=x_dut_xm11_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 645 780 0 0 {name=M12_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_opamp_w l=x_dut_xm12_opamp_l m=x_dut_xm12_opamp_m}
C {devices/sg13_lv_nmos_np.sym} -255 1040 0 1 {name=M13_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_opamp_w l=x_dut_xm13_opamp_l m=x_dut_xm13_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 645 1040 0 0 {name=M14_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_opamp_w l=x_dut_xm14_opamp_l m=x_dut_xm14_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 400 520 0 1 {name=M15_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_opamp_w l=x_dut_xm15_opamp_l m=x_dut_xm15_opamp_m}
C {devices/sg13_lv_nmos_np.sym} -150 520 0 1 {name=M16_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_opamp_w l=x_dut_xm16_opamp_l m=x_dut_xm16_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 10 780 0 1 {name=M1_CHRRL_1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_1_w l=x_dut_xm1_chrrl_1_l m=x_dut_xm1_chrrl_1_m}
C {devices/sg13_lv_nmos_np.sym} 1040 780 0 1 {name=M1_CHRRL_2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_2_w l=x_dut_xm1_chrrl_2_l m=x_dut_xm1_chrrl_2_m}
C {devices/sg13_lv_nmos_np.sym} 1285 780 0 1 {name=M1_CHRRL_3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_3_w l=x_dut_xm1_chrrl_3_l m=x_dut_xm1_chrrl_3_m}
C {devices/sg13_lv_nmos_np.sym} 1530 780 0 1 {name=M1_CHRRL_4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_4_w l=x_dut_xm1_chrrl_4_l m=x_dut_xm1_chrrl_4_m}
C {devices/sg13_lv_pmos_np.sym} 645 0 0 0 {name=M1_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_opamp_w l=x_dut_xm1_opamp_l m=x_dut_xm1_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 10 1040 0 1 {name=M1_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s1_w l=x_dut_xm1_s1_l m=x_dut_xm1_s1_m}
C {devices/sg13_lv_nmos_np.sym} 1040 1040 0 1 {name=M1_S2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s2_w l=x_dut_xm1_s2_l m=x_dut_xm1_s2_m}
C {devices/sg13_lv_nmos_np.sym} -385 520 0 1 {name=M1_S3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s3_w l=x_dut_xm1_s3_l m=x_dut_xm1_s3_m}
C {devices/sg13_lv_nmos_np.sym} 1530 520 0 1 {name=M1_S4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s4_w l=x_dut_xm1_s4_l m=x_dut_xm1_s4_m}
C {devices/sg13_lv_nmos_np.sym} -590 780 0 1 {name=M1_S5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s5_w l=x_dut_xm1_s5_l m=x_dut_xm1_s5_m}
C {devices/sg13_lv_nmos_np.sym} 1735 780 0 1 {name=M1_S6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s6_w l=x_dut_xm1_s6_l m=x_dut_xm1_s6_m}
C {devices/sg13_lv_pmos_np.sym} -790 780 0 1 {name=M2_CHRRL_1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_1_w l=x_dut_xm2_chrrl_1_l m=x_dut_xm2_chrrl_1_m}
C {devices/sg13_lv_pmos_np.sym} 1980 780 0 1 {name=M2_CHRRL_2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_2_w l=x_dut_xm2_chrrl_2_l m=x_dut_xm2_chrrl_2_m}
C {devices/sg13_lv_pmos_np.sym} -1035 780 0 1 {name=M2_CHRRL_3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_3_w l=x_dut_xm2_chrrl_3_l m=x_dut_xm2_chrrl_3_m}
C {devices/sg13_lv_pmos_np.sym} 2220 780 0 1 {name=M2_CHRRL_4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_4_w l=x_dut_xm2_chrrl_4_l m=x_dut_xm2_chrrl_4_m}
C {devices/sg13_lv_pmos_np.sym} 1070 260 0 0 {name=M2_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_w l=x_dut_xm2_opamp_l m=x_dut_xm2_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 1285 1040 0 1 {name=M2_S1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s1_w l=x_dut_xm2_s1_l m=x_dut_xm2_s1_m}
C {devices/sg13_lv_pmos_np.sym} 1530 1040 0 1 {name=M2_S2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s2_w l=x_dut_xm2_s2_l m=x_dut_xm2_s2_m}
C {devices/sg13_lv_pmos_np.sym} -590 520 0 1 {name=M2_S3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s3_w l=x_dut_xm2_s3_l m=x_dut_xm2_s3_m}
C {devices/sg13_lv_pmos_np.sym} 1735 520 0 1 {name=M2_S4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s4_w l=x_dut_xm2_s4_l m=x_dut_xm2_s4_m}
C {devices/sg13_lv_pmos_np.sym} -1280 780 0 1 {name=M2_S5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s5_w l=x_dut_xm2_s5_l m=x_dut_xm2_s5_m}
C {devices/sg13_lv_pmos_np.sym} 2425 780 0 1 {name=M2_S6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s6_w l=x_dut_xm2_s6_l m=x_dut_xm2_s6_m}
C {devices/sg13_lv_pmos_np.sym} 160 260 0 1 {name=M3_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_w l=x_dut_xm3_opamp_l m=x_dut_xm3_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 410 0 0 1 {name=M4_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_opamp_w l=x_dut_xm4_opamp_l m=x_dut_xm4_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 410 260 0 1 {name=M5_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_opamp_w l=x_dut_xm5_opamp_l m=x_dut_xm5_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 635 260 0 1 {name=M6_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_opamp_w l=x_dut_xm6_opamp_l m=x_dut_xm6_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 865 260 0 1 {name=M7_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_opamp_w l=x_dut_xm7_opamp_l m=x_dut_xm7_opamp_m}
C {devices/sg13_lv_pmos_np.sym} -150 260 0 1 {name=M8_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_opamp_w l=x_dut_xm8_opamp_l m=x_dut_xm8_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 1070 520 0 0 {name=M9_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_w l=x_dut_xm9_opamp_l m=x_dut_xm9_opamp_m}
N -1620 170 -1620 230 {}
N -1620 290 -1620 350 {}
N -1620 430 -1620 490 {}
N -1620 550 -1620 610 {}
N -1620 690 -1620 750 {}
N -1620 810 -1620 870 {}
N -1620 950 -1620 1010 {}
N -1620 1070 -1620 1130 {}
N -1360 780 -1360 874 {}
N -1300 690 -1300 750 {}
N -1300 810 -1300 870 {}
N -1260 780 -1260 840 {}
N -1115 780 -1115 874 {}
N -1055 690 -1055 750 {}
N -1055 810 -1055 870 {}
N -1015 780 -1015 840 {}
N -870 780 -870 874 {}
N -810 690 -810 750 {}
N -810 810 -810 870 {}
N -770 780 -770 840 {}
N -670 520 -670 614 {}
N -670 780 -670 874 {}
N -610 430 -610 490 {}
N -610 550 -610 610 {}
N -610 690 -610 750 {}
N -610 810 -610 870 {}
N -540 520 -540 780 {}
N -465 520 -465 614 {}
N -405 460 -405 490 {}
N -405 550 -405 580 {}
N -365 520 -365 580 {}
N -335 520 -335 780 {}
N -335 1040 -335 1134 {}
N -275 690 -275 750 {}
N -275 810 -275 870 {}
N -275 950 -275 1010 {}
N -275 1070 -275 1180 {}
N -235 780 -235 840 {}
N -235 1040 -235 1100 {}
N -230 260 -230 354 {}
N -230 520 -230 614 {}
N -170 170 -170 230 {}
N -170 290 -170 350 {}
N -170 430 -170 490 {}
N -170 550 -170 1180 {}
N -130 260 -130 320 {}
N -130 450 -130 520 {}
N -70 780 -70 874 {}
N -70 1040 -70 1134 {}
N -10 690 -10 750 {}
N -10 810 -10 870 {}
N -10 950 -10 1010 {}
N -10 1070 -10 1180 {}
N 30 780 30 840 {}
N 30 1040 30 1100 {}
N 80 260 80 354 {}
N 80 520 80 614 {}
N 140 170 140 230 {}
N 140 290 140 350 {}
N 140 430 140 490 {}
N 140 550 140 610 {}
N 170 690 170 750 {}
N 170 810 170 870 {}
N 170 950 170 1010 {}
N 170 1070 170 1100 {}
N 180 260 180 320 {}
N 180 520 180 580 {}
N 320 520 320 614 {}
N 330 0 330 94 {}
N 330 260 330 354 {}
N 380 430 380 490 {}
N 380 550 380 1180 {}
N 390 -140 390 -30 {}
N 390 30 390 90 {}
N 390 170 390 230 {}
N 390 290 390 350 {}
N 410 590 410 620 {}
N 410 680 410 710 {}
N 410 850 410 880 {}
N 410 940 410 1010 {}
N 410 1070 410 1100 {}
N 420 450 420 520 {}
N 430 260 430 320 {}
N 555 260 555 354 {}
N 615 170 615 230 {}
N 615 290 615 350 {}
N 635 430 635 490 {}
N 635 560 635 620 {}
N 635 680 635 740 {}
N 635 820 635 880 {}
N 635 940 635 1100 {}
N 655 260 655 320 {}
N 665 -140 665 -30 {}
N 665 30 665 90 {}
N 665 690 665 750 {}
N 665 810 665 870 {}
N 665 950 665 1010 {}
N 665 1070 665 1180 {}
N 725 0 725 94 {}
N 725 780 725 874 {}
N 725 1040 725 1134 {}
N 785 260 785 354 {}
N 845 170 845 230 {}
N 845 290 845 350 {}
N 865 460 865 490 {}
N 865 550 865 610 {}
N 960 780 960 874 {}
N 960 1040 960 1134 {}
N 1020 690 1020 750 {}
N 1020 810 1020 870 {}
N 1020 950 1020 1010 {}
N 1020 1070 1020 1180 {}
N 1050 460 1050 520 {}
N 1060 780 1060 840 {}
N 1060 1040 1060 1100 {}
N 1090 170 1090 230 {}
N 1090 290 1090 490 {}
N 1090 550 1090 610 {}
N 1150 260 1150 354 {}
N 1150 520 1150 614 {}
N 1205 780 1205 874 {}
N 1205 1040 1205 1134 {}
N 1265 690 1265 750 {}
N 1265 810 1265 870 {}
N 1265 950 1265 1010 {}
N 1265 1070 1265 1180 {}
N 1305 780 1305 840 {}
N 1305 1040 1305 1100 {}
N 1450 520 1450 614 {}
N 1450 780 1450 874 {}
N 1450 1040 1450 1134 {}
N 1510 430 1510 490 {}
N 1510 550 1510 610 {}
N 1510 690 1510 750 {}
N 1510 810 1510 870 {}
N 1510 950 1510 1010 {}
N 1510 1070 1510 1180 {}
N 1550 780 1550 840 {}
N 1655 520 1655 614 {}
N 1655 780 1655 874 {}
N 1715 460 1715 490 {}
N 1715 550 1715 580 {}
N 1715 690 1715 750 {}
N 1715 810 1715 870 {}
N 1785 520 1785 780 {}
N 1900 780 1900 874 {}
N 1960 690 1960 750 {}
N 1960 810 1960 870 {}
N 2000 780 2000 840 {}
N 2140 780 2140 874 {}
N 2200 690 2200 750 {}
N 2200 810 2200 870 {}
N 2240 780 2240 840 {}
N 2345 780 2345 874 {}
N 2405 690 2405 750 {}
N 2405 810 2405 870 {}
N -1680 -140 2535 -140 {}
N 330 0 390 0 {}
N 430 0 625 0 {}
N 665 0 725 0 {}
N -230 260 -170 260 {}
N -130 260 -100 260 {}
N 80 260 140 260 {}
N 180 260 210 260 {}
N 330 260 390 260 {}
N 430 260 460 260 {}
N 555 260 615 260 {}
N 655 260 685 260 {}
N 785 260 845 260 {}
N 885 260 945 260 {}
N 990 260 1050 260 {}
N 1090 260 1150 260 {}
N -170 450 -130 450 {}
N 380 450 420 450 {}
N -610 460 -405 460 {}
N 635 460 865 460 {}
N 1510 460 1715 460 {}
N -670 520 -610 520 {}
N -570 520 -540 520 {}
N -465 520 -405 520 {}
N -365 520 -335 520 {}
N -230 520 -170 520 {}
N 80 520 140 520 {}
N 180 520 210 520 {}
N 320 520 380 520 {}
N 1090 520 1150 520 {}
N 1450 520 1510 520 {}
N 1550 520 1580 520 {}
N 1655 520 1715 520 {}
N 1755 520 1815 520 {}
N 575 550 635 550 {}
N -610 580 -405 580 {}
N 1510 580 1715 580 {}
N 350 620 410 620 {}
N 350 680 410 680 {}
N -1360 780 -1300 780 {}
N -1260 780 -1230 780 {}
N -1115 780 -1055 780 {}
N -1015 780 -985 780 {}
N -870 780 -810 780 {}
N -770 780 -740 780 {}
N -670 780 -610 780 {}
N -570 780 -540 780 {}
N -235 780 -205 780 {}
N -70 780 -10 780 {}
N 565 780 625 780 {}
N 665 780 725 780 {}
N 960 780 1020 780 {}
N 1060 780 1090 780 {}
N 1205 780 1265 780 {}
N 1305 780 1335 780 {}
N 1450 780 1510 780 {}
N 1655 780 1715 780 {}
N 1755 780 1785 780 {}
N 1900 780 1960 780 {}
N 2000 780 2030 780 {}
N 2140 780 2200 780 {}
N 2240 780 2270 780 {}
N 2345 780 2405 780 {}
N 2445 780 2505 780 {}
N 350 880 410 880 {}
N 350 940 410 940 {}
N 635 970 1715 970 {}
N -335 1040 -275 1040 {}
N -235 1040 -205 1040 {}
N -70 1040 -10 1040 {}
N 30 1040 60 1040 {}
N 595 1040 625 1040 {}
N 665 1040 725 1040 {}
N 960 1040 1020 1040 {}
N 1060 1040 1090 1040 {}
N 1205 1040 1265 1040 {}
N 1305 1040 1335 1040 {}
N 1450 1040 1510 1040 {}
N 1550 1040 1610 1040 {}
N 170 1100 635 1100 {}
N -1680 1180 2535 1180 {}
C {devices/lab_wire.sym} -1680 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1680 1180 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -1015 840 2 0 {name=l2 lab=clk_ch_rrl}
C {devices/lab_wire.sym} 30 840 2 0 {name=l3 lab=clk_ch_rrl}
C {devices/lab_wire.sym} 1060 840 2 0 {name=l4 lab=clk_ch_rrl}
C {devices/lab_wire.sym} 2240 840 2 0 {name=l5 lab=clk_ch_rrl}
C {devices/lab_wire.sym} -770 840 2 0 {name=l6 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} 1305 840 2 0 {name=l7 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} 1550 840 2 0 {name=l8 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} 2000 840 2 0 {name=l9 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} -570 520 0 0 {name=l10 lab=clk_phi_1}
C {devices/lab_wire.sym} 1305 1100 2 0 {name=l11 lab=clk_phi_1}
C {devices/lab_wire.sym} 1610 1040 0 1 {name=l12 lab=clk_phi_1}
C {devices/lab_wire.sym} 1815 520 0 1 {name=l13 lab=clk_phi_1}
C {devices/lab_wire.sym} -1260 840 2 0 {name=l14 lab=clk_phi_2}
C {devices/lab_wire.sym} -365 580 2 0 {name=l15 lab=clk_phi_2}
C {devices/lab_wire.sym} 30 1100 2 0 {name=l16 lab=clk_phi_2}
C {devices/lab_wire.sym} 1060 1100 2 0 {name=l17 lab=clk_phi_2}
C {devices/lab_wire.sym} 1550 520 0 0 {name=l18 lab=clk_phi_2}
C {devices/lab_wire.sym} 2505 780 0 1 {name=l19 lab=clk_phi_2}
C {devices/lab_wire.sym} 635 1000 2 0 {name=l20 lab=int_n}
C {devices/lab_wire.sym} 1715 870 2 0 {name=l21 lab=int_n}
C {devices/lab_wire.sym} 2405 870 2 0 {name=l22 lab=int_n}
C {devices/lab_wire.sym} -1300 870 2 0 {name=l23 lab=int_p}
C {devices/lab_wire.sym} -610 870 2 0 {name=l24 lab=int_p}
C {devices/lab_wire.sym} 170 950 0 1 {name=l25 lab=int_p}
C {devices/lab_wire.sym} 350 940 0 0 {name=l26 lab=int_p}
C {devices/lab_wire.sym} 410 950 0 1 {name=l27 lab=int_p}
C {devices/lab_wire.sym} -235 1100 2 0 {name=l28 lab=oa_cm_bias}
C {devices/lab_wire.sym} -170 350 2 0 {name=l29 lab=oa_cm_bias}
C {devices/lab_wire.sym} 380 430 0 1 {name=l30 lab=oa_cm_bias}
C {devices/lab_wire.sym} 615 350 2 0 {name=l31 lab=oa_cm_bias}
C {devices/lab_wire.sym} 625 1040 0 0 {name=l32 lab=oa_cm_bias}
C {devices/lab_wire.sym} -170 430 0 1 {name=l33 lab=oa_cm_sense}
C {devices/lab_wire.sym} 390 350 2 0 {name=l34 lab=oa_cm_sense}
C {devices/lab_wire.sym} 845 350 2 0 {name=l35 lab=oa_cm_sense}
C {devices/lab_wire.sym} -170 170 0 1 {name=l36 lab=oa_cm_tail}
C {devices/lab_wire.sym} 390 90 2 0 {name=l37 lab=oa_cm_tail}
C {devices/lab_wire.sym} 390 170 0 1 {name=l38 lab=oa_cm_tail}
C {devices/lab_wire.sym} 615 170 0 1 {name=l39 lab=oa_cm_tail}
C {devices/lab_wire.sym} 845 170 0 1 {name=l40 lab=oa_cm_tail}
C {devices/lab_wire.sym} -275 870 2 0 {name=l41 lab=oa_csrc_n}
C {devices/lab_wire.sym} -275 950 0 1 {name=l42 lab=oa_csrc_n}
C {devices/lab_wire.sym} 665 870 2 0 {name=l43 lab=oa_csrc_p}
C {devices/lab_wire.sym} 665 950 0 1 {name=l44 lab=oa_csrc_p}
C {devices/lab_wire.sym} 1090 350 2 0 {name=l45 lab=oa_d1n}
C {devices/lab_wire.sym} 140 350 2 0 {name=l46 lab=oa_d1p}
C {devices/lab_wire.sym} 140 430 0 1 {name=l47 lab=oa_d1p}
C {devices/lab_wire.sym} 180 320 2 0 {name=l48 lab=oa_inn}
C {devices/lab_wire.sym} 635 740 2 0 {name=l49 lab=oa_inn}
C {devices/lab_wire.sym} 1510 430 0 1 {name=l50 lab=oa_inn}
C {devices/lab_wire.sym} -610 430 0 1 {name=l51 lab=oa_inp}
C {devices/lab_wire.sym} 350 680 0 0 {name=l52 lab=oa_inp}
C {devices/lab_wire.sym} 990 260 0 0 {name=l53 lab=oa_inp}
C {devices/lab_wire.sym} -1300 690 0 1 {name=l54 lab=oa_outn}
C {devices/lab_wire.sym} -610 610 2 0 {name=l55 lab=oa_outn}
C {devices/lab_wire.sym} -610 690 0 1 {name=l56 lab=oa_outn}
C {devices/lab_wire.sym} -275 690 0 1 {name=l57 lab=oa_outn}
C {devices/lab_wire.sym} 430 320 2 0 {name=l58 lab=oa_outn}
C {devices/lab_wire.sym} 1090 610 2 0 {name=l59 lab=oa_outn}
C {devices/lab_wire.sym} 140 610 2 0 {name=l60 lab=oa_outp}
C {devices/lab_wire.sym} 665 690 0 1 {name=l61 lab=oa_outp}
C {devices/lab_wire.sym} 945 260 0 1 {name=l62 lab=oa_outp}
C {devices/lab_wire.sym} 1510 610 2 0 {name=l63 lab=oa_outp}
C {devices/lab_wire.sym} 1715 690 0 1 {name=l64 lab=oa_outp}
C {devices/lab_wire.sym} 2405 690 0 1 {name=l65 lab=oa_outp}
C {devices/lab_wire.sym} 140 170 0 1 {name=l66 lab=oa_tail}
C {devices/lab_wire.sym} 665 90 2 0 {name=l67 lab=oa_tail}
C {devices/lab_wire.sym} 1090 170 0 1 {name=l68 lab=oa_tail}
C {devices/lab_wire.sym} -1055 870 2 0 {name=l69 lab=sc_n}
C {devices/lab_wire.sym} -10 950 0 1 {name=l70 lab=sc_n}
C {devices/lab_wire.sym} 170 870 2 0 {name=l71 lab=sc_n}
C {devices/lab_wire.sym} 1020 870 2 0 {name=l72 lab=sc_n}
C {devices/lab_wire.sym} 1265 870 2 0 {name=l73 lab=sc_n}
C {devices/lab_wire.sym} 1265 950 0 1 {name=l74 lab=sc_n}
C {devices/lab_wire.sym} 1960 870 2 0 {name=l75 lab=sc_n}
C {devices/lab_wire.sym} -810 870 2 0 {name=l76 lab=sc_p}
C {devices/lab_wire.sym} -10 870 2 0 {name=l77 lab=sc_p}
C {devices/lab_wire.sym} 410 810 0 0 {name=l78 lab=sc_p}
C {devices/lab_wire.sym} 1020 950 0 1 {name=l79 lab=sc_p}
C {devices/lab_wire.sym} 1510 870 2 0 {name=l80 lab=sc_p}
C {devices/lab_wire.sym} 1510 950 0 1 {name=l81 lab=sc_p}
C {devices/lab_wire.sym} 2200 870 2 0 {name=l82 lab=sc_p}
C {devices/lab_wire.sym} 635 560 0 1 {name=l83 lab=sum_n}
C {devices/lab_wire.sym} 635 820 0 1 {name=l84 lab=sum_n}
C {devices/lab_wire.sym} 1020 690 0 1 {name=l85 lab=sum_n}
C {devices/lab_wire.sym} 1510 690 0 1 {name=l86 lab=sum_n}
C {devices/lab_wire.sym} 1960 690 0 1 {name=l87 lab=sum_n}
C {devices/lab_wire.sym} 2200 690 0 1 {name=l88 lab=sum_n}
C {devices/lab_wire.sym} -1055 690 0 1 {name=l89 lab=sum_p}
C {devices/lab_wire.sym} -810 690 0 1 {name=l90 lab=sum_p}
C {devices/lab_wire.sym} -10 690 0 1 {name=l91 lab=sum_p}
C {devices/lab_wire.sym} 350 620 0 0 {name=l92 lab=sum_p}
C {devices/lab_wire.sym} 350 880 0 0 {name=l93 lab=sum_p}
C {devices/lab_wire.sym} 1265 690 0 1 {name=l94 lab=sum_p}
C {devices/lab_wire.sym} 180 580 2 0 {name=l95 lab=vb1}
C {devices/lab_wire.sym} 1050 460 0 1 {name=l96 lab=vb1}
C {devices/lab_wire.sym} -235 840 2 0 {name=l97 lab=vb2}
C {devices/lab_wire.sym} 565 780 0 0 {name=l98 lab=vb2}
C {devices/lab_wire.sym} 490 0 0 1 {name=l99 lab=vb3}
C {devices/lab_wire.sym} -130 320 2 0 {name=l100 lab=vb4}
C {devices/lab_wire.sym} 655 320 2 0 {name=l101 lab=vb4}
C {devices/lab_wire.sym} 170 690 0 1 {name=l102 lab=vinn}
C {devices/lab_wire.sym} 410 750 0 0 {name=l103 lab=vinp}
C {devices/lab_wire.sym} 635 430 0 1 {name=l104 lab=voutn}
C {devices/lab_wire.sym} 575 550 0 0 {name=l105 lab=voutp}
C {devices/lab_wire.sym} 865 610 2 0 {name=l106 lab=voutp}
C {devices/lab_wire.sym} 80 614 2 0 {name=l107 lab=vdd}
C {devices/lab_wire.sym} 725 94 2 0 {name=l108 lab=vdd}
C {devices/lab_wire.sym} -870 874 2 0 {name=l109 lab=vdd}
C {devices/lab_wire.sym} 1900 874 2 0 {name=l110 lab=vdd}
C {devices/lab_wire.sym} -1115 874 2 0 {name=l111 lab=vdd}
C {devices/lab_wire.sym} 2140 874 2 0 {name=l112 lab=vdd}
C {devices/lab_wire.sym} 1150 354 2 0 {name=l113 lab=vdd}
C {devices/lab_wire.sym} 1205 1134 2 0 {name=l114 lab=vdd}
C {devices/lab_wire.sym} 1450 1134 2 0 {name=l115 lab=vdd}
C {devices/lab_wire.sym} -670 614 2 0 {name=l116 lab=vdd}
C {devices/lab_wire.sym} 1655 614 2 0 {name=l117 lab=vdd}
C {devices/lab_wire.sym} -1360 874 2 0 {name=l118 lab=vdd}
C {devices/lab_wire.sym} 2345 874 2 0 {name=l119 lab=vdd}
C {devices/lab_wire.sym} 80 354 2 0 {name=l120 lab=vdd}
C {devices/lab_wire.sym} 330 94 2 0 {name=l121 lab=vdd}
C {devices/lab_wire.sym} 330 354 2 0 {name=l122 lab=vdd}
C {devices/lab_wire.sym} 555 354 2 0 {name=l123 lab=vdd}
C {devices/lab_wire.sym} 785 354 2 0 {name=l124 lab=vdd}
C {devices/lab_wire.sym} -230 354 2 0 {name=l125 lab=vdd}
C {devices/lab_wire.sym} 1150 614 2 0 {name=l126 lab=vdd}
C {devices/lab_wire.sym} -275 780 0 0 {name=l127 lab=vss}
C {devices/lab_wire.sym} 725 874 2 0 {name=l128 lab=vss}
C {devices/lab_wire.sym} -335 1134 2 0 {name=l129 lab=vss}
C {devices/lab_wire.sym} 725 1134 2 0 {name=l130 lab=vss}
C {devices/lab_wire.sym} 320 614 2 0 {name=l131 lab=vss}
C {devices/lab_wire.sym} -230 614 2 0 {name=l132 lab=vss}
C {devices/lab_wire.sym} -70 874 2 0 {name=l133 lab=vss}
C {devices/lab_wire.sym} 960 874 2 0 {name=l134 lab=vss}
C {devices/lab_wire.sym} 1205 874 2 0 {name=l135 lab=vss}
C {devices/lab_wire.sym} 1450 874 2 0 {name=l136 lab=vss}
C {devices/lab_wire.sym} -70 1134 2 0 {name=l137 lab=vss}
C {devices/lab_wire.sym} 960 1134 2 0 {name=l138 lab=vss}
C {devices/lab_wire.sym} -465 614 2 0 {name=l139 lab=vss}
C {devices/lab_wire.sym} 1450 614 2 0 {name=l140 lab=vss}
C {devices/lab_wire.sym} -670 874 2 0 {name=l141 lab=vss}
C {devices/lab_wire.sym} 1655 874 2 0 {name=l142 lab=vss}
C {devices/lab_wire.sym} -1620 950 0 1 {name=l143 lab=vb1}
C {devices/lab_wire.sym} -1620 1130 2 0 {name=l144 lab=vss}
C {devices/lab_wire.sym} -1620 870 2 0 {name=l145 lab=vss}
C {devices/lab_wire.sym} -1620 610 2 0 {name=l146 lab=vss}
C {devices/lab_wire.sym} -1620 350 2 0 {name=l147 lab=vss}
C {devices/lab_wire.sym} -1620 690 0 1 {name=l148 lab=vb2}
C {devices/lab_wire.sym} -1620 430 0 1 {name=l149 lab=vb3}
C {devices/lab_wire.sym} -1620 170 0 1 {name=l150 lab=vb4}
C {devices/ipin.sym} -1820 520 0 0 {name=p0 lab=clk_phi_1}
C {devices/ipin.sym} -1820 640 0 0 {name=p1 lab=clk_phi_2}
C {devices/ipin.sym} -1820 780 0 0 {name=p2 lab=clk_ch_rrl}
C {devices/ipin.sym} -1820 900 0 0 {name=p3 lab=clk_ch_rrl_not}
C {devices/iopin.sym} 170 1320 0 0 {name=p4 lab=voutn}
C {devices/iopin.sym} 410 1320 0 0 {name=p5 lab=voutp}
C {devices/iopin.sym} 635 1320 0 0 {name=p6 lab=vinn}
C {devices/iopin.sym} 755 1320 0 0 {name=p7 lab=vinp}
B 8 -499 442 889 1118 {fill=0}
T {NMOS Simple Current Mirror (2 outputs)} -499 424 0 0 0.3 0.3 {layer=8}
B 10 -84 182 1306 598 {fill=0}
T {PMOS Cascode Differential Pair Differential Pair} -84 164 0 0 0.3 0.3 {layer=10}
B 12 -242 702 1600 858 {fill=0}
T {NMOS Differential Pair} -242 684 0 0 0.3 0.3 {layer=12}
B 21 -1042 702 80 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1042 684 0 0 0.3 0.3 {layer=21}
B 15 788 702 1355 858 {fill=0}
T {NMOS Differential Pair} 788 684 0 0 0.3 0.3 {layer=15}
B 13 788 702 2050 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 788 660 0 0 0.3 0.3 {layer=13}
B 18 -1287 702 1355 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1287 684 0 0 0.3 0.3 {layer=18}
B 20 1278 702 2290 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1278 684 0 0 0.3 0.3 {layer=20}
B 8 -802 442 -315 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -802 424 0 0 0.3 0.3 {layer=8}
B 10 1318 442 1805 598 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1318 424 0 0 0.3 0.3 {layer=10}
B 12 -1492 702 -520 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} -1492 684 0 0 0.3 0.3 {layer=12}
B 21 1523 702 2495 858 {fill=0}
T {COMPLEMENTARY Pass Gate Transmission Gate [alt: tg.pair.cmos]} 1523 684 0 0 0.3 0.3 {layer=21}
B 15 174 182 705 338 {fill=0}
T {PMOS Differential Pair} 174 164 0 0 0.3 0.3 {layer=15}
B 13 -386 182 480 338 {fill=0}
T {PMOS Differential Pair} -386 164 0 0 0.3 0.3 {layer=13}
B 18 399 182 935 338 {fill=0}
T {PMOS Differential Pair} 399 164 0 0 0.3 0.3 {layer=18}
B 20 -386 182 935 338 {fill=0}
T {PMOS Differential Pair} -386 140 0 0 0.3 0.3 {layer=20}
B 8 -54 204 1284 316 {fill=0 dash=4}
T {PMOS Differential Pair} -54 138 0 0 0.3 0.3 {layer=8}
